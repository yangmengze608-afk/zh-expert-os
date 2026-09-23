#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="$ROOT/adapters/workbuddy/agents"
TARGET_DIR="${WORKBUDDY_AGENTS_DIR:-$HOME/.workbuddy/agents}"

removed=0
for source in "$SOURCE_DIR"/*.md; do
  [[ -e "$source" ]] || continue
  target="$TARGET_DIR/$(basename "$source")"
  if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
    rm "$target"
    echo "已移除：$target"
    removed=$((removed + 1))
  fi
done

if [[ -d "$TARGET_DIR" && -z "$(ls -A "$TARGET_DIR")" ]]; then
  rmdir "$TARGET_DIR"
  echo "目录已空并删除：$TARGET_DIR"
fi

echo "完成。removed=$removed"
