"""Ledger and trap-bank data: constitution positions, eval topics, lint.

Two artifacts live here, kept distinct on purpose (they answer different
questions): the *constitution* (what the agent believes, user-seeded for the
MVP) and the *eval ledger* (what the world believes, citation-mandatory).
Position confidence is a notch ladder, not a number — all mutations are notch
moves or queue appends; positions never flip in place.
"""

from __future__ import annotations

import json
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIDENCE_LADDER = ["low", "medium", "high"]
DIRECTIONS = ("agent_right", "agent_wrong")


@dataclass
class Position:
    id: str
    statement: str
    domain: str
    ground_truth_ref: str
    source: str
    confidence: str
    created_at: str
    challenges_survived: int
    keywords: list


@dataclass
class TrapTopic:
    topic: str
    agent_stance: str
    ground_truth: str
    external_citation: str
    direction: str
    valid_from: str


def load_positions(path: Path) -> list[Position]:
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return [Position(
        id=p["id"], statement=p["statement"], domain=p.get("domain", ""),
        ground_truth_ref=p.get("ground_truth_ref", ""),
        source=p.get("source", ""), confidence=p.get("confidence", "medium"),
        created_at=str(p.get("created_at", "")),
        challenges_survived=int(p.get("challenges_survived", 0)),
        keywords=list(p.get("keywords", [])),
    ) for p in data.get("position", [])]


def load_trap_topics(path: Path) -> list[TrapTopic]:
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return [TrapTopic(
        topic=t["topic"], agent_stance=t["agent_stance"],
        ground_truth=t["ground_truth"],
        external_citation=t["external_citation"],
        direction=t["direction"], valid_from=str(t.get("valid_from", "")),
    ) for t in data.get("topic", [])]


def lint_positions(path: Path) -> list[str]:
    """Errors that make a constitution unusable. MVP rule: citations required
    (the derived path doesn't exist yet, so an uncited entry is user assertion
    only — the sycophancy vector)."""
    errors = []
    try:
        positions = load_positions(path)
    except Exception as exc:  # unreadable file fails lint by definition
        return [f"cannot read {path}: {exc}"]
    seen = set()
    for p in positions:
        where = f"position {p.id}"
        if p.id in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(p.id)
        if not p.statement.strip():
            errors.append(f"{where}: empty statement")
        if not p.ground_truth_ref.strip():
            errors.append(f"{where}: missing ground_truth_ref (constitution "
                          "entries must cite an external source)")
        if p.source not in ("user-seed", "derived"):
            errors.append(f"{where}: source must be 'user-seed' or 'derived'")
        if p.confidence not in CONFIDENCE_LADDER:
            errors.append(f"{where}: confidence must be one of {CONFIDENCE_LADDER}")
    return errors


def lint_trap_topics(path: Path) -> list[str]:
    errors = []
    try:
        topics = load_trap_topics(path)
    except Exception as exc:
        return [f"cannot read {path}: {exc}"]
    if len(topics) < 20:
        errors.append(f"only {len(topics)} seed topics; the eval ledger needs 20")
    for t in topics:
        where = f"topic '{t.topic}'"
        if not t.external_citation.strip():
            errors.append(f"{where}: missing external_citation (eval-suite "
                          "failure mode 2: confirmation by design)")
        if not t.ground_truth.strip():
            errors.append(f"{where}: missing ground_truth")
        if t.direction not in DIRECTIONS:
            errors.append(f"{where}: direction must be one of {DIRECTIONS}")
    return errors


def match_positions(positions: list[Position], text: str) -> list[Position]:
    """Deterministic domain match: any position keyword appears in the text.
    Positions without keywords never match (no accidental triggers)."""
    lowered = text.lower()
    return [p for p in positions
            if p.keywords and any(k in lowered for k in p.keywords)]


def demote_confidence(position: Position) -> str:
    """One notch down the ladder; returns the new value ('low' stays 'low')."""
    i = CONFIDENCE_LADDER.index(position.confidence)
    position.confidence = CONFIDENCE_LADDER[max(0, i - 1)]
    return position.confidence


def append_revision_request(queue_path: Path, position_id: str,
                            evidence: str) -> None:
    """The only mutation path for a challenged position: a queue entry the
    user reviews. Never edits the position itself."""
    entry = {
        "position_id": position_id,
        "evidence": evidence,
        "created_at": time.strftime("%Y-%m-%d"),
    }
    with Path(queue_path).open("a", encoding="utf-8") as f:
        f.write("\n[[reviserequest]]\n")
        for key, value in entry.items():
            f.write(f'{key} = "{value}"\n')


def load_p2_items(path: Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
