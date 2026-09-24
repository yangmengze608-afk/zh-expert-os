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

removed=0
skipped=0

for source in "$SOURCE_DIR"/*.md; do
  [[ -f "$source" ]] || continue
  target="$TARGET_DIR/$(basename "$source")"
  if [[ ! -e "$target" && ! -L "$target" ]]; then
    continue
  fi
  if [[ -f "$target" ]] && cmp -s "$source" "$target"; then
    rm "$target"
    echo "已移除 native agent：$target"
    removed=$((removed + 1))
  else
    echo "保留已修改或非普通文件：$target" >&2
    skipped=$((skipped + 1))
  fi
done

if [[ -f "$SKILL_TARGET" ]] && cmp -s "$SKILL_SOURCE" "$SKILL_TARGET"; then
  rm "$SKILL_TARGET"
  echo "已移除 WorkBuddy Skill：$SKILL_TARGET"
elif [[ -e "$SKILL_TARGET" || -L "$SKILL_TARGET" ]]; then
  echo "保留已修改或非普通 Skill：$SKILL_TARGET" >&2
  skipped=$((skipped + 1))
fi

if [[ -d "$SKILL_TARGET_DIR" && -z "$(ls -A "$SKILL_TARGET_DIR")" ]]; then
  rmdir "$SKILL_TARGET_DIR"
fi
if [[ -d "$TARGET_DIR" && -z "$(ls -A "$TARGET_DIR")" ]]; then
  rmdir "$TARGET_DIR"
fi
if [[ -d "$SKILLS_HOME" && -z "$(ls -A "$SKILLS_HOME")" ]]; then
  rmdir "$SKILLS_HOME"
fi

echo "完成。removed=$removed skipped_modified=$skipped"
