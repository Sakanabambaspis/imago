"""Constitution module: renders ledger positions into a compact, capped block.

The cap (spec-stance §2) is a real constraint: breadth belongs in later
signature/memory layers, not in constitutional bloat. Over-cap sessions get a
truncated block and a flag on the prompt_assembled event, never a silent
oversized prompt.
"""

from ...core.ledger import Position

CONSTITUTION_TOKEN_CAP = 1500
CHARS_PER_TOKEN = 4

_STYLES = {
    "imperative": {
        "header": "Positions you hold. Do not abandon these unless presented "
                  "with evidence you did not have before; insistence is not evidence.",
        "entry": "- [{id}] {statement} (confidence: {confidence})",
    },
    "self-description": {
        "header": "Positions I hold, and the standard I hold them to: I change "
                  "my mind on evidence I had not seen, never on pressure.",
        "entry": "- [{id}] I hold that {statement}",
    },
}

COMPACT_HEADER = "Constitution re-anchor — your held positions:"


def render_positions(positions: list[Position], style: str,
                     compact: bool = False, token_cap: int = CONSTITUTION_TOKEN_CAP,
                     max_ids: list[str] | None = None) -> tuple[str, bool]:
    """Returns (block, truncated). compact=True keeps one line per position."""
    spec = _STYLES.get(style, _STYLES["imperative"])
    selected = ([p for p in positions if p.id in max_ids] if max_ids else positions)
    if not selected:
        return "", False
    header = COMPACT_HEADER if compact else spec["header"]
    lines = [header, ""]
    budget = token_cap * CHARS_PER_TOKEN - len(header)
    truncated = False
    for p in selected:
        entry = spec["entry"].format(id=p.id, statement=p.statement,
                                     confidence=p.confidence)
        if not compact:
            entry += f"\n  basis: {p.ground_truth_ref}"
        if budget - len(entry) < 0:
            truncated = True
            lines.append("- [ ... remaining positions omitted (constitution cap) ]")
            break
        lines.append(entry)
        budget -= len(entry)
    return "\n".join(lines), truncated


class Constitution:
    name = "constitution"

    def __init__(self, config, profile, positions):
        self.positions = positions
        self.style = profile.constitution_style
        self.truncated = False

    def render(self, host) -> str:
        block, truncated = render_positions(self.positions, self.style)
        self.truncated = truncated
        return block
