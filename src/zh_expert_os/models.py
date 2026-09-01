from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

ExpertStatus = Literal["candidate", "probation", "active", "bench", "retired", "governance"]


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

    @property
    def decisive(self) -> int:
        return self.wins + self.losses

    @property
    def total(self) -> int:
        return self.wins + self.losses + self.ties
