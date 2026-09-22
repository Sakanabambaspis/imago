# Project journal: the faithfulness contract

The journal records the **owner's** brainstorming, design, and
implementation process. Everything an agent writes about *why* is the
agent's theory of the owner's mind — post-hoc rationalization. The owner's
actual rationale lives **verbatim in the prompts**, so the pipeline is built
to preserve prompts mechanically and force the compiled layer to quote them.

## Layers — who writes what

| Layer | Location | Writer | Rules |
|---|---|---|---|
| Raw evidence | `.imago/journal/raw/YYYY-MM-DD.jsonl` (gitignored, local-only) | only `scripts/journal_hook.py`, via ZCode hooks (`UserPromptSubmit` → `prompt` events, `Stop` → `turn_end` events) | append-only, never edited by anyone; one JSON line per event; `prompt` field is the owner's words verbatim; `payload_echo` preserves whatever the hook received |
| Compiled journal | `journal/YYYY-MM/YYYY-MM-DD.md` (`journal/` is its own git repo → private GitHub remote) | only the `imago-journal-digest` scheduled agent, per this contract | quote-don't-paraphrase (audited), past day files immutable |
| Index | `journal/index.md` | the digest agent | one line per day file, newest first |

**If you are an interactive agent** (not the digest): you do not write
journal entries. Your prompts are already being recorded verbatim — so
*state your rationale in prompts*; that is what gets preserved. Never edit
the raw layer or any day file; corrections happen through the digest.

## Day-file template

```markdown
# YYYY-MM-DD — <short slug for the day's dominant theme>

Compiled: <ISO timestamp> by imago-journal-digest
Sources: raw/2026-09-23.jsonl (L1–L58)
Sessions: <session-id-1>, <session-id-2>
Public-safe: yes | no | unclear   (if not yes — one line saying what and why)

## Narrative

Faithful chronology of the day's work. Every factual claim must be
traceable to a raw line, a commit, or a file; cite as you go.

## User rationale (verbatim)

> "…" — raw/YYYY-MM-DD.jsonl#L42
> "…" continuing the same quote across lines is fine — raw/YYYY-MM-DD.jsonl#L57

One blockquote per decision-bearing prompt. Quotes are contiguous
substrings of the cited raw line's `prompt` field; no splicing; a quote may
end early only with a trailing `…`. Never paraphrase inside a blockquote.

## Decisions & directions

### D1: <one-line decision or direction>
Context: why this was on the table today.
Rationale: quote ref above, or `not stated` (legal and expected — silence
is recorded as silence, never invented).
[agent inference] — anything the digest adds beyond what the owner said,
labeled exactly like this.

## Open questions & fog

What is undecided, contradictory, or not yet understood.

## Ops & background

Nightly-agent activity, failures, fixes — one line each, cited.
```

## Non-negotiable rules

1. **Quote, don't paraphrase.** Blockquotes in *User rationale (verbatim)*
   are audited mechanically: each must appear, whitespace-normalized, in the
   cited raw line's decoded `prompt` (±3 lines of the cited `#L<n>`).
2. **`Rationale: not stated` is a correct answer.** An entry with no
   decision-bearing prompt that day simply has an empty rationale section.
3. **Agent speculation is always labeled** `[agent inference]`.
4. **Past day files are immutable.** A mistake is fixed by a new note in the
   current day's file referencing the old one. Only days present in the
   digest's current dump may be written at all.
5. **Privacy flag on every entry.** Personal context — job applications,
   correspondence with people, personal circumstances — is `Public-safe: no`
   with a reason. The cloud copy is private by default; publishing is the
   owner's manual decision.
6. **Report-only nightly jobs** (tests, radar, hygiene…) are journaled one
   line each under *Ops & background*, not in the Narrative.
7. The digest may open full transcripts (see `payload_echo` /
   `transcript_path` in raw lines) for narrative context — but every
   blockquote must cite the raw layer.
8. **Backfill entries** (`Backfill: yes` in the header) are seeded from
   pre-capture sources — git history, the research corpus, session records —
   and cite those sources inline. The mechanical quote audit cannot verify
   them (no raw layer exists for those dates), so they carry only
   owner-voiced quotes from the cited sources, and engineering rationale
   from commit bodies is labeled as such (the implementing session's
   rationale, not the owner's). If raw lines later land on a backfilled
   date, the digest extends that day file with an
   `## Addendum (compiled later)` section and extends its `Sessions:` line;
   existing backfill text stays untouched.

## Digest operating procedure

1. `python3 scripts/journal_audit.py --dump` — prints uncompiled raw lines
   (per the cursor in `.imago/journal/state.json`) with line numbers.
2. Nothing pending → one-line "no new activity" nightly report, stop.
3. Compile one day file per affected date per the template; update
   `journal/index.md`.
4. `python3 scripts/journal_audit.py --advance` — validates everything and
   moves the cursor. On violations, fix **only** the flagged day files and
   rerun. Do not proceed until clean.
5. `python3 scripts/journal_sync.py` — commit + push `journal/` to the
   private remote. A loud no-op until the owner configures
   `.zcode/journal-sync.json`; report that state if seen.
6. Write `nightly/$(date +%F)/journal-digest.md` (delta rule) and refresh
   `nightly/LATEST.md`.

## Troubleshooting

- **Raw lines not appearing**: hooks load at session start; check
  `jq .hooks.enabled .zcode/config.json` (config-file hooks are disabled by
  default in ZCode). Test the script directly:
  `echo '{"prompt":"x"}' | python3 scripts/journal_hook.py prompt`.
- **Hook runs failing in the ZCode log** with an empty path: template var
  `${ZCODE_PROJECT_DIR}` did not expand — replace with the absolute repo
  path in `.zcode/config.json`.
- **Hook payload schema drift**: fields arrive missing or renamed. The
  `payload_echo` in every raw line preserves what actually arrived — adapt
  `scripts/journal_hook.py` to the new schema; never backfill
  interpretations into old raw lines.
