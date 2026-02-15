# Build Journey Maps

Build evidence-based customer-to-employee journey maps with quantified value leakage, friction callouts, and Backbase-enabled future states.

## Usage
`/build-journey [domain] [journeys...]`

Where:
- `[domain]` is: `retail`, `commercial`, `sme`, `wealth`, `investing`, or `corporate`
- `[journeys...]` (optional) specifies which journeys to map. If omitted, the agent recommends top 3-5 by evidence density and asks the consultant to select.

## Prerequisites

Discovery outputs MUST exist in the engagement outputs directory before running this skill:
- `evidence_register.md` — Extracted evidence with IDs and lifecycle tags
- `pain_points.md` — Business problems mapped to lifecycle/journey
- `metrics.md` — Quantitative data points with units

If these files don't exist, run the Discovery Transcript Interpreter first.

## Instructions

When this skill is invoked:

1. **Locate engagement directory** — Find the active engagement directory containing discovery outputs. Check `ENGAGEMENT_JOURNAL.md` for context.

2. **Launch the journey-builder agent** using the Task tool with:
   - Domain from the command argument (or from engagement journal if not specified)
   - Journey selections from the command argument (if specified)
   - Path to the engagement outputs directory

3. **The agent will execute two consultant checkpoints:**
   - **Checkpoint #1 — Journey Selection:** Presents available journeys ranked by evidence density. Consultant picks 2-6 journeys. (Skipped if journeys were specified in the command.)
   - **Checkpoint #2 — Journey Validation:** Presents draft As-Is swimlanes, top frictions with $ estimates, and data gaps. Consultant confirms or adjusts.

4. **Output** is written to the engagement outputs directory:
   - `journey_maps.json` — Structured data consumed by `/generate-assessment-html`
   - `journey_maps_summary.md` — Human-readable summary consumed by the Assembly Agent (Act 4)

## What the Agent Produces

For each selected journey:
- **As-Is Swimlane** — Step-by-step current process with actors, systems, time, handoffs, and friction points
- **Friction Callout Cards** — Top 3-5 friction points ranked by $ impact, each with evidence quote and proposed Backbase fix
- **Value Leakage Waterfall** — Running total of value lost at each step
- **Future-State Swimlane** — Backbase-enabled journey with compressed steps, named products, and reduced time
- **Before/After Summary** — Metrics comparison (elapsed time, completion rate, employee time, STP rate, value leakage, handoffs)

Plus an **Aggregate Summary** across all journeys with total value leakage, total recoverable value, and top friction points.

## Integration

- **Upstream:** Reads discovery outputs (evidence, pain points, metrics registers)
- **Downstream:** Assembly Agent consumes `journey_maps_summary.md` for Act 4; HTML skill consumes `journey_maps.json` for interactive visualization
- **Pipeline position:** Runs after Discovery, in parallel with Market Context, Capability Assessment, and ROI agents

## Examples

```
/build-journey retail
→ Agent recommends top journeys by evidence density, consultant selects

/build-journey retail account-opening loan-origination
→ Agent builds maps for specified journeys directly (skips selection checkpoint)

/build-journey wealth advisory-onboarding portfolio-review
→ Agent builds wealth management journey maps

/build-journey investing account-opening first-investment
→ Agent builds investing journey maps
```

## Notes

- Journey maps are a core deliverable of Act 4 (Deep-Dive Assessment)
- The value leakage totals feed directly into Act 7 (Benefits Case) — these are the same numbers shown from two angles
- Each friction callout traces to capability gaps (Act 5) and ROI levers (Act 7) via trace IDs
- If evidence is thin for a journey, the agent will use domain benchmarks with explicit "benchmark_proxy" labels
- The consultant MUST validate the journey maps before they flow to assembly
