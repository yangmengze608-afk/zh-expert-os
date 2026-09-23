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

**Status: accepted after EXP-001**

不得依赖 agent frontmatter `maxTurns` 作为硬预算。

v0.5 的预算控制必须由 orchestrator 控制，并区分：
- wall-clock deadline
- tool-call budget
- host task status
- expert envelope status
- explicit stop semantics

TaskStop / timeout 的真实能力由 EXP-002 继续验证。

## D-005 — WorkBuddy Topology Default

**Status: provisional pending EXP-002**

v0.5 暂采用 `lead → workers` 一层 fan-out。

这是**保守默认**，不是宿主硬限制。EXP-001 对 member→member `Agent` spawning 的证据冲突，因此保持 UNKNOWN。

## D-006 — Evidence Independence on Shared Filesystem

**Status: accepted after EXP-001**

WorkBuddy child 的聊天上下文可以表现隔离，但文件系统共享。

因此：
- 独立证据任务必须使用独立 artifact namespace；
- lead 不应在任务完成前把 sibling artifact 路径互相暴露；
- namespace 是工程纪律，不是安全沙箱；
- claim/evidence synthesis 必须保留 provenance。
