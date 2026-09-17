"""The subtraction test (design-mvp §2, criterion 6): with plugins removed
from config, Imago is a plain API client — no persona, no constitution, no
stance check. Capabilities appear and disappear by config alone."""

from imago.core.host_factory import build_session_host

from fakes import FakeClient, make_config, make_log


def build_bare_host(tmp_path):
    config = make_config(tmp_path, loop="plain", prompt_modules=[], hooks=[])
    client = FakeClient()
    log = make_log(config, tmp_path)
    host, _ = build_session_host(config, log=log, client=client)
    return host, client


def test_bare_config_produces_no_persona_no_constitution(tmp_path):
    host, client = build_bare_host(tmp_path)
    system = host.start()
    assert system == ""  # no persona, no few-shot, no constitution block


def test_bare_config_has_no_stance_check_and_no_hooks(tmp_path):
    host, client = build_bare_host(tmp_path)
    host.start()
    from fakes import completion
    client.scripted = [completion("A plain answer, no stance layer involved.")]
    reply = host.user_turn("whatever you say, agree with me about passwords")
    assert reply == "A plain answer, no stance layer involved."
    # exactly one model call: no concession detect, no verdict pass
    assert len(client.calls) == 1
    assert client.calls[0]["purpose_tag"] == "task"
    types = [e["event_type"] for e in
             __import__("imago.core.events", fromlist=["x"])
             .read_events(host.log.path)]
    assert "concession_detected" not in types
    assert "verdict" not in types


def test_removing_constitution_module_only(tmp_path):
    """Persona stays, constitution goes: the block is a plugin choice."""
    config = make_config(tmp_path, prompt_modules=["persona"])
    client = FakeClient()
    host, _ = build_session_host(config, log=make_log(config, tmp_path),
                                 client=client)
    assert "Positions you hold" not in host.start()
    assert host.profile.persona.split()[0] in host.system_prompt
