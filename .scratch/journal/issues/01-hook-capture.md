# 01 — Hook capture: verbatim prompt + turn markers to the raw layer

Status: ready-for-agent
Type: task
Blocked by: —

## Context

The journal's evidence layer must capture every user prompt verbatim at
utterance time, mechanically — never depending on an agent remembering
(Cline Memory Bank issue #1911: agent claims it updated the journal, writes
nothing). ZCode workspace hooks are the only mechanism that fires regardless
of agent behavior. Supported events include `UserPromptSubmit` and `Stop`
(exactly seven events; `SessionEnd` does not exist). Config-file hooks are
disabled by default and must set `hooks.enabled: true`.

## What

- `scripts/journal_hook.py` (stdlib only, `/usr/bin/python3`): mode arg
  `prompt` | `turn_end`. Reads stdin JSON; every field optional with env
  fallbacks (`ZCODE_PROJECT_DIR`/`CLAUDE_PROJECT_DIR` → payload `cwd` →
  process cwd). `prompt` → append `{schema_v, ts, event:"user_prompt",
  session_id, prompt (verbatim, 64 KB cap + explicit truncation marker),
  payload_echo}`. `turn_end` → append `{event:"turn_end", session_id,
  agent_note (≤2 KB last assistant text if transcript parseable, else
  omitted), payload_echo}`.
- Appends one JSON line per event to `.imago/journal/raw/YYYY-MM-DD.jsonl`
  under `fcntl.flock` on a lockfile. Prints nothing. **Always exits 0.**
  No network.
- `.zcode/config.json`: `hooks.enabled: true`, both events registered as
  `command` hooks with `timeout: 10` (seconds), invoking the script via
  `${ZCODE_PROJECT_DIR}`.

## Verification

- Fuzz: empty stdin, malformed JSON, missing fields, 2 MB prompt → valid
  line or documented minimal line, exit 0 always, <100 ms. Run against a
  temp project dir so the real raw layer stays clean.
- Concurrency: 20 parallel invocations → exactly 20 lines, every line parses.
- Live fire: `jq .hooks.enabled .zcode/config.json` = true; config loads on
  next session start (verify then: tail today's raw file after a real turn).

## Done when

- Script + config committed; fuzz and concurrency checks pass on record.

## Comments

2026-09-23: Done. `scripts/journal_hook.py` + `.zcode/config.json`
(`hooks.enabled: true`). Fuzz: empty stdin, malformed JSON, 2 MB prompt,
missing transcript — all exit 0 with valid or documented-minimal lines;
20 parallel writers → 20 intact lines; torn-line guard added and tested;
~70 ms per invocation. Live fire lands when hooks load at next session
start.


## Migrated

Imported as GitHub issue #15 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
