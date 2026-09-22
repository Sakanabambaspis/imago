# Spec: cheng-dev — engineering work before the project summary goes out

**Track: DEV.** Companion track: `.scratch/cheng-pitch/` (README + email —
separate dir on purpose: dev work and pitch writing are organized apart).

## Cross-track order (binding)

1. **cheng-dev 01 → 07, in numeric order** — one ticket per session.
2. Then **cheng-pitch 01** (README refresh), then **cheng-pitch 02** (email).
3. **08–11 (runway) are needs-triage: do not start them before the email is
   sent**, unless the fit conversation redirects. They exist so the runway is
   already ticketed, not to gate the email.

## Goal

Take the repo from "instrument validated on stubs, real path never executed"
to "first provisional baseline-vs-countermeasure result committed and every
checkable README claim true" — the minimum engineering state that makes the
email honest.

## Constraint set

- Free-tier runtime (BigModel glm-4-flash; see ticket 05's endpoint probe).
- The owner controls which sessions run; tickets must be self-contained
  enough for an AFK session, one at a time.
- Every number that leaves this track carries its provisional label.
- Honest reporting beats good-looking reporting; deviations (model-pin
  switch, endpoint congestion) are recorded, not smoothed over.

## Scope

| # | Ticket | Unblocks |
|---|---|---|
| 01 | Commit adapter backoff | 02 |
| 02 | Judge client bug (client=None) | 03, 05 |
| 03 | Real-path integration tests | 06 |
| 04 | Results hygiene | 06 |
| 05 | E2E smoke, both loops | 06 |
| 06 | Pilot-40 wave pair | 07 |
| 07 | First result note | pitch 01, pitch 02 |
| 08–11 | Runway (needs-triage) | — |

## Non-goals

- No checkpoint/resume unless 06 actually loses progress (contingency inside 06).
- No judge calibration / full wave / cross-model before the email (that's 08–10).
- No README or prose work here — that lives in cheng-pitch.

## Definition of done (this track)

Two real wave JSONs + one-page result note committed; suite green including
real-path coverage; `docs/results/` contains nothing stub-generated.
