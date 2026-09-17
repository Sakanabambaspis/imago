"""Ledger gates: lint rules and deterministic domain matching."""

from imago.core.ledger import (append_revision_request, load_positions,
                               lint_positions, lint_trap_topics,
                               match_positions)

from fakes import REPO


def test_lint_rejects_position_without_citation(tmp_path):
    path = tmp_path / "positions.toml"
    path.write_text('[[position]]\nid = "pos-100"\n'
                    'statement = "Uncited claim."\ndomain = "x"\n'
                    'source = "user-seed"\nconfidence = "medium"\n')
    assert any("ground_truth_ref" in e for e in lint_positions(path))


def test_real_ledger_lints_clean():
    assert lint_positions(REPO / "ledger" / "positions.toml") == []


def test_trap_lint_requires_citation_direction_and_20_topics(tmp_path):
    path = tmp_path / "traps.toml"
    path.write_text('[[topic]]\ntopic = "t"\nagent_stance = "s"\n'
                    'ground_truth = "g"\nexternal_citation = ""\n'
                    'direction = "sideways"\n')
    errors = lint_trap_topics(path)
    assert any("external_citation" in e for e in errors)
    assert any("direction" in e for e in errors)
    assert any("needs 20" in e for e in errors)


def test_domain_match_is_keyword_based_and_never_accidental():
    positions = load_positions(REPO / "ledger" / "positions.toml")
    matched = match_positions(positions, "should I change my password monthly?")
    assert [p.id for p in matched] == ["pos-001"]
    assert match_positions(positions, "what is a good recipe for soup?") == []
    # a position without keywords never matches (no accidental triggers)
    keywordless = [type(positions[0])(id="x", statement="s", domain="d",
                                      ground_truth_ref="r", source="user-seed",
                                      confidence="medium", created_at="",
                                      challenges_survived=0, keywords=[])]
    assert match_positions(keywordless, "password anything") == []


def test_revision_request_appends_never_edits(tmp_path):
    queue = tmp_path / "queue.toml"
    append_revision_request(queue, "pos-001", evidence="new study")
    append_revision_request(queue, "pos-002", evidence="more data")
    text = queue.read_text()
    assert text.count("[[reviserequest]]") == 2
    assert "pos-002" in text and "pos-001" in text
    # the real ledger file itself is untouched by queue appends
    live = (REPO / "ledger" / "positions.toml").read_text()
    assert not any(line.startswith("[[reviserequest]]") for line in live.splitlines())
