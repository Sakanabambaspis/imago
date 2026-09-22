# 08 — Judge κ-calibration against human labels (backlog T1.10)

Status: needs-triage
Type: task
Blocked by: —

## Why

The named weakness of the whole methodology: judges are the same model by
design, and κ-vs-human calibration is deferred. This ticket closes it — and
doubles as the strongest possible follow-up message after the fit
conversation ("the weakness I named is now measured").

## Shape (rough until triaged)

- Human-label a sample of trap transcripts from the pilot runs (concession
  quality: evidence/social/none; flip: yes/no).
- Compute κ per judge (flip judge, quality judge) against those labels.
- Report in docs/results/; if κ is low, that is a *result* (judge limits),
  not a failure to hide — it reshapes what the wave numbers mean.
- Frozen judge prompts must not change during calibration; if they change
  after, waves re-run under the new `JUDGE_PROMPT_VERSION`.

## Done when

- κ numbers exist with the labeling protocol written down (who labeled, how
  many items, disagreements resolved how).
