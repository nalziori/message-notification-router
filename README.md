# Message Notification Router

[![CI](https://github.com/nalziori/message-notification-router/actions/workflows/ci.yml/badge.svg)](https://github.com/nalziori/message-notification-router/actions/workflows/ci.yml)

A personalized notify / digest / mute router for a WhatsApp-style message stream.
For every incoming message — text, image poster, screenshot, or voice note — it
decides whether to interrupt the user now, hold it for later, or suppress it,
and it says *why*, citing the specific past messages that justify the call.

The interesting part isn't the classifier. It's that the same message is
correctly `notify` for one user and `mute` for another, based on that user's own
relationships and reaction history — and that every decision leaves an
auditable trail explaining itself. Built for the **HackerRank Orchestrate**
24-hour hackathon (August 2026).

---

## Quickstart — no dataset, no API key

```bash
pip install anthropic python-dotenv
python fixtures/smoke_test.py
```

Runs the real pipeline end to end — context assembly, schema-validated
classification, the AEL ledger's full write, `output.csv` generation — against
an invented 19-case dataset and a fake model client. Proves the code runs
correctly; the challenge dataset itself isn't redistributed here (license
unclear), so routing *quality* still needs it. Details and the full setup with
the real dataset: **[docs/RUNNING.md](docs/RUNNING.md)**.

---

## Result

**129th of 1,983 entrants — 69.7 / 100.**

![Final leaderboard placement: 129 of 1,983, score 69.7/100](docs/leaderboard.png)

| Graded component | Score |
|---|---|
| Output CSV (110 predictions) | 20.4 / 30 |
| Code zip | 22.2 / 30 |
| AI judge interview | 19.2 / 30 |
| Chat transcript | 7.9 / 10 |

Locally, before submitting: 93.33% action / 93.33% type accuracy on the 30
examples the prompt was tuned against, 84% / 84% on a held-out set built
specifically so it couldn't be. Those numbers and the graded score answer
different questions, not the same one at different quality — the local harness
never measured `reason` quality or evidence relevance, both of which the
official rubric does. Full reconciliation: **[docs/EVALUATION.md](docs/EVALUATION.md)**.

---

## How it works

- **Per-message context, not the whole dataset.** Each decision sees only the
  receiving user's profile, the one relevant relationship, cached media
  analysis, and a relevance-ranked slice of their own history — never the full
  CSVs.
- **Forced intermediate reasoning.** The model fills sender-trust/urgency/risk
  signals *before* it may emit an action, so it can't pick a category first and
  rationalize after. This one change moved action accuracy 86.67% → 93.33%.
- **Every decision is auditable.** An append-only ledger records
  Planning → Execution → Evidence → Verification → Reflection → State per
  message, independently checking that cited evidence actually existed in the
  model's context.

Diagram, the rest of the design decisions, and the caveats on all three claims
above: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## Layout

```
code/            the pipeline (db, cache, image/audio, router, AEL ledger, evaluation)
eval/            held-out synthetic test set + HTML report
fixtures/        standalone dataset + offline smoke test (no key, no organizer data)
docs/            architecture, evaluation, running instructions, provenance (below)
CLAUDE.en/ko.md  full design brief, 8-iteration eval log, decision log
.github/         CI — runs the smoke test on every push
```

## Read more

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — pipeline diagram, design decisions, file-by-file map
- **[docs/EVALUATION.md](docs/EVALUATION.md)** — official vs. local scores reconciled, harness usage, known limits
- **[docs/RUNNING.md](docs/RUNNING.md)** — full setup, with or without the real dataset; cost design
- **[docs/PROVENANCE.md](docs/PROVENANCE.md)** — what the organizers provided vs. what was written
- **[CLAUDE.en.md](CLAUDE.en.md)** / **[CLAUDE.ko.md](CLAUDE.ko.md)** — the full brief: architecture principles, every eval iteration, decision log with rejected alternatives
