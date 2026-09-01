from __future__ import annotations

import argparse
import json
from pathlib import Path

from .governance import build_personnel_case
from .models import Expert, MatchRecord, QualityScores
from .registry import Registry


def find_root() -> Path:
    here = Path.cwd()
    for candidate in [here, *here.parents]:
        if (candidate / "registry" / "experts.json").exists():
            return candidate
    package_root = Path(__file__).resolve().parents[2]
    if (package_root / "registry" / "experts.json").exists():
        return package_root
    raise RuntimeError("找不到项目根目录（缺少 registry/experts.json）")


def cmd_list(reg: Registry, _args: argparse.Namespace) -> None:
    print("ID\t状态\t中文名称\t岗位")
    for e in reg.list_experts():
        print(f"{e.id}\t{e.status}\t{e.name_zh}\t{e.role}")


def cmd_show(reg: Registry, args: argparse.Namespace) -> None:
    e = reg.get(args.expert_id)
    print(json.dumps(e.to_dict(), ensure_ascii=False, indent=2))


def cmd_recruit(reg: Registry, args: argparse.Namespace) -> None:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    reg.recruit(Expert(**data))
    print(f"已登记候选专家：{data['name_zh']} ({data['id']})")


def cmd_record_match(reg: Registry, args: argparse.Namespace) -> None:
    for expert_id in (args.challenger, args.incumbent):
        reg.get(expert_id)
    match = MatchRecord(args.challenger, args.incumbent, args.wins, args.losses, args.ties)
    reg.record_match(match)
    print(f"已记录挑战赛：{args.challenger} vs {args.incumbent} = {args.wins}-{args.losses}-{args.ties}")


def cmd_recommendation(reg: Registry, args: argparse.Namespace) -> None:
    reg.get(args.challenger)
    reg.get(args.incumbent)
    match = reg.aggregate_match(args.challenger, args.incumbent)
    scores = QualityScores(
        task_quality=args.task_quality,
        factuality=args.factuality,
        stability=args.stability,
        independence=args.independence,
        cost_efficiency=args.cost_efficiency,
        user_adoption=args.user_adoption,
        critical_violations=args.critical_violations,
    )
    case = build_personnel_case(match, scores)
    print(json.dumps(case, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="zh-expert-os", description="中文 AI 专家团治理 CLI")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出专家")

    show = sub.add_parser("show", help="查看专家")
    show.add_argument("expert_id")

    recruit = sub.add_parser("recruit", help="登记候选专家")
    recruit.add_argument("file")

    match = sub.add_parser("record-match", help="记录同任务盲测胜负")
    match.add_argument("--challenger", required=True)
    match.add_argument("--incumbent", required=True)
    match.add_argument("--wins", type=int, required=True)
    match.add_argument("--losses", type=int, required=True)
    match.add_argument("--ties", type=int, default=0)

    rec = sub.add_parser("recommendation", help="生成 CAO 人事建议")
    rec.add_argument("--challenger", required=True)
    rec.add_argument("--incumbent", required=True)
    rec.add_argument("--task-quality", type=float, default=0.85)
    rec.add_argument("--factuality", type=float, default=0.90)
    rec.add_argument("--stability", type=float, default=0.85)
    rec.add_argument("--independence", type=float, default=0.80)
    rec.add_argument("--cost-efficiency", type=float, default=0.80)
    rec.add_argument("--user-adoption", type=float, default=0.80)
    rec.add_argument("--critical-violations", type=int, default=0)
    return p


def main() -> None:
    args = build_parser().parse_args()
    reg = Registry(find_root())
    if args.command == "list":
        cmd_list(reg, args)
    elif args.command == "show":
        cmd_show(reg, args)
    elif args.command == "recruit":
        cmd_recruit(reg, args)
    elif args.command == "record-match":
        cmd_record_match(reg, args)
    elif args.command == "recommendation":
        cmd_recommendation(reg, args)


if __name__ == "__main__":
    main()
