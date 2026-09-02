import json
import sys
import tempfile
import unittest
from pathlib import Path

from zh_expert_os.models import ArenaTask, Expert
from zh_expert_os.runtime import (
    CallableRuntime,
    CommandRuntime,
    RuntimeExecutionError,
    build_invocation,
    load_runtime_config,
    render_expert_prompt,
)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.expert = Expert(
            "product",
            "产品专家",
            "0.1",
            "active",
            "产品策略",
            "internal",
            "MIT",
            "判断产品是否值得做，并给出可验证 MVP",
        )
        self.task = ArenaTask("task-1", "判断学习抽卡宠物产品是否值得做", "product", "normal")

    def test_prompt_contains_role_and_task_but_not_source(self):
        invocation = build_invocation(self.expert, self.task)
        prompt = render_expert_prompt(invocation)
        self.assertIn("产品策略", prompt)
        self.assertIn("学习抽卡宠物", prompt)
        self.assertNotIn("internal", prompt)
        self.assertNotIn("MIT", prompt)

    def test_callable_runtime_returns_result(self):
        runtime = CallableRuntime(lambda inv: f"完成：{inv.task['prompt']}")
        result = runtime.invoke(build_invocation(self.expert, self.task))
        self.assertIn("完成", result.content)
        self.assertEqual(result.expert_id, "product")

    def test_command_runtime_uses_stdin_and_stdout(self):
        runtime = CommandRuntime(
            [sys.executable, "-c", "import sys; data=sys.stdin.read(); print('OK:' + data[:20])"],
            timeout_seconds=5,
        )
        result = runtime.invoke(build_invocation(self.expert, self.task))
        self.assertTrue(result.content.startswith("OK:"))

    def test_nonzero_command_fails_loudly(self):
        runtime = CommandRuntime([sys.executable, "-c", "import sys; print('bad', file=sys.stderr); raise SystemExit(3)"])
        with self.assertRaises(RuntimeExecutionError):
            runtime.invoke(build_invocation(self.expert, self.task))

    def test_load_command_runtime_config(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "runtime.json"
            path.write_text(json.dumps({"type": "command", "command": [sys.executable, "-c", "print('x')"]}), encoding="utf-8")
            runtime = load_runtime_config(path)
            self.assertIsInstance(runtime, CommandRuntime)


if __name__ == "__main__":
    unittest.main()
