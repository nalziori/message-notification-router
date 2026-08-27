# -*- coding: utf-8 -*-
"""Build the AI Judge interview-prep report as two PDFs (English, Korean).

Usage:
    python docs/build_report_pdf.py
Writes docs/agent_workflow_report_en.pdf and docs/agent_workflow_report_ko.pdf
"""

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, PageBreak, KeepTogether, HRFlowable,
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

# ---------------------------------------------------------------- fonts ----
KOREAN_FONT = "MalgunGothic"
KOREAN_FONT_BOLD = "MalgunGothic-Bold"
pdfmetrics.registerFont(TTFont(KOREAN_FONT, r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont(KOREAN_FONT_BOLD, r"C:\Windows\Fonts\malgunbd.ttf"))

ACCENT = colors.HexColor("#1f6f78")
ACCENT_DARK = colors.HexColor("#14464d")
INK = colors.HexColor("#1a1d24")
MUTED = colors.HexColor("#5b6270")
OK = colors.HexColor("#2f9e6e")
MISS = colors.HexColor("#c0374b")
ROW_ALT = colors.HexColor("#f2f5f6")
BORDER = colors.HexColor("#d8dee0")


def make_styles(lang: str):
    base_font = KOREAN_FONT if lang == "ko" else "Helvetica"
    bold_font = KOREAN_FONT_BOLD if lang == "ko" else "Helvetica-Bold"
    ss = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle("TitleX", parent=ss["Title"], fontName=bold_font,
                                 fontSize=22, leading=27, textColor=ACCENT_DARK, spaceAfter=4),
        "Subtitle": ParagraphStyle("SubtitleX", parent=ss["Normal"], fontName=base_font,
                                    fontSize=11, leading=15, textColor=MUTED, spaceAfter=18),
        "H1": ParagraphStyle("H1X", parent=ss["Heading1"], fontName=bold_font,
                              fontSize=15, leading=19, textColor=ACCENT_DARK,
                              spaceBefore=18, spaceAfter=8, borderWidth=0),
        "H2": ParagraphStyle("H2X", parent=ss["Heading2"], fontName=bold_font,
                              fontSize=12, leading=15, textColor=INK, spaceBefore=12, spaceAfter=5),
        "Body": ParagraphStyle("BodyX", parent=ss["Normal"], fontName=base_font,
                                fontSize=9.3, leading=13.5, textColor=INK, spaceAfter=6),
        "BodySmall": ParagraphStyle("BodySmallX", parent=ss["Normal"], fontName=base_font,
                                     fontSize=8.3, leading=11.5, textColor=MUTED, spaceAfter=4),
        "Bullet": ParagraphStyle("BulletX", parent=ss["Normal"], fontName=base_font,
                                  fontSize=9.3, leading=13.5, textColor=INK, spaceAfter=3),
        "Caption": ParagraphStyle("CaptionX", parent=ss["Normal"], fontName=base_font,
                                   fontSize=8, leading=11, textColor=MUTED, spaceBefore=2, spaceAfter=10,
                                   alignment=1),
        "TableHead": ParagraphStyle("TableHeadX", parent=ss["Normal"], fontName=bold_font,
                                     fontSize=8.6, leading=11, textColor=colors.white),
        "TableCell": ParagraphStyle("TableCellX", parent=ss["Normal"], fontName=base_font,
                                     fontSize=8.4, leading=11.5, textColor=INK),
        "TableCellSmall": ParagraphStyle("TableCellSmallX", parent=ss["Normal"], fontName=base_font,
                                          fontSize=7.7, leading=10.5, textColor=MUTED),
    }
    return styles


def p(text, style):
    return Paragraph(text, style)


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(t, style), bulletColor=ACCENT, value="bulletchar") for t in items],
        bulletType="bullet", start="\u2022", leftIndent=14, bulletFontSize=8,
    )


def rich_table(header, rows, styles, col_widths=None, cell_style_key="TableCell"):
    data = [[Paragraph(h, styles["TableHead"]) for h in header]]
    for r in rows:
        data.append([Paragraph(str(c), styles[cell_style_key]) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def hr():
    return HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceBefore=6, spaceAfter=6)


def diagram_flowable(max_width_mm=170):
    try:
        from svglib.svglib import svg2rlg
        drawing = svg2rlg(str(REPO_ROOT / "docs" / "pipeline.svg"))
        scale = (max_width_mm * mm) / drawing.width
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
        return drawing
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] could not embed pipeline.svg: {e}", file=sys.stderr)
        return None


# ============================================================== CONTENT ====
# Content is defined once per language as a list of ("kind", payload) tuples,
# rendered by build_pdf(). Kept data-driven so EN/KO stay structurally
# parallel while each carries independently-written (not machine-translated)
# prose.

def content_en():
    S = []
    add = S.append

    add(("title", "Message Notification Router — Agent Workflow & Engineering Report"))
    add(("subtitle", "HackerRank Orchestrate, August 2026 — AI Judge interview preparation. "
                      "Written from the session's actual build/test/decision history."))

    # 1. Executive summary
    add(("h1", "1. Executive Summary"))
    add(("body", "The challenge: build a personalized notification router for a WhatsApp-style platform. "
                  "For every incoming message (text, image poster/screenshot, or voice note), decide "
                  "<b>notify</b> (interrupt now), <b>digest</b> (show later), or <b>mute</b> (suppress), "
                  "plus a <b>message_type</b>, a grounded <b>reason</b>, a calibrated <b>confidence</b>, "
                  "and supporting <b>evidence_message_ids</b> from the user's own history — personalized "
                  "per receiving user, not per message content alone."))
    add(("body", "Approach: a local preprocessing layer (SQLite-backed context assembly, cached image/"
                  "voice analysis) feeds a Claude Sonnet 5 classification step constrained to a JSON "
                  "schema. The prompt and schema were refined over 8 documented iterations, each driven by "
                  "reading actual miss cases rather than guessing, and validated against three independent "
                  "signals: the official 30 solved examples, a genuinely held-out 19-case synthetic test "
                  "set (text + generated images + generated voice notes) built specifically to catch "
                  "over-fitting to the visible examples, and targeted cheap re-checks on known-hard cases."))
    add(("kv_table", [
        ("action accuracy", "93.33% (30-sample eval)"),
        ("message_type accuracy", "93.33% (30-sample eval)"),
        ("evidence F1", "~48–52% (across evals)"),
        ("output.csv", "110/110 rows, schema-valid, no fallback rows"),
        ("model", "claude-sonnet-5 (vision + classification), local faster-whisper (ASR)"),
    ]))
    add(("body", "The most interview-relevant fact may be a negative result: a plausible-sounding prompt "
                  "idea (a <font name=\"Courier\">key_phrase</font> grounding field) was implemented, "
                  "tested, found to <i>regress</i> accuracy (93.33% \u2192 86.67%), and reverted — kept in "
                  "this report because catching and reverting a bad idea is as much a signal of process "
                  "quality as any accepted improvement."))

    # 2. Problem recap
    add(("h1", "2. Problem Recap"))
    add(("bullets", [
        "<b>Input:</b> <font name=\"Courier\">dataset/messages.csv</font> — one row per incoming message "
        "(sender, conversation type, timestamp, text or media reference).",
        "<b>Output:</b> <font name=\"Courier\">message_id, action, message_type, reason, confidence, "
        "evidence_message_ids</font> — exact columns, exact order, one row per input message.",
        "<b>Personalization is the core requirement:</b> the same message content can be notify for one "
        "user and mute for another, based on that user's relationships, history, and preferences.",
        "<b>Multimodal:</b> text, image posters/screenshots (needs OCR/vision), and voice notes (needs "
        "ASR) must all be reasoned over, not defaulted to a generic type.",
        "<b>Constraints:</b> no hardcoded labels or file-specific answers; deterministic where possible; "
        "secrets only via environment variables; must include an evaluation workflow.",
        "<b>Context data provided:</b> per-user notification behavior, group metadata and membership, "
        "business account trust signals and per-user relationship history, past messages and how the "
        "user reacted to them (opened/replied/dismissed/muted/reported), daily notification load.",
    ]))

    # 3. Architecture
    add(("h1", "3. System Architecture"))
    add(("body", "The pipeline separates decision logic from execution logic across five stages, each a "
                  "separate, independently testable module rather than one large prompt doing everything:"))
    add(("table", (
        ["Stage", "Module", "What it does"],
        [
            ["1. Ingestion", "db.py", "Loads every dataset/*.csv into a local SQLite DB, rebuilt fresh "
                                       "each run. dataset/ stays strictly read-only except for output.csv."],
            ["2. Media\nnormalization", "image_pipeline.py\naudio_pipeline.py", "Images: MIME-sniffed "
             "(not trusted by extension), decoded with Pillow, resized, re-encoded as JPEG, then sent to "
             "Claude for description + OCR + doc-type. Voice: transcribed locally with faster-whisper "
             "behind a swappable provider interface (the Messages API has no direct audio input type)."],
            ["3. Context\nassembly", "router.py\npull_context()", "Per message: receiving user's profile, "
             "the specific group-membership or business-relationship row, cached media analysis, today's "
             "notification load, and a relevance-ranked slice of that user's own message history with "
             "reactions — never the full CSVs."],
            ["4. Classification", "router.py\nclassify_message()", "Claude Sonnet 5 call constrained to a "
             "JSON schema. Internal-only fields (sender_trust, urgency_signal, risk_signal, "
             "repetition_signal, type_candidates) are filled BEFORE the final decision fields, forcing "
             "explicit intermediate reasoning."],
            ["5. Output +\nevaluation", "main.py, to_output_row()\ncode/evaluation/", "Every message gets "
             "exactly one output.csv row, even on failure (safe fallback, never a missing row). A "
             "separate evaluation workflow scores predictions against the 30 solved examples."],
        ]
    )))
    diag = diagram_flowable()
    if diag:
        add(("flowable", diag))
        add(("caption", "Figure 1. Preprocessing, storage, query, and routing layers "
                         "(docs/pipeline.svg — the routing/evaluation layers described above sit "
                         "downstream of what this diagram shows)."))

    # 4. Multimodal handling detail
    add(("h1", "4. Multimodal Handling — Notable Details"))
    add(("bullets", [
        "<b>Format mistrust paid off:</b> MIME-sniffing all 20 images (not just the 3 the problem flagged) "
        "found several \u201c.jpg\u201d files that were actually PNG, in addition to the WebP/AVIF cases. "
        "Always decoding-then-re-encoding to JPEG handled every case uniformly with no per-format branching.",
        "<b>No audio input type exists</b> in the Anthropic Messages API as of this build — confirmed via "
        "the API reference before choosing an approach, not assumed. Local faster-whisper (PyAV-bundled, "
        "no system ffmpeg needed) was used behind a <font name=\"Courier\">TranscriptionProvider</font> "
        "abstraction so a hosted ASR API could be swapped in later with one class change.",
        "<b>Content-hash caching</b> (SHA-256 of file bytes) means a byte-identical file is never "
        "re-analyzed, even across separate runs — renaming doesn't force reprocessing, but any real "
        "change does, automatically.",
        "<b>Bounded concurrency + exponential-backoff retry</b> is shared infrastructure (cache.py) used "
        "by both the image and audio pipelines, not duplicated per pipeline.",
    ]))

    # 5. Internal reasoning fields
    add(("h1", "5. Classification Design — Forcing Intermediate Reasoning"))
    add(("body", "Reviewing early results surfaced two patterns: <b>digest\u2192notify</b> was the single "
                  "most common miss direction, and wrong predictions carried visibly lower confidence than "
                  "correct ones (0.70 vs 0.85 average, across 49 combined evaluation cases). The fix: "
                  "extend the JSON schema with internal-only fields the model must fill <i>before</i> the "
                  "final decision — never written to output.csv, but forcing the decision to follow from "
                  "explicit signals rather than being decided first and rationalized afterward."))
    add(("table", (
        ["Internal field", "Purpose"],
        [
            ["sender_trust", "verified_trusted_relationship \u2192 unverified_or_new_no_relationship (5 levels)"],
            ["urgency_signal", "Does the text itself state or imply urgency, either way? Catches phrases "
                                "like \u201cno rush\u201d that a plan/time mention alone would override."],
            ["risk_signal", "none \u2192 clear_scam_pattern — deception/credential/payment-extraction signals"],
            ["repetition_signal", "How this message relates to the user's history with this sender/topic"],
            ["type_candidates", "1\u20133 candidate message_types with relative likelihood, considered "
                                 "before committing to the single best fit"],
        ]
    )))
    add(("body", "Plus one explicit rule targeting the observed bias: <i>\u201cWhen notify and digest are "
                  "genuinely close, default to digest — uncertainty alone is not justification to "
                  "interrupt.\u201d</i> Combined effect, validated on the 30-sample eval: "
                  "<b>action accuracy 86.67% \u2192 93.33%, message_type 90% \u2192 93.33%, no "
                  "regression</b> on the 26 previously-correct cases."))

    # 6. Decision log
    add(("h1", "6. Key Design Decisions"))
    add(("body", "Selected entries from the running decision log (full log in CLAUDE.en.md/CLAUDE.ko.md \u00a78) "
                  "— each includes the alternative that was rejected and why:"))
    add(("dtable", [
        ("Always re-encode images to JPEG after resize, regardless of source format.",
         "Several \u201c.jpg\u201d files in the dataset were actually WebP/AVIF/PNG. Decode-then-"
         "re-encode handles every format uniformly (including AVIF, which the vision API doesn't accept "
         "as a media_type) with no per-format branching. Rejected: trusting the file extension."),
        ("Local faster-whisper instead of a hosted ASR API.",
         "Confirmed the Messages API has no audio content-block type, so transcription is mandatory "
         "regardless. Local avoids a second API key/cost and PyAV avoids the \u201cno ffmpeg\u201d "
         "blocker on this machine. Rejected: OpenAI Whisper API (unnecessary cost/key for no accuracy "
         "requirement here)."),
        ("Python 3.12 venv instead of the system's default Python 3.14.",
         "ctranslate2 (faster-whisper's backend) is a compiled wheel that lags new Python releases by "
         "months; 3.14 was too recent to trust in a time-boxed hackathon. Verified 3.12 installed "
         "cleanly before committing. Rejected: 3.14 (real risk of no prebuilt wheel)."),
        ("Routing decisions cached by message_id, not content-hash (unlike media).",
         "messages.csv is static for the run's duration and message_id already uniquely identifies each "
         "row; hashing the full joined context (8+ tables) would be complexity with no benefit. "
         "Rejected: content-hash keying (over-engineered here); no caching (re-pays on every test run)."),
        ("evidence_message_ids retrieval is a hand-scored heuristic (sender > group > business > "
         "recency, capped at 12), not embeddings.",
         "Dataset is small enough (at most a few hundred history rows per user) that a fast, explainable "
         "heuristic is sufficient and keeps token cost low. Rejected: full-history dump (token-expensive, "
         "dilutes signal); embedding search (unneeded complexity at this scale)."),
        ("On classification failure after retries, emit a safe digest/unknown fallback row rather than "
         "skipping the message or crashing the run.",
         "The submission contract requires exactly one row per message; a missing row is worse than a "
         "clearly-labeled low-confidence placeholder, and the cache still marks it failed so "
         "retry-failed fixes it for real later. Rejected: omitting the row; crashing the whole run."),
        ("message_type disambiguation rules were derived by reading the actual text of every miss in "
         "the worst-performing categories, not by guessing plausible-sounding definitions.",
         "Category boundaries in this dataset are a labeling convention, not something inferable from "
         "category names alone (e.g. a business-sender appointment reminder being labeled \u201cevent\u201d "
         "isn't obvious without seeing that example). Rejected: generic textbook category definitions "
         "without checking real examples."),
        ("A second, genuinely held-out synthetic test set was built rather than trusting the 30-sample "
         "eval's number as final.",
         "Every prompt fix so far had been validated only against sample_messages.csv, and repeatedly "
         "reading those same 30 examples to derive rules creates real overfitting risk even while trying "
         "to stay general. It surfaced a real gap (under-weighted \u201cnot urgent\u201d framing) the "
         "30-sample set hadn't exposed. Rejected: trusting the 30-sample number alone."),
        ("Synthetic test images/voice were generated locally and free (Pillow, Windows SAPI TTS), not "
         "via an image-gen/TTS API.",
         "This is throwaway evaluation input, not a submission deliverable — only exercising the same "
         "OCR/ASR/vision code paths matters, not media realism. Rejected: a generation API (added cost/"
         "key/latency for eval data discarded after scoring)."),
        ("The key_phrase grounding field was implemented, tested, and reverted after a measured "
         "regression (93.33%\u219286.67% action on the 30-sample eval).",
         "Not every plausible-sounding grounding technique helps — the categorical internal-assessment "
         "fields worked, but adding free-text extraction on top of them didn't. A cheap 30-sample check "
         "caught this before it reached the submission file. Rejected: keeping the change on the "
         "strength of the idea alone, without re-measuring."),
    ]))

    # 7. Eval loop / iteration timeline
    add(("h1", "7. Iterative Development — The Eval Loop"))
    add(("body", "The \u201cbuild \u2192 run \u2192 inspect failures \u2192 fix \u2192 rerun\u201d loop, in "
                  "order. This is the process an AI Judge interview is likely to probe most directly."))
    add(("itable", [
        ("1", "First `route --limit 3` test finished suspiciously fast with 0/3 succeeding. Root cause: "
              "a single SQLite connection shared across ThreadPoolExecutor workers "
              "(\u201cobjects created in a thread\u2026\u201d). Fixed by giving each worker its own "
              "connection."),
        ("2", "Re-ran \u2192 3/3 succeeded. Manually read the output against source text before scaling up "
              "— confirmed grounded reasoning (e.g. caught an OTP-phishing message disguised as personal "
              "chat by matching a prior identical message the same user had reported). Ran the full "
              "110-message batch."),
        ("3", "Discovered sample_messages.csv uses a disjoint message_id namespace (sample_msg_*) from "
              "messages.csv (msg_*) — comparing output.csv to it by id always scores 0/30. Built a script "
              "that runs the router on sample_messages.csv's own input fields instead. Baseline: 90% "
              "action, 63% message_type, 49% evidence F1."),
        ("4", "Found one real gap (opted-in repeat promotions over-muted for repetition alone) and fixed "
              "it with a general rule, not a special case. Action held at 90% (miss moved, not "
              "eliminated \u2014 read as n=30 noise) \u2014 deliberately stopped tuning to avoid "
              "overfitting the visible set."),
        ("5", "User asked specifically to improve message_type accuracy. Read the actual text of every "
              "miss in the worst categories (event, promotion, greeting) and derived 4 generalizable "
              "disambiguation rules from real conventions in the data. Result: message_type 63%\u219290%."),
        ("6", "Built a genuinely held-out 19-case synthetic set (never used to tune the prompt). First "
              "run: 74% action / 79% type \u2014 notably lower, and revealing: personal messages "
              "over-triaged to notify even when text explicitly said \u201cno rush\u201d. Fixed with one "
              "more general rule; re-ran: 84%/84%, no regression on the 30-sample set."),
        ("7", "User pattern-spotted the digest\u2192notify bias and the confidence/correctness "
              "correlation from reviewing results directly. Added internal reasoning fields + a "
              "default-to-digest-under-uncertainty rule. Validated cheaply first (7 previously-wrong "
              "cases: 3 fixed, 0 type regressions) before the full 30-sample check: 93.33%/93.33%, "
              "no regression."),
        ("8", "Tried extending type_candidates with a key_phrase grounding field. Result: a real "
              "regression (93.33%\u219286.67% action). Reverted immediately, restoring the "
              "best-validated version, and reclassified the full 110-message set with it."),
    ]))

    # 8. Testing strategy
    add(("h1", "8. Testing &amp; Validation Strategy"))
    add(("body", "Three independent signals were used together, deliberately, rather than trusting any "
                  "single one:"))
    add(("bullets", [
        "<b>Official 30 solved examples</b> (dataset/sample_messages.csv) — the primary, always-available "
        "local proxy. Scored via a purpose-built harness (code/evaluation/) that validates output schema, "
        "flags degenerate label distributions, and prints an action/message_type confusion matrix.",
        "<b>Genuinely held-out synthetic set</b> (19 cases: 13 text + 3 Pillow-drawn images + 3 "
        "Windows-SAPI-synthesized voice notes) built specifically to check generalization, since the "
        "prompt had never seen these cases. This is what caught the urgency-framing gap the 30-sample "
        "set missed.",
        "<b>Targeted cheap re-checks</b> — before spending on a full re-run after a prompt change, "
        "reclassify only the previously-known-wrong cases first (7 messages, not 30 or 110) to get a "
        "fast, cheap read on whether an idea is working before committing further spend.",
        "<b>Schema and sanity checks</b> — exact column order, allowed action/message_type value sets, "
        "confidence range, evidence ids validated against the actual user's message_history (not "
        "invented, not another user's history), and a non-degenerate action distribution.",
    ]))
    add(("body", "An HTML report with the synthetic set's 19 cases (embedded images/audio, expected-vs-"
                  "actual, pass/fail) plus an illustrative rule-based \u201ctry it yourself\u201d simulator "
                  "was also built and published — clearly labeled as a simplified client-side "
                  "approximation, not a live model call, since the artifact platform available in this "
                  "session offered no capability to call the Anthropic API from a published page without "
                  "risking an API-key leak."))

    # 9. Cost management
    add(("h1", "9. Cost &amp; Resource Management"))
    add(("bullets", [
        "Model choice (Claude Sonnet 5) was made from an explicit cost/quality/speed estimate before any "
        "spend, given the small data volume (20 images, 13 voice notes, 110 messages) made even Opus-tier "
        "cost negligible in absolute terms — Sonnet was chosen for quality headroom at lower cost, not "
        "because it was the only affordable option.",
        "Local, free where it mattered: Whisper ASR (no per-call API cost) and synthetic test-media "
        "generation (Pillow + Windows SAPI TTS) — both throwaway/development-time costs kept at zero.",
        "Content-hash caching across the whole pipeline meant re-running preprocessing after a code fix "
        "never re-paid for unchanged media.",
        "A real cost-tracking bug was found and fixed mid-session: the cache-status command's "
        "\u201ccumulative spend\u201d figure summed only the current cache files, which repeated "
        "<font name=\"Courier\">--force</font> reclassification runs overwrite — so it silently "
        "under-reported total spend across multiple full re-runs. Caught by manually reconciling every "
        "individual run's reported cost, then communicated transparently before continuing to spend.",
    ]))

    # 10. Final results
    add(("h1", "10. Final Results"))
    add(("kv_table", [
        ("action accuracy", "93.33% (28/30, official sample set)"),
        ("message_type accuracy", "93.33% (28/30, official sample set)"),
        ("evidence F1 (avg)", "~48–52%, consistent across evaluation runs"),
        ("synthetic held-out set (final)", "84% action / 84% message_type (19 cases, never used to tune)"),
        ("output.csv", "110/110 rows written, 0 fallback rows, schema-exact"),
        ("action distribution", "mute 55 / notify 33 / digest 22 (non-degenerate)"),
    ]))

    # 11. Limitations
    add(("h1", "11. Known Limitations &amp; Honest Open Items"))
    add(("bullets", [
        "<b>evidence_message_ids F1 (~48–52%)</b> lags action/message_type accuracy — the current "
        "heuristic retrieval works but doesn't always match the exact ids a grader would consider most "
        "relevant. Not tuned further given overfitting risk on a 30-example gold set and limited "
        "remaining budget.",
        "<b>spam vs scam, event vs urgent</b> stayed genuinely ambiguous across both eval sets even "
        "after the message_type fixes — read as inherent category-boundary fuzziness (both readings "
        "defensible on the actual content) rather than a fixable bug.",
        "<b>Whisper model size</b> is <font name=\"Courier\">base</font> (fastest, CPU-only) — a larger "
        "model might improve transcript quality but wasn't attempted; spot-checked transcripts were "
        "already qualitatively good, and budget was tight by the end of the session.",
        "<b>The internal reasoning fields are a heuristic improvement, not a proof</b> — they measurably "
        "helped on two independent eval sets, which is meaningful evidence at this scale, but n=30/n=19 "
        "eval sets can't rule out further edge cases the hidden grading set might contain.",
    ]))

    # 12. Submission
    add(("h1", "12. Submission Artifacts"))
    add(("bullets", [
        "<b>code.zip</b> — the code/ directory only (main.py, config.py, db.py, cache.py, "
        "image_pipeline.py, audio_pipeline.py, router.py, query.py, evaluation/), excluding .venv/, "
        "data/, __pycache__/. Includes a self-contained code/README.md since code.zip's contents are all "
        "a reviewer sees.",
        "<b>output.csv</b> — final predictions for all 110 messages in dataset/messages.csv.",
        "<b>log.txt</b> — the AGENTS.md-mandated chat transcript, appended after every turn for the "
        "entire session, including the onboarding agreement and every decision described in this report.",
    ]))
    add(("body", "This report itself, plus the full CLAUDE.en.md/CLAUDE.ko.md project briefs (architecture "
                  "principles, complete eval loop log, complete decision log, open questions) and the "
                  "synthetic-test HTML report are available in the repository for deeper review, though "
                  "only code/ ships in code.zip per the submission instructions."))

    return S


def content_ko():
    S = []
    add = S.append

    add(("title", "메시지 알림 라우터 — 에이전트 워크플로우 & 엔지니어링 보고서"))
    add(("subtitle", "HackerRank Orchestrate, 2026년 8월 — AI Judge 인터뷰 대비 자료. "
                      "이번 세션의 실제 구현·테스트·의사결정 기록을 바탕으로 작성."))

    add(("h1", "1. 요약"))
    add(("body", "과제: WhatsApp과 유사한 플랫폼을 위한 개인화된 알림 라우터를 구축하는 것. 수신되는 모든 "
                  "메시지(텍스트, 이미지 포스터/스크린샷, 음성 메모)에 대해 <b>notify</b>(즉시 알림), "
                  "<b>digest</b>(나중에 표시), <b>mute</b>(억제) 중 하나를 판단하고, <b>message_type</b>, "
                  "근거가 담긴 <b>reason</b>, 보정된 <b>confidence</b>, 사용자 본인 이력에서 가져온 "
                  "<b>evidence_message_ids</b>까지 산출해야 한다 — 메시지 내용만으로가 아니라 "
                  "수신자별로 개인화된 판단이 핵심이다."))
    add(("body", "접근 방식: 로컬 전처리 계층(SQLite 기반 컨텍스트 구성, 캐시된 이미지/음성 분석)이 "
                  "JSON 스키마로 제약된 Claude Sonnet 5 분류 단계에 데이터를 공급한다. 프롬프트와 스키마는 "
                  "8회의 기록된 반복을 거쳐 다듬어졌으며, 매번 추측이 아니라 실제 오답 사례를 직접 읽고 "
                  "근거를 도출했고, 세 가지 독립적인 신호로 검증했다: 공식 정답 30건, 보이는 예시에 "
                  "과적합됐는지 확인하기 위해 전용으로 만든 진짜 held-out 합성 테스트 19건(텍스트 + 생성 "
                  "이미지 + 생성 음성), 그리고 이미 어려운 것으로 확인된 케이스만 저렴하게 재검증하는 "
                  "타겟 체크."))
    add(("kv_table", [
        ("action 정확도", "93.33% (30건 정답 세트 기준)"),
        ("message_type 정확도", "93.33% (30건 정답 세트 기준)"),
        ("evidence F1", "~48–52% (여러 평가 기준 공통)"),
        ("output.csv", "110/110행, 스키마 검증 통과, fallback 행 없음"),
        ("모델", "claude-sonnet-5 (비전+분류), 로컬 faster-whisper (음성 인식)"),
    ]))
    add(("body", "인터뷰에서 가장 의미 있게 볼 만한 사실은 오히려 \u201c실패 사례\u201d일 수 있다: 그럴듯해 "
                  "보이던 프롬프트 아이디어(<font name=\"MalgunGothic\">key_phrase</font> grounding "
                  "필드)를 실제로 구현·테스트했더니 정확도가 <i>퇴보</i>했고(93.33% \u2192 86.67%), 이를 "
                  "발견해 되돌렸다 — 이런 사례를 굳이 이 보고서에 남긴 이유는, 나쁜 아이디어를 잡아내고 "
                  "되돌리는 것도 채택된 개선 못지않게 프로세스 품질을 보여주는 신호이기 때문이다."))

    add(("h1", "2. 문제 요약"))
    add(("bullets", [
        "<b>입력:</b> <font name=\"MalgunGothic\">dataset/messages.csv</font> — 수신 메시지 1건당 1행 "
        "(발신자, 대화 유형, 타임스탬프, 텍스트 또는 미디어 참조).",
        "<b>출력:</b> <font name=\"MalgunGothic\">message_id, action, message_type, reason, confidence, "
        "evidence_message_ids</font> — 정확한 컬럼, 정확한 순서, 입력 메시지당 정확히 1행.",
        "<b>개인화가 핵심 요구사항이다:</b> 동일한 메시지 내용이라도 수신자의 관계·이력·선호도에 따라 "
        "한 사람에겐 notify, 다른 사람에겐 mute가 될 수 있다.",
        "<b>멀티모달:</b> 텍스트, 이미지 포스터/스크린샷(OCR/비전 필요), 음성 메모(ASR 필요)를 모두 "
        "실제로 분석해야 하며 임의의 기본값으로 처리하면 안 된다.",
        "<b>제약사항:</b> 하드코딩된 라벨이나 파일별 특화 답변 금지; 가능한 한 결정론적으로 동작; "
        "비밀값은 환경변수로만; 평가 워크플로우 필수 포함.",
        "<b>제공된 컨텍스트 데이터:</b> 사용자별 알림 행동, 그룹 메타데이터와 멤버십, 비즈니스 계정 "
        "신뢰 신호 및 사용자별 관계 이력, 과거 메시지와 그에 대한 사용자 반응(열람/답장/무시/음소거/신고), "
        "일일 알림량."
    ]))

    add(("h1", "3. 시스템 아키텍처"))
    add(("body", "파이프라인은 판단 로직과 실행 로직을 5단계로 분리하며, 하나의 거대한 프롬프트가 모든 걸 "
                  "처리하는 대신 각 단계를 독립적으로 테스트 가능한 별도 모듈로 구성했다:"))
    add(("table", (
        ["단계", "모듈", "역할"],
        [
            ["1. 데이터 적재", "db.py", "dataset/*.csv 전체를 로컬 SQLite DB로 적재, 실행마다 새로 "
                                        "빌드. dataset/은 output.csv를 제외하면 엄격히 읽기 전용."],
            ["2. 미디어\n정규화", "image_pipeline.py\naudio_pipeline.py", "이미지: 확장자를 신뢰하지 않고 "
             "실제 MIME 타입 감지 → Pillow로 디코드 → 리사이즈 → JPEG 재인코딩 → Claude에 보내 설명+OCR+"
             "문서유형 산출. 음성: 교체 가능한 provider 인터페이스 뒤에서 로컬 faster-whisper로 전사 "
             "(Messages API에는 직접적인 오디오 입력 타입이 없음)."],
            ["3. 컨텍스트\n구성", "router.py\npull_context()", "메시지마다: 수신 사용자 프로필, 해당 "
             "그룹멤버십 또는 비즈니스관계 행, 캐시된 미디어 분석, 오늘의 알림량, 해당 사용자 본인 "
             "메시지 이력 중 관련성 순으로 추린 일부(반응 포함) — 전체 CSV를 절대 통째로 보내지 않음."],
            ["4. 분류", "router.py\nclassify_message()", "JSON 스키마로 제약된 Claude Sonnet 5 호출. "
             "최종 판단 필드 이전에 내부 전용 필드(sender_trust, urgency_signal, risk_signal, "
             "repetition_signal, type_candidates)를 먼저 채우게 해 명시적 중간 추론을 강제."],
            ["5. 출력 +\n평가", "main.py, to_output_row()\ncode/evaluation/", "실패하더라도 모든 메시지가 "
             "output.csv에 정확히 1행씩 기록됨(안전한 fallback, 누락 행 없음). 별도 평가 워크플로우가 "
             "정답 30건 대비 예측을 채점."],
        ]
    )))
    diag = diagram_flowable()
    if diag:
        add(("flowable", diag))
        add(("caption", "그림 1. 전처리·저장소·질의·라우팅 계층 "
                         "(docs/pipeline.svg — 위에서 설명한 라우팅/평가 계층은 이 다이어그램이 보여주는 "
                         "부분의 다음 단계에 위치)."))

    add(("h1", "4. 멀티모달 처리 — 주목할 만한 세부사항"))
    add(("bullets", [
        "<b>포맷을 신뢰하지 않은 것이 실제로 도움이 됐다:</b> 문제에서 알려준 3개뿐 아니라 이미지 20개 "
        "전체를 MIME 스니핑했더니 WebP/AVIF 사례 외에도 실제로는 PNG인 \u201c.jpg\u201d 파일이 여럿 "
        "발견됐다. 디코드 후 항상 JPEG로 재인코딩하는 방식이 포맷별 분기 없이 모든 경우를 일괄 처리했다.",
        "<b>오디오 입력 타입이 없다는 사실을 확인 후 결정:</b> 이 빌드 시점 Anthropic Messages API에 "
        "오디오 콘텐츠 블록 타입이 없다는 걸 추측이 아니라 API 레퍼런스로 직접 확인한 뒤 접근법을 "
        "정했다. 로컬 faster-whisper(PyAV 내장, 시스템 ffmpeg 불필요)를 "
        "<font name=\"MalgunGothic\">TranscriptionProvider</font> 추상화 뒤에 두어, 나중에 호스팅형 "
        "ASR API로 클래스 하나만 바꿔 교체할 수 있게 설계.",
        "<b>콘텐츠 해시 캐싱</b>(파일 바이트의 SHA-256)으로 바이트가 동일한 파일은 여러 번 실행해도 "
        "재분석하지 않음 — 파일명 변경은 재처리를 유발하지 않지만 실제 내용 변경은 자동으로 재처리됨.",
        "<b>동시성 제한 + 지수 백오프 재시도</b>는 이미지/오디오 파이프라인이 공유하는 인프라(cache.py)로, "
        "파이프라인마다 중복 구현하지 않음.",
    ]))

    add(("h1", "5. 분류 설계 — 중간 추론을 강제하기"))
    add(("body", "초기 결과를 검토하며 두 가지 패턴이 드러났다: <b>digest\u2192notify</b>가 가장 흔한 오답 "
                  "방향이었고, 오답의 confidence가 정답보다 눈에 띄게 낮았다(합산 49건 기준 평균 0.70 vs "
                  "0.85). 해결책: JSON 스키마에 모델이 최종 판단 <i>이전에</i> 반드시 채워야 하는 내부 "
                  "전용 필드를 추가 — output.csv에는 절대 기록되지 않지만, 판단이 먼저 나오고 사후에 "
                  "합리화되는 대신 명시적 신호로부터 도출되도록 강제한다."))
    add(("table", (
        ["내부 필드", "목적"],
        [
            ["sender_trust", "verified_trusted_relationship \u2192 unverified_or_new_no_relationship (5단계)"],
            ["urgency_signal", "본문 자체가 긴급성을 명시/암시하는가(양방향)? \u201cno rush\u201d 같은 "
                                "문구가 일정 언급만으로 무시되는 걸 방지"],
            ["risk_signal", "none \u2192 clear_scam_pattern — 기만/자격증명·결제정보 탈취 시도 신호"],
            ["repetition_signal", "이 메시지가 해당 발신자/주제에 대한 사용자 이력과 어떻게 연관되는가"],
            ["type_candidates", "최종 카테고리를 확정하기 전 고려하는 1~3개 후보 message_type과 상대적 "
                                 "가능성"],
        ]
    )))
    add(("body", "여기에 관찰된 편향을 정확히 겨냥한 규칙 하나를 추가: <i>\u201cnotify와 digest가 "
                  "진짜로 애매하면 digest를 기본값으로 — 불확실하다는 것 자체는 인터럽트를 정당화하지 "
                  "않는다.\u201d</i> 30건 평가에서 검증된 종합 효과: <b>action 정확도 86.67% \u2192 "
                  "93.33%, message_type 90% \u2192 93.33%</b>, 기존에 맞았던 26건에서 "
                  "<b>회귀 없음</b>."))

    add(("h1", "6. 주요 설계 결정"))
    add(("body", "누적 의사결정 로그(전체는 CLAUDE.en.md/CLAUDE.ko.md \u00a78) 중 선별한 항목 — 각각 "
                  "기각한 대안과 이유를 포함:"))
    add(("dtable", [
        ("리사이즈 후 이미지는 원본 포맷과 무관하게 항상 JPEG로 재인코딩.",
         "데이터셋의 \u201c.jpg\u201d 파일 여러 개가 실제로는 WebP/AVIF/PNG였음. 디코드 후 재인코딩하면 "
         "포맷별 분기 없이 모두 처리되며, 비전 API가 media_type으로 허용하지 않는 AVIF 문제도 함께 "
         "해결됨. 기각한 대안: 파일 확장자 신뢰."),
        ("호스팅형 ASR API 대신 로컬 faster-whisper 사용.",
         "Messages API에 오디오 콘텐츠 블록 타입이 없음을 확인했으므로 전사는 어차피 필수. 로컬 방식은 "
         "두 번째 API 키/비용을 피하고, PyAV 덕분에 이 머신의 \u201cffmpeg 없음\u201d 문제도 우회. "
         "기각한 대안: OpenAI Whisper API(여기선 정확도 이점 없이 비용/키만 추가)."),
        ("시스템 기본 Python 3.14 대신 Python 3.12 venv 사용.",
         "faster-whisper의 백엔드인 ctranslate2는 컴파일된 휠이라 최신 Python 출시보다 보통 몇 달 뒤처짐. "
         "3.14는 시간제한 있는 해커톤에서 신뢰하기엔 너무 최신 버전. 결정 전 3.12가 깨끗이 설치됨을 "
         "확인. 기각한 대안: 3.14(휠 미지원 위험 실재)."),
        ("라우팅 판단은 (미디어와 달리) 콘텐츠 해시가 아니라 message_id로 캐싱.",
         "messages.csv는 실행 기간 동안 정적이고 message_id가 이미 각 행을 유일하게 식별함; 8개 이상 "
         "테이블을 조인한 전체 컨텍스트를 해시하는 건 이득 없는 복잡도. 기각한 대안: 콘텐츠 해시 키"
         "(여기선 과설계); 캐시 없음(테스트 실행마다 비용 재지불)."),
        ("evidence_message_ids 검색은 임베딩이 아니라 수동 점수화 휴리스틱(발신자 > 그룹 > 비즈니스 > "
         "최신순, 최대 12건).",
         "데이터셋이 충분히 작아(사용자당 이력 최대 수백 건) 빠르고 설명 가능한 휴리스틱으로 충분하고 "
         "토큰 비용도 낮게 유지됨. 기각한 대안: 전체 이력 통째 전달(토큰 낭비, 신호 희석); 임베딩 검색"
         "(이 규모에서 불필요한 복잡도)."),
        ("재시도 후에도 분류 실패 시, 메시지를 건너뛰거나 실행을 중단하는 대신 안전한 digest/unknown "
         "fallback 행을 출력.",
         "제출 규약상 메시지당 정확히 1행이 있어야 하며, 행 누락보다는 명확히 표시된 저신뢰 대체값이 "
         "낫고, 캐시엔 실패로 남아 나중에 retry-failed가 실제로 재처리함. 기각한 대안: 행 생략; 전체 "
         "실행 중단."),
        ("message_type 세분화 규칙은 그럴듯한 정의를 추측하는 대신, 가장 오답률 높은 카테고리의 실제 "
         "오답 텍스트를 전부 읽어 도출.",
         "이 데이터셋의 카테고리 경계는 라벨링 당시의 관습이지 카테고리 이름만으로 추론 가능한 게 아님"
         "(예: business 발신자의 예약 알림이 \u201cevent\u201d로 분류되는 건 실제 사례를 보지 않고는 "
         "알 수 없음). 기각한 대안: 실제 예시 확인 없이 교과서적 정의만 작성."),
        ("30건 평가 수치를 최종으로 믿는 대신, 완전히 별개인 진짜 held-out 합성 테스트셋을 추가로 구축.",
         "그때까지의 모든 프롬프트 수정이 sample_messages.csv 하나로만 검증됐고, 일반 규칙을 뽑으려 "
         "애써도 같은 30개 예시를 반복해서 읽는 것 자체가 과적합 위험을 만듦. 30건 세트에서는 드러나지 "
         "않았던 진짜 문제(\u201cnot urgent\u201d 프레이밍 과소반영)를 실제로 찾아냄. 기각한 대안: "
         "30건 수치만 신뢰."),
        ("합성 테스트용 이미지/음성은 생성 API 대신 로컬(Pillow, Windows SAPI TTS)로 무료 생성.",
         "채점 후 버려지는 평가용 입력이지 제출물이 아님 — 실제 데이터셋과 동일한 OCR/ASR/비전 코드 "
         "경로만 거치면 되고 미디어의 실사 품질은 중요하지 않음. 기각한 대안: 생성 API(채점 후 버려질 "
         "데이터에 불필요한 비용/키/지연)."),
        ("key_phrase grounding 필드를 구현·테스트했다가, 실측된 퇴보(30건 평가 action 93.33%\u2192"
         "86.67%) 확인 후 되돌림.",
         "그럴듯해 보이는 grounding 기법이라고 다 도움이 되는 건 아님 — 범주형 내부 판단 필드는 효과가 "
         "있었지만 그 위에 자유 텍스트 추출을 얹은 건 아니었음. 저렴한 30건 검증 덕분에 제출 파일에 "
         "반영되기 전에 잡아냄. 기각한 대안: 재측정 없이 아이디어 자체의 그럴듯함만 믿고 유지."),
    ]))

    add(("h1", "7. 반복적 개발 과정 — 평가 루프"))
    add(("body", "\u201c만들고 → 돌리고 → 실패 사례 확인 → 고치고 → 다시 돌리기\u201d 루프를 순서대로 "
                  "정리. AI Judge 인터뷰가 가장 직접적으로 파고들 가능성이 높은 부분이다."))
    add(("itable", [
        ("1", "첫 `route --limit 3` 테스트가 0/3 성공으로, 그것도 비정상적으로 빨리 끝남. 원인: "
              "ThreadPoolExecutor 워커들이 SQLite 커넥션 하나를 공유(\u201c다른 스레드에서 만든 객체는 "
              "그 스레드에서만 사용 가능\u201d). 워커마다 자기 커넥션을 갖도록 수정."),
        ("2", "재실행 → 3/3 성공. 규모를 키우기 전에 출력을 원본 텍스트와 직접 대조 확인 — 근거가 "
              "탄탄함을 확인(예: personal 대화로 위장한 OTP 피싱을, 같은 사용자가 과거 신고한 동일 "
              "메시지와 매칭해 정확히 잡아냄). 전체 110건 배치 실행."),
        ("3", "sample_messages.csv가 messages.csv(msg_*)와 완전히 다른 id 체계(sample_msg_*)를 쓴다는 "
              "걸 발견 — output.csv를 id로 바로 비교하면 항상 0/30. sample_messages.csv 자신의 입력 "
              "필드로 라우터를 돌리는 스크립트를 새로 작성. 기준선: action 90%, message_type 63%, "
              "evidence F1 49%."),
        ("4", "실제 문제 하나 발견(옵트인한 반복 프로모션을 반복성만으로 과다 mute)하여 특정 사례가 "
              "아닌 일반 규칙으로 수정. action은 90% 유지(오답이 사라진 게 아니라 이동 — n=30 노이즈로 "
              "판단) — 보이는 세트에 과적합되지 않도록 의도적으로 튜닝 중단."),
        ("5", "사용자가 message_type 정확도 개선을 명시적으로 요청. 가장 오답률 높은 카테고리(event, "
              "promotion, greeting)의 실제 오답 텍스트를 전부 읽고, 데이터의 실제 관습에서 일반화 "
              "가능한 세분화 규칙 4개를 도출. 결과: message_type 63%→90%."),
        ("6", "프롬프트 튜닝에 한 번도 쓰인 적 없는 진짜 held-out 19건 합성 세트 구축. 첫 실행: action "
              "74% / type 79% — 눈에 띄게 낮았고, 유의미한 원인 발견: \u201cno rush\u201d라고 명시했는데도 "
              "개인 메시지를 notify로 과다 판단. 일반 규칙 하나 더 추가해 재실행: 84%/84%, 30건 세트 "
              "회귀 없음."),
        ("7", "사용자가 결과를 직접 검토하며 digest→notify 편향과 confidence-정확도 상관관계를 발견. "
              "내부 추론 필드 + 불확실 시 digest 기본값 규칙 추가. 저렴하게 먼저 검증(이전 오답 7건: "
              "3건 수정, message_type 회귀 0건) 후 30건 전체 확인: 93.33%/93.33%, 회귀 없음."),
        ("8", "type_candidates에 key_phrase grounding 필드를 확장 시도. 결과: 실제 퇴보(action "
              "93.33%→86.67%). 즉시 되돌려 최고 검증 버전을 복원하고, 그 버전으로 실제 메시지 110건 "
              "전체를 재분류."),
    ]))

    add(("h1", "8. 테스트 및 검증 전략"))
    add(("body", "단일 신호를 맹신하지 않고, 세 가지 독립적인 신호를 의도적으로 함께 사용했다:"))
    add(("bullets", [
        "<b>공식 정답 30건</b>(dataset/sample_messages.csv) — 항상 사용 가능한 1차 로컬 대리 지표. 출력 "
        "스키마를 검증하고, 라벨 쏠림을 경고하며, action/message_type 혼동행렬을 출력하는 전용 하네스"
        "(code/evaluation/)로 채점.",
        "<b>진짜 held-out 합성 세트</b>(19건: 텍스트 13 + Pillow로 그린 이미지 3 + Windows SAPI로 합성한 "
        "음성 3) — 프롬프트가 한 번도 본 적 없어 일반화 여부를 확인하기 위해 전용으로 구축. 30건 세트가 "
        "놓쳤던 긴급성-프레이밍 문제를 이 세트가 잡아냈다.",
        "<b>저렴한 타겟 재검증</b> — 프롬프트 변경 후 전체 재실행에 돈을 쓰기 전에, 이전에 틀렸던 것으로 "
        "이미 알려진 케이스만(30건이나 110건이 아니라 7건) 먼저 재분류해 아이디어가 통하는지 빠르고 "
        "저렴하게 확인.",
        "<b>스키마/정합성 검사</b> — 정확한 컬럼 순서, 허용된 action/message_type 값 집합, confidence "
        "범위, evidence id가 실제 해당 사용자의 message_history에 존재하는지(다른 사용자 이력이나 "
        "허구의 id 아님), action 분포가 한쪽으로 쏠리지 않았는지.",
    ]))
    add(("body", "합성 세트 19건 전체(이미지/오디오 삽입, expected-vs-actual, 성공/실패 표시)와 예시 삼아 "
                  "만든 규칙 기반 \u201c직접 시뮬레이션\u201d 도구를 담은 HTML 리포트도 제작해 게시했다 — "
                  "이 세션에서 사용 가능한 아티팩트 플랫폼이 게시된 페이지에서 API 키 유출 위험 없이 "
                  "Anthropic API를 직접 호출할 방법을 제공하지 않았기 때문에, 실제 모델 호출이 아니라 "
                  "단순화된 클라이언트 사이드 근사치임을 명확히 라벨링했다."))

    add(("h1", "9. 비용 및 리소스 관리"))
    add(("bullets", [
        "모델 선택(Claude Sonnet 5)은 지출 전에 명시적인 비용/품질/속도 추정을 거쳐 결정 — 데이터 "
        "규모가 작아(이미지 20장, 음성 13개, 메시지 110건) Opus급을 써도 절대 금액은 미미했지만, "
        "\u201c유일하게 감당 가능한 선택지라서\u201d가 아니라 낮은 비용에서 품질 여유를 확보하기 위해 "
        "Sonnet을 선택.",
        "중요한 부분에서 로컬·무료 활용: Whisper ASR(호출당 API 비용 없음)과 합성 테스트 미디어 생성"
        "(Pillow + Windows SAPI TTS) — 둘 다 버려지는/개발 시점 비용을 0으로 유지.",
        "파이프라인 전체에 걸친 콘텐츠 해시 캐싱 덕분에, 코드 수정 후 전처리를 다시 돌려도 변하지 않은 "
        "미디어에 대해서는 다시 비용을 지불하지 않음.",
        "세션 중간에 실제 비용 추적 버그를 발견해 수정: cache-status 명령의 \u201c누적 비용\u201d 수치가 "
        "현재 캐시 파일만 합산했는데, 반복된 <font name=\"MalgunGothic\">--force</font> 재분류 실행이 "
        "매번 이 파일들을 덮어써서 여러 번의 전체 재실행에 걸친 총 비용을 조용히 과소보고하고 있었음. "
        "각 실행이 보고한 비용을 하나하나 직접 합산해 발견했고, 이후 지출을 계속하기 전에 사용자에게 "
        "투명하게 알림.",
    ]))

    add(("h1", "10. 최종 결과"))
    add(("kv_table", [
        ("action 정확도", "93.33% (30건 중 28건, 공식 정답 세트)"),
        ("message_type 정확도", "93.33% (30건 중 28건, 공식 정답 세트)"),
        ("evidence F1 (평균)", "~48–52%, 평가 실행마다 일관됨"),
        ("합성 held-out 세트 (최종)", "action 84% / message_type 84% (19건, 튜닝에 사용된 적 없음)"),
        ("output.csv", "110/110행 작성, fallback 행 0건, 스키마 정확히 일치"),
        ("action 분포", "mute 55 / notify 33 / digest 22 (편중 없음)"),
    ]))

    add(("h1", "11. 알려진 한계 및 솔직한 미해결 사항"))
    add(("bullets", [
        "<b>evidence_message_ids F1(~48–52%)</b>은 action/message_type 정확도보다 뒤처짐 — 현재의 "
        "휴리스틱 검색은 작동하지만 채점자가 가장 관련 있다고 볼 id와 항상 정확히 일치하진 않음. 30개 "
        "정답 세트에 과적합될 위험과 남은 예산 제약으로 더 튜닝하지 않음.",
        "<b>spam vs scam, event vs urgent</b>는 message_type 수정 이후에도 두 평가 세트 모두에서 "
        "계속 애매함 — 고칠 수 있는 버그라기보다(실제 내용상 양쪽 해석 다 타당함) 카테고리 경계 자체의 "
        "본질적 모호함으로 판단.",
        "<b>Whisper 모델 크기</b>는 <font name=\"MalgunGothic\">base</font>(가장 빠름, CPU 전용) — "
        "더 큰 모델이 전사 품질을 개선할 수도 있지만 시도하지 않음; 표본 점검한 전사 결과가 이미 질적으로 "
        "충분했고 세션 막바지엔 예산도 빠듯했음.",
        "<b>내부 추론 필드는 경험적 개선이지 증명이 아니다</b> — 두 개의 독립적인 평가 세트에서 측정 "
        "가능한 도움이 됐고 이는 이 규모에서 의미 있는 근거이지만, n=30/n=19 평가 세트만으로는 히든 "
        "채점셋에 있을 수 있는 추가 엣지 케이스를 배제할 수 없음.",
    ]))

    add(("h1", "12. 제출물"))
    add(("bullets", [
        "<b>code.zip</b> — code/ 디렉터리만(main.py, config.py, db.py, cache.py, image_pipeline.py, "
        "audio_pipeline.py, router.py, query.py, evaluation/), .venv/, data/, __pycache__/ 제외. "
        "code.zip 안의 내용만 검토자에게 보이므로 자체 완결된 code/README.md 포함.",
        "<b>output.csv</b> — dataset/messages.csv 110건 전체에 대한 최종 예측 결과.",
        "<b>log.txt</b> — AGENTS.md가 요구하는 채팅 트랜스크립트, 온보딩 동의와 이 보고서에 설명된 모든 "
        "결정을 포함해 세션 내내 매 턴마다 추가됨.",
    ]))
    add(("body", "이 보고서 자체와 CLAUDE.en.md/CLAUDE.ko.md 전체 프로젝트 브리프(아키텍처 원칙, 전체 "
                  "평가 루프 로그, 전체 의사결정 로그, 미해결 질문), 합성 테스트 HTML 리포트는 더 깊은 "
                  "검토를 위해 저장소에 남아있지만, 제출 지침에 따라 code.zip에는 code/만 포함된다."))

    return S


# ============================================================== RENDER ====
def build_pdf(content, out_path: Path, lang: str):
    styles = make_styles(lang)
    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        topMargin=20 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
        title="Message Notification Router - Agent Workflow Report",
    )
    story = []
    for kind, payload in content:
        if kind == "title":
            story.append(p(payload, styles["Title"]))
        elif kind == "subtitle":
            story.append(p(payload, styles["Subtitle"]))
            story.append(hr())
        elif kind == "h1":
            story.append(p(payload, styles["H1"]))
            story.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT, spaceAfter=6))
        elif kind == "h2":
            story.append(p(payload, styles["H2"]))
        elif kind == "body":
            story.append(p(payload, styles["Body"]))
        elif kind == "bullets":
            story.append(bullets(payload, styles["Bullet"]))
        elif kind == "caption":
            story.append(p(payload, styles["Caption"]))
        elif kind == "flowable":
            story.append(KeepTogether(payload))
        elif kind == "kv_table":
            rows = [[k, v] for k, v in payload]
            t = rich_table(["", ""], rows, styles, col_widths=[55 * mm, 115 * mm])
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.white),
                                    ("FONTNAME", (0, 1), (0, -1), styles["TableHead"].fontName),
                                    ("TEXTCOLOR", (0, 1), (0, -1), ACCENT_DARK)]))
            story.append(t)
            story.append(Spacer(1, 8))
        elif kind == "table":
            header, rows = payload
            n = len(header)
            widths = None
            if n == 3:
                widths = [30 * mm, 38 * mm, 102 * mm]
            story.append(rich_table(header, rows, styles, col_widths=widths))
            story.append(Spacer(1, 8))
        elif kind == "dtable":
            rows = [[d, r] for d, r in payload]
            t = rich_table(["Decision", "Reason / rejected alternative"] if lang == "en" else ["결정", "이유 / 기각한 대안"],
                            rows, styles, col_widths=[75 * mm, 95 * mm], cell_style_key="TableCellSmall")
            story.append(t)
            story.append(Spacer(1, 8))
        elif kind == "itable":
            rows = [[i, r] for i, r in payload]
            t = rich_table(["#", "Iteration" if lang == "en" else "반복"], rows, styles,
                            col_widths=[10 * mm, 160 * mm], cell_style_key="TableCellSmall")
            story.append(t)
            story.append(Spacer(1, 8))
    doc.build(story)
    print(f"Wrote {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")


def main():
    build_pdf(content_en(), HERE / "agent_workflow_report_en.pdf", "en")
    build_pdf(content_ko(), HERE / "agent_workflow_report_ko.pdf", "ko")


if __name__ == "__main__":
    main()
