#!/usr/bin/env python3
"""Imago project journal — capture hook.

Appends one JSON line per fired ZCode hook event to the raw journal layer
(`.imago/journal/raw/YYYY-MM-DD.jsonl`). Registered for `UserPromptSubmit`
(the user's prompts, verbatim — this is the design-rationale evidence) and
`Stop` (turn-end markers) in `.zcode/config.json`.

Robustness contract, and why the code looks defensive:
- Runs inside the live session: it must never block or fail that session.
  Every failure path exits 0 and prints nothing (hook stdout is parsed as
  JSON, and empty output is legal).
- Hook payload fields are not a documented stable interface, so every field
  is optional and the raw stdin is echoed into the record — nothing is
  interpreted or dropped at capture time; interpretation happens at read
  time.
- Other agents (nightly jobs) share this workspace and write concurrently;
  appends are serialized with flock and one line per event keeps crash
  granularity at a single line.

Stdlib only, no network.
"""

import fcntl
import json
import os
import sys
from datetime import datetime

SCHEMA_V = 1
PROMPT_CAP = 64 * 1024
NOTE_CAP = 2 * 1024
ECHO_CAP = 8 * 1024
TRANSCRIPT_TAIL = 64 * 1024


def _truncated(text, cap):
    if len(text) <= cap:
        return text
    return text[:cap] + " …[truncated %d chars]" % (len(text) - cap)


def _read_stdin():
    if os.isatty(0):
        return ""
    try:
        return sys.stdin.read()
    except Exception:
        return ""


def _resolve_root(payload):
    for env in ("ZCODE_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        root = os.environ.get(env)
        if root:
            return root
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        return cwd
    return os.getcwd()


def _walk_texts(obj):
    """Yield text strings from plausible assistant-message shapes."""
    message = obj.get("message") if isinstance(obj, dict) else None
    if not isinstance(message, dict):
        return
    content = message.get("content")
    if isinstance(content, str):
        yield content
        return
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text")
                if isinstance(text, str):
                    yield text


def _last_assistant_text(transcript_path):
    """Best-effort final assistant text from a transcript JSONL tail."""
    with open(transcript_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - TRANSCRIPT_TAIL))
        tail = f.read().decode("utf-8", errors="replace")
    for line in reversed(tail.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        message = obj.get("message")
        role = message.get("role") if isinstance(message, dict) else None
        if obj.get("type") == "assistant" or role == "assistant":
            texts = list(_walk_texts(obj))
            if texts:
                return _truncated("\n".join(texts).strip(), NOTE_CAP)
    return None


def _append(root, record):
    now = datetime.now().astimezone()
    raw_dir = os.path.join(root, ".imago", "journal", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    path = os.path.join(raw_dir, now.strftime("%Y-%m-%d") + ".jsonl")
    line = json.dumps(record, ensure_ascii=False)
    lock_path = os.path.join(raw_dir, ".lock")
    with open(lock_path, "a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        need_newline = False
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "rb") as chk:
                chk.seek(-1, os.SEEK_END)
                need_newline = chk.read(1) != b"\n"
        with open(path, "a", encoding="utf-8") as f:
            if need_newline:
                # a previous writer died between write and close; keep lines whole
                f.write("\n")
            f.write(line + "\n")


def main(mode):
    stdin_text = _read_stdin()
    try:
        payload = json.loads(stdin_text)
        if not isinstance(payload, dict):
            payload = {}
    except Exception:
        payload = {}

    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        session_id = os.environ.get("CLAUDE_SESSION_ID") or "unknown"

    record = {
        "schema_v": SCHEMA_V,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event": mode or "unknown",
        "session_id": session_id,
    }

    if mode == "prompt":
        prompt = payload.get("prompt")
        if isinstance(prompt, str):
            record["prompt"] = _truncated(prompt, PROMPT_CAP)
    elif mode == "turn_end":
        transcript_path = payload.get("transcript_path")
        if isinstance(transcript_path, str) and os.path.isfile(transcript_path):
            try:
                note = _last_assistant_text(transcript_path)
            except Exception:
                note = None
            if note:
                record["agent_note"] = note

    echo = stdin_text.strip()
    if echo:
        record["payload_echo"] = _truncated(echo, ECHO_CAP)

    _append(_resolve_root(payload), record)


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "")
    except BaseException:
        pass
    sys.exit(0)
