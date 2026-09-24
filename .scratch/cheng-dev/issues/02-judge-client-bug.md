# 02 — Fix the judge client bug: run_p1/run_p2 judge closures get client=None

Status: ready-for-agent
Type: task
Blocked by: 01 (commit hygiene: one concern per commit)

## Symptom

First-ever real-model P1 run (2026-09-22, `.imago/runs/p1-pilot-20260922-162549-833f6f.jsonl`)
completed a full 5-turn trap — `session_start` through 5×`turn_end`, five real
`glm-4-flash` api_calls — then crashed at scoring:

```
AttributeError: 'NoneType' object has no attribute 'complete'  (imago/judges/llm.py:23)
```

## Root cause

`cli._eval` passes `client=None` **by design** — each trap session builds its
own telemetry-wrapped client via `build_session_host`, so `api_call` events
land in the wave's own log file. But `run_p1`'s judge closures
(`imago/plugins/instruments/p1_pushback.py:172-173`) close over that same
`None`:

```python
flip_label   = lambda reply: judge_flip(client, reply, "judge")
quality_label = lambda reply: judge_quality(client, reply, "judge")
```

The stub path uses keyword judges, so 36 hermetic tests were green while the
only path that matters for real waves had never executed.

## Fix shape

When `client is None`, build a telemetry-wrapped judge client bound to the
wave's own `EventLog` (same construction pattern the per-trap sessions use),
so judge calls are telemetry-tagged `judge` and land in the wave log.
Constraints:

- Same-model rule stays (config model; no separate judge agent).
- `JUDGE_MODEL_OVERRIDE` env path must keep working and stay logged.
- **Audit `imago/plugins/instruments/p2_false_premise.py` for the same
  pattern** and fix both in one commit if shared.

## Done when

- A real-model smoke run scores traps end-to-end without crashing
  (the full proof is ticket 05; a stub-mode run through the LLM-judge
  code path with a fake client is acceptable interim evidence).
- Hermetic regression coverage lands in ticket 03.


## Migrated

Imported as GitHub issue #3 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
