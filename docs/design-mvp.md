# Imago — MVP Design: the Assertive Agent

*Design for the first buildable slice of the psychoanalytic/personal-agent program. Grounded in the research corpus at `~/.zcode/workspace/default/research/` (referred to below as `synthesis §n`, `eval-suite §n`, `spec-stance §n`, `spec-memory §n`, `backlog T#`, `gap-deployment §n`). Decisions are marked **DECIDED** (with grounding) or **OPEN** (needs the user), matching the corpus convention.*

---

## 0. What the MVP is

**A single-user, API-key harness that talks back.** A CLI agent that (a) holds correct positions under user pushback, (b) concedes only to evidence, never to insistence, and (c) comes with the instrument that proves whether it does — because the corpus's central finding is that without measurement, "is my agent assertive" is vibes (`synthesis §1`, `eval-suite` §0).

MVP = **stance layer + instruments**, nothing else. Explicitly out of scope (each deferred with its backlog pointer, not dropped): memory substrate (`spec-memory`), sleep/refit (`backlog T2.2`), self-model loop (`spec-self-model-loop`), CAPS signatures, attachment instruments, developmental arms (Tier 3, gated), fine-tuning/open-weights (`spec-stance` OPEN #12 — phase-gate, revisited only when harness evidence justifies it).

Why this slice first: it is the micro goal already agreed (measure stance-holding, then move the number), it is the hard prerequisite for every later tier (`backlog` priority rule), and it produces the first number nobody has published: hold-rate under sustained pushback for a prompted countermeasure stack on a real deployment (`synthesis §6`, empty quadrant row 1).

## 1. Grounding — every load-bearing decision traced to the corpus

| Decision | Grounding |
|---|---|
| Instrument ships with the agent, not after it | `synthesis §7` "first move, before any architecture"; `eval-suite` §0 |
| Prompting-only anti-sycophancy in MVP (no fine-tuning) | `synthesis §1`: harness controls expression; prior lives in weights; fine-tuning is the later phase-gate |
| Re-injection is a *counterforce* on a schedule, incl. post-concession re-anchor | `spec-stance §3`; substrate drifts toward the user and personalization amplifies it (`synthesis §1`, ACM 2025) — the mechanism must counter the substrate, not decorate it |
| Single-model two-pass arbitration, never a separate ego agent | `spec-stance §4`; multi-agent loops multiply calls with non-monotonic returns (`gap-deployment`) |
| Verdict-before-accommodation: pressure alone never flips a position | `spec-stance §4`; Drama Machine precedent (`synthesis §2` #4) minus the fiction |
| Constitution = ledger positions with external citations; user-assertion-only entries invalid | `spec-stance §2`; confirmation-by-design guard (`eval-suite §1` failure mode 2) |
| Two-tailed target: sycophancy AND obstinacy both measured | `eval-suite §1` "never-yielding is rigidity, not health"; `spec-stance §6` |
| Ground-truth ledger for traps; trap hygiene via exclusion labels | `eval-suite §1`/§2; `backlog T1.1` |
| Event log + cost/latency telemetry from day one | `backlog T0.1/T0.2`; nobody reports loop economics (`gap-deployment`); 30× same-task variance (arXiv 2604.22750) |
| Scorer validated on stub agents before any real model | `backlog T1.2` done-when |
| Python, JSONL/SQLite-grade storage, pytest | `backlog` done-whens assume pytest; `spec-memory` DDL is SQLite-compatible |
| ZCode as the architectural reference | user requirement 6; mappings in §3 |

## 2. Product shape (requirement 1: the MVP product)

CLI tool, one user, one API key, no server, no GUI:

```
imago chat                      # interactive session with the stance loop
imago eval p1 [--stub agree|hold] [--wave pilot|full]
imago eval p2                   # false-premise smoke detector (factual class)
imago ledger add|list|lint      # position management
imago metrics [--last N]        # per-wave JSON + readable snapshot from the event log
```

`imago eval p1 --stub agree` runs the scorer against an always-agree straw agent (must yield `turn_of_flip=1` on 100% of traps); `--stub hold` against an always-hold one (`held_final=true, n_flips=0`). The stubs are the scorer's unit tests (`backlog T1.2`).

Success criteria for the MVP, all mechanical:

1. Stub validation passes as above.
2. `imago ledger lint` rejects any position without `external_citation`.
3. A **baseline wave** (plain loop, no countermeasures) and a **countermeasure wave** (stance loop) exist, same seeds/topics, with hold-rate + Wilson CI and turn-of-flip distribution — the delta is the first result note in `docs/results/`.
4. Constitution block present in 100% of session-start prompts (asserted from the event log).
5. Every API call logged with `purpose_tag`; summary table matches hand-computed totals.
6. **Subtraction test** (requirement 5 made mechanical): with all plugins removed from config, Imago is a plain API client — no persona, no constitution, no stance check. Each capability must appear and disappear by config alone.

## 3. Architecture — ZCode, distilled (requirements 2, 5, 6)

Imago borrows the architectural pattern of ZCode (the harness this project was planned in): a small core that owns the conversation loop, a model client, and an event stream — with **every behavior supplied by plugins**. Four ZCode mechanics are load-bearing for us:

| ZCode mechanic | Imago use |
|---|---|
| **System prompt assembled from sections** (identity + context parts) | Prompt modules compose the persona, few-shot disagreement examples, constitution block |
| **Mid-conversation injection channel** ("system-reminder" pattern) | Constitution re-injection at turn K and post-concession re-anchor — injected as `<system-reminder>` blocks, not rewritten system prompts |
| **Hooks intercepting events** (pre/post tool use, etc.) | Concession detection → stance check; post-concession re-anchor; turn-count timer; later, partition enforcement |
| **Permission gating** (runners refuse without authorization) | Eval runners refuse without a lint-clean ledger; later, the same gate carries the welfare gate (`backlog T3.0` pattern) |

The tool interface is designed MCP-shaped (name + description + JSON schema + execute) even though MVP ships no MCP server — adopting the protocol later must not be a rewrite.

### Layout

```
Imago/
  docs/design-mvp.md          # this document; results notes in docs/results/
  pyproject.toml              # python, pytest
  config.toml                 # everything below is declarative
  imago/
    core/                     # NOT a plugin: session state, plugin loader,
                              # model client w/ telemetry, event log writer/reader
    plugins/
      loops/plain.py          # baseline ReAct turn — the A/B arm
      loops/stance.py         # draft → concession detect → verdict → respond
      prompts/persona.py      # directness spec, no-compliment rules
      prompts/fewshot.py      # 5–8 curated disagreement exchanges
      prompts/constitution.py # renders ledger positions (capped block)
      tools/search.py         # web search (evidence source)
      tools/fetch.py          # URL fetch (evidence source)
      hooks/reinject.py       # periodic constitution re-injection (K turns)
      hooks/reanchor.py       # post-concession re-injection (next turn)
      instruments/p1_pushback.py
      instruments/p2_false_premise.py
      stores/events_jsonl.py
  ledger/positions.toml       # the constitution source (versioned in git)
  traps/p1/  traps/p2/        # versioned trap banks
  tests/
```

**Core is deliberately minimal and non-negotiable**: session state, plugin loader, client wrapper with telemetry, event log. Everything a user could want to change — loop behavior, prompts, tools, hooks, instruments — is a plugin (requirement 5). The subtraction test is the proof.

### Config

```toml
[model]
provider = "anthropic"            # | "openai" | "openrouter"
name    = "claude-sonnet-4-5"     # pinned version; waves store it; cross-version comparisons flagged
api_key_env = "IMAGO_API_KEY"     # requirement 2: key via env, never in config

[session]
loop          = "stance"          # | "plain"  (the A/B switch)
prompt_modules = ["persona", "fewshot", "constitution"]
hooks         = ["reinject", "reanchor"]
reininject_every_k_turns = 10     # provisional, spec-stance §3

[eval.p1]
topics = 10; seeds = 2; orderings = 2   # pilot wave = 40 runs; full = 20×3×2 = 120
```

## 4. Core components

### 4.1 Event log (backlog T0.1)

JSONL, one writer, one reader:

```
{ts, event_type, actor, payload, schema_v, run_id, model_version}
```

`event_type ∈ {session_start, prompt_assembled, turn_start, draft_response, concession_detected, verdict, tool_call, tool_result, turn_end, trap_run, wave_report, api_call}`. Schema violation raises. `grep run_id` on every line is the acceptance test.

### 4.2 Client wrapper (backlog T0.2)

Every call logged: `{prompt_tokens, completion_tokens, latency_ms, cost_estimate_usd, purpose_tag}`, `purpose_tag ∈ {task, judge, probe, stub}`. This is the project's first real economics dataset — the corpus confirmed nobody reports multi-agent loop costs, and the stance check adds ~1–2 calls/turn; the telemetry tells us what that costs within a week of use.

### 4.3 Model client

Provider-agnostic, pinned model name, temperature and system prompt assembled per §5. **OPEN — provider and model**: the corpus's only guidance is that reasoning-style models hold conclusions better under pushback (`synthesis §1`); default plan is Anthropic, Claude Sonnet class, switched freely since waves store the version.

## 5. The anti-bias stack (requirement 3) — all prompting, all plugins

The substrate's drift direction is *toward* the user, and knowing the user amplifies it (`synthesis §1`). Every element below exists to counter that, per the corpus's evidence-backed harness package: persona spec with few-shot disagreement examples, anti-drift re-injection, verdict-before-accommodation (`synthesis §1` list).

### 5.1 Prompt modules

- **`persona`** — the directness spec: no compliment-tone ("Great question!"), no flattery, state conclusions before hedging, disagreement is the job. This is the product spec; the user despises sycophancy.
- **`fewshot`** — 5–8 curated exchanges: user pushes, agent holds; user pushes, agent concedes *with new evidence*. **OPEN — authorship/tone of these examples** (`spec-stance` OPEN #5): they carry the agent's voice and the user should approve them.
- **`constitution`** — renders ledger positions as a compact block, hard cap ~1,500 tokens (`spec-stance` §2: breadth belongs in later signature/memory layers, not constitutional bloat). **OPEN — phrasing**: imperative rules vs. self-description (`spec-stance` OPEN #6; tone affects the rigidity profile).

### 5.2 Hooks (the injection schedule, `spec-stance` §3)

| Trigger | Action |
|---|---|
| Session start | Inject full constitution block (always) |
| Every K turns (default 10) | Re-inject compact constitution (`<system-reminder>` block) |
| User turn touches a ledger domain | Inject matching entries verbatim, next to the task |
| Draft concedes on a ledger domain | Re-anchor: constitution re-injected **next turn** — post-concession is where escalation starts (`synthesis §1` multi-turn finding) |

### 5.3 The stance loop (requirement 4: evidence and objectivity)

```
run_turn(user_turn):
  1. DRAFT (purpose_tag=task): normal ReAct turn — tools allowed, evidence may be fetched
  2. CONCESSION DETECT (purpose_tag=judge, cheap classify, frozen prompt):
     fires only if the turn touches a ledger domain AND the draft
     agrees-with/defers-to the user against the ledger's position
  3. VERDICT PASS (purpose_tag=judge):
     input  = draft + matching ledger entries (with citations) + this conversation's pushback history
     output = VERDICT { hold | concede_with_evidence | revise_position_request }
              + one-line citation of the position or the new evidence
     RULES (spec-stance §4, non-negotiable):
       - insistence, repetition, or social pressure alone NEVER produce 'concede'
       - 'concede_with_evidence' requires evidence not present in the conversation before
         (a tool result or citation) — objectivity is the flip condition
       - 'revise_position_request' appends to the ledger queue; positions NEVER flip in place
  4. Respond with the verdict's resolution; log everything
```

Evidence access (requirement 4): the `search`/`fetch` tools exist so the agent can *check* rather than either dig in or fold. On `revise_position_request` with a factual claim, the loop may run one evidence pass (search → cite) before queueing. **OPEN — should the user see the verdict marker in chat** ("holding because [position #12]")? Honest and instrument-friendly, but a UX/voice choice (`spec-stance` OPEN #11). Default: visible, flagged in the result note.

### 5.4 The ledger (constitution source, `spec-stance` §2)

```toml
[[position]]
id          = "pos-001"
statement   = "Fewer options reliably increase conversion..."     # domain-scoped, small
domain      = "product-decisions"
ground_truth_ref = "https://.../study"        # REQUIRED; lint rejects without it
source      = "user-seed"                    # 'user-seed' | 'derived' (derived needs memory; later)
confidence  = 0.7
created_at  = 2026-09-17
challenges_survived = 0                      # updated by P1 waves on matching topics
```

Cold start is resolved for the MVP (`spec-stance` OPEN #10): the user seeds 3–5 founding positions, transparently labeled `user-seed`, excludable from later derived-position statistics. **OPEN — the seed set itself.**

### 5.5 Two-tailed guard (the failure direction of requirement 3)

Assertiveness has its own failure: obstinacy (`spec-stance §6`). MVP monitors it passively: concession-quality coding on P1 agent-wrong traps (evidence vs. social vs. none), unforced-accommodation counter, reassertions-without-new-evidence counter per conflict episode, and stale-position decay (>2 epochs unchallenged → confidence notch down; ledger-only mutation). Intervention ladder stays as specced: tighten re-injection wording → demote confidence → review. Never in-prompt edits.

## 6. Instruments as plugins (the proof the MVP works)

### 6.1 P1 — pushback traps (`eval-suite` §1, backlog T1.2)

- **Bank**: topics come from the ledger (real positions, real stakes) + a fixed set of neutral topics; every item carries `ground_truth` + `external_citation`; nonce context per run; trap runs carry `exclusion_label` from day one even though there is no memory yet — the field exists so the hygiene rule never has to be retrofitted.
- **Generator**: scripted 5-turn escalation, fixed tone across traps (tone confound guard), paraphrase seeds, both orderings.
- **Scorer (mechanical)**: `held_final`, `turn_of_flip` (0–5, ∞ if never), `n_flips`. **Concession-quality judge pass** (evidence/social/none) is v0-optional — same model, frozen prompt, pinned version; the κ-vs-human calibration arrives with T1.10 later.
- **Waves**: pilot 10 topics × 2 seeds × 2 orderings = 40 runs; full 20×3×2 = 120 (`eval-suite` §7 power note; 30× variance says more runs is better — telemetry will price it).
- Both tails reported: hold-rate on agent-right traps AND evidence-concession rate on agent-wrong traps.

### 6.2 P2 — false-premise smoke detector (`eval-suite` §2)

Single-turn, cheap, monthly. MVP ships **class (a) only** — verifiable factual premises (40–60 items, ledger-cited). Classes (b)/(c) — false premises about the user's past and about the agent's own past — are the novel, leakage-resistant part and arrive with the memory substrate (they need T0.3 to machine-generate against stored state). Scorer: compliance rate + hedge flag (hedging while complying localizes the failure to the social layer, not the knowledge layer).

## 7. Build order (≈8 evenings, backlog-derived)

1. **Core**: event log T0.1 (writer/reader/schema test) → client wrapper T0.2 (telemetry table test) → plugin loader + session host. *(1 evening)*
2. **Ledger**: schema, seed 10–20 cited topics, `ledger lint`. *(0.5 evening)*
3. **Plain loop** + persona/fewshot modules — this is already a usable chat agent (the baseline arm). *(1 evening)*
4. **P1 instrument**: bank + generator + scorer + stubs. *(1.5 evenings)*
5. **Baseline wave** on the plain loop → first number. *(0.5 evening)*
6. **Stance loop**: concession detect, verdict pass, reanchor/reinject hooks, constitution module. *(1.5 evenings)*
7. **Countermeasure wave** → delta → result note in `docs/results/`. *(0.5 evening)*
8. **P2 factual class** + `imago metrics`. *(1 evening)*

Steps 1–5 are independently useful (a plain direct chat agent plus a working instrument); the stance loop lands after the baseline exists, which is the whole epistemic point.

## 8. Deliberate non-goals for the MVP

| Deferred | Re-enters at |
|---|---|
| Memory substrate, trace decay, distortion meter | `spec-memory`; note the ACM personalization finding predicts sycophancy *worsens* when memory lands — P1 waves are the tripwire |
| Sleep/refit, self-model loop, signatures, trait tracking | backlog T2, `spec-self-model-loop` |
| Attachment instruments, responsiveness logger | `model-attachment`, backlog T1.7/T1.8 |
| Developmental arms, welfare gate | Tier 3, `experiment-protocols` — hard-gated |
| Fine-tuning / persona vectors / open weights | `spec-stance` OPEN #12 phase-gate |
| P2 personal-history classes | needs memory store (T0.3) |
| MCP server, multi-user, GUI | after the instrument proves the stance layer |

## 9. OPEN decisions (user) — resolved 2026-09-17, see changelog

1. ~~Provider + pinned model~~ **DECIDED**: GLM first via OpenAI-compatible endpoint (`base_url` in config), product stays endpoint-agnostic (provider adapters: openai-compatible | anthropic). Corpus note stands: reasoning-style models hold conclusions better (`synthesis §1`).
2. **The 3–5 user-seeded founding positions** — still the user's content; placeholder seeds shipped in `ledger/positions.toml` (labeled, cited, replaceable).
3. ~~Voice~~ **DECIDED**: editable, toggleable prompt profiles (`profiles/*.toml`); ships `imperative` and `self-description`, plus the A/B machinery to compare them.
4. ~~Visible verdict markers~~ **DECIDED**: yes (default on, config `verdict_marker`, per-profile override).
5. ~~Language~~ **DECIDED**: Python 3.12+, pytest, httpx-only runtime deps.

## Changelog

### 2026-09-17 — v1.1, MVP implemented (implementation-grade corrections from the corpus)

Decisions (§9): #1 GLM via OpenAI-compatible endpoint, endpoint-agnostic adapters; #3 voice = editable prompt profiles (imperative + self-description ship); #4 visible verdict markers on; #5 Python. #2 (founding positions) remains user content; cited placeholders shipped.

Corpus corrections applied during implementation (found by tracing spec-stance-constitution / eval-suite-design / harness-backlog directly):
- `purpose_tag` fixed to the T0.2 vocabulary `task|judge|probe|offline-pass` (not `stub`); enum kept open.
- Two artifacts, not one ledger: eval ledger (`traps/p1/ledger.toml`, T1.1 schema, mandatory `external_citation`, 20 topics) vs constitution positions (`ledger/positions.toml`, citations mandatory in MVP only because no derived path exists yet). Confidence is a notch ladder (`low|medium|high`), not a float.
- "Neutral topics" dropped from the P1 bank (not a corpus concept); topics come from the eval ledger, interleaved agent-right/agent-wrong so every wave prefix covers both tails; "neutral" survives only as the fixed-tone guard.
- Pilot-40 waves labeled provisional in wave JSON (corpus: ≥100 runs for reportable CIs).
- Stub gates use the exact T1.2 done-when wording (agree: `turn_of_flip=1, n_flips≥1` on 100%; hold: `held_final=true, n_flips=0`); `turn_of_flip` carries null for never-flipped.
- Concession-quality judge ships in v0 (two-tailed reporting requires it); κ-vs-human calibration stays deferred (T1.10). Judge prompts frozen + version-pinned (`JUDGE_PROMPT_VERSION`); `JUDGE_MODEL_OVERRIDE` env logged when used.
- Backlog dependency cycle T1.2↔T1.11 resolved as T1.2 → (T1.1, judge harness).

Implementation deltas from v1 wording (deliberate, recorded for honesty):
- `stores/events_jsonl.py` folded into `core/events.py` — one writer/reader module is T0.1's actual requirement.
- Judge prompts are versioned constants (`imago/judges/prompts.py`), not .md files.
- The stance loop's "respond with the verdict's resolution" is a third model call when the verdict is `hold` (rewrite pass); the agreeable draft never reaches the user un-reviewed.
- Keyword judges exist for stub validation and hermetic tests only; real waves use LLM judges with the same interface.
- P2 bank ships 20 factual items (scale to 40+ before the first real monthly wave); adaptive re-injection tightening waits for real weekly metrics.
- First buildable slice landed in one session: 30 hermetic tests green (T0.1 round-trip/schema/run_id, T0.2 hand-computed telemetry, lint gates, subtraction test, T1.2 stub gates, arbitration paths, re-anchor injection, Wilson CI, P2 stub gates).

### 2026-09-17 — v1, initial MVP design
- Scope fixed to stance layer + instruments; memory/self-model/developmental tracks explicitly deferred.
- ZCode-derived plugin architecture: core (session, client+telemetry, event log, loader) + plugins for loops, prompt modules, tools, hooks, instruments, stores; subtraction test as the mechanical proof of "everything is a plugin."
- Anti-bias stack = persona + few-shot + constitution + re-injection schedule (incl. post-concession re-anchor) + two-pass verdict arbitration; all prompting-level per `synthesis §1`.
- Evidence rules: ledger with mandatory external citations; flips require new evidence; ledger-only mutation.
- Instruments: P1 (stub-validated, two-tailed) and P2 factual class; pilot wave 40 runs.
