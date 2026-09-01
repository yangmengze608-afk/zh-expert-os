# Eval Arena v0.2

v0.2 把 v0.1 的“手动录入 18:2”推进成真正的匿名评测协议。

## 一场 Battle 的生命周期

```text
benchmark task
  ↓
Arena Director 创建 battle + task fingerprint
  ↓
挑战者 / 现任在同条件下分别提交
  ↓
系统随机映射为 A / B
  ↓
不同 Judge 收到匿名 packet，展示顺序自动 AB / BA 对冲
  ↓
Judge 对 A / B 独立打分
  ↓
多 Judge 聚合：多数票 + 平均分差 + 硬错误门槛
  ↓
该题产生 challenger_win / incumbent_win / tie
  ↓
以 source_battle_id 幂等写入长期 MatchRecord
  ↓
累计到 Beta-Binomial 后验，供 CAO 人事决策
```

## 为什么不是“一位 Judge 说了算”

LLM Judge 也会有偏差，尤其包括位置偏差、长度偏好、措辞偏好和同模型偏好。因此默认至少 3 个 Judge，并记录：

- A / B / TIE 票数；
- 多数票比例；
- 平均质量分差；
- Judge 分歧率；
- 首位答案被偏好的比例；
- 位置偏差 flag。

v0.2 不假装已经彻底解决 Judge bias，而是先把偏差暴露成可观察数据。

## 硬错误优先

如果一个答案平均风格分很高，但出现严重事实错误、伪造来源、安全违规等 `critical_violations`，它会优先输给没有严重硬伤的答案。

这是为了避免“更会说话的错误答案”在竞技场里持续晋升。

## JSONL Benchmark

每行一题：

```json
{"id":"product-001","prompt":"判断这个产品是否值得做，并给出最小验证方案。","category":"product","risk_level":"normal"}
```

校验：

```bash
zh-expert-os benchmark-validate examples/arena/product-benchmark.jsonl
```

批量建场：

```bash
zh-expert-os arena-seed \
  --file examples/arena/product-benchmark.jsonl \
  --challenger product-pm-v2 \
  --incumbent product-pm-v1
```

## Judge Packet

```bash
zh-expert-os arena-view --battle battle-xxxx --judge-id judge-1
```

返回的数据只包含：任务、任务指纹、匿名 A/B 输出、展示顺序、评分 rubric。不会包含真实专家 ID。

## 当前边界

v0.2 是**评测与战绩层**，还没有绑定某一家模型 API。也就是说，它已经定义好“怎么公平比赛、怎么记分、怎么进入长期后验”，但真正自动调用 Claude / Codex / ChatGPT 等执行专家的适配器在后续版本完成。

这个边界是刻意的：先把评测制度做稳定，再自动化调用，避免先做出一个会自动跑、却不知道谁真的更强的系统。
