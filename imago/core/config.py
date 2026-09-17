"""Configuration and voice profiles.

Config is optional: with no config.toml and no environment beyond an API key,
Imago still runs with defaults (errors are defined out of existence). The only
hard error paths are "no API key" and "unknown profile name", and both error
messages state exactly what to do.
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULTS = {
    "provider": "openai-compatible",
    "name": "glm-4.6",
    "base_url": "https://api.z.ai/api/paas/v4",
    "api_key_env": "IMAGO_API_KEY",
    "temperature": 0.7,
}


@dataclass
class Paths:
    root: Path
    profiles_dir: Path
    ledger_path: Path
    queue_path: Path
    p1_ledger_path: Path
    p2_items_path: Path
    runs_dir: Path
    results_dir: Path


@dataclass
class ModelConfig:
    provider: str
    name: str
    base_url: str
    api_key_env: str
    temperature: float
    pricing: dict = field(default_factory=dict)  # "provider/name" -> per-mtok

    @property
    def key(self) -> str:
        return f"{self.provider}/{self.name}"


@dataclass
class SessionConfig:
    loop: str = "stance"
    profile: str = "imperative"
    prompt_modules: list = field(
        default_factory=lambda: ["persona", "fewshot", "constitution"])
    hooks: list = field(default_factory=lambda: ["reinject", "reanchor"])
    reinject_every_k_turns: int = 10
    verdict_marker: bool = True


@dataclass
class EvalConfig:
    p1_topics: int = 10
    p1_seeds: int = 2
    p1_orderings: int = 2
    p1_full_topics: int = 20
    p1_full_seeds: int = 3
    p2_paraphrases: int = 4


@dataclass
class Profile:
    name: str
    persona: str
    fewshot: list  # [{user, assistant}, ...]
    constitution_style: str
    verdict_marker: bool


@dataclass
class Config:
    model: ModelConfig
    session: SessionConfig
    eval: EvalConfig
    judge_prompt_version: str
    paths: Paths


def _paths(root: Path) -> Paths:
    return Paths(
        root=root,
        profiles_dir=root / "profiles",
        ledger_path=root / "ledger" / "positions.toml",
        queue_path=root / "ledger" / "positions.toml",
        p1_ledger_path=root / "traps" / "p1" / "ledger.toml",
        p2_items_path=root / "traps" / "p2" / "factual.json",
        runs_dir=root / ".imago" / "runs",
        results_dir=root / "docs" / "results",
    )


def load_config(path: Path | None = None) -> Config:
    """Load config.toml; absent file means defaults (not an error)."""
    path = Path(path) if path else Path("config.toml")
    root = path.resolve().parent if path.exists() else Path.cwd()
    data = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    m = {**DEFAULTS, **data.get("model", {})}
    pricing = {k.replace("pricing.", "", 1): dict(v)
               for k, v in data.get("model", {}).items()
               if isinstance(v, dict) and k.startswith("pricing.")}
    s = data.get("session", {})
    session = SessionConfig(
        loop=s.get("loop", "stance"),
        profile=s.get("profile", "imperative"),
        prompt_modules=list(s.get("prompt_modules",
                                  ["persona", "fewshot", "constitution"])),
        hooks=list(s.get("hooks", ["reinject", "reanchor"])),
        reinject_every_k_turns=int(s.get("reinject_every_k_turns", 10)),
        verdict_marker=bool(s.get("verdict_marker", True)),
    )
    e = data.get("eval", {})
    p1, p2 = e.get("p1", {}), e.get("p2", {})
    eval_cfg = EvalConfig(
        p1_topics=int(p1.get("topics", 10)),
        p1_seeds=int(p1.get("seeds", 2)),
        p1_orderings=int(p1.get("orderings", 2)),
        p1_full_topics=int(p1.get("full_topics", 20)),
        p1_full_seeds=int(p1.get("full_seeds", 3)),
        p2_paraphrases=int(p2.get("paraphrases", 4)),
    )
    model = ModelConfig(
        provider=m["provider"], name=m["name"], base_url=m.get("base_url", ""),
        api_key_env=m["api_key_env"], temperature=float(m["temperature"]),
        pricing=pricing,
    )
    return Config(
        model=model, session=session, eval=eval_cfg,
        judge_prompt_version=data.get("judge", {}).get("prompt_version", "v1"),
        paths=_paths(root),
    )


def load_profile(config: Config, name: str) -> Profile:
    """Load profiles/<name>.toml plus its few-shot file."""
    path = config.paths.profiles_dir / f"{name}.toml"
    if not path.exists():
        available = sorted(p.stem for p in config.paths.profiles_dir.glob("*.toml"))
        raise SystemExit(
            f"Unknown profile '{name}'. Available: {', '.join(available)}. "
            f"Edit or add files in {config.paths.profiles_dir}/ to change the voice.")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    fewshot_path = path.parent / data.get("fewshot_file", "")
    fewshot = json.loads(fewshot_path.read_text(encoding="utf-8")) \
        if fewshot_path.exists() else []
    return Profile(
        name=name,
        persona=data.get("persona", ""),
        fewshot=fewshot,
        constitution_style=data.get("constitution_style", "imperative"),
        verdict_marker=bool(data.get("verdict_marker", True)),
    )
