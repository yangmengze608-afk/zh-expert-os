# Expert Runtime Bridge

v0.4-alpha1 开始，Zh Expert OS 不再只管理 Expert 配置：它可以真正调用一个外部 Agent Runtime，让两个 Expert 用独立 invocation 完成同一任务，并把输出自动送入 Eval Arena。

## 调用语义

- Skill：同一个 Agent 加载新的做事说明；
- Expert：以独立 invocation 运行一个角色；
- Team：多个 Expert invocation + 编排；
- Tool：Expert 在执行中调用的函数/API；
- Plugin：把上述能力注册/安装进宿主的分发形式。

本阶段实现的是 **Expert Runtime**，不是把 Skill 当成第二个 Agent。

## Runtime 契约

`CommandRuntime` 启动一个独立外部进程：

1. Zh Expert OS 根据 Expert 的名称、岗位、使命和 ArenaTask 生成输入；
2. Prompt 通过 stdin 发送给外部命令；
3. 外部命令的 stdout 视为专家答案；
4. 非零退出码、超时和空输出均 fail loud；
5. `shell=False`，用户任务不会被拼接进 shell 命令；
6. 两个 Expert 默认并行启动，因此在 CommandRuntime 下是两个独立进程。

Runtime 配置：

```json
{
  "type": "command",
  "command": ["python", "my_agent_adapter.py"],
  "timeout_seconds": 300
}
```

`my_agent_adapter.py` 只需要遵守：**stdin 读 Prompt，stdout 写最终答案**。因此 Claude/Codex/Gemini/Ollama/自建 API 都可以通过薄适配器接入，不把某一家平台写死在核心代码里。

## 真正的 Shadow Trial

先确保挑战者已经以 `probation` 身份登记，然后：

```bash
zh-expert-os runtime-trial \
  --task-file examples/arena/task-product.json \
  --challenger shadow-xxxx \
  --incumbent product-incumbent \
  --runtime-config runtime.json
```

执行链：

```text
ArenaTask
  ↓
Shadow Expert ──独立 Runtime──→ Output A/B
Incumbent    ──独立 Runtime──→ Output A/B
  ↓
Arena 自动匿名
  ↓
status = judging
```

随后继续使用已有的：

```bash
zh-expert-os arena-view --battle <id> --judge-id judge-1
zh-expert-os arena-judge --battle <id> --file judgment.json
zh-expert-os arena-finalize --battle <id>
```

## 治理边界

Runtime Trial **不会自动晋升任何人**。它只解决“让 Shadow 真的上岗干同一道题”。裁判、长期战绩、CAO 建议、Auditor 与人工批准仍保留。

此外，同一模型生成的多个 Judge 不能当作统计独立证据。若使用自动裁判，应该记录模型/版本/提示词，并尽可能采用不同 Judge 或人工抽检。
