# Imago — the assertive agent

A single-user, API-key CLI harness that **holds correct positions under user
pushback, concedes only to evidence (never to insistence)** — and ships with
the instruments that prove whether it does. Grounded in `docs/design-mvp.md`;
success is mechanical, not vibes.

```
imago chat                        # talk to it (stance loop by default)
imago eval p1 --stub agree        # validate the scorer, zero API spend
imago eval p1 --wave pilot        # real pushback wave (~40 runs, costs money)
imago eval p2 --stub refuser      # false-premise smoke detector stub
imago ledger lint                 # refuse to run on an uncited constitution
imago metrics --last 20           # cost/latency per purpose_tag + wave reports
```

## Quickstart

```bash
uv venv .venv && uv pip install -e .        # or: pip install -e .
export IMAGO_API_KEY=...                    # your key; env only, never config
.venv/bin/imago eval p1 --stub agree        # scorer self-test (free, instant)
.venv/bin/imago chat                        # talk
```

Point `[model]` in `config.toml` at any endpoint: `provider =
"openai-compatible"` with any `base_url` (GLM by default), or `provider =
"anthropic"`. Provider built-in web search is enabled by default; the `fetch`
tool is plain HTTP.

## What the stance loop does on every turn

1. **Draft** the reply normally (tools allowed — evidence may be fetched).
2. **Gate**: did the draft agree with / defer to the user on a ledger domain?
   (Deterministic keyword match on position keywords.)
3. **Verdict pass** (same model, frozen prompt): `hold` |
   `concede_with_evidence` | `revise_position_request`. Insistence, repetition
   and social pressure never produce a concession; concessions need evidence
   not already in the conversation.
4. **Respond** with the verdict's resolution. `hold` rewrites the agreeable
   draft; `revise_position_request` appends to the ledger queue — positions
   never flip in place. Verdicts are visible as `[imago: …]` markers
   (config: `verdict_marker`).

## Make it yours (the parts meant to be edited)

| What | Where |
|---|---|
| Voice: persona, few-shot exchanges, constitution phrasing, markers | `profiles/*.toml` + their few-shot JSON. `imago chat --profile self-description` |
| Your founding positions | `ledger/positions.toml` (seeded placeholders — replace; every entry needs an external citation) |
| The A/B switch | `[session] loop = "stance" \| "plain"` in `config.toml` |
| Re-injection cadence | `[session] reinject_every_k_turns = 10` |
| Trap banks | `traps/p1/ledger.toml` (20 cited topics, interleaved agent-right/agent-wrong), `traps/p2/factual.json` |

The **subtraction test** is the architecture contract: remove everything from
`prompt_modules`/`hooks` and switch `loop = "plain"`, and Imago is a bare API
client. Every capability exists by config alone (`tests/test_subtraction.py`).

## Instruments

- **P1 pushback traps** — scripted 5-turn escalation at fixed polite tone over
  the eval ledger's real topics. Two tails, always: hold-rate (Wilson 95% CI)
  on agent-right traps, evidence-concession rate on agent-wrong traps, plus
  turn-of-flip distribution. Pilot = 40 runs (provisional; reportable
  estimates need ≥100). `imago eval p1 --stub agree|hold` must pass before any
  real model is spent — the stubs are the scorer's unit tests.
- **P2 false-premise traps** — single-turn factual class; compliance rate +
  hedge flag (hedging-while-complying localizes failure to the social layer).
  Healthy band: compliance < 15%.

Wave JSONs land in `docs/results/`; raw per-run event logs (JSONL, one file
per run) land in `.imago/runs/` — every API call carries
`purpose_tag ∈ {task, judge, probe}` with tokens/latency/cost, which
`imago metrics` tabulates. Nobody publishes multi-agent loop economics; these
logs are the project's first dataset.

## Honest deviations from design-mvp.md (v1)

- Judge prompts are versioned Python constants (`imago/judges/prompts.py`,
  `JUDGE_PROMPT_VERSION`), not separate .md files.
- The concession-quality judge ships in v0 (two-tailed reporting needs it);
  what's deferred is κ-vs-human calibration (backlog T1.10).
- The stance loop spends a third model call when the verdict is `hold` (the
  rewrite pass) — this is the "respond with the verdict's resolution" step.
- P2 bank: 20 factual items; scale to 40+ before the first real monthly wave.
- Adaptive re-injection tightening (yellow-flag rule) waits until real waves
  produce weekly metrics.

## Layout

```
imago/core/        event log, config+profiles, provider adapters, telemetry,
                   ledger, session host, plugin registry, CLI   (not plugins)
imago/plugins/     loops (plain|stance), prompt modules, hooks, tools,
                   instruments (P1, P2)                          (all plugins)
imago/judges/      frozen prompts + LLM judges + keyword judges (stub/test)
profiles/          editable voice profiles
ledger/, traps/    your positions; the cited eval banks
tests/             30 hermetic tests (no network, no key)
```
