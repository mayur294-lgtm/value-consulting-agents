#!/bin/bash
# _resolve_python.sh — interpreter resolver for hooks that need the PII venv.
#
# Decision record: .design/solution-design-v6.md D12.
#
# .claude/settings.json invokes every hook as `python3 <script>` — i.e. the
# SYSTEM interpreter (3.9.6 here), which cannot import Presidio (needs
# 3.10-3.13; see scripts/setup_pii.sh). A hook that imports Presidio at
# module level (e.g. a future anonymize-guard.py — PR 3 in prd-v6.md) must
# instead run under the venv scripts/setup_pii.sh creates at .venv.
#
# This script is that indirection point. settings.json calls it in place of
# `python3` for any hook that needs Presidio; it resolves to:
#   - "$CLAUDE_PROJECT_DIR"/.venv/bin/python, if that venv exists
#   - system `python3`, otherwise
#
# It NEVER hard-fails: if the venv is missing (the consultant hasn't run
# `bash scripts/setup_pii.sh` yet — exactly the situation pii-preflight.sh
# exists to announce), it falls back to system python3 and runs the hook
# anyway. The hook itself is responsible for its own fail-open/fail-closed
# behaviour when Presidio can't be imported (see anonymize-guard.py's
# "engine unavailable" case in .design/ux-design-v6.md) — this script's only
# job is picking the interpreter, never deciding whether to block.
#
# Usage (from settings.json):
#   "$CLAUDE_PROJECT_DIR"/.claude/hooks/_resolve_python.sh "$CLAUDE_PROJECT_DIR"/.claude/hooks/<hook>.py

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
VENV_PY="$PROJECT_DIR/.venv/bin/python"

if [ -x "$VENV_PY" ]; then
    exec "$VENV_PY" "$@"
else
    exec python3 "$@"
fi
