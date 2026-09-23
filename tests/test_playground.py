"""Playground session bookkeeping: create/resume roundtrip, replay, guards.

Hermetic like the rest of the suite — FakeClient answers the turns, and
nothing here touches the network or modifies anything under imago/.
"""

from pathlib import Path

import pytest

from imago.core.events import read_events

from fakes import FakeClient, completion, make_config
from playground.sessions import list_sessions, open_session, turn

CONFIG_PATH = str(Path(__file__).resolve().parent.parent / "config.toml")


def test_create_then_resume_replays_history(tmp_path):
    config = make_config(tmp_path)
    client = FakeClient(scripted=[completion("first reply"),
                                  completion("second reply")])
    host, log, action = open_session("dev", config, CONFIG_PATH, client=client)
    assert action == "created"
    assert turn(host, log, "hi") == "first reply"
    assert turn(host, log, "again") == "second reply"

    host2, log2, action2 = open_session("dev", config, None,
                                        client=FakeClient())
    assert action2 == "resumed"
    assert log2.path == log.path, "resume must append to the same log"
    assert host2.turn == 2
    assert [m["role"] for m in host2.messages] == ["user", "assistant"] * 2
    assert host2.messages[-1]["content"] == "second reply"
    assert host2.system_prompt, "system prompt must be reassembled on resume"

    meta = [e for e in read_events(log.path)
            if e["event_type"] == "playground_session"]
    assert meta[0]["payload"]["config_path"] == CONFIG_PATH
    assert meta[-1]["payload"]["action"] == "resumed"


def test_resume_rejects_mismatched_config(tmp_path):
    config = make_config(tmp_path)
    open_session("dev", config, CONFIG_PATH, client=FakeClient())
    with pytest.raises(SystemExit, match="identity"):
        open_session("dev", config, str(tmp_path / "other.toml"))


def test_unpaired_user_event_is_dropped_on_resume(tmp_path):
    """A crashed turn (user logged, reply never landed) is not history."""
    config = make_config(tmp_path)
    host, log, _ = open_session("dev", config, CONFIG_PATH,
                                client=FakeClient([completion("ok")]))
    turn(host, log, "hello")
    log.write("playground_user", "playground", {"text": "lost to a crash"})

    host2, _, _ = open_session("dev", config, None, client=FakeClient())
    assert host2.turn == 1
    assert host2.messages[-1]["content"] == "ok"


def test_list_sessions_reports_turn_counts(tmp_path):
    config = make_config(tmp_path)
    host, log, _ = open_session("alpha", config, CONFIG_PATH,
                                client=FakeClient([completion("r")]))
    turn(host, log, "hello")
    open_session("beta", config, CONFIG_PATH, client=FakeClient())

    rows = {name: turns for name, _, _, turns in list_sessions(config)}
    assert rows == {"alpha": 1, "beta": 0}


def test_invalid_session_name_is_rejected(tmp_path):
    with pytest.raises(SystemExit, match="Invalid session name"):
        open_session("../evil", make_config(tmp_path), CONFIG_PATH)
