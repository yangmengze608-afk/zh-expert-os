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

**Status: provisional**

新招聘候选优先先以 ephemeral independent expert 试岗。是否能在 WorkBuddy 当前会话中自动生成并热注册 persistent native agent，等待 EXP-001 验证。