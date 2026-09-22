# 01 — Commit the adapter backoff work (already written, uncommitted)

Status: ready-for-agent
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
