# 04 — Results hygiene: stub JSON out of docs/results/, smoke config decided

Status: ready-for-agent
Type: task
Blocked by: —

## Why

`docs/results/` currently holds `p1-pilot-20260919-001553-d04c80.json` — a
**stub** wave (`model_version: stub:agree`, hold_rate 0.0). The README's own
rule: "Wave JSONs from stub runs are scorer self-tests, not results — delete
them." A browsing professor who opens results first sees a fake result
contradicting the repo's stated rules. Internal inconsistency, not dishonesty,
but indistinguishable from the outside.

Also: `config.smoke.toml` (1 topic × 1 seed smoke harness, pinned to
glm-4-flash) is an untracked scratch file in the tree — limbo.

## What

1. Delete the stub JSON from `docs/results/`.
2. Decide `config.smoke.toml`: commit it as a documented smoke harness
   (recommended — ticket 05 uses it) **or** gitignore it. Either is fine;
   limbo is not. If committed, one README pointer line.
3. Optional: the stub JSONLs in `.imago/runs/` are gitignored artifacts —
   leaving them is fine.

## Done when

- `docs/results/` contains no stub-generated JSON.
- `config.smoke.toml` is either committed with a pointer or ignored.


## Migrated

Imported as GitHub issue #5 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
