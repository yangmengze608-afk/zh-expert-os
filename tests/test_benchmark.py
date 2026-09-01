import tempfile
import unittest
from pathlib import Path

from zh_expert_os.benchmark import load_jsonl_tasks


class BenchmarkTests(unittest.TestCase):
    def test_load_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "tasks.jsonl"
            p.write_text('{"id":"a","prompt":"任务A"}\n{"id":"b","prompt":"任务B","category":"product"}\n', encoding="utf-8")
            tasks = load_jsonl_tasks(p)
            self.assertEqual([t.id for t in tasks], ["a", "b"])

    def test_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "tasks.jsonl"
            p.write_text('{"id":"a","prompt":"1"}\n{"id":"a","prompt":"2"}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_jsonl_tasks(p)


if __name__ == "__main__":
    unittest.main()
