# Provenance

← [back to README](../README.md)

This repository is a hackathon submission, so it matters which parts were
handed out and which were written.

| Provided by the organizers | Written for this submission |
|---|---|
| `problem_statement.md`, `AGENTS.md` | Everything under `code/` except the two stubs below |
| `dataset/` (all input CSVs + media) | `eval/` — held-out synthetic test set + HTML report |
| `code/main.py`, `code/evaluation/main.py` — **empty stub files** | `fixtures/` — standalone dataset + offline smoke test |
| The original starter `README.md` (replaced by this one) | `docs/` — architecture diagram, workflow reports, this documentation |
| | `CLAUDE.en.md` / `CLAUDE.ko.md` — design brief, eval log, decision log |
| | `.github/workflows/ci.yml` — CI, added after submission |

The git history here starts at this submission. The organizers' starter repo had
its own history, which is not reproduced because it consisted entirely of commits
adding the challenge dataset (see [Running This](RUNNING.md) for why that data
isn't here).

`fixtures/` and `.github/workflows/ci.yml` were added after the hackathon
concluded, in response to an external review of the public repo — see
[Evaluation](EVALUATION.md#known-limits) for what prompted them.
