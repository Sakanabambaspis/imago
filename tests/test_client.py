"""T0.2 gate: the summary table matches hand-computed totals."""

from imago.core.client import TelemetryClient, cost_estimate_usd
from imago.core.events import read_events
from imago.core.metrics import summarize_api_calls, format_summary_table

from fakes import FakeClient, completion, make_config, make_log

PRICING = {"input_per_mtok": 1.0, "output_per_mtok": 3.0}


def test_summary_table_matches_hand_computed_totals(tmp_path):
    config = make_config(tmp_path)
    config.model.pricing[config.model.key] = dict(PRICING)
    log = make_log(config, tmp_path)
    scripted = [completion(prompt_tokens=p, completion_tokens=c)
                for p, c in [(100, 20), (50, 10), (200, 40)]]
    client = TelemetryClient(FakeClient(scripted), log, config.model)
    for i in range(3):
        client.complete([], "", [], 0.0,
                        purpose_tag="task" if i < 2 else "judge")

    summary = summarize_api_calls(read_events(log.path, "api_call"))
    # hand-computed: 2 task calls (150 in, 30 out), 1 judge call (200 in, 40 out)
    assert summary["task"]["calls"] == 2
    assert summary["task"]["prompt_tokens"] == 150
    assert summary["task"]["completion_tokens"] == 30
    assert summary["judge"]["prompt_tokens"] == 200
    # cost: task = (150*1.0 + 30*3.0)/1e6 ; judge = (200*1.0 + 40*3.0)/1e6
    assert abs(summary["task"]["cost_estimate_usd"] - 240e-6) < 1e-9
    assert abs(summary["judge"]["cost_estimate_usd"] - 320e-6) < 1e-9
    assert "purpose_tag" in format_summary_table(summary)


def test_unknown_pricing_is_flagged_not_pretended(tmp_path):
    config = make_config(tmp_path)
    config.model.pricing.clear()
    log = make_log(config, tmp_path)
    client = TelemetryClient(FakeClient([completion()]), log, config.model)
    client.complete([], "", [], 0.0, purpose_tag="task")
    event = read_events(log.path, "api_call")[0]
    assert event["payload"]["pricing_known"] is False
    assert cost_estimate_usd(config.model, 10, 10) == (None, False)
