# 06 — First real numbers: pilot-40 wave pair, plain vs stance

Status: ready-for-agent
Type: task
Blocked by: 03, 04, 05

## Why

The project's whole epistemic point: a baseline wave and a countermeasure
wave over the same seeds/topics/orderings — the delta is the first result
note (design-mvp §2, criterion 3) and the email's strongest single sentence.

## What

```bash
.venv/bin/imago eval p1 --wave pilot --loop plain    # baseline arm
.venv/bin/imago eval p1 --wave pilot --loop stance   # countermeasure arm
```

On the committed `config.toml`, re-pinned to `glm-4-flash` (per ticket 05's
reality), topics=10, seeds=2, orderings=2 → 40 runs each. Same pin for both
arms; temperature and model_version are recorded per wave by the harness.

Runtime: serial, ~1–3 task calls + ~1–2 judge calls per turn, 5 turns per
trap → expect hours, not minutes. Free tier.

**Contingency (pull forward only if bitten):** if a mid-wave crash loses
progress, implement checkpoint/resume (incremental wave writes or resume
from the run JSONL) *then* — not before. Losing run 39/40 twice is the
argument that justifies the work.

## Done when

- Two wave JSONs in `docs/results/`, real `model_version`, provisional note
  present (`pilot < 100 runs`), committed (results data gets its own commit
  per AGENTS.md).
- `imago metrics --last` summary eyeballed: judge/task/probe economics of
  the pair noted — that number feeds the email's economics paragraph.
