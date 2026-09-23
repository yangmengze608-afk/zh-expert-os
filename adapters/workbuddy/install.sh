#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="$ROOT/adapters/workbuddy/agents"
TARGET_DIR="${WORKBUDDY_AGENTS_DIR:-$HOME/.workbuddy/agents}"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "未找到 WorkBuddy agent 目录：$SOURCE_DIR" >&2
  exit 1
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
      echo "已连接：$target -> $source"
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
  echo "已安装：$target -> $source"
  installed=$((installed + 1))
done

echo
echo "WorkBuddy native agents 安装完成。new=$installed existing/skipped=$existing"
echo "目录：$TARGET_DIR"
echo
echo "注意：v0.5-alpha1 默认 lead -> workers 一层 fan-out。"
echo "不要把普通 child 当成可可靠递归 spawn 的 team lead。"
echo
if command -v zh-expert-os >/dev/null 2>&1; then
  echo "zh-expert-os CLI：$(command -v zh-expert-os)"
else
  echo "尚未发现 zh-expert-os CLI。建议执行："
  echo "  python -m pip install -e \"$ROOT\" --no-build-isolation"
fi
