#!/bin/bash
# Auto-branch on Claude Code session start
# Creates a feature branch so consultants never work directly on main.
#
# Branch naming: {username}/{date}-{short-session-id}
# Example: mayur/20260211-a3f2

set -e

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Only act in git repos
git rev-parse --git-dir > /dev/null 2>&1 || exit 0

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

# If already on a feature branch, do nothing
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
  exit 0
fi

# Check for uncommitted changes — stash them if present
HAS_CHANGES=false
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
  HAS_CHANGES=true
fi

# Pull latest main
git pull --rebase origin "$CURRENT_BRANCH" 2>/dev/null || true

# Build branch name
USERNAME=$(git config user.name 2>/dev/null | tr ' ' '-' | tr '[:upper:]' '[:lower:]' || echo "unknown")
DATE=$(date +%Y%m%d)
SHORT_ID=$(echo "$RANDOM" | md5sum 2>/dev/null | head -c 4 || echo "0000")
BRANCH_NAME="${USERNAME}/${DATE}-${SHORT_ID}"

# Create and switch to the branch
git checkout -b "$BRANCH_NAME" 2>/dev/null

# Output message for Claude to relay to the user
echo "Auto-created branch: $BRANCH_NAME"
if [ "$HAS_CHANGES" = true ]; then
  echo "Note: Uncommitted changes from main are now on this branch."
fi

exit 0
