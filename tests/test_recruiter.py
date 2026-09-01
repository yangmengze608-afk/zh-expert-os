import unittest

from zh_expert_os.recruiter import (
    CandidateAsset,
    CapabilityGap,
    build_recruitment_plan,
    build_search_queries,
    candidate_score,
    decide_engagement,
    license_gate,
    screen_candidate,
)


class RecruiterTests(unittest.TestCase):
    def test_non_expert_gap_does_not_hire_person(self):
        gap = CapabilityGap("t1", "分析实时行情", "A股实时行情", "tool", "现有专家没有行情接口")
        self.assertEqual(decide_engagement(gap), "connect_tool")

    def test_one_off_expert_gap_uses_consultant(self):
        gap = CapabilityGap("t2", "检查澳洲宠物食品进口", "澳洲宠物食品监管", "expert", "现役无覆盖")
        self.assertEqual(decide_engagement(gap), "temporary_consultant")

    def test_recurring_expert_gap_can_create_permanent_role(self):
        gap = CapabilityGap(
            "t3", "连续处理中国教育产品任务", "中国教育游戏化产品", "expert", "过去任务重复出现",
            recurrence_count=5,
        )
        self.assertEqual(decide_engagement(gap), "permanent_expert")

    def test_expert_search_is_not_limited_to_expert_keyword(self):
        gap = CapabilityGap("t4", "设计SaaS定价", "中国 SaaS 定价", "expert", "现役缺口")
        queries = build_search_queries(gap)
        self.assertTrue(any("skill" in q for q in queries))
        self.assertTrue(any("playbook" in q for q in queries))
        self.assertTrue(any("agent" in q for q in queries))

    def test_unknown_license_is_research_only(self):
        c = CandidateAsset(
            "c1", "agent", "owner/repo", "agents/pricing.md", "unknown", "zh",
            ["pricing"], 0.95, 0.9, 0.9, 0.9, 0.1,
        )
        result = screen_candidate(c)
        self.assertEqual(result["action"], "RESEARCH_ONLY")
        self.assertFalse(result["license"]["can_copy"])

    def test_good_mit_candidate_goes_to_shadow(self):
        c = CandidateAsset(
            "c2", "skill", "owner/repo", "skills/pricing/SKILL.md", "MIT", "zh",
            ["pricing"], 0.92, 0.88, 0.90, 0.80, 0.20,
        )
        self.assertGreater(candidate_score(c), 0.8)
        self.assertEqual(screen_candidate(c)["action"], "SEND_TO_SHADOW")

    def test_plan_states_task_driven_principle(self):
        gap = CapabilityGap("t5", "做产品MVP", "游戏化设计", "skill", "产品经理缺少该技能")
        plan = build_recruitment_plan(gap)
        self.assertEqual(plan["diagnosis"]["engagement"], "acquire_skill")
        self.assertIn("任务驱动", plan["diagnosis"]["principle"])

    def test_license_gate_copyleft_requires_review(self):
        self.assertEqual(license_gate("AGPL-3.0")["decision"], "review")


if __name__ == "__main__":
    unittest.main()
