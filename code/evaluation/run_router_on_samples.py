"""Run the actual router (../router.py) against dataset/sample_messages.csv's
own input fields (ignoring its pre-filled label columns) and write the
predictions to code/evaluation/sample_predictions.csv. This IS the required
"evaluation workflow" for the submission -- sample_messages.csv uses a
disjoint message_id namespace (sample_msg_* vs messages.csv's msg_*), so it
is a separate solved example set, not a labeled subset of messages.csv.
Comparing dataset/output.csv directly to sample_messages.csv (by id) will
always show 0 matches; this script closes that gap by actually classifying
the sample rows themselves, then eval_harness_en.py/eval_harness_ko.py score
the result.

Usage (from the repo root):
    python code/evaluation/run_router_on_samples.py
    python code/evaluation/eval_harness_en.py --pred code/evaluation/sample_predictions.csv --gold dataset/sample_messages.csv
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic

import config
from db import build_database, get_connection
from router import process_message, to_output_row

INPUT_COLUMNS = [
    "message_id", "user_id", "conversation_type", "group_id", "business_id",
    "sender_user_id", "created_at", "message_text", "media_type", "media_id", "forwarded_count",
]


def main():
    parser = argparse.ArgumentParser(description="Classify dataset/sample_messages.csv with the router")
    parser.add_argument(
        "--use-cache", action="store_true",
        help="Reuse cached classifications instead of forcing a fresh call per message. Default is "
             "to force-reclassify every run, because a stale cache entry from an earlier prompt "
             "version would otherwise silently score the OLD prompt instead of the current one.",
    )
    args = parser.parse_args()

    config.require_api_key()
    build_database()

    with open(config.DATASET_DIR / "sample_messages.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    client = anthropic.Anthropic()
    conn = get_connection()
    predictions = []
    for row in rows:
        message_row = {k: row.get(k, "") for k in INPUT_COLUMNS}
        record = process_message(message_row, conn, client, force=not args.use_cache)
        predictions.append(to_output_row(row["message_id"], record))
        print(f"  [{record.get('status')}] {row['message_id']}")
    conn.close()

    out_path = Path(__file__).resolve().parent / "sample_predictions.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
        )
        writer.writeheader()
        writer.writerows(predictions)
    print(f"\nWrote {out_path} ({len(predictions)} rows)")


if __name__ == "__main__":
    main()
