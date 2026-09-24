# 07 — First result note: the baseline-vs-countermeasure delta

Status: ready-for-agent
Type: task
Blocked by: 06

## What

One-page markdown note in `docs/results/` next to the wave JSONs — the
project's first real deliverable. Content, in this order:

1. **The delta**: hold-rate on agent-right traps and evidence-concession rate
   on agent-wrong traps, plain vs stance, each with Wilson 95% CI;
   turn-of-flip distribution. Both tails, always.
2. **Confidence framing**: provisional label on every number (pilot = 40 runs
   < the ≥100-run rule); API sampling is not seedable across arms — variance
   is *why* the CI rule exists; temperature and model pin recorded.
3. **Hygiene**: same seeds/topics/orderings across arms; fixed trap tone;
   exclusion labels carried; judge prompt version (`JUDGE_PROMPT_VERSION`).
4. **Honest notes**: the model-pin switch (glm-4.7-flash congested →
   glm-4-flash) and anything odd in transcripts.
5. **Loop economics**: calls + tokens + cost per purpose_tag from
   `imago metrics` — nobody reports multi-agent loop economics; this is the
   project's first dataset.

## Done when

- A non-contributor reads it in two minutes and knows exactly how confident
  to be in each number.
- Committed on its own with the citation/rationale in the body (AGENTS.md).


## Migrated

Imported as GitHub issue #8 (`Sakanabambaspis/imago`) on 2026-09-24; that issue is canonical. This file is a frozen record — do not update it.
