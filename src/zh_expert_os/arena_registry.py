from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .arena import (
    aggregate_judgments,
    alias_assignment,
    expected_presentation_order,
    task_fingerprint,
)
from .models import ArenaJudgment, ArenaTask, MatchRecord
from .registry import Registry


class ArenaRegistry:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / "registry" / "arena.json"
        if not self.path.exists():
            raise FileNotFoundError("缺少 registry/arena.json；请使用 v0.2 初始化文件")

    @staticmethod
    def _load(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _save(path: Path, data: dict) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    def list_battles(self) -> list[dict]:
        return self._load(self.path)["battles"]

    def get(self, battle_id: str) -> dict:
        for battle in self.list_battles():
            if battle["id"] == battle_id:
                return battle
        raise KeyError(f"未找到 Arena battle：{battle_id}")

    def _battle_id(self, task: ArenaTask, challenger: str, incumbent: str) -> str:
        raw = f"{task_fingerprint(task)}:{challenger}:{incumbent}"
        return "battle-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def create_battle(
        self,
        registry: Registry,
        task: ArenaTask,
        challenger: str,
        incumbent: str,
        battle_id: str | None = None,
    ) -> str:
        task.validate()
        registry.get(challenger)
        registry.get(incumbent)
        if challenger == incumbent:
            raise ValueError("挑战者和现任不能相同")
        battle_id = battle_id or self._battle_id(task, challenger, incumbent)
        data = self._load(self.path)
        if any(b["id"] == battle_id for b in data["battles"]):
            raise ValueError(f"Battle ID 已存在：{battle_id}")
        data["battles"].append({
            "id": battle_id,
            "task": task.to_dict(),
            "task_fingerprint": task_fingerprint(task),
            "challenger": challenger,
            "incumbent": incumbent,
            "aliases": alias_assignment(battle_id, challenger, incumbent),
            "status": "collecting",
            "submissions": {},
            "judgments": [],
            "result": None,
            "match_recorded": False,
        })
        self._save(self.path, data)
        return battle_id

    def submit(
        self,
        battle_id: str,
        expert_id: str,
        content: str,
        *,
        latency_ms: int | None = None,
        cost_units: float | None = None,
    ) -> str:
        if not content.strip():
            raise ValueError("提交内容不能为空")
        data = self._load(self.path)
        for battle in data["battles"]:
            if battle["id"] != battle_id:
                continue
            if battle["status"] == "finalized":
                raise ValueError("已结束的 battle 不能再提交")
            inverse = {v: k for k, v in battle["aliases"].items()}
            if expert_id not in inverse:
                raise ValueError("该专家不属于此 battle")
            alias = inverse[expert_id]
            if alias in battle["submissions"]:
                raise ValueError(f"{alias} 已提交，禁止覆盖")
            battle["submissions"][alias] = {
                "content": content,
                "latency_ms": latency_ms,
                "cost_units": cost_units,
            }
            if set(battle["submissions"]) == {"A", "B"}:
                battle["status"] = "judging"
            self._save(self.path, data)
            return alias
        raise KeyError(f"未找到 Arena battle：{battle_id}")

    def judge_packet(self, battle_id: str, judge_id: str) -> dict:
        battle = self.get(battle_id)
        if set(battle["submissions"]) != {"A", "B"}:
            raise ValueError("A/B 尚未全部提交")
        order = expected_presentation_order(battle_id, judge_id)
        aliases = list(order)
        return {
            "battle_id": battle_id,
            "task": battle["task"],
            "task_fingerprint": battle["task_fingerprint"],
            "judge_id": judge_id,
            "presentation_order": order,
            "outputs": [
                {"alias": alias, "content": battle["submissions"][alias]["content"]}
                for alias in aliases
            ],
            "rubric": {
                "task_completion": "是否完成用户真实任务",
                "factuality": "事实正确、不过度断言",
                "evidence_quality": "证据、验证路径与不确定性处理",
                "chinese_native": "是否真正适合中文用户与中国语境",
                "clarity": "表达清楚、直接、可执行",
            },
        }

    def add_judgment(self, judgment: ArenaJudgment) -> None:
        judgment.validate()
        expected = expected_presentation_order(judgment.battle_id, judgment.judge_id)
        if judgment.presentation_order != expected:
            raise ValueError(
                f"presentation_order 与盲测分配不一致：应为 {expected}，收到 {judgment.presentation_order}"
            )
        data = self._load(self.path)
        for battle in data["battles"]:
            if battle["id"] != judgment.battle_id:
                continue
            if battle["status"] != "judging":
                raise ValueError("battle 还未进入 judging 或已经结束")
            if any(j["judge_id"] == judgment.judge_id for j in battle["judgments"]):
                raise ValueError(f"Judge 已评分：{judgment.judge_id}")
            battle["judgments"].append(judgment.to_dict())
            self._save(self.path, data)
            return
        raise KeyError(f"未找到 Arena battle：{judgment.battle_id}")

    def finalize_and_record(self, battle_id: str, registry: Registry, *, min_judges: int = 3) -> dict:
        data = self._load(self.path)
        target = None
        for battle in data["battles"]:
            if battle["id"] == battle_id:
                target = battle
                break
        if target is None:
            raise KeyError(f"未找到 Arena battle：{battle_id}")

        if target["result"] is None:
            judgments = [ArenaJudgment.from_dict(x) for x in target["judgments"]]
            aggregate = aggregate_judgments(judgments, min_judges=min_judges)
            if not aggregate.get("ready"):
                raise ValueError(aggregate["reason"])
            winner_alias = aggregate["winner_alias"]
            if winner_alias == "TIE":
                outcome = "tie"
                match = MatchRecord(target["challenger"], target["incumbent"], 0, 0, 1, battle_id)
            else:
                winner_id = target["aliases"][winner_alias]
                if winner_id == target["challenger"]:
                    outcome = "challenger_win"
                    match = MatchRecord(target["challenger"], target["incumbent"], 1, 0, 0, battle_id)
                else:
                    outcome = "incumbent_win"
                    match = MatchRecord(target["challenger"], target["incumbent"], 0, 1, 0, battle_id)
            target["result"] = {
                "outcome": outcome,
                "winner_alias": winner_alias,
                "aggregate": aggregate,
            }
            target["status"] = "finalized"
        else:
            outcome = target["result"]["outcome"]
            if outcome == "challenger_win":
                match = MatchRecord(target["challenger"], target["incumbent"], 1, 0, 0, battle_id)
            elif outcome == "incumbent_win":
                match = MatchRecord(target["challenger"], target["incumbent"], 0, 1, 0, battle_id)
            else:
                match = MatchRecord(target["challenger"], target["incumbent"], 0, 0, 1, battle_id)

        self._save(self.path, data)
        inserted = registry.record_match(match)

        data = self._load(self.path)
        for battle in data["battles"]:
            if battle["id"] == battle_id:
                battle["match_recorded"] = True
                result = battle["result"]
                break
        self._save(self.path, data)
        return {**result, "match_inserted": inserted}
