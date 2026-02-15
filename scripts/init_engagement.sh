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
#   1. Creates the client directory if it doesn't exist
#   2. Creates CLIENT_PROFILE.md from template if this is a new client
#   3. Creates the engagement directory with inputs/ and outputs/ subdirs
#   4. Copies engagement_intake.md template to inputs/
#   5. Copies engagement_journal.md template
#   6. Generates a session UUID
#   7. Prints next steps for the consultant
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

CLIENT_DIR="${ENGAGEMENTS_DIR}/${CLIENT_SLUG}"
ENGAGEMENT_DIR="${CLIENT_DIR}/${ENGAGEMENT_NAME}"

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

# Check engagement doesn't already exist
if [ -d "$ENGAGEMENT_DIR" ]; then
    echo "Error: Engagement directory already exists: ${ENGAGEMENT_DIR}"
    echo "If you want to resume, just cd into it."
    exit 1
fi

# --- Create client directory if new ---

IS_NEW_CLIENT="No"
if [ ! -d "$CLIENT_DIR" ]; then
    IS_NEW_CLIENT="Yes"
    echo "Creating new client: ${CLIENT_SLUG}"
    mkdir -p "$CLIENT_DIR"

    # Copy client profile template
    if [ -f "${CORTEX_ROOT}/templates/client_profile.md" ]; then
        cp "${CORTEX_ROOT}/templates/client_profile.md" "${CLIENT_DIR}/CLIENT_PROFILE.md"
        # Replace placeholder with client slug
        sed -i.bak "s/\[Client Name\]/${CLIENT_SLUG}/g" "${CLIENT_DIR}/CLIENT_PROFILE.md"
        sed -i.bak "s/\[slug used in directory names, e.g., \`navy_federal\`\]/${CLIENT_SLUG}/g" "${CLIENT_DIR}/CLIENT_PROFILE.md"
        rm -f "${CLIENT_DIR}/CLIENT_PROFILE.md.bak"
        echo "  Created CLIENT_PROFILE.md (fill in client details)"
    else
        echo "  Warning: templates/client_profile.md not found. Creating placeholder."
        echo "# Client Profile — ${CLIENT_SLUG}" > "${CLIENT_DIR}/CLIENT_PROFILE.md"
        echo "" >> "${CLIENT_DIR}/CLIENT_PROFILE.md"
        echo "> Fill in using template from templates/client_profile.md" >> "${CLIENT_DIR}/CLIENT_PROFILE.md"
    fi
else
    echo "Existing client: ${CLIENT_SLUG}"
    echo "  Client profile: ${CLIENT_DIR}/CLIENT_PROFILE.md"
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
    # Fix client profile reference
    sed -i.bak "s#\`engagements/\[client_short_name\]/CLIENT_PROFILE.md\`#\`engagements/${CLIENT_SLUG}/CLIENT_PROFILE.md\`#g" "${ENGAGEMENT_DIR}/inputs/engagement_intake.md"
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

# --- Summary ---

echo ""
echo "=================================================="
echo "  Engagement initialized successfully!"
echo "=================================================="
echo ""
echo "  Client:      ${CLIENT_SLUG} (${IS_NEW_CLIENT} — new client)"
echo "  Engagement:  ${ENGAGEMENT_NAME}"
echo "  Type:        ${ENGAGEMENT_TYPE}"
echo "  Directory:   ${ENGAGEMENT_DIR}"
echo "  Session ID:  ${SESSION_ID}"
echo ""
echo "Directory structure:"
echo "  engagements/"
echo "  └── ${CLIENT_SLUG}/"
if [ "$IS_NEW_CLIENT" = "Yes" ]; then
echo "      ├── CLIENT_PROFILE.md        ← Fill in client details"
fi
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
