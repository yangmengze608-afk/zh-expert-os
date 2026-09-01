# 中文 AI 专家团操作系统（Zh Expert OS）

> 面向中文用户、能够按真实任务发现能力缺口、招聘候选、匿名评测、晋升、降级与淘汰 AI 专家的开源专家组织框架。

**当前版本：v0.3.0 — Task-driven Recruiter**

本项目不是“几百个 Prompt 的合集”。核心问题是：**一个 AI 专家组织怎样因为真实任务而进化，并用可复现证据长期保持最强，而不是越堆越大？**

## 核心原则

1. **先有任务，再补能力。** Recruitment is task-driven, not collection-driven.
2. **缺能力不等于缺专家。** 先区分 `Expert / Skill / Tool / Knowledge / Workflow`。
3. **一次性需求不默认永久招人。** 小众能力先用临时顾问，重复或战略能力才建立正式岗位。
4. **搜索的是能力资产，不是只搜 expert。** GitHub 候选来源可以是 agent、expert、persona、role、skill、playbook、workflow、team 或高质量领域 repo。
5. **候选不是员工。** 外部资产先经过来源与 License 检查、中文标准化、Shadow、Eval Arena，赢了才可能入职。
6. **招聘是手段，完成原始任务才是目的。**

## 1. 自我进化闭环

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
GitHub / 社区 / 原创候选
  ↓
License + 能力 + 中文原生度 + 重复度筛选
  ↓
Shadow
  ↓
Eval Arena：同题匿名 A/B + 多 Judge
  ↓
长期 Beta-Binomial 战绩
  ↓
CAO 人事建议 → Auditor → 人类批准
  ↓
继续完成最初用户任务
```

详细招聘协议见 [`docs/RECRUITER.md`](docs/RECRUITER.md)，竞技场协议见 [`docs/ARENA.md`](docs/ARENA.md)。

## 2. v0.3 新增：任务驱动 Recruiter

`src/zh_expert_os/recruiter.py` 现在提供：

- `CapabilityGap`：记录这次真实任务为什么缺能力；
- `decide_engagement()`：决定该补 Skill / Tool / Knowledge / Workflow，还是临时/正式 Expert；
- `build_search_queries()`：围绕能力生成 GitHub 搜索词，不局限于 `expert`；
- `CandidateAsset`：统一描述来自 Agent / Skill / Playbook / Team 等不同来源的候选；
- `license_gate()`：宽松许可证允许进入改造流程，copyleft 进入人工审查，未知许可证只允许研究；
- `candidate_score()`：把岗位匹配、中文原生度、可迁移性、可维护性和非重复价值纳入评分；
- `screen_candidate()`：只有合格候选才进入 Shadow；
- `build_recruitment_plan()`：把“任务 → 缺口 → 搜索 → 下一步”组织成招聘计划。

示例任务：[`examples/recruiter/gap-china-edu-gamification.json`](examples/recruiter/gap-china-edu-gamification.json)。

## 3. Python API 示例

```python
from zh_expert_os.recruiter import CapabilityGap, build_recruitment_plan

gap = CapabilityGap(
    task_id="product-001",
    task_goal="设计面向中国大学生的学习抽卡宠物 MVP",
    capability="中国教育游戏化产品",
    gap_type="expert",
    reason="现役团队缺少教育心理 + 游戏化 + 中国学生市场的联合判断",
    recurrence_count=4,
    strategic=True,
)

plan = build_recruitment_plan(gap)
print(plan["diagnosis"])
print(plan["search_queries"])
```

系统会先判断是否真的需要正式专家，再生成候选搜索计划。

## 4. Eval Arena

v0.2 已经实现：

- 同题匿名 A/B；
- A/B 身份随机映射；
- Judge 展示顺序 AB / BA 对冲；
- 多 Judge 独立评分；
- 任务完成度、事实性、证据质量、中文原生度、清晰度评分；
- 严重事实错误硬门槛；
- 分歧率与位置偏差监控；
- 单题结果幂等写入长期战绩；
- 长期 Beta-Binomial 后验决定是否值得晋升。

## 5. 快速开始

要求 Python 3.11+，核心包零第三方依赖。

```bash
git clone https://github.com/yangmengze608-afk/zh-expert-os.git
cd zh-expert-os
python -m pip install -e .
python -m unittest discover -s tests -v
```

现有 CLI 继续支持专家 Registry、Benchmark 和 Arena 操作。

## 6. 当前治理角色

- `cao` — 首席专家官：发现缺口、提出招聘与人事建议；
- `auditor` — 独立审计官：监督 CAO 和规则漂移；
- `router` — 中文任务路由官；
- `red-team` — 红队反证专家；
- `arena-director` — 竞技场主持官；
- `arena-judge` — 匿名评测裁判。

领域专家不应被一次性手写堆进仓库，而应通过任务驱动招聘与竞技场逐步进入。

## 7. 开源与许可证原则

核心代码使用 MIT License。外部专家资产必须逐项记录来源与许可证：

- MIT / Apache-2.0 / BSD / ISC：可进入改造候选流程，但仍保留来源；
- MPL / GPL / LGPL / AGPL：默认 `review`，不自动复制进核心仓库；
- 未知或缺失许可证：`RESEARCH_ONLY`。

> **借鉴架构，不做许可证洗白。**

## 8. 路线图

- **v0.1 ✅**：治理内核、专家生命周期、贝叶斯晋升、宪法、审计。
- **v0.2 ✅**：匿名 Eval Arena、多 Judge、偏差监控、长期战绩。
- **v0.3 ✅**：任务驱动 Recruiter、能力缺口分类、GitHub 候选搜索策略、License 门禁、Shadow 准入。
- **v0.4**：Team Runtime：中文 Router 自动组队、并行/串行 Workflow、Red Team、Evidence Synthesis。
- **v0.5**：Claude / Codex / ChatGPT / Cursor 等跨平台 Adapter。
- **v1.0**：中文原生、自我进化的 AI Expert OS。

详情见 [`docs/ROADMAP.md`](docs/ROADMAP.md)。

## 9. 项目定位

> **用一句中文描述任务，系统先判断现有组织缺什么能力；只有确实缺 Expert 时才去招聘候选，并让候选通过 Shadow 与匿名竞技场证明自己。**
