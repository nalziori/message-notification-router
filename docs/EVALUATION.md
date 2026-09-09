# Evaluation

← [back to README](../README.md)

## Official result

**129th of 1,983 entrants — 69.7 / 100.**

![Final leaderboard placement: 129 of 1,983, score 69.7/100](leaderboard.png)

| Graded component | Score | |
|---|---|---|
| Output CSV — the 110 routed predictions | 20.4 / 30 | 68% |
| Code zip — implementation quality | 22.2 / 30 | 74% |
| AI judge interview — defending the design | 19.2 / 30 | 64% |
| Chat transcript — documented process | 7.9 / 10 | 79% |

## Local result (before submitting)

| Evaluation set | `action` | `message_type` | evidence F1 |
|---|---|---|---|
| 30 solved examples (`sample_messages.csv`) — **tuned against** | 93.33% | 93.33% | ~48–52% |
| 19 held-out synthetic cases — **never used for tuning** | 84% | 84% | — |

Full run: 110/110 messages routed, ~$0.75 in API spend for the final pass.

## Reading these two together

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

## Running the harness

```bash
python code/evaluation/main.py                 # classify the 30 solved examples, then score
python code/evaluation/main.py --lang ko       # same, Korean report
python code/evaluation/main.py --skip-classify # re-score existing predictions, no API calls
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

## Where the evidence-F1 bottleneck actually is

An external review of this repo prescribed a reranker (BM25/embedding/LLM) as the
top fix for the ~50% evidence F1. Before building it, `eval/evidence_retrieval_ablation.py`
measured whether retrieval was the bottleneck at all — with zero API calls.

`router.get_relevant_history()` scores candidates by relationship (same sender +3,
same group +2, same business +2) and passes only the top 12; `valid_evidence_ids`
then restricts the model to that pool. So if a gold evidence id isn't in the top 12,
F1 cannot improve no matter how the prompt changes. That recall is computable offline.

| ranker | @5 | @12 | @all |
|---|---|---|---|
| rule (current) | 81% | **97%** | 100% |
| bm25 | 90% | 100% | 100% |
| hybrid (relationship first, BM25 as tiebreak) | 90% | 100% | 100% |

Of 31 gold evidence ids, 0 were missing from the user's history — the candidate-set
ceiling is 100%, and the current ranker already reaches 97% of it. **Retrieval was
not the bottleneck.** A perfect reranker was worth at most 3 points here.

Scoring the *selection* step the same way found the real leak: gold answers carry
1.03 evidence ids on average, the router emits 2.93 (2.8x). On the 30 solved
examples that is precision 28% / recall 81% / **F1 42%**. Capping the list at one
id moves it to 48% / 45% / **47%**.

Three caveats, because this is a measurement and not a shipped fix:

- **This 42% is not the ~48–52% quoted above.** That figure is over all 110
  messages; this one is the 30-sample subset. They are not interchangeable.
- **The cap was not applied to the router.** It trades recall 81% → 45%, and it
  was tuned on n=30 — structurally the same trap as the Iteration 8 regression.
  Confirming it on the held-out set has to come first.
- **Precision is still only 48% even at top-1**, so ranking quality is a second,
  separate problem. Reranking isn't useless — it's aimed at the wrong stage. It
  belongs on selection order, not on the candidate set. (Unmeasured; needs API calls.)

```bash
python eval/evidence_retrieval_ablation.py            # needs dataset/ (not shipped)
python eval/evidence_retrieval_ablation.py --selftest # no data, no API calls
```

## Known limits

- Evidence F1 (~48–52%) lags accuracy. Retrieval is a hand-scored heuristic
  (same sender > same group > same business > recency, capped at 12); it finds
  relevant history but not always the exact ids the grader wants. The section
  above locates the leak in selection rather than retrieval, but the fix it
  points at is measured, not applied.
- `spam` vs `scam` and `event` vs `urgent` stayed genuinely ambiguous across
  both eval sets. Both readings are defensible on the actual message content;
  chasing it further meant overfitting to small-sample noise.
- Whisper runs at `base` on CPU. Spot checks were fine, but larger models were
  never benchmarked.
- The 30-sample set is n=30. Single-case movements there are noise, and were
  deliberately not treated as signal.
- The AEL ledger verifies evidence *exists* in the model's context, not that it's
  *relevant* to the decision — an external review of this repo flagged this as
  the next real gap. Existence checking (`evidence_valid` in `ael_verification`)
  is implemented; relevance/support scoring is not.
