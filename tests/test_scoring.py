import unittest

from zh_expert_os.models import MatchRecord, QualityScores
from zh_expert_os.scoring import posterior_summary, promotion_recommendation, weighted_quality


class ScoringTests(unittest.TestCase):
    def test_weighted_quality(self):
        scores = QualityScores(0.9, 0.9, 0.8, 0.8, 0.8, 0.8)
        q = weighted_quality(scores)
        self.assertGreater(q, 0.84)
        self.assertLess(q, 0.90)

    def test_posterior_prefers_dominant_challenger(self):
        summary = posterior_summary(MatchRecord("c", "i", 18, 2, 0), samples=10000)
        self.assertGreater(summary["posterior_mean"], 0.80)
        self.assertGreater(summary["prob_gt_threshold"], 0.99)

    def test_small_sample_blocks_promotion(self):
        scores = QualityScores(0.95, 0.95, 0.95, 0.9, 0.9, 0.9)
        rec = promotion_recommendation(MatchRecord("c", "i", 7, 1, 0), scores, min_total_tasks=20)
        self.assertNotEqual(rec["action"], "PROMOTE")
        self.assertTrue(any("总盲测任务不足" in x for x in rec["blockers"]))

    def test_critical_violation_rejects(self):
        scores = QualityScores(0.95, 0.95, 0.95, 0.9, 0.9, 0.9, critical_violations=1)
        rec = promotion_recommendation(MatchRecord("c", "i", 18, 2, 0), scores)
        self.assertEqual(rec["action"], "REJECT")


if __name__ == "__main__":
    unittest.main()
