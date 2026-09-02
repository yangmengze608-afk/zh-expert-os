# Roadmap

## v0.1 — Governance Kernel ✅
- Constitution
- CAO / Auditor / Router / Red Team 种子专家
- Registry
- 专家生命周期
- Beta-Binomial 挑战后验
- 晋升建议器
- CLI + 单元测试

## v0.2 — Eval Arena ✅
- JSONL benchmark 校验与批量建场
- 同题匿名 A/B battle
- A/B 身份随机映射
- Judge 展示顺序 AB / BA 自动对冲
- 多 Judge 评分聚合
- 严重错误硬门槛
- Judge 分歧率与位置偏差监控
- battle → MatchRecord 幂等写回
- Arena Director / Arena Judge 治理角色
- CLI + CI + 单元测试

## v0.3 — Task-driven Recruiter ✅
- 先由真实任务触发能力覆盖检查
- Expert / Skill / Tool / Knowledge / Workflow 缺口分类
- 非 Expert 缺口禁止通过“招人”掩盖
- Expert 缺口区分临时顾问与正式岗位
- CandidateAsset 标准化
- License 门禁
- 中文原生度、可迁移性、可维护性、重复度纳入候选评分

### v0.3.1 — GitHub Discovery ✅
- GitHub 仓库级候选搜索
- GitHub 代码级候选搜索
- 覆盖 agent / expert / role / skill / playbook / workflow / team
- 无 Token 时安全降级到仓库级搜索

### v0.3.2 — Recruitment Pipeline ✅
- 读取候选 README / SKILL.md / Agent / Role / Playbook
- 补齐仓库活跃度、Stars、Archived、License 等背景信息
- 从候选文本提取岗位相关证据
- 自动推断 source type
- 生成可审计 CandidateAsset 档案
- 岗位匹配 / 中文原生 / 可迁移 / 可维护 / 重复度评分
- Shortlist 排名
- 仅为合格且许可证允许的候选生成 Shadow / probation Expert 规格
- `recruit-pipeline` CLI
- 可选登记前 N 个 Shadow 候选；绝不直接转 active

## v0.4 — Team Runtime

### v0.4-alpha1 — Expert Runtime Bridge ✅
- `AgentRuntime` 抽象
- `CommandRuntime`：外部 CLI / adapter 通过 stdin/stdout 接入
- `CallableRuntime`：宿主和测试接入
- Expert 配置转独立 invocation
- Shadow / incumbent 同任务默认并行执行
- CommandRuntime 下两个 Expert 为两个独立进程
- 输出自动提交 Arena 并匿名 A/B
- `runtime-trial` CLI
- 超时、非零退出码、空输出 fail loud
- Runtime 不拥有晋升权限

### v0.4 正式版待完成
- 中文意图理解
- Router 自动组队
- 并行 / 串行 workflow
- Red Team
- Evidence synthesis
- 任务结束后自动写回专家表现
- 任务执行中按需触发临时顾问与能力补全
- 为 Shadow 自动选择公平 baseline 并生成 Arena 任务包
- 可选自动 Judge Runtime，但同模型 Judge 不冒充独立证据

## v0.5 — Adapters
- Claude Code
- Codex
- ChatGPT
- Cursor
- OpenCode / Gemini CLI（按社区需求）

## v1.0 — Self-Evolving Chinese Expert OS
- 自动发现能力缺口
- 招聘 / 试用 / 晋升 / 替补 / 退休闭环
- 人类治理面板
- Git 历史 + 可回滚专家组织
