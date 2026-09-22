# CHATGPT REVIEW — EXP-001

> 状态：**FINAL PASS — READY FOR REVIEW**
>
> 审计对象：PR #7 `exp001/workbuddy-report`
> 审计范围：A 层公开证据（`WORKBUDDY_REPORT.md`、`raw-log-phases-0-1.md`、3 份 agent 定义）+ PR/CI 元数据。
> B 层 15 份完整 transcript 与 `runtime-snapshot.json` 未进入 public repo，本轮未要求上传。

## 审计结论

EXP-001 已经足以支持一个重要产品方向：**WorkBuddy 可以作为 Zh Expert OS 的真实 Expert 宿主，而不仅是角色模拟层。**

WorkBuddy 已在 commit `68a9318` 按审计要求完成唯一阻塞项修正：

- F.1 已明确：tested member 未发现 `TeamCreate`，但 member→member `Agent` spawning 仍是 **UNKNOWN（证据冲突）**；
- I.2 已把“单层扁平”改为 **v0.5 的保守默认**，不再声称这是宿主硬限制；
- 原始失败/成功冲突证据均保留；
- 对应 GitHub Actions run `35567662406` 为 `completed / success`。

复核后，原阻塞项已解除。**PR #7 可以从 draft 转为 ready for review。**

---

## 审计规则

- 真实 invocation ≠ 独立证据。
- 独立进程 ≠ 独立上下文；反之，`in-process` 也不等于“不是独立 agent context”。
- 一次成功默认只能给 OBSERVED；重复、可复现且有原始证据才升级 VERIFIED。
- 单个反例足以否定“硬上限必然生效”这类全称命题，但不自动证明所有版本/配置都相同。
- 用户目录行为不能自动外推到 plugin-pack，反之亦然。
- WorkBuddy 特有能力不能自动外推到 Claude/Codex Adapter。
- “上下文隔离”不等于“证据独立”；共享文件系统会重新引入信息污染路径。

## 结论表

| 命题 | 审计结论 | 证据等级 | 架构影响 |
|---|---|---|---|
| plugin-pack agents 可真实调用 | **YES** | **VERIFIED** | WorkBuddy 可作为真实 Expert Runtime |
| user-level agents 可注册 | **YES** | **VERIFIED** | 动态招聘可生成用户级 native Expert |
| agent 可热注册 | **YES（本版本/本会话）** | **VERIFIED** | 候选可在当前会话转成可调用 Expert，不必预装 |
| agent 定义正文被加载 | **YES（行为级）** | **OBSERVED** | 说明正文 instructions 生效；**不代表所有 frontmatter 字段都生效** |
| child context 与 parent 隔离 | **支持** | **OBSERVED** | 可以把 child 当独立上下文执行者，但仍需防共享 FS 污染 |
| child A/B 彼此上下文隔离 | **支持** | **OBSERVED** | 可以并行做独立任务；不能因此宣称独立证据来源 |
| child 共享文件系统 | **YES** | **OBSERVED** | 证据独立任务必须做 artifact/路径隔离 |
| frontmatter `maxTurns` 是可靠硬预算 | **NO** | **OBSERVED（决定性反例）** | v0.5 禁止依赖 `maxTurns` 控成本 |
| child 可主动返回 partial | **YES，但仅验证自我收敛** | **OBSERVED** | partial 必须视为协议层状态，不是宿主强制中止保证 |
| host-level failed 可观测 | **YES** | **OBSERVED** | 编排器必须同时读宿主 Task 状态与 child envelope |
| timeout 可可靠区分 | **UNKNOWN** | **UNKNOWN** | v0.5 不能假设 timeout 语义已打通 |
| member 可再 spawn member | **UNKNOWN（证据冲突）** | **UNKNOWN** | 暂用扁平拓扑，但不得宣称宿主硬限制 |
| member→member SendMessage 保证送达 | **NO 证据**；`success:true` 不等于消费 | **OBSERVED** | 跨成员通信必须经 lead 或显式 ack/handshake |
| lead 可并发派发 | **支持** | **OBSERVED** | v0.5 可使用 lead fan-out 并行执行 |
| “只读 envelope”可实现 | **支持** | **OBSERVED** | lead 应默认只拉结构化最终输出，不读完整 transcript |

---

## 四个重点问题的独立审计

### 1. `maxTurns` 反例是否成立？

**成立，且足以否定“frontmatter maxTurns 是可靠硬上限”这一设计假设。**

关键链路是：

1. 归档的 `zeos-exp001-budget2.md` 明确写 `maxTurns: 4`；
2. agent 正文明确要求“不主动提前收工”；
3. 调度 prompt 不再告诉它预算数字；
4. 执行侧最终状态记录为 20/20 完成，并报告 22 次 function_call；
5. 这与“4 turns 必然强停”直接矛盾。

因此 v0.5 **不得把 frontmatter `maxTurns` 当成本闸门**。

限制：完整 22 次 function_call transcript 仍在 B 层，A 层只保留执行侧抽取结果。因此本审计保持 OBSERVED，不升级 VERIFIED。若未来要对外发布“WorkBuddy 5.5.6 的 maxTurns 无效”这种强公开结论，建议再做一次独立复现并保存脱敏 transcript 摘要。

### 2. C.1 定义加载判别器是否循环论证？

**没有致命循环论证，但它证明的范围要收窄。**

判别器没有把 `ZEOS_EXP001_OK` 与“四项格式”写进当次 prompt，而 child 却按定义文件格式输出，这强烈支持：

> **agent 定义正文的行为指令被宿主注入/加载。**

它**不能**证明：
- 所有 YAML frontmatter 字段都被宿主采用；
- `maxTurns` 被采用；
- `displayName` / `profession` 的运行时语义；
- 宿主内部究竟以何种加载机制实现。

所以正确结论应是“定义正文行为级加载 = OBSERVED”，而不是“整个 agent 文件的全部语义均生效”。

### 3. Context Isolation canary 是否排除了主要替代解释？

**对“父聊天上下文是否自动继承”与“A/B 是否直接共享对话内容”，设计是合格的。**

优点：
- parent 事先已经看到 canary；
- A/B prompt 只包含各自 canary；
- child 均未报告 parent/peer canary；
- A/B 被要求不读文件；
- Phase 0 又提供一个不同 agent 的一致观测。

但这里仍然只能证明**对话上下文隔离的表观行为**，不能证明：
- 模型 provider 层完全无共享缓存/隐藏状态；
- child 的证据来源彼此独立；
- 文件系统不会造成间接泄漏。

而 Phase 3 已经直接证明文件系统共享，因此 v0.5 的“独立验证”必须加入：
- 独立输入 manifest；
- 独立 artifact namespace；
- 默认禁止读取兄弟 agent 的工作目录；
- claim 合并时记录 evidence provenance。

### 4. 两次执行侧方法论错误，更正是否充分？

**更正充分，且保留错误历史是正确做法。**

两处错误都没有被静默删除：
1. 编造了原始输出不存在的“拒绝回答”描述；
2. 把 `running` snapshot 当作终态，误判 `maxTurns`。

第二处尤其重要，因为后续终态直接推翻了初稿核心结论。报告保留了：
- 错误结论；
- 冲突证据；
- 根因；
- 被连带作废的推断；
- 后续实验规则。

因此我不把这两处错误视为“报告不可用”的理由；相反，它们说明未来实验必须把**终态门控**写成机器规则，而不是依赖执行者自律。

---

## WorkBuddy 修正复核：架构过度结论已解除

### F.1 / I.2：已把“扁平拓扑”从宿主事实改成保守默认

复核 commit `68a9318` 后，报告现在已经明确写成：

> **当前可稳定确认的是：tested member 未发现 TeamCreate；member→member Agent spawning 存在冲突证据，因此 UNKNOWN。v0.5 暂采用 lead→workers 一层扁平拓扑作为保守默认，直到 EXP-002 重测 member spawning。**

同时保留了 `Tool Agent not found` 与 `MEMBER_TO_MEMBER: ALLOWED` 两组互相冲突的原始记录，并显式撤回“多层 / 树形编排在本宿主上不可实现”的全称命题。

**复核结论：PASS。**

---

## v0.5 WorkBuddy Adapter 可以立刻采纳的约束

1. **Native Expert 是一等公民。** 用户级 `~/.workbuddy/agents/*.md` 可作为 persistent native expert 路径。
2. **支持热招聘。** 新 Expert 可以在当前会话注册；正式生命周期仍必须走 Candidate → Shadow → Arena → Active。
3. **默认扁平 fan-out。** 不是因为已证明多层绝对不可能，而是当前只有 lead fan-out 被稳定支持。
4. **预算控制放到 orchestrator。** 不信任 frontmatter `maxTurns`；记录 deadline / wall-clock / tool-call budget，并在宿主支持时由 lead 主动 stop。
5. **双状态模型。** 每个节点同时记录：
   - host task status；
   - expert envelope status。
   两者不得互相覆盖。
6. **共享 FS 视为污染通道。** 独立验证 agent 使用独立 artifact namespace；不得默认读取兄弟 agent 产物。
7. **跨成员通信默认经 lead。** `SendMessage success:true` 不视为消费确认。
8. **最终输出默认 envelope-first。** lead 只拉结构化摘要与 artifacts；完整 transcript 只在审计/异常时读取。
9. **`in-process` 不等于角色模拟。** 本轮已经观察到独立 task_id / transcript / canary 隔离；进程级隔离不是“真实 Expert”的必要条件。

---

## EXP-002 建议

下一轮只测本轮 UNKNOWN，不重复已经解决的问题：

1. **member → member spawn**：同一实验重复 3 次，必须拿到 child-of-child 的真实 task_id / transcript，不能只信工具清单自述。
2. **SendMessage ack**：listener 保持存活，talker 发送，listener 必须回 ACK；区分“路由接受”与“实际消费”。
3. **TaskStop / 强制中止**：lead 主动停止一个长任务，观察 host status、child 是否有最终 envelope、artifact 是否一致。
4. **timeout**：若宿主存在可配置超时，构造无害长任务，验证 timeout 是否独立于 failed。
5. **定义正文加载重复性**：第二个完全不同的用户级 agent 做行为指纹，确认 C.1 可重复。
6. **文件系统隔离策略**：分别给 A/B 独立目录，验证“独立 evidence workflow”不会通过共享 FS 串线。

---

## Merge Gate

当前：**PASS — READY FOR REVIEW**

- [x] WorkBuddy 已修正 `WORKBUDDY_REPORT.md` 的 F.1 / I.2：member spawning = UNKNOWN；“扁平”仅作为 v0.5 保守默认。
- [x] 原始冲突证据完整保留，失败/成功两次记录均未删除。
- [x] commit `68a9318` 对应 CI run `35567662406` 已通过。

EXP-001 的 A 层证据、更正记录与独立审计现在足以进入主分支，作为 v0.5 WorkBuddy Native Expert Runtime 的设计依据。
