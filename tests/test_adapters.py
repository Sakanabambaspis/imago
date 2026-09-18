"""build_client honors config: builtin_search is per-endpoint, not hardcoded."""

from dataclasses import replace

from imago.core.adapters import build_client
from imago.core.config import load_config

from fakes import make_config


def test_builtin_search_defaults_on_for_bare_config(tmp_path):
    config = load_config(tmp_path / "absent.toml")  # no file -> DEFAULTS
    assert config.model.builtin_search is True


def test_build_client_builtin_search_follows_config(tmp_path, monkeypatch):
    monkeypatch.setenv("IMAGO_API_KEY", "test-key")
    config = make_config(tmp_path)  # model section comes from committed config.toml
    assert build_client(config.model).builtin_search is config.model.builtin_search
    flipped = replace(config, model=replace(
        config.model, builtin_search=not config.model.builtin_search))
    assert build_client(flipped.model).builtin_search is (not config.model.builtin_search)
