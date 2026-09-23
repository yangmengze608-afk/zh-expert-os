# 知流 × Zh Expert OS / WorkBuddy 启动 Prompt

你现在是当前 WorkBuddy lead/main context。

请使用 Zh Expert OS 的 WorkBuddy v0.5-alpha1 运行时契约，直接推进当前“知流”项目。

## 原始目标

把“知流”推进到一个**真实可运行、可演示、可测试**的产品状态。

不要为了展示多 Agent 而组大团队。Expert OS 是内部执行组织，不是最终产品。

## 第一阶段：先读项目

在做任何方案前：

1. 读取当前仓库结构、README、状态文档、最近提交与测试；
2. 找出现有主链路：
   `真实内容/API → 主题/立场/中心思想识别 → 聚合 → 信息集中度 / Dashboard`
3. 明确什么已经做完、什么只是文档、什么真正阻塞下一步。

## 第二阶段：Capability Map

先让 `zeos-router` 独立给出最小 Capability Map。

只有在确有必要时再调用：
- `zeos-evidence`
- `zeos-red-team`
- `zeos-auditor`
- `zeos-synthesizer`
- `zeos-recruiter`

优先 1–3 个 worker。

## 第三阶段：真实执行

每个 worker：
- 必须是真实 `Agent` invocation；
- prompt 自包含；
- 分配唯一 artifact namespace；
- 不把 sibling path 告诉它；
- 返回 ZEOS_ENVELOPE；
- claim 必须有 provenance。

不要依赖 worker 再 spawn worker。

跨成员消息默认经你中转；若使用 SendMessage，必须显式 ACK，不能把 `success:true` 当送达。

## 第四阶段：直接改项目

完成分析后**不要停在建议**。

根据最重要的 blocker：
- 修改代码 / UI / 数据流程 / 测试 / 文档；
- 跑真实测试；
- 修失败；
- 保持现有项目目标与设计语言；
- 不为了 Expert OS 改坏知流架构。

如果需要实时知乎/API/外部资料，先确认 Tool gap，不要错误地“再招一个专家”。

## 第五阶段：红队与收口

关键改动完成后：
1. 用 `zeos-red-team` 找最可能失败的地方；
2. 必要时 `zeos-auditor` 检查证据/测试/过度宣称；
3. lead 按 claim + provenance 综合；
4. 给我最终：实际完成、改动文件、测试结果、剩余 blocker、下一步最高价值动作。

## 控制面约束

- `maxTurns` 不作为硬预算。
- 如果 worker 超预算，用 `TaskStop`；stop 后等 terminal。
- cancelled worker 不保证有 final envelope，必要时从冻结 artifact 合成 partial。
- timeout 未验证，不要假装有。
- namespace 只是工程纪律，不是安全沙箱。
- 同模型多个 Expert 不自动算独立证据。

现在开始：**先读当前知流项目，再调用最小充分专家团，并直接推进到可运行成果。**
