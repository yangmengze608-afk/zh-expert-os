# ChatGPT × WorkBuddy Collaboration Protocol

本目录是 Zh Expert OS 的跨宿主协作面。目标不是让两个模型互相“聊天”，而是让它们围绕同一个可审计任务，通过仓库文件交换实验计划、原始观测、审计结论和架构决策。

## 角色分工

- **ChatGPT / 架构审计侧**：定义实验、验收标准、证据等级；审查 WorkBuddy 报告；把宿主行为转化为可迁移架构结论。
- **WorkBuddy / 宿主执行侧**：在真实宿主中调用 TeamCreate / subagent / agent 文件；记录原始日志、失败、超时、上下文可见性与环境变化。
- **Human Owner**：批准会改变用户环境、治理规则、正式 Expert 名册的操作。

## 单一事实源

1. 当前任务：`CURRENT_TASK.md`
2. 给 WorkBuddy 的动作单：`WORKBUDDY_REQUEST.md`
3. WorkBuddy 实测回报：`WORKBUDDY_REPORT.md`
4. ChatGPT 审计：`CHATGPT_REVIEW.md`
5. 已采纳决策：`DECISIONS.md`
6. 单次实验：`experiments/EXP-*.md`

## 证据等级

- **VERIFIED**：有可复现步骤 + 原始日志/产物，重复至少一次且结果一致。
- **OBSERVED**：真实宿主中观察到一次，但尚未重复。
- **INFERRED**：由现象推断，尚无直接宿主证据。
- **UNKNOWN**：未测试或证据冲突。

任何“宿主支持 X”的架构声明，至少需要 VERIFIED；仅有 OBSERVED 时必须保留限定语。

## 交接规则

WorkBuddy 不要只写“成功/失败”，必须留下：宿主版本、任务 ID、agent id、subagent_type、调用顺序、输入摘要、状态、耗时、原始错误、输出摘要、生成文件、环境变化、是否可复现。

ChatGPT 不把“多个角色输出”自动当作“独立证据”。独立性至少要区分：独立 invocation、独立上下文、独立证据来源、独立模型/供应商。