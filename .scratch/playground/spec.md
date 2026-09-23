# Spec: playground — R&D chat tool, independent of the product

**Track: TOOLING.** Not a product, not a pivot. A workshop for developing and
debugging Imago itself. Decided 2026-09-23 after the "build an LLM playground
instead" alternative was evaluated and rejected as a product replacement
(contradicts ADR-0001); this spec records the accepted narrow version.

## Purpose

Interactive, multi-session chat for development work the batch runners can't
do: reproduce a judge misfire conversationally, hand-probe verdict prompts /
profiles / constitution modules before freezing them in a wave, poke the real
API path between hermetic runs. The instrument (`imago eval`) stays the only
source of numbers; the playground produces impressions, never results.

## Independence rules (binding)

- Lives outside `imago/` (e.g. a top-level `playground/`). Product code never
  imports it; nothing in `imago/` may change to serve it.
- One-way dependency: `playground → imago.core` (`host_factory`, `config`,
  `adapters`). The subtraction test must keep passing untouched.
- Its tickets never block `cheng-dev 01→07` or the `cheng-pitch` email.
  Default sequencing: after the email, alongside the 08–11 runway, unless the
  owner explicitly pulls a ticket forward (e.g. real-path debugging during
  cheng-dev 05/06 demands it).

## Feature bar (v1 — deliberately small)

- Multiple named chat sessions, resumable. Build on the event log and `run_id`
  that already exist; do not invent a second storage layer.
- Per-session behavior comes from an Imago config: system prompt (prompt
  modules + constitution), profile, loop choice, tool access — the same knobs
  as `config.toml`, no parallel configuration system.
- Everything else — web UI, provider management, tool-schema editors, sharing,
  "modular as possible" plugin machinery of its own — is out of scope until a
  concrete session of dev work demands it. The product's registry is already
  the configurability story; the playground is a dumb client over it.

## Non-goals

- No product features, no scoring, no wave logic, no GUI by default.
- No changes to `imago/` to accommodate it (if a change seems needed, that is
  a `revise_position_request` against this spec, not a quiet edit).
