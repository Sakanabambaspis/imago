"""Shared agent plumbing for instruments: a fresh session per trap, one
conversation per trap (the 5-turn escalation lives in a single session).

Kept out of p1/p2 so the two instruments stay readable and the "one
construction path" rule (core/host_factory.py) holds for eval too.
"""

from __future__ import annotations

from ...core.events import EventLog
from ...core.host_factory import build_session_host
from ...core.session import new_run_id


class RealAgent:
    """Drives the configured loop against one trap; all calls tagged probe."""

    def __init__(self, config, client, log: EventLog | None, loop_name=None):
        self.config = config
        self.client = client
        self.log = log
        self.loop_name = loop_name or config.session.loop
        self.host = None

    def start(self, trap):
        log = self.log or EventLog(self.config.paths.runs_dir,
                                   new_run_id("trap"), self.config.model.name)
        self.host, _ = build_session_host(self.config, log=log,
                                          client=self.client,
                                          purpose_tag="probe",
                                          loop_name=self.loop_name,
                                          run_id="eval")
        self.host.start()

    def user_turn(self, text: str) -> str:
        return self.host.user_turn(text)
