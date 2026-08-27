"""Evaluation workflow entry point (required by the problem statement's
"Must include an evaluation workflow" requirement).

Runs the router against dataset/sample_messages.csv's own input fields (the
30 solved examples), then scores the result against their known-correct
labels. sample_messages.csv uses a disjoint message_id namespace from
messages.csv, so this is the correct way to get a real accuracy read --
comparing dataset/output.csv to sample_messages.csv by id would always score
zero matches.

This is a local, non-hidden proxy for the real (hidden) grading set --
useful for catching regressions before submitting, not a substitute for it.

Usage (from the repo root):
    python code/evaluation/main.py                 # English report
    python code/evaluation/main.py --lang ko        # Korean report
"""

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_CSV = HERE / "sample_predictions.csv"
GOLD_CSV = HERE.parent.parent / "dataset" / "sample_messages.csv"
HISTORY_CSV = HERE.parent.parent / "dataset" / "message_history.csv"


def main():
    parser = argparse.ArgumentParser(description="Evaluation workflow: classify sample_messages.csv, then score it")
    parser.add_argument("--lang", choices=["en", "ko"], default="en")
    parser.add_argument("--skip-classify", action="store_true",
                         help="Reuse an existing sample_predictions.csv instead of reclassifying (no API calls)")
    args = parser.parse_args()

    python = sys.executable

    if not args.skip_classify:
        print("== Step 1: classify dataset/sample_messages.csv with the router ==")
        subprocess.run([python, str(HERE / "run_router_on_samples.py")], check=True)
    else:
        print("== Step 1 skipped (--skip-classify): reusing existing sample_predictions.csv ==")
        if not PRED_CSV.exists():
            print(f"  {PRED_CSV} does not exist -- run without --skip-classify first.")
            sys.exit(1)

    print("\n== Step 2: score against dataset/sample_messages.csv ==")
    harness = HERE / f"eval_harness_{args.lang}.py"
    subprocess.run([
        python, str(harness),
        "--pred", str(PRED_CSV),
        "--gold", str(GOLD_CSV),
        "--history", str(HISTORY_CSV),
    ], check=True)


if __name__ == "__main__":
    main()
