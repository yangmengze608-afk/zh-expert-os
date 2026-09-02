import json
import tempfile
import unittest
from pathlib import Path

from zh_expert_os.models import ArenaTask, Expert
from zh_expert_os.registry import Registry
from zh_expert_os.runtime import CallableRuntime
from zh_expert_os.trial import run_runtime_trial


class TrialTests(unittest.TestCase):
    def _root(self, td: str) -> Path:
        root = Path(td)
        (root / "registry").mkdir(parents=True)
        experts = [
            Expert("shadow-1", "游戏化候选专家", "0.1", "probation", "教育游戏化", "github:x/y", "MIT", "设计学习激励机制"),
            Expert("incumbent", "产品现任专家", "0.1", "active", "产品策略", "internal", "MIT", "设计和验证 MVP"),
        ]
        (root / "registry" / "experts.json").write_text(
            json.dumps({"experts": [e.to_dict() for e in experts]}, ensure_ascii=False), encoding="utf-8"
        )
        (root / "registry" / "matches.json").write_text(json.dumps({"matches": []}), encoding="utf-8")
        (root / "registry" / "arena.json").write_text(json.dumps({"battles": []}), encoding="utf-8")
        return root

    def test_trial_invokes_both_experts_and_reaches_judging(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            reg = Registry(root)
            seen = []

            def fn(inv):
                seen.append(inv.expert_id)
                return f"{inv.expert_name} 对任务的独立答案"

            result = run_runtime_trial(
                root,
                reg,
                ArenaTask("task-1", "设计学习抽卡宠物 MVP", "product", "normal"),
                "shadow-1",
                "incumbent",
                CallableRuntime(fn),
                parallel=False,
            )
            self.assertEqual(result["status"], "judging")
            self.assertTrue(result["judge_ready"])
            self.assertEqual(set(seen), {"shadow-1", "incumbent"})
            battle = json.loads((root / "registry" / "arena.json").read_text(encoding="utf-8"))["battles"][0]
            self.assertEqual(set(battle["submissions"]), {"A", "B"})
            self.assertNotEqual(battle["aliases"]["A"], battle["aliases"]["B"])


if __name__ == "__main__":
    unittest.main()
