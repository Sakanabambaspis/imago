# 01 — Minimal multi-session REPL over SessionHost

Status: ready-for-agent
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
