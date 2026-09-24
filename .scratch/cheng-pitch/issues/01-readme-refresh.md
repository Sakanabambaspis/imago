# 01 — README refresh: consistent with what a browser will find

Status: ready-for-agent
Type: task
Blocked by: cheng-dev 06, cheng-dev 07

## Why

The README is the front door the email points at. Staleness found on
2026-09-22: "30 hermetic tests" (40 now, more after cheng-dev 03); pin named
`glm-4.7-flash` (persistently congested — the working pin is `glm-4-flash`);
no pointer to the first result note; smoke harness unmentioned (if
cheng-dev 04 commits `config.smoke.toml`).

The "Honest deviations from design-mvp.md" section **stays** — see spec.

## What

- Test count current.
- Model pin current, congestion reality in one clause.
- Status line / pointer to the result note in docs/results/.
- One-line pointer to the smoke harness if committed.
- Nothing in the README may contradict what a reader finds in the repo
  within ninety seconds of clicking any claim.

## Done when

- Every checkable claim in the README checks out against the tree.


## Migrated

Imported as GitHub issue #13 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
