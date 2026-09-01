import json
import tempfile
import unittest
from pathlib import Path

from zh_expert_os.models import Expert, MatchRecord
from zh_expert_os.registry import Registry


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "registry").mkdir()
        (root / "registry" / "experts.json").write_text(
            json.dumps({"schema_version": "0.1", "experts": [{
                "id": "gov", "name_zh": "治理", "version": "0.1.0", "status": "governance",
                "role": "governance", "source": "original", "license": "MIT", "mission": ""
            }]}, ensure_ascii=False), encoding="utf-8"
        )
        (root / "registry" / "matches.json").write_text(
            json.dumps({"schema_version": "0.2", "matches": []}), encoding="utf-8"
        )
        self.reg = Registry(root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_recruit_candidate(self):
        expert = Expert("candidate-a", "候选A", "0.1.0", "candidate", "demo", "original", "MIT")
        self.reg.recruit(expert)
        self.assertEqual(self.reg.get("candidate-a").name_zh, "候选A")

    def test_governance_cannot_be_changed_normally(self):
        with self.assertRaises(PermissionError):
            self.reg.change_status("gov", "retired")

    def test_match_aggregation(self):
        self.reg.record_match(MatchRecord("c", "i", 3, 2, 1))
        self.reg.record_match(MatchRecord("c", "i", 4, 1, 0))
        agg = self.reg.aggregate_match("c", "i")
        self.assertEqual((agg.wins, agg.losses, agg.ties), (7, 3, 1))

    def test_source_battle_is_idempotent(self):
        self.reg.record_match(MatchRecord("c", "i", 1, 0, 0, "battle-x"))
        inserted = self.reg.record_match(MatchRecord("c", "i", 1, 0, 0, "battle-x"))
        self.assertFalse(inserted)
        self.assertEqual(self.reg.aggregate_match("c", "i").wins, 1)


if __name__ == "__main__":
    unittest.main()
