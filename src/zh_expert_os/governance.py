from __future__ import annotations

from .models import MatchRecord, QualityScores
from .scoring import promotion_recommendation


def build_personnel_case(
    match: MatchRecord,
    scores: QualityScores,
) -> dict:
    rec = promotion_recommendation(match, scores)
    return {
        "case_type": "expert_challenge",
        "challenger": match.challenger,
        "incumbent": match.incumbent,
        "evidence": {
            "wins": match.wins,
            "losses": match.losses,
            "ties": match.ties,
            "quality": rec["quality"],
            "posterior": rec["posterior"],
        },
        "cao_recommendation": rec["action"],
        "blockers": rec["blockers"],
        "audit_required": rec["requires_auditor"],
        "human_approval_required": rec["requires_human_approval"],
        "rollback": f"若晋升后出现回归，将 {match.challenger} 调回 probation / bench，并召回 {match.incumbent}。",
    }
