# Message Notification Router

[![CI](https://github.com/nalziori/message-notification-router/actions/workflows/ci.yml/badge.svg)](https://github.com/nalziori/message-notification-router/actions/workflows/ci.yml)

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

**Final: 129th of 1,983 entrants — 69.7 / 100.**

![Final leaderboard placement: 129 of 1,983, score 69.7/100](docs/leaderboard.png)

| Graded component | Score | |
|---|---|---|
| Output CSV — the 110 routed predictions | 20.4 / 30 | 68% |
| Code zip — implementation quality | 22.2 / 30 | 74% |
| AI judge interview — defending the design | 19.2 / 30 | 64% |
| Chat transcript — documented process | 7.9 / 10 | 79% |

Locally, before submitting:

| Evaluation set | `action` | `message_type` | evidence F1 |
|---|---|---|---|
| 30 solved examples (`sample_messages.csv`) — **tuned against** | 93.33% | 93.33% | ~48–52% |
| 19 held-out synthetic cases — **never used for tuning** | 84% | 84% | — |

### Reading these two together

The local 93% and the graded 20.4/30 are not the same measurement, and treating
the gap as a straight accuracy drop would be wrong. The local harness scores one
narrow thing: whether the `action` and `message_type` *labels* match. The
official rubric scores the whole submission — label correctness plus `reason`
quality (judged by an AI grader), whether `evidence_message_ids` point at
genuinely relevant history, and confidence calibration.

`reason` quality was never measured locally at all. The harness says so in its
own docstring, and it went unaddressed: every one of the eight tuning iterations
optimized labels, because labels were the only thing the local loop could see.
Evidence F1 was visible and stayed at ~50% — the weakest measured number, and
the one most likely to have cost points on a rubric that weights it.

The one comparison that *is* apples-to-apples is the two local rows: 93% on the
set the prompt was tuned against, 84% on a set built specifically so it couldn't
be. That ~10-point gap was measurable before submitting, and it's the reason the
synthetic set exists. What the final score adds is that an eval which only
watches labels will happily report 93% while the parts it isn't watching decide
the outcome.

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

### Try it without the dataset or an API key

```bash
pip install anthropic python-dotenv   # imported at module load; never called or needed live
python fixtures/smoke_test.py
```

`fixtures/` is a small, entirely invented dataset (70 rows across 8 context
tables — users, groups, business relationships, message history) built to
resolve the 19 held-out synthetic test cases from `eval/synthetic_cases.csv`
without the organizer data. Those cases were originally written reusing real
organizer entity ids for convenience, which is exactly what stopped them
running once the organizer data was excluded — `fixtures/build_fixtures.py`
is what closes that gap.

The smoke test runs the real pipeline end to end — context assembly, JSON
response parsing, label validation, the AEL ledger's full Planning→State
write, output.csv generation, and the official schema check — against a fake
model client (`fixtures/fake_client.py`) that returns the fixture's own
labels instead of calling the API. It proves the code runs correctly, not
that the router is accurate; routing quality still needs the real dataset and
a key. Labels in `fixtures/expected_labels.csv` were assigned by a human
reading each case's assembled context (not the message text alone) —
`note` on 7 of the 19 records why the call was genuinely close.

### With the real dataset and an API key

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
.github/workflows/ci.yml   runs the two lines below on every push (fixture dataset only)
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
fixtures/               standalone dataset + offline smoke test (no key, no organizer data)
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
