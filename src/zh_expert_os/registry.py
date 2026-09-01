from __future__ import annotations

import json
from pathlib import Path

from .models import Expert, MatchRecord


class Registry:
    def __init__(self, root: Path):
        self.root = root
        self.experts_path = root / "registry" / "experts.json"
        self.matches_path = root / "registry" / "matches.json"

    @staticmethod
    def _load(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _save(path: Path, data: dict) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    def list_experts(self) -> list[Expert]:
        data = self._load(self.experts_path)
        return [Expert(**item) for item in data["experts"]]

    def get(self, expert_id: str) -> Expert:
        for expert in self.list_experts():
            if expert.id == expert_id:
                return expert
        raise KeyError(f"未找到专家：{expert_id}")

    def recruit(self, expert: Expert) -> None:
        if expert.status not in {"candidate", "probation"}:
            raise ValueError("新招聘专家必须以 candidate 或 probation 身份进入")
        data = self._load(self.experts_path)
        existing = {e["id"] for e in data["experts"]}
        if expert.id in existing:
            raise ValueError(f"专家 ID 已存在：{expert.id}")
        data["experts"].append(expert.to_dict())
        self._save(self.experts_path, data)

    def change_status(self, expert_id: str, new_status: str) -> None:
        data = self._load(self.experts_path)
        found = False
        for e in data["experts"]:
            if e["id"] == expert_id:
                if e["status"] == "governance":
                    raise PermissionError("治理专家不能通过普通状态变更接口被修改")
                e["status"] = new_status
                found = True
                break
        if not found:
            raise KeyError(f"未找到专家：{expert_id}")
        self._save(self.experts_path, data)

    def record_match(self, match: MatchRecord) -> bool:
        data = self._load(self.matches_path)
        if match.source_battle_id:
            for row in data["matches"]:
                if row.get("source_battle_id") == match.source_battle_id:
                    return False
        row = {
            "challenger": match.challenger,
            "incumbent": match.incumbent,
            "wins": match.wins,
            "losses": match.losses,
            "ties": match.ties,
        }
        if match.source_battle_id:
            row["source_battle_id"] = match.source_battle_id
        data["matches"].append(row)
        self._save(self.matches_path, data)
        return True

    def aggregate_match(self, challenger: str, incumbent: str) -> MatchRecord:
        data = self._load(self.matches_path)
        wins = losses = ties = 0
        for row in data["matches"]:
            if row["challenger"] == challenger and row["incumbent"] == incumbent:
                wins += row["wins"]
                losses += row["losses"]
                ties += row.get("ties", 0)
        return MatchRecord(challenger, incumbent, wins, losses, ties)
