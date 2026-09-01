#!/usr/bin/env bash
#
# migrate_engagement_ids.sh — Move existing client-named engagement directories
# to opaque engagement IDs.  DRY RUN IS THE DEFAULT.
#
# Usage:
#   ./scripts/migrate_engagement_ids.sh                        # plan only, changes nothing
#   ./scripts/migrate_engagement_ids.sh --name hdfc="HDFC Bank"
#   ./scripts/migrate_engagement_ids.sh --names-file names.txt
#   ./scripts/migrate_engagement_ids.sh --names-file names.txt --apply
#
#   --name SLUG=NAME    the client's real name for a directory slug (repeatable)
#   --names-file PATH   a file of `slug=Client Name` lines
#   --only SLUG         migrate only these client slugs (repeatable)
#   --apply             actually move things
#
# WHY A NAME IS REQUIRED
#   The client directory name is not only a leak — it is also a deny-list
#   source. Six of the seven live directories have no other one, so replacing
#   the slug with an opaque ID would silently disarm the outbound-query gate
#   for them. The migration writes a CLIENT_PROFILE.md carrying the client's
#   real name into each opaque directory to replace it, verifies the resulting
#   deny-list still covers every term the old one had, and REFUSES the whole
#   run if any engagement would come up short. See scripts/migrate_engagements.py.
#
# Runs on the SYSTEM python3 — no Presidio venv needed.
#
# Never invoked automatically. Not from a hook, not at session start. This is
# a consultant-invoked, one-time change to their own working directories.

set -euo pipefail

CORTEX_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "${CORTEX_ROOT}/CLAUDE.md" ]; then
    echo "Error: cannot find CLAUDE.md — run this from the cortex repo." >&2
    exit 1
fi

# --apply is the only destructive path, and it asks before proceeding. The
# plan is printed by the Python tool first either way, so the confirmation is
# given AFTER the consultant has seen exactly what will move.
APPLYING="no"
for arg in "$@"; do
    if [ "$arg" = "--apply" ]; then APPLYING="yes"; fi
done

if [ "$APPLYING" = "yes" ]; then
    # Show the plan first, without applying, then confirm.
    FILTERED=()
    for arg in "$@"; do
        if [ "$arg" != "--apply" ]; then FILTERED+=("$arg"); fi
    done
    python3 "${CORTEX_ROOT}/scripts/migrate_engagements.py" \
        --project-dir "${CORTEX_ROOT}" ${FILTERED+"${FILTERED[@]}"}

    echo ""
    echo "This MOVES the directories above. engagements/ is gitignored, so there"
    echo "is no git history to fall back on — take a copy first if you want one."
    printf "Type 'migrate' to proceed: "
    read -r CONFIRM
    if [ "$CONFIRM" != "migrate" ]; then
        echo "Cancelled. Nothing was changed."
        exit 1
    fi
fi

exec python3 "${CORTEX_ROOT}/scripts/migrate_engagements.py" \
    --project-dir "${CORTEX_ROOT}" "$@"
