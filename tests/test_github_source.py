import unittest

from zh_expert_os.github_source import GitHubHit, discover_candidate_assets, expert_asset_code_queries


class FakeClient:
    def search_repositories(self, query, limit=5):
        return [GitHubHit("repo", "demo/agents", "", "https://github.com/demo/agents", 1.0, "MIT")]

    def search_code(self, query, limit=5):
        if "SKILL.md" in query:
            return [GitHubHit("code", "demo/agents", "skills/pricing/SKILL.md", "https://github.com/demo/agents/blob/main/skills/pricing/SKILL.md", 1.0)]
        return []


class GitHubSourceTests(unittest.TestCase):
    def test_queries_search_expert_assets_not_only_expert_names(self):
        queries = expert_asset_code_queries("中国 SaaS 定价")
        self.assertTrue(any("SKILL.md" in q for q in queries))
        self.assertTrue(any("path:agents" in q for q in queries))
        self.assertTrue(any("path:skills" in q for q in queries))

    def test_discovery_deduplicates_and_serializes_hits(self):
        result = discover_candidate_assets("中国 SaaS 定价", client=FakeClient(), per_query=3)
        self.assertEqual(len(result["repository_hits"]), 1)
        self.assertEqual(len(result["code_hits"]), 1)
        self.assertEqual(result["repository_hits"][0]["license"], "MIT")
        self.assertIn("Shadow", result["principle"])


if __name__ == "__main__":
    unittest.main()
