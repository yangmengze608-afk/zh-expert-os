#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL_SOURCE="$ROOT/.claude/skills/zh-expert-os"
SKILLS_HOME="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
SKILL_TARGET="$SKILLS_HOME/zh-expert-os"

if [[ ! -f "$SKILL_SOURCE/SKILL.md" ]]; then
  echo "未找到 Skill: $SKILL_SOURCE/SKILL.md" >&2
  exit 1
fi

mkdir -p "$SKILLS_HOME"

if [[ -L "$SKILL_TARGET" ]]; then
  CURRENT="$(readlink "$SKILL_TARGET")"
  if [[ "$CURRENT" == "$SKILL_SOURCE" ]]; then
    echo "Claude Skill 已连接：$SKILL_TARGET -> $SKILL_SOURCE"
  else
    echo "目标已存在且指向其他位置：$SKILL_TARGET -> $CURRENT" >&2
    echo "请先手动确认后再替换，避免覆盖其他 Skill。" >&2
    exit 2
  fi
elif [[ -e "$SKILL_TARGET" ]]; then
  echo "目标已存在：$SKILL_TARGET" >&2
  echo "安装器不会自动覆盖。请先备份或删除后重试。" >&2
  exit 2
else
  ln -s "$SKILL_SOURCE" "$SKILL_TARGET"
  echo "已安装 Claude Skill：$SKILL_TARGET -> $SKILL_SOURCE"
fi

echo
if command -v zh-expert-os >/dev/null 2>&1; then
  echo "zh-expert-os CLI 已可用：$(command -v zh-expert-os)"
else
  echo "尚未发现 zh-expert-os CLI。建议执行："
  echo "  python -m pip install -e \"$ROOT\" --no-build-isolation"
fi

echo
echo "完成后可在任意 Claude Code 项目中调用 /zh-expert-os，"
echo "或直接描述复杂任务，让 Claude 根据 Skill description 自动判断是否使用。"
