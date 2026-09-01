# 专家资产规范（Expert Spec）v0.1

每个专家文件应包含以下字段：

1. `id`：稳定、唯一、机器可读。
2. `name_zh`：中文名称。
3. `version`：语义化版本。
4. `status`：`candidate | probation | active | bench | retired | governance`。
5. `mission`：一句话使命。
6. `use_when`：适用场景。
7. `do_not_use_when`：不适用场景。
8. `inputs`：必须输入与可选输入。
9. `workflow`：工作步骤。
10. `evidence_policy`：事实、来源与验证要求。
11. `tools`：允许工具与限制。
12. `output_contract`：输出结构。
13. `self_check`：提交前检查。
14. `collaboration`：上下游专家与冲突处理方式。
15. `eval_dimensions`：该岗位特别重视的指标。
16. `provenance`：原创 / 改写 / 外部来源 + 许可证。

## 最低质量标准

一个专家不能只写：

> “你是一名世界顶级产品经理，请认真分析。”

至少必须定义**什么时候不该用它、它要验证什么、它怎样失败、输出怎么验收**。
