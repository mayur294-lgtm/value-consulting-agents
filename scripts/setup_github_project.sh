#!/bin/bash
# Flywheel: Set up GitHub Projects board
#
# Creates a GitHub Projects v2 board called "VC AgenticOS Flywheel"
# with the standard Kanban columns for tracking improvement items.
#
# Run this once to set up the project board.
#
# Prerequisites:
#   - gh CLI installed and authenticated
#   - Repository must exist on GitHub

set -e

REPO="${1:-$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null)}"

if [ -z "$REPO" ]; then
    echo "Usage: ./setup_github_project.sh [OWNER/REPO]"
    echo "Or run from within a GitHub-linked git repo."
    exit 1
fi

OWNER=$(echo "$REPO" | cut -d'/' -f1)

echo "=== Setting up Flywheel Project Board ==="
echo "Repository: $REPO"
echo ""

# Create the project
echo "Creating project..."
PROJECT_URL=$(gh project create \
    --owner "$OWNER" \
    --title "VC AgenticOS Flywheel" \
    --format json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('url',''))" 2>/dev/null || echo "")

if [ -z "$PROJECT_URL" ]; then
    echo "Note: Could not create project via CLI. You may need to create it manually at:"
    echo "  https://github.com/orgs/$OWNER/projects/new"
    echo ""
    echo "Create a project called 'VC AgenticOS Flywheel' with these columns:"
    echo "  1. Telemetry Inbox"
    echo "  2. Aggregated"
    echo "  3. Prioritized"
    echo "  4. In Development"
    echo "  5. Awaiting Approval"
    echo "  6. Released"
    echo ""
    echo "Then add these labels to the repository:"
fi

# Create labels for the repository
echo "Creating labels..."
LABELS=(
    "telemetry:Telemetry data from consultant engagements:0E8A16"
    "improvement:System improvement identified by Flywheel:1D76DB"
    "ready-for-dev:Prioritized and ready for Dev Agent:FBCA04"
    "dev-agent:Created or modified by Dev Agent:7057FF"
    "needs-review:Awaiting human review and approval:D93F0B"
    "critical:Critical severity issue:B60205"
    "high:High severity issue:FF6600"
    "moderate:Moderate severity issue:FBCA04"
    "low:Low severity issue:0E8A16"
)

for label_info in "${LABELS[@]}"; do
    IFS=':' read -r name description color <<< "$label_info"
    gh label create "$name" \
        --repo "$REPO" \
        --description "$description" \
        --color "$color" \
        --force 2>/dev/null && echo "  [OK] Label: $name" || echo "  [EXISTS] Label: $name"
done

# Create labels for each agent (for filtering)
AGENTS=(
    "capability-assessment"
    "roi-business-case-builder"
    "discovery-transcript-interpreter"
    "narrative-assembler"
    "roadmap-prioritization"
    "benchmark-librarian"
    "market-context-researcher"
    "value-consulting-orchestrator"
)

for agent in "${AGENTS[@]}"; do
    gh label create "$agent" \
        --repo "$REPO" \
        --description "Related to $agent agent" \
        --color "EDEDED" \
        --force 2>/dev/null && echo "  [OK] Label: $agent" || echo "  [EXISTS] Label: $agent"
done

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Labels created. The Flywheel workflows will use these labels to:"
echo "  - 'telemetry' — Tag raw telemetry from consultants"
echo "  - 'improvement' — Tag deduplicated improvement items"
echo "  - 'ready-for-dev' — Trigger the Dev Agent (event-driven)"
echo "  - 'dev-agent' — Tag PRs created by Dev Agent"
echo "  - 'needs-review' — Tag items awaiting Mayur's approval"
echo ""
if [ -n "$PROJECT_URL" ]; then
    echo "Project board: $PROJECT_URL"
fi
