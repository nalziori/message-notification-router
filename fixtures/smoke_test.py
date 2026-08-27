"""Offline smoke test -- runs the real pipeline over the fixture dataset with
zero network calls and no ANTHROPIC_API_KEY. This is what a reviewer without
the challenge dataset (or CI) can run to confirm the code actually works, and
what to run first on hackathon day before spending any API budget.

Exercises for real: build_database, router.pull_context/build_context_block,
schema-shaped response parsing, action/type/confidence validation, AEL
recording (all 6 stages) and its own get_cycle() read path, to_output_row,
output.csv writing, and the required-workflow schema check
(code/evaluation/eval_harness_en.py's check_schema, reused rather than
reimplemented). Also re-runs everything a second time to guard against the
ael_state cache-hit collision fixed 2026-08-27 (see code/test_ael_client.py
for the unit-level version of that same regression).

Does NOT exercise: image_pipeline.py / audio_pipeline.py (they call the
Anthropic API / faster-whisper directly) or routing quality -- the fake
client always returns the fixture's own expected label, so every fixture
case both routes and reports 100% agreement with itself by construction.
That is not a claim about accuracy; see fixtures/expected_labels.csv's `note`
column for the cases a human reader found genuinely ambiguous.

    python fixtures/smoke_test.py
Exit 0 on pass, 1 on any failure.
"""

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "evaluation"))

import config  # noqa: E402

# Redirect every config path at scratch locations under fixtures/ BEFORE
# importing router/ael_client -- both snapshot config.CACHE_DIR/DATA_DIR into
# their own module-level constants (ROUTING_CACHE_DIR, AEL_DB_PATH) at import
# time, so patching config after importing them would be silently ignored.
SCRATCH = HERE / "_scratch"
config.DATASET_DIR = HERE / "dataset"
config.DATA_DIR = SCRATCH
config.DB_PATH = SCRATCH / "fixture.db"
config.CACHE_DIR = SCRATCH / "cache"
config.IMAGE_CACHE_DIR = config.CACHE_DIR / "images"
config.AUDIO_CACHE_DIR = config.CACHE_DIR / "audio"
for d in (config.DATA_DIR, config.CACHE_DIR, config.IMAGE_CACHE_DIR, config.AUDIO_CACHE_DIR):
    d.mkdir(parents=True, exist_ok=True)

from db import build_database, get_connection  # noqa: E402
import router  # noqa: E402
import ael_client  # noqa: E402
from eval_harness_en import check_schema  # noqa: E402

sys.path.insert(0, str(HERE))
from fake_client import FakeAnthropic  # noqa: E402

OUT_CSV = SCRATCH / "smoke_output.csv"
FIELDNAMES = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]


def route_all(messages, client, force):
    conn = get_connection()
    try:
        records = {}
        for m in messages:
            records[m["message_id"]] = router.process_message(m, conn, client, force=force)
        return records
    finally:
        conn.close()


def main() -> int:
    ok = True

    print("== build_database (fixtures/dataset) ==")
    summary = build_database(dataset_dir=config.DATASET_DIR, db_path=config.DB_PATH)
    for table, count in summary.items():
        print(f"  {table}: {count} rows")

    ael_client.init_db(ael_client.AEL_DB_PATH)

    with open(config.DATASET_DIR / "messages.csv", newline="", encoding="utf-8") as f:
        messages = list(csv.DictReader(f))

    client = FakeAnthropic()
    print(f"\n== routing {len(messages)} fixture message(s), offline ==")
    records = route_all(messages, client, force=True)
    for m in messages:
        r = records[m["message_id"]]
        print(f"  [{r.get('status')}] {m['message_id']}: {r.get('action')}/{r.get('message_type')}")

    n_success = sum(1 for r in records.values() if r.get("status") == "success")
    if n_success != len(messages):
        ok = False
        print(f"  [FAIL] {n_success}/{len(messages)} classified successfully")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for m in messages:
            w.writerow(router.to_output_row(m["message_id"], records[m["message_id"]]))

    print(f"\n== schema check ({OUT_CSV.relative_to(ROOT)}) ==")
    errors = check_schema(str(OUT_CSV))
    if errors:
        ok = False
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print(f"  [ok] header matches the required {len(FIELDNAMES)} columns exactly")

    print("\n== AEL ledger check (Planning..State per message) ==")
    ael_conn = ael_client.get_connection(ael_client.AEL_DB_PATH)
    incomplete = []
    for m in messages:
        cycle = ael_client.get_cycle(m["message_id"], conn=ael_conn)
        if not all(cycle[stage] for stage in ("planning", "execution", "verification", "reflection", "state")):
            incomplete.append(m["message_id"])
    ael_conn.close()
    if incomplete:
        ok = False
        print(f"  [FAIL] incomplete ledger cycle for: {incomplete}")
    else:
        print(f"  [ok] {len(messages)} complete Planning->State cycles recorded")

    print("\n== cache-hit replay (regression guard, must not crash) ==")
    try:
        route_all(messages, client, force=False)
        print("  [ok] second pass, served from cache, completed without error")
    except Exception as e:  # noqa: BLE001 -- a smoke test should catch and report, not propagate
        ok = False
        print(f"  [FAIL] cache-hit replay crashed: {e}")

    print(f"\n{'PASS' if ok else 'FAIL'} -- {len(messages)} fixture message(s), 0 API calls")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
