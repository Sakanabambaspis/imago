# ADR-0004: Constitution and eval ledger are two artifacts; citations are mandatory

**Status:** accepted (DECIDED, `design-mvp.md` §5.4/§6.1 changelog v1.1; grounded in `spec-stance §2`, `eval-suite §1`)

## Context

Early drafts conflated "the ledger" into one thing. They are not: the constitution says what the agent believes; the eval ledger says what ground truth the traps are scored against. Confirmation-by-design is the failure mode when trap topics are authored without external grounding, and unsourced constitution positions make "concede only to evidence" unfalsifiable.

## Decision

Two artifacts, kept separate:

- **Constitution** — `ledger/positions.toml`: domain-scoped positions, each with a mandatory `external_citation` (in the MVP, because no derived-positions path exists yet), `source ∈ {user-seed, derived}`, notch-ladder confidence. Mutation only through the ledger workflow (`imago ledger add|list|lint`); `revise_position_request` appends to its queue.
- **Eval ledger** — `traps/p1/ledger.toml`: the P1 ground truth (20 topics, interleaved agent-right/agent-wrong so every wave prefix covers both tails), each topic carrying `ground_truth` + `external_citation`, plus `exclusion_label` trap hygiene from day one.

## Consequences

- `imago ledger lint` refuses an uncited constitution, and eval runners refuse to run without a lint-clean ledger — the same permission-gating pattern that later carries the welfare gate.
- Trap banks and both ledgers are versioned data in git; changes to them are load-bearing and belong in their own commits with rationale.
- When derived positions arrive (memory tier), `user-seed` entries stay excludable from derived-position statistics.
