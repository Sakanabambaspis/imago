# Nightly tests — 2026-09-20

**Result: 36 passed, 0 failed, 0 skipped — 0.36s.** Nothing flaky, nothing broken, no test authoring needed.

## Run details
- Runner: **pytest** (detected from `[tool.pytest.ini_options]` in `pyproject.toml`), invoked as `.venv/bin/pytest tests/`.
- Full suite: pyproject defines no `addopts` and the tests contain no markers or `skipif`s, so there is no day-time exclusion to undo — the default run **is** the entire suite. All 11 files under `tests/` executed.
- Environment: pytest 9.1.1, Python 3.13.14 (project `.venv`), plugins: anyio only.
- No `nightly/config.md` exists — no overrides to honor.

## Failure triage
No failing tests, so no isolated re-runs and no flaky/broken classifications tonight.

## Flakiness table (last 7 nights)

| Test | Nights flaky (last 7) | Last result |
|------|----------------------|-------------|
| — (no entries yet) | | |

First night this task ran: no previous `tests.md` exists under `nightly/` (only tonight's folder; `archive/` is empty), so the table starts empty. All 36 tests passed tonight; any test that fails-then-passes on retry in future nights will be added here, and 2+ flaky nights out of 7 will be highlighted.

## Coverage
No coverage tool is configured (`pytest-cov`/`coverage` absent from `pyproject.toml` dependencies and from installed plugins), so no coverage number was collected and no trend started.

## Changed since last night
First night — no baseline report to diff against. Next night's report should compare: pass/fail set, new/removed tests, and the flakiness table.

---
*Report-only run: no project files modified, nothing committed, nothing pushed.*
