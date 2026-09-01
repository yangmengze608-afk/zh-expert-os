# v0.3 Recruiter：任务驱动的能力补全

> 核心原则：**Recruitment is task-driven, not collection-driven.**
>
> 招聘由真实任务驱动，而不是为了扩大专家数量。

## 1. 先诊断，再招人

一个任务失败或覆盖不足时，CAO 必须先判断缺口属于哪一类：

- `expert`：需要长期独立判断与责任边界的人；
- `skill`：现有专家缺少一个可复用技能；
- `tool`：缺 API / MCP / Connector / 数据源；
- `knowledge`：缺可信、版本明确的知识资产；
- `workflow`：Router、编排或输入输出契约有问题；
- `unknown`：证据不足，先调查。

只有 `expert` 缺口才进入“是否招人”的判断。其他缺口优先补 Skill、Tool、Knowledge 或 Workflow。

## 2. Expert 缺口也不默认永久扩编

第一次遇到一个小众问题，默认使用 `temporary_consultant`。

满足以下任一条件，才建议建立正式岗位：

- 同类能力缺口重复出现至少 3 次；
- 属于组织长期战略能力；
- 关键性非常高（默认 `criticality >= 0.85`）。

这样可以避免为了一个任务永久增加一个专家，导致组织无限膨胀。

## 3. 搜索的是“能力资产”，不是只搜索 expert

当确实需要专家时，Recruiter 不只搜索：

```text
<capability> expert
```

还会同时寻找：

```text
agent
expert
persona
role
skill
playbook
workflow
multi-agent team
```

因为 GitHub 上最强的能力资产可能藏在 `SKILL.md`、playbook、workflow 或完整团队中，而不一定叫 Expert。

进入系统前，这些都只是 **source asset / 候选资产**，不是正式专家。

## 4. 候选标准化

每个候选至少记录：

- 来源仓库与路径；
- source type；
- License；
- 语言；
- 能力标签；
- 与岗位的 fit；
- 中文原生度；
- 跨平台可迁移性；
- 可维护性；
- 与现役专家的职责重复度。

候选综合分：

```text
40% 岗位匹配
20% 中文原生度
15% 可迁移性
15% 可维护性
10% 非重复价值
```

## 5. 许可证门禁

宽松许可证（MIT / Apache-2.0 / BSD / ISC）可进入复制与改造候选流程，但仍必须记录 attribution。

GPL / LGPL / MPL / AGPL 默认进入 `review`，核心仓库不自动复制。

未知、无许可证或不明确许可证：

```text
RESEARCH_ONLY
```

可以研究架构和能力定义，但不能直接复制内容。

## 6. 招聘闭环

```text
用户任务
↓
现役能力覆盖检查
↓
能力缺口诊断
↓
Expert / Skill / Tool / Knowledge / Workflow
↓
如果不是 Expert → 补能力，不招人
↓
如果是 Expert → 临时顾问 or 正式岗位
↓
生成搜索词
↓
发现 GitHub / 社区 / 原创候选
↓
许可证 + 能力 + 重复度筛选
↓
中文标准化草案
↓
Shadow
↓
Eval Arena
↓
CAO 人事建议
↓
Auditor
↓
正式入职 / 延长试用 / 拒绝
↓
继续完成最初用户任务
```

最后一行最重要：**招聘是手段，完成原始任务才是目的。**
