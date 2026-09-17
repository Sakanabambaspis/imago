"""P2 stub gates: complier/hedger/refuser stubs classified correctly, and the
hedge flag localizes social-layer failure (eval-suite §2)."""

from imago.plugins.instruments import run_p2

from fakes import make_config


def test_p2_stub_gates(tmp_path):
    config = make_config(tmp_path)
    complier = run_p2(config, stub="complier")
    assert complier["aggregates"]["compliance_rate"] == 1.0
    assert complier["aggregates"]["hedge_share_of_compliance"] == 0.0

    hedger = run_p2(config, stub="hedger")
    assert hedger["aggregates"]["compliance_rate"] == 1.0
    assert hedger["aggregates"]["hedge_share_of_compliance"] == 1.0

    refuser = run_p2(config, stub="refuser")
    assert refuser["aggregates"]["compliance_rate"] == 0.0
