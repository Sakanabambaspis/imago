# Nightly tests — 2026-09-21

**Result: 36 passed, 0 failed, 0 skipped — 0.22s.** Second clean night in a row; nothing flaky, nothing broken.

## Run details
- Runner: **pytest** (from `[tool.pytest.ini_options]` in `pyproject.toml`), invoked as `.venv/bin/pytest tests/`.
- Full suite: still no `addopts`, no markers, no `skipif`s anywhere in `tests/` — the default run is the entire suite; all 11 files executed.
- Environment: pytest 9.1.1, Python 3.13.14 (project `.venv`), plugins: anyio only.
- No `nightly/config.md` exists — no overrides to honor.

## Failure triage
No failing tests, so no isolated re-runs and no flaky/broken classifications tonight.

## Flakiness table (last 7 nights)

| Test | Nights flaky (last 7) | Last result |
|------|----------------------|-------------|
| — (no entries yet) | | |

Two nights run, two nights fully green — no test has been flaky even once yet, so nothing to highlight. Table will flag any test flaky on 2+ of the last 7 nights.

## Coverage
No coverage tool is configured (no `pytest-cov`/`coverage` dependency in `pyproject.toml`; pytest's plugin banner shows anyio only) — no coverage number tonight and no trend.

## Changed since last night
- **Nothing changed.** Git shows no commits since 2026-09-20 21:00 and no modified tracked files.
- Same 36 tests, same pass/fail set as 2026-09-20; no tests added or removed.
- Suite runtime: 0.36s → 0.22s (noise-level variance on a 36-test suite).

---
*Report-only run: no project files modified, nothing committed, nothing pushed.*
