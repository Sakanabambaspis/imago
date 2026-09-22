"""Provider adapters: OpenAI-compatible (GLM, OpenAI, OpenRouter, vLLM, ...)
and Anthropic native. Both speak the same narrow `ModelClient` interface, and
both translate Imago's tool set into their native wire format, including the
provider's built-in web search when available (capability flag).

Simplification, deliberate for the MVP: multi-round tool use passes tool
results back as plain text in a follow-up call, so the loop above this layer
stays provider-neutral.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Protocol

import httpx

TIMEOUT = httpx.Timeout(120.0)

_MAX_ATTEMPTS = 5
_BACKOFF_BASE_S = 1.0
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


class TransientHTTP(Exception):
    """Retryable endpoint condition (rate limit, overload)."""

    def __init__(self, status: int, body: str):
        self.status, self.body = status, body
        super().__init__(f"HTTP {status}: {body}")


@dataclass
class ToolSpec:
    """MCP-shaped tool description (name + description + JSON schema)."""
    name: str
    description: str
    parameters: dict  # JSON schema


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class Completion:
    text: str
    tool_calls: list  # list[ToolCall]
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int


class ModelClient(Protocol):
    def complete(self, messages: list, system: str, tools: list,
                 temperature: float) -> Completion: ...


class _BaseClient:
    """Shared: optional built-in web search marker + request plumbing."""

    builtin_search = False

    def _timed(self, send) -> Completion:
        """Send with bounded exponential backoff on transient failures.

        Free-tier endpoints 429 under load; a wave is ~hundreds of serial
        calls, so a single unhandled 429 kills it. Reported latency_ms is
        the successful attempt's only — backoff waits are not request latency.
        """
        for attempt in range(_MAX_ATTEMPTS):
            if attempt:
                time.sleep(_BACKOFF_BASE_S * 2 ** (attempt - 1))
            t0 = time.monotonic()
            try:
                data = send()
            except TransientHTTP as exc:
                if attempt == _MAX_ATTEMPTS - 1:
                    raise RuntimeError(
                        f"{self.model} API returned {exc.status} on all "
                        f"{_MAX_ATTEMPTS} attempts: {exc.body}") from exc
                continue
            return self._parse(data, int((time.monotonic() - t0) * 1000))
        raise AssertionError("unreachable")  # pragma: no cover

    def _parse(self, data: dict, latency: int) -> Completion:  # pragma: no cover
        raise NotImplementedError


class OpenAICompatClient(_BaseClient):
    """Any endpoint speaking POST {base_url}/chat/completions (GLM default)."""

    def __init__(self, base_url: str, api_key: str, model: str,
                 builtin_search: bool = False):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.builtin_search = builtin_search

    def complete(self, messages, system, tools, temperature) -> Completion:
        body: dict = {
            "model": self.model,
            "messages": ([{"role": "system", "content": system}] if system else [])
                        + list(messages),
            "temperature": temperature,
        }
        if tools or self.builtin_search:
            body["tools"] = [
                {"type": "function", "function": {
                    "name": t.name, "description": t.description,
                    "parameters": t.parameters}} for t in tools]
            if self.builtin_search:
                # Zhipu/GLM server-side web search.
                body["tools"].append(
                    {"type": "web_search", "web_search": {"enable": True}})
        request = {
            "method": "POST",
            "url": f"{self.base_url}/chat/completions",
            "headers": {"Authorization": f"Bearer {self.api_key}"},
            "json": body,
        }

        def send():
            with httpx.Client(timeout=TIMEOUT) as http:
                response = http.request(**request)
            if response.status_code in _RETRYABLE_STATUS:
                raise TransientHTTP(response.status_code, response.text[:300])
            if response.status_code != 200:
                raise RuntimeError(
                    f"{self.model} API returned {response.status_code}: "
                    f"{response.text[:300]}")
            return response.json()

        return self._timed(send)

    def _parse(self, data: dict, latency: int) -> Completion:
        message = data["choices"][0]["message"]
        calls = [ToolCall(id=c["id"], name=c["function"]["name"],
                          arguments=json.loads(c["function"]["arguments"] or "{}"))
                 for c in message.get("tool_calls") or []]
        usage = data.get("usage") or {}
        return Completion(text=message.get("content") or "", tool_calls=calls,
                          prompt_tokens=int(usage.get("prompt_tokens", 0)),
                          completion_tokens=int(usage.get("completion_tokens", 0)),
                          latency_ms=latency)


class AnthropicClient(_BaseClient):
    builtin_search = False  # enabled via constructor flag

    def __init__(self, api_key: str, model: str, builtin_search: bool = False):
        self.api_key = api_key
        self.model = model
        self.builtin_search = builtin_search

    def complete(self, messages, system, tools, temperature) -> Completion:
        body: dict = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": temperature,
            "messages": list(messages),
        }
        if system:
            body["system"] = system
        wire_tools = [{"name": t.name, "description": t.description,
                       "input_schema": t.parameters} for t in tools]
        if self.builtin_search:
            wire_tools.append(
                {"type": "web_search_20250305", "name": "web_search"})
        if wire_tools:
            body["tools"] = wire_tools
        request = {
            "method": "POST",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {"x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"},
            "json": body,
        }

        def send():
            with httpx.Client(timeout=TIMEOUT) as http:
                response = http.request(**request)
            if response.status_code in _RETRYABLE_STATUS:
                raise TransientHTTP(response.status_code, response.text[:300])
            if response.status_code != 200:
                raise RuntimeError(
                    f"{self.model} API returned {response.status_code}: "
                    f"{response.text[:300]}")
            return response.json()

        return self._timed(send)

    def _parse(self, data: dict, latency: int) -> Completion:
        text_parts, calls = [], []
        for block in data.get("content", []):
            if block.get("type") == "text":
                text_parts.append(block["text"])
            elif block.get("type") == "tool_use":
                calls.append(ToolCall(id=block["id"], name=block["name"],
                                      arguments=block.get("input") or {}))
        usage = data.get("usage") or {}
        return Completion(text="".join(text_parts), tool_calls=calls,
                          prompt_tokens=int(usage.get("input_tokens", 0)),
                          completion_tokens=int(usage.get("output_tokens", 0)),
                          latency_ms=latency)


def build_client(model_cfg) -> ModelClient:
    """Factory: env-provided key, pinned model, provider adapter.

    The one place an API key problem becomes an error, with instructions.
    """
    key = os.environ.get(model_cfg.api_key_env, "")
    if not key:
        raise SystemExit(
            f"Missing API key: set {model_cfg.api_key_env} "
            f"(export {model_cfg.api_key_env}=... or put it in a local .env — "
            "see .env.example). The key is read from the environment only; "
            "it is never stored in config or code.")
    # Server-side search is a per-endpoint extension (Zhipu-style web_search,
    # Anthropic web_search); endpoints without it reject the tool, so it's config.
    enable_search = model_cfg.builtin_search
    if model_cfg.provider == "openai-compatible":
        return OpenAICompatClient(model_cfg.base_url, key, model_cfg.name,
                                  builtin_search=enable_search)
    if model_cfg.provider == "anthropic":
        return AnthropicClient(key, model_cfg.name, builtin_search=enable_search)
    raise SystemExit(
        f"Unknown provider '{model_cfg.provider}'. "
        "Use 'openai-compatible' (any OpenAI-shaped endpoint) or 'anthropic'.")
