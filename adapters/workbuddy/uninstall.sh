#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ADAPTER_DIR="$ROOT/adapters/workbuddy"
SOURCE_DIR="$ADAPTER_DIR/agents"
TARGET_DIR="${WORKBUDDY_AGENTS_DIR:-$HOME/.workbuddy/agents}"
SKILLS_HOME="${WORKBUDDY_SKILLS_DIR:-$HOME/.workbuddy/skills}"
SKILL_TARGET="$SKILLS_HOME/zh-expert-os"

removed=0
for source in "$SOURCE_DIR"/*.md; do
  [[ -e "$source" ]] || continue
  target="$TARGET_DIR/$(basename "$source")"
  if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
    rm "$target"
    echo "已移除 native agent：$target"
    removed=$((removed + 1))
  fi
done

if [[ -L "$SKILL_TARGET" && "$(readlink "$SKILL_TARGET")" == "$ADAPTER_DIR" ]]; then
  rm "$SKILL_TARGET"
  echo "已移除 WorkBuddy Skill：$SKILL_TARGET"
fi

if [[ -d "$TARGET_DIR" && -z "$(ls -A "$TARGET_DIR")" ]]; then
  rmdir "$TARGET_DIR"
  echo "agents 目录已空并删除：$TARGET_DIR"
fi

if [[ -d "$SKILLS_HOME" && -z "$(ls -A "$SKILLS_HOME")" ]]; then
  rmdir "$SKILLS_HOME"
  echo "skills 目录已空并删除：$SKILLS_HOME"
fi

echo "完成。native_agents_removed=$removed"
