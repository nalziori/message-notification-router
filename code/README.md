# Message Notification Router — Code

Personalized notify/digest/mute router for the HackerRank Orchestrate
"Message Notification Router" challenge. This is the `code/` directory as
submitted — it expects to run from inside the full contest repo (needs
`dataset/` alongside it), not standalone.

## Setup

```bash
# From the repo root (one level above this code/ directory):
python -m venv .venv
# Windows:
.venv\Scripts\pip install anthropic pillow faster-whisper python-dotenv pillow-avif-plugin
# macOS/Linux:
.venv/bin/pip install anthropic pillow faster-whisper python-dotenv pillow-avif-plugin

# Set your API key (never hardcoded, read from the environment only):
# Windows PowerShell:
$env:ANTHROPIC_API_KEY = "sk-ant-..."
# macOS/Linux:
export ANTHROPIC_API_KEY="sk-ant-..."
# ...or create a .env file in the repo root: ANTHROPIC_API_KEY=sk-ant-...
```

Requires Python 3.11+ (developed and tested on 3.12 — `ctranslate2`, the
`faster-whisper` backend, is a compiled wheel that can lag brand-new Python
releases, so a very recent interpreter may not have a prebuilt wheel yet).
Audio decoding is bundled via PyAV — no system `ffmpeg` install needed.

## Run

```bash
python main.py validate            # check dataset/media files + API key presence, no network calls
python main.py preprocess          # build the SQLite DB + analyze all images/audio (cached)
python main.py route               # classify every dataset/messages.csv row -> writes dataset/output.csv
python main.py cache-status        # DB row counts, media/routing cache status, spend to date
python main.py retry-failed        # re-run only media/routing that failed or was never processed
python main.py query "<question>"  # ad-hoc retrieval + Q&A over the dataset (dev/debug tool)

# Required evaluation workflow (scores against dataset/sample_messages.csv's 30 solved examples):
python evaluation/main.py                 # English report
python evaluation/main.py --lang ko        # Korean report
python evaluation/main.py --skip-classify  # re-score existing evaluation/sample_predictions.csv, no API calls

python test_ael_client.py                  # ledger self-check (no dataset, no API key, no network)
```

All commands are run from inside this `code/` directory, with the repo's
`dataset/` folder present one level up (`../dataset/`).

## Architecture

- `config.py` — env vars, paths, model settings. `config.require_api_key()` gives a clear setup
  message and makes zero network calls if `ANTHROPIC_API_KEY` is unset.
- `db.py` — loads every `dataset/*.csv` into a local SQLite DB (`../data/processed.db`), rebuilt
  fresh each run. `dataset/` is read-only; only `dataset/output.csv` is ever written.
- `cache.py` — SHA-256 content-hash cache + a bounded-concurrency/retry runner shared by the
  image and audio pipelines.
- `image_pipeline.py` — decodes every image with Pillow regardless of its (sometimes wrong) file
  extension, resizes it, re-encodes as JPEG, then sends it to Claude for a short description + OCR
  text + doc-type classification via a JSON-schema-constrained response.
- `audio_pipeline.py` — transcribes voice notes with local `faster-whisper` (no API cost) behind a
  `TranscriptionProvider` interface, since the Anthropic Messages API doesn't accept audio as a
  direct input type.
- `router.py` — the actual deliverable. For each message, `pull_context()` assembles the receiving
  user's profile, group/business relationship, cached media analysis, today's notification load,
  and a relevance-ranked slice of that user's own message history — then sends a compact,
  personalized context to Claude with a JSON-schema-constrained response. Before the final
  `action`/`message_type`/`confidence` fields (the only ones written to `output.csv`), the model
  fills internal-only fields (`sender_trust`, `urgency_signal`, `risk_signal`, `repetition_signal`,
  `type_candidates`) that force explicit intermediate reasoning rather than a direct categorical
  jump. A message that fails classification after retries gets a clearly-labeled `digest`/`unknown`
  fallback row — `output.csv` always has exactly one row per input message.
- `query.py` — a retrieval + Q&A helper used during development, not part of the submission path.
- `ael_client.py` / `ael_schema.sql` — an append-only decision ledger (Planning → Execution → Evidence →
  Verification → Reflection → State) in its own SQLite file, so any routing decision can be explained
  after the fact. Verification independently re-checks that every cited `evidence_message_id` was
  actually present in the context the model received, catching hallucinated evidence.
- `test_ael_client.py` — assert-based self-check for the ledger write path. Runs standalone with no
  dataset, API key, or network access.
- `evaluation/` — the required evaluation workflow: classifies `dataset/sample_messages.csv`'s own
  30 solved rows with the real router (`sample_messages.csv` uses a different `message_id`
  namespace than `messages.csv`, so this is the only way to get a real accuracy read locally), then
  scores the result and prints an action/message_type confusion matrix.

See the repo root's `CLAUDE.en.md`/`CLAUDE.ko.md` for the full design rationale, eval-loop history,
and decision log (outside `code/`, for reviewer context — not required to run this code).
