# WORKBUDDY REQUEST — EXP-002

请执行：

`coordination/experiments/EXP-002-workbuddy-control-plane.md`

本轮目标不是“证明多 agent 很强”，而是把 **spawn / message delivery / stop / timeout** 四个控制面语义测清楚。

## 先决条件

1. 先同步本分支最新状态：`exp002/workbuddy-control-plane`。
2. 记录 WorkBuddy 版本、主模型、实际 subagent 模型与宿主版本。
3. 所有测试资源使用前缀 `zeos-exp002-`。
4. 只使用合成 canary；不要使用私人数据或真实秘密。
5. 不修改 `src/`、Registry、正式 Expert 名册或既有 Runtime。
6. 不把工具“自述存在”当作成功；关键能力必须出现**真实 invocation / task_id / transcript / artifact**。
7. 任何运行中的 snapshot 都不得当终态。必须等完成通知或明确 stop/terminal 状态后再下结论。
8. 若新证据与已写结论冲突，先撤回结论并留下更正记录，再继续。
9. 不确定即 `UNKNOWN`。

## 本轮特别禁止

- 不得再用 “tool list 里有 Agent” 推出“member spawning 成功”。
- 不得用 `SendMessage success:true` 推出“对方已收到”。
- 不得把 `TaskStop` 当 timeout。
- 不得把独立 artifact 目录称为安全沙箱；它只是工程纪律，不是宿主级访问控制。
- 不得把 `in-process` 等同于“不是独立 Expert”。

## 交付

完成后填写：

`coordination/experiments/EXP-002-WORKBUDDY_REPORT.md`

并将可公开的 A 层证据放到：

`coordination/experiments/EXP-002-artifacts/`

完整 transcript / runtime snapshot 继续按 EXP-001 的 A/B 分层处理，不要未经 Human Owner 批准放进 public repo。

不要填写：

`coordination/experiments/EXP-002-CHATGPT_REVIEW.md`

那部分由 ChatGPT 独立审计。
