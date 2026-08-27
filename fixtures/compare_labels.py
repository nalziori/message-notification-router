"""Read the filled-in LABEL_SHEET.md, diff it against August's labels, and
write the result as the fixture set's ground truth.

The diff is the point. August's labels were assigned against the challenge
dataset's context; these are assigned against the fixture context. Where they
agree, the label was carried by the message text and the case is context-robust.
Where they disagree, the context genuinely decided the answer -- those are the
cases worth reading twice, because one of the two contexts is telling a
different story about the same message.

    python fixtures/compare_labels.py           -> report + fixtures/dataset/messages.csv
    python fixtures/compare_labels.py --check   -> report only, exit 1 if unlabelled
"""

import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHEET = HERE / "LABEL_SHEET.md"
CASES = ROOT / "eval" / "synthetic_cases.csv"
OUT_MESSAGES = HERE / "dataset" / "messages.csv"
OUT_TRUTH = HERE / "expected_labels.csv"

ALLOWED_ACTIONS = {"notify", "digest", "mute"}
ALLOWED_TYPES = {
    "personal", "urgent", "event", "payment", "business_update", "promotion",
    "greeting", "forward", "spam", "scam", "unknown",
}

# [^\n]* rather than (.*?) with DOTALL: an unfilled "action:" is an empty
# value, and a dot-matches-newline group would swallow the next lines whole,
# reporting the rest of the block as this field's content.
BLOCK = re.compile(
    r"```yaml\n"
    r"message_id:[ \t]*([^\n]*)\n"
    r"action:[ \t]*([^\n]*)\n"
    r"message_type:[ \t]*([^\n]*)\n"
    r"note:[ \t]*([^\n]*)\n"
    r"```"
)


def parse_sheet(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    out = {}
    for mid, action, mtype, note in BLOCK.findall(text):
        out[mid] = {
            "action": action.strip(),
            "message_type": mtype.strip(),
            "note": note.strip(),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, don't write files")
    args = ap.parse_args()

    if not SHEET.exists():
        sys.exit(f"{SHEET} not found -- run fixtures/label_sheet.py first")

    labels = parse_sheet(SHEET)
    with open(CASES, newline="", encoding="utf-8") as f:
        cases = list(csv.DictReader(f))

    blank, bad = [], []
    for c in cases:
        lab = labels.get(c["message_id"])
        if lab is None:
            bad.append((c["message_id"], "시트에 블록 없음"))
        elif not lab["action"] or not lab["message_type"]:
            blank.append(c["message_id"])
        else:
            if lab["action"] not in ALLOWED_ACTIONS:
                bad.append((c["message_id"], f"action='{lab['action']}' 허용값 아님"))
            if lab["message_type"] not in ALLOWED_TYPES:
                bad.append((c["message_id"], f"message_type='{lab['message_type']}' 허용값 아님"))

    if blank:
        print(f"[대기] {len(blank)}/{len(cases)}건이 아직 비어 있습니다: {', '.join(blank)}")
    for mid, why in bad:
        print(f"[오류] {mid}: {why}")
    if bad or blank:
        print("\n채운 뒤 다시 실행하세요.")
        sys.exit(1)

    agree_a = agree_t = 0
    moved = []
    for c in cases:
        lab = labels[c["message_id"]]
        a_same = lab["action"] == c["expected_action"]
        t_same = lab["message_type"] == c["expected_type"]
        agree_a += a_same
        agree_t += t_same
        if not (a_same and t_same):
            moved.append((c["message_id"], c["expected_action"], c["expected_type"],
                          lab["action"], lab["message_type"], lab["note"]))

    n = len(cases)
    print(f"== 8월 라벨 대비 ({n}건) ==")
    print(f"  action 일치:       {agree_a}/{n}")
    print(f"  message_type 일치: {agree_t}/{n}")

    if moved:
        print(f"\n== 달라진 {len(moved)}건 — 컨텍스트가 답을 바꾼 케이스 ==")
        for mid, oa, ot, na, nt, note in moved:
            print(f"  {mid}: {oa}/{ot}  ->  {na}/{nt}")
            if note:
                print(f"      note: {note}")
        print("\n  이 케이스들은 두 번 읽을 값이 있습니다 — 같은 메시지에 대해")
        print("  두 컨텍스트가 서로 다른 이야기를 하고 있다는 뜻입니다.")
    else:
        print("\n  전부 일치 — 19건 모두 메시지 본문만으로 라벨이 정해졌다는 뜻입니다.")
        print("  컨텍스트가 판단에 기여하지 않는 세트라면 테스트로서는 약합니다;")
        print("  다음 세트는 컨텍스트가 답을 가르는 케이스를 의도적으로 넣으세요.")

    if args.check:
        return

    fieldnames = ["message_id", "user_id", "conversation_type", "group_id",
                  "business_id", "sender_user_id", "created_at", "message_text",
                  "media_type", "media_id", "forwarded_count"]
    with open(OUT_MESSAGES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows({k: c[k] for k in fieldnames} for c in cases)

    with open(OUT_TRUTH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["message_id", "action", "message_type", "note"])
        for c in cases:
            lab = labels[c["message_id"]]
            w.writerow([c["message_id"], lab["action"], lab["message_type"], lab["note"]])

    print(f"\n  wrote {OUT_MESSAGES}")
    print(f"  wrote {OUT_TRUTH}")


if __name__ == "__main__":
    main()
