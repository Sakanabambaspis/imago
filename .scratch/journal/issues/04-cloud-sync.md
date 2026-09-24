# 04 — Cloud sync: journal/ as its own repo → private GitHub remote

Status: ready-for-agent
Type: task
Blocked by: 03

## Context

Owner decision (2026-09-23): compiled journal syncs to a **private** GitHub
repo; raw stays local-only; flipping the cloud copy public is a manual owner
decision. `journal/` is deliberately a standalone git repo (gitignored by
imago) so journal history and code history never couple.

## What

- `scripts/journal_sync.py` (stdlib + git CLI): reads
  `.zcode/journal-sync.json` `{"remote": <url>, "branch": "main"}`;
  inits `journal/` repo if needed; commits pending changes
  (`journal: <date> digest`); pushes to `origin`. Unconfigured ⇒ documented
  no-op with a loud warning line, exit 0. Never force-push; divergence ⇒
  fail loudly (exit 1). Config holds a URL only — no tokens (auth via the
  owner's existing git credential helper/SSH).

## Verification

- No config → no-op + warning, exit 0.
- Throwaway local bare repo as origin → init + commit + push succeed; second
  run reports "nothing to push"; divergence check refuses force.

## Done when

- Script committed; both paths demonstrated. Owner still owes the one-time
  repo creation (setup step in the spec's Done section of the plan).

## Comments

2026-09-23: Done. Unconfigured → loud no-op, exit 0. Configured with a
throwaway local bare repo → init + commit + push; second run idempotent
with no spurious URL rewrite. True divergence (competing commit landed on
the remote first) → exit 1, remote untouched, never force-pushes. Owner
still owes: create the private GitHub repo and drop the URL into
`.zcode/journal-sync.json`.


## Migrated

Imported as GitHub issue #18 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
