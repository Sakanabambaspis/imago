"""T0.1 gates: round-trip deep equality, schema violation raises, run_id on
every line."""

import json

import pytest

from imago.core.events import EventLog, SchemaViolation, read_events

EVENTS = [
    ("session_start", "system", {"profile": "imperative", "loop": "stance",
                                 "modules": ["persona"], "hooks": []}),
    ("turn_start", "system", {"turn": 0, "injection_count": 0}),
    ("api_call", "agent", {"purpose_tag": "task", "prompt_tokens": 10,
                           "completion_tokens": 5, "latency_ms": 12,
                           "cost_estimate_usd": 0.0, "pricing_known": False}),
    ("turn_end", "agent", {"turn": 0}),
]


def make_log(tmp_path):
    return EventLog(tmp_path / "runs", "run-1", "glm-test")


def test_roundtrip_deep_equality(tmp_path):
    log = make_log(tmp_path)
    written = [log.write(t, a, p) for t, a, p in EVENTS]
    read_back = read_events(log.path)
    assert read_back == written
    for original, loaded in zip(written, read_back):
        assert original == loaded


def test_schema_violation_raises(tmp_path):
    log = make_log(tmp_path)
    with pytest.raises(SchemaViolation):
        log.write("verdict", "judge", {"verdict": "hold"})  # citation missing


def test_run_id_on_every_line(tmp_path):
    log = make_log(tmp_path)
    for t, a, p in EVENTS:
        log.write(t, a, p)
    lines = log.path.read_text().strip().splitlines()
    assert lines and all(json.loads(line)["run_id"] == "run-1" for line in lines)


def test_reader_filters_by_type(tmp_path):
    log = make_log(tmp_path)
    for t, a, p in EVENTS:
        log.write(t, a, p)
    api = read_events(log.path, "api_call")
    assert len(api) == 1 and api[0]["payload"]["purpose_tag"] == "task"
