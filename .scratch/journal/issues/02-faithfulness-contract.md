# 02 — Faithfulness contract + digest job spec

Status: ready-for-agent
Type: task
Blocked by: 01

## Context

The compiled journal is written by a scheduled agent, and everything an
agent writes about "why" is the agent's theory of the owner's mind — post-hoc
rationalization (Parnas & Clements). The contract exists to keep the owner's
actual rationale (verbatim prompts) load-bearing and the agent's inference
visibly labeled.

## What

- `docs/agents/journal.md`: entry template (header with `Compiled:` /
  `Sources:` / `Sessions:` / `Public-safe:`; Narrative; User rationale
  verbatim with `raw/<file>.jsonl#L<n>` citations; Decisions with
  `Rationale:` = user-quote ref or `not stated`; `[agent inference]` label;
  Open questions; Ops & background) + the rules (quote-don't-paraphrase,
  no spliced quotes, past day files immutable, raw is append-only evidence,
  personal topics ⇒ `Public-safe: no`, report-only nightly jobs go under
  Ops) + digest operating procedure (audit `--dump` → compile → audit
  `--advance` → sync → nightly report).
- Digest job spec appended to
  `~/.zcode/workspace/default/imago-scheduled-tasks.md` in house format:
  daily 07:30 (after the 06:55 end of the night shift), hard deadline,
  nightly report + LATEST.md refresh.

## Done when

- Contract committed; job spec added to the scheduled-tasks file (CronCreate
  registration is a separate final step, after 01–04 verify).

## Comments

2026-09-23: Done. `docs/agents/journal.md` committed (template + 8 rules,
including the backfill/addendum rule); job spec appended to
`~/.zcode/workspace/default/imago-scheduled-tasks.md` as
`imago-journal-digest` — daily 07:30, hard stop 08:30, after the night
shift ends. Automation registered via CronCreate same day.
