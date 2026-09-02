# Recruitment Pipeline｜任务驱动招聘流水线

v0.3.2 把此前分离的“能力缺口诊断、GitHub 搜索、候选筛选、Shadow”串成一条可执行流水线。

## 核心原则

> 招聘由真实任务驱动，不由“收集更多 Agent”驱动。

一次招聘必须从 `CapabilityGap` 开始。系统先判断缺的是 `Expert / Skill / Tool / Knowledge / Workflow`。只有 `Expert` 缺口会进入人才搜索。

## 流水线

```text
原始任务
  ↓
CapabilityGap
  ↓
是否真的缺 Expert？
  ├─ 否 → 补 Skill / Tool / Knowledge / Workflow
  └─ 是
       ↓
GitHub 仓库 + 代码资产发现
       ↓
读取 README / SKILL.md / agents/*.md / roles/*.md / playbook
       ↓
候选背景调查
       ├─ 来源与 URL
       ├─ License
       ├─ stars / 活跃度 / archived
       └─ 与能力缺口相关的证据行
       ↓
CandidateAsset 标准化
       ├─ source_type
       ├─ fit_score
       ├─ chinese_native_score
       ├─ portability_score
       ├─ maintainability_score
       └─ overlap_score
       ↓
License Gate + 综合评分
       ↓
Shortlist
       ↓
Shadow Expert Spec (probation)
       ↓
Eval Arena
       ↓
CAO → Auditor → 人类批准
```

## 为什么“读取资产”很重要

仅凭仓库名、Star 数或 `expert` 关键词不能判断一个候选是否值得招聘。v0.3.2 会读取候选最能代表能力的文本：

- 代码搜索命中时：读取该 `SKILL.md` / Agent Markdown / Role / Playbook 文件；
- 仓库级命中时：优先读取 README；
- 同时读取仓库元数据和许可证。

读取内容只用于背景调查与候选分析。系统不会因为发现了一个开源 Prompt 就自动复制进核心仓库。

## 当前分析器

v0.3.2 默认使用透明、可测试的启发式分析器，避免 CI 或基础功能强绑定某家模型 API。

它会评估：

1. **岗位匹配度**：候选文本与目标能力的覆盖；
2. **中文原生度**：中文内容比例与中国场景信号；
3. **可迁移性**：是否为 Markdown / Skill / Agent 等易迁移资产，以及是否提到多个 Agent Harness；
4. **可维护性**：仓库是否 archived、近期是否活跃、社区信号；
5. **重复度**：目标能力与现役专家职责的重叠。

这些分数是筛选信号，不是最终能力证明。真正的人事判断仍然由 Shadow + Eval Arena 的真实任务结果完成。

后续可以新增 LLM Analyzer 作为可插拔分析器，但其输出必须保留证据并接受同样的 License 与 Arena 规则。

## CLI

先准备能力缺口文件，例如：

```json
{
  "task_id": "study-pet-001",
  "task_goal": "设计面向中国大学生的学习抽卡宠物 MVP",
  "capability": "中国教育游戏化产品",
  "gap_type": "expert",
  "reason": "现役缺少教育心理 + 游戏化 + 中国学生市场联合能力",
  "recurrence_count": 4,
  "strategic": true,
  "criticality": 0.8
}
```

只生成招聘档案，不修改专家注册表：

```bash
zh-expert-os recruit-pipeline \
  --gap-file examples/recruiter/gap-china-edu-gamification.json \
  --output registry/recruitment/study-pet-001.json
```

把排名最高的 1 名合格候选登记为 Shadow / probation：

```bash
zh-expert-os recruit-pipeline \
  --gap-file examples/recruiter/gap-china-edu-gamification.json \
  --register-shadow 1 \
  --output registry/recruitment/study-pet-001.json
```

`--register-shadow` 默认为 `0`。也就是说，系统默认先调查、再决定是否入试用，不会自动扩编。

## GitHub Token

仓库搜索可以匿名运行，但 GitHub 限流更严格。代码级搜索通常需要：

```bash
export GITHUB_TOKEN=...
```

Token 只从环境变量读取，不应写入仓库、招聘档案或任何 Expert 文件。

没有 Token 时，流水线仍可进行仓库级发现，并会在结果中明确记录 code search 未执行的原因。

## License Gate

- MIT / Apache-2.0 / BSD / ISC：可以进入标准化与 Shadow 流程，但仍保留来源记录；
- GPL / LGPL / AGPL / MPL：进入人工许可证审查，不默认复制；
- 未知 / 无许可证：只允许研究能力结构，不直接复制资产。

Shadow 规格只能从满足自动门禁的候选生成。进入 Shadow 不代表转正。

## 当前边界

v0.3.2 已经打通“发现 → 读取 → 背调 → 标准化 → 排名 → Shadow 规格”。

仍未自动完成两件事：

1. 自动调用外部模型让 Shadow 专家执行任务；
2. 自动选择最公平的现任 / baseline 与 Shadow 进入 Arena。

这两项属于 Team Runtime / Adapter 层。当前版本刻意保持一个治理原则：**招聘系统可以自动推荐和试用，但不能绕过真实任务竞技场直接把候选变成正式专家。**
