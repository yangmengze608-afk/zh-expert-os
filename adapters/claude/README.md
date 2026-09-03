# Claude Code Adapter

Zh Expert OS 本身不是一个单一 Skill；它是 Expert / Recruiter / Runtime / Arena 的上层系统。

Claude Code 里的 `.claude/skills/zh-expert-os/SKILL.md` 只是**入口适配器**：让 Claude 知道什么时候应调用 Expert OS、怎样区分 Skill / Expert / Team / Tool，以及怎样把复杂任务交给现有 CLI 和独立 Expert Runtime。

## 1. 在 Zh Expert OS 仓库内直接使用

仓库已经包含：

```text
.claude/skills/zh-expert-os/SKILL.md
```

在本仓库打开 Claude Code 后，可直接尝试：

```text
/zh-expert-os 帮我分析当前项目下一步最值得做什么，并直接执行。
```

也可以不写 `/zh-expert-os`，直接描述一个明显复杂、跨专业的任务，让 Claude 根据 Skill 的 `description` 判断是否加载。

## 2. 在其他项目中使用（推荐）

如果你希望在“知流”或其他独立仓库中调用 Zh Expert OS，建议把它安装成用户级 Skill。

先 clone 并安装本项目：

```bash
git clone https://github.com/yangmengze608-afk/zh-expert-os.git
cd zh-expert-os
python -m pip install -e . --no-build-isolation
```

然后运行：

```bash
bash adapters/claude/install.sh
```

安装器会把：

```text
<zh-expert-os>/.claude/skills/zh-expert-os
```

链接到：

```text
~/.claude/skills/zh-expert-os
```

它不会自动覆盖已有同名 Skill。

之后进入任意项目，例如：

```bash
cd /path/to/zhiliu
claude
```

即可使用：

```text
/zh-expert-os <你的任务>
```

## 3. 调用语义

Claude 看到这个 Skill 后应按下面的运行时语义理解项目：

```text
Skill  = 当前 Agent 加载方法 / SOP
Expert = 尽量使用独立 subagent / agent context
Team   = 多个 Expert invocation + orchestration
Tool   = API / CLI / Connector / function
Plugin = 上述能力的安装与分发容器
```

因此 `/zh-expert-os` 不是让 Claude“假装成很多人”，而是告诉主 Agent：

```text
先理解真实任务
→ 诊断能力缺口
→ 组最小充分专家团
→ 必要时招聘 Shadow
→ 尽可能独立调用 Expert
→ Red Team / Arena
→ 回到原始任务交付
```

如果宿主环境暂时没有真正的 subagent 能力，Claude 可以退化为单上下文执行，但必须明确这种结果不等于多 Agent 独立证据。

## 4. CLI 可用性

用户级 Skill 只负责让 Claude发现和理解 Zh Expert OS。真正调用 Registry / Recruiter / Runtime / Arena 时，建议确保：

```bash
zh-expert-os list
```

可以正常运行。

常用命令包括：

```bash
zh-expert-os recruit-pipeline ...
zh-expert-os runtime-trial ...
zh-expert-os arena-view ...
zh-expert-os arena-finalize ...
```

## 5. 用于其他项目时的原则

Zh Expert OS 不应篡改目标项目的目标。

在“知流”这类项目里，Expert OS 是**总调度层**，真正目标仍是：

- 读取并理解现有项目；
- 找出当前最大缺口；
- 组织最合适的专家完成它；
- 实际修改代码 / 产品 / 文档；
- 测试和验证最终交付。

不要把时间浪费在为了展示 Agent 系统而招聘无关专家。

## 6. 示例

见：

[`examples/claude/zhiliu-project-prompt.md`](../../examples/claude/zhiliu-project-prompt.md)

该 Prompt 可以直接用于 Claude Code 中已经打开的“知流”项目。
