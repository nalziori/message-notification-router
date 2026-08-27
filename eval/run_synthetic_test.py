"""Phase 2: TEST -- read eval/synthetic_cases.csv (written by
generate_synthetic_testset.py), run the real image/audio pipelines and the
real router against it, and score against the hand-assigned expected labels.

This DOES call the Anthropic API: image analysis for each image case (~3
calls) and routing classification for every case (~20 calls). Audio
transcription is local (faster-whisper), $0 either way. Estimated cost:
well under $1 for the full 20-case set (see the resource estimate in the
chat before running this).

Usage:
    python eval/run_synthetic_test.py
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))

import anthropic

import config
import router
from audio_pipeline import process_audio
from db import build_database, get_connection
from image_pipeline import process_image

SYN_DIR = Path(__file__).resolve().parent / "synthetic_media"
CASES_CSV = Path(__file__).resolve().parent / "synthetic_cases.csv"
PRED_CSV = Path(__file__).resolve().parent / "synthetic_predictions.csv"


def main():
    if not CASES_CSV.exists():
        print(f"{CASES_CSV} not found -- run eval/generate_synthetic_testset.py first.")
        sys.exit(1)

    config.require_api_key()
    build_database()
    client = anthropic.Anthropic()
    conn = get_connection()

    with open(CASES_CSV, newline="", encoding="utf-8") as f:
        cases = list(csv.DictReader(f))

    print(f"== Analyzing media for {sum(1 for c in cases if c['media_type'])} case(s) with attachments ==")
    for c in cases:
        if c["media_type"] == "image":
            img_path = SYN_DIR / "images" / f"{c['message_id']}.jpg"
            result = process_image(c["media_id"], img_path, client)
            router.EXTRA_MEDIA_PATHS[c["media_id"]] = ("image", img_path)
            print(f"  [image] [{result.get('status')}] {c['message_id']}: "
                  f"ocr=\"{result.get('ocr_text', '')[:60]}\"")
        elif c["media_type"] == "voice":
            wav_path = SYN_DIR / "audio" / f"{c['message_id']}.wav"
            result = process_audio(c["media_id"], wav_path, [c["message_id"]], [c["user_id"]])
            router.EXTRA_MEDIA_PATHS[c["media_id"]] = ("voice", wav_path)
            print(f"  [voice] [{result.get('status')}] {c['message_id']}: "
                  f"text=\"{result.get('text', '')[:60]}\"")

    print(f"\n== Routing {len(cases)} case(s) ==")
    predictions = []
    for c in cases:
        message_row = {k: c[k] for k in [
            "message_id", "user_id", "conversation_type", "group_id", "business_id",
            "sender_user_id", "created_at", "message_text", "media_type", "media_id", "forwarded_count",
        ]}
        record = router.process_message(message_row, conn, client, force=True)
        row = router.to_output_row(c["message_id"], record)
        row["expected_action"] = c["expected_action"]
        row["expected_type"] = c["expected_type"]
        predictions.append(row)
        marker_a = "OK" if row["action"] == c["expected_action"] else "MISS"
        marker_t = "OK" if row["message_type"] == c["expected_type"] else "MISS"
        print(f"  [{marker_a}/{marker_t}] {c['message_id']}: action={row['action']} "
              f"(exp {c['expected_action']}) type={row['message_type']} (exp {c['expected_type']})")

    conn.close()

    with open(PRED_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(predictions[0].keys()))
        writer.writeheader()
        writer.writerows(predictions)

    n = len(predictions)
    action_ok = sum(1 for r in predictions if r["action"] == r["expected_action"])
    type_ok = sum(1 for r in predictions if r["message_type"] == r["expected_type"])
    print(f"\n=== Synthetic held-out set results ({n} cases) ===")
    print(f"action accuracy:       {action_ok}/{n} = {action_ok/n:.0%}")
    print(f"message_type accuracy: {type_ok}/{n} = {type_ok/n:.0%}")
    print(f"Wrote {PRED_CSV}")


if __name__ == "__main__":
    main()
