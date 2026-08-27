"""Phase 1: GENERATE a held-out synthetic test set (~20 messages spanning
text/image/voice) with hand-assigned expected labels. No Anthropic API calls
here -- images are drawn locally with Pillow, voice notes are synthesized
locally with Windows SAPI TTS. Free and instant. Writes:
  - eval/synthetic_media/images/*.jpg, eval/synthetic_media/audio/*.wav
  - eval/synthetic_cases.csv (the message specs + expected labels)

Run eval/run_synthetic_test.py separately (a deliberate second step, since
that phase DOES call the Anthropic API: image analysis + routing
classification for these 20 cases) once you're ready to spend on it.

This is independent of sample_messages.csv (which the routing prompt has
already been tuned against) -- a fresh set is the honest way to check the
prompt changes generalize rather than just fitting the 30 visible examples.
Every message reuses REAL user_id/group_id/business_id/sender_user_id values
already in dataset/*.csv, so the router's context lookups resolve normally
through the real SQLite DB with no schema changes needed.

Usage:
    python eval/generate_synthetic_testset.py
"""

import csv
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SYN_DIR = Path(__file__).resolve().parent / "synthetic_media"
SYN_IMAGES = SYN_DIR / "images"
SYN_AUDIO = SYN_DIR / "audio"
SYN_IMAGES.mkdir(parents=True, exist_ok=True)
SYN_AUDIO.mkdir(parents=True, exist_ok=True)

CASES_CSV = Path(__file__).resolve().parent / "synthetic_cases.csv"

FIELDNAMES = [
    "message_id", "user_id", "conversation_type", "group_id", "business_id",
    "sender_user_id", "created_at", "message_text", "media_type", "media_id",
    "forwarded_count", "expected_action", "expected_type",
]


def make_poster(path: Path, lines: list[str], bg=(255, 237, 213), fg=(120, 53, 15)):
    im = Image.new("RGB", (900, 700), bg)
    draw = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("arial.ttf", 34)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = font_small = ImageFont.load_default()
    y = 60
    for i, line in enumerate(lines):
        f = font if i == 0 else font_small
        draw.text((50, y), line, fill=fg, font=f)
        y += 60
    im.save(path, "JPEG", quality=90)


def make_voice(path: Path, text: str):
    ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice("Microsoft Zira Desktop")
$synth.SetOutputToWaveFile("{path.as_posix()}")
$synth.Speak({text!r})
$synth.Dispose()
'''
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_script], check=True, capture_output=True)


# Each entry: input fields (matching messages.csv schema) + our own expected
# action/message_type for later scoring, + optional media spec to generate.
CASES = [
    dict(mid="synth_msg_01", user_id="u_002", conversation_type="personal", sender_user_id="u_017",
         text="Hey, are we still on for dinner tonight around 8? No rush, just checking.",
         expected_action="digest", expected_type="personal"),
    dict(mid="synth_msg_02", user_id="u_002", conversation_type="personal", sender_user_id="u_017",
         text="Emergency -- I'm locked out and the landlord isn't picking up. Can you call me back right now?",
         expected_action="notify", expected_type="urgent"),
    dict(mid="synth_msg_03", user_id="u_002", conversation_type="group", group_id="group_003", sender_user_id="u_045",
         text="Route B parents: pickup moved to 3:45 today because of the assembly, please plan accordingly.",
         expected_action="notify", expected_type="event"),
    dict(mid="synth_msg_04", user_id="u_002", conversation_type="group", group_id="group_003", sender_user_id="u_017",
         text="Selling a barely-used badminton racket, good condition. Pickup near the school gate this Friday if anyone wants it.",
         expected_action="digest", expected_type="promotion"),
    dict(mid="synth_msg_05", user_id="u_002", conversation_type="group", group_id="group_001", sender_user_id="u_013",
         text="Good morning family! Hope everyone has a peaceful and blessed day today.",
         expected_action="digest", expected_type="greeting"),
    dict(mid="synth_msg_06", user_id="u_002", conversation_type="group", group_id="group_001", sender_user_id="u_007",
         text="Fwd: Doctors say drinking warm turmeric water every morning boosts immunity, please share with family.",
         expected_action="mute", expected_type="forward", forwarded_count="9"),
    dict(mid="synth_msg_08", user_id="u_008", conversation_type="business", business_id="business_011",
         text="Hi! A new arrival just dropped in your size based on your last order. Check it out in the app.",
         expected_action="digest", expected_type="promotion"),
    dict(mid="synth_msg_09", user_id="u_005", conversation_type="business", business_id="business_062",
         text="URGENT: Your bank account will be suspended in 2 hours. Reply with your debit card number and OTP to verify and avoid suspension.",
         expected_action="mute", expected_type="scam"),
    dict(mid="synth_msg_10", user_id="u_005", conversation_type="business", business_id="business_041",
         text="CONGRATULATIONS you have been selected!! Claim your free prize now by clicking the link and entering your details!!!",
         expected_action="mute", expected_type="spam"),
    dict(mid="synth_msg_11", user_id="u_002", conversation_type="personal", sender_user_id="u_090",
         text="hi, saw your post about tutoring, do you still have slots open",
         expected_action="digest", expected_type="unknown"),
    dict(mid="synth_msg_12", user_id="u_002", conversation_type="group", group_id="group_003", sender_user_id="u_045",
         text="@u_002 quick one -- can you send the signed consent form before 5pm today? Office closes early.",
         expected_action="notify", expected_type="urgent"),
    dict(mid="synth_msg_13", user_id="u_001", conversation_type="business", business_id="business_001",
         text="Your order has been delivered. Thanks for shopping with us!",
         expected_action="digest", expected_type="business_update"),
    dict(mid="synth_msg_14", user_id="u_002", conversation_type="group", group_id="group_001", sender_user_id="u_007",
         text="Fwd: Fwd: Fwd: this message has been forwarded many times, click here to win a free iPhone, forward to 10 people to activate",
         expected_action="mute", expected_type="spam", forwarded_count="47"),
    dict(mid="synth_msg_15", user_id="u_002", conversation_type="business", business_id="business_011",
         text="", media_type="image", media_id="synth_img_promo",
         image_lines=["MEGA SALE", "Flat 60% OFF", "Ends tonight!", "Use code SAVE60"],
         expected_action="digest", expected_type="promotion"),
    dict(mid="synth_msg_16", user_id="u_005", conversation_type="business", business_id="business_062",
         text="", media_type="image", media_id="synth_img_scam",
         image_lines=["SECURITY ALERT", "Unusual login detected", "Verify your OTP now", "or account will be locked"],
         expected_action="mute", expected_type="scam"),
    dict(mid="synth_msg_17", user_id="u_002", conversation_type="group", group_id="group_001", sender_user_id="u_013",
         text="", media_type="image", media_id="synth_img_photo",
         image_lines=["Family Dinner", "Sunday 7pm", "at grandma's place"],
         expected_action="digest", expected_type="event"),
    dict(mid="synth_msg_18", user_id="u_002", conversation_type="personal", sender_user_id="u_017",
         text="", media_type="voice", media_id="synth_vn_casual",
         voice_text="Hey it's me, just checking in, nothing urgent, call me whenever you get a chance.",
         expected_action="digest", expected_type="personal"),
    dict(mid="synth_msg_19", user_id="u_002", conversation_type="personal", sender_user_id="u_017",
         text="", media_type="voice", media_id="synth_vn_urgent",
         voice_text="Please call me back right away, something came up and I really need your help in the next few minutes.",
         expected_action="notify", expected_type="urgent"),
    dict(mid="synth_msg_20", user_id="u_005", conversation_type="business", business_id="business_062",
         text="", media_type="voice", media_id="synth_vn_scam",
         voice_text="This is your bank calling. Your account has suspicious activity. Please say your one time password now to secure your account.",
         expected_action="mute", expected_type="scam"),
]


def main():
    rows = []
    for c in CASES:
        if c.get("media_type") == "image":
            img_path = SYN_IMAGES / f"{c['mid']}.jpg"
            make_poster(img_path, c["image_lines"])
            print(f"  [image]  {img_path.relative_to(Path(__file__).resolve().parent.parent)}  "
                  f"(text drawn: {' / '.join(c['image_lines'])})")
        elif c.get("media_type") == "voice":
            wav_path = SYN_AUDIO / f"{c['mid']}.wav"
            make_voice(wav_path, c["voice_text"])
            size_kb = wav_path.stat().st_size / 1024
            print(f"  [voice]  {wav_path.relative_to(Path(__file__).resolve().parent.parent)}  "
                  f"({size_kb:.0f} KB, script: \"{c['voice_text'][:60]}...\")")
        else:
            print(f"  [text]   {c['mid']}: \"{c['text'][:70]}\"")

        rows.append({
            "message_id": c["mid"],
            "user_id": c["user_id"],
            "conversation_type": c["conversation_type"],
            "group_id": c.get("group_id", ""),
            "business_id": c.get("business_id", ""),
            "sender_user_id": c.get("sender_user_id", ""),
            "created_at": "2026-08-01 12:00",
            "message_text": c.get("text", ""),
            "media_type": c.get("media_type", ""),
            "media_id": c.get("media_id", ""),
            "forwarded_count": c.get("forwarded_count", "0"),
            "expected_action": c["expected_action"],
            "expected_type": c["expected_type"],
        })

    with open(CASES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    n_text = sum(1 for c in CASES if not c.get("media_type"))
    n_img = sum(1 for c in CASES if c.get("media_type") == "image")
    n_voice = sum(1 for c in CASES if c.get("media_type") == "voice")
    print(f"\n=== Generated {len(rows)} cases: {n_text} text-only, {n_img} image, {n_voice} voice ===")
    print(f"Wrote {CASES_CSV}")
    print("No Anthropic API calls were made in this step.")
    print("Next: eval/run_synthetic_test.py (this WILL call the API -- image analysis + routing).")


if __name__ == "__main__":
    main()
