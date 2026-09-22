# 09 — Full wave: 120 runs for reportable CIs

Status: needs-triage
Type: task
Blocked by: —

## Why

Pilot-40 is provisional by construction. The corpus rule: ≥100 runs per wave
before CIs are reportable. If the pilot delta is interesting, this is the
spend that makes it citable.

## Shape (rough until triaged)

- Price it first from `imago metrics` (pilot economics × 3) — the telemetry
  exists precisely for this decision.
- Only worth running on a stable, non-congested endpoint or a paid pin;
  record the pin switch vs the pilot waves.
- Consider running only the arm that needs tightening if the other arm's CI
  is already adequate — triage decides.

## Done when

- Wave JSONs at ≥100 runs/arm with the provisional note absent, and the
  result note updated or superseded.
