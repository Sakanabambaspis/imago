"""Prompt modules: pieces of the system prompt, each a plugin.

A module is constructed once per session with (config, profile, positions)
and renders itself via render(host). Modules may set self.truncated; the
session host records it on prompt_assembled.
"""

from .constitution import Constitution
from .fewshot import Fewshot
from .persona import Persona

PROMPT_MODULES = {
    "persona": Persona,
    "fewshot": Fewshot,
    "constitution": Constitution,
}
