"""Render the 19 synthetic cases for human labelling.

Each case is shown as the router actually assembles it -- the same context
block that goes to the model -- so a label assigned here is a label on the
same input the model gets. Anything less (labelling from the message text
alone) produces labels the router cannot be fairly scored against.

August's labels are deliberately NOT shown: they were assigned against the
challenge dataset's context, which is gone, and showing them would anchor the
new pass. Run compare_labels.py afterwards to diff the two and surface the
cases where the context change actually moved the answer.

No API key, no network, no challenge dataset needed. Media analysis is read
from the existing cache; cases whose media was never analysed are marked so.

    python fixtures/label_sheet.py            -> fixtures/LABEL_SHEET.md
"""

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "code"))

import config  # noqa: E402
import router  # noqa: E402
from cache import content_hash  # noqa: E402
from db import build_database, get_connection  # noqa: E402

FIXTURE_DATA = HERE / "dataset"
FIXTURE_DB = HERE / "fixture.db"
CASES = ROOT / "eval" / "synthetic_cases.csv"
SYN_MEDIA = ROOT / "eval" / "synthetic_media"
OUT = HERE / "LABEL_SHEET.md"

ACTIONS = "notify | digest | mute"
TYPES = ("personal, urgent, event, payment, business_update, promotion, "
         "greeting, forward, spam, scam, unknown")


def register_media(cases):
    """Point the router at the synthetic media by absolute path, the same way
    eval/run_synthetic_test.py does -- these files were never in images.csv /
    voice_notes.csv, so the normal manifest lookup can't find them."""
    found = 0
    for c in cases:
        if not c["media_type"]:
            continue
        sub, ext = ("images", "jpg") if c["media_type"] == "image" else ("audio", "wav")
        path = SYN_MEDIA / sub / f"{c['message_id']}.{ext}"
        if path.exists():
            router.EXTRA_MEDIA_PATHS[c["media_id"]] = (c["media_type"], path)
            found += 1
    return found


def media_summary(case):
    """Read the cached analysis for this case's media, if it was ever analysed.
    Returns a display string, or None when there is no media."""
    if not case["media_type"]:
        return None
    sub, ext = ("images", "jpg") if case["media_type"] == "image" else ("audio", "wav")
    path = SYN_MEDIA / sub / f"{case['message_id']}.{ext}"
    if not path.exists():
        return "(미디어 파일 없음)"
    cache_dir = config.IMAGE_CACHE_DIR if case["media_type"] == "image" else config.AUDIO_CACHE_DIR
    rec_path = cache_dir / f"{content_hash(path)}.json"
    if not rec_path.exists():
        return "(아직 분석 안 됨 — preprocess 필요)"
    rec = json.loads(rec_path.read_text(encoding="utf-8"))
    if case["media_type"] == "image":
        ocr = (rec.get("ocr_text") or "").replace("\n", " / ")
        return f"[{rec.get('doc_type')}] {rec.get('short_description', '')}\n  - OCR: {ocr}"
    return f"음성 전사: \"{rec.get('text', '')}\""


def main():
    if not CASES.exists():
        sys.exit(f"{CASES} not found")

    with open(CASES, newline="", encoding="utf-8") as f:
        cases = list(csv.DictReader(f))

    build_database(dataset_dir=FIXTURE_DATA, db_path=FIXTURE_DB)
    n_media = register_media(cases)
    conn = get_connection(FIXTURE_DB)

    out = [
        "# 합성 케이스 19건 — 라벨링 시트",
        "",
        "각 케이스는 **라우터가 실제로 모델에게 보내는 컨텍스트 그대로**입니다.",
        "아래 `action:` / `message_type:` 옆 빈칸을 채우세요.",
        "",
        f"- action: `{ACTIONS}`",
        f"- message_type: `{TYPES}`",
        "",
        "판단이 갈리면 `note:`에 왜 애매한지 한 줄 남겨 주세요 — 그 자체가 유용한 신호입니다.",
        "8월 라벨은 일부러 숨겼습니다(앵커링 방지). 채운 뒤 `compare_labels.py`로 대조합니다.",
        "",
        "---",
        "",
    ]

    for i, c in enumerate(cases, 1):
        message_row = {k: c[k] for k in (
            "message_id", "user_id", "conversation_type", "group_id", "business_id",
            "sender_user_id", "created_at", "message_text", "media_type", "media_id",
            "forwarded_count")}
        ctx = router.pull_context(conn, message_row)
        block = router.build_context_block(ctx)

        out.append(f"## {i}. `{c['message_id']}`")
        out.append("")
        media = media_summary(c)
        if media:
            out.append(f"**첨부 {c['media_type']}**: {media}")
            out.append("")
        out.append("```")
        out.append(block)
        out.append("```")
        out.append("")
        out.append("```yaml")
        out.append(f"message_id:   {c['message_id']}")
        out.append("action:       ")
        out.append("message_type: ")
        out.append("note:         ")
        out.append("```")
        out.append("")
        out.append("---")
        out.append("")

    conn.close()
    OUT.write_text("\n".join(out), encoding="utf-8")

    print(f"  cases: {len(cases)}")
    print(f"  media registered: {n_media}")
    print(f"  wrote {OUT}  ({OUT.stat().st_size:,} bytes)")
    print("\n라벨을 채운 뒤: python fixtures/compare_labels.py")


if __name__ == "__main__":
    main()
