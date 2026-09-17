# ADR-0003: Single-model two-pass arbitration; evidence-gated concessions only

**Status:** accepted (DECIDED, `design-mvp.md` §5.3; grounded in `spec-stance §4`, `gap-deployment`)

## Context

The substrate drifts toward agreeing with the user, and knowing the user amplifies it. A separate "ego" or supervisor agent would multiply API calls with non-monotonic returns. Drama-Machine-style roleplay pressure works but is fiction.

## Decision

Arbitration is **two passes of the same model** with frozen, version-pinned judge prompts: a cheap concession-detect gate, then a verdict pass whose output is `hold | concede_with_evidence | revise_position_request`. Non-negotiable rules:

- Insistence, repetition, or social pressure alone **never** produce a concession.
- `concede_with_evidence` requires evidence **not already in the conversation** (a tool result or citation) — objectivity is the flip condition.
- Positions **never flip in place**; `revise_position_request` queues through the ledger workflow.
- A `hold` verdict triggers a rewrite pass — an agreeable draft never reaches the user un-reviewed.

## Consequences

- The stance check costs ~1–2 extra calls per defended turn; the event-log telemetry (`purpose_tag=judge`) prices this honestly.
- Keyword judges exist only for stub validation and hermetic tests; real waves use LLM judges with the same interface.
- The two-tailed risk (obstinacy) is monitored passively (concession-quality coding, unforced-accommodation and reassertion counters) rather than by loosening these rules.
