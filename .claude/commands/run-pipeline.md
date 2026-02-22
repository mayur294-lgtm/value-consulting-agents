# Run Pipeline

Execute the Cortex assessment pipeline for an engagement using the Python orchestrator.

## Usage

The consultant should first point to an engagement folder in conversation, then invoke:
```
/run-pipeline
```

Or with an explicit path:
```
/run-pipeline engagements/client_name/2026-02_retail_assessment
```

## What This Does

Runs `scripts/orchestrate.py` which deterministically executes the full assessment pipeline:

1. **Discovery** — Process transcripts, extract evidence (sequential)
2. **Parallel Block A** — Journey Builder, Market Context, Capability, ROI, Benchmark (5 agents simultaneously)
3. **Roadmap** — Phased implementation plan (depends on ROI + Capability)
4. **Assembly** — 7-act narrative report (3 phases)
5. **HTML + Excel** — Dashboard and ROI model (parallel)
6. **Validation** — Output completeness check

Checkpoints are auto-approved with summaries shown in output. The consultant can review checkpoint summaries as they appear and interrupt if needed.

## Instructions

1. **Identify the engagement directory.** Look at the current conversation context for references to an engagement folder. The path should be under `engagements/` and contain an `inputs/` subdirectory with at least one `transcript_*.md` file and `engagement_intake.md`.

2. **Resolve the path.** If the user provided a relative path, resolve it relative to the cortex project root: `/Users/mayur@backbase.com/Documents/cortex/`

3. **Validate inputs exist.** Before running, check:
   - `<engagement_dir>/inputs/engagement_intake.md` exists
   - At least one `<engagement_dir>/inputs/transcript_*.md` exists
   - If missing, tell the consultant what's needed.

4. **Run the pipeline.** Execute:

```bash
cd /Users/mayur@backbase.com/Documents/cortex && CLAUDECODE= python3 scripts/orchestrate.py --non-interactive <engagement_dir>
```

The `CLAUDECODE=` prefix unsets the nesting restriction. The `--non-interactive` flag auto-approves checkpoints (required when running inside Claude Code since `input()` is not available).

5. **Stream progress.** The script prints timing, agent status, and checkpoint summaries to stdout. Relay key milestones to the consultant as they appear:
   - When Discovery completes
   - When parallel agents complete
   - When the final report is assembled
   - Final timing summary

6. **Report results.** When done, summarize:
   - Total time taken
   - Output files produced (with sizes)
   - Any validation warnings
   - Where to find the HTML dashboard and Excel model

## Options

Add these flags as needed:

- `--express` — Also auto-approve intermediate checkpoints with less output (faster)
- `--resume-from <step>` — Resume from: `discovery`, `parallel_a`, `roadmap`, `assembly`, `generate`, `validate`
- `--dry-run` — Show what would execute without running

## Example Flow

Consultant says: "I've uploaded transcripts for Acme Bank in engagements/acme_bank/2026-03_retail_assessment/inputs/. Run the pipeline."

You respond:
1. Verify the engagement folder and inputs exist
2. Run: `CLAUDECODE= python3 scripts/orchestrate.py --non-interactive engagements/acme_bank/2026-03_retail_assessment/`
3. Stream progress updates as the pipeline runs
4. Report final results with output file locations
