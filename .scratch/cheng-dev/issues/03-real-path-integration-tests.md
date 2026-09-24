# 03 — Real-path integration tests: FakeClient through run_p1/run_p2

Status: ready-for-agent
Type: task
Blocked by: 02

## Why

"40 tests green" coexisted with "the LLM-judge path never executed" — the gap
that let ticket 02's bug ship. This is the exact question an engineering
reviewer asks ("how did your suite miss the only path that matters?"). Close
it structurally, not by hope.

## What

Wire the existing `FakeClient` (`tests/fakes.py`) through the **full**
instrument path with `stub=None`:

- `run_p1` end-to-end on a tmp config: wave JSON written, aggregates present,
  every trap scored through the **LLM** judges (not keyword judges).
- `run_p2` same treatment.
- Assert judge `api_call` events land in the wave's own log with
  `purpose_tag=judge`, task calls with `purpose_tag=probe` — the telemetry
  contract is part of the path.

## Done when

- New tests pass.
- **Reverting ticket 02's fix makes the new test fail** — that is the proof
  the gap is closed. Verify this once, note it in `## Comments`.


## Migrated

Imported as GitHub issue #4 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
