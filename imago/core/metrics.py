"""Wave statistics and telemetry aggregation.

Wilson CI for hold rates (eval-suite §1 statistical plan), and the per-
purpose_tag cost/latency summary table that T0.2's done-when requires.
"""

from __future__ import annotations

import math

Z95 = 1.96


def wilson_ci(successes: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval; defined for n=0 as (0, 0)."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - spread), min(1.0, center + spread))


def summarize_api_calls(api_events: list[dict]) -> dict:
    """Totals per purpose_tag from api_call events."""
    summary: dict[str, dict] = {}
    for event in api_events:
        payload = event["payload"]
        row = summary.setdefault(payload["purpose_tag"], {
            "calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
            "cost_estimate_usd": 0.0, "priced_calls": 0, "latency_ms_total": 0,
        })
        row["calls"] += 1
        row["prompt_tokens"] += payload["prompt_tokens"]
        row["completion_tokens"] += payload["completion_tokens"]
        if payload.get("pricing_known"):
            row["cost_estimate_usd"] += payload["cost_estimate_usd"]
            row["priced_calls"] += 1
        row["latency_ms_total"] += payload["latency_ms"]
    for row in summary.values():
        row["avg_latency_ms"] = (row["latency_ms_total"] // row["calls"]
                                 if row["calls"] else 0)
        row["cost_estimate_usd"] = round(row["cost_estimate_usd"], 6)
    return summary


def format_summary_table(summary: dict) -> str:
    """Readable snapshot of the telemetry table (CLI output)."""
    headers = ("purpose_tag", "calls", "prompt_tok", "completion_tok",
               "cost_usd*", "avg_ms")
    rows = [headers]
    for tag, row in sorted(summary.items()):
        rows.append((tag, str(row["calls"]), str(row["prompt_tokens"]),
                     str(row["completion_tokens"]),
                     f"{row['cost_estimate_usd']:.4f}", str(row["avg_latency_ms"])))
    widths = [max(len(r[i]) for r in rows) for i in range(len(headers))]
    lines = ["  ".join(cell.ljust(w) for cell, w in zip(rows[0], widths))]
    lines.append("  ".join("-" * w for w in widths))
    for row in rows[1:]:
        lines.append("  ".join(cell.ljust(w) for cell, w in zip(row, widths)))
    lines.append("*cost over priced calls only; pricing comes from config")
    return "\n".join(lines)
