"""
Evaluation harness for the Message Notification Router (English version)

Purpose:
- Score your `output.csv` against the 30 solved rows in `dataset/sample_messages.csv`
  as a local proxy for the hidden ground truth used for real grading.
- Catch degenerate strategies early (e.g. always `digest`, always `mute`).
- Catch schema violations that would break automated grading before you submit.
- Validate that `evidence_message_ids` actually exist in `dataset/message_history.csv`
  for the *same* user (hallucinated or cross-user evidence is a real failure mode here).

This does NOT replace the real evaluation — the real ground truth is hidden and also
scores `reason` quality via an AI judge. Use this to catch mechanical bugs and get a
directional read on `action`/`message_type` accuracy before you submit.

Usage:
    python eval_harness_en.py --pred dataset/output.csv --gold dataset/sample_messages.csv \
        --history dataset/message_history.csv
"""

import argparse
import csv
import sys
from collections import Counter

# Force UTF-8 stdout/stderr so non-ASCII output (and en-dashes) render correctly
# regardless of the Windows console's active code page.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_COLUMNS = [
    "message_id",
    "action",
    "message_type",
    "reason",
    "confidence",
    "evidence_message_ids",
]

ALLOWED_ACTIONS = {"notify", "digest", "mute"}

ALLOWED_MESSAGE_TYPES = {
    "personal",
    "urgent",
    "event",
    "payment",
    "business_update",
    "promotion",
    "greeting",
    "forward",
    "spam",
    "scam",
    "unknown",
}


def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_schema(pred_path: str) -> list[str]:
    """Verify output.csv has exactly the required columns, in the required order."""
    errors = []
    with open(pred_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
    if header != REQUIRED_COLUMNS:
        errors.append(
            f"Header mismatch.\n  expected: {REQUIRED_COLUMNS}\n  got:      {header}"
        )
    return errors


def parse_evidence(raw: str) -> set[str]:
    raw = (raw or "").strip()
    if raw == "" or raw.lower() == "none":
        return set()
    return {piece.strip() for piece in raw.split(";") if piece.strip()}


def sanity_check(
    preds: list[dict],
    history_ids_by_user: dict[str, set[str]] | None = None,
) -> None:
    """Flag degenerate strategies, out-of-set labels, bad confidence values, and
    evidence ids that don't actually exist in that user's history."""
    total = len(preds)
    if total == 0:
        print("[warning] predictions file is empty.", file=sys.stderr)
        return

    action_counts = Counter(row["action"] for row in preds)
    for label, count in action_counts.items():
        ratio = count / total
        if ratio > 0.9:
            print(
                f"[warning] action '{label}' makes up {ratio:.0%} of predictions. "
                f"Check the system isn't collapsing onto a single action.",
                file=sys.stderr,
            )

    bad_action = [r["message_id"] for r in preds if r.get("action") not in ALLOWED_ACTIONS]
    if bad_action:
        print(
            f"[error] {len(bad_action)} row(s) have an action outside {ALLOWED_ACTIONS}: "
            f"{bad_action[:5]}...",
            file=sys.stderr,
        )

    bad_type = [
        r["message_id"] for r in preds if r.get("message_type") not in ALLOWED_MESSAGE_TYPES
    ]
    if bad_type:
        print(
            f"[error] {len(bad_type)} row(s) have a message_type outside the allowed set: "
            f"{bad_type[:5]}...",
            file=sys.stderr,
        )

    bad_confidence = []
    for r in preds:
        try:
            c = float(r.get("confidence", ""))
            if not (0.0 <= c <= 1.0):
                bad_confidence.append(r["message_id"])
        except (TypeError, ValueError):
            bad_confidence.append(r["message_id"])
    if bad_confidence:
        print(
            f"[error] {len(bad_confidence)} row(s) have a non-numeric or out-of-range "
            f"confidence (must be 0-1): {bad_confidence[:5]}...",
            file=sys.stderr,
        )

    empty_reason = [r["message_id"] for r in preds if not (r.get("reason") or "").strip()]
    if empty_reason:
        print(
            f"[warning] {len(empty_reason)} row(s) have an empty reason: "
            f"{empty_reason[:5]}...",
            file=sys.stderr,
        )

    if history_ids_by_user is not None:
        hallucinated = []
        for r in preds:
            user_id = r.get("user_id")  # only present if caller merged it in
            evidence = parse_evidence(r.get("evidence_message_ids", ""))
            if not evidence or user_id is None:
                continue
            valid_ids = history_ids_by_user.get(user_id, set())
            bad_ids = evidence - valid_ids
            if bad_ids:
                hallucinated.append((r["message_id"], bad_ids))
        if hallucinated:
            print(
                f"[error] {len(hallucinated)} row(s) cite evidence_message_ids not found in "
                f"that user's message_history.csv (hallucinated or cross-user evidence): "
                f"{hallucinated[:3]}...",
                file=sys.stderr,
            )


def score(
    preds: list[dict],
    golds: list[dict],
    id_col: str = "message_id",
) -> dict:
    """Compare predictions to the solved sample rows: action/type accuracy, evidence
    overlap, and confidence calibration. This scores a 30-row local sample, not the
    real hidden test set — treat the numbers as directional, not final."""
    gold_map = {row[id_col]: row for row in golds}
    pred_map = {row[id_col]: row for row in preds}

    missing = set(gold_map) - set(pred_map)
    if missing:
        print(f"[warning] {len(missing)} sample id(s) missing from predictions: {sorted(missing)}")

    action_correct = 0
    type_correct = 0
    evidence_f1_sum = 0.0
    confusion = Counter()
    scored = 0

    for _id, gold in gold_map.items():
        pred = pred_map.get(_id)
        if pred is None:
            continue
        scored += 1

        gold_action, pred_action = gold["action"], pred.get("action")
        confusion[(gold_action, pred_action)] += 1
        if pred_action == gold_action:
            action_correct += 1

        if pred.get("message_type") == gold["message_type"]:
            type_correct += 1

        gold_evidence = parse_evidence(gold.get("evidence_message_ids", ""))
        pred_evidence = parse_evidence(pred.get("evidence_message_ids", ""))
        if not gold_evidence and not pred_evidence:
            evidence_f1_sum += 1.0
        elif not gold_evidence or not pred_evidence:
            evidence_f1_sum += 0.0
        else:
            overlap = len(gold_evidence & pred_evidence)
            precision = overlap / len(pred_evidence)
            recall = overlap / len(gold_evidence)
            f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
            evidence_f1_sum += f1

    return {
        "n_gold": len(gold_map),
        "n_scored": scored,
        "n_missing": len(missing),
        "action_accuracy": action_correct / scored if scored else 0.0,
        "message_type_accuracy": type_correct / scored if scored else 0.0,
        "evidence_f1_avg": evidence_f1_sum / scored if scored else 0.0,
        "confusion": confusion,
    }


def eval_loop_reminder() -> None:
    print(
        "\n[reminder] Don't just look at the accuracy numbers above — open the rows "
        "marked MISS below and figure out why. This 30-row sample is a small, non-hidden "
        "proxy: strong action/message_type accuracy here doesn't guarantee it on the hidden "
        "set, and it says nothing about reason quality, which the AI judge scores separately. "
        "Log each iteration in the 'Eval Loop Log' section of CLAUDE.en.md / CLAUDE.ko.md.",
        file=sys.stderr,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Score router output against dataset/sample_messages.csv"
    )
    parser.add_argument("--pred", required=True, help="Path to your output.csv")
    parser.add_argument(
        "--gold", default="dataset/sample_messages.csv", help="Path to the solved sample rows"
    )
    parser.add_argument(
        "--history",
        default="dataset/message_history.csv",
        help="Path to message_history.csv, used to validate evidence ids per user",
    )
    parser.add_argument("--id-col", default="message_id")
    args = parser.parse_args()

    schema_errors = check_schema(args.pred)
    for e in schema_errors:
        print(f"[error] {e}", file=sys.stderr)
    if schema_errors:
        print(
            "[error] Fix the header before continuing — a header mismatch will break "
            "automated grading.",
            file=sys.stderr,
        )
        sys.exit(1)

    preds = load_csv(args.pred)
    golds = load_csv(args.gold)

    # Build user_id -> valid history message_id set, then merge user_id onto preds via
    # the input messages file so sanity_check can validate evidence per user.
    history_ids_by_user: dict[str, set[str]] = {}
    try:
        history_rows = load_csv(args.history)
        for row in history_rows:
            history_ids_by_user.setdefault(row["user_id"], set()).add(row["message_id"])
    except FileNotFoundError:
        history_ids_by_user = {}
        print(f"[warning] history file not found at {args.history}, skipping evidence validation.")

    # gold rows carry user_id already (same schema as messages.csv); use that to
    # attach user_id onto matching predictions for evidence validation.
    gold_user_map = {row[args.id_col]: row.get("user_id") for row in golds}
    for row in preds:
        if row[args.id_col] in gold_user_map:
            row["user_id"] = gold_user_map[row[args.id_col]]

    sanity_check(preds, history_ids_by_user=history_ids_by_user if history_ids_by_user else None)
    result = score(preds, golds, id_col=args.id_col)

    print(f"\nScored {result['n_scored']} / {result['n_gold']} sample rows "
          f"({result['n_missing']} missing)")
    print(f"action accuracy:        {result['action_accuracy']:.2%}")
    print(f"message_type accuracy:  {result['message_type_accuracy']:.2%}")
    print(f"evidence F1 (avg):      {result['evidence_f1_avg']:.2%}")
    print("\nAction confusion (gold, pred) -> count:")
    for (gold_label, pred_label), count in sorted(
        result["confusion"].items(), key=lambda x: -x[1]
    ):
        marker = "OK" if gold_label == pred_label else "MISS"
        print(f"  [{marker}] {gold_label} -> {pred_label}: {count}")

    eval_loop_reminder()


if __name__ == "__main__":
    main()
