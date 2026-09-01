from __future__ import annotations

import random
from dataclasses import asdict

from .models import MatchRecord, QualityScores

DEFAULT_WEIGHTS = {
    "task_quality": 0.30,
    "factuality": 0.25,
    "stability": 0.15,
    "independence": 0.10,
    "cost_efficiency": 0.10,
    "user_adoption": 0.10,
}


def weighted_quality(scores: QualityScores, weights: dict[str, float] | None = None) -> float:
    scores.validate()
    weights = weights or DEFAULT_WEIGHTS
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("评分权重之和必须为 1")
    raw = asdict(scores)
    return sum(float(raw[k]) * w for k, w in weights.items())


def posterior_summary(
    match: MatchRecord,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    threshold: float = 0.5,
    samples: int = 30000,
    seed: int = 20260901,
) -> dict[str, float]:
    """Beta-Binomial 后验。

    ties 暂不进入胜负似然，但保留在总样本信息中。
    用固定 seed 的 Monte Carlo 估计 P(p > threshold)，保证 CLI 结果可复现。
    """
    if min(match.wins, match.losses, match.ties) < 0:
        raise ValueError("胜 / 负 / 平局次数不能为负")
    if samples < 1000:
        raise ValueError("samples 至少为 1000")

    alpha = prior_alpha + match.wins
    beta = prior_beta + match.losses
    mean = alpha / (alpha + beta)

    rng = random.Random(seed)
    exceed = 0
    draws = []
    for _ in range(samples):
        x = rng.betavariate(alpha, beta)
        draws.append(x)
        if x > threshold:
            exceed += 1
    draws.sort()
    lo = draws[int(samples * 0.025)]
    hi = draws[min(samples - 1, int(samples * 0.975))]

    return {
        "alpha": alpha,
        "beta": beta,
        "posterior_mean": mean,
        "prob_gt_threshold": exceed / samples,
        "credible_95_low": lo,
        "credible_95_high": hi,
    }


def promotion_recommendation(
    match: MatchRecord,
    challenger_scores: QualityScores,
    *,
    min_total_tasks: int = 20,
    min_decisive_tasks: int = 12,
    min_quality: float = 0.80,
    min_factuality: float = 0.85,
    min_stability: float = 0.75,
    min_prob_better: float = 0.95,
) -> dict:
    quality = weighted_quality(challenger_scores)
    posterior = posterior_summary(match)

    blockers: list[str] = []
    if match.total < min_total_tasks:
        blockers.append(f"总盲测任务不足：{match.total} < {min_total_tasks}")
    if match.decisive < min_decisive_tasks:
        blockers.append(f"有效胜负样本不足：{match.decisive} < {min_decisive_tasks}")
    if quality < min_quality:
        blockers.append(f"综合质量不足：{quality:.3f} < {min_quality:.3f}")
    if challenger_scores.factuality < min_factuality:
        blockers.append(f"事实性不足：{challenger_scores.factuality:.3f} < {min_factuality:.3f}")
    if challenger_scores.stability < min_stability:
        blockers.append(f"稳定性不足：{challenger_scores.stability:.3f} < {min_stability:.3f}")
    if challenger_scores.critical_violations > 0:
        blockers.append(f"存在严重违规 / 致命错误：{challenger_scores.critical_violations}")
    if posterior["prob_gt_threshold"] < min_prob_better:
        blockers.append(
            "胜过现任的后验概率不足："
            f"{posterior['prob_gt_threshold']:.3f} < {min_prob_better:.3f}"
        )

    if not blockers:
        action = "PROMOTE"
    elif challenger_scores.critical_violations > 0:
        action = "REJECT"
    elif quality >= 0.70 and challenger_scores.factuality >= 0.75:
        action = "EXTEND_PROBATION"
    else:
        action = "REJECT"

    return {
        "action": action,
        "quality": quality,
        "posterior": posterior,
        "blockers": blockers,
        "requires_auditor": action == "PROMOTE",
        "requires_human_approval": action == "PROMOTE",
    }
