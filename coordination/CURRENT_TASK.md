# CURRENT TASK

## 目标

实现 **v0.5-alpha1 — WorkBuddy Native Expert Runtime**。

EXP-001 / EXP-002 已结束并通过独立审计。现在停止继续扩展 Reality Check，把已经验证的宿主事实编码进正式 Adapter。

## 已确认的 WorkBuddy 边界

- user-level `~/.workbuddy/agents/*.md` 可热注册并真实 invocation；
- child 对话上下文表现隔离，但文件系统共享；
- frontmatter `maxTurns` 不能作为硬预算；
- `TaskStop` 已 2/2 验证能真正停止 worker；
- stop 不是瞬时，且被 stop 的 child 不保证留下 final envelope；
- `SendMessage success:true` 只表示 route accepted，不等于 consumed；
- tested `general-purpose` member 未观测到 nested spawn；
- tested interface 未暴露可验证的 agent timeout/deadline；
- user-level agent 定义正文的行为级热加载可重复；
- artifact namespace 是工程纪律，不是安全沙箱。

## 当前里程碑

**v0.5-alpha1：Flat Native Runtime**

本轮实现：

1. WorkBuddy native Expert 定义与安装器；
2. `lead → workers` 一层 fan-out 契约；
3. host status + expert envelope 双状态；
4. `ROUTE_ACCEPTED / CONSUMED / ACKED` 消息状态；
5. evidence provenance pointer；
6. artifact 相对路径 + sha256；
7. Registry Expert → WorkBuddy native agent 导出 CLI；
8. 真实项目调用示例（现保留知流样例作为历史/参考模板）；
9. 单元测试与文档。

## 明确不做

本轮不宣称：
- nested spawn 已可依赖；
- agent timeout 已打通；
- namespace 是安全隔离；
- `maxTurns` 是预算硬闸门；
- 热注册 = 晋升；
- 多个同模型 Expert = 多份独立证据。

## 当前发布门

ChatGPT 已完成 PR #9 代码审计并修复 node schema、agent identity、symlink 安装预检与 envelope 严格校验问题。代码审计记录见 `coordination/releases/V0.5A1_CHATGPT_CODE_REVIEW.md`。

**release smoke 已完成并通过 ChatGPT 终审；当前下一步是合并 PR #9。**

已完成的真实 WorkBuddy release smoke：

- `coordination/releases/V0.5A1_WORKBUDDY_SMOKE.md`
- `coordination/releases/V0.5A1_WORKBUDDY_SMOKE_REPORT.md`

只验证安装、native worker invocation、assignment/host task identity、envelope 校验、artifact provenance、动态 export 和 Skill discovery。

这不是新的 Reality Check，不重新测试 EXP-001/002 已解决的问题。

## 完成条件

- 新增 WorkBuddy runtime contract 测试全部通过；
- 现有测试无回归；
- PR CI green；
- Adapter 文档与 EXP-001 / EXP-002 证据边界一致；
- WorkBuddy release smoke 通过 ChatGPT 复核；
- 合并后选择**当前仍在真实推进的项目**做第一轮 end-to-end 业务 trial，不再把“知流”作为下一阶段默认目标。
