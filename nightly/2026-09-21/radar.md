# Codebase radar — 2026-09-21

Nightly trend report for Imago. Repo HEAD at scan time: `7c1a380` (2026-09-19, "Per-provider env vars + Groq config profile"). **First night — this report is the baseline.** Per-metric history starts here; comparisons and "growing debt" flags begin once 3+ nights exist. No `nightly/config.md` overrides present; defaults used.

## Changed since last night

Nothing to compare against — no previous radar.md exists (archive is empty). All four metrics below are initial readings.

## 1. Ten largest source files (Python, lines)

| # | File | Lines |
|---|------|------:|
| 1 | imago/plugins/instruments/p1_pushback.py | 213 |
| 2 | imago/core/adapters.py | 204 |
| 3 | imago/core/config.py | 195 |
| 4 | imago/core/cli.py | 168 |
| 5 | imago/core/ledger.py | 145 |
| 6 | imago/plugins/instruments/p2_false_premise.py | 121 |
| 7 | tests/test_stance_loop.py | 107 |
| 8 | imago/core/session.py | 99 |
| 9 | imago/judges/llm.py | 98 |
| 10 | imago/judges/prompts.py | 80 |

Context: 42 `.py` files, 2,597 lines total. Healthy spread — largest file is 213 lines (8% of codebase).

## 2. Most-changed files, last 90 days

7 commits total in window (2026-06-23 → 2026-09-21; repo imported 2026-09-17).

| # | File | Commits touching it |
|---|------|--------------------:|
| 1 | config.toml | 4 |
| 2 | README.md | 4 |
| 3 | tests/test_adapters.py | 3 |
| 3 | imago/core/config.py | 3 |
| 3 | imago/core/adapters.py | 3 |
| 6 | imago/core/cli.py | 2 |
| 6 | docs/adr/0005-api-keys-env-only.md | 2 |
| 6 | .gitignore | 2 |
| 6 | .env.example | 2 |

(8 further files changed once; cut off.) Pattern: churn concentrates in **config + adapters** — matches the recent commit run (8e7c425, 1118dcc, f9e1c9f, 7c1a380 all touch provider/config wiring). Nothing alarming at 7 commits' scale.

## 3. Duplication scan (repeated blocks of 6+ lines)

Scanned all 42 `.py` files; 2,067 distinct 6-line blocks, **13 duplicated windows in 2 clusters**, rest clean.

- **Cluster A — `imago/core/adapters.py` (in-file, ~10 lines × 2).** `OpenAICompatibleClient.complete()` and `AnthropicClient.complete()` each build their own HTTP `request` dict plus an identical `send()` closure (httpx client, 200-check, `RuntimeError` with `response.text[:300]`). The provider-specific parts legitimately differ (tools wire format, auth headers); the send/error scaffolding is exact. Likely fix when it next grows: hoist `send()`/error handling into `_BaseClient`.
- **Cluster B — `_write_wave()` copied verbatim across plugins (cross-file, ~10 lines).** Identical function defined in `imago/plugins/instruments/p1_pushback.py:204` and `imago/plugins/instruments/p2_false_premise.py:112` (mkdir, wave JSON write, `wave_report` log event). Textbook candidate for a shared `imago/plugins/instruments/_common.py` before a third instrument copies it.

Neither cluster is new debt introduced by a specific recent commit — both date from the MVP import (d28471a); noted as starting conditions, not regressions.

## 4. Dependency counts

| Metric | Value |
|--------|------:|
| Runtime dependencies | 1 (`httpx>=0.27`) |
| Optional dependencies | 0 |
| Dependency groups | 0 |
| Lockfile | none |
| Python floor | >=3.12 |
| Tool config | pytest only |

Minimal by design; nothing to trend yet.

## Running per-metric history

| Night | Largest file (lines) | Total .py lines | Dup windows | Runtime deps | Debt flags |
|-------|---------------------:|----------------:|------------:|-------------:|-----------:|
| 2026-09-21 | p1_pushback.py 213 | 2,597 | 13 (2 clusters) | 1 | — (baseline) |

Growing-debt rule (from tomorrow): any metric worse 3+ nights in a row gets flagged with a one-line cause correlated against recent commits.
