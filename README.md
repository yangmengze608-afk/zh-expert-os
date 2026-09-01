# 中文 AI 专家团操作系统（Zh Expert OS）

> 一个面向中文用户、可自我招聘 / 试用 / 晋升 / 降级 / 裁撤专家的开源 AI 专家组织框架。

**当前版本：v0.1.0 — 治理内核 MVP**

本项目不是“几百个 Prompt 的合集”。第一版先解决更底层的问题：**一个专家组织应该如何长期保持最强？**

核心设计：

- **首席专家官（CAO）**：持续发现能力缺口、招聘候选、安排试岗、提出晋升 / 降级 / 合并 / 退休建议。
- **独立审计官（Auditor）**：独立审核 CAO 的人事建议，防止评价漂移、偏袒和自我强化。
- **组织宪法（Constitution）**：CAO 与普通专家都不可自行修改的最高规则。
- **Router**：面向具体任务自动组建临时专家团，而不是让用户手动挑几十个 Agent。
- **Red Team**：对重要结论做反证、找漏洞和失效条件。
- **候选 → 试用 → 正式 → 替补 → 退休**：专家有完整生命周期，退休不等于删除，可回滚、可召回。
- **证据化晋升**：用同任务盲测、胜负记录、质量评分和贝叶斯后验来决定挑战者是否真的强于现任。
- **中文原生**：角色定义、任务理解、输出规范、治理术语均以简体中文为主，不以“翻译英文 Prompt”为产品定位。

## 1. 组织结构

```text
                         人类维护者
                             │
                    constitution/宪法
                             │
              ┌──────────────┴──────────────┐
              │                             │
        首席专家官 CAO                  独立审计官
   招聘 / 试用 / 晋升 / 裁撤             监督 CAO
              │                             │
              └──────────────┬──────────────┘
                             ↓
                        专家注册表
                             │
             候选 → 试用 → 正式 → 替补 → 退休
                             │
                             ↓
                           Router
                             │
                 按任务临时组建专家团
                             │
                             ↓
                         Red Team
                             │
                             ↓
                         最终交付
```

## 2. v0.1.0 已经能做什么

这是一个**可运行的治理内核**，不是只有文档：

```bash
python -m zh_expert_os.cli list
python -m zh_expert_os.cli show cao
python -m zh_expert_os.cli recruit examples/candidates/chinese-market-researcher.json
python -m zh_expert_os.cli record-match --challenger chinese-market-researcher --incumbent router --wins 14 --losses 6 --ties 0
python -m zh_expert_os.cli recommendation --challenger chinese-market-researcher --incumbent router
```

核心逻辑包括：

1. 注册 / 更新候选专家；
2. 记录挑战者与现任的同任务盲测结果；
3. Beta-Binomial 贝叶斯后验估计挑战者胜率；
4. 结合质量、事实性、稳定性、独立价值、成本效率等维度形成综合分；
5. 根据硬门槛生成 `PROMOTE / EXTEND_PROBATION / REJECT` 建议；
6. 重大人事变动必须进入审计流程，不能由 CAO 自己直接永久删除专家。

## 3. 快速开始

要求 Python 3.11+，核心包**零第三方依赖**。

```bash
git clone https://github.com/yangmengze608-afk/zh-expert-os.git
cd zh-expert-os
python -m pip install -e .
zh-expert-os list
zh-expert-os show cao
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 4. 专家不是 Prompt，而是“可管理资产”

每个专家至少要有：

```text
身份 / 使命
适用场景
不适用场景
输入要求
工作流程
工具权限
证据要求
输出规范
自检规则
协作关系
评测指标
版本与来源
```

规范见 [`docs/EXPERT_SPEC.md`](docs/EXPERT_SPEC.md)。

## 5. 招聘与裁撤原则

CAO **不能**“看到 GitHub 上一个 Agent 就直接塞进来”。标准流程：

```text
发现能力缺口
→ 招募候选
→ 统一中文标准化
→ 离线基准测试
→ Shadow 试岗
→ 与现任同任务盲测
→ 贝叶斯后验 + 质量门槛
→ Auditor 审计
→ 晋升 / 延长试用 / 拒绝 / 退休
```

`retired` 是历史库而不是垃圾桶。永久删除是例外动作。

## 6. 为什么用贝叶斯后验

“挑战者 7:3 赢了现任”不代表已经证明挑战者更强，样本可能太少。

系统把挑战结果建模为：

```text
p ~ Beta(1, 1)
观察 wins / losses 后：
p | data ~ Beta(1 + wins, 1 + losses)
```

然后估计：

```text
P(p > 0.5 | data)
```

只有在**样本量、后验概率、事实性和稳定性**都过线时才建议晋升。新证据出现后，判断会继续更新。

## 7. 当前种子专家

v0.1.0 故意只保留 4 个治理专家：

- `cao` — 首席专家官
- `auditor` — 独立审计官
- `router` — 中文任务路由官
- `red-team` — 红队反证专家

后续领域专家应该通过同一套“招聘系统”进入，而不是维护者一次性手写 200 个。

## 8. 路线图

- **v0.1**：治理内核、专家生命周期、贝叶斯挑战赛、宪法、审计。
- **v0.2**：真正的 Eval Runner；支持 JSONL 任务集、匿名 A/B 输出、LLM/Judge + 人类评分。
- **v0.3**：GitHub 招聘器；发现开源候选并生成许可证 / 来源 / 能力差异报告。
- **v0.4**：中文 Router + 动态专家组队 + Red Team + Synthesis。
- **v0.5**：Claude / Codex / ChatGPT / Cursor 适配器。
- **v1.0**：中文 Expert OS：自动招聘、自动试岗、自动评测、人工治理、跨平台运行。

详情见 [`docs/ROADMAP.md`](docs/ROADMAP.md)。

## 9. 开源策略

代码建议采用 **MIT License**。外部专家资产必须逐项记录来源与许可证，禁止把不兼容许可证的 Prompt / 代码直接复制进入核心仓库。

这也是项目的一个原则：**借鉴架构，不做许可证洗白。**

## 10. 项目定位

> **面向中文用户的开源 AI 专家团操作系统：用一句中文描述任务，自动组建最合适的专家团队进行协作、质疑、验证和交付；同时通过持续招聘、试岗、评测和淘汰，让专家组织长期进化。**
