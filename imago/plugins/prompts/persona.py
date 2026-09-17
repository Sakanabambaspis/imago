"""Persona module: the directness spec comes from the active voice profile."""

class Persona:
    name = "persona"
    truncated = False

    def __init__(self, config, profile, positions):
        self.text = profile.persona

    def render(self, host) -> str:
        return self.text.strip()
