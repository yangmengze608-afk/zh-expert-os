import unittest

from zh_expert_os.github_source import CandidateDocument, GitHubHit
from zh_expert_os.models import Expert
from zh_expert_os.recruiter import CapabilityGap
from zh_expert_os.recruitment_pipeline import (
    analyze_candidate_document,
    infer_source_type,
    run_recruitment_pipeline,
    shadow_expert_from_dossier,
)


class FakePipelineClient:
    def search_repositories(self, query, limit=5):
        return [GitHubHit("repo", "demo/chinese-agents", "", "https://github.com/demo/chinese-agents", 1.0, "MIT", 120, "2026-08-20T00:00:00Z")]

    def search_code(self, query, limit=5):
        if "SKILL.md" in query:
            return [GitHubHit("code", "demo/chinese-agents", "skills/gamification/SKILL.md", "https://github.com/demo/chinese-agents/blob/main/skills/gamification/SKILL.md", 1.0, "MIT", 120, "2026-08-20T00:00:00Z")]
        return []

    def fetch_candidate_document(self, hit):
        text = """# 中国教育游戏化产品专家\n面向中国大学生设计学习游戏化产品。\n技能包括教育心理、游戏化机制、抽卡经济、留存设计、用户研究。\n可作为 Claude、Codex、ChatGPT 的 Markdown Skill 使用。\n"""
        return CandidateDocument(
            hit=hit,
            text=text,
            metadata={
                "description": "中文原生教育游戏化 Agent / Skill",
                "topics": ["agent", "education", "gamification"],
                "stars": 120,
                "updated_at": "2026-08-20T00:00:00Z",
                "pushed_at": "2026-08-20T00:00:00Z",
                "archived": False,
                "license": hit.license,
            },
            source_label=hit.path or "README.md",
        )


class NoSearchClient:
    def search_repositories(self, query, limit=5):
        raise AssertionError("非 Expert 缺口不应该触发 GitHub 招聘")

    def search_code(self, query, limit=5):
        raise AssertionError("非 Expert 缺口不应该触发 GitHub 招聘")


class RecruitmentPipelineTests(unittest.TestCase):
    def setUp(self):
        self.gap = CapabilityGap(
            task_id="study-pet-001",
            task_goal="设计面向中国大学生的学习抽卡宠物 MVP",
            capability="中国教育游戏化产品",
            gap_type="expert",
            reason="现役缺少教育心理 + 游戏化 + 中国学生市场联合能力",
            recurrence_count=4,
            strategic=True,
            criticality=0.8,
        )

    def test_infers_skill_from_skill_md(self):
        hit = GitHubHit("code", "demo/repo", "skills/a/SKILL.md", "https://example.com", 1.0, "MIT")
        self.assertEqual(infer_source_type(hit), "skill")

    def test_document_becomes_auditable_candidate_dossier(self):
        client = FakePipelineClient()
        hit = client.search_code("SKILL.md")[0]
        dossier = analyze_candidate_document(client.fetch_candidate_document(hit), self.gap, existing_experts=[])
        self.assertEqual(dossier["candidate"]["source_type"], "skill")
        self.assertGreater(dossier["screen"]["score"], 0.7)
        self.assertEqual(dossier["screen"]["action"], "SEND_TO_SHADOW")
        self.assertTrue(dossier["background_check"]["evidence"])

    def test_full_pipeline_reaches_shadow_without_direct_hire(self):
        existing = [
            Expert("router", "中文任务路由官", "0.1", "governance", "任务路由", "internal", "MIT", "根据任务组队"),
        ]
        result = run_recruitment_pipeline(
            self.gap,
            client=FakePipelineClient(),
            existing_experts=existing,
            per_query=2,
            max_documents=5,
            shortlist_size=2,
        )
        self.assertEqual(result["status"], "READY_FOR_SHADOW")
        self.assertGreaterEqual(result["candidate_count"], 1)
        self.assertGreaterEqual(len(result["shadow_specs"]), 1)
        self.assertEqual(result["shadow_specs"][0]["status"], "probation")
        self.assertIn("Arena", result["next_step"])

    def test_shadow_spec_cannot_be_created_from_unqualified_candidate(self):
        client = FakePipelineClient()
        hit = client.search_code("SKILL.md")[0]
        hit.license = "unknown"
        doc = client.fetch_candidate_document(hit)
        doc.hit.license = "unknown"
        doc.metadata["license"] = "unknown"
        dossier = analyze_candidate_document(doc, self.gap)
        self.assertEqual(dossier["screen"]["action"], "RESEARCH_ONLY")
        with self.assertRaises(ValueError):
            shadow_expert_from_dossier(dossier, self.gap)

    def test_non_expert_gap_stops_before_search(self):
        gap = CapabilityGap("market-001", "分析 A 股实时行情", "A股实时行情", "tool", "缺行情接口")
        result = run_recruitment_pipeline(gap, client=NoSearchClient())
        self.assertEqual(result["status"], "NO_EXPERT_RECRUITMENT")
        self.assertEqual(result["plan"]["diagnosis"]["engagement"], "connect_tool")


if __name__ == "__main__":
    unittest.main()
