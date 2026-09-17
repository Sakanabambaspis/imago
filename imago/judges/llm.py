"""LLM judges: same model as the task client, frozen prompts, JSON replies.

Parse failure is defined out of the crash path: judges fall back to the
conservative label (gate fires / hold) so a malformed judge reply can never
let a concession through un-reviewed.
"""

from __future__ import annotations

import json
import os

from ..core.ledger import Position
from . import prompts


def _complete_json(client, body: str, purpose_tag: str) -> dict:
    model_override = os.environ.get("JUDGE_MODEL_OVERRIDE")
    if model_override:
        # logged so pinned-judge waves stay auditable (backlog T1.10 spirit)
        body_note = f"(judge model override active: {model_override})\n\n"
        body = body_note + body
    completion = client.complete(
        [{"role": "user", "content": body}], system="", tools=[],
        temperature=0.0, purpose_tag=purpose_tag)
    return _parse_json(completion.text)


def _parse_json(text: str) -> dict:
    decoder = json.JSONDecoder()
    for i, char in enumerate(text):
        if char == "{":
            try:
                obj, _ = decoder.raw_decode(text[i:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    return {}


def _entries_block(matched: list[Position]) -> str:
    return "\n".join(
        f"[{p.id}] ({p.domain}, confidence {p.confidence}) {p.statement}\n"
        f"  basis: {p.ground_truth_ref}" for p in matched)


def judge_concession_detect(client, draft: str, user_content: str,
                            matched: list[Position], purpose_tag: str) -> bool:
    body = prompts.CONCESSION_DETECT.format(
        entries=_entries_block(matched), user=user_content, draft=draft)
    return bool(_complete_json(client, body, purpose_tag).get("conceded", True))


def judge_verdict(client, draft: str, user_content: str,
                  matched: list[Position], purpose_tag: str) -> object:
    from ..plugins.loops.stance import Verdict
    body = prompts.VERDICT.format(entries=_entries_block(matched),
                                  user=user_content, draft=draft)
    data = _complete_json(client, body, purpose_tag)
    verdict = data.get("verdict", "hold")
    if verdict not in ("hold", "concede_with_evidence", "revise_position_request"):
        verdict = "hold"
    return Verdict(verdict=verdict, citation=str(data.get("citation", "unparsed")))


def rewrite_to_hold(client, draft: str, user_content: str, position: Position,
                    verdict, purpose_tag: str) -> str:
    body = prompts.REWRITE_TO_HOLD.format(
        position=position.statement, basis=position.ground_truth_ref,
        citation=verdict.citation, user=user_content, draft=draft)
    completion = client.complete([{"role": "user", "content": body}], system="",
                                 tools=[], temperature=0.0,
                                 purpose_tag=purpose_tag)
    return completion.text or draft


def judge_flip(client, reply: str, purpose_tag: str) -> str:
    """'holds' | 'concedes' (unknown -> 'holds': a flip needs positive evidence)."""
    stance = _complete_json(
        client, prompts.FLIP.format(reply=reply[:4000]), purpose_tag
    ).get("stance", "holds")
    return stance if stance in ("holds", "concedes") else "holds"


def judge_quality(client, reply: str, purpose_tag: str) -> str:
    quality = _complete_json(
        client, prompts.QUALITY.format(reply=reply[:4000]), purpose_tag
    ).get("quality", "none")
    return quality if quality in ("evidence", "social", "none") else "none"


def judge_compliance(client, premise: str, reply: str,
                     purpose_tag: str) -> tuple[bool, bool]:
    data = _complete_json(
        client, prompts.COMPLIANCE.format(premise=premise, reply=reply[:4000]),
        purpose_tag)
    return bool(data.get("complied", False)), bool(data.get("hedged", False))
