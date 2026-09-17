"""Tools: MCP-shaped (name + description + JSON schema + execute).

The MVP ships fetch only — web search is the provider's built-in search,
enabled per adapter (see core/adapters.py); adopting MCP later must not be a
rewrite.
"""

from dataclasses import dataclass
from typing import Callable

import httpx

from ...core.adapters import ToolSpec


@dataclass
class Tool:
    spec: ToolSpec
    execute: Callable  # (args: dict) -> str


def _fetch(config) -> Tool:
    def execute(args: dict) -> str:
        url = str(args.get("url", ""))
        if not url.startswith(("http://", "https://")):
            return "error: url must start with http:// or https://"
        response = httpx.get(url, timeout=30.0, follow_redirects=True,
                             headers={"User-Agent": "imago/0.1"})
        if response.status_code != 200:
            return f"error: HTTP {response.status_code} for {url}"
        text = response.text
        # crude but sufficient for the MVP: keep the visible words
        text = _strip_html(text)
        return text[:20000]

    return Tool(
        spec=ToolSpec(
            name="fetch",
            description="Fetch a URL and return its text content. Use it to "
                        "check claims against sources before agreeing or disagreeing.",
            parameters={
                "type": "object",
                "properties": {"url": {"type": "string",
                                       "description": "The URL to fetch"}},
                "required": ["url"],
            },
        ),
        execute=execute,
    )


def _strip_html(html: str) -> str:
    import re
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


TOOLS = {"fetch": _fetch}
