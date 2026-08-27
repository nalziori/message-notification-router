# Running This

← [back to README](../README.md)

**The challenge dataset is not included.** The input CSVs and media under
`dataset/` were supplied by the organizers and their redistribution licensing is
unclear, so this repo ships the pipeline and the schema rather than the data.
`dataset/output.csv` — this project's own 110-row result — is kept as evidence
of the run.

## Without the dataset or an API key

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

`.github/workflows/ci.yml` runs this same smoke test (plus the AEL ledger
self-check) on every push, so it's continuously verified to still work.

## With the real dataset and an API key

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

## Cost design

Media analysis is cached by SHA-256 of file *content*, so a renamed file is
never re-analyzed and a changed file always is, with no manual invalidation.
Images are downscaled before upload. Voice transcription is local and free.
`query.py` retrieves before it asks, never sending the full dataset.

One sharp edge worth knowing: routing decisions are cached by `message_id`, not
by content hash, so **editing the prompt does not invalidate them**. `route`
needs an explicit `--force` to reclassify. `code/evaluation/run_router_on_samples.py`
force-reclassifies by default for exactly this reason.
