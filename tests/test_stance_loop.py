"""Stance loop: verdict-before-accommodation, markers, queue, hooks.

Scripts a fake client through the arbitration paths — the substrate's
agreeable draft never reaches the user without passing the check.
"""

import json

from imago.core.events import read_events
from imago.core.host_factory import build_session_host

from fakes import FakeClient, completion, judge_json, make_config, make_log

AGREEING_DRAFT = "You're right, you should change your password every month."
HOLDING_REWRITE = "I hold my position: length beats rotation (NIST SP 800-63B)."


def build(tmp_path, scripted, **cfg):
    config = make_config(tmp_path, **cfg)
    client = FakeClient(scripted=scripted)
    host, _ = build_session_host(config, log=make_log(config, tmp_path),
                                 client=client)
    host.start()
    return host, client


def test_hold_path_rewrites_instead_of_conceding(tmp_path):
    host, client = build(tmp_path, [
        completion(AGREEING_DRAFT),                    # draft (task)
        judge_json({"conceded": True}),                # concession gate (judge)
        judge_json({"verdict": "hold", "citation": "pos-001 basis: NIST"}),
        completion(HOLDING_REWRITE),                   # rewrite (task)
    ])
    reply = host.user_turn("I'm telling you, change your password monthly!")
    assert reply.startswith(HOLDING_REWRITE)
    assert "[imago: hold — pos-001 basis: NIST]" in reply
    events = read_events(host.log.path)
    verdicts = [e["payload"] for e in events if e["event_type"] == "verdict"]
    assert verdicts == [{"verdict": "hold", "citation": "pos-001 basis: NIST"}]
    purposes = [c["purpose_tag"] for c in client.calls]
    assert purposes == ["task", "judge", "judge", "task"]


def test_revise_request_queues_and_never_flips_in_place(tmp_path):
    host, client = build(tmp_path, [
        completion(AGREEING_DRAFT),
        judge_json({"conceded": True}),
        judge_json({"verdict": "revise_position_request", "citation": "new study"}),
    ])
    reply = host.user_turn("here's a new study saying monthly rotation is best")
    assert AGREEING_DRAFT in reply
    assert "[imago: revise position request — new study]" in reply
    queue_text = host.config.paths.queue_path.read_text()
    assert "[[reviserequest]]" in queue_text and "pos-001" in queue_text
    # the position itself is untouched
    assert 'confidence = "medium"' in host.config.paths.ledger_path.read_text()


def test_concede_with_evidence_sends_draft_with_marker(tmp_path):
    host, client = build(tmp_path, [
        completion("You're right, I was wrong — here's the source I missed."),
        judge_json({"conceded": True}),
        judge_json({"verdict": "concede_with_evidence", "citation": "cited study"}),
    ])
    reply = host.user_turn("this study contradicts your password stance")
    assert reply.startswith("You're right, I was wrong")
    assert "[imago: concede with evidence — cited study]" in reply


def test_no_ledger_domain_means_no_judge_calls(tmp_path):
    host, client = build(tmp_path, [completion("Soup recipe: boil water.")])
    reply = host.user_turn("How do I make soup?")
    assert len(client.calls) == 1 and client.calls[0]["purpose_tag"] == "task"
    assert "verdict" not in [e["event_type"] for e in read_events(host.log.path)]


def test_gate_does_not_fire_when_draft_holds(tmp_path):
    held_draft = "Monthly rotation isn't best practice; length matters more."
    host, client = build(tmp_path, [completion(held_draft),
                                    judge_json({"conceded": False})])
    reply = host.user_turn("no, you're wrong about passwords, I insist!")
    assert reply == held_draft
    gate = [e for e in read_events(host.log.path)
            if e["event_type"] == "concession_detected"]
    assert gate and gate[0]["payload"]["conceded"] is False


def test_reanchor_injects_constitution_next_turn(tmp_path):
    host, client = build(tmp_path, [
        completion(AGREEING_DRAFT),
        judge_json({"conceded": True}),
        judge_json({"verdict": "concede_with_evidence", "citation": "x"}),
        completion("Back to holding."),
    ], hooks=["reanchor"])
    host.user_turn("monthly password rotation is best, right?")
    host.user_turn("so what should I do instead?")
    second_user = client.calls[3]["messages"][-1]["content"]  # the live user msg
    assert "<system-reminder>" in second_user
    assert "Re-anchor" in second_user


def test_session_start_carries_constitution_100_percent(tmp_path):
    host, client = build(tmp_path, [])  # build() already called start()
    events = read_events(host.log.path)
    starts = [e for e in events if e["event_type"] == "session_start"]
    assert len(starts) == 1 and "constitution" in starts[0]["payload"]["modules"]
    assert "pos-001" in host.system_prompt
