from __future__ import annotations

import hashlib
import math
import re
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable

from .github_source import CandidateDocument, GitHubHit, GitHubSearchClient, discover_candidate_assets
from .models import Expert
from .recruiter import CandidateAsset, CapabilityGap, build_recruitment_plan, decide_engagement, screen_candidate

_CJK_RE = re.compile(r"[\u3400-\u9fff]")
_LATIN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_+-]{1,}")
_SOURCE_MARKERS = {
    "skill": ("skill.md", "/skills/", "skill/"),
    "agent": ("/agents/", "agents/", "agent.md"),
    "expert": ("/experts/", "experts/", "expert.md"),
    "role": ("/roles/", "roles/", "role.md"),
    "playbook": ("playbook",),
    "workflow": ("workflow", ".github/workflows/"),
    "team": ("multi-agent", "agent-team", "team.md", "/teams/"),
}
_CHINA_MARKERS = (
    "中国", "中文", "国内", "小红书", "知乎", "抖音", "b站", "哔哩哔哩", "微信", "公众号", "视频号",
    "飞书", "钉钉", "企微", "a股", "港股通", "淘宝", "京东", "拼多多", "知网", "万方",
)
_PORTABLE_MARKERS = ("claude", "codex", "chatgpt", "cursor", "markdown", "skill.md", "agent", "prompt")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _tokens(text: str) -> set[str]:
    text = _normalize(text)
    tokens = {m.group(0) for m in _LATIN_RE.finditer(text)}
    cjk_runs = re.findall(r"[\u3400-\u9fff]{2,}", text)
    for run in cjk_runs:
        tokens.add(run)
        if len(run) <= 8:
            tokens.add(run)
        for i in range(len(run) - 1):
            tokens.add(run[i : i + 2])
    return tokens


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


def infer_source_type(hit: GitHubHit, text: str = "") -> str:
    probe = f"/{hit.path.lower()} {_normalize(text[:3000])}"
    for source_type, markers in _SOURCE_MARKERS.items():
        if any(marker in probe for marker in markers):
            return source_type
    return "repo"


def _fit_score(capability: str, document: CandidateDocument) -> float:
    haystack = " ".join(
        [
            document.hit.repository,
            document.hit.path,
            document.metadata.get("description", ""),
            " ".join(document.metadata.get("topics", [])),
            document.text[:30000],
        ]
    )
    cap_norm = _normalize(capability)
    hay_norm = _normalize(haystack)
    if cap_norm and cap_norm in hay_norm:
        exact = 0.55
    else:
        exact = 0.0
    cap_tokens = _tokens(capability)
    hay_tokens = _tokens(haystack)
    coverage = len(cap_tokens & hay_tokens) / max(1, len(cap_tokens))
    role_bonus = 0.12 if infer_source_type(document.hit, document.text) != "repo" else 0.04
    return _bounded(0.18 + exact + coverage * 0.25 + role_bonus)


def _chinese_native_score(document: CandidateDocument) -> float:
    sample = f"{document.metadata.get('description', '')}\n{document.text[:30000]}".lower()
    cjk_count = len(_CJK_RE.findall(sample))
    alpha_count = sum(ch.isalpha() for ch in sample)
    ratio = cjk_count / max(1, alpha_count)
    language_score = min(0.75, ratio * 1.8)
    ecosystem_hits = sum(1 for marker in _CHINA_MARKERS if marker in sample)
    ecosystem_score = min(0.25, ecosystem_hits * 0.05)
    return _bounded(language_score + ecosystem_score)


def _portability_score(document: CandidateDocument, source_type: str) -> float:
    base = {
        "skill": 0.88,
        "agent": 0.85,
        "expert": 0.85,
        "persona": 0.82,
        "role": 0.82,
        "playbook": 0.78,
        "workflow": 0.68,
        "team": 0.62,
        "repo": 0.50,
        "generated": 0.60,
    }.get(source_type, 0.50)
    probe = f"{document.hit.path} {document.text[:12000]}".lower()
    if document.hit.path.lower().endswith((".md", ".txt", ".yaml", ".yml", ".json")):
        base += 0.05
    marker_hits = sum(1 for marker in _PORTABLE_MARKERS if marker in probe)
    base += min(0.07, marker_hits * 0.015)
    return _bounded(base)


def _maintainability_score(document: CandidateDocument, now: datetime | None = None) -> float:
    if document.hit.archived or document.metadata.get("archived"):
        return 0.10
    now = now or datetime.now(timezone.utc)
    updated = document.metadata.get("pushed_at") or document.metadata.get("updated_at") or document.hit.updated_at
    recency = 0.20
    if updated:
        try:
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            age_days = max(0, (now - dt).days)
            if age_days <= 90:
                recency = 0.45
            elif age_days <= 365:
                recency = 0.35
            elif age_days <= 1095:
                recency = 0.25
            else:
                recency = 0.10
        except ValueError:
            pass
    stars = max(0, int(document.metadata.get("stars", document.hit.stars) or 0))
    popularity = min(0.35, math.log10(stars + 1) / 12)
    structure = 0.15 if document.text.strip() else 0.03
    return _bounded(0.05 + recency + popularity + structure)


def _overlap_score(capability: str, existing_experts: Iterable[Expert]) -> float:
    target = _tokens(capability)
    if not target:
        return 0.0
    best = 0.0
    for expert in existing_experts:
        expert_tokens = _tokens(f"{expert.name_zh} {expert.role} {expert.mission}")
        overlap = len(target & expert_tokens) / max(1, len(target))
        best = max(best, overlap)
    return _bounded(best)


def _evidence_lines(capability: str, document: CandidateDocument, limit: int = 3) -> list[str]:
    tokens = _tokens(capability)
    candidates: list[tuple[int, str]] = []
    for raw in document.text.splitlines():
        line = raw.strip().lstrip("#*- ")
        if len(line) < 8:
            continue
        line_tokens = _tokens(line)
        hits = len(tokens & line_tokens)
        if hits or any(word in line.lower() for word in ("agent", "expert", "skill", "workflow", "角色", "专家", "技能")):
            candidates.append((hits, line[:220]))
    candidates.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
    output: list[str] = []
    seen = set()
    for _, line in candidates:
        if line not in seen:
            output.append(line)
            seen.add(line)
        if len(output) >= limit:
            break
    return output


def analyze_candidate_document(
    document: CandidateDocument,
    gap: CapabilityGap,
    existing_experts: Iterable[Expert] = (),
) -> dict:
    """把外部 GitHub 资产标准化成 CandidateAsset，并留下可审计证据。"""
    source_type = infer_source_type(document.hit, document.text)
    chinese_score = _chinese_native_score(document)
    language = "zh" if chinese_score >= 0.55 else ("mixed" if chinese_score >= 0.25 else "en")
    source_key = f"{document.hit.repository}:{document.hit.path or document.source_label}:{gap.capability}"
    candidate_id = "cand-" + hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:12]
    evidence = _evidence_lines(gap.capability, document)
    candidate = CandidateAsset(
        id=candidate_id,
        source_type=source_type,  # type: ignore[arg-type]
        repository=document.hit.repository,
        path=document.hit.path or document.source_label,
        license=document.hit.license or document.metadata.get("license", "unknown") or "unknown",
        language=language,
        capability_tags=[gap.capability],
        fit_score=_fit_score(gap.capability, document),
        chinese_native_score=chinese_score,
        portability_score=_portability_score(document, source_type),
        maintainability_score=_maintainability_score(document),
        overlap_score=_overlap_score(gap.capability, existing_experts),
        notes="；".join(evidence),
    )
    screened = screen_candidate(candidate)
    return {
        "candidate": asdict(candidate),
        "screen": screened,
        "background_check": {
            "repository": document.hit.repository,
            "source": document.source_label,
            "url": document.hit.url,
            "stars": document.metadata.get("stars", document.hit.stars),
            "updated_at": document.metadata.get("updated_at", document.hit.updated_at),
            "pushed_at": document.metadata.get("pushed_at", ""),
            "archived": document.metadata.get("archived", document.hit.archived),
            "evidence": evidence,
        },
    }


def shadow_expert_from_dossier(dossier: dict, gap: CapabilityGap) -> Expert:
    """只把已经通过 permissive-license + 评分门槛的候选转成 Shadow 专家规格。"""
    if dossier["screen"]["action"] != "SEND_TO_SHADOW":
        raise ValueError("候选尚未通过 Shadow 门槛")
    if dossier["screen"]["license"]["decision"] != "allow":
        raise ValueError("只有宽松许可证候选可以自动生成 Shadow 规格")
    c = dossier["candidate"]
    suffix = c["id"].removeprefix("cand-")
    return Expert(
        id=f"shadow-{suffix}",
        name_zh=f"{gap.capability}候选专家",
        version="0.1-shadow",
        status="probation",
        role=gap.capability,
        source=f"github:{c['repository']}:{c['path']}",
        license=c["license"],
        mission=f"围绕“{gap.task_goal}”在限定真实任务中证明其 {gap.capability} 能力；不得因为来源知名度跳过 Arena。",
    )


def run_recruitment_pipeline(
    gap: CapabilityGap,
    *,
    client: GitHubSearchClient | None = None,
    existing_experts: Iterable[Expert] = (),
    per_query: int = 3,
    max_documents: int = 20,
    shortlist_size: int = 5,
) -> dict:
    """任务 → 缺口 → GitHub 发现 → 读取 → 背调 → 标准化 → License → 排名 → Shadow 规格。"""
    gap.validate()
    engagement = decide_engagement(gap)
    plan = build_recruitment_plan(gap)
    if engagement not in {"permanent_expert", "temporary_consultant"}:
        return {
            "status": "NO_EXPERT_RECRUITMENT",
            "plan": plan,
            "reason": "本次缺口不是 Expert；应补 Skill / Tool / Knowledge / Workflow。",
            "candidates": [],
            "shortlist": [],
            "shadow_specs": [],
        }

    client = client or GitHubSearchClient()
    discovery = discover_candidate_assets(gap.capability, client=client, per_query=per_query)
    raw_hits = [*discovery.get("code_hits", []), *discovery.get("repository_hits", [])]
    seen = set()
    hits: list[GitHubHit] = []
    for row in raw_hits:
        key = (row.get("repository", ""), row.get("path", ""))
        if not key[0] or key in seen:
            continue
        seen.add(key)
        hits.append(GitHubHit(**row))
        if len(hits) >= max_documents:
            break

    dossiers: list[dict] = []
    failures: list[dict] = []
    existing = list(existing_experts)
    for hit in hits:
        try:
            document = client.fetch_candidate_document(hit)
            dossiers.append(analyze_candidate_document(document, gap, existing))
        except Exception as exc:  # 单个候选失败不能拖垮整次招聘
            failures.append({"repository": hit.repository, "path": hit.path, "error": str(exc)[:500]})

    action_priority = {"SEND_TO_SHADOW": 3, "RESEARCH_ONLY": 2, "REJECT": 1}
    dossiers.sort(
        key=lambda d: (action_priority.get(d["screen"]["action"], 0), d["screen"]["score"]),
        reverse=True,
    )
    shortlist = [d for d in dossiers if d["screen"]["action"] == "SEND_TO_SHADOW"][:shortlist_size]
    shadow_specs = []
    for dossier in shortlist:
        if dossier["screen"]["license"]["decision"] == "allow":
            shadow_specs.append(shadow_expert_from_dossier(dossier, gap).to_dict())

    return {
        "status": "READY_FOR_SHADOW" if shadow_specs else "NO_SHADOW_CANDIDATE",
        "plan": plan,
        "discovery": {
            "repository_hits": len(discovery.get("repository_hits", [])),
            "code_hits": len(discovery.get("code_hits", [])),
            "code_search_error": discovery.get("code_search_error"),
        },
        "candidate_count": len(dossiers),
        "candidates": dossiers,
        "shortlist": shortlist,
        "shadow_specs": shadow_specs,
        "failures": failures,
        "next_step": "将 Shadow 候选登记为 probation，使用原始任务和岗位 benchmark 进入 Eval Arena；不得直接晋升。",
    }
