from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass


@dataclass(slots=True)
class GitHubHit:
    kind: str
    repository: str
    path: str
    url: str
    score: float
    license: str = "unknown"
    stars: int = 0
    updated_at: str = ""
    archived: bool = False


@dataclass(slots=True)
class CandidateDocument:
    hit: GitHubHit
    text: str
    metadata: dict
    source_label: str

    def to_dict(self) -> dict:
        return {
            "hit": asdict(self.hit),
            "text": self.text,
            "metadata": self.metadata,
            "source_label": self.source_label,
        }


class GitHubSearchClient:
    """零第三方依赖的 GitHub 候选发现与读取客户端。

    - repo 搜索可匿名使用，但限流更严格；
    - code 搜索建议/通常需要 GITHUB_TOKEN；
    - 读取阶段只读取公开候选的 README / Agent / Skill 文本；
    - 这里只负责发现和背景调查，不自动复制 Prompt 或代码到核心仓库。
    """

    api = "https://api.github.com"

    def __init__(self, token: str | None = None, timeout: float = 15.0):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout

    def _request(self, path: str, params: dict[str, str | int] | None = None) -> dict:
        query = urllib.parse.urlencode(params or {})
        url = f"{self.api}{path}" + (f"?{query}" if query else "")
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "zh-expert-os-recruiter",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {exc.code}: {body[:500]}") from exc

    def search_repositories(self, query: str, limit: int = 5) -> list[GitHubHit]:
        data = self._request(
            "/search/repositories",
            {"q": query, "sort": "stars", "order": "desc", "per_page": max(1, min(limit, 30))},
        )
        hits: list[GitHubHit] = []
        for item in data.get("items", []):
            license_info = item.get("license") or {}
            stars = int(item.get("stargazers_count", 0) or 0)
            hits.append(
                GitHubHit(
                    kind="repo",
                    repository=item.get("full_name", ""),
                    path="",
                    url=item.get("html_url", ""),
                    score=float(item.get("score", 0.0)),
                    license=license_info.get("spdx_id") or "unknown",
                    stars=stars,
                    updated_at=item.get("updated_at", "") or "",
                    archived=bool(item.get("archived", False)),
                )
            )
        return hits

    def search_code(self, query: str, limit: int = 10) -> list[GitHubHit]:
        if not self.token:
            raise RuntimeError("代码搜索需要 GITHUB_TOKEN；没有 Token 时可先使用 repository 搜索。")
        data = self._request(
            "/search/code",
            {"q": query, "per_page": max(1, min(limit, 30))},
        )
        hits: list[GitHubHit] = []
        for item in data.get("items", []):
            repo = item.get("repository") or {}
            hits.append(
                GitHubHit(
                    kind="code",
                    repository=repo.get("full_name", ""),
                    path=item.get("path", ""),
                    url=item.get("html_url", ""),
                    score=float(item.get("score", 0.0)),
                    license="unknown",
                    stars=int(repo.get("stargazers_count", 0) or 0),
                    updated_at=repo.get("updated_at", "") or "",
                    archived=bool(repo.get("archived", False)),
                )
            )
        return hits

    def fetch_repository_metadata(self, repository: str) -> dict:
        if "/" not in repository:
            raise ValueError("repository 必须是 owner/name")
        return self._request(f"/repos/{repository}")

    @staticmethod
    def _decode_content(payload: dict) -> str:
        encoded = payload.get("content")
        if not encoded:
            return ""
        if payload.get("encoding") != "base64":
            return str(encoded)
        try:
            return base64.b64decode(encoded, validate=False).decode("utf-8", errors="replace")
        except (ValueError, TypeError):
            return ""

    def fetch_candidate_document(self, hit: GitHubHit, max_chars: int = 60000) -> CandidateDocument:
        """读取候选最能代表其能力的文本，并补齐仓库元数据与许可证。"""
        metadata = self.fetch_repository_metadata(hit.repository)
        license_info = metadata.get("license") or {}
        if not hit.license or hit.license == "unknown":
            hit.license = license_info.get("spdx_id") or "unknown"
        hit.stars = int(metadata.get("stargazers_count", hit.stars) or 0)
        hit.updated_at = metadata.get("updated_at", hit.updated_at) or hit.updated_at
        hit.archived = bool(metadata.get("archived", hit.archived))

        if hit.path:
            path = urllib.parse.quote(hit.path, safe="/")
            payload = self._request(f"/repos/{hit.repository}/contents/{path}")
            text = self._decode_content(payload)
            source_label = hit.path
        else:
            try:
                payload = self._request(f"/repos/{hit.repository}/readme")
                text = self._decode_content(payload)
                source_label = payload.get("path", "README") or "README"
            except RuntimeError:
                text = metadata.get("description", "") or ""
                source_label = "repository-description"

        return CandidateDocument(
            hit=hit,
            text=text[:max_chars],
            metadata={
                "description": metadata.get("description") or "",
                "topics": metadata.get("topics") or [],
                "default_branch": metadata.get("default_branch") or "",
                "stars": hit.stars,
                "forks": int(metadata.get("forks_count", 0) or 0),
                "open_issues": int(metadata.get("open_issues_count", 0) or 0),
                "updated_at": hit.updated_at,
                "pushed_at": metadata.get("pushed_at") or "",
                "archived": hit.archived,
                "license": hit.license,
            },
            source_label=source_label,
        )


def expert_asset_code_queries(capability: str) -> list[str]:
    """优先查可能承载 Agent/Expert/Skill 定义的文件，而非只匹配仓库名称。"""
    c = capability.strip()
    if not c:
        raise ValueError("capability 不能为空")
    return [
        f'"{c}" filename:SKILL.md',
        f'"{c}" path:agents extension:md',
        f'"{c}" path:experts extension:md',
        f'"{c}" path:roles extension:md',
        f'"{c}" path:skills extension:md',
        f'"{c}" playbook extension:md',
    ]


def discover_candidate_assets(
    capability: str,
    *,
    client: GitHubSearchClient | None = None,
    per_query: int = 5,
) -> dict:
    client = client or GitHubSearchClient()
    repo_terms = [
        f"{capability} agent",
        f"{capability} expert",
        f"{capability} skill",
        f"{capability} playbook",
        f"{capability} multi-agent",
    ]
    repo_hits: list[GitHubHit] = []
    seen_repo = set()
    for q in repo_terms:
        for hit in client.search_repositories(q, per_query):
            key = (hit.repository, hit.path)
            if key not in seen_repo:
                seen_repo.add(key)
                repo_hits.append(hit)

    code_hits: list[GitHubHit] = []
    code_error = None
    try:
        seen_code = set()
        for q in expert_asset_code_queries(capability):
            for hit in client.search_code(q, per_query):
                key = (hit.repository, hit.path)
                if key not in seen_code:
                    seen_code.add(key)
                    code_hits.append(hit)
    except RuntimeError as exc:
        code_error = str(exc)

    return {
        "capability": capability,
        "repository_hits": [asdict(h) for h in repo_hits],
        "code_hits": [asdict(h) for h in code_hits],
        "code_search_error": code_error,
        "principle": "发现结果只是候选资产；必须经过 License、能力匹配、中文标准化、Shadow 与 Arena 才能入职。",
    }
