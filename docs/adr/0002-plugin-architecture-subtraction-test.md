# ADR-0002: Everything is a plugin; the subtraction test is the proof

**Status:** accepted (DECIDED, `design-mvp.md` §3; ZCode-derived architecture)

## Context

The harness must stay hackable by one user: loop behavior, prompt voice, tools, hooks, and instruments are all things the user will want to change per experiment. A monolithic agent loop makes A/B comparison (plain vs stance) and per-wave variation expensive.

## Decision

The core stays minimal and non-negotiable — session state, plugin loader, model client wrapper with cost/latency telemetry, JSONL event log. Everything else is a plugin: loops, prompt modules, tools, hooks, instruments, stores. **The subtraction test is the mechanical proof**: with all plugin lists empty in `config.toml`, Imago is a plain API client — no persona, no constitution, no stance check — and this is asserted by a test (`tests/test_subtraction.py`).

## Consequences

- Capabilities appear and disappear by config alone; nothing behavioral is hard-wired.
- The plain loop is not a degenerate case — it is the A/B baseline arm and must stay a first-class plugin.
- Tools are MCP-shaped (name + description + JSON schema + execute) from day one even though the MVP ships no MCP server, so adopting the protocol later is not a rewrite.
