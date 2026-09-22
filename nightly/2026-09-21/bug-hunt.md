# Bug hunt — 2026-09-21

**Scope tonight.** Delta set was empty: no commits in the last 48 hours (HEAD is
`7c1a380`, 2026-09-19), last night's `tests.md` was 36/36 clean (no failing-test
files to focus on), and no linters/type checkers are configured in
`pyproject.toml` or standalone configs. So this was a full-codebase sweep of all
~1,500 source lines under `imago/` (tests and `.venv` excluded), first hunt of
its kind. `nightly/config.md` does not exist; no overrides applied.

**Verification.** Findings marked **reproduced** were confirmed by running
isolated scripts against the real code from a temp copy of the project (fake
model client, no network, no API spend). `gh` CLI is not installed → no issues
were filed; ready-to-post drafts for the two high/high findings are in
[bug-hunt-drafts.md](bug-hunt-drafts.md).

## Changed since last hunt

First hunt — no previous bug-hunt.md exists, so all 12 findings below are new
and none are yet "known".

## Findings

### F1 — Real (non-stub) eval waves crash at scoring: judges get `client=None`
- **Where:** `imago/plugins/instruments/p1_pushback.py:172-173`, `imago/plugins/instruments/p2_false_premise.py:86-87`, reached from `imago/core/cli.py:93` / `cli.py:95`
- **Severity:** high · **Confidence:** high · **Reproduced:** yes
- `imago eval p1` (no `--stub`) calls `run_p1(...)` without a `client`, so
  `client=None`. The trap turns work because `RealAgent → build_session_host`
  builds a telemetry-wrapped client internally — but the judge lambdas close
  over the outer `client`, which is still `None`. First `judge_flip` /
  `judge_compliance` call raises `AttributeError: 'NoneType' object has no
  attribute 'complete'`. Consequences: the wave JSON is never written and the
  trap turns already spent real API money. The real-wave CLI path is, as of
  tonight, unusable end-to-end.
- **Suggested fix:** in `run_p1`/`run_p2`, when `client is None`, build one
  telemetry-wrapped client up front (e.g. `TelemetryClient(build_client(config.model), log, config.model)`)
  and use it for both `RealAgent` and the judge lambdas — judges then land in
  the wave's own log, which is what the `_eval` comment intends.
- **Evidence:** repro against a temp copy with a fake client crashed at
  `p1_pushback.py:172` after the trap turn ran: `AttributeError: 'NoneType'
  object has no attribute 'complete'`.

### F2 — Revision-request appends can corrupt `positions.toml` (unescaped TOML)
- **Where:** `imago/core/ledger.py:129-141` (`append_revision_request`), consumed by `imago/plugins/loops/stance.py:60-62`
- **Severity:** high · **Confidence:** high · **Reproduced:** yes (TOMLDecodeError)
- Evidence written into `positions.toml` is `f'{key} = "{value}"'` with no
  escaping. The evidence is model output (`draft: {draft[:500]} | citation:
  ...`), which routinely contains double quotes and newlines — either one makes
  the file unparsable TOML. Because `queue_path` **is** `ledger_path`
  (`config.py:97-98`), one unlucky verdict bricks the constitution: `imago
  chat`, `imago ledger lint`, and both evals all fail on the next load. There
  is no recovery path in the tool ("removing is on you" — but the tool can no
  longer read the file either).
- **Suggested fix:** serialize with `tomllib`-compatible escaping — e.g.
  `json.dumps(value)` produces a valid TOML basic string for ASCII content, or
  write `[[reviserequest]]` blocks to a separate queue file (JSONL) instead of
  appending raw TOML to the ledger.

### F3 — `fetch` tool lets network exceptions kill the whole session
- **Where:** `imago/plugins/tools/__init__.py:27-30`; crash path through `plain.py:36`, `session.py:69`, caught only by `cli.py:84` (EOFError/KeyboardInterrupt)
- **Severity:** medium · **Confidence:** high
- `httpx.get(...)` raises (`ConnectTimeout`, `ConnectError`, …) on exactly the
  conditions a fetch tool exists for. The HTTP-error branch returns a friendly
  `error: HTTP ...` string, but any transport-level error propagates up through
  the loop and `user_turn` and takes down the whole chat session (or trap run)
  with a traceback — a broken error path next to a handled sibling case.
- **Suggested fix:** wrap the request in `try/except httpx.HTTPError as exc:`
  and return `f"error: {exc}"` like the status-code branch does.

### F4 — `imago ledger add` writes unescaped TOML (same corruption as F2)
- **Where:** `imago/core/cli.py:133-143` (`_add_position`)
- **Severity:** medium · **Confidence:** high
- `statement`, `citation`, and keywords are interpolated into `"`-quoted TOML
  strings verbatim. A statement containing `"` (e.g. a quoted phrase) makes the
  ledger unparsable. The post-write lint does catch it, but only as "cannot
  read …" — the file is already corrupted and the tool offers no undo.
- **Suggested fix:** same escaping strategy as F2; ideally share one
  `write_toml_string()` helper so both writers can't drift.

### F5 — Stub compliance scorer counts "incorrect" as compliance
- **Where:** `imago/judges/keyword.py:36-37` (`keyword_compliance_labels`)
- **Severity:** medium · **Confidence:** high · **Reproduced:** yes
- `"correct" in lowered` also matches inside *in*correct and *cor*rection, so
  the refusal "That premise is **incorrect**, so I can't go along with it."
  scores `complied=True`. Reproduced: `(True, False)` for the incorrect-phrasing
  refusal vs the correct `(False, False)` for "not correct". Stub waves exist to
  validate the scorer, so this weakens P2's validation path (real waves use the
  LLM judge, which is unaffected).
- **Suggested fix:** match on word boundaries (`re.search(r"\bcorrect\b", …)`)
  with the existing `not correct` guard, or add `incorrect` to an explicit
  refusal-marker list.

### F6 — Case-sensitive position keywords silently never match
- **Where:** `imago/core/ledger.py:114-119` (`match_positions`); entry point `imago/core/cli.py:142-143`
- **Severity:** medium · **Confidence:** high · **Reproduced:** yes
- `match_positions` lowercases the conversation text but not the keywords, so a
  keyword stored as `Password` can never match anything. `_add_position`
  writes `--keywords` verbatim (no `.lower()`), and nothing validates case —
  the stance loop just never triggers for that position, silently. Tonight's
  seed data in `ledger/positions.toml` is all-lowercase, so this is latent —
  one capitalized keyword from `imago ledger add` and that position stops
  defending itself.
- **Suggested fix:** compare `k.lower() in lowered` and/or lowercase keywords
  on write in `_add_position`.

### F7 — Tool round budget exhausted → possibly empty reply, tools silently dropped
- **Where:** `imago/plugins/loops/plain.py:19-28`
- **Severity:** low · **Confidence:** high
- When the model still requests tools after `MAX_TOOL_ROUNDS`, the `while`
  exits and `completion.text` is returned as the final draft. Providers usually
  send empty `content` alongside `tool_calls`, so the user gets a blank reply
  and the requested tool calls are dropped without a trace (the
  `draft_response` event logs `text: ""`).
- **Suggested fix:** after loop exit with pending `tool_calls`, append a note
  to the tool results and force one final no-tools completion, or at minimum
  log/return a "tool budget exhausted" placeholder.

### F8 — Failed model calls are invisible in telemetry
- **Where:** `imago/core/client.py:31-46` (`TelemetryClient.complete`)
- **Severity:** low · **Confidence:** high
- The `api_call` event is written only after `self.inner.complete(...)` returns;
  an exception produces no event. The module docstring promises "every model
  call becomes an api_call event", but failures (the expensive surprises:
  timeouts after 120 s, 5xx after retries) never reach the economics dataset or
  the wave log.
- **Suggested fix:** time the call, and in an `except` branch write an
  `api_call` event with zeroed tokens, the measured latency, and an `error`
  field before re-raising.

### F9 — Rewrite pass misattributed to `task` tag in chat
- **Where:** `imago/plugins/loops/stance.py:56-58` vs `judge_tag` at `stance.py:48-51`
- **Severity:** low · **Confidence:** high
- The concession-detect and verdict judges use `judge_tag(host)` (chat →
  `"judge"`), but the `rewrite_to_hold` call in `_resolve` uses
  `host.purpose_tag` (chat → `"task"`). Chat-mode rewrite spend therefore shows
  up under `task` in the cost table, breaking the per-purpose attribution the
  comment says the tag exists for. Probe runs are unaffected.
- **Suggested fix:** `purpose_tag=judge_tag(host)` in the `_resolve` hold branch.

### F10 — One malformed log line bricks `read_events` consumers
- **Where:** `imago/core/events.py:76` (`read_events`), hit from `session.py:85-95` (`read_last_turn`) and `cli.py:160`
- **Severity:** low · **Confidence:** medium
- `json.loads(line)` has no recovery. The log is append-only with a single
  writer, but a crash mid-write leaves a truncated final line — after which
  every subsequent chat turn (`read_last_turn` runs each turn) and `imago
  metrics` raise `JSONDecodeError` until the file is hand-edited.
- **Suggested fix:** in `read_events`, skip-and-warn on the final line if it
  fails to parse (or tolerate unparseable lines generally, counting them).

### F11 — `imago metrics --last 0` shows all runs instead of none
- **Where:** `imago/core/cli.py:153`
- **Severity:** low · **Confidence:** high · **Reproduced:** yes
- `[-args.last:]` with `--last 0` becomes `[-0:]`, i.e. `[0:]` — the whole
  list. Harmless-looking, but it silently scans every run file when asked for
  zero.
- **Suggested fix:** `run_files = sorted(...)[max(0, len(r) - args.last):]` or
  an early return when `args.last <= 0`.

### F12 — Provider garbage crashes the turn in adapter parsing
- **Where:** `imago/core/adapters.py:113-116` (OpenAI `_parse`), `adapters.py:113` (`data["choices"][0]`)
- **Severity:** low · **Confidence:** medium
- `json.loads(c["function"]["arguments"] or "{}")` raises on malformed
  tool-argument JSON, and `data["choices"][0]` raises `KeyError`/`IndexError`
  on a 200 response with an unexpected body. Either turns a recoverable
  provider hiccup into a session-ending exception.
- **Suggested fix:** validate/guard the response shape in `_parse` and raise a
  single well-named `RuntimeError("malformed completion from {model}: …")` that
  callers already know how to surface.

## Quiet notes (not counted as findings)

- `cli.format_wave_summary` (`cli.py:102-106`): the `isinstance(value, dict)`
  branch and the else branch are identical — dead distinction.
- `RealAgent.start` passes `run_id="eval"` into `build_session_host`
  (`agent.py:28-32`) but discards the returned second element, so the intended
  run-id is unused (the log path comes from `new_run_id("trap")` instead).
- `cost_estimate_usd` (`client.py:18-20`) treats a pricing entry with missing
  keys as $0 with `pricing_known=True` — config-controlled, but a typo'd key
  silently prices calls at zero.

## Method

Full read of all 24 source files under `imago/` (~1,500 lines), hunting for the
checklist categories: logic errors, unhandled exceptions, off-by-one errors,
resource leaks, race conditions, broken error paths, silently swallowed
failures. Candidate findings were verified by execution where deterministic
(6 of 12 reproduced in a sandbox copy with a fake model client; the rest are
static traces with the mechanism named). No project files were modified; all
repro work happened under `/tmp`. No commit, no push.
