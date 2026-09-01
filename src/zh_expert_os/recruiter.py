from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

GapType = Literal["expert", "skill", "tool", "knowledge", "workflow", "unknown"]
Engagement = Literal[
    "permanent_expert",
    "temporary_consultant",
    "acquire_skill",
    "connect_tool",
    "add_knowledge",
    "repair_workflow",
    "investigate",
]
SourceType = Literal["agent", "expert", "persona", "role", "skill", "playbook", "workflow", "team", "repo", "generated"]


@dataclass(slots=True)
class CapabilityGap:
    task_id: str
    task_goal: str
    capability: str
    gap_type: GapType
    reason: str
    recurrence_count: int = 1
    strategic: bool = False
    criticality: float = 0.5
    evidence: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.task_id.strip() or not self.task_goal.strip() or not self.capability.strip():
            raise ValueError("task_id、task_goal、capability 不能为空")
        if self.recurrence_count < 1:
            raise ValueError("recurrence_count 至少为 1")
        if not 0 <= self.criticality <= 1:
            raise ValueError("criticality 必须在 [0, 1]")


@dataclass(slots=True)
class CandidateAsset:
    id: str
    source_type: SourceType
    repository: str
    path: str
    license: str
    language: str
    capability_tags: list[str]
    fit_score: float
    chinese_native_score: float
    portability_score: float
    maintainability_score: float
    overlap_score: float = 0.0
    notes: str = ""

    def validate(self) -> None:
        for name in ("fit_score", "chinese_native_score", "portability_score", "maintainability_score", "overlap_score"):
            value = getattr(self, name)
            if not 0 <= value <= 1:
                raise ValueError(f"{name} 必须在 [0, 1]")


PERMISSIVE_LICENSES = {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "isc"}
REVIEW_LICENSES = {"mpl-2.0", "gpl-2.0", "gpl-3.0", "lgpl-2.1", "lgpl-3.0", "agpl-3.0"}


def decide_engagement(gap: CapabilityGap) -> Engagement:
    """先诊断缺口类型，再决定是否真的需要“招人”。"""
    gap.validate()
    if gap.gap_type == "skill":
        return "acquire_skill"
    if gap.gap_type == "tool":
        return "connect_tool"
    if gap.gap_type == "knowledge":
        return "add_knowledge"
    if gap.gap_type == "workflow":
        return "repair_workflow"
    if gap.gap_type == "unknown":
        return "investigate"

    # Expert 缺口也不默认永久扩编：高复用或战略能力才建正式岗位。
    if gap.recurrence_count >= 3 or gap.strategic or gap.criticality >= 0.85:
        return "permanent_expert"
    return "temporary_consultant"


def build_search_queries(gap: CapabilityGap) -> list[str]:
    """搜索的是能力资产，不只搜索名字中包含 expert 的仓库。"""
    gap.validate()
    base = gap.capability.strip()
    if gap.gap_type != "expert":
        suffixes = {
            "skill": ["skill", "SKILL.md", "playbook"],
            "tool": ["MCP", "connector", "tool"],
            "knowledge": ["guide", "handbook", "knowledge base"],
            "workflow": ["workflow", "playbook", "framework"],
            "unknown": ["agent", "skill", "workflow", "playbook"],
        }[gap.gap_type]
    else:
        suffixes = ["agent", "expert", "persona", "role", "skill", "playbook", "workflow", "multi-agent team"]
    return [f"{base} {suffix}" for suffix in suffixes]


def license_gate(license_name: str) -> dict[str, str | bool]:
    normalized = license_name.strip().lower()
    if normalized in PERMISSIVE_LICENSES:
        return {"decision": "allow", "can_copy": True, "reason": "宽松许可证；仍需保留来源与许可记录。"}
    if normalized in REVIEW_LICENSES:
        return {
            "decision": "review",
            "can_copy": False,
            "reason": "存在 copyleft / 传播义务；核心仓库默认不直接复制，先做许可证审查。",
        }
    return {
        "decision": "reject_copy",
        "can_copy": False,
        "reason": "许可证未知、缺失或不在允许清单；可以研究能力结构，但不能直接复制资产。",
    }


def candidate_score(candidate: CandidateAsset) -> float:
    candidate.validate()
    # “中文原生”和可迁移性作为正式竞争优势；职责高度重复会扣分。
    raw = (
        candidate.fit_score * 0.40
        + candidate.chinese_native_score * 0.20
        + candidate.portability_score * 0.15
        + candidate.maintainability_score * 0.15
        + (1 - candidate.overlap_score) * 0.10
    )
    return round(raw, 6)


def screen_candidate(candidate: CandidateAsset, min_score: float = 0.70) -> dict:
    candidate.validate()
    license_result = license_gate(candidate.license)
    score = candidate_score(candidate)
    if license_result["decision"] == "reject_copy":
        action = "RESEARCH_ONLY"
    elif score >= min_score:
        action = "SEND_TO_SHADOW"
    else:
        action = "REJECT"
    return {
        "candidate": asdict(candidate),
        "score": score,
        "license": license_result,
        "action": action,
    }


def build_recruitment_plan(gap: CapabilityGap) -> dict:
    engagement = decide_engagement(gap)
    return {
        "task_id": gap.task_id,
        "task_goal": gap.task_goal,
        "capability_gap": asdict(gap),
        "diagnosis": {
            "gap_type": gap.gap_type,
            "engagement": engagement,
            "principle": "先补能力缺口，再决定是否扩编；招聘由任务驱动，而不是为了扩大专家数量。",
        },
        "search_queries": build_search_queries(gap),
        "next_step": {
            "permanent_expert": "搜索候选资产 → 背景调查 → 中文标准化 → Shadow → Arena",
            "temporary_consultant": "临时搜索候选 → 限定任务 Shadow；重复出现后再评估正式建岗",
            "acquire_skill": "优先寻找可挂载到现有专家的 Skill，而不是新建专家",
            "connect_tool": "优先补 Connector / MCP / API，不招聘重复专家",
            "add_knowledge": "补充可信知识源与版本信息，不将资料库伪装成专家",
            "repair_workflow": "检查 Router / 编排 / 输入输出契约，先修流程",
            "investigate": "收集失败证据，区分 Expert / Skill / Tool / Knowledge / Workflow",
        }[engagement],
    }
