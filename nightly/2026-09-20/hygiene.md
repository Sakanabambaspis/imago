# Nightly hygiene — 2026-09-20

**Result: all checks pass, nothing failing.** 384 KB of caches freed; no stale links, no archive rotation needed, working tree clean apart from the untracked `nightly/` folder itself.

## (5) Build / entry-point spot-check — PASS
- `ast.parse`d all **42** project `.py` files (excluding `.venv/` and `nightly/`): **0 syntax failures**.
- CLI entry point `imago.core.cli:main` imports under `.venv/bin/python` with `PYTHONDONTWRITEBYTECODE=1`; `main` is callable.
- Nothing suddenly fails, so no urgent findings this morning.

## (1) Archive rotation — nothing to do
- No dated report folders exist under `nightly/` yet (the other night tasks were registered yesterday and their first runs start tonight), so there was nothing older than 30 days to move.
- `nightly/archive/` is empty — nothing older than 90 days to delete.

## (2) LATEST.md link check — created fresh
- `nightly/LATEST.md` **did not exist** (no prior night had produced reports). No stale links to fix; this run created it, pointing at tonight's `hygiene.md`.

## (3) Gitignored cleanup — 384 KB freed
Deleted (regenerable caches only):
- `.pytest_cache/` — 32 KB
- 10 × `__pycache__/` under `imago/` and `tests/` — 352 KB

Deliberately left alone despite being gitignored — not build artifacts or caches:
- `.env` / `.env.*` — secrets
- `.venv/` — Python environment (would force a full reinstall)
- `.imago/` — application runtime data

No `dist/` or `*.egg-info/` present.

## (4) Uncommitted changes & stashes — reported, untouched
- Branch: `main`; **no stashes**.
- Uncommitted: `?? nightly/` (the whole nightly folder is untracked, as designed).
- Observation: `nightly/topics.md` contains an empty unchecked bullet (`- [ ]`) — the night-shift worker may pick it up as a topic; worth filling in or removing.

*No tracked project files were modified, moved, or deleted; nothing committed or pushed.*
