---
version: 4
prd: prd-v4.md
status: draft
date: 2026-07-28
author: Mariam Titus George
previous: ux-design-v3.md
---

# UX Design v4 — Lossless PII Round-Trip

The "user" here is the consultant watching the pipeline log or invoking the skills/CLI. No screens are involved; the UX surface is terminal output, exit codes, and the files that land in the engagement directory.

## User Flows

### Flow 1 — Anonymization during discovery (pipeline)

```
orchestrate.py step_discovery finds transcript_*.md
        │
        ▼
For each transcript: anonymize_transcript_file(..., shared numbering threaded across files)
        │
        ├──[entity names found]──▶ log "Anonymized: transcript_1.md → .anon_transcript_1.md"
        │
        ├──[entity list EMPTY]──▶ log ⚠ "No client/person names found in intake or context —
        │                          only generic PII (emails, phones, SSNs, accounts) was stripped.
        │                          Client and person names may reach the API in plaintext.
        │                          Check inputs/engagement_intake.md."   (pipeline continues)
        │
        └──[anonymization raises]──▶ existing fail-closed path: transcript SKIPPED loudly, never sent raw
        │
        ▼
Combined mapping written to .pii_mapping.json (chmod 600)
        │
        ▼
Per-transcript .anon_mapping_*.json files deleted
        │
        ▼
log "PII mapping saved (N substitutions); per-transcript mappings cleaned up"
```

### Flow 2 — De-anonymization of outputs (pipeline step 6b / `/build-roi` / `/generate-roi-excel` / `/publish` via `artifact_boundary.py deanon`)

```
deanonymize_dir(outputs_dir)
        │
        ├──[.pii_mapping.json missing]──▶ existing LOUD red failure: "outputs NOT client-ready", exit 1
        │
        ▼
Walk outputs/ RECURSIVELY (rglob), skip interim* and dotfiles
        │
        ├──[.md/.html/.json/.txt]──▶ text replacement (as today)
        │
        ├──[.xlsx]──▶ openpyxl available? ──yes──▶ restore placeholders in cell strings + sheet titles
        │                    │
        │                    └──no──▶ log ✗ "openpyxl unavailable — ROI_Model.xlsx NOT restored,
        │                             still contains placeholders. pip install openpyxl and re-run
        │                             `python3 scripts/artifact_boundary.py deanon <dir>`."
        │                             → client_ready = false, exit 1
        │
        ▼
log "✓ De-anonymized N output file(s) (M spreadsheets)"  → exit 0
```

### Flow 3 — Standalone CLI round-trip (unchanged surface)

`python3 scripts/anonymize_transcript.py --file t.md --engagement-dir <dir>` prints the anon + mapping paths as today; the mapping file is now mode 600. `--deanonymize --mapping <file>` restores **every** occurrence to its own original value — no behavioral flags added, no CLI changes.

## Component States (terminal/log surface)

| State | Trigger | What the consultant sees |
| --- | --- | --- |
| Anonymized OK | ≥1 entity name + PII replaced | Per-file "Anonymized:" lines, then "PII mapping saved (N substitutions)" |
| Empty entity list | Intake/context yield no names | Yellow ⚠ warning naming the checked files and the residual risk; run continues |
| Anonymize failure | Exception on a transcript | Red ✗ "SKIPPING (raw transcript will NOT be sent)" (existing fail-closed path) |
| Deanon OK | Mapping present, all files restored | Cyan "Restoring…", green "✓ De-anonymized N file(s)"; exit 0 |
| Mapping missing | No `.pii_mapping.json` | Red ✗ "NOT client-ready" block (existing); exit 1 |
| xlsx not restorable | openpyxl import fails | Red ✗ naming each unrestored file + the fix command; `client_ready: false`; exit 1 |
| Legacy mapping | Old `[X-REDACTED]` keys on disk | Works silently — de-anonymization is key-driven |

## Error States

| Error | Cause | Message | Recovery |
| --- | --- | --- | --- |
| Empty entity list | Intake missing/unparseable | ⚠ warning above (Flow 1) | Fix `inputs/engagement_intake.md`, re-run discovery |
| xlsx unrestored | openpyxl missing in caller's env | ✗ per-file line + "pip install openpyxl and re-run …deanon" | Install dep, re-run the printed command |
| xlsx corrupt/unreadable | Bad workbook file | ⚠ "<file>: could not open workbook (<ExcType>) — NOT restored" ; `client_ready: false` | Regenerate the workbook, re-run deanon |
| Mapping missing | Pipeline never ran anonymization | Existing red "NO PII MAPPING FOUND" block | Run pipeline anonymization or pass `--mapping` |
