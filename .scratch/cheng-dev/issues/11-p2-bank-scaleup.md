# 11 — P2 bank scale-up: 20 → 40+ factual items

Status: needs-triage
Type: task
Blocked by: —

## Why

The README's honest-deviations section says it outright: the P2 bank ships
20 factual items and must scale to 40+ before the first real monthly wave.
Closing this removes a line from the deviations list and makes the monthly
smoke detector actually worth running.

## Shape (rough until triaged)

- Items need `ground_truth` + external citations, like P1's ledger — lint
  enforces it.
- Keep the class-(a)-only scope (verifiable factual premises); classes (b)/(c)
  stay deferred (they need the memory substrate).

## Done when

- `traps/p2/factual.json` ≥40 cited items; `imago ledger lint` (or the P2
  equivalent gate) passes; README deviation line updated.
