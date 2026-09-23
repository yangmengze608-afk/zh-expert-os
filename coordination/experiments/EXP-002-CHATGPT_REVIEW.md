# CHATGPT REVIEW — EXP-002

> 状态：**FINAL PASS — READY FOR REVIEW**
>
> 审计对象：PR #8 `exp002/workbuddy-control-plane`
> 审计范围：A 层公开证据（`EXP-002-WORKBUDDY_REPORT.md`、`redacted-raw-logs.md`、`runtime-excerpts.json`、两份脱敏 fingerprint agent 定义）+ PR/CI 元数据。
> B 层 15 份完整 transcript、runtime snapshot 与未脱敏 fingerprint 定义未进入 public repo，本轮未直接读取。

## 总体结论

EXP-002 已经把 WorkBuddy v0.5 最关键的控制面边界测得足够清楚：

- **TaskStop 是本轮唯一达到 VERIFIED 的控制面能力**：2/2 run 中，工具返回、宿主状态、transcript 终态与 artifact 冻结四层一致。
- **nested spawn 在当前受测条件下未观测到**：3/3 `general-purpose` parent 无真实 `Agent` function_call、无 grandchild task/transcript；这支持继续采用 `lead → workers` 保守默认，但不支持“宿主永久不支持多层”的全称命题。
- **SendMessage 的 `success:true` 只证明路由层接受，不证明消费**；显式 ACK 是必要协议层。
- **timeout/deadline 在受测接口中未暴露**，因此保持 UNKNOWN，不能用 TaskStop 冒充。
- **artifact namespace 是可审计工程纪律，不是安全隔离。**

WorkBuddy 已在 commit `726fbb4` 完成两处审计修正，并保持原始证据不删：

1. H2 已从“消费/送达依赖回合状态”收紧为：**本实验中与 receiver 回合状态存在稳定关联，但不证明它是唯一或决定性因果因素**。run1/run2/run3 的原始 token、ACK 与 transcript 记录均保留。
2. A 层 `runtime-excerpts.json` 已把 `maxTurns` 纳入完整的 `schema.member_keys`，并明确 `members[]` 只是可公开字段子集；公开证据现在自洽。

另外，EXP-001 遗留的三个 `/tmp/zeos-exp001-*` 目录已在 Human Owner 授权后删除。报告 §K 保留原始“当时仍存在”的冻结态记录，并追加 2026-09-23 的 post-freeze cleanup 更新；这种写法**可接受**，因为它没有改写历史，只记录后续状态变化。

复核结果：**原 merge blocker 已全部解除。PR #8 可以从 draft 转为 ready for review。**

---

## Conclusion Table

| Claim | Audit Conclusion | Evidence Level | Architecture Impact |
|---|---|---|---|
| member can spawn member | **本轮未观测到**，仅限 WorkBuddy 5.5.6 / 本会话 / tested `general-purpose` | **OBSERVED** | v0.5 继续 `lead → workers` 保守默认；不宣称宿主硬限制 |
| `SendMessage success:true` guarantees consumption | **NO** | **OBSERVED** | 路由接受、消费、ACK 三层必须拆开 |
| explicit ACK protocol works | **YES，在 1 个 consumed run 中成立** | **OBSERVED** | v0.5 跨成员消息必须 ACK；无 ACK 不得判送达 |
| TaskStop actually stops worker | **YES** | **VERIFIED** | 可作为 orchestrator 主动成本/生命周期闸门 |
| stopped child reliably emits final envelope | **NO 证据；本轮 2/2 均无最终 envelope** | **OBSERVED** | stop 后由 lead 基于 host status + artifacts 重建 partial 状态 |
| timeout is exposed/distinct | **NOT EXPOSED IN TESTED INTERFACE** | **UNKNOWN** | 不假设 timeout 语义；TaskStop 不冒充 timeout |
| definition body hot-load repeatable | **支持 2/2，但独立审计未见 B 层真值** | **OBSERVED（审计侧）** | 可用于 v0.5，但若要升为独立 VERIFIED，需定向核验 B 层 fingerprint 真值 |
| namespace discipline reduces accidental cross-read | **本轮成立** | **OBSERVED** | 独立任务必须独立 namespace + lead 终态后统一验 hash |
| namespace provides security isolation | **NO** | **不支持** | 禁止称 sandbox / ACL / 安全隔离 |

---

## H1 — Nested Spawn 审计

WorkBuddy 没有重复 EXP-001 的“工具清单自述”错误，而是把成功条件绑定到真实 task graph：

- parent transcript 中必须出现真实 `Agent` function_call；
- 必须出现 child-of-child task/invocation 标识；
- 必须有 grandchild 独立 transcript / output；
- canary 必须在 grandchild 侧出现。

A 层记录显示 3/3 parent 的 function_call 序列中没有 `Agent`，无 grandchild task_id，也无孙代 transcript。

因此正确表述是：

> **在 WorkBuddy 5.5.6、本会话、tested `general-purpose` member 条件下，nested spawn 未被观测到。**

保持 OBSERVED 是合适的。不能升级成“WorkBuddy 永远不支持 nested spawn”。

---

## H2 — Message Delivery / ACK 审计

三层拆分是正确的：

```
ROUTE_ACCEPTED
↓
CONSUMED
↓
ACKED
```

A 层支持：

- ROUTE_ACCEPTED：3/3；
- CONSUMED：1/3；
- ACKED：1/3；
- 两个 mid-turn run 的 listener transcript 中 token 0 次；
- 正向 run 的 token 以新的 user message 进入 listener transcript，然后 listener 发 ACK。

这足以否定：

> `success:true` = 已送达/已消费

WorkBuddy 已按审计要求修正为：

> **在本实验中，消费只出现在 receiver 已结束回合的 run；两个 mid-turn run 均未消费。receiver turn state 与消费结果存在稳定关联，但本实验不证明它是唯一或决定性因果因素。**

这与 A 层证据一致，也保留了 listener 行为、调度时机、唤醒语义等未控变量。

**复核：PASS。** v0.5 工程结论保持：必须显式 ACK；无 ACK 就按未确认处理。

---

## H3 — TaskStop 审计

本轮证据链是合格的，而且比只看工具返回强很多：

1. `TaskStop` 返回 cancelled；
2. runtime member status = cancelled；
3. transcript 终态出现 `Interrupted by user` / `status: incomplete`；
4. stop 后 artifact 文件数冻结；
5. DONE 未生成；
6. stop 后无继续 function_call；
7. 2/2 重复一致。

因此“TaskStop 能实际终止 worker”可以评为 **VERIFIED**。

同时必须保留两个契约边界：

- stop **不是瞬时**，至少观测到一个步长的尾部执行；
- 被 stop 的 child **不能假设会交最终 envelope**，本轮 2/2 都没有。

所以 v0.5 的 stop path 应该是：

```
lead issues stop
→ wait host terminal
→ freeze/read artifacts
→ synthesize partial status
→ never wait for child final envelope as a requirement
```

---

## H4 — Timeout 审计

本轮做法正确：

- 没拿 `TaskOutput.timeout` 冒充 agent deadline；
- 没拿 TaskStop 冒充 timeout；
- 没拿 shell timeout 冒充 WorkBuddy timeout；
- tested invocation/control schemas 与 runtime excerpt 未暴露 agent timeout/deadline。

因此只能结论：

> **UNKNOWN / NOT EXPOSED IN TESTED INTERFACE**

这不是“WorkBuddy 没有 timeout”，只是“本轮受测接口没有暴露可验证的 timeout 语义”。

---

## H5 — Definition Body Hot-load 审计

WorkBuddy 报告的设计是合格的：

- A/B 两个完全不同的 user-level agent；
- signature 不在 dispatch prompt；
- child 返回各自 signature；
- 没有 Read/Grep/Bash 等旁路取值；
- 两个 signature 不同。

但是公开 A 层对 signature 做了正确的隐私/实验脱敏，真值只在 B 层。因此**我无法仅凭当前公开 PR 独立比较“定义真值 = child 输出”**。

所以区分两个等级：

- WorkBuddy 执行侧：按它保存的 B 层证据，可记 **VERIFIED 2/2**；
- ChatGPT 独立审计侧：当前只记 **OBSERVED**。

这**不阻塞** v0.5 使用 user-level native Expert，因为 EXP-001 已经支持正文行为级加载；如果以后要把“2/2 definition hot-load independently VERIFIED”作为对外结论，只需定向提供这四个私有证据即可，无需公开整个 B 层：
- fingerprint A 原始定义；
- A transcript 对应输出片段；
- fingerprint B 原始定义；
- B transcript 对应输出片段。

---

## H6 — Namespace Discipline 审计

当前措辞边界正确。

本轮证明的是：

> 两个 worker 在各自 namespace 工作时，没有观测到 sibling path 进入对方 transcript；artifact hash 可由 lead 在终态后独立重算。

它没有证明任何 ACL / sandbox / 宿主访问控制。

v0.5 应把它编码成**纪律和 provenance**：

- 每个 worker 唯一 artifact namespace；
- prompt 不泄漏 sibling path；
- worker 输出相对路径 + hash；
- lead 在所有相关 worker terminal 后统一读取；
- lead 独立重算 hash；
- synthesis 记录 artifact provenance。

---

## 方法论事故审计

WorkBuddy 本轮再次出现了“自造观测值”的严重错误：伪造了一个看似真实的 SHA256，并把它回显进命令，导致伪值落盘、产生“伪旁证”。

更正过程是充分的：
- 回查 child transcript 原始 stdout；
- 回查 SendMessage 原文；
- 回查 lead 收到的 teammate message；
- 定位伪值首次出现于 lead 自身 reasoning；
- 撤回“child 哈希不可信 / payload 被篡改”的假结论；
- 保留错误记录而非静默删除。

但这说明后续实验与 v0.5 Auditor 必须加一个机器化证据规则：

> **任何进入 evidence registry 的标量/字符串都必须带 provenance pointer（source task_id + record index/tool result + optional artifact hash）。禁止人工重打观测值后再拿它做验证输入。**

优先级建议：

```
raw tool result / artifact
> transcript record
> machine-derived transform with provenance
> human/model transcription
```

最后一层默认不得作为独立证据。

---

## A-layer Artifact Consistency Re-review

`runtime-excerpts.json` 已修正：

- `schema.member_keys` 现在包含 `maxTurns`；
- note 明确 `member_keys` 是 runtime member objects 的完整观测键集；
- `members[]` 被定义为其中的可公开字段子集；
- 当前公开 member objects 没有出现 `member_keys` 之外的字段。

这消除了上一轮指出的 A 层 schema 自洽问题。

**复核：PASS。**

---

## Merge Gate

当前：**PASS — READY FOR REVIEW**

- [x] No running snapshot used as terminal evidence.
- [x] No self-report-only nested spawn claim.
- [x] No `success:true` conflated with message consumption.
- [x] No TaskStop conflated with timeout.
- [x] No namespace discipline mislabeled as security isolation.
- [x] H2 因果措辞已收紧为“稳定关联，不证明唯一/决定性因果”。
- [x] `runtime-excerpts.json` 的 `member_keys` / `maxTurns` 已自洽。
- [x] WorkBuddy correction commit `726fbb4` 对应 CI run `35818228029` 已通过。

EXP-002 的公开证据、修正记录与独立审计现在足以进入主分支，作为 v0.5 WorkBuddy Native Expert Runtime Adapter 的控制面依据。

## Human Owner Cleanup Decision

关于 EXP-001 遗留的：

- `/tmp/zeos-exp001-budget`
- `/tmp/zeos-exp001-budget2`
- `/tmp/zeos-exp001-fs`

**建议删除。** A/B 层证据已经归档，这三个临时目录不再承担唯一证据角色；继续保留反而会增加后续实验误读旧 artifact 的污染风险。

关于 EXP-002 已 terminal 的 15 个 worker：**同意 WorkBuddy 不再 post-hoc shutdown**。报告冻结后再唤醒/关闭会制造新的 transcript 记录，破坏冻结态与 B 层归档的一致性。
