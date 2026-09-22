# 05 — Routing + backfill: make the journal load-bearing and non-empty

Status: ready-for-agent
Type: task
Blocked by: 04

## Context

Routing is what makes the journal real: instructions tell agents what never
to do (edit raw, rewrite history), and the backfill makes day one of the
pipeline a populated journal rather than an empty machine.

## What

- `AGENTS.md`: new "### Project journal" subsection — layers, the
  never-edit-raw / past-entries-are-immutable rules, corrections go through
  the digest, and the note that prompts are recorded verbatim (stating
  rationale in prompts is what gets preserved).
- `.gitignore`: add `journal/`.
- `journal/index.md` + `journal/2026-09/` backfill entries, marked
  `Backfill: yes`, `Sources:` git log / research corpus. Rationale quoted
  **only** where commit bodies or corpus files actually state it — no
  reconstruction of "why" that was never written down. Entries: corpus
  research (Sep 15–16), repo import + agent-skills setup (Sep 17),
  provider/config + .env work (Sep 18–19), nightly jobs + adapter backoff
  (Sep 20–22), this journal feature (Sep 23, quoting the owner's request
  messages verbatim from this session).

## Done when

- Routing committed; backfill entries audited by `scripts/journal_audit.py`
  semantics (quotes verifiable against git bodies / corpus files cited);
  index lists all entries.

## Comments

2026-09-23: Done. AGENTS.md routing + `.gitignore` entry committed;
`journal/` seeded with six backfill entries + index. Faithfulness discipline
held: owner-voiced quotes only (research-corpus brief, this session's
messages), commit-body rationale labeled as implementing-session rationale,
and "not stated" used where the owner's pre-capture rationale was never
recorded. `journal/` initialized as its own git repo; cloud push pending
the owner's remote.
