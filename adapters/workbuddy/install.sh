#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ADAPTER_DIR="$ROOT/adapters/workbuddy"
SOURCE_DIR="$ADAPTER_DIR/agents"
TARGET_DIR="${WORKBUDDY_AGENTS_DIR:-$HOME/.workbuddy/agents}"
SKILLS_HOME="${WORKBUDDY_SKILLS_DIR:-$HOME/.workbuddy/skills}"
SKILL_TARGET="$SKILLS_HOME/zh-expert-os"

if [[ ! -f "$ADAPTER_DIR/SKILL.md" || ! -d "$SOURCE_DIR" ]]; then
  echo "WorkBuddy Adapter 不完整：$ADAPTER_DIR" >&2
  exit 1
fi

mkdir -p "$SKILLS_HOME"

if [[ -L "$SKILL_TARGET" ]]; then
  current="$(readlink "$SKILL_TARGET")"
  if [[ "$current" == "$ADAPTER_DIR" ]]; then
    echo "WorkBuddy Skill 已连接：$SKILL_TARGET -> $ADAPTER_DIR"
  else
    echo "Skill 目标已存在且指向其他位置：$SKILL_TARGET -> $current" >&2
    echo "为避免覆盖其他 Skill，安装终止。" >&2
    exit 2
  fi
elif [[ -e "$SKILL_TARGET" ]]; then
  echo "Skill 目标已存在：$SKILL_TARGET" >&2
  echo "安装器不会自动覆盖。请先备份或删除后重试。" >&2
  exit 2
else
  ln -s "$ADAPTER_DIR" "$SKILL_TARGET"
  echo "已安装 WorkBuddy Skill：$SKILL_TARGET -> $ADAPTER_DIR"
fi

mkdir -p "$TARGET_DIR"

installed=0
existing=0

for source in "$SOURCE_DIR"/*.md; do
  [[ -e "$source" ]] || continue
  name="$(basename "$source")"
  target="$TARGET_DIR/$name"

  if [[ -L "$target" ]]; then
    current="$(readlink "$target")"
    if [[ "$current" == "$source" ]]; then
      echo "已连接 native agent：$target -> $source"
      existing=$((existing + 1))
      continue
    fi
    echo "目标 symlink 已指向其他位置，跳过：$target -> $current" >&2
    existing=$((existing + 1))
    continue
  fi

  if [[ -e "$target" ]]; then
    echo "目标已存在，安装器不会覆盖：$target" >&2
    existing=$((existing + 1))
    continue
  fi

  ln -s "$source" "$target"
  echo "已安装 native agent：$target -> $source"
  installed=$((installed + 1))
done

echo
echo "WorkBuddy Adapter 安装完成。native_agents_new=$installed existing/skipped=$existing"
echo "Skill：$SKILL_TARGET"
echo "Agents：$TARGET_DIR"
echo
echo "v0.5-alpha1：由当前 lead/main context 加载 zh-expert-os Skill，再 fan-out 到真实 native workers。"
echo "不要把普通 child 当成可可靠递归 spawn 的 team lead。"
echo
if command -v zh-expert-os >/dev/null 2>&1; then
  echo "zh-expert-os CLI：$(command -v zh-expert-os)"
else
  echo "尚未发现 zh-expert-os CLI。建议执行："
  echo "  python -m pip install -e \"$ROOT\" --no-build-isolation"
fi
