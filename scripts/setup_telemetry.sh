#!/bin/bash
# Flywheel Telemetry Setup
#
# Run this script once to set up automatic telemetry collection and syncing.
# It installs Git hooks that:
#   1. Extract telemetry from engagement journals on commit
#   2. Sync telemetry to GitHub Issues on push

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ -z "$REPO_ROOT" ]; then
    echo "Error: Not inside a Git repository."
    exit 1
fi

echo "=== Flywheel Telemetry Setup ==="
echo ""
echo "This will configure automatic telemetry collection for the"
echo "Value Consulting AgenticOS. Your engagement metrics will be"
echo "synced to help improve the system for all consultants."
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "  [!] Python 3 not found. Telemetry extraction will be skipped."
    echo "      Install Python 3 to enable full telemetry."
else
    echo "  [OK] Python 3 found"
fi

if ! command -v gh &> /dev/null; then
    echo "  [!] GitHub CLI (gh) not found. Auto-sync on push will be disabled."
    echo "      Install: https://cli.github.com/"
    echo "      You can still use /sync-telemetry to sync manually."
else
    if gh auth status &> /dev/null 2>&1; then
        echo "  [OK] GitHub CLI authenticated"
    else
        echo "  [!] GitHub CLI not authenticated. Run: gh auth login"
        echo "      Auto-sync will be enabled once authenticated."
    fi
fi

echo ""

# Configure git to use custom hooks directory
echo "Configuring Git hooks..."
git config core.hooksPath .githooks

# Make hooks executable
chmod +x "$REPO_ROOT/.githooks/post-commit" 2>/dev/null || true
chmod +x "$REPO_ROOT/.githooks/pre-push" 2>/dev/null || true

echo "  [OK] Git hooks installed (.githooks/post-commit, .githooks/pre-push)"

# Create telemetry cache file
touch "$REPO_ROOT/.telemetry_cache.jsonl"
echo "  [OK] Telemetry cache created (.telemetry_cache.jsonl)"

# Add telemetry cache to gitignore if not already there
if ! grep -q '.telemetry_cache.jsonl' "$REPO_ROOT/.gitignore" 2>/dev/null; then
    echo '.telemetry_cache.jsonl' >> "$REPO_ROOT/.gitignore"
    echo "  [OK] Added .telemetry_cache.jsonl to .gitignore"
fi

# Add session ID files to gitignore
if ! grep -q '.engagement_session_id' "$REPO_ROOT/.gitignore" 2>/dev/null; then
    echo '.engagement_session_id' >> "$REPO_ROOT/.gitignore"
    echo "  [OK] Added .engagement_session_id to .gitignore"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "How it works:"
echo "  1. When you commit engagement files, telemetry is extracted automatically"
echo "  2. When you push, telemetry is synced to GitHub as an Issue"
echo "  3. The Flywheel's Triage Agent processes these weekly"
echo "  4. Improvements are built and sent for approval automatically"
echo ""
echo "Optional commands:"
echo "  /log-modification   — Log when you manually edit an agent's output"
echo "  /sync-telemetry     — Manually sync telemetry if auto-sync isn't working"
echo ""
echo "No further action needed. The system works silently in the background."
