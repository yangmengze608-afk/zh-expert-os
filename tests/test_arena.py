import json
import tempfile
import unittest
from pathlib import Path

from zh_expert_os.arena import aggregate_judgments, judgment_preference
from zh_expert_os.arena_registry import ArenaRegistry
from zh_expert_os.models import ArenaJudgment, ArenaTask, JudgeScores
from zh_expert_os.registry import Registry


def score(v: float, critical: int = 0) -> JudgeScores:
    return JudgeScores(v, v, v, v, v, critical)


class ArenaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "registry").mkdir()
        experts = {
            "schema_version": "0.2",
            "experts": [
                {"id":"c","name_zh":"候选","version":"0.2","status":"probation","role":"x","source":"original","license":"MIT","mission":""},
                {"id":"i","name_zh":"现任","version":"0.2","status":"active","role":"x","source":"original","license":"MIT","mission":""},
            ],
        }
        (self.root / "registry" / "experts.json").write_text(json.dumps(experts), encoding="utf-8")
        (self.root / "registry" / "matches.json").write_text('{"schema_version":"0.2","matches":[]}', encoding="utf-8")
        (self.root / "registry" / "arena.json").write_text('{"schema_version":"0.2","battles":[]}', encoding="utf-8")
        self.reg = Registry(self.root)
        self.arena = ArenaRegistry(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_critical_violation_is_hard_loss(self):
        j = ArenaJudgment("b", "judge", "AB", score(0.99, 1), score(0.70, 0))
        self.assertEqual(judgment_preference(j), "B")

    def test_judge_packet_hides_expert_identity(self):
        battle = self.arena.create_battle(self.reg, ArenaTask("t1", "分析这个产品是否值得做", "product"), "c", "i")
        self.arena.submit(battle, "c", "候选输出")
        self.arena.submit(battle, "i", "现任输出")
        packet = self.arena.judge_packet(battle, "judge-1")
        dumped = json.dumps(packet, ensure_ascii=False)
        self.assertNotIn('"c"', dumped)
        self.assertNotIn('"i"', dumped)
        self.assertIn("候选输出", dumped)
        self.assertIn("现任输出", dumped)

    def test_aggregate_requires_three_judges(self):
        j = ArenaJudgment("b", "j1", "AB", score(0.9), score(0.7))
        result = aggregate_judgments([j], min_judges=3)
        self.assertFalse(result["ready"])

    def test_finalize_records_exactly_once(self):
        battle = self.arena.create_battle(self.reg, ArenaTask("t2", "给出一个市场进入方案", "business"), "c", "i")
        self.arena.submit(battle, "c", "C output")
        self.arena.submit(battle, "i", "I output")
        aliases = self.arena.get(battle)["aliases"]
        challenger_alias = next(alias for alias, expert in aliases.items() if expert == "c")
        for judge_id in ("j1", "j2", "j3"):
            packet = self.arena.judge_packet(battle, judge_id)
            if challenger_alias == "A":
                a, b = score(0.94), score(0.70)
            else:
                a, b = score(0.70), score(0.94)
            self.arena.add_judgment(ArenaJudgment(battle, judge_id, packet["presentation_order"], a, b))
        first = self.arena.finalize_and_record(battle, self.reg)
        second = self.arena.finalize_and_record(battle, self.reg)
        agg = self.reg.aggregate_match("c", "i")
        self.assertEqual(first["outcome"], "challenger_win")
        self.assertTrue(first["match_inserted"])
        self.assertFalse(second["match_inserted"])
        self.assertEqual((agg.wins, agg.losses, agg.ties), (1, 0, 0))

    def test_wrong_presentation_order_is_rejected(self):
        battle = self.arena.create_battle(self.reg, ArenaTask("t3", "test"), "c", "i")
        self.arena.submit(battle, "c", "C")
        self.arena.submit(battle, "i", "I")
        packet = self.arena.judge_packet(battle, "judge-x")
        wrong = "BA" if packet["presentation_order"] == "AB" else "AB"
        with self.assertRaises(ValueError):
            self.arena.add_judgment(ArenaJudgment(battle, "judge-x", wrong, score(0.9), score(0.8)))


if __name__ == "__main__":
    unittest.main()
