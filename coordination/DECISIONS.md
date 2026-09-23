# Cross-host Decisions

## D-001 — Real Expert Definition

**Status: accepted**

Zh Expert OS 中“真实 Expert”最低要求是：一次可识别的独立 agent invocation。若要把多个 Expert 的结论作为独立证据，还需要进一步证明上下文/证据路径的独立性。

`Skill` 不因具有人格化 Prompt 就自动升级为 Expert。

## D-002 — Platform Adapter Boundary

**Status: accepted**

- WorkBuddy：优先 Native Expert / Expert Team。
- Claude Code：Skill 是入口，subagent / Runtime 才是 Expert 执行层。
- Codex 等其他宿主：按宿主原语适配，不伪装成统一原生能力。

## D-003 — Recruitment Persistence

**Status: accepted after EXP-001**

WorkBuddy 5.5.6 实测支持：在当前会话中创建用户级 `~/.workbuddy/agents/*.md` 后直接以对应 `subagent_type` 调用。

因此 WorkBuddy Adapter 可以把通过治理门槛的候选持久化为 native Expert。

边界：
- 这不等于候选可绕过 Shadow / Arena / Human gate 直接晋升 Active；
- agent 定义正文的行为级加载已观察到，但并非所有 frontmatter 字段都可靠生效。

## D-004 — WorkBuddy Budget Control

**Status: accepted after EXP-002**

不得依赖 agent frontmatter `maxTurns` 作为硬预算。

v0.5 的预算控制必须由 orchestrator 控制，并区分：
- wall-clock deadline
- tool-call budget
- host task status
- expert envelope status
- explicit stop semantics

`TaskStop` 已由 EXP-002 以 2/2 四层证据验证能真正终止 worker，因此可作为 orchestrator 主动成本/生命周期闸门。

边界：
- stop 不是瞬时；
- stop 后必须等 host terminal；
- 被 stop 的 child 不保证产出 final envelope；
- tested interface 未暴露 agent timeout/deadline，timeout 继续保持 UNKNOWN。

## D-005 — WorkBuddy Topology Default

**Status: accepted as conservative default after EXP-002**

v0.5 暂采用 `lead → workers` 一层 fan-out。

这是**保守默认**，不是宿主硬限制。EXP-002 在 tested `general-purpose` member 中 3/3 未观测到真实 `Agent` function_call 或孙代 task/transcript，因此 v0.5-alpha1 不依赖 nested spawn。

## D-006 — Evidence Independence on Shared Filesystem

**Status: accepted after EXP-001**

WorkBuddy child 的聊天上下文可以表现隔离，但文件系统共享。

因此：
- 独立证据任务必须使用独立 artifact namespace；
- lead 不应在任务完成前把 sibling artifact 路径互相暴露；
- namespace 是工程纪律，不是安全沙箱；
- claim/evidence synthesis 必须保留 provenance。


## D-007 — WorkBuddy Message Delivery Contract

**Status: accepted after EXP-002**

跨成员消息必须区分：

`ROUTE_ACCEPTED → CONSUMED → ACKED`

`SendMessage success:true` 只表示路由层接受，不能用来证明接收方已经消费。

v0.5-alpha1 默认跨成员信息经 lead 中转；若必须 member-to-member SendMessage，只有显式 ACK 才算 confirmed。

## D-008 — Machine Evidence Provenance

**Status: accepted after EXP-002**

任何进入 evidence registry 的具体值、字符串、数字、哈希或结论，都必须携带 machine-checkable provenance pointer：

- source task_id
- source kind
- locator（tool result / transcript record / artifact）
- artifact sha256（如适用）
- derived evidence 的 parent refs

证据优先级：

`raw tool result / artifact > transcript record > machine-derived transform + provenance > human/model transcription`

最后一层默认不能独立作证。

禁止把模型自己手打、猜测或记忆中的“观测值”回显到命令/文件后，再用搜索结果把它包装成旁证。

## D-009 — WorkBuddy Native Expert Persistence

**Status: accepted for v0.5-alpha1**

Registry 中已进入 Shadow / probation / active / governance 生命周期的 Expert 可以被渲染为 WorkBuddy user-level native agent 文件。

“热注册成功”只表示宿主可以调用，不改变 Registry 身份，不绕过 Arena / Auditor / Human approval。
