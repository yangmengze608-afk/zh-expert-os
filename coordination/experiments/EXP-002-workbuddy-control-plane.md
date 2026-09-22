# EXP-002 — WorkBuddy Control Plane Reality Check

## Purpose

EXP-001 已验证“真实 Expert 能跑起来”。EXP-002 只验证**控制面是否可靠**：

- nested spawn
- message delivery + ACK
- active stop
- timeout
- definition hot-load repeatability
- artifact namespace discipline

本实验不扩大正式专家团，不做业务能力评测。

---

## Evidence Levels

沿用：

- **VERIFIED**：可复现步骤 + 原始证据，至少两次一致；若实验明确要求 3 次，则按该门槛。
- **OBSERVED**：真实宿主中观察到一次，但未达到重复门槛。
- **INFERRED**：由现象推断，没有直接宿主证据。
- **UNKNOWN**：未测试、无法测试或证据冲突。

对“不支持”这类全称结论尤其谨慎：一次失败只能说明该次失败，除非重复控制条件一致且没有反例。

---

# H1 — Member → Member Spawn

## 问题

一个已经作为 child 运行的 member，能否真实调用 `Agent` 再产生 child-of-child？

EXP-001 证据冲突，因此本轮不看工具清单自述，只看**实际 task graph**。

## 方法

执行 **3 个独立 run**：`nested-1 / nested-2 / nested-3`。

每次：

1. lead spawn 一个独立 parent member，使用唯一 name。
2. parent 收到自包含任务，要求它：
   - 若真实拥有 `Agent` 能力，则 spawn 一个 grandchild；
   - grandchild prompt 只包含该 run 的唯一 synthetic canary；
   - parent 必须回传实际 child-of-child `task_id`（若宿主返回）、调用结果和原始错误。
3. lead 不得代替 parent spawn grandchild。
4. 只有同时满足以下证据才计为 **spawn success**：
   - parent transcript 中存在真实 `Agent` function_call；
   - 宿主返回新的 child-of-child task/invocation 标识；
   - grandchild 有独立最终输出或 transcript；
   - grandchild 正确看到自己的 canary。
5. “工具列表写有 Agent”“模型说我成功了”都不计。

## 记录

每个 run 分别记录：

- parent task_id
- parent subagent_type / model
- Agent function_call 是否真实出现
- grandchild task_id
- grandchild transcript 是否存在
- canary 是否正确
- terminal status
- 原始 error

## 判定

- 3/3 success → **VERIFIED 可用**
- 1–2 success → **OBSERVED / 不稳定**
- 0/3，且三次同条件、同类宿主错误 → **OBSERVED 不可用（仅限当前版本/配置）**
- 结果冲突且无法解释 → **UNKNOWN**

---

# H2 — SendMessage Delivery + ACK

## 问题

`SendMessage` 返回 `success:true` 时，接收方是否真的消费消息？

## 方法

执行至少 **3 个 run**。

每次：

1. lead 先 spawn listener，listener 必须保持 alive，不得立即结束。
2. listener 准备等待唯一 token，例如运行短时、无害等待循环；具体实现按宿主能力，但必须记录。
3. lead 确认 listener 仍为 running 后，再 spawn/指令 talker。
4. talker 使用**实际 spawn 返回的 listener name** 调 `SendMessage`，发送唯一 token。
5. listener 只有在真实看到 token 后，才：
   - 在自己的最终输出中逐字回显 token；
   - 向 lead 发送 `ACK:<token>`。
6. lead 必须核验：
   - sender tool result；
   - listener transcript 是否真实出现 token；
   - listener ACK 是否到达 lead。

## 判定

把三层分开：

- ROUTE_ACCEPTED：sender `success:true`
- CONSUMED：listener transcript 出现 token
- ACKED：lead 收到 listener 的 ACK

不得合并成一个“成功”。

---

# H3 — TaskStop / Forced Stop

## 问题

lead 是否能可靠停止一个正在运行的 child？停止后状态如何表现？

## 方法

执行 **2 个 run**。

worker 做无害长任务：

- 在 `/tmp/zeos-exp002-stop/<run>/` 下串行创建编号文件；
- 每步之间 sleep 1 秒；
- 总步数足够长，确保 lead 有时间 stop；
- 不修改仓库文件。

lead：

1. spawn worker；
2. 确认 host status = running；
3. 等至少 5 个文件出现；
4. 调用 `TaskStop(task_id)`；
5. 等到宿主给出 terminal/stop 结果；
6. stop 后再等待至少 5 秒；
7. 重新统计文件数，确认是否继续增长；
8. 记录 child 是否产生最终 envelope。

## 必须分别记录

- TaskStop tool result
- stop 前文件数
- stop 后立即文件数
- +5s 后文件数
- host task status
- child 最终正文 / envelope 是否存在
- transcript 最后一条记录
- 是否仍有后续 function_call

## 判定

“TaskStop 调用成功”与“worker 实际停止”是两件事，必须分别给等级。

---

# H4 — Timeout Semantics

## 问题

WorkBuddy 是否有**真实、可配置、可与 failed/stop 区分**的 timeout？

## 方法

1. 先检查当前可用 invocation / task API 是否暴露 timeout 或 deadline 控制。
2. 若不存在明确的 timeout 配置接口：
   - **不要用 TaskStop 模拟 timeout**；
   - 直接记 `UNKNOWN / NOT EXPOSED IN TESTED INTERFACE`。
3. 若存在：
   - 用无害长任务设置短 timeout；
   - 等真实 terminal 状态；
   - 记录 host status / error type / child envelope / artifacts；
   - 至少重复 2 次。

## 禁止

- 不得把本地 shell `timeout` 命令当作 WorkBuddy agent timeout。
- 不得把人为 TaskStop 当作 timeout。

---

# H5 — User-level Definition Body Hot-load Repeatability

## 问题

EXP-001 的“agent 定义正文被加载”是否可重复？

## 方法

创建两个**完全不同**的一次性用户级 agent：

- `zeos-exp002-fingerprint-a`
- `zeos-exp002-fingerprint-b`

每个定义正文含一个运行时随机生成的 signature，signature：

- 不放进 dispatch prompt；
- 不写进公开 experiment 文档；
- child 不允许读文件或执行搜索；
- parent 只要求：“返回你定义中配置的 signature 与固定格式”。

要求：

1. A、B 各真实 invocation 一次；
2. child 输出正确 signature；
3. transcript 中无 Read / Grep / Bash 等旁路取值；
4. 两个 agent 使用不同 signature。

成功两次一致 → 可把“definition body hot-load”从 OBSERVED 提升为 **VERIFIED**。

---

# H6 — Artifact Namespace Discipline

## 问题

共享文件系统无法变成真正安全隔离，但我们能否建立一个**可审计的工程纪律**，避免独立证据任务无意互读？

## 方法

并发两个 worker：

- A 只允许 `/tmp/zeos-exp002-artifacts/A/`
- B 只允许 `/tmp/zeos-exp002-artifacts/B/`

每个 worker：

1. 只收到自己的 namespace；
2. 写入自己的 synthetic evidence artifact；
3. 不被告知 sibling 路径；
4. 最终 envelope 只列自己 artifact 的相对路径/哈希。

lead：

- 不把 A 的路径传给 B，反之亦然；
- 任务结束后检查 transcript 是否出现 sibling namespace；
- 最后统一读两个 namespace 做 synthesis。

## 结论边界

即使通过，也只能说：

> “namespace discipline 在本实验中避免了交叉读取。”

**不能**说：

> “文件系统已安全隔离。”

---

# Methodology Guardrails

本轮强制执行：

1. **Terminal-state gate**：任何“停止/失败/截断”结论必须等 terminal event。
2. **Raw-output anchor**：每个结论必须能指回原始 tool result / transcript / artifact。
3. **No self-report-only success**：nested spawn、message delivery、stop 都不得只信 agent 自述。
4. **Contradiction first**：发现反例先撤回旧结论，不做“倾向性”硬解释。
5. **Unique names**：每个 run 使用唯一 name，避免 auto-team 重名改写混淆 task identity。
6. **Public evidence hygiene**：公开证据脱敏；完整 transcript 默认 B 层。
7. **Cleanup after terminal only**：所有 child 真正 terminal 后再清理 agent / tmp 资源。

---

# Pass Criteria for v0.5 Control Plane

进入正式 v0.5 Adapter 实现，不要求所有 H 都为 YES，但必须满足：

- H1 有明确等级，不再是“自述冲突”；若仍 UNKNOWN，v0.5 继续扁平默认。
- H2 至少搞清 route accepted / consumed / acked 三层语义。
- H3 明确 TaskStop 是否能实际终止 worker。
- H4 若宿主不暴露 timeout，明确保持 UNKNOWN，不伪造。
- H5 definition body hot-load 达到 VERIFIED，或明确保留 OBSERVED。
- H6 形成 artifact namespace 规范，并明确它不是安全沙箱。
- 所有新结论通过 ChatGPT 独立审计。

---

# Cleanup

实验完成后：

- 删除所有 `~/.workbuddy/agents/zeos-exp002-*`
- 若目录原本不存在且已为空，恢复到不存在
- 删除 `/tmp/zeos-exp002-*` 测试产物，除非为了审计显式保留
- 保留 A 层脱敏证据
- B 层完整 transcript 继续本地保存
- 报告所有环境变更与清理结果
