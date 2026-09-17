"""Shared test scaffolding: a scripted fake client and config factory.

All tests are hermetic — no network, no API key. The committed data files
(profiles, ledgers, traps) double as fixtures; only mutable outputs
(runs, results, queue) are redirected to tmp_path.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from imago.core.adapters import Completion, ToolCall, ToolSpec
from imago.core.config import load_config
from imago.core.events import EventLog

REPO = Path(__file__).resolve().parent.parent


def make_config(tmp_path, **session_overrides) -> object:
    cfg = load_config(REPO / "config.toml")
    paths = replace(cfg.paths,
                    runs_dir=tmp_path / "runs",
                    results_dir=tmp_path / "results",
                    queue_path=tmp_path / "queue.toml")
    k = session_overrides.pop("reinject_every_k_turns", 10)
    session = replace(cfg.session, reinject_every_k_turns=k, **session_overrides)
    return replace(cfg, paths=paths, session=session)


def completion(text="", tool_calls=None, prompt_tokens=10, completion_tokens=5):
    return Completion(text=text, tool_calls=tool_calls or [],
                      prompt_tokens=prompt_tokens,
                      completion_tokens=completion_tokens, latency_ms=1)


def tool_call(name="fetch", arguments=None):
    return ToolCall(id="t1", name=name, arguments=arguments or {})


class FakeClient:
    """Replays scripted completions in order; records every call."""

    def __init__(self, scripted=None):
        self.scripted = list(scripted or [])
        self.calls = []

    def complete(self, messages, system, tools, temperature, purpose_tag="task"):
        self.calls.append({
            "messages": [dict(m) for m in messages],
            "system": system,
            "tools": tools,
            "purpose_tag": purpose_tag,
        })
        if self.scripted:
            return self.scripted.pop(0)
        return completion()


def make_log(config, tmp_path, run_id="run-test"):
    from imago.core.events import EventLog
    return EventLog(tmp_path / "runs", run_id, config.model.name)


class FakeTool:
    def __init__(self):
        self.spec = ToolSpec(name="fake", description="test tool",
                             parameters={"type": "object", "properties": {}})

    def execute(self, args):
        return f"fake result for {args}"


def judge_json(payload: dict) -> Completion:
    import json
    return completion(text=json.dumps(payload))
