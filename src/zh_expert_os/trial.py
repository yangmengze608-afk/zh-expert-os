from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .arena_registry import ArenaRegistry
from .models import ArenaTask
from .registry import Registry
from .runtime import AgentRuntime, build_invocation


def run_runtime_trial(
    root: Path,
    registry: Registry,
    task: ArenaTask,
    challenger: str,
    incumbent: str,
    runtime: AgentRuntime,
    *,
    battle_id: str | None = None,
    context: str = "",
    parallel: bool = True,
) -> dict:
    """真正执行挑战者与现任，并把两份输出直接送入匿名 Arena。

    两个 Expert 使用各自独立 invocation；CommandRuntime 下会启动两个独立进程。
    本函数只推进到 judging，不自动裁判或晋升。
    """
    challenger_expert = registry.get(challenger)
    incumbent_expert = registry.get(incumbent)
    if challenger_expert.status not in {"candidate", "probation", "active", "bench", "governance"}:
        raise ValueError("挑战者状态不可执行")
    if incumbent_expert.status not in {"active", "bench", "governance", "probation"}:
        raise ValueError("现任状态不可执行")

    arena = ArenaRegistry(root)
    battle = arena.create_battle(registry, task, challenger, incumbent, battle_id)
    experts = [challenger_expert, incumbent_expert]

    results = {}
    if parallel:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {
                pool.submit(runtime.invoke, build_invocation(expert, task, context)): expert.id
                for expert in experts
            }
            for future in as_completed(futures):
                expert_id = futures[future]
                results[expert_id] = future.result()
    else:
        for expert in experts:
            results[expert.id] = runtime.invoke(build_invocation(expert, task, context))

    accepted = {}
    for expert in experts:
        result = results[expert.id]
        alias = arena.submit(
            battle,
            expert.id,
            result.content,
            latency_ms=result.latency_ms,
            cost_units=result.cost_units,
        )
        accepted[expert.id] = {
            "alias": alias,
            "latency_ms": result.latency_ms,
            "runtime": result.runtime,
        }

    state = arena.get(battle)
    return {
        "battle_id": battle,
        "status": state["status"],
        "challenger": challenger,
        "incumbent": incumbent,
        "submissions": accepted,
        "judge_ready": state["status"] == "judging",
        "next_step": "使用 arena-view 生成匿名 Judge packet；完成至少 3 个 Judge 后 arena-finalize。",
    }
