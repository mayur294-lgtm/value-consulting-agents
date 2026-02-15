# Engagement Journal — [Client Name]

> This file is the system's memory. Every agent writes to it. Every decision is recorded.
> If you're picking up this engagement after a break, read this file first.

## Engagement Summary

- **Client:** [Client Name]
- **Client Profile:** `engagements/[client_short_name]/CLIENT_PROFILE.md`
- **Domain:** [retail | sme | commercial | corporate | wealth | investing]
- **Region:** [e.g., Southeast Asia]
- **Engagement Type:** [assessment | ignite | hybrid]
- **Initiative Name:** [e.g., "Digital Investor Platform" — if multiple initiatives exist for this client]
- **Started:** [Date]
- **Current Status:** [In Progress | Paused | Complete]
- **Last Updated:** [Date]

## Prior Engagement Context

> Auto-populated from CLIENT_PROFILE.md. Helps agents understand what's already been discovered.

### Previous Engagements for This Client
| Date | Engagement | Domain | Key Outcome |
|------|-----------|--------|-------------|
| — | — | — | — |

### Carry-Forward Insights
> Insights from prior engagements that are relevant to THIS engagement. Copied from CLIENT_PROFILE.md cross-engagement insights + engagement intake "Cross-Engagement Leverage" section.

- [e.g., "Tech landscape validated in Jan 2026 — Fiserv DNA core, no changes expected"]
- [e.g., "Pain point P3 (manual onboarding) scored 4/5 severity — use as anchor"]

### Known Contradictions to Verify
- [e.g., "Prior digital adoption rate was 40% — client now claims 60%"]

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
2. Read `CLIENT_PROFILE.md` in the parent client directory — for persistent client context
3. Read `engagement_intake.md` — for this specific engagement's scope
4. Check the "Status After This Step" in the most recent journal entry — to see where we left off
5. Read only the latest output files listed in "Outputs Produced" — NOT the raw transcripts
6. Ask the consultant: "Based on the journal, here's where we left off: [summary]. What would you like to work on next?"

## On Engagement Completion

When this engagement is marked complete, the orchestrator MUST:
1. Update `CLIENT_PROFILE.md` → Engagement History table with this engagement's summary
2. Update `CLIENT_PROFILE.md` → Cross-Engagement Insights with any new recurring themes
3. Update `CLIENT_PROFILE.md` → Strategic Context if new information was discovered
4. Update `CLIENT_PROFILE.md` → Cumulative Value Delivered totals
