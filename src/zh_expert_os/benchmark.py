from __future__ import annotations

import json
from pathlib import Path

from .models import ArenaTask


def load_jsonl_tasks(path: Path) -> list[ArenaTask]:
    tasks: list[ArenaTask] = []
    seen: set[str] = set()
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSONL 第 {line_no} 行不是合法 JSON：{exc.msg}") from exc
        task = ArenaTask(**data)
        task.validate()
        if task.id in seen:
            raise ValueError(f"JSONL 存在重复 task id：{task.id}")
        seen.add(task.id)
        tasks.append(task)
    if not tasks:
        raise ValueError("benchmark 不能为空")
    return tasks
