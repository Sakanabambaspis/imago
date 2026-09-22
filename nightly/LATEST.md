# LATEST — nightly reports for Imago

- **2026-09-22** — [worker.md](2026-09-22/worker.md) — night queue empty for the second night: no items in `nightly/queue/`, no open topics in `topics.md`; worker stood down.
- **2026-09-21** — [bug-hunt.md](2026-09-21/bug-hunt.md) — first full-codebase bug hunt: 12 findings; top 2 (high/high): real eval waves crash at scoring (`client=None` judges), and revision-request appends can corrupt `positions.toml`. gh missing → drafts in [bug-hunt-drafts.md](2026-09-21/bug-hunt-drafts.md).
- **2026-09-21** — [radar.md](2026-09-21/radar.md) — first radar night (baseline): largest file 213 lines, 13 dup windows in 2 clusters (`adapters.py` send() boilerplate, verbatim `_write_wave()` in both instruments), 1 runtime dep; no comparisons yet.
- **2026-09-21** — [tests.md](2026-09-21/tests.md) — 36/36 passed in 0.22s, second clean night; no flakes, nothing changed since last night.
- **2026-09-21** — [worker.md](2026-09-21/worker.md) — night queue empty: no items in `nightly/queue/`, no open topics in `topics.md`; worker stood down.
- **2026-09-20** — [tests.md](2026-09-20/tests.md) — 36/36 passed in 0.36s, no flakes; flakiness table started (first night).
- **2026-09-20** — [hygiene.md](2026-09-20/hygiene.md) — all checks pass, 384 KB caches freed, entry point imports OK.
