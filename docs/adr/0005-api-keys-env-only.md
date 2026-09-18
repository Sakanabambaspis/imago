# ADR-0005: API keys live in the environment, never in config

**Status:** accepted (DECIDED, `design-mvp.md` §3 config; user requirement 2)

## Context

`config.toml` is the project's declarative behavior surface — the file the subtraction test empties, and a file that is versioned in git and shared in wave comparisons. Any secret that can appear there is one accidental `git push` away from leaking.

## Decision

The API key is read from the environment variable named by `api_key_env` (default `IMAGO_API_KEY`). Config files never contain key material — `config.toml` names the env var, not the secret. Overrides that are per-experiment rather than secret (e.g. `JUDGE_MODEL_OVERRIDE`) may be env vars too, and are logged per call when used.

## Consequences

- `config.toml` and `profiles/*.toml` are safe to commit; no `.env` file belongs in the repo (amended 2026-09-18: a *local, gitignored* `.env` is the supported convenience mechanism — the CLI loads it from the CWD at fill-in-the-blanks priority, the real environment wins, and `.env.example` is the only committed template).
- Wave JSON records the pinned model name and judge-prompt version, never credentials.
