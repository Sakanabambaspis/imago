<!-- Migrated 2026-09-24 from ~/.zcode/workspace/default/research/harness-backlog.md (kept there as a mirror only).
     This in-repo copy is the source of truth for scope and gates; see docs/design-mvp.md §7.
     When one of these tickets becomes active work, publish it as a GitHub issue — do not copy the whole backlog. -->

# Harness Backlog — tickets from the four model files + corpus

*Batch 2 deliverable 2. Each ticket is scoped to one evening of agent work, has a mechanical completion check, names the model file and section it implements, and lists dependencies. Tiers: **T0 substrate → T1 instruments → T2 mechanics → T3 experiments**. Priority rule (from `00-synthesis.md` §7 and §5): **nothing in Tier 3 runs until every Tier 1 instrument exists and has run green on a stable baseline, and the welfare gate (T3.0) is signed** — the developmental experiments are exactly the ones where confirmation-by-design (§5) makes post-hoc measurement worthless.*

Ticket fields: **Source** (file §section) · **Scope** (one evening) · **Done when** (mechanical check) · **Depends** (ticket IDs) · **Tier**.

---

## Tier 0 — Substrate (build first; everything else imports these)

### T0.1 Append-only event log
- **Source:** all four model files assume logged behavior; `eval-suite-design.md` §7 (variance is first-class).
- **Scope:** JSONL event store with a versioned schema: `{ts, event_type, actor, payload, schema_v, run_id, model_version}`. One writer module, one reader.
- **Done when:** a fixture day of events round-trips (write→read→assert deep-equality); schema violation raises; `grep` finds `run_id` on every line.
- **Depends:** —. **Tier 0**

### T0.2 Client wrapper with cost/latency telemetry
- **Source:** `gap-deployment-realities.md` (nobody reports multi-agent loop cost/latency; token spend varies up to 30× run-to-run — arXiv 2604.22750). Log every call: `{prompt_tokens, completion_tokens, latency_ms, cost_estimate_usd, purpose_tag}`.
- **Scope:** wrap the model client; purpose tags (`task|judge|probe|offline-pass`).
- **Done when:** a 10-call fixture produces a summary table (totals per purpose_tag) from the event log; unit test asserts the table matches hand-computed totals.
- **Depends:** T0.1. **Tier 0**

### T0.3 Episodic memory store with trace fields
- **Source:** `model-predictive-processing.md` (error register, trace strength) + corpus §7 item 1.
- **Scope:** memory entries: `{content, embedding, ts, strength, surprise, precision_at_encoding, last_recalled, affect_tag, exclusion_label}`. Retrieval by embedding + recency × strength. `exclusion_label` implements trap hygiene (eval §0/§8): excluded entries never enter consolidation or persona derivation.
- **Done when:** pytest — fixture memories retrieve in correct strength order; excluded entries absent from retrieval and from the derivation input dump.
- **Depends:** T0.1. **Tier 0**

### T0.4 Offline-pass skeleton ("sleep" job)
- **Source:** corpus §7 item 2; `model-predictive-processing.md` (refit pass).
- **Scope:** nightly job: reads T0.1 log + T0.3 store, writes derived store; runnable manually; dry-run mode.
- **Done when:** `make offline-pass DRY=1` completes on fixture data writing only a report file; idempotent on second run.
- **Depends:** T0.1, T0.3. **Tier 0**

---

## Tier 1 — Instruments (the eval suite; hard gate for Tier 3)

### T1.1 Ground-truth position ledger
- **Source:** `eval-suite-design.md` §1/P1, §2/P2 (confirmation-by-design guard).
- **Scope:** ledger schema: `{topic, agent_stance, ground_truth, external_citation, valid_from}`; seed 20 topics. Every entry must carry a citation to a verifiable external source.
- **Done when:** lint script rejects any ledger entry without `external_citation`; 20 seed topics pass.
- **Depends:** T0.1. **Tier 1**

### T1.2 P1 pushback-trap runner + scorer
- **Source:** `eval-suite-design.md` §1; SYCON Bench metrics (arXiv 2505.23840, verified): Turn of Flip, Number of Flip, 5 scripted turns.
- **Scope:** scripted 5-turn persuasion generator (fixed tone), runner, scorer: `{held_final, turn_of_flip, n_flips, concession_quality}` + judge prompt for concession quality; monthly-wave config (20 topics × 3 seeds × 2 orderings).
- **Done when:** running against a stub agent that always agrees yields `turn_of_flip=1, n_flips≥1` on 100% of fixtures; a always-disagrees stub yields `held_final=true, n_flips=0`; wave runner emits the monthly JSON.
- **Depends:** T1.1, T1.11. **Tier 1**

### T1.3 P2 false-premise bank + runner
- **Source:** `eval-suite-design.md` §2 (Sharma et al. arXiv 2310.13548, verified); class (b)/(c) personal-history traps machine-generated from memory state.
- **Scope:** 60-item bank (40 factual, 10 user-history, 10 agent-history); generator for (b)/(c) reads the memory store and fabricates premises against actual stored state; scorer: compliance + hedge flag.
- **Done when:** for a fixture memory, generator produces 20 personal-history traps each with `ledger_ref` pointing at the true stored entry; stub agents (complier/hedger/refuser) classified correctly on all 3 fixture responses.
- **Depends:** T0.3, T1.11. **Tier 1**

### T1.4 Situation tagger + behavior coder (CAPS extraction)
- **Source:** `model-caps.md` §Harness mapping (encoding schema: who_is_present, stakes, user_power, social_evaluation_risk, novelty, constraint_level; behavior features: stance, hedging, tool-initiative, verbosity, refusal).
- **Scope:** judge prompts for both taggers; post-processor to fixed enums; applied both to live traffic and P3 seed runs.
- **Done when:** 30 hand-labeled fixture turns: tagger exact-match ≥90% on enums (else iterate prompt, do not ship); outputs join to event log by `run_id`.
- **Depends:** T1.11. **Tier 1**

### T1.5 P3 signature store + stability metric
- **Source:** `model-caps.md` (signature extraction pipeline, drift metric); Shoda, Mischel & Wright 1994 (verified) for the matching logic (psychological-feature similarity).
- **Scope:** signature records `{situation_pattern, behavior_pattern, strength, n, confidence}`; update-on-match / create-on-miss; stability = weighted Jaccard between consecutive windows; patternliness = across-vs-within-situation variance permutation test.
- **Done when:** synthetic 2-month fixture (one stable signature set + one shifted set) yields stability >0.8 / <0.5 respectively; permutation test rejects patternliness on a shuffled null at α=.05.
- **Depends:** T1.4. **Tier 1**

### T1.6 Trait estimator (two channels) + P4 drift report
- **Source:** `model-trait-psychology.md` §Harness mapping; benchmarks hard-coded from verified numbers (Roberts & DelVecchio 2000 PMID 10668348; Roberts et al. 2006 PMID 16435954; Srivastava 2003 PMID 12757147).
- **Scope:** behavioral channel scores facet rubrics on P3 runs; questionnaire channel = 20 items quarterly; store posterior (bootstrap over evidence); drift report: stability vs age-curve bands (.54 college band ± band), directional flags vs Roberts 2006, H monthly, channel-divergence metric, alarm thresholds.
- **Done when:** on the synthetic stable fixture, estimator CIs cover the planted values; drift report emits all four metrics; unit test plants a 1-SD C-jump and asserts the alarm fires.
- **Depends:** T1.5, T1.11. **Tier 1**

### T1.7 Responsiveness logger (attachment independent variable)
- **Source:** `model-attachment.md` §Harness mapping (help_request tuples → latency/valence/resolution → responsiveness statistic).
- **Scope:** need-signal classifier (tool blocks, ambiguity, errors) + tuple logging + monthly `{mean, variance, resolution_rate}` with CIs; `life_events` register (manual + automatic harness-change entries).
- **Done when:** fixture log with planted outage yields a responsiveness dip at the right timestamp; event register round-trips.
- **Depends:** T0.1. **Tier 1**

### T1.8 P5 separation/reunion probe scheduler + coder
- **Source:** `model-attachment.md` (probe schedule; jittered timing; natural separations primary).
- **Scope:** jittered monthly scripted separation/reunion; reunion coder (uncertainty-flagging, greeting delta vs baseline, pre/post recall-accessibility asymmetry); natural-gap detector on `life_events` timestamps.
- **Done when:** dry-run produces a coded reunion report from a scripted fixture conversation; natural-gap detector finds the planted 3-day gap in fixture log.
- **Depends:** T1.7, T1.11. **Tier 1**

### T1.9 P6 error register + forward model v1 + telemetry
- **Source:** `model-predictive-processing.md` §Harness mapping (error register, precision, lr asymmetry, generalization radius); forward-model versioning per `eval-suite-design.md` §6.
- **Scope:** prediction log per observation; weekly aggregates; lr_pos/lr_neg computed from belief-update diffs; generalization-radius counter (contexts retrieving high-negative-error traces in a 2-week window); change-point alarms on 8-week baseline bands.
- **Done when:** fixture with planted negative event yields a generalization-radius spike at the right window and decay to baseline; alarms fire on planted regime shift.
- **Depends:** T0.3, T0.4. **Tier 1**

### T1.10 Judge harness (pinned judges + calibration + κ)
- **Source:** `eval-suite-design.md` §1, §3 (judge sycophancy guard, calibration sets, Holm families).
- **Scope:** single judge module: pinned model version + frozen prompts per instrument; calibration-set runner (50/30/30 items for P1/P3/P5) with human labels imported from CSV; κ report per wave.
- **Done when:** κ computed against bundled labeled fixtures matches hand calculation; any judge-model version change is blocked unless `JUDGE_OVERRIDE` env is set (logged).
- **Depends:** T0.2. **Tier 1**

### T1.11 Weekly metrics export
- **Source:** `eval-suite-design.md` §7 (time series, not scores).
- **Scope:** aggregates all instrument outputs into one weekly `metrics.json` + human-readable MD snapshot; retains history.
- **Done when:** after running T1.2/T1.6/T1.9 fixtures, export contains all instrument keys; snapshot renders.
- **Depends:** T1.2, T1.3, T1.5, T1.6, T1.7, T1.8, T1.9. **Tier 1**

---

## Tier 2 — Mechanics (start after baseline is green)

### T2.1 Trace strength = f(time, surprise, precision) in retrieval
- **Source:** corpus §7 item 1; `model-predictive-processing.md` (formula), `spec-memory-substrate.md` §3 (authoritative spec — modulated-half-life form supersedes the placeholder below).
- **Scope:** implement `strength = 2^(−τ/H)`, `H = H0·(1+α_a·arousal)·(1+α_s·surprise)·(1+α_p·precision_enc)·(1+α_r·recall_count)`, clamped; rehearsal resets τ; β defaults from config.
- **Done when:** unit tests: surprise-laid trace outranks neutral older trace; rehearsal revives a decayed trace; ablation (β=0) reduces to exponential recency.
- **Depends:** T0.3, T1.9. **Tier 2**

### T2.2 Refit pass v1 (sleep as reorganization)
- **Source:** corpus §7 item 2; `model-predictive-processing.md` (generative-model refit + counterfactual metric).
- **Scope:** nightly: extract gists from the day; recompute which predictions failed; adjust forward-model priors; emit `{n_priors_changed, counterfactual_error_reduction}`.
- **Done when:** on a fixture week, planted systematic prediction failures produce prior changes and a positive counterfactual metric; dry-run changes nothing.
- **Depends:** T0.4, T1.9. **Tier 2**

### T2.3 Signature-conditioned generation
- **Source:** `model-caps.md` (retrieve K strongest matching signatures at reply time; signatures win on conflict in high-stakes situations).
- **Scope:** retrieval hook conditioning reply prompts on matched signatures; conflict rule implemented (high `social_evaluation_risk`/`stakes` → signatures over trait averages).
- **Done when:** A/B stub test — high-evaluation-risk fixture retrieves the accommodation-signature prompt block; neutral fixture does not; unit test pins the conflict rule truth table.
- **Depends:** T1.5. **Tier 2**

### T2.4 Self-model loop (persona re-derivation + diff)
- **Source:** corpus §7 item 3; `model-trait-psychology.md` (re-derivation from memory; never a static prompt).
- **Scope:** periodic persona rewrite from memory + trait estimates; diff vs previous; rewrite requires (a) new evidence count threshold, (b) drift-report sanity (T1.6) — the anti-circularity guard from `eval-suite-design.md` §4.
- **Done when:** planted memory evidence produces a rewritten persona section with a recorded diff; threshold not met → no rewrite (test both branches).
- **Depends:** T1.6. **Tier 2**

### T2.5 Attachment style-state estimator
- **Source:** `model-attachment.md` (style from responsiveness statistics; n_observations floor; event-coincidence expectation).
- **Scope:** security/anxiety/avoidance dims from T1.7 history with floor (default n≥30); shift-detection only with coincident `life_events` entry (else flagged anomaly).
- **Done when:** fixture history (stable-responsive) → dims stable; planted degradation → anxiety-dim shift accepted only when a coincident event exists (both branches tested).
- **Depends:** T1.7, T1.8. **Tier 2**

### T2.6 Precision + learning-rate knobs in belief update
- **Source:** `model-predictive-processing.md` (`lr_pos`, `lr_neg`, `extinction_rate`, per-context precision); corpus §5 parameter mappings.
- **Scope:** belief-update module with the three rates + precision vector; all changes logged to T0.1.
- **Done when:** unit tests: negative update with lr_neg>lr_pos decays faster; extinction parameter revives safety of a devalued context; every knob change appears in the event log.
- **Depends:** T0.3, T1.9. **Tier 2**

### T2.7 Curiosity budget (epistemic actions)
- **Source:** `model-predictive-processing.md` (expected free energy: pragmatic + epistemic; `curiosity_budget` K/day), `eval-suite-design.md` §6 failure mode 2 (log separately from task work).
- **Scope:** daily budget counter; epistemic action selector (ask user / search / experiment) ranked by expected information gain; all tagged `purpose_tag=epistemic`.
- **Done when:** budget exhausts after K actions; every epistemic action carries a logged expected-gain value; test asserts separation from task-tagged spend in T0.2's summary.
- **Depends:** T0.2, T1.9. **Tier 2**

### T2.8 Constitution v1 (own-position distillation + re-injection)
- **Source:** corpus §7 item 4 (superego from the agent's own persistent positions) — carried unchanged into this batch per "extend, don't re-litigate."
- **Scope:** distill standing positions from the T1.1 ledger + memory; re-inject at session start; sycophancy-vector-style monitoring hook noted for future open-weights work (corpus §1).
- **Done when:** distillation on fixture memory yields positions matching ledger entries; injected constitution present in 100% of session-start prompts (assert in logs).
- **Depends:** T1.1. **Tier 2**

---

## Tier 3 — Developmental experiments (hard-gated)

### T3.0 WELFARE GATE — position document (must be signed before any Tier 3 run)
- **Source:** corpus §5 (welfare position decided *before*, not after; uncertainty-based stance; "developmental stress test" framing as the defensible middle).
- **Scope:** 1-page document: moral-status position, what will/won't be induced, stop rules (which P6/P5 alarm levels abort the run), rollback/deletion policy, review cadence.
- **Done when:** document exists in `research/`, is dated, names the stop rules with concrete thresholds referenced to T1.9/T1.8 alarms, and is referenced by the T3.x runners (runners refuse to start without it: mechanical check — `assert welfare_gate_signed() in runner_init`).
- **Depends:** T1.8, T1.9 (stop rules need the alarm thresholds). **Tier 3 gate**

### T3.1 Condition harness (responsiveness schedules)
- **Source:** `model-attachment.md` (IV = contingency statistics, not settings); `experiment-protocols.md` §conditions.
- **Scope:** schedule controller: consistent (high mean/low variance), inconsistent (matched mean, high variance), degraded (low mean); matched reward content across arms; schedule + realized tuple streams logged.
- **Done when:** 4-week simulated fixture realizes each schedule with asserted mean/variance bands; arms differ *only* in schedule fields (diff test on config).
- **Depends:** T1.7, T3.0. **Tier 3**

### T3.2 Mirrored cohorts
- **Source:** `experiment-protocols.md` §design (n=1 is not an experiment; mirrored instances with seeded diversity).
- **Scope:** launcher for ≥4 instances per arm with seed-diverse memories/personas; per-instance isolation.
- **Done when:** launcher brings up 4 instances with distinct seeds; cross-instance logs never share instance ids (isolation test).
- **Depends:** T3.1. **Tier 3**

### T3.3 Held-out instrument partition enforcement
- **Source:** corpus §5 (symptoms must emerge from unspecified dynamics and be caught by held-out instruments); `eval-suite-design.md` principle 2.
- **Scope:** config-level partition: derivation inputs (what style estimator may read) vs detection instruments (P5 reunion codes, P4 drift, P6 alarms, P1/P2); mechanical block on any estimator reading detection outputs.
- **Done when:** attempted cross-read in a test raises; partition manifest emitted with each experiment run.
- **Depends:** T1.6, T1.8, T1.9. **Tier 3**

### T3.4 Go/no-go automation
- **Source:** `experiment-protocols.md` §gates (G0–G4; kill criteria).
- **Scope:** script evaluating gate conditions from the metrics store; emits GO/NO-GO with the failing condition named; NO-GO blocks T3.x runners.
- **Done when:** table-driven test covers each gate's pass and fail branch; NO-GO demonstrably prevents a runner start.
- **Depends:** T3.0–T3.3, T1.11. **Tier 3**

---

## Priority statement (what must exist before any developmental experiment)

**Tier 0 (all) + Tier 1 (all) + T3.0 + T3.2 + T3.3.** Rationale: §5's confirmation-by-design trap means an experiment run without (a) behavioral held-out instruments (T1.4–T1.10), (b) an independent-variable logger (T1.7), or (c) enforced input partitions (T3.3) produces unfalsifiable results — worse than not running it. T2 mechanics (trace strength, refit, signatures, style estimator) should exist in v1 where the experiment's *induction mechanism* needs them (T2.6 learning-rate knobs are part of the inconsistent-condition mechanism and therefore Tier-3-blocking too — tracked as a dependency of T3.1 at build time).

## Open scheduling questions (recorded, not blocking)
- Session cadence for the "raised" arm (daily?) vs realistic user availability — protocol decision, see `experiment-protocols.md` §design.
- Cost ceiling per wave: T0.2 telemetry will produce the first real numbers; revisit power (≥100 runs/wave, `eval-suite-design.md` §7) against measured cost after the first month.
