#!/usr/bin/env bash
set -euo pipefail

UPSTREAM="${1:?usage: apply_patch.sh <telegram-ios-checkout>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHANGES="${CHANGES_DIR:-$ROOT/changes}"

if [[ ! -f "$UPSTREAM/build-system/Make/Make.py" ]]; then
  echo "error: $UPSTREAM is not a Telegram-iOS checkout" >&2
  exit 1
fi
if [[ ! -d "$CHANGES" ]]; then
  echo "error: patch directory not found: $CHANGES" >&2
  exit 1
fi

cd "$CHANGES"
find . -type f -print0 | while IFS= read -r -d '' file; do
  rel="${file#./}"
  mkdir -p "$UPSTREAM/$(dirname "$rel")"
  cp "$file" "$UPSTREAM/$rel"
  echo "applied $rel"
done

grep -q "ChatListFolderRailView" "$UPSTREAM/submodules/ChatListUI/Sources/ChatListControllerNode.swift"
test -f "$UPSTREAM/submodules/ChatListUI/Sources/ChatListFolderRailView.swift"
echo "landscape patch applied"
