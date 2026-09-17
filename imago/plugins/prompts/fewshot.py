"""Few-shot module: curated disagreement exchanges from the voice profile."""

class Fewshot:
    name = "fewshot"
    truncated = False

    def __init__(self, config, profile, positions):
        self.exchanges = profile.fewshot[:8]

    def render(self, host) -> str:
        if not self.exchanges:
            return ""
        lines = ["How you handle pushback (example exchanges):"]
        for ex in self.exchanges:
            lines.append(f"User: {ex['user']}\nYou: {ex['assistant']}")
        return "\n\n".join(lines)
