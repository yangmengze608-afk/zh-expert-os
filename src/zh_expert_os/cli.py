from __future__ import annotations

import argparse
import json
from pathlib import Path

from .arena_registry import ArenaRegistry
from .benchmark import load_jsonl_tasks
from .governance import build_personnel_case
from .models import ArenaJudgment, ArenaTask, Expert, MatchRecord, QualityScores
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


def cmd_benchmark_validate(args: argparse.Namespace) -> None:
    tasks = load_jsonl_tasks(Path(args.file))
    print(json.dumps({"valid": True, "task_count": len(tasks), "task_ids": [t.id for t in tasks]}, ensure_ascii=False, indent=2))


def _load_task(path: str) -> ArenaTask:
    return ArenaTask(**json.loads(Path(path).read_text(encoding="utf-8")))


def cmd_arena_create(root: Path, reg: Registry, args: argparse.Namespace) -> None:
    arena = ArenaRegistry(root)
    task = _load_task(args.task_file)
    battle_id = arena.create_battle(reg, task, args.challenger, args.incumbent, args.battle_id)
    battle = arena.get(battle_id)
    print(json.dumps({"battle_id": battle_id, "status": battle["status"], "task_fingerprint": battle["task_fingerprint"]}, ensure_ascii=False, indent=2))


def cmd_arena_seed(root: Path, reg: Registry, args: argparse.Namespace) -> None:
    arena = ArenaRegistry(root)
    tasks = load_jsonl_tasks(Path(args.file))
    created = []
    for task in tasks:
        created.append(arena.create_battle(reg, task, args.challenger, args.incumbent))
    print(json.dumps({"created": len(created), "battle_ids": created}, ensure_ascii=False, indent=2))


def cmd_arena_submit(root: Path, args: argparse.Namespace) -> None:
    arena = ArenaRegistry(root)
    content = Path(args.file).read_text(encoding="utf-8")
    alias = arena.submit(args.battle, args.expert, content, latency_ms=args.latency_ms, cost_units=args.cost_units)
    print(json.dumps({"battle_id": args.battle, "accepted_as": alias}, ensure_ascii=False, indent=2))


def cmd_arena_view(root: Path, args: argparse.Namespace) -> None:
    packet = ArenaRegistry(root).judge_packet(args.battle, args.judge_id)
    print(json.dumps(packet, ensure_ascii=False, indent=2))


def cmd_arena_judge(root: Path, args: argparse.Namespace) -> None:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    judgment = ArenaJudgment.from_dict(data)
    if judgment.battle_id != args.battle:
        raise ValueError("judgment 文件中的 battle_id 与命令参数不一致")
    ArenaRegistry(root).add_judgment(judgment)
    print(json.dumps({"battle_id": args.battle, "judge_id": judgment.judge_id, "accepted": True}, ensure_ascii=False, indent=2))


def cmd_arena_finalize(root: Path, reg: Registry, args: argparse.Namespace) -> None:
    result = ArenaRegistry(root).finalize_and_record(args.battle, reg, min_judges=args.min_judges)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_arena_show(root: Path, args: argparse.Namespace) -> None:
    battle = ArenaRegistry(root).get(args.battle)
    safe = {
        "id": battle["id"],
        "task": battle["task"],
        "challenger": battle["challenger"],
        "incumbent": battle["incumbent"],
        "status": battle["status"],
        "submission_count": len(battle["submissions"]),
        "judge_count": len(battle["judgments"]),
        "result": battle["result"],
        "match_recorded": battle["match_recorded"],
    }
    print(json.dumps(safe, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="zh-expert-os", description="中文 AI 专家团治理与 Eval Arena CLI")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出专家")

    show = sub.add_parser("show", help="查看专家")
    show.add_argument("expert_id")

    recruit = sub.add_parser("recruit", help="登记候选专家")
    recruit.add_argument("file")

    match = sub.add_parser("record-match", help="手动记录同任务盲测胜负")
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

    bv = sub.add_parser("benchmark-validate", help="校验 JSONL benchmark")
    bv.add_argument("file")

    ac = sub.add_parser("arena-create", help="创建一个匿名 A/B battle")
    ac.add_argument("--task-file", required=True)
    ac.add_argument("--challenger", required=True)
    ac.add_argument("--incumbent", required=True)
    ac.add_argument("--battle-id")

    seed = sub.add_parser("arena-seed", help="从 JSONL benchmark 批量创建 battle")
    seed.add_argument("--file", required=True)
    seed.add_argument("--challenger", required=True)
    seed.add_argument("--incumbent", required=True)

    submit = sub.add_parser("arena-submit", help="提交专家输出")
    submit.add_argument("--battle", required=True)
    submit.add_argument("--expert", required=True)
    submit.add_argument("--file", required=True)
    submit.add_argument("--latency-ms", type=int)
    submit.add_argument("--cost-units", type=float)

    view = sub.add_parser("arena-view", help="生成匿名 Judge packet")
    view.add_argument("--battle", required=True)
    view.add_argument("--judge-id", required=True)

    judge = sub.add_parser("arena-judge", help="提交 Judge 评分 JSON")
    judge.add_argument("--battle", required=True)
    judge.add_argument("--file", required=True)

    fin = sub.add_parser("arena-finalize", help="聚合多 Judge 结果并写入长期战绩")
    fin.add_argument("--battle", required=True)
    fin.add_argument("--min-judges", type=int, default=3)

    ashow = sub.add_parser("arena-show", help="查看 battle 状态")
    ashow.add_argument("--battle", required=True)
    return p


def main() -> None:
    args = build_parser().parse_args()
    root = find_root()
    reg = Registry(root)
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
    elif args.command == "benchmark-validate":
        cmd_benchmark_validate(args)
    elif args.command == "arena-create":
        cmd_arena_create(root, reg, args)
    elif args.command == "arena-seed":
        cmd_arena_seed(root, reg, args)
    elif args.command == "arena-submit":
        cmd_arena_submit(root, args)
    elif args.command == "arena-view":
        cmd_arena_view(root, args)
    elif args.command == "arena-judge":
        cmd_arena_judge(root, args)
    elif args.command == "arena-finalize":
        cmd_arena_finalize(root, reg, args)
    elif args.command == "arena-show":
        cmd_arena_show(root, args)


if __name__ == "__main__":
    main()
