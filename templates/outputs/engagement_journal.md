# Engagement Journal — [Client Name]

> This file is the system's memory. Every agent writes to it. Every decision is recorded.
> If you're picking up this engagement after a break, read this file first.

## Engagement Summary

- **Client:** [Client Name]
- **Domain:** [retail | sme | commercial | corporate | wealth]
- **Region:** [e.g., Southeast Asia]
- **Engagement Type:** [assessment | ignite | hybrid]
- **Started:** [Date]
- **Current Status:** [In Progress | Paused | Complete]
- **Last Updated:** [Date]

## Files Inventory

### Inputs Provided
| File | Description | Size | Status |
|------|-------------|------|--------|
| `engagement_intake.md` | Client context and scope | — | Processed |
| `transcript_[name].md` | [Stakeholder] interview | [X lines] | Processed / Pending |

### Outputs Produced
| File | Description | Produced By | Date |
|------|-------------|-------------|------|
| `evidence_register.md` | Consolidated evidence from all transcripts | Discovery Agent | [Date] |
| `capability_assessment.md` | Maturity scoring and gap analysis | Capability Agent | [Date] |
| `roi_report.md` | Financial business case | ROI Agent | [Date] |
| `roadmap.md` | Phased implementation plan | Roadmap Agent | [Date] |
| `executive_summary.md` | Decision document | Assembly Agent | [Date] |

### Interim Files (processing artifacts)
| File | Description | Can be deleted? |
|------|-------------|----------------|
| `interim_transcript_[name].md` | Per-transcript evidence extraction | Yes, after consolidation |

---

## Decision Log

> Every significant decision, assumption, and consultant direction is recorded here.
> Format: newest entries at the top.

---

### [YYYY-MM-DD HH:MM] — [Agent Name]

**Action:** [What was done — e.g., "Processed 3 discovery transcripts"]

<!-- TELEMETRY_START -->
- Agent: [agent-name]
- Session ID: [from .engagement_session_id file]
- Start Time: [ISO timestamp when you began work]
- End Time: [ISO timestamp when you finished]
- Duration: [seconds]
- Input Files: [count and total size in KB]
- Output Files: [count and total size in KB]
- Errors Encountered: [none | brief error descriptions]
- Quality Self-Check: [passed | failed | passed_with_warnings]
<!-- TELEMETRY_END -->

**Input Files Read:**
- [List of files this agent consumed]

**Output Files Written:**
- [List of files this agent produced]

**Key Findings:**
- [Finding 1]
- [Finding 2]

**Decisions Made:**
- [Decision and rationale — e.g., "Scored onboarding maturity at 2/5 based on E3, E7 evidence of manual processes and >7-day cycle time"]

**Assumptions Made:**
- [Assumption, basis, and confidence — e.g., "Assumed 500K customer base based on regional tier-2 bank benchmarks (Medium confidence). Flagged for validation with client."]

**Consultant Direction:**
- [What the consultant asked for, approved, or rejected — e.g., "Consultant confirmed focus on onboarding and servicing journeys only. Lending out of scope."]

**Status After This Step:**
- **Completed:** [What's done]
- **Next:** [What should happen next]
- **Blocked/Pending:** [Anything waiting on input]

---

### [YYYY-MM-DD HH:MM] — [Next Agent Entry]

[Continue with same format...]

---

## Assumptions Register (Cumulative)

> All assumptions across all agents, consolidated here for easy reference.

| ID | Assumption | Made By | Confidence | Basis | Validation Owner | Status |
|----|-----------|---------|------------|-------|------------------|--------|
| A1 | [Statement] | [Agent] | H/M/L | [Why] | [Who should validate] | Open / Validated / Revised |

## Open Questions

> Items that need consultant or client input before proceeding.

| ID | Question | Raised By | Priority | Status |
|----|----------|-----------|----------|--------|
| Q1 | [Question] | [Agent] | Critical/High/Medium | Open / Resolved |

## Knowledge Harvest Log

> Auto-populated by Orchestrator Step 9. Do not edit manually.

| Category | Entries Written | Target File | Harvest Date |
|----------|----------------|-------------|--------------|
| Benchmarks | — | — | — |
| Pain Points | — | — | — |
| Capability Maturity | — | — | — |
| ROI Patterns | — | — | — |

**Harvest Status:** Pending (runs automatically at engagement completion)

---

## How to Resume This Engagement

1. Read this journal file — it contains the complete history
2. Read `engagement_intake.md` — for client context
3. Check the "Status After This Step" in the most recent journal entry — to see where we left off
4. Read only the latest output files listed in "Outputs Produced" — NOT the raw transcripts
5. Ask the consultant: "Based on the journal, here's where we left off: [summary]. What would you like to work on next?"
