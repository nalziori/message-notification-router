"""CLI entry point for the dataset preprocessing + query system.

Commands:
  validate       Check dataset files, media files, and API key presence. No network calls.
  preprocess     Build the SQLite DB and analyze all images/audio (cached, skips already-done work).
  route          Classify every message in messages.csv (notify/digest/mute) and write dataset/output.csv.
  retry-failed   Re-run only media/routing that previously failed or was never processed.
  cache-status   Report DB row counts, media cache, and routing/output.csv status.
  query "<q>"    Answer a question using retrieval over the local DB + cache, then a minimal Claude call.

Run with -h on any subcommand for its options.
"""

import argparse
import csv
import json
import sys
import time

# Force UTF-8 stdout/stderr so Claude's responses (which may include em-dashes,
# non-ASCII text, etc.) print correctly regardless of the Windows console's
# active code page (cp949 on Korean Windows raises UnicodeEncodeError otherwise).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import config
from cache import load_cached, process_concurrently
from db import build_database, get_connection


def _load_media_manifest():
    """Return (image_id, path) and (voice_note_id, path, linked_message_ids, linked_user_ids)
    lists built from images.csv / voice_notes.csv joined against every
    message table that carries media_id."""
    images = []
    with open(config.DATASET_DIR / "images.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            images.append((row["image_id"], config.DATASET_DIR / row["file_path"]))

    voice_notes = []
    conn = get_connection()
    try:
        with open(config.DATASET_DIR / "voice_notes.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                vn_id = row["voice_note_id"]
                linked = []
                for table in ("messages", "message_history", "sample_messages"):
                    try:
                        rows = conn.execute(
                            f'SELECT message_id, user_id FROM "{table}" WHERE media_id = ?', (vn_id,)
                        ).fetchall()
                    except Exception:
                        continue
                    linked.extend(rows)
                msg_ids = sorted({r["message_id"] for r in linked if r["message_id"]})
                user_ids = sorted({r["user_id"] for r in linked if r["user_id"]})
                voice_notes.append((vn_id, config.DATASET_DIR / row["file_path"], msg_ids, user_ids))
    finally:
        conn.close()
    return images, voice_notes


def cmd_validate(args):
    print("== Dataset validation (no network calls) ==")
    required_csvs = [
        "messages.csv", "sample_messages.csv", "users.csv", "groups.csv",
        "group_members.csv", "business_accounts.csv", "user_business_history.csv",
        "message_history.csv", "message_events.csv", "images.csv", "voice_notes.csv",
        "daily_notification_summary.csv", "output.csv",
    ]
    ok = True
    for name in required_csvs:
        path = config.DATASET_DIR / name
        if path.exists():
            # Count via csv.reader, not raw newlines -- message_text can contain
            # embedded newlines inside quoted fields, which inflates a naive line count.
            with open(path, encoding="utf-8", newline="") as f:
                n = sum(1 for _ in csv.reader(f)) - 1
            print(f"  [ok]   {name}  ({n} rows)")
        else:
            print(f"  [MISSING] {name}")
            ok = False

    images, voice_notes = _load_media_manifest()
    missing_media = [p for _, p in images if not p.exists()]
    missing_media += [p for _, p, _, _ in voice_notes if not p.exists()]
    print(f"  images.csv references {len(images)} images, {sum(1 for _, p in images if p.exists())} found on disk")
    print(f"  voice_notes.csv references {len(voice_notes)} audio files, "
          f"{sum(1 for _, p, _, _ in voice_notes if p.exists())} found on disk")
    if missing_media:
        print(f"  [WARNING] {len(missing_media)} media file(s) referenced but not found on disk")
        ok = False

    key = config.get_api_key()
    print(f"  ANTHROPIC_API_KEY: {'set' if key else 'NOT SET (preprocess/query will refuse to run)'}")
    print(f"  Whisper model: {config.WHISPER_MODEL_SIZE} (device={config.WHISPER_DEVICE})")
    print("  Result:", "OK" if ok else "PROBLEMS FOUND")
    return 0 if ok else 1


def cmd_preprocess(args):
    print("== Building SQLite database from dataset/*.csv ==")
    summary = build_database()
    for table, count in summary.items():
        print(f"  {table}: {count} rows")

    images, voice_notes = _load_media_manifest()
    if args.limit:
        images = images[: args.limit]
        voice_notes = voice_notes[: args.limit]

    already_cached_images = sum(
        1 for _, p in images
        if p.exists() and _is_cached_success(config.IMAGE_CACHE_DIR, p)
    )
    already_cached_audio = sum(
        1 for _, p, _, _ in voice_notes
        if p.exists() and _is_cached_success(config.AUDIO_CACHE_DIR, p)
    )
    print("\n== Media plan ==")
    print(f"  images: {len(images)} total, {already_cached_images} already cached, "
          f"{len(images) - already_cached_images} to process")
    print(f"  audio:  {len(voice_notes)} total, {already_cached_audio} already cached, "
          f"{len(voice_notes) - already_cached_audio} to process")

    if args.dry_run:
        print("\n[dry-run] No API calls or transcription performed.")
        return 0

    if len(images) - already_cached_images > 0:
        config.require_api_key()  # raises with clear guidance if unset -- fail before any network call

    import anthropic
    from image_pipeline import process_image

    client = anthropic.Anthropic() if len(images) - already_cached_images > 0 else None

    print("\n== Processing images ==")
    t0 = time.time()

    def _proc_image(item):
        image_id, path = item
        if not path.exists():
            return {"image_id": image_id, "status": "failed", "error": "file not found"}
        return process_image(image_id, path, client)

    def _report(item, result):
        image_id, _ = item
        status = result.get("status")
        cached = " (cached)" if result.get("from_cache") else ""
        print(f"  [{status}] {image_id}{cached}")

    image_results = process_concurrently(images, _proc_image, on_result=_report)
    print(f"  done in {time.time() - t0:.1f}s")

    print("\n== Processing audio (local Whisper, no API cost) ==")
    from audio_pipeline import process_audio

    t0 = time.time()

    def _proc_audio(item):
        vn_id, path, msg_ids, user_ids = item
        if not path.exists():
            return {"voice_note_id": vn_id, "status": "failed", "error": "file not found"}
        return process_audio(vn_id, path, msg_ids, user_ids)

    def _report_audio(item, result):
        vn_id, *_ = item
        status = result.get("status")
        cached = " (cached)" if result.get("from_cache") else ""
        print(f"  [{status}] {vn_id}{cached}")

    audio_results = process_concurrently(voice_notes, _proc_audio, on_result=_report_audio)
    print(f"  done in {time.time() - t0:.1f}s")

    n_img_ok = sum(1 for r in image_results if r.get("status") == "success")
    n_aud_ok = sum(1 for r in audio_results if r.get("status") == "success")
    print("\n== Summary ==")
    print(f"  images: {n_img_ok}/{len(image_results)} succeeded")
    print(f"  audio:  {n_aud_ok}/{len(audio_results)} succeeded (local Whisper, $0 API cost)")
    _print_run_cost(image_results)
    return 0


def _print_run_cost(results):
    """Sum token usage for calls actually made THIS run (skips cache hits,
    which cost nothing now) and print an estimated dollar cost. Pricing is
    for claude-sonnet-5 introductory rate ($2/$10 per MTok, through 2026-08-31);
    update if ANTHROPIC_MODEL or pricing changes."""
    fresh = [r for r in results if r.get("status") == "success" and not r.get("from_cache") and r.get("usage")]
    if not fresh:
        print("  cost this run: $0.00 (all results served from cache)")
        return
    in_tok = sum(r["usage"]["input_tokens"] for r in fresh)
    out_tok = sum(r["usage"]["output_tokens"] for r in fresh)
    cost = (in_tok / 1_000_000) * 2.0 + (out_tok / 1_000_000) * 10.0
    print(f"  cost this run: ~${cost:.4f}  ({in_tok} input + {out_tok} output tokens, "
          f"{len(fresh)} fresh API call(s), claude-sonnet-5 intro pricing $2/$10 per MTok)")


def _is_cached_success(cache_dir, path) -> bool:
    from cache import content_hash, is_success

    return is_success(load_cached(cache_dir, content_hash(path)))


def cmd_retry_failed(args):
    print("== Retrying failed / unprocessed media ==")
    images, voice_notes = _load_media_manifest()
    failed_images = [(i, p) for i, p in images if p.exists() and not _is_cached_success(config.IMAGE_CACHE_DIR, p)]
    failed_audio = [(v, p, m, u) for v, p, m, u in voice_notes if p.exists() and not _is_cached_success(config.AUDIO_CACHE_DIR, p)]
    print(f"  {len(failed_images)} image(s) and {len(failed_audio)} audio file(s) need (re)processing")

    if not failed_images and not failed_audio:
        print("  Nothing to retry.")
        return 0

    if failed_images:
        config.require_api_key()
        import anthropic
        from image_pipeline import process_image

        client = anthropic.Anthropic()
        for image_id, path in failed_images:
            result = process_image(image_id, path, client, force=True)
            print(f"  [{result.get('status')}] {image_id}")

    if failed_audio:
        from audio_pipeline import process_audio

        for vn_id, path, msg_ids, user_ids in failed_audio:
            result = process_audio(vn_id, path, msg_ids, user_ids, force=True)
            print(f"  [{result.get('status')}] {vn_id}")

    if config.DB_PATH.exists():
        messages = _load_messages()
        failed_routes = [m for m in messages if (_routing_cache_record(m["message_id"]) or {}).get("status") != "success"]
        if failed_routes:
            print(f"  {len(failed_routes)} routing decision(s) need (re)processing")
            config.require_api_key()
            import anthropic
            from ael_client import init_db as init_ael_db
            from router import process_message

            init_ael_db()
            client = anthropic.Anthropic()
            conn = get_connection()
            for m in failed_routes:
                result = process_message(m, conn, client, force=True)
                print(f"  [{result.get('status')}] {m['message_id']}")
            conn.close()
            _write_output_csv(messages)
    return 0


def cmd_cache_status(args):
    print("== Database ==")
    if not config.DB_PATH.exists():
        print("  No database built yet. Run: python main.py preprocess --dry-run")
    else:
        conn = get_connection()
        tables = [r["name"] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        for t in sorted(tables):
            n = conn.execute(f'SELECT COUNT(*) AS n FROM "{t}"').fetchone()["n"]
            print(f"  {t}: {n} rows")
        conn.close()

    print("\n== Media cache ==")
    images, voice_notes = _load_media_manifest()
    img_ok = sum(1 for _, p in images if p.exists() and _is_cached_success(config.IMAGE_CACHE_DIR, p))
    aud_ok = sum(1 for _, p, _, _ in voice_notes if p.exists() and _is_cached_success(config.AUDIO_CACHE_DIR, p))
    print(f"  images: {img_ok}/{len(images)} cached successfully")
    print(f"  audio:  {aud_ok}/{len(voice_notes)} cached successfully (local Whisper, $0 API cost)")

    total_in = total_out = 0
    for f in config.IMAGE_CACHE_DIR.glob("*.json"):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        usage = rec.get("usage") or {}
        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)
    if total_in or total_out:
        cost = (total_in / 1_000_000) * 2.0 + (total_out / 1_000_000) * 10.0
        print(f"  cumulative image-analysis spend to date: ~${cost:.4f} "
              f"({total_in} input + {total_out} output tokens across all cached images)")

    print("\n== Routing (output.csv) cache ==")
    from router import ROUTING_CACHE_DIR

    messages_path = config.DATASET_DIR / "messages.csv"
    if messages_path.exists():
        messages = _load_messages()
        n_ok = sum(1 for m in messages if (_routing_cache_record(m["message_id"]) or {}).get("status") == "success")
        print(f"  routed: {n_ok}/{len(messages)} messages classified successfully")
        route_in = route_out = 0
        for f in ROUTING_CACHE_DIR.glob("*.json"):
            try:
                rec = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            usage = rec.get("usage") or {}
            route_in += usage.get("input_tokens", 0)
            route_out += usage.get("output_tokens", 0)
        if route_in or route_out:
            cost = (route_in / 1_000_000) * 2.0 + (route_out / 1_000_000) * 10.0
            print(f"  cumulative routing spend to date: ~${cost:.4f} "
                  f"({route_in} input + {route_out} output tokens)")
        out_csv = config.DATASET_DIR / "output.csv"
        print(f"  {out_csv} {'exists' if out_csv.exists() else 'NOT YET WRITTEN -- run: python code/main.py route'}")
    return 0


def _load_messages():
    with open(config.DATASET_DIR / "messages.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _routing_cache_record(message_id):
    from router import ROUTING_CACHE_DIR

    path = ROUTING_CACHE_DIR / f"{message_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def cmd_route(args):
    print("== Building SQLite database from dataset/*.csv ==")
    build_database()

    from ael_client import init_db as init_ael_db

    init_ael_db()

    messages = _load_messages()
    to_process = messages[: args.limit] if args.limit else messages
    already_ok = sum(
        1 for m in to_process
        if (_routing_cache_record(m["message_id"]) or {}).get("status") == "success"
    )
    print("\n== Routing plan ==")
    print(f"  messages.csv: {len(messages)} total")
    print(f"  this run will attempt: {len(to_process)} message(s), "
          f"{already_ok} already cached successfully" + ("" if args.force else " (skipped unless --force)"))

    if args.dry_run:
        print("\n[dry-run] No API calls performed. output.csv not written.")
        return 0

    if any((_routing_cache_record(m["message_id"]) or {}).get("status") != "success" for m in to_process) or args.force:
        config.require_api_key()

    import anthropic
    from router import process_message

    client = anthropic.Anthropic()
    t0 = time.time()

    def _proc(message_row):
        # SQLite connections aren't thread-safe -- process_concurrently runs
        # this from a thread pool, so each worker gets its own connection
        # rather than sharing one (which raised "objects created in a thread
        # can only be used in that same thread" on the first real run).
        conn = get_connection()
        try:
            return process_message(message_row, conn, client, force=args.force)
        finally:
            conn.close()

    def _report(message_row, result):
        status = result.get("status")
        cached = " (cached)" if result.get("from_cache") else ""
        print(f"  [{status}] {message_row['message_id']}{cached}")

    results = process_concurrently(to_process, _proc, on_result=_report)
    print(f"  done in {time.time() - t0:.1f}s")

    n_ok = sum(1 for r in results if r.get("status") == "success")
    print("\n== Summary (this run) ==")
    print(f"  routed: {n_ok}/{len(results)} succeeded")
    _print_run_cost(results)

    _write_output_csv(messages)
    return 0


def _write_output_csv(messages):
    from router import to_output_row

    out_path = config.DATASET_DIR / "output.csv"
    fieldnames = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
    rows = []
    n_fallback = 0
    for m in messages:
        mid = m["message_id"]
        record = _routing_cache_record(mid)
        row = to_output_row(mid, record)
        if record is None or record.get("status") != "success":
            n_fallback += 1
        rows.append(row)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n== Wrote {out_path} ==")
    print(f"  {len(rows)} row(s), {len(rows) - n_fallback} classified, {n_fallback} fallback "
          f"(digest/unknown -- run 'retry-failed' to reclassify these)")


def cmd_query(args):
    config.require_api_key()
    import anthropic
    from query import answer_question

    client = anthropic.Anthropic()
    result = answer_question(args.question, client)
    print(result["answer"])
    print("\nEvidence message_ids:", ", ".join(result["evidence_message_ids"]) or "none")
    usage = result.get("usage")
    if usage:
        cost = (usage["input_tokens"] / 1_000_000) * 2.0 + (usage["output_tokens"] / 1_000_000) * 10.0
        print(f"cost this query: ~${cost:.4f} ({usage['input_tokens']} in + {usage['output_tokens']} out tokens)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Dataset preprocessing + query CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Check dataset/media files and API key presence (no network calls)")

    p_preprocess = sub.add_parser("preprocess", help="Build the DB and analyze all images/audio")
    p_preprocess.add_argument("--dry-run", action="store_true", help="Show planned work without calling any API")
    p_preprocess.add_argument("--limit", type=int, default=None, help="Only process the first N images/audio (testing)")

    p_route = sub.add_parser("route", help="Classify every message in messages.csv and write dataset/output.csv")
    p_route.add_argument("--dry-run", action="store_true", help="Show planned work without calling any API or writing output.csv")
    p_route.add_argument("--limit", type=int, default=None, help="Only classify the first N messages this run (testing)")
    p_route.add_argument("--force", action="store_true", help="Reclassify even messages already cached successfully")

    sub.add_parser("retry-failed", help="Re-run only media/routing that previously failed or was never processed")
    sub.add_parser("cache-status", help="Report DB row counts, media cache status, and routing/output.csv status")

    p_query = sub.add_parser("query", help="Answer a question using retrieval + Claude")
    p_query.add_argument("question", help="The question to answer")

    args = parser.parse_args()
    handlers = {
        "validate": cmd_validate,
        "preprocess": cmd_preprocess,
        "route": cmd_route,
        "retry-failed": cmd_retry_failed,
        "cache-status": cmd_cache_status,
        "query": cmd_query,
    }
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
