# Message Notification Router

A personalized notify / digest / mute router for a WhatsApp-style message stream.
For every incoming message — text, image poster, screenshot, or voice note — it
decides whether to interrupt the user now, hold it for later, or suppress it,
and it says *why*, citing the specific past messages that justify the call.

Built for the **HackerRank Orchestrate** 24-hour hackathon (August 2026).

The interesting part isn't the classifier. It's that the same message is
correctly `notify` for one user and `mute` for another, because the decision is
made against that user's own relationships, opt-ins, and reaction history — and
that every decision leaves an auditable trail explaining itself.

---

## Results

| Evaluation set | `action` | `message_type` | evidence F1 |
|---|---|---|---|
| 30 solved examples (`sample_messages.csv`) — **tuned against** | 93.33% | 93.33% | ~48–52% |
| 19 held-out synthetic cases — **never used for tuning** | 84% | 84% | — |

Both numbers are reported on purpose. The 30-sample set was read repeatedly
while deriving prompt rules, so it is an optimistic estimate; the synthetic set
was built specifically to find out how much of the gain was real. It cost ~10
points, which is the honest generalization gap.

Full run: 110/110 messages routed, ~$0.75 in API spend for the final pass.

---

## Provenance

This repository is a hackathon submission, so it matters which parts were
handed out and which were written.

| Provided by the organizers | Written for this submission |
|---|---|
| `problem_statement.md`, `AGENTS.md` | Everything under `code/` except the two stubs below |
| `dataset/` (all input CSVs + media) | `eval/` — held-out synthetic test set + HTML report |
| `code/main.py`, `code/evaluation/main.py` — **empty stub files** | `docs/` — architecture diagram, workflow reports |
| The original starter `README.md` (replaced by this one) | `CLAUDE.en.md` / `CLAUDE.ko.md` — design brief, eval log, decision log |

The git history here starts at this submission. The organizers' starter repo had
its own history, which is not reproduced because it consisted entirely of commits
adding the challenge dataset (see *Running this* below for why that data isn't here).

---

## How it works

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
after. Adding them moved action accuracy 86.67% → 93.33%.

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
rather than trusted.

**Untrusted input is treated as data.** Message text, OCR output, and
transcripts are all explicitly framed to the model as content to classify, never
as instructions. A message that tries to instruct the router is itself scored as
scam evidence.

---

## Evaluation

```bash
python code/evaluation/main.py                 # classify the 30 solved examples, then score
python code/evaluation/main.py --lang ko       # same, Korean report
python code/evaluation/main.py --skip-classify # re-score existing predictions, no API calls
python code/test_ael_client.py                 # ledger self-check, no API calls
```

The harness scores `action`/`message_type` accuracy and evidence F1, prints a
confusion matrix, and independently flags degenerate strategies (everything
collapsing onto one action), schema violations, and evidence ids that don't
exist in that user's history.

`sample_messages.csv` uses a disjoint id namespace (`sample_msg_*`) from
`messages.csv` (`msg_*`), so comparing `output.csv` against it by id scores a
flat 0/30. The harness runs the router against the sample rows' own inputs
instead — a bug worth mentioning because it silently reports "0% accuracy"
rather than failing loudly.

`CLAUDE.en.md` §7 has the full iteration log, including the two negative
results: a `key_phrase` grounding field that sounded reasonable, regressed
accuracy 93.33% → 86.67%, and was reverted; and a stale-cache incident where
routing decisions cached under an old prompt kept scoring the old prompt.

---

## Running this

**The challenge dataset is not included.** The input CSVs and media under
`dataset/` were supplied by the organizers and their redistribution licensing is
unclear, so this repo ships the pipeline and the schema rather than the data.
`dataset/output.csv` — this project's own 110-row result — is kept as evidence
of the run.

What *is* included is `eval/synthetic_cases.csv` and `eval/synthetic_media/`: 19
test cases generated for this project using the Claude API and local Pillow/SAPI
rendering, modeled on the real data's shape. They reference organizer entity ids,
so they still need `dataset/` present to resolve context.

With the dataset in place:

```bash
py -3.12 -m venv .venv     # ctranslate2 wheels lag very new Python releases
.venv/Scripts/pip install anthropic pillow faster-whisper python-dotenv pillow-avif-plugin
cp .env.example .env       # then fill in ANTHROPIC_API_KEY

python code/main.py validate       # check files + key presence, zero network calls
python code/main.py preprocess     # build the DB, analyze all media (cached)
python code/main.py route          # classify every message -> dataset/output.csv
python code/main.py cache-status   # row counts, cache state, spend to date
python code/main.py retry-failed   # re-run only what failed
python code/main.py query "did u_010 get any urgent work messages?"
```

Add `--dry-run` to `preprocess`/`route` to see the plan without spending
anything. No key is ever hardcoded; `config.require_api_key()` fails with setup
instructions before any network call, and `validate`/`cache-status` never need
one at all.

### Cost design

Media analysis is cached by SHA-256 of file *content*, so a renamed file is
never re-analyzed and a changed file always is, with no manual invalidation.
Images are downscaled before upload. Voice transcription is local and free.
`query.py` retrieves before it asks, never sending the full dataset.

One sharp edge worth knowing: routing decisions are cached by `message_id`, not
by content hash, so **editing the prompt does not invalidate them**. `route`
needs an explicit `--force` to reclassify. `code/evaluation/run_router_on_samples.py`
force-reclassifies by default for exactly this reason.

---

## Layout

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
eval/                   held-out synthetic test set + HTML report
docs/                   architecture diagram, workflow reports
CLAUDE.en.md/.ko.md     design brief, eval loop log, decision log
log.txt                 the hackathon session transcript
```

`CLAUDE.en.md` (or `CLAUDE.ko.md`) is the substantive read: architecture
principles, all 8 eval iterations with what each one found, and a decision log
with the alternatives that were rejected and why.

---

## Known limits

- Evidence F1 (~48–52%) lags accuracy. Retrieval is a hand-scored heuristic
  (same sender > same group > same business > recency, capped at 12); it finds
  relevant history but not always the exact ids the grader wants.
- `spam` vs `scam` and `event` vs `urgent` stayed genuinely ambiguous across
  both eval sets. Both readings are defensible on the actual message content;
  chasing it further meant overfitting to small-sample noise.
- Whisper runs at `base` on CPU. Spot checks were fine, but larger models were
  never benchmarked.
- The 30-sample set is n=30. Single-case movements there are noise, and were
  deliberately not treated as signal.
