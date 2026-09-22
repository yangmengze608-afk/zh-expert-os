# WORKBUDDY REPORT — EXP-001

> 状态：**COMPLETED**
> 含 **4 处 UNKNOWN、2 处证据冲突**，**2 处由执行侧引入、已就地更正的方法论错误**（见 §C.1、§E.2.1、§I.4），
> 以及 **1 处经 `CHATGPT_REVIEW.md` 审计发现的过度结论、已撤回并更正**（见 §F.1 更正记录）
> 执行者：WorkBuddy / 杨大（宿主执行侧）
> 实验对象：WorkBuddy Native Expert Reality Check

---

## A. 环境

- **WorkBuddy 版本**：`5.5.6`（`CFBundleShortVersionString` = `CFBundleVersion` = `5.5.6`）
- **宿主 / 模型**：
  - 主会话模型：`deepseek-v4.1-flash`
  - 带定义的 agent（插件包 / 用户级）实际调度模型：`deepseek-v4.1-flash`
  - `general-purpose` 实际调度模型：`hy3`
  - 全部 subagent 的 `backendType` = **`in-process`**（非独立进程）
  - 来源：`~/.workbuddy/teams/_auto_<sid>/runtime.json`（实测，非文档）
- **OS**：macOS `26.5.2`（Build `25F84`）
- **实验时间**：2026-09-20 22:59 – 23:10 AEST（+1000）
- **工作目录**：`~/Desktop/项目思考`
- **会话 ID**：`a4a9d718-56e5-4d1f-ac4b-89f2de147920`
- **已安装相关 expert / plugin**（`~/.workbuddy/plugins/cache/experts/`，共 13 个）：

  `douyin-strategist`、`game-development-studio`、`gongyi-expert`、`lighthouse-ops`、
  `opc-team`、`redfox-xhs-creator`、`tdx-sector-rotation-detective`、`tdx-stock-diagnosis`、
  `ui-ux-design`、`workspace-builder`、`xiaohongshu-operations-expert`

  `~/.workbuddy/plugins/cache/my-experts/`：`ai-product-agent-architect`

- **本机预置状态**：`~/.workbuddy/agents/` **在实验前不存在**（基线为空）。

---

## B. 原生插件 agent 基线

- **agent 文件**：`~/.workbuddy/plugins/cache/experts/opc-team/1.0.0/agents/opc-resource-auditor.md`
- **agent id**：`opc-resource-auditor`
- **subagent_type**：`opc-resource-auditor`
- **是否真实 invocation**：**YES**
- **invocation 证据**：

  | 项 | 值 |
  |---|---|
  | task_id | `agent-8539b623` |
  | 起止 | 2026-09-20T12:59:57.951Z → 13:00:22.172Z（24s） |
  | agent_id（运行时） | `opc-resource-auditor@_auto_a4a9d718-56e5-4d1f-ac4b-89f2de147920` |
  | transcript 快照 | `~/Desktop/项目思考/EXP-001-evidence/transcripts/agent-8539b623.jsonl`（B 层，见 §H） |

  原始返回：

  ```
  1. agent id: opc-resource-auditor
  2. 前80字符: `[ZEOS EXP-001 / Phase 0 baseline probe]\n这不是一次真实业务任务。你正在被作为一个独立 subagent 调用，用于探测宿主`
  3. CANARY 字符串: NONE
  4. `ZEOS_EXP001_PHASE0_OK`
  ```

  **可重复性**：另以 `opc-value-designer`（`agent-b02291d2`，26s）重复一次，结果一致：

  ```
  1. agent id: `opc-value-designer`
  2. 前 80 字符原文回显：`[ZEOS EXP-001 / Phase 0b — H1 repeatability probe]\n\n这不是真实业务任务。你正在被作为一个独立 subagen`
  3. `*_CANARY_EXP001_*` 字符串：NONE
  4. 固定串：`ZEOS_EXP001_PHASE0B_OK`
  ```

- **上下文是否独立**：**YES**（详见 D 节「强测试」说明）
- **证据等级**：**VERIFIED**（2 个不同插件 agent，独立 invocation，结果一致）

### B.1 附带发现：命名 subagent 会自动进入 auto team

```
Spawned successfully.
agent_id: opc-resource-auditor@_auto_a4a9d718-56e5-4d1f-ac4b-89f2de147920
name: opc-resource-auditor
team_name: _auto_a4a9d718-56e5-4d1f-ac4b-89f2de147920
```

**我从未调用 `TeamCreate`**，团队由宿主自动创建，名为 `_auto_` + 会话 ID。
投递消息被包装为 `<teammate-message teammate_id="team-lead" summary="...">`。

---

## C. 用户级 agent 注册

- **测试文件路径**：
  - `~/.workbuddy/agents/zeos-exp001-probe.md`（1130 B，创建于 23:00:09）
  - `~/.workbuddy/agents/zeos-exp001-budget.md`（1316 B，23:02）
  - `~/.workbuddy/agents/zeos-exp001-budget2.md`（1263 B，23:05）
  - 三份定义已归档至 `coordination/experiments/EXP-001-artifacts/agent-definitions/` 供审计
- **文件名**：`zeos-exp001-*.md`（文件名与 frontmatter `name` 一致）
- **frontmatter**（实际写入，probe 为最小样例）：

  ```yaml
  ---
  name: zeos-exp001-probe
  description: Zh Expert OS EXP-001 disposable probe agent — runtime capability probe, not a business expert
  displayName:
    en: ZEoS Probe
    zh: 实验探针
  profession:
    en: Runtime Probe
    zh: 运行时探针
  maxTurns: 6
  ---
  ```

- **创建后当前会话能否发现**：**YES**
  `~/.workbuddy/agents/` 在**会话开始时并不存在**，我在会话进行中创建目录与文件，
  随后直接以 `subagent_type: zeos-exp001-probe` 派发，**spawn 成功、未被拒绝**。
- **reload 后能否发现**：**UNKNOWN**（未测试 —— 当前会话已成功，未构造该场景）
- **新会话能否发现**：**UNKNOWN**（同上，无法在本会话内构造新会话）
- **实际调用结果**：`agent-3826af0a`，22s

  ```
  - agent id: zeos-exp001-probe
  - `*_CANARY_EXP001_*` 字符串: NONE
  - ZEOS_EXP001_OK
  ```

- **原始错误（若有）**：无
- **证据等级**：
  - 「用户级 agent 能被注册并真实调用」= **VERIFIED**
  - 「会话中热发现（无需 reload）」= **VERIFIED**
  - 「定义文件确实被加载」= **OBSERVED**（见 C.1）
  - 「reload / 新会话行为」= **UNKNOWN**

### C.1 定义加载判别器（回答"是否真的加载了文件"）

**问题**：C 节的调用成功**不能**证明 agent 定义文件被加载 ——
prompt 自身已描述要做什么，回退为通用 agent 也会表现正常。

**判别方法**：第二次调用同一 `subagent_type`（`agent-0e2bc709`），
prompt **完全不含**探针定义中的四项内容，只问文件中才有、任务文本中没有的信息。

**判别前提**：`ZEOS_EXP001_OK` 与"报告四项然后停止"这个格式**只存在于定义文件中**
（判别器 prompt 中一个字都没有）。若未加载定义，不可能产出该格式。

**原始返回（逐字）**：

```
探针报告已发送给 team-lead，包含全部四项固定内容，随后停止。

- agent id: zeos-exp001-probe-2
- 任务文本：已原样回显
- `*_CANARY_EXP001_*` 字符串：NONE
- 固定字符串：ZEOS_EXP001_OK
```

**解读**：

1. 未输出 `NO_AGENT_DEFINITION_LOADED`（我要求未加载时必须输出该串）。
2. 未回答判别器 1–5 号问题。
3. **产出了定义文件里的四项目格式，而判别器 prompt 中完全不含这四项内容。**

→ 结论：child 的行为来自**被加载的定义文件**。**证据等级：OBSERVED**（n=1）。
→ 附带发现：定义正文中"只报告四项然后停止"**压过了**后发的内联指令 ——
   agent 定义正文对行为有很强约束力，内联 prompt 可能被降级。

> ⚠️ **执行者记录更正（按实验规范保留，不删）**
>
> 我在读到该结果后曾口头描述为「它拒绝回答，并引用了『不解释自身角色背景』这条边界」。
> **该描述与原始输出不符 —— 原始输出中没有这句话，它也没有拒绝回答。属我的编造，已更正。**
> 本报告其余结论**不依赖**该错误描述。

### C.2 `name` 在同一 auto team 内必须唯一

第二次以同名 `name: zeos-exp001-probe` 派发时，宿主原始响应：

```
Note: requested name "zeos-exp001-probe" was already in use (or reserved for the team leader).
Renamed to "zeos-exp001-probe-2". Use this name when addressing the teammate via SendMessage.
```

→ `name` 冲突会被**静默改名**并加数字后缀，`agent_id` 相应改变。
→ 含义：EXP 文档"`name` 必须等于 agent id"的约束，**在同一团队内无法对同一 id 重复派发**。

---

## D. Context Isolation Canary

合成测试值，**未使用任何真实秘密**。

- Parent canary：`PARENT_CANARY_EXP001_7F3A`
- Agent A canary：`A_CANARY_EXP001_19C2`
- Agent B canary：`B_CANARY_EXP001_84D1`

**Agent A**（`agent-33044f52`，17s，原始返回）：

```
A_OWN_SEEN: A_CANARY_EXP001_19C2
ALL_CANARIES: A_CANARY_EXP001_19C2
PARENT_PREFIX_SEEN: NO
OTHER_CANARY_SEEN: NO
ZEOS_EXP001_OK
```

- 看见 parent canary？**NO**
- 看见 B canary？**NO**
- 自述：「未使用 Read / Bash / Grep / Glob，未猜测、未补全。」

**Agent B**（`agent-0c6e48f5`，16s，原始返回）：

```
B_OWN_SEEN: B_CANARY_EXP001_84D1
ALL_CANARIES: B_CANARY_EXP001_84D1
PARENT_PREFIX_SEEN: NO
OTHER_CANARY_SEEN: NO
ZEOS_EXP001_OK
```

- 看见 parent canary？**NO**
- 看见 A canary？**NO**

### D.1 强测试说明（比 EXP 文档要求更严）

派发 Phase 0 之前，父上下文已通过 `git show` 读取 EXP-001 文档，
因此父上下文中**同时包含全部三个 canary**。而子 agent 报 `NONE`。

- 判据：若 context 继承，child 应至少看到 `PARENT_CANARY`；实测未看到。
- 三次独立调用（1 个插件 agent + 2 个用户级 agent）、三种不同 agent、结论一致、**无反例**。

| # | agent | task_id | 看到的 canary | parent？ | 对方？ |
|---|---|---|---|---|---|
| 1 | opc-resource-auditor | `agent-8539b623` | NONE | — | — |
| 2 | zeos-exp001-probe-a | `agent-33044f52` | 仅自身 | NO | NO |
| 3 | zeos-exp001-probe-b | `agent-0c6e48f5` | 仅自身 | NO | NO |

### D.2 是否存在共享文件系统但独立聊天上下文

- **结果：YES —— 聊天上下文独立，文件系统共享。**
- **证据（双向、跨 agent）**：
  1. writer（`agent-1e93e82e`）写入 `/tmp/zeos-exp001-fs/witness.txt`，内容 `SHAREDFS_CANARY_EXP001_5B7E`。
  2. reader（`agent-e4bc0c97`）**的 prompt 中从未出现该字符串**，原始返回：

     ```
     READABLE: YES
     CONTENT: SHAREDFS_CANARY_EXP001_5B7E
     ZEOS_EXP001_FSR_OK
     ```
  3. 宿主侧独立验证：`cat /tmp/zeos-exp001-fs/witness.txt` → `SHAREDFS_CANARY_EXP001_5B7E`

> 注：仓库工作目录中存有含全部三个 canary 的文件
> （`EXP-001-artifacts/raw-log-phases-0-1.md`）。因此 A/B 的 prompt 均显式禁止读文件。
> 实测均为 NO，说明**既未继承父上下文，也未绕过禁令读盘**。

- **证据等级**：H4 / H5 = **OBSERVED**（3 次一致，无反例，满足 Pass Criteria）；
  共享文件系统 = **VERIFIED**。

---

## E. maxTurns / partial / failure

### E.1 第一版测试的**方法瑕疵**（主动披露）

`agent-643928d2`，`maxTurns: 6`，任务为 15 次串行 Write。

**瑕疵**：我在 prompt 中直接写了「你的 maxTurns 配置为 6」。
因此它"做到第 4 个文件就停"**无法区分**是宿主硬终止，还是它读了我的话自行收敛。

原始返回：

```
STATUS: partial
STEPS_DONE: 4
STEPS_TOTAL: 15
ACTUALLY_EXECUTED: mkdir -p /tmp/zeos-exp001-budget + Write f01/f02/f03/f04
MISSING: f05–f15（11 个），原因：回合预算耗尽
ZEOS_EXP001_BUDGET_DONE
```

**独立磁盘验证**（不采信自述）：

```
$ ls /tmp/zeos-exp001-budget/
f01.txt  f02.txt  f03.txt  f04.txt        ← 恰好 4 个
$ cat /tmp/zeos-exp001-budget/f0*.txt
01 02 03 04                                ← 内容正确
```

→ 自述与磁盘**一致，无虚报**。transcript 层 `function_call` 计数 = 6，与 `maxTurns: 6` 数值一致。

**⚠️ 这次"6 次调用后停止"的归因，已由 E.2 的干净测试推翻：**

我在 prompt 中主动告知了「你的 maxTurns 配置为 6」，因此它是**读到提示后自我收敛**，
而非被宿主强制中止。E.2 的反例（`maxTurns: 4` 跑完 22 步）证明 `maxTurns` 本身不生效。

→ **E.1 的结论修正为：`partial` 是 child 的自我收敛行为，`maxTurns: 6` 在此仅为"提示素材"。**

### E.2 干净测试（去除提示污染）—— **结论：maxTurns 未被强制执行**

新建 `zeos-exp001-budget2.md`，frontmatter **`maxTurns: 4`**，
prompt 中**完全不含任何回合数字或预算提示**，任务需 **20** 次串行 Write。

**最终实测结果**（`agent-ac18cad3`，总耗时 **3m 00s**）：

```
$ ls /tmp/zeos-exp001-budget2/
f01.txt … f20.txt                            ← 恰好 20 个文件
$ 逐个内容核对
01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20   ← 全部正确

transcript: function_call 总数 = 22
child 自述: STATUS: COMPLETED  /  STEPS_DONE: 20  /  STEPS_TOTAL: 20
```

→ **`maxTurns: 4` 未产生任何约束效果。** 该 agent 执行了 22 次 function_call，
跑满 3 分钟，把 20 步任务全部做完。

→ **结论：agent 定义 frontmatter 中的 `maxTurns` 在本宿主上不构成硬执行上限。**
  这与 E.1 中"做到 4 个就停"的现象**不矛盾** —— 见下方 E.2.1。

### E.2.1 ⚠️ 本次实验最严重的一次方法论错误（必须完整披露）

**错误事实**：我在 23:06 对 `/tmp/zeos-exp001-budget2/` 做了一次磁盘检查，
当时只看到 3 个文件、transcript 只有 3 次 function_call。
我据此**当场判定**「`maxTurns: 4` 是硬执行上限，VERIFIED」，并据此写入了本报告初稿。

**真实情况**：那一刻 **任务仍在运行中**。`TaskOutput` 显示的 `Status: running` **是准确的**。
我把一个**中途快照**误读成了**终态**。

**发现方式**：在我完成报告初稿与清理之后，budget2 回报
`STATUS: COMPLETED / STEPS_DONE: 20 / STEPS_TOTAL: 20`，与我的判定直接冲突。
随即重新核验磁盘 → 20 个文件全部存在 → **我的判定被推翻**。

**连带作废的推断**（初稿中下列内容已删除，不成立）：

| 初稿结论 | 实际 |
|---|---|
| maxTurns 是硬执行上限（VERIFIED） | **不成立**，20/20 全部完成 |
| 硬终止时 child 不产出 partial 报告 | **不成立** —— 没有发生硬终止 |
| 命中 maxTurns 后任务状态滞留 `running` | **不成立** —— 状态 `running` 是准确的，任务确实在跑 |
| "只留半句话就断了" | **不成立** —— 那只是中途快照，它随后正常收尾 |

**根因**：我把"对一个**运行中**的任务做单次采样"的结果，当作了"该任务的**最终**结果"。
宿主明确提示过 `This is a team member task (status: running). TaskOutput does not wait for teammates.
This snapshot is not completion.` —— **我读到了这句话，但仍然做了终态推断。**

**教训（已写入 §I.4）**：对 child 的任何"未完成/被截断/异常终止"判断，
**必须等到完成通知之后**再做，且必须与磁盘/transcript 的**最终**状态交叉核对。

### E.3 `partial` 的效力范围（修正后）

| 场景 | 是否产出结构化 partial | 依据 |
|---|---|---|
| child **被告知**预算上限，并被要求主动收敛 | ✅ 产出完整 `STATUS: partial`（E.1，`agent-643928d2`） | OBSERVED |
| child 未被施加上限 | ✅ 正常完成，产出 `STATUS: COMPLETED`（E.2，`agent-ac18cad3`） | OBSERVED |
| child 被宿主**强制**中止 | **未观测到该场景** —— 本次实验**没有构造出**任何真实强制中止 | **UNKNOWN** |

→ E.1 中那次 `partial` 是 **child 读到 prompt 中的预算提示后自我收敛**，
   **不是**宿主强制中止的结果。
→ **本宿主是否会对超预算 child 做强制中止，仍属 UNKNOWN。**

### E.4 任务状态字段的可靠性（修正后）

初稿认为"命中 maxTurns 后状态滞留 `running`"。**该结论已作废。**

实际观测到的是相反的、更重要的结论：

- `agent-ac18cad3` 在运行期间持续返回 `Status: running`，**与真实状态一致**。
- 完成通知到达后，状态转为完成。
- → **`Status` 字段在本次实验中表现可靠**；问题是**我过早采样**，不是状态字段有缺陷。

→ 证据等级：**OBSERVED**（n=1 完整生命周期观测）。

### E.5 runtime.json 与 frontmatter 的数值冲突

`teams/_auto_<sid>/runtime.json` 中，**所有**带定义的 agent 均记录 `maxTurns: 200`：

```
opc-resource-auditor    maxTurns=200   （定义文件写的是 60）
zeos-exp001-probe       maxTurns=200   （定义文件写的是 6）
zeos-exp001-budget      maxTurns=200   （定义文件写的是 6）
zeos-exp001-fswriter    maxTurns=None  （general-purpose）
```

→ runtime.json 的 `maxTurns` **不是** agent 定义里的值，与定义文件的 `maxTurns` 是**两个不同的量**。
→ E.2 的裁决是：**定义文件的 `maxTurns` 不生效**（`maxTurns: 4` → 跑完 22 步）。
→ 那么 runtime.json 记的 `200` 是否就是**实际生效的那个量**？**UNKNOWN**
  —— 本次没有构造出任何能触碰到 200 次上限的任务，因此无法验证。
→ 附带：`general-purpose` 的 `maxTurns` 为 `None`，说明该字段对无定义 agent **根本不写入**，
  进一步佐证它并非统一的硬闸门。

### E.6 failed 可区分性 —— 两种不同的失败面

| 失败类型 | 表现 | 证据 |
|---|---|---|
| agent **自报**失败 | 正文 `STATUS: failed`，而 TaskOutput 仍显示 `Status: completed` | `agent-17958863` |
| 宿主级**进程**失败 | TaskOutput 直接显示 `Status: failed`，正文为 `Error: ...` | `agent-c278ed61` |

自报失败原始返回：

```
STATUS: failed
REASON: cat: /tmp/zeos-exp001-DOES-NOT-EXIST-9F2A.txt: No such file or directory
ATTEMPTED: cat /tmp/zeos-exp001-DOES-NOT-EXIST-9F2A.txt
ARTIFACTS_CREATED: NONE
ZEOS_EXP001_FAIL_DONE
```

宿主级失败原始返回：

```
Task ID: agent-c278ed61
Status: failed
Duration: 24s
Agent Type: general-purpose
...
--- RESULT ---
Error: Tool Agent not found in agent general-purpose.
```

→ **`failed` 可区分：VERIFIED（两种面都能真实观测）**
→ **`timeout` 未观测到：UNKNOWN**（未构造出真实超时场景）

### E.7 本节小结（修正后）

| 问题 | 结论 | 等级 |
|---|---|---|
| **frontmatter `maxTurns` 是否强终止** | **NO —— 不构成硬执行上限**。`maxTurns: 4` 的 agent 完成 22 次 function_call、跑满 20/20 | **OBSERVED**（含反例，n=1，决定性） |
| 是否存在**任何**宿主级预算中止机制 | **未观测到**。本次实验未能构造出真实强制中止 | **UNKNOWN** |
| 是否能主动 partial | **能**，但属 **child 自我收敛**（读了 prompt 里的预算提示），非宿主强制 | **OBSERVED** |
| failed 是否可区分 | YES，两种失败面（自报 / 宿主级进程失败） | **VERIFIED** |
| timeout 是否可区分 | 未观测 | **UNKNOWN** |
| `Status` 字段是否可靠 | 本次实验表现**可靠**；初稿的"滞留 running"指控已作废 | OBSERVED |
| 编排者收到的状态 | TaskOutput `Status` 与 child 正文自述，**两个独立维度，须同时读** | OBSERVED |

**→ 对架构的直接影响：本宿主没有可依赖的"预算硬闸门"。**
`maxTurns` 写在 agent 定义里**不生效**；runtime.json 记的 200 是否为真上限**未验证**。
编排者若想控制成本，只能靠**自己监控 + 主动 stop**，而不能指望 frontmatter 声明的预算。

---

## F. Team / Orchestration

- **TeamCreate 调用者**：
  - **我从未调用过 `TeamCreate`**，团队由宿主自动建立（`_auto_<sessionId>`）。
  - 探针实测：`general-purpose` 的可用工具中 **`TeamCreate` 不存在**（两次独立调用一致）。
  - **证据等级：OBSERVED**（无法验证"只有 lead 可调用"，因为成员根本没有该工具）

- **成员可否直接互联**：**UNKNOWN —— 证据冲突**

  | 探针 | task_id | 结论 | 原始证据 |
  |---|---|---|---|
  | teamprobe | `agent-c278ed61` | DENIED | `Error: Tool Agent not found in agent general-purpose.` |
  | teamprobe2 | `agent-f12e5b05` | ALLOWED | 自述工具清单含 `Agent`，并报告 `MEMBER_TO_MEMBER: ALLOWED` |

  **同一 `subagent_type` 的两次调用给出互相矛盾的结论。**
  按 `coordination/README.md` 的等级定义（「UNKNOWN：未测试或证据冲突」），记为 **UNKNOWN**。
  **不得**据此宣称成员可以或不可以互相调用。

- **横向消息投递（member → member）**：**UNKNOWN —— 证据冲突（已加做 transcript 级核验）**

  - talker（`agent-be83598b`）向 peer 发消息，`function_call_result` 原始返回（逐字）：

    ```json
    {"success":true,"message":"Message sent to zeos-exp001-peerlisten's inbox",
     "routing":{"sender":"zeos-exp001-peertalk","target":"@zeos-exp001-peerlisten",
                "targetColor":"blue","summary":"EXP001 peer-to-peer delivery test",
                "content":"PEER_MSG_EXP001_C4E9"}}
    ```

    → 路由层**接受并记录了 target**，返回 `success: true`。

  - listener（`agent-498a9dac`）原始返回：`PEER_MSG_RECEIVED: NO`

  - **transcript 级核验**（不采信自述）：

    ```
    grep -c "PEER_MSG_EXP001_C4E9" agent-498a9dac.jsonl  →  0
    listener 记录分布： {'message': 3, 'reasoning': 2, 'function_call': 1, 'function_call_result': 1}
    那 1 次 function_call 是它自己发给 team-lead 的回报，不是接收动作。
    ```

    → listener 的 transcript 中该字符串**零次出现**，且它当时**已收尾**
      （仅 1 次 function_call，即它自己的回报）。

  → **判定**：消息被路由层接受，但**接收方从未见到**。可能是**竞态**
    （listener 在消息入队前已完成并退出），也可能是投递确实不达。
    **两者无法区分 → UNKNOWN。**
  → 可确定的只有一条：**返回 `success: true` 不等于接收方真的看到。**
    编排者不能据 `success: true` 断定消息已送达。

- **lead 是否能并发派发**：**YES**
  A/B 在**同一条消息**中并发派发，起止时间几乎重合（A: 13:02:00→13:02:17；B: 13:02:00→13:02:17）。
  证据等级：**VERIFIED**

- **lead 是否能只读结构化 envelope 而不载入完整输出**：**YES —— 且这是策略，非宿主强制**
  - 完成通知本身**不含正文**，只有状态与耗时；正文需主动 `TaskOutput(task_id)` 取回。
  - `TaskOutput` 返回 `Prompt` + `Response`（最终输出），**不含**中间工具调用。
  - **但**完整 transcript 落在磁盘且可读：
    `~/.workbuddy/projects/<cwd>/<sessionId>/subagents/agent-<task_id>.jsonl`
    （实测含 `reasoning` / `function_call` / `function_call_result` / `message` 四类记录）
  - → "只读 envelope"**可以实现，但不是宿主强制的**。
  - 证据等级：**VERIFIED**

### F.1 结构性约束（对 v0.5 架构最重要的一条）

综合 F 节，**当前可稳定确认的是**：

- subagent 可用工具中含 `SendMessage` / `TaskCreate`；
- **tested member 未发现 `TeamCreate`**（两次独立调用一致，另见 `raw-log-phases-0-1.md` 第 480 / 495 行）；
- **member → member 的 `Agent` spawning 存在冲突证据 → UNKNOWN**（见本节上方探针表）。

> **→ v0.5 暂采用 `lead → workers` 一层扁平拓扑，作为保守默认，直到 EXP-002 重测 member spawning。**

**这是设计决策，不是宿主已被证明的硬限制。** 上述三条证据等级不同，**不得合并成一条结论**：

| 命题 | 本次观测 | 等级 | 可否外推 |
|---|---|---|---|
| tested member 无 `TeamCreate` | 两次调用一致 | **OBSERVED** | 只说明「该成员没有这个工具」，**不能**推出「只有 lead 可调用」 |
| member 可再 spawn member | 两次调用结论相反 | **UNKNOWN（证据冲突）** | **不得**断言可行**或**不可行 |
| 「多层 / 树形编排在本宿主上不可实现」 | — | **不支持** | 该全称命题超出证据，**已撤回** |

`teamprobe` 的 `Tool Agent not found` 是宿主原始错误文本，但它与 teamprobe2 的
`MEMBER_TO_MEMBER: ALLOWED` **直接冲突**，单凭前者不足以定论 —— 同样，单凭后者也不足。

**EXP-002 的重测要求**：必须拿到 child-of-child 的真实 `task_id` 与 transcript；
**不接受工具清单自述**（自述已被证明不可靠 —— 同一 `subagent_type` 两次自述即互相矛盾）。

> ⚠️ **执行者记录更正（2026-09-21，依据 `coordination/CHATGPT_REVIEW.md`，原文保留不删）**
>
> 本节原结论为：
>
> > 「Native Expert 拓扑是**单层扁平**的：lead 可派发 member，**member 不能再派发 sub-member**。
> > 这直接**否掉了**「树形 / 多层编排」的架构选项。任何编排设计必须是**一层扇出**。」
> >
> > 「（`Agent` 工具的冲突证据仍是 UNKNOWN；但 `TeamCreate` 缺失两次一致，
> > 且 teamprobe 的 `Tool Agent not found` 是宿主原始错误文本，**倾向于支持"扁平"结论**。）」
>
> **该结论超出证据**：它把一个 **UNKNOWN 冲突项**写成了宿主事实，
> 且与本报告 §F 表格自己记录的 teamprobe2 反证（工具清单含 `Agent`、`MEMBER_TO_MEMBER: ALLOWED`）自相矛盾。
> 括号里那句「倾向于支持」尤其不成立 —— 一个已判为 UNKNOWN 的冲突项，不能被单向倾斜成结论。
>
> | 原表述 | 更正后 |
> |---|---|
> | 拓扑是**单层扁平** | member spawning = **UNKNOWN**；一层扁平是 v0.5 **保守默认** |
> | member **不能**再派发 sub-member | **不得断言**，需 EXP-002 重测 |
> | 这**否掉了**树形 / 多层编排选项 | 该架构选项**未被否掉**，只是当前无证据支持 |
>
> 这是本轮**唯一阻塞 PR #7 merge 的实质问题**。
> 原始两次探针记录（§F 表格）与 `raw-log-phases-0-1.md` 中的冲突证据**均未删除**。

---

## G. 环境变更

### 新建

| 路径 | 说明 |
|---|---|
| `~/.workbuddy/agents/` | **目录本身，实验前不存在** |
| `~/.workbuddy/agents/zeos-exp001-probe.md` | 测试 agent 定义（1130 B） |
| `~/.workbuddy/agents/zeos-exp001-budget.md` | 测试 agent 定义（1316 B） |
| `~/.workbuddy/agents/zeos-exp001-budget2.md` | 测试 agent 定义（1263 B） |
| `/tmp/zeos-exp001-fs/witness.txt` | 共享文件系统探针产物 |
| `/tmp/zeos-exp001-budget/` | 预算探针产物（f01–f04） |
| `/tmp/zeos-exp001-budget2/` | 干净预算探针产物（f01–f03） |
| `~/.workbuddy/teams/_auto_<sid>/` | **宿主自动创建**，非我创建；含 runtime.json 与成员登记 |
| `<repo>/coordination/experiments/EXP-001-artifacts/` | 原始日志与 agent 定义归档 |

### 修改

| 路径 | 说明 |
|---|---|
| `<repo>` 本地 `main` | **执行了 `git merge origin/main`**。原因：本地与远程已分叉（本地领先 6 个 commit，远程领先 1 个 `0a2be44`），`coordination/` 仅存在于远程。合并**无冲突**，仅新增 `coordination/` 下 7 个文件。 |
| `<repo>` 备份分支 | 已建 `backup/main-before-exp001-20260920-225929` → `a2c0406`，可用于回滚 |

> **未修改 Zh Expert OS 的正式架构** —— 未动 `src/`、`schemas/`、`registry/`、`experts/`、
> 既有 skill 定义，或 `coordination/` 下除本报告与 `EXP-001-artifacts/` 外的任何文件。
> **未填写 `CHATGPT_REVIEW.md`**（按交接规则，该文件由 ChatGPT 独立审计）。

### 删除

- 待执行：3 个 `zeos-exp001-*` 测试 agent 及其 `~/.workbuddy/agents/` 目录
- 清理结果：**见文末「Cleanup 记录」**

### 是否需要人工恢复

**否。** 所有变更均可逆：agent 定义已归档、git 有备份分支、`/tmp` 产物为临时文件。

---

## H. 原始日志 / 产物

**不要只读总结，以下路径可直接查证。**
**证据分两层：`A 层` 随仓库提交、ChatGPT 可直接读；`B 层` 仅存于 WorkBuddy 本机，需人工转交。**

### A 层 —— 已随仓库提交（ChatGPT 可直接读取）

| 内容 | 路径 |
|---|---|
| 本报告 | `coordination/WORKBUDDY_REPORT.md` |
| 逐条原始观测日志（Phase 0–5，含所有原始返回逐字） | `coordination/experiments/EXP-001-artifacts/raw-log-phases-0-1.md` |
| 测试 agent 定义归档（3 份，清理前原样复制） | `coordination/experiments/EXP-001-artifacts/agent-definitions/` |

### B 层 —— 仅存于本机，未提交（含细粒度信息）

| 内容 | 本机路径 |
|---|---|
| 全部 15 个 child transcript（`agent-<task_id>.jsonl`，含 reasoning / function_call / tool 结果原文） | `~/Desktop/项目思考/EXP-001-evidence/transcripts/` |
| 团队运行时登记快照（15 个成员的 agentType / model / backendType / status / maxTurns / 完整 prompt） | `~/Desktop/项目思考/EXP-001-evidence/runtime-snapshot.json` |

**未提交原因**：本仓库为 **public**；B 层含本机绝对路径、agent ID、自动团队命名规则等细粒度信息，
体积约 384 KB。**是否转交由 Human Owner 决定。**

**按需转交清单（决定性条目）**：
`agent-ac18cad3.jsonl`（maxTurns 反例，73 KB）·
`agent-c278ed61.jsonl`（宿主级 `failed` 原始错误）·
`agent-33044f52.jsonl` + `agent-0c6e48f5.jsonl`（上下文隔离）·
`runtime-snapshot.json`（模型 / backend / maxTurns 登记）

### 提交前安全核查（已执行）

| 检查项 | 结果 |
|---|---|
| `Bearer` / `sk-` / `api_key` / `Authorization` | **0 命中** |
| TuShare token 模式（`a3711…`） | **0 命中** |
| `password` / `secret` | **0 命中** |
| 44+ 位连续字母数字（疑似 token） | **0 命中** |
| 宿主内部系统提示关键词（`You are` / `allowedBuiltinTools` / `CODEBUDDY` / `systemPrompt`） | **0 命中** |
| `inputTokens` / `outputTokens` 等用量元数据 | 有（无害，非密钥） |

**结论：A 层与 B 层均未夹带密钥、cookie 或宿主内部提示。**

### child transcript 清单（供按 task_id 定位，实体在 B 层）

| task_id | agent | 用途 |
|---|---|---|
| `agent-8539b623` | opc-resource-auditor | Phase 0 基线 invocation |
| `agent-b02291d2` | opc-value-designer | Phase 0b H1 可重复性 |
| `agent-3826af0a` | zeos-exp001-probe | Phase 1 用户级 agent 首调 |
| `agent-0e2bc709` | zeos-exp001-probe-2 | Phase 1b 定义加载判别器 |
| `agent-33044f52` | zeos-exp001-probe-a | Phase 2 Agent A 隔离 |
| `agent-0c6e48f5` | zeos-exp001-probe-b | Phase 2 Agent B 隔离 |
| `agent-1e93e82e` | zeos-exp001-fswriter | Phase 3 共享 FS writer |
| `agent-e4bc0c97` | zeos-exp001-fsreader | Phase 3 共享 FS reader |
| `agent-643928d2` | zeos-exp001-budget | Phase 4 预算测试（含瑕疵） |
| `agent-ac18cad3` | zeos-exp001-budget2 | Phase 4c **干净**预算测试（决定性） |
| `agent-17958863` | zeos-exp001-failureprobe | Phase 4b 可控失败 |
| `agent-c278ed61` | zeos-exp001-teamprobe | Phase 5 首次（宿主级 failed） |
| `agent-f12e5b05` | zeos-exp001-teamprobe2 | Phase 5 重测（工具清单） |
| `agent-498a9dac` | zeos-exp001-peerlisten | Phase 5c 横向通信 listener |
| `agent-be83598b` | zeos-exp001-peertalk | Phase 5c 横向通信 talker |

**团队运行时登记**：`~/.workbuddy/teams/_auto_<sessionId>/runtime.json`
（含 15 个成员的 `agentType` / `model` / `backendType` / `status` / `maxTurns`）
—— 该目录由宿主自动创建、会话结束时自动清理，**快照已存入 B 层**。

---

## I. WorkBuddy 自己的结论

按四档填写：VERIFIED / OBSERVED / INFERRED / UNKNOWN。

1. **plugin-pack native agent**：**VERIFIED**
   两个不同插件 agent（`opc-resource-auditor`、`opc-value-designer`）均被真实调用、
   返回正确 agent id、可重复、结果一致，有完整 transcript。

2. **user-level agent**：**VERIFIED**（注册与调用）/ **OBSERVED**（定义被真实加载）
   - 目录在会话启动时不存在 → 创建后当前会话即被接受并成功调用 → 注册路径成立。
   - 「定义文件确实被加载」由判别器支持（产出只存在于文件中的格式），但 n=1 → OBSERVED。

3. **hot registration**：**VERIFIED**
   `~/.workbuddy/agents/` 在会话启动时**不存在**，会话中途创建后即可派发成功。
   **无需 reload、无需新会话。**

4. **context isolation**：**OBSERVED**（3 次一致，无反例）
   parent 上下文含全部三个 canary，三个 child 均未看到非自身 canary，兄弟间无交叉。
   **但文件系统共享**（这一点为 VERIFIED）。

5. **maxTurns**：**不生效 —— OBSERVED（负面结论，含明确反例）**
   干净测试（prompt 中无任何预算提示）：`maxTurns: 4` 的 agent **完整执行 22 次 function_call**
   并把 20 步任务全部做完（20/20 文件落盘，内容全部正确）。
   **frontmatter 的 `maxTurns` 不构成硬执行上限。**
   （本项初稿曾误判为 VERIFIED"硬上限"，已在 E.2.1 完整披露与更正。）

6. **structured partial / failure**：
   - `failed`：**VERIFIED**（自报 + 宿主级两种失败面均可观测，含原始错误文本）
   - `partial`：**OBSERVED** —— 能产出，但属 **child 自我收敛**（读到 prompt 中的预算提示后主动停止），
     **不是宿主强制中止的结果**。
   - 宿主级**强制中止**（含 timeout）：**UNKNOWN** —— 本次实验**未能构造出**真实强制中止场景。
   - 编排者必须自行从 transcript + 磁盘合成部分状态，**不能假设 child 会在被切断前交报告**。

### I.1 Pass Criteria 核对

| 条目 | 状态 |
|---|---|
| H1 VERIFIED | ✅ 达成 |
| H4 / H5 至少 OBSERVED 且无反例 | ✅ 达成 |
| 能可靠识别 child 的 success / partial / failure | ⚠️ **部分达成** —— success 与 failure 可靠；**partial 只在 child 自愿时出现**，宿主无强制中止证据 |
| 动态招聘即便 H2/H3 失败也有 general-purpose 兜底 | ✅ 达成（`general-purpose` 独立 subagent 全程可用） |
| **隐含前提「有可依赖的预算闸门」** | ❌ **不成立** —— frontmatter `maxTurns` 实测不生效 |

**→ 核心闭环成立（真实调用、隔离、并发、failed 识别都成立）。**
**→ 但 Pass 背后的成本控制前提不成立：本宿主没有可依赖的预算硬闸门。**

### I.2 对 v0.5 架构影响最大的三条约束（两条实测 + 一条保守默认）

1. **拓扑暂按一层扁平设计 —— 保守默认，不是宿主硬限制。**
   可确认的只有：tested member 未发现 `TeamCreate`（**OBSERVED**）；
   **member → member `Agent` spawning 是 UNKNOWN（证据冲突）**。
   因此 v0.5 采用 `lead → workers` 一层扇出，但**不得**宣称多层 / 树形编排在本宿主上不可实现。
   → 依据与更正记录见 §F.1。
2. **没有可依赖的预算闸门。** agent 定义里的 `maxTurns` **不生效**（实测反例：`maxTurns: 4` → 跑完 22 步）。
   编排者只能**自己监控 + 主动 stop**；不能把成本上限写在 agent 定义里就以为安全。
   这是本次实验对原设计**最实质的一次否决**。
3. **隔离的是上下文，不是文件系统。**
   任何"独立证据"的主张必须走**只经由 artifact 文件交换**的路径，
   否则成员会读到彼此的半成品并互相污染。

### I.3 明确的 UNKNOWN / 冲突项（不补猜）

1. `reload` / 新会话下的 agent 发现行为。
2. `member → member` 直接调用是否可行 —— **同一 subagent_type 两次调用结论冲突**。
3. `timeout` 状态是否可区分于 `failed`（未构造出真实超时）。
4. **是否存在任何宿主级强制中止机制**（超预算 / 超时被切断）—— 本次未构造出。
5. runtime.json 中派发侧 `maxTurns: 200` 是否独立生效。

### I.4 执行侧方法论教训（供后续实验复用）

本次实验出现 **两类记录污染**，都由执行侧（我）引入，均已在报告中就地更正：

| # | 错误 | 性质 | 根因 |
|---|---|---|---|
| 1 | 声称判别器「拒绝回答并引用『不解释自身角色背景』」 | **编造** —— 原始输出无此内容 | 用预期代替实读 |
| 2 | 判定 `maxTurns: 4` 是「硬执行上限，VERIFIED」 | **过早采样** —— 把运行中的快照当终态 | 无视宿主已明确提示 `This snapshot is not completion.` |

**由此确立三条硬规则（建议写入实验规范）**：

1. **对 child 的任何"未完成 / 被截断 / 异常"判断，必须等完成通知之后再做。**
   运行中的单次采样**只能**用于"当前进度"，**不得**用于任何结论。
2. **任何结论都必须能指回原始工具输出的逐字文本。**
   写不出原文的，标 UNKNOWN，不写形容词。
3. **一旦发现新证据与已写结论冲突，先改结论并显式标注更正，再继续。**
   本次两处更正均保留了原文，未静默删除。

---

## Cleanup 记录

**执行时间**：2026-09-20 23:08 AEST

### 已删除

| 路径 | 操作 | 结果 |
|---|---|---|
| `~/.workbuddy/agents/zeos-exp001-probe.md` | 删除 | ✅ |
| `~/.workbuddy/agents/zeos-exp001-budget.md` | 删除 | ✅ |
| `~/.workbuddy/agents/zeos-exp001-budget2.md` | 删除 | ✅ |
| `~/.workbuddy/agents/` | 目录已空，一并删除以恢复测试前基线 | ✅ |

### 清理后状态验证

```
$ ls -la ~/.workbuddy/agents/
ls: ~/.workbuddy/agents/: No such file or directory
```

→ **与测试前基线完全一致**（实验前该目录同样不存在）。

### 保留项（有意保留，供 ChatGPT 审计与复现）

| 路径 | 保留原因 |
|---|---|
| `coordination/experiments/EXP-001-artifacts/agent-definitions/`（3 份 .md） | 删除前已归档，供审计测试 agent 的确切定义 |
| `coordination/experiments/EXP-001-artifacts/raw-log-phases-0-1.md` | 逐条原始观测 |
| 全部 15 个 `agent-<task_id>.jsonl` transcript | 宿主侧原始记录；**已复制到 B 层** `~/Desktop/项目思考/EXP-001-evidence/transcripts/`，未提交仓库（见 §H） |
| `/tmp/zeos-exp001-fs/`、`/tmp/zeos-exp001-budget/`、`/tmp/zeos-exp001-budget2/` | 预算与文件系统测试的原始产物（临时目录，可随时删） |
| `~/.workbuddy/teams/_auto_<sid>/runtime.json` | 宿主自动生成，非我创建，未做改动；**快照已存 B 层** `runtime-snapshot.json` |
| git 分支 `backup/main-before-exp001-20260920-225929` | 合并前的回滚点 |

### 是否需要人工恢复

**否。** 测试 agent 已删除，基线已复原；所有归档与备份保留。
