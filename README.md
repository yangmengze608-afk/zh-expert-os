# 中文 AI 专家团操作系统（Zh Expert OS）

> 面向中文用户、能够按真实任务发现能力缺口、招聘候选、匿名评测、晋升、降级与淘汰 AI 专家的开源专家组织框架。

**当前版本：v0.3.2 — End-to-end Recruitment Pipeline**

本项目不是“几百个 Prompt 的合集”。核心问题是：**一个 AI 专家组织怎样因为真实任务而进化，并用可复现证据长期保持最强，而不是越堆越大？**

## 核心原则

1. **先有任务，再补能力。** Recruitment is task-driven, not collection-driven.
2. **缺能力不等于缺专家。** 先区分 `Expert / Skill / Tool / Knowledge / Workflow`。
3. **一次性需求不默认永久招人。** 小众能力先用临时顾问，重复或战略能力才建立正式岗位。
4. **搜索的是能力资产，不是只搜 expert。** GitHub 候选可以来自 agent、expert、persona、role、skill、playbook、workflow、team 或高质量领域 repo。
5. **候选不是员工。** 外部资产必须经过来源与 License 检查、中文标准化、Shadow、Eval Arena，赢了才可能入职。
6. **招聘是手段，完成原始任务才是目的。**

## 1. 已打通的自我进化闭环

```text
用户任务
  ↓
现役能力覆盖检查
  ↓
能力缺口诊断
  ↓
┌────────┬───────┬──────┬───────────┬──────────┐
│ Expert │ Skill │ Tool │ Knowledge │ Workflow │
└────────┴───────┴──────┴───────────┴──────────┘
  ↓
如果不是 Expert → 补 Skill / Tool / Knowledge / Workflow，不扩编
  ↓
如果是 Expert → 临时顾问 or 正式岗位
  ↓
GitHub 仓库搜索 + 代码资产搜索
  ↓
读取 README / SKILL.md / Agent / Role / Playbook
  ↓
背景调查 + CandidateAsset 标准化
  ↓
License + 岗位匹配 + 中文原生度 + 可迁移性 + 可维护性 + 重复度
  ↓
Shortlist
  ↓
Shadow / probation
  ↓
Eval Arena：同题匿名 A/B + 多 Judge
  ↓
长期 Beta-Binomial 战绩
  ↓
CAO 人事建议 → Auditor → 人类批准
  ↓
继续完成最初用户任务
```

招聘协议见 [`docs/RECRUITER.md`](docs/RECRUITER.md)，端到端流水线见 [`docs/RECRUITMENT_PIPELINE.md`](docs/RECRUITMENT_PIPELINE.md)，竞技场协议见 [`docs/ARENA.md`](docs/ARENA.md)。

## 2. v0.3.2 新增：真正的招聘流水线

现在系统不只会“生成 GitHub 搜索词”，而是已经可以：

- 用真实 `CapabilityGap` 决定是否应该招聘 Expert；
- 搜 GitHub 仓库级候选；
- 有 `GITHUB_TOKEN` 时进一步搜 `SKILL.md`、`agents/*.md`、`experts/*.md`、`roles/*.md`、playbook；
- 读取候选 README 或具体能力文件；
- 补齐仓库元数据、活跃度、Stars、Archived 状态和 License；
- 从候选文本中提取与岗位相关的证据行；
- 自动标准化成 `CandidateAsset`；
- 评分岗位匹配、中文原生度、可迁移性、可维护性和职责重复度；
- 执行 License Gate；
- 生成可审计的 shortlist；
- 只为合格、许可证允许的候选生成 `probation` Shadow Expert 规格；
- 可选择把前 N 个 Shadow 候选登记进专家 Registry，但**绝不直接晋升为 active**。

核心实现：

- `src/zh_expert_os/recruiter.py`
- `src/zh_expert_os/github_source.py`
- `src/zh_expert_os/recruitment_pipeline.py`

## 3. 一条命令跑招聘

先使用示例缺口：

[`examples/recruiter/gap-china-edu-gamification.json`](examples/recruiter/gap-china-edu-gamification.json)

只调查和生成候选档案，不修改专家注册表：

```bash
zh-expert-os recruit-pipeline \
  --gap-file examples/recruiter/gap-china-edu-gamification.json \
  --output registry/recruitment/study-pet-001.json
```

如果确认要让排名第一的合格候选进入 Shadow：

```bash
zh-expert-os recruit-pipeline \
  --gap-file examples/recruiter/gap-china-edu-gamification.json \
  --register-shadow 1 \
  --output registry/recruitment/study-pet-001.json
```

`--register-shadow` 默认是 `0`，所以默认行为是**先调查，不扩编**。

代码级 GitHub 搜索通常需要：

```bash
export GITHUB_TOKEN=...
```

Token 只从环境变量读取，不写入仓库或招聘档案。没有 Token 时仍可做仓库级发现。

## 4. 候选评分不是最终判决

当前默认分析器刻意保持透明和可测试，不绑定某家模型 API。它负责做第一轮猎头筛选，而不是替代真实能力验证。

一个候选分数再高，也只能获得：

```text
SEND_TO_SHADOW
```

不能直接获得：

```text
ACTIVE
```

真正的人事证据仍来自：

- 真实任务 Shadow；
- 同题匿名 A/B；
- 多 Judge；
- 事实错误硬门槛；
- 长期 Beta-Binomial 后验；
- Auditor 审核。

## 5. Eval Arena

v0.2 已实现：

- 同题匿名 A/B；
- A/B 身份随机映射；
- Judge 展示顺序 AB / BA 对冲；
- 多 Judge 独立评分；
- 任务完成度、事实性、证据质量、中文原生度、清晰度评分；
- 严重事实错误硬门槛；
- 分歧率与位置偏差监控；
- 单题结果幂等写入长期战绩；
- 长期 Beta-Binomial 后验决定是否值得晋升。

## 6. 快速开始

要求 Python 3.11+，核心包零第三方依赖。

```bash
git clone https://github.com/yangmengze608-afk/zh-expert-os.git
cd zh-expert-os
python -m pip install -e .
python -m unittest discover -s tests -v
```

## 7. 当前治理角色

- `cao` — 首席专家官：发现缺口、提出招聘与人事建议；
- `auditor` — 独立审计官：监督 CAO 和规则漂移；
- `router` — 中文任务路由官；
- `red-team` — 红队反证专家；
- `arena-director` — 竞技场主持官；
- `arena-judge` — 匿名评测裁判。

领域专家不应被一次性手写堆进仓库，而应通过任务驱动招聘与竞技场逐步进入。

## 8. 开源与许可证原则

核心代码使用 MIT License。外部专家资产必须逐项记录来源与许可证：

- MIT / Apache-2.0 / BSD / ISC：可进入标准化与 Shadow 流程，但仍保留来源；
- MPL / GPL / LGPL / AGPL：默认 `review`，不自动复制进核心仓库；
- 未知或缺失许可证：`RESEARCH_ONLY`。

> **借鉴架构，不做许可证洗白。**

## 9. 路线图

- **v0.1 ✅**：治理内核、专家生命周期、贝叶斯晋升、宪法、审计。
- **v0.2 ✅**：匿名 Eval Arena、多 Judge、偏差监控、长期战绩。
- **v0.3 ✅**：任务驱动 Recruiter、能力缺口分类、License 门禁、Shadow 准入。
- **v0.3.1 ✅**：GitHub 仓库 / 代码候选实时发现。
- **v0.3.2 ✅**：读取候选资产、背景调查、标准化评分、Shortlist、Shadow 规格与 CLI 流水线。
- **v0.4**：Team Runtime：中文 Router 自动组队、并行/串行 Workflow、Red Team、Evidence Synthesis。
- **v0.5**：Claude / Codex / ChatGPT / Cursor 等跨平台 Adapter。
- **v1.0**：中文原生、自我进化的 AI Expert OS。

详情见 [`docs/ROADMAP.md`](docs/ROADMAP.md)。

## 10. 项目定位

> **用一句中文描述任务，系统先判断现有组织缺什么；只有确实缺 Expert 时才去 GitHub 招聘，读取候选真实能力资产、做背景调查，把最强候选送进 Shadow 与匿名竞技场证明自己。**
