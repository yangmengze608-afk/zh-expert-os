# CURRENT TASK

## 目标

把 Zh Expert OS 从“可模拟专家团的方法论/Runtime”推进为 **WorkBuddy Native Expert Runtime**，优先验证真实独立 Expert 是否可被宿主稳定注册、调用、隔离和编排。

## 当前里程碑

**EXP-001：WorkBuddy Native Expert Reality Check**

在修改 Zh Expert OS 的正式 WorkBuddy Adapter 前，回答四个事实问题：

1. 插件包内 `agents/*.md` 是否会注册成可真实调用的独立 subagent？
2. 用户目录 `~/.workbuddy/agents/*.md` 是否支持同等注册？
3. 新建 agent 后，当前会话能否热发现，还是必须 reload / 新会话？
4. 不同 subagent 的会话上下文是否隔离，失败/partial 是否可被编排者诚实回收？

## 成功标准

只有出现可审计的真实 invocation 证据，才称“真实 Expert”。同一主上下文里的角色扮演不算。

实验完成后，由 ChatGPT 在 `CHATGPT_REVIEW.md` 给出 VERIFIED / OBSERVED / INFERRED / UNKNOWN 结论，再决定 v0.5 WorkBuddy Adapter 的正式架构。