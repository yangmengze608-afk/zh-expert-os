from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

ExpertStatus = Literal["candidate", "probation", "active", "bench", "retired", "governance"]
BattleStatus = Literal["collecting", "judging", "finalized"]
PresentationOrder = Literal["AB", "BA"]


@dataclass(slots=True)
class Expert:
    id: str
    name_zh: str
    version: str
    status: ExpertStatus
    role: str
    source: str
    license: str
    mission: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class QualityScores:
    task_quality: float
    factuality: float
    stability: float
    independence: float
    cost_efficiency: float
    user_adoption: float
    critical_violations: int = 0

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if name == "critical_violations":
                if value < 0:
                    raise ValueError("critical_violations 不能小于 0")
                continue
            if not 0 <= value <= 1:
                raise ValueError(f"{name} 必须在 [0, 1] 范围内")


@dataclass(slots=True)
class MatchRecord:
    challenger: str
    incumbent: str
    wins: int
    losses: int
    ties: int = 0
    source_battle_id: str | None = None

    @property
    def decisive(self) -> int:
        return self.wins + self.losses

    @property
    def total(self) -> int:
        return self.wins + self.losses + self.ties


@dataclass(slots=True)
class ArenaTask:
    id: str
    prompt: str
    category: str = "general"
    risk_level: str = "normal"

    def validate(self) -> None:
        if not self.id.strip():
            raise ValueError("ArenaTask.id 不能为空")
        if not self.prompt.strip():
            raise ValueError("ArenaTask.prompt 不能为空")

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)


@dataclass(slots=True)
class JudgeScores:
    task_completion: float
    factuality: float
    evidence_quality: float
    chinese_native: float
    clarity: float
    critical_violations: int = 0

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if name == "critical_violations":
                if value < 0:
                    raise ValueError("critical_violations 不能小于 0")
                continue
            if not 0 <= value <= 1:
                raise ValueError(f"{name} 必须在 [0, 1] 范围内")


@dataclass(slots=True)
class ArenaJudgment:
    battle_id: str
    judge_id: str
    presentation_order: PresentationOrder
    score_a: JudgeScores
    score_b: JudgeScores
    rationale: str = ""

    def validate(self) -> None:
        if not self.battle_id.strip() or not self.judge_id.strip():
            raise ValueError("battle_id / judge_id 不能为空")
        if self.presentation_order not in {"AB", "BA"}:
            raise ValueError("presentation_order 必须为 AB 或 BA")
        self.score_a.validate()
        self.score_b.validate()

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ArenaJudgment":
        return cls(
            battle_id=data["battle_id"],
            judge_id=data["judge_id"],
            presentation_order=data["presentation_order"],
            score_a=JudgeScores(**data["score_a"]),
            score_b=JudgeScores(**data["score_b"]),
            rationale=data.get("rationale", ""),
        )
