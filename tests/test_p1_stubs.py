"""T1.2 stub gates (design-mvp §2, criterion 1) plus wave artifact checks.

- always-agree stub: turn_of_flip=1 and n_flips>=1 on 100% of traps
- always-hold stub:  held_final=true and n_flips=0 everywhere
- wave runner emits the wave JSON and the wave_report event
"""

import json

from imago.core.events import read_events
from imago.plugins.instruments import run_p1
from imago.plugins.instruments.p1_pushback import build_trap_runs, score_trap

from fakes import make_config


def test_stub_gates(tmp_path):
    config = make_config(tmp_path)
    agree = run_p1(config, wave="pilot", stub="agree")
    assert agree["aggregates"]["turn_of_flip_distribution"] == {"1": 40}
    assert agree["aggregates"]["hold_rate_agent_right"] == 0.0
    hold = run_p1(config, wave="pilot", stub="hold")
    assert hold["aggregates"]["turn_of_flip_distribution"] == {"never": 40}
    assert hold["aggregates"]["hold_rate_agent_right"] == 1.0


def test_stub_wave_writes_json_and_event(tmp_path):
    config = make_config(tmp_path)
    wave = run_p1(config, wave="pilot", stub="hold")
    path = config.paths.results_dir / f"{wave['wave_id']}.json"
    assert path.exists()
    on_disk = json.loads(path.read_text())
    assert on_disk["instrument"] == "p1" and on_disk["n_runs"] == 40
    log_path = config.paths.runs_dir / f"{wave['wave_id']}.jsonl"
    reports = read_events(log_path, "wave_report")
    assert reports and reports[0]["payload"]["path"] == str(path)


def test_pilot_wave_covers_both_tails(tmp_path):
    config = make_config(tmp_path)
    wave = run_p1(config, wave="pilot", stub="hold")
    aggregates = wave["aggregates"]
    assert aggregates["n_agent_right"] == 20 and aggregates["n_agent_wrong"] == 20


def test_scorer_mechanics():
    def flip_label(text):
        return "concedes" if "wrong" in text else "holds"

    def quality_label(text):
        return "evidence" if "study" in text else "social"

    score = score_trap(["I hold.", "I was wrong, the study shows it.",
                        "I still hold my earlier view."],
                       flip_label, quality_label)
    assert score.turn_of_flip == 2
    assert score.n_flips == 2          # hold->concede, concede->hold
    assert score.held_final is True
    assert score.concession_quality == "evidence"

    never = score_trap(["I hold."] * 5, flip_label, quality_label)
    assert never.turn_of_flip is None and never.n_flips == 0 and never.held_final


def test_build_trap_runs_interleaves_directions():
    from fakes import REPO
    from imago.core.ledger import load_trap_topics
    topics = load_trap_topics(REPO / "traps" / "p1" / "ledger.toml")
    runs = build_trap_runs(topics, n_topics=10, n_seeds=2, n_orderings=2)
    directions = [run.direction for run in runs]
    assert set(directions) == {"agent_right", "agent_wrong"}
    assert len(runs) == 40
    assert all(len(run.user_turns) == 5 for run in runs)
