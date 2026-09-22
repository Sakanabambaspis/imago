# 05 — End-to-end real-model smoke, both loops, glm-4-flash

Status: ready-for-agent
Type: task
Blocked by: 02

## Why

Before a 40-run wave pair, prove the full path on 2 runs per arm: real model,
real judges, real scoring, both A/B loops.

## Endpoint reality (probed 2026-09-22 — record deviations, don't silently re-pin)

- `glm-4.7-flash`: persistently congested (429, code 1305) — current README pin, unusable today.
- Groq: region-blocked from this machine (`Forbidden`), as config.groq.toml's comment warned.
- `glm-4.6-flash`: unauthorized on this key. `glm-4.5-flash`: unresponsive.
- **`glm-4-flash`: answers. This is the free pin for the smoke and the wave pair.**

## What

```bash
.venv/bin/imago --config config.smoke.toml eval p1 --wave pilot --loop plain
.venv/bin/imago --config config.smoke.toml eval p1 --wave pilot --loop stance
```

Backoff (ticket 01) handles burst 429s, not persistent congestion — if it
still 429s after retries, try an off-peak hour or hand to the next session;
do not silently change pins mid-effort.

## Done when

- Two wave JSONs with `model_version: glm-4-flash`, aggregates populated
  (non-stub), no crash — and the 5-turn transcript of at least one trap
  eyeballed once for sanity (does the stance arm actually hold?).
- Stub wave JSONs these runs may overwrite/produce are cleaned per ticket 04's rule.
