from __future__ import annotations

import hashlib
from dataclasses import asdict
from statistics import mean

from .models import ArenaJudgment, ArenaTask, JudgeScores

ARENA_WEIGHTS = {
    "task_completion": 0.25,
    "factuality": 0.30,
    "evidence_quality": 0.20,
    "chinese_native": 0.15,
    "clarity": 0.10,
}


def task_fingerprint(task: ArenaTask) -> str:
    task.validate()
    normalized = "\n".join(line.rstrip() for line in task.prompt.strip().splitlines())
    payload = f"{task.id}\n{task.category}\n{task.risk_level}\n{normalized}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _coin(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16) % 2


def alias_assignment(battle_id: str, challenger: str, incumbent: str) -> dict[str, str]:
    if challenger == incumbent:
        raise ValueError("挑战者和现任不能是同一个专家")
    if _coin(f"alias:{battle_id}:{challenger}:{incumbent}") == 0:
        return {"A": challenger, "B": incumbent}
    return {"A": incumbent, "B": challenger}


def expected_presentation_order(battle_id: str, judge_id: str) -> str:
    return "AB" if _coin(f"order:{battle_id}:{judge_id}") == 0 else "BA"


def judge_quality(scores: JudgeScores, weights: dict[str, float] | None = None) -> float:
    scores.validate()
    weights = weights or ARENA_WEIGHTS
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("Arena 评分权重之和必须为 1")
    raw = asdict(scores)
    return sum(float(raw[k]) * weight for k, weight in weights.items())


def judgment_preference(judgment: ArenaJudgment, tie_margin: float = 0.03) -> str:
    judgment.validate()
    a_bad = judgment.score_a.critical_violations
    b_bad = judgment.score_b.critical_violations
    if a_bad != b_bad:
        return "A" if a_bad < b_bad else "B"
    qa = judge_quality(judgment.score_a)
    qb = judge_quality(judgment.score_b)
    if abs(qa - qb) < tie_margin:
        return "TIE"
    return "A" if qa > qb else "B"


def aggregate_judgments(
    judgments: list[ArenaJudgment],
    *,
    min_judges: int = 3,
    min_majority_share: float = 0.60,
    min_mean_gap: float = 0.03,
) -> dict:
    if len(judgments) < min_judges:
        return {
            "ready": False,
            "reason": f"Judge 数量不足：{len(judgments)} < {min_judges}",
            "judge_count": len(judgments),
        }

    seen = set()
    for j in judgments:
        j.validate()
        if j.judge_id in seen:
            raise ValueError(f"Judge 重复：{j.judge_id}")
        seen.add(j.judge_id)

    prefs = [judgment_preference(j) for j in judgments]
    counts = {k: prefs.count(k) for k in ("A", "B", "TIE")}
    mean_a = mean(judge_quality(j.score_a) for j in judgments)
    mean_b = mean(judge_quality(j.score_b) for j in judgments)

    top_alias = "A" if counts["A"] > counts["B"] else "B" if counts["B"] > counts["A"] else "TIE"
    top_votes = max(counts["A"], counts["B"])
    majority_share = top_votes / len(judgments)
    mean_gap = abs(mean_a - mean_b)

    if top_alias == "TIE" or majority_share < min_majority_share or mean_gap < min_mean_gap:
        winner = "TIE"
    else:
        winner = top_alias

    decisive = 0
    first_position_wins = 0
    for j, pref in zip(judgments, prefs):
        if pref == "TIE":
            continue
        decisive += 1
        first_alias = j.presentation_order[0]
        if pref == first_alias:
            first_position_wins += 1
    first_rate = (first_position_wins / decisive) if decisive else None
    position_bias_flag = bool(decisive >= 4 and first_rate is not None and abs(first_rate - 0.5) > 0.25)

    disagreement_rate = 1.0 - (max(counts.values()) / len(judgments))
    confidence = 0.0 if winner == "TIE" else min(
        1.0,
        0.7 * max(0.0, (majority_share - 0.5) * 2) + 0.3 * min(1.0, mean_gap / 0.20),
    )

    return {
        "ready": True,
        "winner_alias": winner,
        "judge_count": len(judgments),
        "vote_counts": counts,
        "mean_score_a": mean_a,
        "mean_score_b": mean_b,
        "mean_gap": mean_gap,
        "majority_share": majority_share,
        "disagreement_rate": disagreement_rate,
        "first_position_preference_rate": first_rate,
        "position_bias_flag": position_bias_flag,
        "confidence": confidence,
    }
