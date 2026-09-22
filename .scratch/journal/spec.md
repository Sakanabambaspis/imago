# Spec: journal — the dev-process journal pipeline

**Track: INFRA.** No code work in the `imago/` package (subtraction test and
MVP scope untouched).

## Goal

A project journal that records the owner's brainstorming, design, and
implementation rationale — the owner's, not the agent's — as a faithful,
detailed record, with routing so every step of research/design/development
is logged automatically.

## Architecture (decided 2026-09-23, plan approved by owner)

```
prompts ──► [ZCode hooks: UserPromptSubmit + Stop]     mechanical, live
                 ▼
        .imago/journal/raw/YYYY-MM-DD.jsonl    local-only (gitignored), append-only
                 ▼ daily 07:30, cursor-scanned
        [journal-digest scheduled agent]
                 ▼ compiles per docs/agents/journal.md, audits, syncs
        journal/ (own git repo) ──► PRIVATE GitHub remote
```

Design rationale (from the research pass, 2026-09-23): agent-written "why"
is post-hoc rationalization; the owner's actual rationale lives verbatim in
prompts. So capture is mechanical (hooks, never agent diligence — Cline
Memory Bank issue #1911 failure mode), and the compiled layer is
contract-bound to quote the owner with citations that a script verifies.

## Constraint set

- **Robustness over cleverness**: hooks always exit 0, never block the
  session, degrade gracefully on missing payload fields, are
  concurrency-safe (flock), and crash-safe (append-per-event, offset cursor).
- **Faithfulness**: verbatim quotes with raw-line citations, mechanically
  audited; `rationale: not stated` is a legal value; agent inference must be
  labeled `[agent inference]`.
- **Privacy**: raw layer never leaves the machine; compiled journal syncs to
  a private repo only; `Public-safe: yes/no/unclear` flag per entry; going
  public is a manual owner decision (undecided as of this spec).
- Cloud target: private GitHub repo (owner choice, 2026-09-23).

## Scope

| # | Ticket | Unblocks |
|---|--------|----------|
| 01 | Hook capture (`scripts/journal_hook.py`, `.zcode/config.json`) | 02 |
| 02 | Faithfulness contract (`docs/agents/journal.md`) + digest job spec | 03 |
| 03 | Mechanical audit (`scripts/journal_audit.py`) | 04 |
| 04 | Cloud sync (`scripts/journal_sync.py`) | 05 |
| 05 | Routing (AGENTS.md, .gitignore) + backfill entries + index | — |

Automation registration (CronCreate, daily 07:30) happens only after 01–04
verify. Scheduled-task spec joins
`~/.zcode/workspace/default/imago-scheduled-tasks.md` in house format.

## Non-goals

Public-publication flow · full transcript copying · journaling inside the
`imago/` package · search UI · weekly/monthly digests.
