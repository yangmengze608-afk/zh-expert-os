# 中文 AI 专家团操作系统（Zh Expert OS）

> 面向中文用户、能够按真实任务发现能力缺口、招聘候选、真实调用 Expert、匿名评测、晋升、降级与淘汰 AI 专家的开源专家组织框架。

**当前版本：v0.4-alpha2 — Claude Skill Adapter**

本项目不是“几百个 Prompt 的合集”。核心问题是：**一个 AI 专家组织怎样因为真实任务而进化，并用可复现证据长期保持最强，而不是越堆越大？**

## 核心原则

1. **先有任务，再补能力。** Recruitment is task-driven, not collection-driven.
2. **缺能力不等于缺专家。** 先区分 `Expert / Skill / Tool / Knowledge / Workflow`。
3. **一次性需求不默认永久招人。** 小众能力先用临时顾问，重复或战略能力才建立正式岗位。
4. **搜索的是能力资产，不是只搜 expert。** GitHub 候选可以来自 agent、expert、persona、role、skill、playbook、workflow、team 或高质量领域 repo。
5. **候选不是员工。** 外部资产必须经过来源与 License 检查、中文标准化、Shadow、Eval Arena，赢了才可能入职。
6. **Expert 必须真的运行。** Skill 是同一 Agent 加载方法；Expert 是独立 invocation；Team 是多个 Expert invocation + orchestration。
7. **招聘是手段，完成原始任务才是目的。**

## 1. 已打通的自我进化闭环

```text
用户任务
  ↓
现役能力覆盖检查
  ↓
能力缺口诊断
  ↓
Expert / Skill / Tool / Knowledge / Workflow
  ↓
如果不是 Expert → 补能力，不扩编
  ↓
如果是 Expert → 临时顾问 or 正式岗位
  ↓
GitHub 发现 → 读取 README / SKILL.md / Agent / Role / Playbook
  ↓
背景调查 + CandidateAsset 标准化
  ↓
License + 岗位匹配 + 中文原生度 + 可迁移性 + 可维护性 + 重复度
  ↓
Shortlist → Shadow / probation
  ↓
Expert Runtime：Shadow 与现任独立执行同一真实任务
  ↓
Eval Arena：自动匿名 A/B + 多 Judge
  ↓
长期 Beta-Binomial 战绩
  ↓
CAO 人事建议 → Auditor → 人类批准
  ↓
继续完成最初用户任务
```

招聘协议见 [`docs/RECRUITER.md`](docs/RECRUITER.md)，端到端招聘见 [`docs/RECRUITMENT_PIPELINE.md`](docs/RECRUITMENT_PIPELINE.md)，Runtime 见 [`docs/RUNTIME.md`](docs/RUNTIME.md)，竞技场见 [`docs/ARENA.md`](docs/ARENA.md)。

## 2. v0.4-alpha2：Claude Code 现在可以直接调用

仓库新增标准 Skill 入口：

```text
.claude/skills/zh-expert-os/SKILL.md
```

在本仓库使用 Claude Code 时可以直接调用：

```text
/zh-expert-os 帮我分析当前项目，并组最小充分专家团直接推进。
```

如果要在“知流”或其他独立项目中使用，推荐安装为用户级 Skill：

```bash
git clone https://github.com/yangmengze608-afk/zh-expert-os.git
cd zh-expert-os
python -m pip install -e . --no-build-isolation
bash adapters/claude/install.sh
```

安装后会把 Skill 链接到：

```text
~/.claude/skills/zh-expert-os
```

之后在任意 Claude Code 项目中都可以：

```text
/zh-expert-os <复杂任务>
```

也可以直接描述复杂、跨专业、多步骤任务，让 Claude 根据 Skill 的 `description` 自动判断是否加载。

Claude Adapter 说明见 [`adapters/claude/README.md`](adapters/claude/README.md)。知流项目可直接使用的调用示例见 [`examples/claude/zhiliu-project-prompt.md`](examples/claude/zhiliu-project-prompt.md)。

这个 Skill 只是**入口**，不是把 Zh Expert OS 降级成单个 Skill。运行时语义仍然是：

```text
Skill  = SAME AGENT + instructions
Expert = independent invocation / subagent context
Team   = multiple Expert invocations + orchestration
Tool   = function / API / connector / CLI
Plugin = 安装和分发这些能力的容器
```

## 3. v0.4-alpha1：Expert 真的开始干活

新增：

- `AgentRuntime` 运行时协议；
- `CommandRuntime`：通过外部 CLI / 适配脚本启动独立 Agent 进程；
- `CallableRuntime`：测试和宿主集成接口；
- Expert 配置 → 独立 invocation；
- Shadow 与 incumbent 默认并行执行同一 `ArenaTask`；
- 输出自动写入 Arena，并立即匿名成 A/B；
- 执行成功后 battle 自动进入 `judging`；
- Runtime 超时、非零退出码、空输出全部 fail loud；
- `shell=False`，不把用户任务拼进 shell 命令。

核心实现：

- `src/zh_expert_os/runtime.py`
- `src/zh_expert_os/trial.py`

## 4. 一条命令让 Shadow 和现任真正 PK

Runtime 配置示例：

```json
{
  "type": "command",
  "command": ["python", "my_agent_adapter.py"],
  "timeout_seconds": 300
}
```

适配器只需要：**stdin 读取 Prompt，stdout 输出最终答案**。

然后执行：

```bash
zh-expert-os runtime-trial \
  --task-file examples/arena/task-product.json \
  --challenger shadow-xxxx \
  --incumbent product-incumbent \
  --runtime-config runtime.json
```

Runtime Trial **不会自动晋升**，因此招聘系统依然不能绕过 Arena / Auditor / 人类治理。

## 5. 招聘流水线

```bash
zh-expert-os recruit-pipeline \
  --gap-file examples/recruiter/gap-china-edu-gamification.json \
  --output registry/recruitment/study-pet-001.json
```

默认只调查，不修改专家注册表。确认要试岗时：

```bash
zh-expert-os recruit-pipeline \
  --gap-file examples/recruiter/gap-china-edu-gamification.json \
  --register-shadow 1 \
  --output registry/recruitment/study-pet-001.json
```

代码级 GitHub 搜索通常需要 `GITHUB_TOKEN`；没有 Token 时仍可做仓库级发现。

## 6. Eval Arena

已实现同题匿名 A/B、AB/BA 顺序对冲、多 Judge、事实错误硬门槛、分歧率与位置偏差监控、幂等战绩写回以及长期 Beta-Binomial 晋升证据。

注意：同一个模型扮演多个 Judge 不等于多个统计独立证据。

## 7. 快速开始

要求 Python 3.11+，核心包零第三方依赖。

```bash
git clone https://github.com/yangmengze608-afk/zh-expert-os.git
cd zh-expert-os
python -m pip install -e . --no-build-isolation
python -m unittest discover -s tests -v
```

## 8. 当前治理角色

- `cao` — 首席专家官：发现缺口、提出招聘与人事建议；
- `auditor` — 独立审计官；
- `router` — 中文任务路由官；
- `red-team` — 红队反证专家；
- `arena-director` — 竞技场主持官；
- `arena-judge` — 匿名评测裁判。

## 9. 开源与许可证原则

核心代码使用 MIT License。MIT / Apache-2.0 / BSD / ISC 可进入标准化与 Shadow 流程但仍保留来源；MPL / GPL / LGPL / AGPL 默认 `review`；未知或缺失许可证为 `RESEARCH_ONLY`。

> **借鉴架构，不做许可证洗白。**

## 10. 路线图

- **v0.1 ✅**：治理内核、专家生命周期、贝叶斯晋升、宪法、审计。
- **v0.2 ✅**：匿名 Eval Arena、多 Judge、偏差监控、长期战绩。
- **v0.3 ✅**：任务驱动 Recruiter、能力缺口分类、License 门禁、Shadow 准入。
- **v0.3.1 ✅**：GitHub 仓库 / 代码候选实时发现。
- **v0.3.2 ✅**：读取候选资产、背景调查、Shortlist、Shadow 规格与 CLI 流水线。
- **v0.4-alpha1 ✅**：Expert Runtime Bridge；Shadow 与现任可真正执行同一任务并自动进入 Arena。
- **v0.4-alpha2 ✅**：Claude Code Skill Adapter；可从任意项目以 `/zh-expert-os` 作为总入口。
- **v0.4**：Team Runtime：Router 自动组队、并行/串行 Workflow、Red Team、Evidence Synthesis、任务表现写回。
- **v0.5**：Codex / ChatGPT / Cursor / Gemini 等更多平台 Adapter。
- **v1.0**：中文原生、自我进化的 AI Expert OS。

## 11. 项目定位

> **用户像调用一个“超级 Expert”一样调用 Zh Expert OS；它在内部诊断能力、招聘候选、真正调用多个 Expert、让候选用真实任务证明自己，再由证据决定组织如何进化。**
