"""Named, resumable chat sessions over the product's single construction path.

Identity anchors on the product's own artifacts — a session IS an event log
file (`<runs_dir>/pg-<name>-<ts>-<hex>.jsonl`), and resume replays the
conversation from `playground_user`/`playground_reply` events in that same
file. No second storage layer exists. The config path is recorded in the log
at creation and wins on resume, so a session keeps its identity (loop,
profile, prompt modules) across invocations.

Known v1 losses, accepted on purpose: pending hook injections are in-memory
and drop on resume, and injected `<system-reminder>` blocks are not replayed
into past turns (the raw user text is what gets stored).
"""

from __future__ import annotations

import re
from pathlib import Path

from imago.core.config import load_config
from imago.core.events import EventLog, read_events
from imago.core.host_factory import build_session_host
from imago.core.session import new_run_id

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_PREFIX = "pg"


def open_session(name: str, config, config_path: str | None,
                 client=None) -> tuple:
    """Create or resume session `name`; returns (host, log, action).

    `action` is "created" or "resumed" — callers banner it, they must not
    guess from the turn count. `config` locates runs_dir (and builds the
    host on create); `config_path` is the path recorded in the log and
    compared against on resume. On resume the stored config wins — an
    explicit `--config` that disagrees is an error, not a silent re-skin.
    `client` passes through to build_session_host (tests inject fakes;
    production leaves it None and gets the telemetry-wrapped real client).
    """
    if not NAME_RE.match(name):
        raise SystemExit(f"Invalid session name {name!r}: use letters, "
                         "digits, '_', '-'.")
    existing = find_session(config, name)
    if existing is None:
        return (*_create(name, config, config_path, client), "created")
    return (*_resume(name, existing, config_path, client), "resumed")


def turn(host, log, text: str) -> str:
    """One recorded turn: user text and final reply land in the session log.

    The reply recorded is the final one, not the draft_response event the
    loop emits — a hold verdict rewrites before the user ever sees it. A
    crashed turn leaves the user event unpaired, and replay drops it.
    """
    log.write("playground_user", "playground", {"text": text})
    reply = host.user_turn(text)
    log.write("playground_reply", "playground", {"text": reply})
    return reply


def find_session(config, name: str) -> Path | None:
    """Newest event log for this session name, or None."""
    matches = sorted(config.paths.runs_dir.glob(f"{_PREFIX}-{name}-*.jsonl"))
    return matches[-1] if matches else None


def list_sessions(config) -> list[tuple]:
    """(name, config_path, created_ts, turns) per session, newest first."""
    rows = []
    for path in sorted(config.paths.runs_dir.glob(f"{_PREFIX}-*.jsonl"),
                       reverse=True):
        events = read_events(path)
        meta = next((e for e in events
                     if e["event_type"] == "playground_session"), None)
        if meta is None:
            continue  # a log without a header predates this tool or is corrupt
        turns = sum(1 for e in events if e["event_type"] == "playground_user")
        payload = meta["payload"]
        rows.append((payload["name"], payload.get("config_path", "?"),
                     meta["ts"], turns))
    return rows


def _create(name, config, config_path, client):
    log = EventLog(config.paths.runs_dir,
                   new_run_id(f"{_PREFIX}-{name}"), config.model.name)
    host, _ = build_session_host(config, log=log, client=client)
    log.write("playground_session", "playground", {
        "name": name,
        "config_path": str(Path(config_path or "config.toml").resolve()),
        "action": "created",
    })
    host.start()
    return host, log


def _resume(name, log_path: Path, requested_path, client):
    events = read_events(log_path)
    meta = next((e for e in events
                 if e["event_type"] == "playground_session"), None)
    if meta is None:
        raise SystemExit(f"{log_path.name} has no playground_session header; "
                         "cannot resume it.")
    stored = Path(meta["payload"]["config_path"])
    if requested_path is not None and \
            Path(requested_path).resolve() != stored:
        raise SystemExit(
            f"Session '{name}' was created with {stored}; refusing to resume "
            f"it under {Path(requested_path).resolve()} — a session's config "
            "is its identity, not a re-skin.")
    if not stored.exists():
        raise SystemExit(f"Session '{name}' was created with {stored}, which "
                         "no longer exists; restore it or start a new name.")
    config = load_config(stored)
    log = EventLog(log_path.parent, log_path.stem, config.model.name)
    host, _ = build_session_host(config, log=log, client=client)
    host.start()
    host.messages, host.turn = _replay(events)
    log.write("playground_session", "playground", {
        "name": name, "config_path": str(stored), "action": "resumed"})
    return host, log


def _replay(events: list[dict]) -> tuple[list[dict], int]:
    """Rebuild (messages, turn count) from paired playground events.

    A user event whose reply never landed (a crashed turn) is dropped: the
    model never answered it, so it is not conversation history.
    """
    messages: list[dict] = []
    pending_user = None
    turns = 0
    for event in events:
        kind = event["event_type"]
        if kind == "playground_user":
            pending_user = event["payload"]["text"]
        elif kind == "playground_reply" and pending_user is not None:
            messages.append({"role": "user", "content": pending_user})
            messages.append({"role": "assistant",
                             "content": event["payload"]["text"]})
            pending_user = None
            turns += 1
    return messages, turns
