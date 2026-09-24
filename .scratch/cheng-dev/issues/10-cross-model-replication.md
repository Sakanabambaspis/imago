# 10 — Cross-model replication of the stance delta

Status: needs-triage
Type: task
Blocked by: —

## Why

The honest test of whether the countermeasure is prompt-general or
model-specific: does the plain→stance delta replicate on a second endpoint/
pin? Also the natural "benchmarking" artifact — transfer of a behavioral
measure across models is the kind of result an evaluation lab reads.

## Shape (rough until triaged)

- Second endpoint: anything OpenAI-compatible with sane free/cheap tier, or
  Anthropic native (adapter exists). Probe availability before committing.
- Pilot-sized pair first (both arms, new pin), same protocol; full wave only
  if the pilot delta replicates in direction.
- Results live as their own note; comparison table vs the glm-4-flash pair.

## Done when

- A replication note exists stating same-direction / different-magnitude /
  no-replication, with the same confidence framing as ticket 07's note.


## Migrated

Imported as GitHub issue #11 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
