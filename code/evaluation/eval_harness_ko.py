"""
Message Notification Router 평가 하네스 (한국어 버전)

목적:
- `output.csv`를 `dataset/sample_messages.csv`의 정답 30건과 비교해,
  실제 채점에 쓰이는 히든 정답에 대한 로컬 대리 지표로 삼는다.
- 극단적 전략(항상 `digest`, 항상 `mute` 등)을 조기에 발견한다.
- 제출 전에 자동 채점을 깨뜨릴 스키마 위반을 미리 잡는다.
- `evidence_message_ids`가 **동일 사용자**의 `dataset/message_history.csv`에 실제로
  존재하는지 검증한다(가짜 근거나 다른 사용자의 이력을 인용하는 것은 이 과제에서
  실제로 자주 발생하는 실패 유형이다).

주의: 이 스크립트는 실제 평가를 대체하지 않는다. 실제 정답은 히든 상태이며
`reason`의 품질은 AI judge가 별도로 채점한다. 제출 전 기계적인 버그를 잡고
`action`/`message_type` 정확도를 방향성 있게 가늠하는 용도로만 사용한다.

사용법:
    python eval_harness_ko.py --pred dataset/output.csv --gold dataset/sample_messages.csv \
        --history dataset/message_history.csv
"""

import argparse
import csv
import sys
from collections import Counter

# Windows 콘솔 코드페이지(cp949 등)에서 한글이 깨져 보이는 것을 방지한다.
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
    """output.csv의 컬럼이 요구된 순서/구성과 정확히 일치하는지 확인한다."""
    errors = []
    with open(pred_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
    if header != REQUIRED_COLUMNS:
        errors.append(
            f"헤더 불일치.\n  기대값: {REQUIRED_COLUMNS}\n  실제값: {header}"
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
    """극단적 전략, 허용되지 않은 라벨, 잘못된 confidence 값,
    그리고 해당 사용자 이력에 실존하지 않는 evidence id를 경고한다."""
    total = len(preds)
    if total == 0:
        print("[경고] 예측 파일이 비어 있습니다.", file=sys.stderr)
        return

    action_counts = Counter(row["action"] for row in preds)
    for label, count in action_counts.items():
        ratio = count / total
        if ratio > 0.9:
            print(
                f"[경고] action '{label}'이(가) 전체의 {ratio:.0%}를 차지합니다. "
                f"단일 action으로 몰아 찍고 있지 않은지 확인하세요.",
                file=sys.stderr,
            )

    bad_action = [r["message_id"] for r in preds if r.get("action") not in ALLOWED_ACTIONS]
    if bad_action:
        print(
            f"[오류] {len(bad_action)}건의 action이 허용 범위({ALLOWED_ACTIONS})를 벗어났습니다: "
            f"{bad_action[:5]}...",
            file=sys.stderr,
        )

    bad_type = [
        r["message_id"] for r in preds if r.get("message_type") not in ALLOWED_MESSAGE_TYPES
    ]
    if bad_type:
        print(
            f"[오류] {len(bad_type)}건의 message_type이 허용 목록을 벗어났습니다: "
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
            f"[오류] {len(bad_confidence)}건의 confidence가 숫자가 아니거나 0~1 범위를 "
            f"벗어났습니다: {bad_confidence[:5]}...",
            file=sys.stderr,
        )

    empty_reason = [r["message_id"] for r in preds if not (r.get("reason") or "").strip()]
    if empty_reason:
        print(
            f"[경고] {len(empty_reason)}건의 reason이 비어 있습니다: "
            f"{empty_reason[:5]}...",
            file=sys.stderr,
        )

    if history_ids_by_user is not None:
        hallucinated = []
        for r in preds:
            user_id = r.get("user_id")  # 호출자가 병합해 넣은 경우에만 존재
            evidence = parse_evidence(r.get("evidence_message_ids", ""))
            if not evidence or user_id is None:
                continue
            valid_ids = history_ids_by_user.get(user_id, set())
            bad_ids = evidence - valid_ids
            if bad_ids:
                hallucinated.append((r["message_id"], bad_ids))
        if hallucinated:
            print(
                f"[오류] {len(hallucinated)}건이 해당 사용자의 message_history.csv에 없는 "
                f"evidence_message_ids를 인용했습니다(허위 근거 또는 다른 사용자 이력 인용 가능성): "
                f"{hallucinated[:3]}...",
                file=sys.stderr,
            )


def score(
    preds: list[dict],
    golds: list[dict],
    id_col: str = "message_id",
) -> dict:
    """예측 결과를 정답이 채워진 샘플 행과 비교한다: action/type 정확도,
    evidence 겹침 정도, confidence 보정 상태. 이는 30건짜리 로컬 샘플 채점이며
    실제 히든 테스트셋 채점이 아니므로, 수치는 최종이 아닌 방향성 참고용이다."""
    gold_map = {row[id_col]: row for row in golds}
    pred_map = {row[id_col]: row for row in preds}

    missing = set(gold_map) - set(pred_map)
    if missing:
        print(f"[경고] {len(missing)}개의 샘플 id가 예측 결과에서 누락됨: {sorted(missing)}")

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
        "\n[리마인더] 위 정확도 수치만 보지 말고, 아래 MISS로 표시된 케이스를 직접 열어 "
        "왜 틀렸는지 확인하세요. 이 30건 샘플은 히든셋이 아닌 작은 로컬 대리 지표입니다 — "
        "여기서 action/message_type 정확도가 높다고 해서 히든셋에서도 그렇다는 보장은 없고, "
        "AI judge가 별도로 채점하는 reason 품질에 대해서는 아무것도 말해주지 않습니다. "
        "각 반복은 CLAUDE.ko.md / CLAUDE.en.md의 '평가 루프 로그' 섹션에 기록하세요.",
        file=sys.stderr,
    )


def main():
    parser = argparse.ArgumentParser(
        description="라우터 출력을 dataset/sample_messages.csv 대비 채점"
    )
    parser.add_argument("--pred", required=True, help="output.csv 경로")
    parser.add_argument(
        "--gold", default="dataset/sample_messages.csv", help="정답이 채워진 샘플 파일 경로"
    )
    parser.add_argument(
        "--history",
        default="dataset/message_history.csv",
        help="사용자별 evidence id 검증에 쓰이는 message_history.csv 경로",
    )
    parser.add_argument("--id-col", default="message_id")
    args = parser.parse_args()

    schema_errors = check_schema(args.pred)
    for e in schema_errors:
        print(f"[오류] {e}", file=sys.stderr)
    if schema_errors:
        print(
            "[오류] 계속하기 전에 헤더부터 고치세요 — 헤더가 다르면 자동 채점이 깨집니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    preds = load_csv(args.pred)
    golds = load_csv(args.gold)

    # user_id -> 유효한 history message_id 집합을 만든 뒤, 입력 messages 파일 기준으로
    # user_id를 예측 결과에 병합해 sanity_check가 사용자별 evidence를 검증할 수 있게 한다.
    history_ids_by_user: dict[str, set[str]] = {}
    try:
        history_rows = load_csv(args.history)
        for row in history_rows:
            history_ids_by_user.setdefault(row["user_id"], set()).add(row["message_id"])
    except FileNotFoundError:
        history_ids_by_user = {}
        print(f"[경고] {args.history} 경로에 history 파일이 없어 evidence 검증을 건너뜁니다.")

    # gold 행에는 이미 user_id가 있으므로(messages.csv와 동일 스키마), 이를 이용해
    # 매칭되는 예측 결과에 user_id를 붙여 evidence 검증에 사용한다.
    gold_user_map = {row[args.id_col]: row.get("user_id") for row in golds}
    for row in preds:
        if row[args.id_col] in gold_user_map:
            row["user_id"] = gold_user_map[row[args.id_col]]

    sanity_check(preds, history_ids_by_user=history_ids_by_user if history_ids_by_user else None)
    result = score(preds, golds, id_col=args.id_col)

    print(f"\n{result['n_gold']}건 중 {result['n_scored']}건 채점 완료 "
          f"(누락 {result['n_missing']}건)")
    print(f"action 정확도:          {result['action_accuracy']:.2%}")
    print(f"message_type 정확도:    {result['message_type_accuracy']:.2%}")
    print(f"evidence F1 (평균):      {result['evidence_f1_avg']:.2%}")
    print("\naction 혼동 행렬 (gold, pred) -> count:")
    for (gold_label, pred_label), count in sorted(
        result["confusion"].items(), key=lambda x: -x[1]
    ):
        marker = "OK" if gold_label == pred_label else "MISS"
        print(f"  [{marker}] {gold_label} -> {pred_label}: {count}")

    eval_loop_reminder()


if __name__ == "__main__":
    main()
