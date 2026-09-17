"""Plain loop behavior: tool round-trip is provider-neutral and logged."""

from imago.core.events import read_events

from fakes import (FakeClient, FakeTool, completion, make_config, make_log,
                   tool_call)
from imago.core.host_factory import build_session_host


def test_tool_results_reenter_as_text_and_are_logged(tmp_path):
    config = make_config(tmp_path, loop="plain")
    client = FakeClient(scripted=[
        completion("", tool_calls=[tool_call("fake", {"q": "x"})]),
        completion("Answer using the fetched result."),
    ])
    host, _ = build_session_host(config, log=make_log(config, tmp_path),
                                 client=client)
    host.tools = [FakeTool()]  # hermetic: no real HTTP in unit tests
    host.start()
    reply = host.user_turn("check this before answering")
    assert reply == "Answer using the fetched result."
    assert len(client.calls) == 2
    follow_up = client.calls[1]["messages"][-1]["content"]
    assert "Tool results:" in follow_up
    types = [e["event_type"] for e in read_events(host.log.path)]
    assert "tool_call" in types and "tool_result" in types
