#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Cortex — One-time harvest token setup
# Run once per machine. Never needs to be run again after a git pull.
#
# Usage:
#   ./scripts/setup-harvest.sh ghp_xxxxxxxxxxxx
#
# Get the token from: 1Password → "Cortex Harvest Token"
# ─────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORTEX_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$CORTEX_DIR/.env"

TOKEN="$1"

if [ -z "$TOKEN" ]; then
    echo ""
    echo "  ❌  No token provided."
    echo ""
    echo "  Usage:  ./scripts/setup-harvest.sh <token>"
    echo "  Token:  1Password → 'Cortex Harvest Token'"
    echo ""
    exit 1
fi

# Validate it looks like a GitHub token
if [[ ! "$TOKEN" == ghp_* ]] && [[ ! "$TOKEN" == github_pat_* ]]; then
    echo ""
    echo "  ⚠️   That doesn't look like a GitHub token (should start with ghp_ or github_pat_)"
    echo "  Get it from 1Password → 'Cortex Harvest Token'"
    echo ""
    exit 1
fi

# Remove any existing CORTEX_HARVEST_TOKEN line and append fresh
touch "$ENV_FILE"
grep -v "^CORTEX_HARVEST_TOKEN=" "$ENV_FILE" > "$ENV_FILE.tmp" && mv "$ENV_FILE.tmp" "$ENV_FILE"
echo "CORTEX_HARVEST_TOKEN=$TOKEN" >> "$ENV_FILE"

echo ""
echo "  ✅  Harvest token saved to .env"
echo ""
echo "  That's it. From now on, every pipeline run will automatically"
echo "  push anonymised learnings back to the shared knowledge base."
echo "  You don't need to do anything else."
echo ""
