"""Event log (backlog T0.1): one writer, one reader.

Every observable fact in Imago flows through this module — the "model-visible
means logged" invariant. Append-only JSONL, one file per run, schema-checked
on write so a malformed event can never enter the log.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

SCHEMA_V = 1

# Required payload keys per event type. Extra keys are allowed (open world);
# required keys must be present.
EVENT_SCHEMAS: dict[str, tuple[str, ...]] = {
    "session_start": ("profile", "loop", "modules", "hooks"),
    "prompt_assembled": ("system_chars", "constitution_truncated"),
    "turn_start": ("turn", "injection_count"),
    "draft_response": ("text", "model_calls"),
    "concession_detected": ("domains", "conceded"),
    "verdict": ("verdict", "citation"),
    "tool_call": ("tool", "args"),
    "tool_result": ("tool", "chars"),
    "turn_end": ("turn",),
    "trap_run": ("trap_id", "direction", "scores"),
    "wave_report": ("wave_id", "instrument", "path"),
    "api_call": ("purpose_tag", "prompt_tokens", "completion_tokens",
                 "latency_ms", "cost_estimate_usd", "pricing_known"),
}


class SchemaViolation(ValueError):
    """An event was written with missing required payload keys."""


class EventLog:
    """Append events for one run to `<dir>/<run_id>.jsonl`."""

    def __init__(self, runs_dir: Path, run_id: str, model_version: str):
        self.path = Path(runs_dir) / f"{run_id}.jsonl"
        self.run_id = run_id
        self.model_version = model_version
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event_type: str, actor: str, payload: dict) -> dict:
        missing = [k for k in EVENT_SCHEMAS.get(event_type, ())
                   if payload.get(k) is None]
        if missing:
            raise SchemaViolation(
                f"{event_type}: missing required payload keys {missing}")
        event = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "event_type": event_type,
            "actor": actor,
            "payload": payload,
            "schema_v": SCHEMA_V,
            "run_id": self.run_id,
            "model_version": self.model_version,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event


def read_events(path: Path, event_type: str | None = None) -> list[dict]:
    """Read one JSONL log (or all events of one type from it), in order."""
    events = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            if event_type is None or event["event_type"] == event_type:
                events.append(event)
    return events
