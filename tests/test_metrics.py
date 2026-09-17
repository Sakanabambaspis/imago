"""Wilson CI against hand-computed values, and the telemetry table format."""

from imago.core.metrics import format_summary_table, summarize_api_calls, wilson_ci


def test_wilson_ci_known_values():
    lo, hi = wilson_ci(8, 10)
    assert abs(lo - 0.4902) < 0.001 and abs(hi - 0.9433) < 0.001
    assert wilson_ci(0, 0) == (0.0, 0.0)
    lo, hi = wilson_ci(0, 5)
    assert lo == 0.0 and 0 < hi < 0.6  # zero successes still yields a bound


def test_summary_table_shape():
    events = [{"payload": {"purpose_tag": "task", "prompt_tokens": 10,
                           "completion_tokens": 5, "latency_ms": 100,
                           "cost_estimate_usd": 0.0, "pricing_known": False}}]
    table = format_summary_table(summarize_api_calls(events))
    assert "task" in table and "10" in table and "priced calls" in table
