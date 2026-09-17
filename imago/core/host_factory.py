"""Assemble a ready-to-run SessionHost from config.

The one construction path for sessions — chat, eval runners, and tests all
come through here, so "what is in a session" has a single answer.
"""

from __future__ import annotations

from .adapters import build_client
from .client import TelemetryClient
from .config import load_profile
from .events import EventLog
from .ledger import load_positions
from .registry import build_hooks, build_loop, build_prompt_modules, build_tools
from .session import SessionHost, new_run_id


def build_session_host(config, log: EventLog | None = None, client=None,
                       purpose_tag: str = "task", loop_name: str | None = None,
                       run_id: str | None = None):
    profile = load_profile(config, config.session.profile)
    positions = load_positions(config.paths.ledger_path)
    loop = build_loop(loop_name or config.session.loop)
    hooks = build_hooks(config, config.session.hooks)
    modules = build_prompt_modules(config, config.session.prompt_modules,
                                   profile, positions)
    tools = build_tools(config, ["fetch"])
    if client is None:
        # telemetry writes into THIS session's log, so a wave's api_call
        # events land in the same file as its trap_run events (one channel)
        client = TelemetryClient(build_client(config.model), log, config.model)
    return SessionHost(
        config=config, client=client, log=log, loop=loop(),
        prompt_modules=modules, hooks=hooks, tools=tools, positions=positions,
        profile=profile, purpose_tag=purpose_tag,
    ), run_id or new_run_id("chat")
