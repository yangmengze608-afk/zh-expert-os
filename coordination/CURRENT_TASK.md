# CURRENT TASK

## 目标

进入 **v0.5 WorkBuddy Native Expert Runtime** 的控制面验证阶段。

EXP-001 已确认：WorkBuddy 能承载真实 Expert invocation，用户级 `~/.workbuddy/agents/*.md` 可在当前会话热注册；同时确认共享文件系统会形成污染通道，frontmatter `maxTurns` 不能当硬预算。

现在不再重复 EXP-001。当前只解决仍会阻塞 v0.5 Runtime 的控制面 UNKNOWN。

## 当前里程碑

**EXP-002：WorkBuddy Control Plane — Spawn / Delivery / Stop / Timeout**

需要回答：

1. member → member `Agent` spawning 到底能否稳定成立？
2. `SendMessage success:true` 与“接收方实际消费”之间是什么关系？
3. lead 能否用 `TaskStop` 可靠停止一个正在运行的 child？
4. 强制停止后，host task status、expert envelope、artifact 三者分别是什么状态？
5. WorkBuddy 是否存在可实际配置并区分的 timeout 语义？
6. 用户级 agent 定义正文的热加载是否可在第二组、不同定义上重复？
7. 在共享文件系统前提下，独立 artifact namespace 能否作为工程纪律减少交叉污染？

## 当前默认架构

在 EXP-002 得出结论前：

- v0.5 暂用 `lead → workers` 一层 fan-out；
- 这只是**保守默认**，不是宿主硬限制；
- 跨成员通信默认经 lead；
- `maxTurns` 不参与成本硬控制；
- 每个节点同时记录 host task status + expert envelope status；
- “独立证据”任务必须使用独立 artifact namespace。

## 完成条件

WorkBuddy 完成 `coordination/experiments/EXP-002-workbuddy-control-plane.md`，回填
`coordination/experiments/EXP-002-WORKBUDDY_REPORT.md`。

随后由 ChatGPT 独立填写
`coordination/experiments/EXP-002-CHATGPT_REVIEW.md`。

只有审计通过后，才开始把这些宿主事实编码进正式 v0.5 WorkBuddy Adapter。
