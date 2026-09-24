# 03 — Mechanical audit: quotes must exist in the raw layer

Status: ready-for-agent
Type: task
Blocked by: 02

## Context

The digest agent is an LLM and can fabricate. The faithfulness contract is
therefore enforced by a script, not by hope: every verbatim quote in a
compiled entry must exist in the cited raw line, and every session in the
uncompiled window must be covered by a day file.

## What

- `scripts/journal_audit.py` (stdlib only), modes:
  - `--dump`: print uncompiled raw lines (per cursor in
    `.imago/journal/state.json`) as readable text for the digest agent.
  - default: validate day files for every date with uncompiled data —
    header lines present; `Sessions:` covers every session id in pending
    raw; every rationale blockquote (whitespace-normalized, trailing `…`
  allowed) is a contiguous substring of the cited raw line ±3.
  - `--advance`: on validation success, move the cursor to end-of-raw.
  - `--dry-run`: validate/report without advancing.
- Cursor semantics: `{file, offset}` — everything before offset compiled;
  earlier files fully compiled; missing state = start of history.

## Verification

- Happy path: seeded raw + correct entry → passes, cursor advances once,
  second run reports nothing pending.
- Fabrication test: entry quotes a sentence not in the cited raw file →
  audit fails with a precise citation; fix → passes.
- Coverage test: raw session id missing from `Sessions:` → fails.

## Done when

- Script committed; all three checks demonstrated on seeded fixtures.

## Comments

2026-09-23: Done. Happy path validates quotes and advances the cursor
exactly once; fabricated quote, missing session coverage, cross-day
citation, and missing day file each fail with precise citations;
incremental appends recompile only new lines; clean "nothing pending" after
catch-up. Two bugs found and fixed during testing: pending dates with zero
new lines were being validated (false pass on coverage), and the
emptiness check tested the wrong dict.


## Migrated

Imported as GitHub issue #17 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
