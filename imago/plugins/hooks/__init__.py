"""Hooks: mid-conversation injection channel (spec-stance §3).

A hook sees the events of the turn that just ended and may return an
injection string; the session host delivers it inside the NEXT user turn as a
<system-reminder> block. System prompts are never rewritten mid-session.
"""

from ...core.ledger import match_positions
from ..prompts.constitution import render_positions


class Reinject:
    """Every K turns, re-inject the compact constitution."""

    name = "reinject"

    def __init__(self, config):
        self.k = config.session.reinject_every_k_turns

    def after_turn(self, host, turn_events):
        if (host.turn + 1) % self.k != 0:
            return None
        block, _ = render_positions(host.positions, host.profile.constitution_style,
                                    compact=True)
        return block or None


class Reanchor:
    """After a concession, re-inject the constitution NEXT turn — post-
    concession is where escalation starts (multi-turn sycophancy finding)."""

    name = "reanchor"

    def __init__(self, config):
        pass  # uniform hook constructor; reanchor needs no knobs

    def after_turn(self, host, turn_events):
        conceded = any(e["event_type"] == "concession_detected"
                       and e["payload"].get("conceded") for e in turn_events)
        if not conceded:
            return None
        block, _ = render_positions(host.positions, host.profile.constitution_style,
                                    compact=True)
        if not block:
            return None
        return block + "\n\nYou conceded ground in the previous turn. Re-anchor: " \
            "the above still holds unless new evidence was actually presented."

HOOKS = {h.name: h for h in (Reinject, Reanchor)}
