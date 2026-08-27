"""Content-hash based cache for media analysis results, plus a small bounded
concurrency + retry runner shared by the image and audio pipelines.

Cache entries are one JSON file per content hash under data/cache/<kind>/.
Keying by content hash (not file path) means a byte-identical file is never
re-processed even if it gets renamed, and a changed file (different hash)
is always re-processed even if the path is unchanged.
"""

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Iterable

from config import MAX_RETRIES, MEDIA_CONCURRENCY


def content_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cache_path(cache_dir: Path, digest: str) -> Path:
    return cache_dir / f"{digest}.json"


def load_cached(cache_dir: Path, digest: str) -> dict | None:
    p = cache_path(cache_dir, digest)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_cached(cache_dir: Path, digest: str, record: dict) -> None:
    p = cache_path(cache_dir, digest)
    p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def is_success(record: dict | None) -> bool:
    return bool(record) and record.get("status") == "success"


def run_with_retries(fn: Callable[[], dict], max_retries: int = MAX_RETRIES) -> dict:
    """Call fn() (a zero-arg closure that returns a result dict or raises),
    retrying on exception with exponential backoff. Returns a dict with at
    least a 'status' key -- 'success' or 'failed' (+ 'error')."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 - we deliberately catch broadly here
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
    return {"status": "failed", "error": last_error, "attempts": max_retries}


def process_concurrently(
    items: list,
    process_one: Callable[[object], dict],
    max_workers: int = MEDIA_CONCURRENCY,
    on_result: Callable[[object, dict], None] | None = None,
) -> list[dict]:
    """Run process_one(item) for every item with bounded concurrency.
    process_one is expected to internally handle caching/retries and return
    a result dict; exceptions here are a bug, not an expected failure mode
    (process_one should already convert failures into a {'status':'failed'} dict)."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(process_one, item): item for item in items}
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            result = future.result()
            results.append(result)
            if on_result:
                on_result(item, result)
    return results
