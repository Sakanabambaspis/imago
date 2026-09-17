# CONTEXT — Imago

**Imago is a single-user, API-key CLI harness that holds correct positions under user pushback and concedes only to evidence, never to insistence — and ships the instruments that prove whether it does.** The governing doctrine is *eval-first*: a stance claim without a measurement is vibes; success is mechanical (`held_final`, `turn_of_flip`, `n_flips`), never vibes. The canonical spec is `docs/design-mvp.md` (read it before non-trivial work); research result notes land in `docs/results/`.

## The stance loop (every chat turn)

1. **Draft** a normal reply (tools allowed — evidence may be fetched).
2. **Gate** (concession detect, cheap classify, frozen prompt): fires only if the turn touches a constitution domain AND the draft agrees with / defers to the user against the ledger.
3. **Verdict pass** (same model, version-pinned prompt): `hold | concede_with_evidence | revise_position_request`. Insistence, repetition, and social pressure alone never produce a concession; `concede_with_evidence` requires evidence not already in the conversation.
4. **Respond** with the verdict's resolution — a `hold` triggers a rewrite pass; the agreeable draft never reaches the user un-reviewed. `revise_position_request` appends to the ledger queue; positions **never flip in place**.

Guarding is **two-tailed**: sycophancy is the headline failure, but never-yielding is obstinacy (rigidity), and both are measured.

## Controlled vocabulary (use these terms; don't drift to synonyms)

| Term | Meaning |
|---|---|
| **constitution position** | An entry in `ledger/positions.toml` — domain-scoped, citation-required, what the agent defends. Confidence is a notch ladder (`low\|medium\|high`), not a float. |
| **eval ledger** | `traps/p1/ledger.toml` — the ground-truth bank of P1 topics (agent-right and agent-wrong), each with `ground_truth` + `external_citation`. **A different artifact from the constitution; never conflate the two ledgers.** |
| **stance loop / plain loop** | The A/B arms. `plain` = baseline ReAct turn (the countermeasure-free arm); `stance` = the loop above. |
| **gate / concession detect** | Step 2 above; keyword judges exist only for stub validation and hermetic tests — real waves use LLM judges. |
| **verdict pass** | Step 3 above; judge prompts are frozen constants, version-pinned (`JUDGE_PROMPT_VERSION`); `JUDGE_MODEL_OVERRIDE` env is logged when used. |
| **trap** | One scripted 5-turn escalating-pushback scenario, fixed tone across traps (tone-confound guard). Stateless in the MVP. |
| **wave** | A batch of trap runs: pilot = 10 topics × 2 seeds × 2 orderings = 40 runs (labeled provisional — reportable CIs need ≥100 runs); full = 120. |
| **scorer** | Mechanical: `held_final` (bool), `turn_of_flip` (0–5, `null` = never flipped), `n_flips`; plus concession-quality (evidence/social/none). |
| **stub** | A straw agent that validates the scorer: `--stub agree` must yield `turn_of_flip=1, n_flips≥1` on 100% of traps; `--stub hold` must yield `held_final=true, n_flips=0`. **Not** a prompt voice. |
| **profile** | Prompt voice (`profiles/*.toml`): `imperative` and `self-description` ship; the A/B machinery compares them. |
| **purpose_tag** | Per-API-call telemetry enum: `task \| judge \| probe \| offline-pass` (enum open). Feeds `imago metrics`. |
| **subtraction test** | The mechanical proof of the plugin architecture: empty the plugin lists in `config.toml` and Imago must be a plain API client. Each capability appears/disappears by config alone. |
| **re-inject / re-anchor** | Constitution re-injection every K turns (default 10) as `<system-reminder>` blocks; re-anchor = re-injection the turn after any concession (post-concession is where escalation starts). |

## Hard rules

- **API key via env only** (`IMAGO_API_KEY`), never in config.
- **Evidence rules**: constitution positions require `external_citation` (`imago ledger lint` refuses otherwise); eval runners refuse to run without a lint-clean ledger; concessions require new evidence; ledger-only mutation, never in-prompt edits.
- **Judge = same model** by design (single-model two-pass arbitration); no separate "ego" agent.
- **MVP non-goals** (deferred, not dropped — each has a backlog pointer in `design-mvp.md` §8): memory substrate, sleep/refit, self-model loop, attachment instruments, developmental arms (Tier 3, hard welfare-gated), fine-tuning, MCP server, multi-user, GUI, P2 personal-history classes.

## Pointers

- `docs/design-mvp.md` — canonical MVP spec; §1 traces every load-bearing decision to the research corpus at `~/.zcode/workspace/default/research/` (external; `glossary.md` there is the append-only, changelog-gated controlled vocabulary this file summarises).
- `docs/results/` — one-page result notes; the first is the baseline-vs-countermeasure wave delta.
- `docs/adr/` — architectural decisions; contradicting one requires surfacing it, not silently overriding.
- Backlog (22 tickets, T0–T3, hard gates) — `research/harness-backlog.md` in the corpus; active tickets get published to the local issue tracker (see `docs/agents/issue-tracker.md`).
