"""Stance loop: draft -> concession detect -> verdict -> respond.

Ordering is the whole point (verdict-before-accommodation): user pressure
never reaches the user as agreement without passing the check. The verdict
pass and the concession gate are the same model as the draft — single-model
two-pass arbitration, not a separate ego agent.
"""

from dataclasses import dataclass

from ...core.ledger import append_revision_request, match_positions
from ..loops.plain import PlainLoop
from ...judges.llm import judge_concession_detect, judge_verdict


@dataclass
class Verdict:
    verdict: str       # hold | concede_with_evidence | revise_position_request
    citation: str


class StanceLoop(PlainLoop):
    name = "stance"

    def run_turn(self, host, user_content: str) -> str:
        draft = super().run_turn(host, user_content)
        matched = match_positions(host.positions, user_content + "\n" + draft)
        if not matched:
            return draft

        conceded = judge_concession_detect(host.client, draft, user_content,
                                           matched, purpose_tag=judge_tag(host))
        host.emit("concession_detected", "judge", {
            "domains": sorted({p.domain for p in matched}),
            "conceded": conceded,
        })
        if not conceded:
            return draft

        verdict = judge_verdict(host.client, draft, user_content, matched,
                                purpose_tag=judge_tag(host))
        host.emit("verdict", "judge", {"verdict": verdict.verdict,
                                       "citation": verdict.citation})
        reply = _resolve(host, draft, user_content, matched, verdict)
        return _with_marker(host, reply, verdict)


def judge_tag(host) -> str:
    # Chat judges tag as "judge"; probe runs (P1/P2) keep the probe tag so all
    # spend of an instrument run is attributable to it.
    return "probe" if host.purpose_tag == "probe" else "judge"


def _resolve(host, draft, user_content, matched, verdict: Verdict) -> str:
    if verdict.verdict == "hold":
        from ...judges.llm import rewrite_to_hold
        return rewrite_to_hold(host.client, draft, user_content,
                               matched[0], verdict, purpose_tag=host.purpose_tag)
    if verdict.verdict == "revise_position_request":
        append_revision_request(
            host.config.paths.queue_path, matched[0].id,
            evidence=f"draft: {draft[:500]} | citation: {verdict.citation}")
        return draft
    return draft  # concede_with_evidence: the draft already carries the evidence


def _with_marker(host, reply: str, verdict: Verdict) -> str:
    if not (host.config.session.verdict_marker and host.profile.verdict_marker):
        return reply
    return f"{reply}\n\n[imago: {verdict.verdict.replace('_', ' ')} — {verdict.citation}]"
