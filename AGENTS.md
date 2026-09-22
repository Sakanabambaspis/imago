# AGENTS.md

Imago — a single-user, API-key CLI harness that holds correct positions under user
pushback and concedes only to evidence. Read `CONTEXT.md` first, then `docs/design-mvp.md`
for non-trivial work; contradicts-an-ADR findings must be surfaced, not silently applied.

## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/<feature>/` in this repo (no remote yet). See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage-role labels are used verbatim as the `Status:` line of `.scratch/` tickets. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at the root + `docs/adr/`. See `docs/agents/domain.md`.

### Project journal

Dev-process capture runs mechanically: ZCode hooks append every prompt and
turn-end to `.imago/journal/raw/` (append-only, local-only, gitignored). A
scheduled digest compiles `journal/` — its own git repo, private GitHub
remote — per the faithfulness contract in `docs/agents/journal.md`. Never
edit the raw layer or past day files; corrections go through the digest.
Prompts are recorded verbatim, so stating design rationale in prompts is
what gets preserved.

## Git conventions

- Trunk-based on `main`. Short-lived branches are fine for risky experiments (e.g. a countermeasure stack between waves); merge back promptly — there is no review gate for a solo repo, there is only history.
- Subjects in imperative mood ("Add Wilson CI to wave report"), body for rationale, especially **why** and, for eval-affecting changes, the wave it will be measured in.
- `ledger/positions.toml`, `traps/` and `profiles/` are load-bearing versioned data, not config dust: changes to them get their own commit with the citation or rationale in the body.
- `.imago/` (run artifacts), `.venv/` and caches are gitignored and never committed; wave reports that matter are copied into `docs/results/` as one-page notes.
