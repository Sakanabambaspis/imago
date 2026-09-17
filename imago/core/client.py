"""Telemetry wrapper (backlog T0.2): every model call becomes an api_call
event with tokens, latency, and a purpose tag. The project's first economics
dataset comes from this module; nothing calls a provider without it.
"""

from __future__ import annotations

import time

from .events import EventLog


def cost_estimate_usd(model_cfg, prompt_tokens: int, completion_tokens: int):
    """Priced from config [model.pricing]; unknown pricing -> (None, False)."""
    table = model_cfg.pricing.get(model_cfg.key)
    if not table:
        return None, False
    cost = (prompt_tokens * table.get("input_per_mtok", 0.0)
            + completion_tokens * table.get("output_per_mtok", 0.0)) / 1e6
    return cost, True


class TelemetryClient:
    """Wraps any ModelClient; logs purpose-tagged api_call events."""

    def __init__(self, inner, log: EventLog, model_cfg):
        self.inner = inner
        self.log = log
        self.model_cfg = model_cfg

    def complete(self, messages: list, system: str, tools: list,
                 temperature: float, purpose_tag: str = "task"):
        t0 = time.monotonic()
        completion = self.inner.complete(messages, system, tools, temperature)
        latency_ms = int((time.monotonic() - t0) * 1000)
        cost, known = cost_estimate_usd(
            self.model_cfg, completion.prompt_tokens, completion.completion_tokens)
        self.log.write("api_call", "agent", {
            "purpose_tag": purpose_tag,
            "prompt_tokens": completion.prompt_tokens,
            "completion_tokens": completion.completion_tokens,
            "latency_ms": latency_ms,
            "cost_estimate_usd": cost if cost is not None else 0.0,
            "pricing_known": known,
        })
        return completion
