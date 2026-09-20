# WORKBUDDY REQUEST — EXP-001

请在真实 WorkBuddy 宿主中执行 `experiments/EXP-001-workbuddy-native-expert.md`。

## 强制要求

- 先记录 WorkBuddy/宿主版本和当前可用 agent 能力。
- 只使用**合成 canary 字符串**测试上下文隔离，不读取或记录私人信息。
- 改动 `~/.workbuddy/agents/` 前先列目录；若创建测试 agent，使用唯一前缀 `zeos-exp001-`，实验后明确报告是否清理。
- 不要把“agent 文件存在”当作“可调用”；必须实际 invocation。
- 不要把“两个角色回答了”当作“独立上下文”；必须执行隔离测试。
- 无法验证的字段写 `UNKNOWN`，不要补猜。
- timeout / failed / partial 必须原样报告。

## 需要回填

完成后覆盖填写 `coordination/WORKBUDDY_REPORT.md`，并尽可能附上宿主日志或可复现命令/截图路径。

特别关注：

- 实际可用的 agent 定义 frontmatter；
- `name`、文件名、`subagent_type` 的映射；
- `maxTurns` 是否表现为硬上限；
- TeamCreate 是否只能由 lead/orchestrator 发起；
- 成员是否能直接互联；
- 当前会话新增 agent 的发现时机；
- parent context 是否自动泄漏到 child；
- 两个 child 是否互相看到对方专属 canary。