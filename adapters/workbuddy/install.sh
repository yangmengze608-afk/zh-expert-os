#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ADAPTER_DIR="$ROOT/adapters/workbuddy"
SOURCE_DIR="$ADAPTER_DIR/agents"
SKILL_SOURCE="$ADAPTER_DIR/SKILL.md"

TARGET_DIR="${WORKBUDDY_AGENTS_DIR:-$HOME/.workbuddy/agents}"
SKILLS_HOME="${WORKBUDDY_SKILLS_DIR:-$HOME/.workbuddy/skills}"
SKILL_TARGET_DIR="$SKILLS_HOME/zh-expert-os"
SKILL_TARGET="$SKILL_TARGET_DIR/SKILL.md"

if [[ ! -f "$SKILL_SOURCE" || ! -d "$SOURCE_DIR" ]]; then
  echo "WorkBuddy Adapter 不完整：$ADAPTER_DIR" >&2
  exit 1
fi

# Preflight first: never leave a half-installed adapter because of a late conflict.
conflicts=0

if [[ -e "$SKILL_TARGET" ]] && ! cmp -s "$SKILL_SOURCE" "$SKILL_TARGET"; then
  echo "Skill 已存在且内容不同：$SKILL_TARGET" >&2
  conflicts=$((conflicts + 1))
fi

for source in "$SOURCE_DIR"/*.md; do
  [[ -f "$source" ]] || continue
  target="$TARGET_DIR/$(basename "$source")"
  if [[ -e "$target" || -L "$target" ]]; then
    if [[ -f "$target" ]] && cmp -s "$source" "$target"; then
      continue
    fi
    echo "native agent 已存在且内容不同：$target" >&2
    conflicts=$((conflicts + 1))
  fi
done

if (( conflicts > 0 )); then
  echo "发现 $conflicts 个冲突。安装器不会覆盖用户已有内容；请先人工处理。" >&2
  exit 2
fi

mkdir -p "$SKILL_TARGET_DIR" "$TARGET_DIR"
cp "$SKILL_SOURCE" "$SKILL_TARGET"

installed=0
for source in "$SOURCE_DIR"/*.md; do
  [[ -f "$source" ]] || continue
  target="$TARGET_DIR/$(basename "$source")"
  if [[ -f "$target" ]] && cmp -s "$source" "$target"; then
    echo "已是最新：$target"
    continue
  fi
  cp "$source" "$target"
  echo "已安装 native agent：$target"
  installed=$((installed + 1))
done

echo "已安装 WorkBuddy Skill：$SKILL_TARGET"
echo
echo "WorkBuddy Adapter 安装完成。native_agents_written=$installed"
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
