from __future__ import annotations

import json
import shlex
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Protocol

from .models import ArenaTask, Expert


@dataclass(slots=True)
class AgentInvocation:
    expert_id: str
    expert_name: str
    role: str
    mission: str
    task: dict
    context: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class AgentResult:
    expert_id: str
    content: str
    latency_ms: int
    cost_units: float | None = None
    runtime: str = "unknown"

    def to_dict(self) -> dict:
        return asdict(self)


class AgentRuntime(Protocol):
    name: str

    def invoke(self, invocation: AgentInvocation) -> AgentResult:
        ...


class RuntimeExecutionError(RuntimeError):
    pass


def build_invocation(expert: Expert, task: ArenaTask, context: str = "") -> AgentInvocation:
    task.validate()
    return AgentInvocation(
        expert_id=expert.id,
        expert_name=expert.name_zh,
        role=expert.role,
        mission=expert.mission,
        task=task.to_dict(),
        context=context,
    )


def render_expert_prompt(invocation: AgentInvocation) -> str:
    """把 Expert 配置转成一次独立 Agent 调用的输入。

    不把来源仓库、许可证、Arena 身份等信息写入 Prompt，避免给执行模型造成不必要偏差。
    """
    task = invocation.task
    blocks = [
        f"你现在作为独立专家工作。\n专家名称：{invocation.expert_name}\n岗位：{invocation.role}",
    ]
    if invocation.mission.strip():
        blocks.append(f"职责：{invocation.mission.strip()}")
    blocks.append(
        "当前任务：\n"
        f"任务 ID：{task.get('id', '')}\n"
        f"类别：{task.get('category', 'general')}\n"
        f"风险等级：{task.get('risk_level', 'normal')}\n"
        f"用户任务：{task.get('prompt', '')}"
    )
    if invocation.context.strip():
        blocks.append(f"可用上下文：\n{invocation.context.strip()}")
    blocks.append(
        "要求：直接完成任务。明确区分事实、推断和不确定性；需要证据时说明验证路径。"
        "不要讨论你在竞技场中的身份，也不要根据其他候选人的表现调整答案。"
    )
    return "\n\n".join(blocks)


class CallableRuntime:
    """测试或宿主集成用 Runtime。每次 invoke 都由调用方提供的函数独立处理。"""

    name = "callable"

    def __init__(self, fn: Callable[[AgentInvocation], str]):
        self.fn = fn

    def invoke(self, invocation: AgentInvocation) -> AgentResult:
        started = time.perf_counter()
        content = self.fn(invocation)
        latency_ms = max(0, round((time.perf_counter() - started) * 1000))
        if not str(content).strip():
            raise RuntimeExecutionError("Runtime 返回了空内容")
        return AgentResult(invocation.expert_id, str(content), latency_ms, runtime=self.name)


class CommandRuntime:
    """通过外部 CLI 启动一个独立 Agent 进程。

    JSON/文本 Prompt 通过 stdin 发送，stdout 作为专家输出。使用 shell=False，避免把用户任务拼进 shell。
    这使 Claude Code、Codex CLI、Gemini CLI、Ollama wrapper 等都能通过适配脚本接入。
    """

    name = "command"

    def __init__(self, command: list[str], timeout_seconds: float = 300.0, cwd: str | None = None):
        if not command or not all(str(x).strip() for x in command):
            raise ValueError("command 不能为空")
        self.command = [str(x) for x in command]
        self.timeout_seconds = timeout_seconds
        self.cwd = cwd

    def invoke(self, invocation: AgentInvocation) -> AgentResult:
        prompt = render_expert_prompt(invocation)
        started = time.perf_counter()
        try:
            proc = subprocess.run(
                self.command,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                cwd=self.cwd,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeExecutionError(f"Agent 运行超时：{self.timeout_seconds}s") from exc
        except OSError as exc:
            raise RuntimeExecutionError(f"无法启动 Agent Runtime：{exc}") from exc
        latency_ms = max(0, round((time.perf_counter() - started) * 1000))
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()[:1000]
            raise RuntimeExecutionError(f"Agent Runtime 退出码 {proc.returncode}: {stderr}")
        content = (proc.stdout or "").strip()
        if not content:
            raise RuntimeExecutionError("Agent Runtime stdout 为空")
        return AgentResult(invocation.expert_id, content, latency_ms, runtime=self.name)


def load_runtime_config(path: Path) -> AgentRuntime:
    data = json.loads(path.read_text(encoding="utf-8"))
    runtime_type = data.get("type")
    if runtime_type != "command":
        raise ValueError("当前可配置 Runtime 仅支持 type=command；测试可直接使用 CallableRuntime")
    command = data.get("command")
    if isinstance(command, str):
        command = shlex.split(command)
    if not isinstance(command, list):
        raise ValueError("runtime config 的 command 必须是字符串或字符串数组")
    return CommandRuntime(
        [str(x) for x in command],
        timeout_seconds=float(data.get("timeout_seconds", 300)),
        cwd=data.get("cwd"),
    )
