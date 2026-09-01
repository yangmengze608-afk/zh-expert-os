# 中文 AI 专家团操作系统（Zh Expert OS）

> 面向中文用户、能够持续招聘、匿名评测、晋升、降级与淘汰 AI 专家的开源专家组织框架。

**当前版本：v0.2.0 — Eval Arena**

本项目不是“几百个 Prompt 的合集”。核心问题是：**一个 AI 专家组织怎样用可复现证据长期保持最强，而不是越堆越大？**

## 核心设计

- **首席专家官（CAO）**：发现能力缺口、招聘候选、安排试岗并提出人事建议。
- **Eval Arena**：挑战者与现任做同题匿名 A/B 比赛，不靠印象决定谁更强。
- **Arena Director**：负责匿名、任务指纹、展示顺序对冲和战绩写回。
- **Arena Judge**：只看匿名输出，按任务完成、事实性、证据质量、中文原生度和清晰度评分。
- **独立审计官（Auditor）**：监督 CAO 与评测制度，防止评价漂移和自我强化。
- **组织宪法（Constitution）**：CAO 与普通专家都不可自行修改的最高规则。
- **Router + Red Team**：后续运行时负责自动组队与反证。
- **贝叶斯晋升**：单场胜负只是新证据，最终晋升依据长期 Beta-Binomial 后验和质量门槛。

## 1. 组织与评测闭环

```text
                         人类维护者
                             │
                        Constitution
                             │
              ┌──────────────┴──────────────┐
              │                             │
        首席专家官 CAO                  独立审计官
              │                             │
       发现岗位能力缺口                 监督制度漂移
              │
              ↓
       候选 → Shadow 试岗
              │
              ↓
          Eval Arena
   同题 / 同条件 / 匿名 A-B
              │
      多 Judge + 偏差监控
              │
              ↓
      每题胜 / 负 / 平写回
              │
              ↓
       Beta-Binomial 后验
              │
              ↓
        晋升 / 延长试用 / 拒绝
```

## 2. v0.2 新增：真正的 Eval Arena

v0.1 只能手动告诉系统“挑战者 18:2 赢了”。v0.2 开始定义一场可复现比赛本身：

1. 同一个 benchmark task 同时给挑战者和现任；
2. 用 SHA-256 生成 task fingerprint，防止测试途中换题；
3. 双方输出随机映射为 `A / B`；
4. Judge 看不到专家 ID、模型名或来源；
5. 不同 Judge 的展示顺序自动在 `AB / BA` 间对冲；
6. 至少 3 个 Judge 独立评分；
7. 聚合多数票、平均分差、分歧率和位置偏差信号；
8. 严重事实错误 / 伪造来源 / 安全违规通过 `critical_violations` 形成硬门槛；
9. 每一题只写回一次 MatchRecord，`source_battle_id` 保证幂等；
10. 多题结果继续进入 CAO 的长期贝叶斯晋升判断。

详细协议见 [`docs/ARENA.md`](docs/ARENA.md)。

## 3. 快速开始

要求 Python 3.11+，核心包零第三方依赖。

```bash
git clone https://github.com/yangmengze608-afk/zh-expert-os.git
cd zh-expert-os
python -m pip install -e .
zh-expert-os list
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 4. JSONL Benchmark

示例：

```json
{"id":"product-001","prompt":"判断这个产品最需要验证的三个假设。","category":"product","risk_level":"normal"}
```

校验：

```bash
zh-expert-os benchmark-validate examples/arena/product-benchmark.jsonl
```

批量创建挑战赛：

```bash
zh-expert-os arena-seed \
  --file examples/arena/product-benchmark.jsonl \
  --challenger product-pm-v2 \
  --incumbent product-pm-v1
```

也可以单题建场：

```bash
zh-expert-os arena-create \
  --task-file examples/arena/task-product.json \
  --challenger product-pm-v2 \
  --incumbent product-pm-v1
```

## 5. 匿名提交与 Judge Packet

专家分别提交自己的输出：

```bash
zh-expert-os arena-submit --battle battle-xxxx --expert product-pm-v2 --file output-v2.md
zh-expert-os arena-submit --battle battle-xxxx --expert product-pm-v1 --file output-v1.md
```

给 Judge 生成匿名数据包：

```bash
zh-expert-os arena-view --battle battle-xxxx --judge-id judge-1
```

Judge 只会看到任务、匿名输出 A/B、展示顺序与 rubric，不会看到真实专家身份。

提交 Judge 评分后：

```bash
zh-expert-os arena-judge --battle battle-xxxx --file judgment-judge-1.json
zh-expert-os arena-finalize --battle battle-xxxx
```

最终结果自动累计到挑战者对现任的长期战绩。

## 6. 中文原生不是“翻译成中文”

Arena 把 `chinese_native` 单独作为正式评分维度，因为中文专家应该理解真实中文用户、中国平台和中国语境，而不是把英文 Agent Prompt 翻译一遍。

这意味着一个英文 benchmark 上很强、但对中文真实场景不适配的专家，不应该自动成为中文专家组织里的冠军。

## 7. 为什么需要多 Judge 和偏差监控

Judge 自己也是模型，也会犯错。v0.2 不假设 Judge 客观，而是记录它可能偏在哪里：

- `vote_counts`
- `majority_share`
- `mean_gap`
- `disagreement_rate`
- `first_position_preference_rate`
- `position_bias_flag`

我们不把“LLM Judge”包装成真理，而是把它当成一个有噪声的测量仪器。

## 8. 当前种子治理专家

- `cao` — 首席专家官
- `auditor` — 独立审计官
- `router` — 中文任务路由官
- `red-team` — 红队反证专家
- `arena-director` — 竞技场主持官
- `arena-judge` — 匿名评测裁判

领域专家仍应通过招聘和竞技场进入，而不是维护者一次性手写 200 个。

## 9. 当前边界

v0.2 完成的是**公平评测、偏差监控和长期战绩层**。它暂时不绑定 Claude / Codex / ChatGPT API 自动执行专家。

这是刻意的开发顺序：

> 先解决“我们怎么知道谁更强”，再解决“怎么自动把所有人叫来干活”。

后续 Adapter 会把不同运行环境接进同一个 Arena 协议。

## 10. 路线图

- **v0.1 ✅**：治理内核、专家生命周期、贝叶斯晋升、宪法、审计。
- **v0.2 ✅**：JSONL benchmark、匿名 A/B Arena、多 Judge、位置偏差监控、战绩幂等写回。
- **v0.3**：GitHub Recruiter：自动寻找候选、检查 License、分析能力差异并进入 Shadow。
- **v0.4**：中文 Router + 动态专家组队 + Red Team + Evidence Synthesis。
- **v0.5**：Claude / Codex / ChatGPT / Cursor 等跨平台 Adapter。
- **v1.0**：中文原生、自我进化的 AI Expert OS。

详情见 [`docs/ROADMAP.md`](docs/ROADMAP.md)。

## 11. 开源原则

核心代码使用 MIT License。外部专家资产必须逐项记录来源与许可证，不把不兼容许可证的 Prompt / 代码直接复制进核心仓库。

> **借鉴架构，不做许可证洗白。**

## 12. 项目定位

> **面向中文用户的开源 AI 专家团操作系统：系统自己发现缺口、招聘候选、让候选匿名挑战现任，用真实任务和长期证据决定谁留下。**
