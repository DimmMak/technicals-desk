#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="$HOME/.claude/skills/technicals-desk"
STALE_ZIP="$HOME/.claude/skills/technicals-desk.skill"

echo "📦 technicals-desk install/sync"

if ! python3 -c "import yfinance, pandas" 2>/dev/null; then
  echo "📦 Installing yfinance + pandas..."
  pip3 install yfinance pandas || exit 1
fi

[ -f "$STALE_ZIP" ] && { echo "🗑️  removing stale $STALE_ZIP"; rm "$STALE_ZIP"; }
[ "${1:-}" = "--clean" ] && rm -rf "$INSTALL_DIR"

mkdir -p "$INSTALL_DIR"
cp "$REPO_DIR/SKILL.md" "$INSTALL_DIR/"
cp -R "$REPO_DIR/scripts" "$INSTALL_DIR/"
[ -d "$REPO_DIR/data" ] && cp -R "$REPO_DIR/data" "$INSTALL_DIR/"

VERSION=$(grep -m1 "^version:" "$INSTALL_DIR/SKILL.md" | awk '{print $2}')
echo "✅ installed technicals-desk v$VERSION — restart Claude Code to reload"
