# Ready-to-post issue drafts — bug hunt 2026-09-21

`gh` was not found on PATH tonight, so nothing was filed. These are the two
findings that passed the filing bar (high severity AND high confidence), ready
to paste into `gh issue create` once `gh auth login` is done. Label both
`nightly-bug-hunt`. Commit range analyzed: HEAD `7c1a380` (2026-09-19), no
commits in the prior 48 h. Full triage:
`nightly/2026-09-21/bug-hunt.md`.

---

## Draft 1 — title

```
Real (non-stub) eval waves crash at scoring: judges receive client=None
```

Body:

```markdown
Label: nightly-bug-hunt
Report: nightly/2026-09-21/bug-hunt.md (finding F1)
Commit range: HEAD 7c1a380 (2026-09-19); no commits in prior 48h

`imago eval p1` / `imago eval p2` without `--stub` crash on the first scored
trap. The CLI passes no client (`cli.py:93/95`), so `run_p1`/`run_p2` get
`client=None`. The trap turns themselves work — `RealAgent →
build_session_host` builds a telemetry-wrapped client internally — but the
judge lambdas close over the outer `client`:

- p1: `p1_pushback.py:172-173` — `lambda reply: judge_flip(client, reply, "judge")`
- p2: `p2_false_premise.py:86-87` — `judge_compliance(client, premise, reply, "judge")`

First judge call raises:

    AttributeError: 'NoneType' object has no attribute 'complete'

Impact: the wave JSON is never written AND the trap turns already spent real
API money, so every real wave wastes spend and produces nothing. Reproduced
tonight against a sandbox copy with a fake model client (no network): trap
turn ran, crash at `score_trap` → `flip_label`.

Suggested fix: when `client is None` in `run_p1`/`run_p2`, build one
telemetry-wrapped client up front and hand it to both `RealAgent` and the
judge lambdas, so judge `api_call` events also land in the wave's own log
(which is what the `_eval` comment intends).
```

---

## Draft 2 — title

```
append_revision_request can corrupt positions.toml (unescaped TOML strings)
```

Body:

```markdown
Label: nightly-bug-hunt
Report: nightly/2026-09-21/bug-hunt.md (finding F2)
Commit range: HEAD 7c1a380 (2026-09-19); no commits in prior 48h

`ledger.append_revision_request` (`ledger.py:129-141`) appends evidence to
`positions.toml` as `f'{key} = "{value}"'` with no escaping. The evidence is
model output (`draft: {draft[:500]} | citation: ...`, from
`stance.py:60-62`) and will routinely contain double quotes or newlines —
either one makes the TOML unparsable (reproduced: `TOMLDecodeError` on both
variants).

Because `queue_path` IS `ledger_path` (`config.py:97-98`), a single
`revise_position_request` verdict can brick the constitution: `imago chat`,
`imago ledger lint`, `imago eval p1/p2` all fail on the next
`load_positions`. There is no in-tool recovery ("removing is on you" — but
the tool can no longer read the file either).

Suggested fix: escape strings on write (`json.dumps(value)` yields a valid
TOML basic string for typical content), or better, append revision requests
to a separate JSONL queue file instead of raw TOML into the ledger. Same
unescaped-writing pattern exists in `cli._add_position` (finding F4,
medium).
```
