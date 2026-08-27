# Architecture

← [back to README](../README.md)

```
dataset/*.csv ──► db.py ──────────────► data/processed.db  (SQLite, indexed join keys)

media/images/* ─► image_pipeline.py ──┐
media/audio/*  ─► audio_pipeline.py ──┤► data/cache/  (content-hash keyed, JSON)
                                       │
messages.csv ──► router.pull_context() ┘
                        │
                        ▼
                 compact per-message context ──► Claude (JSON-schema constrained)
                        │
                        ├──► dataset/output.csv   (the deliverable)
                        └──► data/ael.db          (decision ledger)
```

**Per-message context, not the whole dataset.** `pull_context()` assembles only
what bears on *this* message: the receiving user's profile, the one group
membership or business relationship that applies, cached media analysis if
there's an attachment, today's notification load, and a relevance-ranked slice
of that user's own history with their reactions to it. The full CSVs are never
sent to the model.

**Forced intermediate reasoning.** The response schema makes the model fill
`sender_trust`, `urgency_signal`, `risk_signal`, `repetition_signal`, and
`type_candidates` *before* it may emit `action`. These never reach `output.csv`
— they exist to stop the model from picking a category first and rationalizing
after. Adding them moved action accuracy 86.67% → 93.33% (see
[Evaluation](EVALUATION.md) for what that number does and doesn't mean).

**Media handled by content, not extension.** Several `.jpg` files in this
dataset are actually WebP, AVIF, or PNG. Everything is decoded with Pillow and
re-encoded as bounded-size JPEG, so the wrong extension never matters and AVIF
(which the vision API won't accept) works anyway.

**Voice notes cost nothing.** The Messages API has no audio content block, so
transcription is required regardless. It runs locally through `faster-whisper`
behind a `TranscriptionProvider` interface — no API cost, no system `ffmpeg`.

**Every decision is auditable.** `code/ael_client.py` writes an append-only
ledger — Planning → Execution → Evidence → Verification → Reflection → State —
to a database separate from the rebuilt-every-run `processed.db`. Verification
independently checks that every cited `evidence_message_id` actually existed in
the context the model was given, so hallucinated evidence is caught and flagged
rather than trusted. This checks that the evidence *exists*, not that it's
*relevant* — see [Known limits](EVALUATION.md#known-limits) for that gap.

**Untrusted input is treated as data.** Message text, OCR output, and
transcripts are all explicitly framed to the model as content to classify, never
as instructions. A message that tries to instruct the router is itself scored as
scam evidence.

## File-by-file

```
code/
  main.py               CLI: validate | preprocess | route | retry-failed | cache-status | query
  router.py             the deliverable — context assembly + classification
  ael_client.py         append-only decision ledger (schema in ael_schema.sql)
  config.py             env vars, paths, model settings — no secrets, ever
  db.py                 dataset/*.csv -> SQLite
  cache.py              content-hash cache + bounded concurrency/retry runner
  image_pipeline.py     any format -> JPEG -> vision analysis
  audio_pipeline.py     local ASR behind a swappable provider interface
  query.py              ad-hoc retrieval + Q&A (dev tool, not the submission path)
  test_ael_client.py    ledger self-check
  evaluation/           scoring harness (EN/KO) — single source of truth
```

`code/README.md` has the same table with one more sentence of "why" per file,
written for an AI-judge reviewer who only sees `code.zip`.
