# 01 — Commit the adapter backoff work (already written, uncommitted)

Status: resolved
Type: task
Blocked by: —

## Context

Free-tier endpoints 429 under load and a wave is hundreds of serial calls;
one unhandled 429 killed a whole smoke run on 2026-09-22 (BigModel code 1305,
"model congested"). The fix is already written and tested in the working tree.

## What

- Verify current state: `imago/core/adapters.py` has `_MAX_ATTEMPTS = 5`,
  exponential backoff (1→2→4→8s) on 429/500/502/503/504 via `TransientHTTP`,
  latency_ms excludes backoff wait; `tests/test_adapters.py` has four new
  hermetic tests. Full suite 40/40 green on 2026-09-22.
- Run the suite once to confirm, then commit.
- Commit body should carry the why (free-tier survival, latency honesty).

## Done when

- Working tree backoff changes committed as their own commit; suite green.

## Comments

- 2026-09-23 (agent session): done-when already satisfied — the work was
  committed on 2026-09-22 as `02061d7` ("fix(adapters): retry transient HTTP
  failures with exponential backoff"), its own commit, body carrying the
  free-tier-survival and latency-honesty why. Verified in tree:
  `_MAX_ATTEMPTS = 5`, backoff 1→2→4→8s via `TransientHTTP` on
  429/500/502/503/504, `latency_ms` wraps only the successful attempt. All
  four hermetic tests present (`tests/test_adapters.py`: retry-until-success,
  exhaustion, non-retryable immediate, latency-excludes-backoff). Full suite
  40/40 green this session. Ticket was written against an uncommitted tree;
  the commit landed the same evening, so nothing remained to design or do.
  Marked resolved.


## Migrated

Imported as GitHub issue #1 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
