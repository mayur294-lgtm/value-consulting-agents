#!/bin/bash
# validate_engagement_outputs.sh — Hard gate for engagement completion
# Usage: ./scripts/validate_engagement_outputs.sh <engagement_dir> <engagement_type>
# Returns exit code 0 if all required outputs exist, 1 if any are missing.
# Prints missing files so the orchestrator knows what to generate.

set -euo pipefail

ENGAGEMENT_DIR="${1:?Usage: validate_engagement_outputs.sh <engagement_dir> <engagement_type>}"
ENGAGEMENT_TYPE="${2:-assessment}"

OUTPUTS_DIR="${ENGAGEMENT_DIR}/outputs"
MISSING=()
WARNINGS=()

echo "=========================================="
echo "ENGAGEMENT OUTPUT VALIDATION"
echo "=========================================="
echo "Directory: ${ENGAGEMENT_DIR}"
echo "Type: ${ENGAGEMENT_TYPE}"
echo ""

# ── Core deliverables (ALL engagement types) ──
check_required() {
    local file="$1"
    local desc="$2"
    if [ -f "${OUTPUTS_DIR}/${file}" ]; then
        size=$(wc -c < "${OUTPUTS_DIR}/${file}")
        if [ "$size" -lt 100 ]; then
            MISSING+=("${file} (exists but EMPTY — ${size} bytes) [${desc}]")
            echo "  ✗ ${file} — EXISTS BUT EMPTY (${size} bytes)"
        else
            echo "  ✓ ${file} ($(numfmt --to=iec ${size} 2>/dev/null || echo "${size}B"))"
        fi
    else
        MISSING+=("${file} [${desc}]")
        echo "  ✗ ${file} — MISSING"
    fi
}

check_html() {
    local pattern="$1"
    local desc="$2"
    local found=$(find "${OUTPUTS_DIR}" -name "${pattern}" -type f 2>/dev/null | head -1)
    if [ -n "$found" ]; then
        size=$(wc -c < "$found")
        name=$(basename "$found")
        if [ "$size" -lt 50000 ]; then
            WARNINGS+=("${name} exists but small (${size} bytes — expected >200KB) [${desc}]")
            echo "  ⚠ ${name} — EXISTS BUT SMALL (${size} bytes, expected >200KB)"
        else
            echo "  ✓ ${name} ($(numfmt --to=iec ${size} 2>/dev/null || echo "${size}B"))"
        fi
    else
        MISSING+=("${pattern} [${desc}]")
        echo "  ✗ ${pattern} — MISSING"
    fi
}

# ── Discovery outputs ──
echo "── Discovery Registers ──"
check_required "evidence_register.md" "Discovery Agent output"
check_required "pain_points.md" "Discovery Agent output"
check_required "metrics.md" "Discovery Agent output"
check_required "stakeholder_intelligence.md" "Discovery Agent output"

# ── Assessment-specific outputs ──
if [ "$ENGAGEMENT_TYPE" = "assessment" ] || [ "$ENGAGEMENT_TYPE" = "ignite_assess" ]; then
    echo ""
    echo "── Capability Assessment ──"
    check_required "capability_assessment.md" "Capability Agent output"

    echo ""
    echo "── Market Context ──"
    check_required "market_context_validated.md" "Market Context Agent output"

    echo ""
    echo "── Benchmarks ──"
    check_required "benchmarks_validated.md" "Benchmark Librarian output"

    echo ""
    echo "── Roadmap ──"
    check_required "roadmap.md" "Roadmap Agent output"

    echo ""
    echo "── ROI Business Case ──"
    check_required "roi_report.md" "ROI Agent output"
    check_required "roi_config.json" "ROI Agent output — needed for Excel generation"

    echo ""
    echo "── Final Assembly ──"
    check_required "assessment_report.md" "Narrative Assembler output"
    check_required "executive_summary.md" "Narrative Assembler output"

    echo ""
    echo "── Generated Deliverables (Skills) ──"
    check_html "*.html" "HTML Dashboard — invoke /generate-assessment-html"
    # check_required "roi_model.xlsx" "ROI Excel — invoke /generate-roi-excel"
fi

# ── Ignite-specific outputs ──
if [ "$ENGAGEMENT_TYPE" = "ignite" ] || [ "$ENGAGEMENT_TYPE" = "ignite_assess" ]; then
    echo ""
    echo "── Workshop Outputs ──"
    check_html "*workshop*.html" "Workshop deck — Workshop Prep Agent"
fi

# ── Checkpoint audit trail ──
echo ""
echo "── Checkpoint Audit Trail ──"
cp_count=$(find "${OUTPUTS_DIR}" -name "CHECKPOINT_*.md" ! -name "*APPROVED*" | wc -l)
ap_count=$(find "${OUTPUTS_DIR}" -name "CHECKPOINT_*_APPROVED.md" | wc -l)
echo "  Checkpoints written: ${cp_count}"
echo "  Checkpoints approved: ${ap_count}"
unapproved=$((cp_count - ap_count))
if [ "$unapproved" -gt 0 ]; then
    echo "  ⚠ ${unapproved} checkpoint(s) without approval:"
    comm -23 \
        <(find "${OUTPUTS_DIR}" -name "CHECKPOINT_*.md" ! -name "*APPROVED*" -exec basename {} \; | sort) \
        <(find "${OUTPUTS_DIR}" -name "CHECKPOINT_*_APPROVED.md" -exec basename {} \; | sed 's/_APPROVED//' | sort) \
        | while read f; do echo "    - $f"; done
fi

# ── Summary ──
echo ""
echo "=========================================="
if [ ${#MISSING[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ]; then
    echo "STATUS: ✓ ALL REQUIRED OUTPUTS PRESENT"
    echo "=========================================="
    exit 0
else
    if [ ${#MISSING[@]} -gt 0 ]; then
        echo "STATUS: ✗ MISSING ${#MISSING[@]} REQUIRED OUTPUT(S)"
        echo ""
        echo "MISSING FILES (must generate before completion):"
        for m in "${MISSING[@]}"; do
            echo "  → ${m}"
        done
    fi
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo ""
        echo "WARNINGS:"
        for w in "${WARNINGS[@]}"; do
            echo "  ⚠ ${w}"
        done
    fi
    echo ""
    echo "=========================================="
    echo "ACTION: Generate missing files before marking engagement complete."
    echo "=========================================="
    exit 1
fi
