from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from .models import Expert

EvidenceKind = Literal["tool_result", "transcript_record", "artifact", "derived"]
EnvelopeStatus = Literal["ok", "partial", "failed"]
HostTaskStatus = Literal["queued", "running", "completed", "cancelled", "failed", "unknown"]

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_WORKBUDDY_COMPAT_MAX_TURNS = 200


class WorkBuddyContractError(ValueError):
    pass


@dataclass(slots=True)
class EvidenceRef:
    """A machine-checkable pointer to the origin of one observed value or claim."""

    source_task_id: str
    kind: EvidenceKind
    locator: str
    artifact_sha256: str | None = None
    parent_refs: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.source_task_id.strip():
            raise WorkBuddyContractError("source_task_id 不能为空")
        if self.kind not in {"tool_result", "transcript_record", "artifact", "derived"}:
            raise WorkBuddyContractError(f"未知 evidence kind: {self.kind}")
        if not self.locator.strip():
            raise WorkBuddyContractError("evidence locator 不能为空")
        if self.artifact_sha256 is not None and not _SHA256_RE.fullmatch(self.artifact_sha256):
            raise WorkBuddyContractError("artifact_sha256 必须是 64 位小写十六进制")
        if self.kind == "derived" and not self.parent_refs:
            raise WorkBuddyContractError("derived evidence 必须列出 parent_refs")

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)


@dataclass(slots=True)
class ArtifactRef:
    relative_path: str
    sha256: str

    def validate(self) -> None:
        p = Path(self.relative_path)
        if p.is_absolute() or ".." in p.parts or not self.relative_path.strip():
            raise WorkBuddyContractError("artifact 路径必须是无 .. 的相对路径")
        if not _SHA256_RE.fullmatch(self.sha256):
            raise WorkBuddyContractError("artifact sha256 必须是 64 位小写十六进制")

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)


@dataclass(slots=True)
class EvidenceClaim:
    statement: str
    confidence: float
    evidence: list[EvidenceRef]

    def validate(self) -> None:
        if not self.statement.strip():
            raise WorkBuddyContractError("claim statement 不能为空")
        if not 0 <= self.confidence <= 1:
            raise WorkBuddyContractError("claim confidence 必须在 [0, 1]")
        if not self.evidence:
            raise WorkBuddyContractError("进入 evidence registry 的 claim 必须有 provenance")
        for ref in self.evidence:
            ref.validate()

    def to_dict(self) -> dict:
        self.validate()
        return {
            "statement": self.statement,
            "confidence": self.confidence,
            "evidence": [ref.to_dict() for ref in self.evidence],
        }


@dataclass(slots=True)
class ExpertEnvelope:
    agent_id: str
    task_id: str
    status: EnvelopeStatus
    confidence: float
    summary: str
    claims: list[EvidenceClaim] = field(default_factory=list)
    artifacts: list[ArtifactRef] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.agent_id.strip() or not self.task_id.strip():
            raise WorkBuddyContractError("agent_id / task_id 不能为空")
        if self.status not in {"ok", "partial", "failed"}:
            raise WorkBuddyContractError(f"未知 envelope status: {self.status}")
        if not 0 <= self.confidence <= 1:
            raise WorkBuddyContractError("envelope confidence 必须在 [0, 1]")
        if not self.summary.strip():
            raise WorkBuddyContractError("summary 不能为空")
        for claim in self.claims:
            claim.validate()
        for artifact in self.artifacts:
            artifact.validate()

    def to_dict(self) -> dict:
        self.validate()
        return {
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "status": self.status,
            "confidence": self.confidence,
            "summary": self.summary,
            "claims": [claim.to_dict() for claim in self.claims],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "open_questions": list(self.open_questions),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExpertEnvelope":
        required = {"agent_id", "task_id", "status", "confidence", "summary", "claims", "artifacts", "open_questions"}
        extra = set(data) - required
        missing = required - set(data)
        if missing:
            raise WorkBuddyContractError(f"ZEOS_ENVELOPE 缺少字段：{sorted(missing)}")
        if extra:
            raise WorkBuddyContractError(f"ZEOS_ENVELOPE 含未知字段：{sorted(extra)}")
        claims = [
            EvidenceClaim(
                statement=row["statement"],
                confidence=row["confidence"],
                evidence=[EvidenceRef(**ref) for ref in row.get("evidence", [])],
            )
            for row in data.get("claims", [])
        ]
        artifacts = [ArtifactRef(**row) for row in data.get("artifacts", [])]
        envelope = cls(
            agent_id=data["agent_id"],
            task_id=data["task_id"],
            status=data["status"],
            confidence=data["confidence"],
            summary=data["summary"],
            claims=claims,
            artifacts=artifacts,
            open_questions=list(data.get("open_questions", [])),
        )
        envelope.validate()
        return envelope


@dataclass(slots=True)
class WorkBuddyNodeState:
    """Keep WorkBuddy host task identity separate from the lead-assigned ZEOS assignment."""

    host_task_id: str
    assignment_id: str
    agent_id: str
    host_status: HostTaskStatus
    envelope: ExpertEnvelope | None = None

    def validate(self) -> None:
        if not self.host_task_id.strip() or not self.assignment_id.strip() or not self.agent_id.strip():
            raise WorkBuddyContractError("host_task_id / assignment_id / agent_id 不能为空")
        if self.host_status not in {"queued", "running", "completed", "cancelled", "failed", "unknown"}:
            raise WorkBuddyContractError(f"未知 host status: {self.host_status}")
        if self.envelope is not None:
            self.envelope.validate()
            if self.envelope.task_id != self.assignment_id:
                raise WorkBuddyContractError("envelope.task_id 必须等于 lead 分配的 assignment_id")
            if self.envelope.agent_id != self.agent_id:
                raise WorkBuddyContractError("envelope.agent_id 必须等于节点 agent_id")

    @property
    def terminal(self) -> bool:
        return self.host_status in {"completed", "cancelled", "failed"}

    def to_dict(self) -> dict:
        self.validate()
        return {
            "host_task_id": self.host_task_id,
            "assignment_id": self.assignment_id,
            "agent_id": self.agent_id,
            "host_status": self.host_status,
            "terminal": self.terminal,
            "envelope": self.envelope.to_dict() if self.envelope else None,
        }


@dataclass(slots=True)
class MessageDeliveryState:
    """Do not collapse route acceptance, consumption, and acknowledgement."""

    route_accepted: bool = False
    consumed: bool = False
    acked: bool = False

    def validate(self) -> None:
        if self.acked and not self.consumed:
            raise WorkBuddyContractError("ACKED 必须建立在 CONSUMED 之上")
        if self.consumed and not self.route_accepted:
            raise WorkBuddyContractError("CONSUMED 必须建立在 ROUTE_ACCEPTED 之上")

    @property
    def confirmed(self) -> bool:
        self.validate()
        return self.acked

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)


@dataclass(slots=True)
class WorkBuddyTeamPlan:
    lead_id: str
    worker_ids: list[str]
    artifact_namespaces: dict[str, str]
    topology: str = "flat"

    def validate(self) -> None:
        if self.topology != "flat":
            raise WorkBuddyContractError("v0.5-alpha1 只把 flat fan-out 作为已支持默认")
        if not self.lead_id.strip():
            raise WorkBuddyContractError("lead_id 不能为空")
        if not self.worker_ids:
            raise WorkBuddyContractError("worker_ids 不能为空")
        if len(set(self.worker_ids)) != len(self.worker_ids):
            raise WorkBuddyContractError("worker id 必须唯一")
        if self.lead_id in self.worker_ids:
            raise WorkBuddyContractError("lead 不能同时作为 worker")
        if set(self.artifact_namespaces) != set(self.worker_ids):
            raise WorkBuddyContractError("每个 worker 必须且只能有一个 artifact namespace")
        namespaces = list(self.artifact_namespaces.values())
        if any(not str(x).strip() for x in namespaces) or len(set(namespaces)) != len(namespaces):
            raise WorkBuddyContractError("artifact namespace 必须非空且互不重复")

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)


@dataclass(slots=True)
class NativeExpertSpec:
    id: str
    display_name_zh: str
    display_name_en: str
    profession_zh: str
    profession_en: str
    description: str
    instructions: str

    def validate(self) -> None:
        if not _ID_RE.fullmatch(self.id):
            raise WorkBuddyContractError("native expert id 必须是小写字母/数字/连字符")
        for value in (
            self.display_name_zh,
            self.display_name_en,
            self.profession_zh,
            self.profession_en,
            self.description,
            self.instructions,
        ):
            if not str(value).strip():
                raise WorkBuddyContractError("native expert 文本字段不能为空")


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def envelope_contract_text() -> str:
    return """## Runtime 回传契约

Lead 必须在任务 prompt 中给你：
- `ZEOS_TASK_ID`：lead 分配的逻辑 assignment id
- `ZEOS_ARTIFACT_NAMESPACE`：你的唯一 artifact namespace

最终回答必须包含一个 `ZEOS_ENVELOPE` JSON 区块。不要猜 WorkBuddy host task_id；`task_id` 只回显 `ZEOS_TASK_ID`。

```text
ZEOS_ENVELOPE
{
  "agent_id": "<你的 agent name>",
  "task_id": "<ZEOS_TASK_ID>",
  "status": "ok | partial | failed",
  "confidence": 0.0,
  "summary": "简洁结论",
  "claims": [
    {
      "statement": "可验证 claim",
      "confidence": 0.0,
      "evidence": [
        {
          "source_task_id": "<ZEOS_TASK_ID>",
          "kind": "tool_result | transcript_record | artifact | derived",
          "locator": "真实来源定位",
          "artifact_sha256": null,
          "parent_refs": []
        }
      ]
    }
  ],
  "artifacts": [
    {
      "relative_path": "namespace 内相对路径",
      "sha256": "64位小写 sha256"
    }
  ],
  "open_questions": []
}
```

规则：
- 没有可追溯来源的判断不要放进 `claims`。
- derived evidence 必须列 `parent_refs`。
- 没 artifact 时返回 `artifacts: []`。
- 宿主 host status 与本 envelope status 是两个维度，不得互相覆盖。
- 若宿主在你提交 envelope 前将你 stop，你可能不会有机会回传；由 lead 根据 host status 与已落地 artifact 重建 partial。
"""

def render_native_expert(spec: NativeExpertSpec) -> str:
    spec.validate()
    frontmatter = [
        "---",
        f"name: {spec.id}",
        f"description: {_yaml_string(spec.description)}",
        "displayName:",
        f"  en: {_yaml_string(spec.display_name_en)}",
        f"  zh: {_yaml_string(spec.display_name_zh)}",
        "profession:",
        f"  en: {_yaml_string(spec.profession_en)}",
        f"  zh: {_yaml_string(spec.profession_zh)}",
        f"maxTurns: {_WORKBUDDY_COMPAT_MAX_TURNS}",
        "---",
        "",
    ]
    return "\n".join(frontmatter) + spec.instructions.rstrip() + "\n\n" + envelope_contract_text() + "\n"


def native_spec_from_expert(expert: Expert) -> NativeExpertSpec:
    if expert.status not in {"probation", "active", "governance"}:
        raise WorkBuddyContractError(
            "只有 probation / active / governance Expert 可导出为 WorkBuddy native agent"
        )
    if not _ID_RE.fullmatch(expert.id):
        raise WorkBuddyContractError(f"Expert id 不可用于 WorkBuddy native agent: {expert.id}")
    mission = expert.mission.strip() or "按岗位职责完成分配任务，并诚实报告不确定性。"
    instructions = f"""# {expert.name_zh}

## 身份
你是 Zh Expert OS 中的独立 Expert：{expert.name_zh}。

## 岗位
{expert.role}

## 使命
{mission}

## 边界
- Lead 应在 prompt 中给你 `ZEOS_TASK_ID` 与 `ZEOS_ARTIFACT_NAMESPACE`；最终 envelope 的 task_id 只回显该 assignment id，不猜 host task id。
- 只处理 lead 明确分配给你的子任务，不自行扩张任务范围。
- 不把同模型多角色当作独立证据。
- 不读取 sibling Expert 的 artifact namespace，除非 lead 明确授权并说明原因。
- 事实、推断、不确定性分开写。
- 任何进入 evidence registry 的具体值必须指向真实 tool result / transcript record / artifact。
- 禁止把自己手打或猜测的“观测值”回显到命令/文件后再当作旁证。
"""
    return NativeExpertSpec(
        id=expert.id,
        display_name_zh=expert.name_zh,
        display_name_en=expert.id,
        profession_zh=expert.role,
        profession_en=expert.role,
        description=f"Zh Expert OS native Expert：{expert.name_zh}；岗位：{expert.role}",
        instructions=instructions,
    )


def write_native_expert(expert: Expert, output_dir: Path, overwrite: bool = False) -> Path:
    spec = native_spec_from_expert(expert)
    output_dir = output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{spec.id}.md"
    if path.is_symlink():
        if not overwrite:
            raise FileExistsError(f"目标 symlink 已存在：{path}")
        path.unlink()
    elif path.exists() and not overwrite:
        raise FileExistsError(f"目标已存在：{path}")
    path.write_text(render_native_expert(spec), encoding="utf-8")
    return path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_expert_envelope(text: str) -> ExpertEnvelope:
    """Parse the first JSON object after a ZEOS_ENVELOPE marker."""
    marker = "ZEOS_ENVELOPE"
    idx = text.find(marker)
    if idx < 0:
        raise WorkBuddyContractError("输出中缺少 ZEOS_ENVELOPE 标记")
    start = text.find("{", idx + len(marker))
    if start < 0:
        raise WorkBuddyContractError("ZEOS_ENVELOPE 后缺少 JSON object")
    try:
        data, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError as exc:
        raise WorkBuddyContractError(f"ZEOS_ENVELOPE JSON 无法解析：{exc}") from exc
    if not isinstance(data, dict):
        raise WorkBuddyContractError("ZEOS_ENVELOPE 必须是 JSON object")
    return ExpertEnvelope.from_dict(data)
