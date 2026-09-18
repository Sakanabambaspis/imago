"""Tests for the stdlib .env loader (ADR-0005 convenience mechanism)."""

import os
from pathlib import Path

from imago.core.config import load_dotenv


def test_loads_key_and_strips_quotes(tmp_path, monkeypatch):
    monkeypatch.delenv("IMAGO_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text(
        "# comment\n"
        "\n"
        'export IMAGO_API_KEY="sk-test-123"\n'
        "PLAIN=value\n",
        encoding="utf-8")
    load_dotenv(env)
    assert os.environ["IMAGO_API_KEY"] == "sk-test-123"
    assert os.environ["PLAIN"] == "value"


def test_real_environment_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("IMAGO_API_KEY", "from-shell")
    env = tmp_path / ".env"
    env.write_text("IMAGO_API_KEY=from-file\n", encoding="utf-8")
    load_dotenv(env)
    assert os.environ["IMAGO_API_KEY"] == "from-shell"


def test_unquoted_inline_comment_is_dropped(tmp_path, monkeypatch):
    monkeypatch.delenv("IMAGO_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text("IMAGO_API_KEY=sk-real # not this\n", encoding="utf-8")
    load_dotenv(env)
    assert os.environ["IMAGO_API_KEY"] == "sk-real"


def test_missing_file_is_a_no_op(tmp_path):
    load_dotenv(tmp_path / "absent.env")  # must not raise
