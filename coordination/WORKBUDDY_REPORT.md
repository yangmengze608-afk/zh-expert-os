# WORKBUDDY REPORT — EXP-001

> 状态：PENDING

## A. 环境

- WorkBuddy 版本：
- 宿主/模型：
- OS：
- 实验时间：
- 工作目录：
- 已安装相关 expert/plugin：

## B. 原生插件 agent 基线

- agent 文件：
- agent id：
- subagent_type：
- 是否真实 invocation：
- invocation 证据：
- 上下文是否独立：
- 证据等级：UNKNOWN

## C. 用户级 agent 注册

- 测试文件路径：
- 文件名：
- frontmatter：
- 创建后当前会话能否发现：
- reload 后能否发现：
- 新会话能否发现：
- 实际调用结果：
- 原始错误（若有）：
- 证据等级：UNKNOWN

## D. Context Isolation Canary

合成测试值，不得使用真实秘密。

- Parent canary：
- Agent A canary：
- Agent B canary：

Agent A：
- 看见 parent canary？ YES / NO / UNKNOWN
- 看见 B canary？ YES / NO / UNKNOWN

Agent B：
- 看见 parent canary？ YES / NO / UNKNOWN
- 看见 A canary？ YES / NO / UNKNOWN

是否存在共享文件系统但独立聊天上下文：
- 结果：
- 证据：

## E. maxTurns / partial / failure

- maxTurns 测试：
- 是否强终止：
- 是否能主动 partial：
- failed 是否可区分：
- timeout 是否可区分：
- 编排者收到的状态：
- 证据等级：UNKNOWN

## F. Team / Orchestration

- TeamCreate 调用者：
- 成员可否直接互联：
- lead 是否能并发派发：
- lead 是否能只读结构化 envelope 而不载入完整输出：
- 证据：

## G. 环境变更

- 新建：
- 修改：
- 删除：
- 是否已清理测试 agent：
- 是否需要人工恢复：

## H. 原始日志 / 产物

请贴关键日志，或给出可访问的文件路径/仓库路径。不要只写总结。

## I. WorkBuddy 自己的结论

按四档填写：VERIFIED / OBSERVED / INFERRED / UNKNOWN。

1. plugin-pack native agent：
2. user-level agent：
3. hot registration：
4. context isolation：
5. maxTurns：
6. structured partial/failure：
