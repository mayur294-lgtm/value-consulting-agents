# Build ROI Model

Standalone ROI pipeline — orchestrates the hypothesis builder and financial modeler agents outside the full assessment pipeline.

Use this when you need an ROI model without running the full orchestrator (e.g., solution-specific pitch, quick business case, standalone value assessment).

## Steps

### 1. Gather Context

Collect from the user (ask if not provided):
- **Bank name and country**
- **LOB** — Retail, SME, Commercial, Corporate, Wealth, Investing
- **Problem or objective** — what the bank wants to achieve OR what Backbase solution is being pitched
- **Available evidence** — any of: transcripts, questionnaires, data files, pain points, or just a verbal problem statement
- **Engagement directory** — where to write outputs (create if needed)

Determine the domain for knowledge loading (retail, wealth, commercial, sme, corporate, investing).

### 2. Launch Hypothesis Builder

Invoke the `roi-hypothesis-builder` agent with the gathered context.

**Prompt template:**
```
Engagement directory: {engagement_dir}
Bank: {bank_name}, {country}
LOB: {lob}
Domain: {domain}

Problem/Objective: {user's description}

Available evidence:
{list files or paste problem statement}

Read methodology:
- knowledge/methodologies/hypothesis_tree_decomposition.md
- knowledge/methodologies/value_lever_framework.md
- knowledge/domains/{domain}/benchmarks.md
- knowledge/domains/{domain}/roi_levers.md (if exists)

Produce:
- {outputs_dir}/lever_candidates.md
- {outputs_dir}/CHECKPOINT_roi_levers.md
```

Wait for the agent to complete and produce `lever_candidates.md`.

### 3. Consultant Validation

Present the lever candidates to the consultant:
- Show the problem statement
- Show the lever table (ID, name, lifecycle, type, gap estimate, confidence)
- Show excluded branches
- Ask: "Are these the right levers? Any to add, remove, or adjust?"

Incorporate feedback. If the consultant approves, write `CHECKPOINT_roi_levers_APPROVED.md`.

### 4. Launch Financial Modeler

Invoke the `roi-financial-modeler` agent with the validated levers.

**Prompt template:**
```
Engagement directory: {engagement_dir}
Domain: {domain}

Read validated lever candidates: {outputs_dir}/lever_candidates.md

Also read:
- knowledge/domains/{domain}/benchmarks.md
- knowledge/domains/{domain}/roi_levers.md (if exists)
- {outputs_dir}/market_context_validated.md (if exists)
- {outputs_dir}/capability_assessment.md (if exists)

Produce:
- {outputs_dir}/roi_report.md
- {outputs_dir}/roi_config.json
```

Wait for completion.

### 5. Run the Reasonableness Gate

Standalone `/build-roi` runs get the same reasonableness guarantee as a full pipeline run — the cap gate is not optional and not skippable just because there's no orchestrator in the loop.

Immediately after the financial modeler writes `{outputs_dir}/roi_config.json`, run the gate via Bash:

```
python3 scripts/artifact_boundary.py cap {outputs_dir}/roi_config.json
```

This caps any `backbase_impact` value over 60% in place (idempotent — safe to re-run) and prints a JSON gate report. Surface a **one-line gate report** to the consultant before moving on, derived from that JSON:

- If `modified: true`, summarize each capped value from `warnings`, e.g.: *"Gate: backbase_impact capped 0.72 → 0.60 on L3_retention (2 more capped — see full report)."*
- If `modified: false` and `warnings` is empty: *"Gate: no changes — within bounds."*
- If `modified: false` but `warnings` is non-empty (e.g. a curve-adjusted ROI outside the segment benchmark range): surface that warning too — it's not a cap violation, but it's exactly the kind of thing a consultant should see before presenting the number.

Do not silently swallow the gate output — if `roi_config.json` doesn't exist or fails to parse, stop and flag it rather than proceeding to Excel generation with an unverified config.

### 6. Review and Generate Excel

Present the financial model summary to the consultant (NPV, ROI, payback, per-lever breakdown), including the one-line gate report from step 5.

If approved, optionally run `/generate-roi-excel` to produce the Excel workbook:
```
/generate-roi-excel
```

(`/generate-roi-excel` re-runs the same cap gate itself before generating — it's idempotent, so this is a no-op if step 5 already capped the config. It exists as a skill-level backstop so an uncapped config can never reach Excel, even if `/generate-roi-excel` is invoked on a `roi_config.json` from somewhere other than this flow.)

### Shortcut: Skip to Financial Modeler

If the consultant already has a lever list (from a previous run, manual work, or another source), skip steps 2-3 and go directly to step 4. The financial modeler accepts any `lever_candidates.md` that follows the expected format. Step 5 (the gate) still applies regardless of how `roi_config.json` was produced.

### Output Files

| File | Description |
|------|-------------|
| `lever_candidates.md` | Validated lever list with four-link chains |
| `CHECKPOINT_roi_levers.md` | Lever checkpoint for audit trail |
| `roi_report.md` | Full analytical ROI report |
| `roi_config.json` | Structured config for Excel generation (capped by the reasonableness gate — step 5) |
| `*_ROI_Model.xlsx` | Excel workbook (if /generate-roi-excel invoked) |
