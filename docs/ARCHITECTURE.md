# 架构说明

## 控制面与执行面分离

**控制面**：Constitution、CAO、Auditor、Registry、Eval。

**执行面**：Router、领域专家、Red Team、Synthesis。

这样做的原因是：负责“干活”的 Agent 不应该同时拥有修改组织规则和评价标准的权力。

## 专家生命周期

```text
candidate
   ↓
probation
   ↓
active ↔ bench
   ↓
retired
```

- `candidate`：通过基本格式 / 来源 / 许可证检查。
- `probation`：允许 Shadow 运行，不默认承担关键任务。
- `active`：当前岗位主力。
- `bench`：可调用但不默认。
- `retired`：历史保留，不参与默认路由。

治理专家使用 `governance`，不得通过普通 CLI 被自动退休。

## 挑战赛

对同一岗位，挑战者 C 与现任 I 在同一批任务上生成匿名输出。

记录：

- C 胜；
- I 胜；
- 平局；
- 质量维度评分；
- 严重事实错误；
- 成本和延迟。

v0.1 用 Beta 后验估计挑战者赢得单个可比任务的概率。v0.2 会引入更完整的分层 Eval。
