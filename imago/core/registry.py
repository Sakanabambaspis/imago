"""Plugin registry: registration tables, not ordered chains.

Every plugin kind is claimed by name in a dict; config selects members. Empty
lists in config mean the capability is absent — that is the subtraction test,
not a special case.
"""

from ..plugins.hooks import HOOKS
from ..plugins.loops import LOOPS
from ..plugins.prompts import PROMPT_MODULES
from ..plugins.tools import TOOLS


def build_loop(name):
    if name not in LOOPS:
        raise SystemExit(f"Unknown loop '{name}'. Available: {', '.join(LOOPS)}")
    return LOOPS[name]


def build_hooks(config, names):
    hooks = []
    for name in names:
        if name not in HOOKS:
            raise SystemExit(
                f"Unknown hook '{name}'. Available: {', '.join(HOOKS)}")
        hooks.append(HOOKS[name](config))
    return hooks


def build_prompt_modules(config, names, profile, positions):
    modules = []
    for name in names:
        if name not in PROMPT_MODULES:
            raise SystemExit(f"Unknown prompt module '{name}'. Available: "
                             f"{', '.join(PROMPT_MODULES)}")
        modules.append(PROMPT_MODULES[name](config, profile, positions))
    return modules


def build_tools(config, names):
    tools = []
    for name in names:
        if name not in TOOLS:
            raise SystemExit(
                f"Unknown tool '{name}'. Available: {', '.join(TOOLS)}")
        tools.append(TOOLS[name](config))
    return tools
