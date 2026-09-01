from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass(slots=True)
class GitHubHit:
    kind: str
    repository: str
    path: str
    url: str
    score: float
    license: str = "unknown"


class GitHubSearchClient:
    """零第三方依赖的 GitHub 候选发现器。

    - repo 搜索可匿名使用，但限流更严格；
    - code 搜索建议/通常需要 GITHUB_TOKEN；
    - 这里只负责发现候选，不负责自动复制 Prompt 或代码。
    """

    api = "https://api.github.com"

    def __init__(self, token: str | None = None, timeout: float = 15.0):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout

    def _request(self, path: str, params: dict[str, str | int]) -> dict:
        url = f"{self.api}{path}?{urllib.parse.urlencode(params)}"
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
            hits.append(
                GitHubHit(
                    kind="repo",
                    repository=item.get("full_name", ""),
                    path="",
                    url=item.get("html_url", ""),
                    score=float(item.get("score", 0.0)),
                    license=license_info.get("spdx_id") or "unknown",
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
                )
            )
        return hits


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
        "repository_hits": [h.__dict__ for h in repo_hits],
        "code_hits": [h.__dict__ for h in code_hits],
        "code_search_error": code_error,
        "principle": "发现结果只是候选资产；必须经过 License、能力匹配、中文标准化、Shadow 与 Arena 才能入职。",
    }
