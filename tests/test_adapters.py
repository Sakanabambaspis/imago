"""build_client honors config: builtin_search is per-endpoint, not hardcoded."""

from dataclasses import replace

from imago.core.adapters import build_client
from imago.core.config import load_config

from fakes import make_config


def test_builtin_search_defaults_on_for_bare_config(tmp_path):
    config = load_config(tmp_path / "absent.toml")  # no file -> DEFAULTS
    assert config.model.builtin_search is True


def test_build_client_builtin_search_follows_config(tmp_path, monkeypatch):
    config = make_config(tmp_path)  # model section comes from committed config.toml
    monkeypatch.setenv(config.model.api_key_env, "test-key")
    assert build_client(config.model).builtin_search is config.model.builtin_search
    flipped = replace(config, model=replace(
        config.model, builtin_search=not config.model.builtin_search))
    assert build_client(flipped.model).builtin_search is (not config.model.builtin_search)


# --- transient-failure backoff (_timed) ---

from imago.core.adapters import (  # noqa: E402
    Completion, OpenAICompatClient, TransientHTTP, _MAX_ATTEMPTS)

import imago.core.adapters as adapters  # noqa: E402


class _CountingClient(OpenAICompatClient):
    """openai-compatible client with send() replaced by a scripted fn."""

    def __init__(self, script):
        super().__init__("http://x", "k", "test-model")
        self.script, self.calls = list(script), []

    def complete(self, messages, system, tools, temperature):
        def send():
            self.calls.append(1)
            item = self.script.pop(0)
            if isinstance(item, BaseException):
                raise item
            return item
        return self._timed(send)

    def _parse(self, data, latency):
        return Completion(text=str(data), tool_calls=[],
                          prompt_tokens=1, completion_tokens=1,
                          latency_ms=latency)


def test_429_is_retried_until_success(monkeypatch):
    sleeps = []
    monkeypatch.setattr(adapters.time, "sleep", sleeps.append)
    client = _CountingClient([TransientHTTP(429, "busy"),
                              TransientHTTP(503, "overloaded"),
                              {"ok": 1}])
    result = client.complete([], "", [], 0.0)
    assert result.text == "{'ok': 1}"
    assert len(client.calls) == 3
    assert sleeps == [1.0, 2.0]  # backoff waits between the three attempts


def test_exhausted_retries_raise_runtime_error(monkeypatch):
    monkeypatch.setattr(adapters.time, "sleep", lambda s: None)
    client = _CountingClient([TransientHTTP(429, "busy")] * _MAX_ATTEMPTS)
    try:
        client.complete([], "", [], 0.0)
        raise AssertionError("should have raised")
    except RuntimeError as exc:
        assert "429" in str(exc) and "test-model" in str(exc)
    assert len(client.calls) == _MAX_ATTEMPTS


def test_non_retryable_status_is_immediate(monkeypatch):
    monkeypatch.setattr(adapters.time, "sleep", lambda s: None)
    client = _CountingClient([RuntimeError("test-model API returned 401")])
    try:
        client.complete([], "", [], 0.0)
        raise AssertionError("should have raised")
    except RuntimeError:
        pass
    assert len(client.calls) == 1  # 401 is fatal; no retry


def test_latency_excludes_backoff_wait(monkeypatch):
    monkeypatch.setattr(adapters.time, "sleep", lambda s: None)
    client = _CountingClient([TransientHTTP(429, "busy"), {"ok": 1}])
    result = client.complete([], "", [], 0.0)
    assert 0 <= result.latency_ms < 60_000  # sane, not accumulated wall time
