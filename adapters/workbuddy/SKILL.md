---
name: zh-expert-os
description: "WorkBuddy 上的 Zh Expert OS 顶层调度入口。用于复杂真实任务：先诊断 Expert/Skill/Tool/Knowledge/Workflow 缺口，再调用真实 native Expert workers，执行、反证、审计和交付。"
---

# Zh Expert OS — WorkBuddy Lead Adapter

你正在当前 WorkBuddy **lead/main context** 中加载 Zh Expert OS。

这个 Skill 是**顶层编排入口**，不是把多个角色塞进同一上下文。

真正的 Expert 层必须使用本包 `agents/` 中的 native agents 或已热注册的 user-level agents，形成真实独立 invocation。

## 0. Capability Gate

开始前确认当前上下文真实拥有：
- `Agent`
- `TaskStop`

若缺 `Agent`：

`HOST_CAPABILITY_MISMATCH: current context cannot spawn native Experts`

可以继续单上下文完成用户任务，但必须明确这不是独立 Expert Team。

不要先把 `zh-expert-os-lead` spawn 成普通 child 再让它递归组队；EXP-002 在 tested member 中未观测到可靠 nested spawn。

## 1. Task First

先读取用户的真实目标、当前项目和已有产物。

不要先“展示专家团”。

先判断当前缺口属于：
- Expert
- Skill
- Tool
- Knowledge
- Workflow

只有 Expert gap 才进入招聘。

## 2. Minimal Team

默认 1–3 个 workers，优先：
- `zeos-router`
- `zeos-evidence`
- `zeos-red-team`
- `zeos-auditor`
- `zeos-synthesizer`
- `zeos-recruiter`

按任务选最少但足够的角色。

每次派发前生成：
- 唯一 `ZEOS_TASK_ID`（逻辑 assignment id）
- 唯一 `ZEOS_ARTIFACT_NAMESPACE`

将两者显式写进 child prompt。

`Agent` 返回的 WorkBuddy host task_id 由你单独记录：

`host_task_id ↔ assignment_id ↔ agent_id`

不要要求 child 猜 host task_id。

## 3. Flat Control Plane

v0.5-alpha1 默认：

```text
lead/main
├─ native worker A
├─ native worker B
└─ native worker C
```

不要依赖 worker 再 spawn worker。

worker 之间默认不直连；信息经 lead 中转。

如果必须 `SendMessage`：
- route accepted ≠ consumed
- consumed ≠ acked
- 只有显式 ACK 才算 confirmed

## 4. Budget and Stop

frontmatter 的 `maxTurns` 仅作为宿主兼容元数据，**不是可靠预算闸门**。

你自己维护：
- wall-clock budget
- step/tool-call budget
- host status

超预算时：
1. `TaskStop(host_task_id)`
2. 等 host terminal
3. 再读冻结 artifact
4. 若 child 没 final envelope，由你根据 host status + artifact 标记 partial/cancelled

不要伪造 child envelope。

## 5. Evidence

任何进入 evidence registry 的值必须可追溯。

Worker 的 `source_task_id` 指 lead 分配的 `ZEOS_TASK_ID`。

Lead ingest 时绑定实际 WorkBuddy host task_id 和 transcript/tool/artifact locator。

优先级：

`raw tool result / artifact > transcript record > machine-derived transform + provenance > human/model transcription`

禁止把自己手打/猜测的“观测值”写进命令或文件，再把搜索命中当旁证。

## 6. Artifact Discipline

每个 worker 只知道自己的 namespace。

不要把 sibling namespace 放进另一个 worker prompt。

Worker 只返回相对路径 + sha256。

相关 workers terminal 后，lead 独立重算 hash 再综合。

这是工程纪律，不是安全 sandbox。

## 7. Recruitment

若确认是 Expert gap：
1. 定义岗位；
2. 调 Recruiter / `zh-expert-os recruit-pipeline`；
3. Candidate 只能进入 Shadow/probation；
4. 需要 WorkBuddy native 化时：
   `zh-expert-os workbuddy-export-expert --expert <id>`
5. 热注册成功后继续 real-task trial / Arena；
6. Auditor；
7. Human approval；
8. 才能 Active。

## 8. Synthesis

不做多数投票。

按 claim + provenance 合并：
- 同源不重复计权；
- 关键冲突交 Red Team / Auditor；
- 非关键冲突显式未收敛；
- failed/cancelled 节点单独报告；
- 不用别人的输出填补失败节点。

最终回答回到用户真实任务，优先交付已完成成果，而不是内部会议纪要。
