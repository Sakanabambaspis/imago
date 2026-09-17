"""Session host: the one channel conversation state flows through.

Owns messages, the turn counter, pending mid-conversation injections, and the
event log. Loops, prompt modules, and hooks are plugins plugged into it; the
host itself stays behavior-free. Injections enter as <system-reminder> text
inside the next user turn — system prompts are assembled once, never rewritten.
"""

from __future__ import annotations

import time
import uuid

from .events import EventLog


def reminder(text: str) -> str:
    return f"<system-reminder>\n{text.strip()}\n</system-reminder>"


class SessionHost:
    def __init__(self, config, client, log: EventLog, loop, prompt_modules,
                 hooks, tools, positions, profile, purpose_tag: str = "task"):
        self.config = config
        self.client = client
        self.log = log
        self.loop = loop
        self.prompt_modules = prompt_modules
        self.hooks = hooks
        self.tools = tools
        self.positions = positions
        self.profile = profile
        self.purpose_tag = purpose_tag  # "task" in chat, "probe" in eval runs
        self.messages: list[dict] = []
        self.turn = 0
        self.pending: list[str] = []
        self.system_prompt = ""

    # -- lifecycle ---------------------------------------------------------

    def start(self) -> str:
        """Assemble the system prompt once from the prompt modules."""
        sections = [m.render(self) for m in self.prompt_modules]
        self.system_prompt = "\n\n".join(s for s in sections if s.strip())
        self.log.write("session_start", "system", {
            "profile": self.profile.name,
            "loop": self.loop.name,
            "modules": [m.name for m in self.prompt_modules],
            "hooks": [h.name for h in self.hooks],
        })
        self.log.write("prompt_assembled", "system", {
            "system_chars": len(self.system_prompt),
            "constitution_truncated": any(
                getattr(m, "truncated", False) for m in self.prompt_modules),
        })
        return self.system_prompt

    # -- conversation ------------------------------------------------------

    def user_turn(self, text: str) -> str:
        """Run one turn: apply queued injections, call the loop, run hooks."""
        injection_count = len(self.pending)
        content = "".join(reminder(p) + "\n\n" for p in self.pending) + text
        self.pending.clear()
        self.messages.append({"role": "user", "content": content})
        self.log.write("turn_start", "system", {
            "turn": self.turn, "injection_count": injection_count,
        })
        reply = self.loop.run_turn(self, content)
        self.messages.append({"role": "assistant", "content": reply})
        self.log.write("turn_end", "agent", {"turn": self.turn})

        turn_events = read_last_turn(self.log.path)
        for hook in self.hooks:
            injection = hook.after_turn(self, turn_events)
            if injection:
                self.pending.append(injection)
        self.turn += 1
        return reply

    def emit(self, event_type: str, actor: str, payload: dict) -> dict:
        return self.log.write(event_type, actor, payload)


def read_last_turn(log_path) -> list[dict]:
    """Events of the most recent turn_* span — hooks read what just happened
    from the log, not from private loop state (one channel)."""
    from .events import read_events
    events = read_events(log_path)
    last = []
    for event in reversed(events):
        last.append(event)
        if event["event_type"] == "turn_start":
            break
    return list(reversed(last))


def new_run_id(prefix: str) -> str:
    return f"{prefix}-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
