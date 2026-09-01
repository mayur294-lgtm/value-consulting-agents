#!/usr/bin/env bash
#
# init_engagement.sh — Bootstrap a new engagement within the Client → Engagement hierarchy.
#
# Usage:
#   ./scripts/init_engagement.sh <client_short_name> <engagement_name> [engagement_type]
#
# Examples:
#   ./scripts/init_engagement.sh navy_federal 2026-02_retail_assessment assessment
#   ./scripts/init_engagement.sh navy_federal 2026-03_wealth_ignite ignite
#   ./scripts/init_engagement.sh acme_bank 2026-01_sme_assessment assessment
#
# What it does:
#   1. Mints an OPAQUE engagement ID and records it in .engagement_map.json
#   2. Writes CLIENT_PROFILE.md carrying the client's identifier forms
#   3. Creates the engagement directory with inputs/ and outputs/ subdirs
#   4. Copies engagement_intake.md template to inputs/
#   5. Copies engagement_journal.md template
#   6. Generates a session UUID
#   7. Prints next steps for the consultant
#
# WHY THE DIRECTORY IS AN OPAQUE ID (solution-design-v6.md D6)
#   `compose_prompt` renders `engagement_dir` into every agent invocation as a
#   VALUE, and `run_agent` sets `cwd` to it. A directory called `hdfc` therefore
#   tells the model the client's name on every single call, however well the
#   file CONTENTS are scrubbed. So the directory is `engagements/<opaque_id>/`
#   and the ID -> client binding lives only in `.engagement_map.json` (repo
#   root, chmod 600, gitignored), which never leaves this machine.
#
#   You never have to know or type the ID. Find any engagement with:
#       ./scripts/find_engagement.sh <client>
#
# The call signature is UNCHANGED — you still pass the client's short name.
#
# IMPORTANT: Run this from the cortex repo root.

set -euo pipefail

CORTEX_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENGAGEMENTS_DIR="${CORTEX_ROOT}/engagements"

# --- Argument parsing ---

if [ $# -lt 2 ]; then
    echo "Usage: $0 <client_short_name> <engagement_name> [engagement_type]"
    echo ""
    echo "  client_short_name   Lowercase slug for the bank (e.g., navy_federal)"
    echo "  engagement_name     YYYY-MM_domain_type format (e.g., 2026-02_retail_assessment)"
    echo "  engagement_type     assessment | ignite | hybrid | roi_only | deal_strategy (default: assessment)"
    echo ""
    echo "Examples:"
    echo "  $0 navy_federal 2026-02_retail_assessment assessment"
    echo "  $0 acme_bank 2026-01_sme_ignite ignite"
    exit 1
fi

CLIENT_SLUG="$1"
ENGAGEMENT_NAME="$2"
ENGAGEMENT_TYPE="${3:-assessment}"

# --- Validation ---

# Validate engagement type
VALID_TYPES="assessment ignite hybrid roi_only deal_strategy"
if ! echo "$VALID_TYPES" | grep -qw "$ENGAGEMENT_TYPE"; then
    echo "Error: Invalid engagement type '${ENGAGEMENT_TYPE}'"
    echo "Valid types: ${VALID_TYPES}"
    exit 1
fi

# Check we're in the cortex root
if [ ! -f "${CORTEX_ROOT}/CLAUDE.md" ]; then
    echo "Error: Cannot find CLAUDE.md. Are you running from the cortex repo root?"
    echo "Run: cd /path/to/cortex && ./scripts/init_engagement.sh ..."
    exit 1
fi

# --- Mint the opaque engagement ID + write CLIENT_PROFILE.md ---
#
# Both halves are `scripts/pii/identity.py`'s job and both must happen or
# neither: the map entry is what keeps the directory findable at all, and
# CLIENT_PROFILE.md is what keeps the client's name on the deny-list now that
# the directory name no longer supplies it.
#
# The profile is CARRIED FORWARD from this client's most recent prior
# engagement when there is one — CLIENT_PROFILE.md is long-term memory that
# survives across engagements, and one opaque directory per engagement must
# not quietly fragment it.
#
# System python3 is enough: identity.py is stdlib-only and 3.9-clean by
# contract, so starting an engagement never needs the Presidio venv.

INIT_OUT="$(CORTEX_ROOT="$CORTEX_ROOT" CLIENT_SLUG="$CLIENT_SLUG" \
            ENGAGEMENT_NAME="$ENGAGEMENT_NAME" \
            python3 "${CORTEX_ROOT}/scripts/init_engagement_identity.py")" || exit $?

ENGAGEMENT_ID="$(echo "$INIT_OUT" | sed -n '1p')"
IS_NEW_CLIENT="$(echo "$INIT_OUT" | sed -n '2p')"

CLIENT_DIR="${ENGAGEMENTS_DIR}/${ENGAGEMENT_ID}"
ENGAGEMENT_DIR="${CLIENT_DIR}/${ENGAGEMENT_NAME}"

if [ "$IS_NEW_CLIENT" = "Yes" ]; then
    echo "Creating new client: ${CLIENT_SLUG}"
    echo "  Created CLIENT_PROFILE.md (fill in client details)"
else
    echo "Existing client: ${CLIENT_SLUG}"
    echo "  Client profile carried forward: ${CLIENT_DIR}/CLIENT_PROFILE.md"
fi

# --- Create engagement directory structure ---

echo "Creating engagement: ${ENGAGEMENT_NAME}"
mkdir -p "${ENGAGEMENT_DIR}/inputs"
mkdir -p "${ENGAGEMENT_DIR}/outputs"

# Copy engagement intake template
if [ -f "${CORTEX_ROOT}/templates/inputs/engagement_intake.md" ]; then
    cp "${CORTEX_ROOT}/templates/inputs/engagement_intake.md" "${ENGAGEMENT_DIR}/inputs/engagement_intake.md"
    # Pre-fill known fields
    sed -i.bak "s/\[e.g., \`navy_federal\` — must match directory name under \`engagements\/\`\]/${CLIENT_SLUG}/g" "${ENGAGEMENT_DIR}/inputs/engagement_intake.md"
    # Use # as delimiter to avoid conflict with | in the pattern
    sed -i.bak "s#\[Yes | No — if Yes, CLIENT_PROFILE.md will be created by init_engagement.sh\]#${IS_NEW_CLIENT}#g" "${ENGAGEMENT_DIR}/inputs/engagement_intake.md"
    # Pre-fill engagement type
    sed -i.bak "s#\[assessment | ignite | hybrid | ROI_only | deal_strategy\]#${ENGAGEMENT_TYPE}#g" "${ENGAGEMENT_DIR}/inputs/engagement_intake.md"
    # Fix client profile reference — now the opaque directory, not the slug
    sed -i.bak "s#\`engagements/\[client_short_name\]/CLIENT_PROFILE.md\`#\`engagements/${ENGAGEMENT_ID}/CLIENT_PROFILE.md\`#g" "${ENGAGEMENT_DIR}/inputs/engagement_intake.md"
    rm -f "${ENGAGEMENT_DIR}/inputs/engagement_intake.md.bak"
    echo "  Created inputs/engagement_intake.md"
else
    echo "  Warning: engagement intake template not found"
fi

# Copy engagement journal template
if [ -f "${CORTEX_ROOT}/templates/outputs/engagement_journal.md" ]; then
    cp "${CORTEX_ROOT}/templates/outputs/engagement_journal.md" "${ENGAGEMENT_DIR}/ENGAGEMENT_JOURNAL.md"
    # Pre-fill client name
    TODAY=$(date +%Y-%m-%d)
    sed -i.bak "s/\[Client Name\]/${CLIENT_SLUG}/g" "${ENGAGEMENT_DIR}/ENGAGEMENT_JOURNAL.md"
    sed -i.bak "s/\[assessment | ignite | hybrid\]/${ENGAGEMENT_TYPE}/g" "${ENGAGEMENT_DIR}/ENGAGEMENT_JOURNAL.md"
    sed -i.bak "s/\[Date\]/${TODAY}/g" "${ENGAGEMENT_DIR}/ENGAGEMENT_JOURNAL.md"
    rm -f "${ENGAGEMENT_DIR}/ENGAGEMENT_JOURNAL.md.bak"
    echo "  Created ENGAGEMENT_JOURNAL.md"
else
    echo "  Warning: engagement journal template not found"
fi

# Generate session UUID
SESSION_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
echo "$SESSION_ID" > "${ENGAGEMENT_DIR}/.engagement_session_id"
echo "  Generated session ID: ${SESSION_ID}"

# --- Summary (Flow G) ---

echo ""
echo "=================================================="
echo "  Engagement initialized successfully!"
echo "=================================================="
echo ""
echo "  Created engagement ${ENGAGEMENT_ID} for ${CLIENT_SLUG}."
echo ""
echo "  Find it any time with:"
echo "      ./scripts/find_engagement.sh ${CLIENT_SLUG}"
echo ""
echo "  Client:      ${CLIENT_SLUG} (${IS_NEW_CLIENT} — new client)"
echo "  Engagement:  ${ENGAGEMENT_NAME}"
echo "  Type:        ${ENGAGEMENT_TYPE}"
echo "  Directory:   ${ENGAGEMENT_DIR}"
echo "  Session ID:  ${SESSION_ID}"
echo ""
echo "  The directory is an opaque ID on purpose: its name would otherwise"
echo "  reach the model on every agent call. Nothing inside it changes."
echo ""
echo "Directory structure:"
echo "  engagements/"
echo "  └── ${ENGAGEMENT_ID}/"
echo "      ├── CLIENT_PROFILE.md        ← Fill in client details"
echo "      └── ${ENGAGEMENT_NAME}/"
echo "          ├── inputs/"
echo "          │   └── engagement_intake.md  ← Fill in engagement details"
echo "          ├── outputs/                  ← Agent outputs go here"
echo "          ├── ENGAGEMENT_JOURNAL.md     ← System memory"
echo "          └── .engagement_session_id    ← Telemetry UUID"
echo ""
echo "Next steps:"
echo "  1. Fill in: ${ENGAGEMENT_DIR}/inputs/engagement_intake.md"
if [ "$IS_NEW_CLIENT" = "Yes" ]; then
echo "  2. Fill in: ${CLIENT_DIR}/CLIENT_PROFILE.md"
echo "  3. Add transcripts to: ${ENGAGEMENT_DIR}/inputs/"
echo "  4. Start Claude Code from the cortex directory and run the orchestrator"
else
echo "  2. Add transcripts to: ${ENGAGEMENT_DIR}/inputs/"
echo "  3. Review prior engagement insights in CLIENT_PROFILE.md"
echo "  4. Start Claude Code from the cortex directory and run the orchestrator"
fi
echo ""
