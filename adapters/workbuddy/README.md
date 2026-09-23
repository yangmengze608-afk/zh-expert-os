# WorkBuddy Native Expert Adapter — v0.5-alpha1

这个 Adapter 的目标不是把 Zh Expert OS 伪装成一段“多人角色扮演 Prompt”，而是把 WorkBuddy 已实测可用的 **native user-level agents** 接成一个可审计的 Expert Team Runtime。

EXP-001 / EXP-002 已确认的宿主边界决定了本 Adapter 的设计：

- `~/.workbuddy/agents/*.md` 可以在当前会话热注册并真实 invocation；
- child 对话上下文表现隔离，但文件系统共享；
- `maxTurns` frontmatter 不能作为硬预算；
- `TaskStop` 2/2 实测能真正停止 worker；
- `SendMessage success:true` 只代表 route accepted，不代表 consumed；
- tested `general-purpose` member 未观测到 nested spawn，因此 v0.5-alpha1 采用 **lead → workers** 一层 fan-out；
- tested interface 没有可验证的 agent timeout/deadline；
- user-level agent 定义正文的行为级热加载可重复；
- artifact namespace 是工程纪律，不是安全沙箱。

详细实验证据见：

- `coordination/experiments/EXP-001-*`
- `coordination/experiments/EXP-002-*`

## 1. 安装

先安装项目 CLI：

```bash
python -m pip install -e . --no-build-isolation
```

然后：

```bash
bash adapters/workbuddy/install.sh
```

安装器同时安装两层：

```text
~/.workbuddy/skills/zh-expert-os  -> adapters/workbuddy/
~/.workbuddy/agents/*.md          -> adapters/workbuddy/agents/*.md
```

- Skill 在**当前 lead/main context** 提供顶层编排契约；
- `agents/*.md` 是真实 native workers；
- 安装器不会覆盖已有同名 Skill / agent。

可用 `WORKBUDDY_SKILLS_DIR` / `WORKBUDDY_AGENTS_DIR` 指定其他目录。

实际使用时，优先让当前主会话加载 `zh-expert-os` Skill，再由主会话调用 native workers。这样避免把 orchestrator 自己先降成一个无 nested-spawn 能力的 child。

## 2. 原生角色

- `zh-expert-os-lead` — 顶层 Meta-Expert / Orchestrator
- `zeos-router` — Capability Map / 最小组队
- `zeos-evidence` — 事实查证与 provenance
- `zeos-red-team` — 反证与替代解释
- `zeos-auditor` — 证据与治理审计
- `zeos-synthesizer` — claim/evidence synthesis
- `zeos-recruiter` — 任务驱动招聘

### 重要：Lead 必须是真正的 lead/main context

EXP-002 没有在 tested worker 中观测到可靠 nested spawn。

所以不要：

```text
main
  → Agent(zh-expert-os-lead)
       → 再让 lead child spawn workers
```

然后假装这是可靠拓扑。

v0.5-alpha1 的宿主语义是：

```text
WorkBuddy 当前 lead/main context
  ↓ 加载/遵循 zh-expert-os-lead contract
Agent(zeos-router)
Agent(zeos-evidence)
Agent(zeos-red-team)
...
```

如果 WorkBuddy 的某种“Expert 包”模式把 `zh-expert-os-lead` 作为真正 team-lead context 加载，它可以直接作为入口。

如果宿主把它当普通 worker，且它检查不到 `Agent` / `TaskStop`，它必须返回 `HOST_CAPABILITY_MISMATCH`，不能假装已组队。

## 3. 运行时协议

### 3.1 Flat fan-out

当前默认：

```text
lead
├─ worker A
├─ worker B
└─ worker C
```

这只是**保守默认**，不是宣称 WorkBuddy 永远不支持树形 multi-agent。

### 3.2 双状态

每个节点必须同时记录：

```text
WorkBuddy host_task_id
+
ZEOS assignment_id
+
host task status
+
expert envelope status
```

Lead 在派发 prompt 里给 worker 一个 `ZEOS_TASK_ID`；worker envelope 的 `task_id` 只回显这个 assignment id。真实 WorkBuddy host task_id 由 lead 从 `Agent` 返回单独记录，二者不能混为一谈。

例如被 `TaskStop` 的 worker 可能是：

```text
host_status = cancelled
envelope = null
```

不要伪造一个 child 自己从未提交过的 final envelope。

### 3.3 Message ACK

跨成员通信默认经 lead。

若必须 `SendMessage`：

```text
ROUTE_ACCEPTED
→ CONSUMED
→ ACKED
```

只有 ACKED 才算 confirmed。

### 3.4 Budget / Stop

不要依赖 `maxTurns`。

Lead 自己维护：
- wall-clock budget
- step/tool-call budget
- host status

超预算：
1. `TaskStop(task_id)`
2. 等 terminal
3. 再读 artifact
4. 合成 partial/cancelled 状态

### 3.5 Artifact namespace

每个 worker 一个唯一 namespace。

Worker 只返回：
- relative path
- sha256

Lead 在所有相关 worker terminal 后重算 hash。

这不是 ACL，也不是安全隔离。

## 4. Evidence provenance

核心代码：`src/zh_expert_os/workbuddy.py`

任何进入 evidence registry 的 claim 都必须携带 `EvidenceRef`：

```text
source_task_id   # 指 ZEOS assignment id
kind
locator
artifact_sha256?
parent_refs?      # derived evidence 必须有
```

优先级：

```text
raw tool result / artifact
> transcript record
> machine-derived transform + provenance
> human/model transcription
```

最后一层不能独立作证。

## 5. 动态招聘 → Native Expert

如果 Recruiter 已把候选注册为 Shadow / probation：

```bash
zh-expert-os workbuddy-export-expert \
  --expert shadow-xxxx
```

默认写入：

```text
~/.workbuddy/agents/shadow-xxxx.md
```

WorkBuddy EXP-001/002 支持当前会话热发现 user-level agent，但：

> **能调用 ≠ 已晋升。**

它仍必须经过 real-task trial / Arena / Auditor / Human approval。

## 6. 知流

见：

`examples/workbuddy/zhiliu-project-prompt.md`

目标仍然是把“知流”做成可运行、可测试的产品；Expert OS 只是内部组织方式，不应把项目变成 Agent demo。

## 7. 当前限制

v0.5-alpha1 **不宣称**：

- member → member nested spawn 可依赖；
- WorkBuddy agent timeout 已打通；
- `maxTurns` 是预算闸门；
- namespace 是安全沙箱；
- `SendMessage success:true` 等于已送达；
- 同模型多个 Expert 自动构成独立证据。
