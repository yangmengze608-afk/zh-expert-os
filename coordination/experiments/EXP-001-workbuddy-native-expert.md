# EXP-001 — WorkBuddy Native Expert Reality Check

## Purpose

验证 WorkBuddy 中“Expert”是否真的对应可独立调用的 agent，以及动态注册的可靠边界。

## Hypotheses

- H1：已安装 expert/plugin 包内 `agents/*.md` 可被宿主作为独立 `subagent_type` 调用。
- H2：`~/.workbuddy/agents/*.md` 可以注册用户级 native agent。
- H3：用户级 agent 创建后无需重启即可热发现。
- H4：child agent 不自动继承 parent 对话中的未传递 canary。
- H5：两个 child agent 互相看不到对方未传递的专属 canary。
- H6：`maxTurns` 能形成可靠执行预算；partial / failed / timeout 可区分。

## Phase 0 — Baseline

找到一个当前已安装、已知能被调度的 expert team。记录 lead/member agent 文件、frontmatter 与一次真实 subagent invocation。不要依赖文档宣称。

## Phase 1 — Minimal User Agent

若宿主允许，在 `~/.workbuddy/agents/` 新建：

`zeos-exp001-probe.md`

建议最小定义：

```yaml
---
name: zeos-exp001-probe
description: Zh Expert OS EXP-001 disposable probe agent
displayName:
  en: ZEoS Probe
  zh: 实验探针
profession:
  en: Runtime Probe
  zh: 运行时探针
maxTurns: 6
---
```

正文只要求返回：
1. 自己的 agent id；
2. 收到的任务文本；
3. 是否看到指定 canary；
4. 一个固定字符串 `ZEOS_EXP001_OK`。

依次测试：当前会话发现 → reload 后发现 → 新会话发现。任何一步成功，都要真实调用一次。

## Phase 2 — Context Isolation

只使用合成字符串。

Parent context 中放：
`PARENT_CANARY_EXP001_7F3A`

Agent A 的自包含 prompt 只放：
`A_CANARY_EXP001_19C2`

Agent B 的自包含 prompt 只放：
`B_CANARY_EXP001_84D1`

分别询问 A/B：
- 是否看到了 parent canary；
- 是否看到了另一个 child canary。

不要在 A 的 prompt 中写 B canary；不要在 B 的 prompt 中写 A canary。若编排器为了问问题不得不泄漏 token，则该测试无效，重新设计。

## Phase 3 — Independence vs Shared Resources

记录：
- 是否独立 invocation；
- 是否独立 chat/context；
- 是否共享工作目录/文件系统；
- 是否共享工具权限；
- 是否共享模型/provider。

这些是不同维度，不要合并成“独立/不独立”一个词。

## Phase 4 — Budget and Failure

设计一个会自然超过 6 turns 的无害任务，观察 `maxTurns: 6`。

再做两个受控任务：
- 一个要求 agent 在预算不足时主动返回 `status=partial`；
- 一个触发可控失败，确认 lead 能否区分 failed 与 timeout。

不得为了测试故意破坏真实项目文件。

## Phase 5 — Team Semantics

验证并记录：
- TeamCreate 是否只能由 orchestrator/lead 发起；
- lead 是否可以并发派发两个 member；
- member 是否能直接调用 member；
- lead 收到的是完整 child transcript 还是最终 output/摘要；
- 是否能要求 child 返回结构化 envelope。

## Pass Criteria

“WorkBuddy Native Expert 可用于 v0.5”至少需要：

- H1 VERIFIED；
- H4/H5 至少 OBSERVED 且无反例；
- 能可靠识别 child 的 success/partial/failure；
- 动态招聘即便 H2/H3 失败，也存在 general-purpose independent subagent 兜底。

H2/H3 是增强项，不是核心闭环的阻断项。

## Cleanup

实验结束后删除 `zeos-exp001-*` 测试 agent，除非用户明确要求保留。记录清理结果。