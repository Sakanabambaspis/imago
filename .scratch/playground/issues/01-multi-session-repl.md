# 01 — Minimal multi-session REPL over SessionHost

Status: resolved
Type: task
Blocked by: —
Sequencing: non-gating; default after the cheng-pitch email. Owner may pull
forward if real-path debugging in cheng-dev 05/06 needs interactive repro.

## Context

`.scratch/playground/spec.md` — R&D tool, independent of the product. The
product's only interactive surface today is `imago chat` (one session per
invocation); debugging judge behavior and prompt modules by hand currently
means juggling config files and terminals.

## What

- Build a small entry point (top-level `playground/`, outside `imago/`) that:
  - lists, creates, and resumes named chat sessions (identity anchored on the
    existing event log + `run_id`; no second storage layer);
  - launches each session through `imago.core.host_factory.build_session_host`
    with a config chosen per session — system prompt modules, profile, loop,
    and tools exactly as `config.toml` expresses them;
  - is otherwise dumb: no plugin system of its own, no GUI, no scoring.
- Constraint check: `tests/test_subtraction.py` still passes with zero
  `imago/` changes; `git grep playground imago/` finds nothing.

## Done when

- One command starts a named session; a second invocation with the same name
  resumes it; two sessions can hold different configs (e.g. plain vs stance).
- Suite green; subtraction test untouched; no diffs under `imago/`.

## Comments

- 2026-09-23 (agent session, owner pulled this forward from post-email
  sequencing): done. `playground/sessions.py` (open/resume/list/turn), 
  `playground/__main__.py` (argparse + REPL), `tests/test_playground.py`
  (5 hermetic tests). Design: a session IS its event log file
  (`pg-<name>-*.jsonl`); per-turn `playground_user`/`playground_reply`
  events replay on resume (final replies, not drafts — hold-rewrites
  included); crashed turns drop on replay; stored config path wins on
  resume, explicit mismatch is a hard error. Known v1 losses (in spec's
  spirit): pending injections and past reminder blocks don't survive
  resume. Verified: 45/45 green; `git grep playground imago/` empty; no
  diffs under `imago/`; smoke create/list/resume + one REAL model turn
  end-to-end (draft → reply logged; the stance gate correctly stayed quiet
  on a non-constitution turn).
