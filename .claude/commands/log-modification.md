---
description: "Log when you manually modify an agent's output. Helps the Flywheel learn what needs improving."
---

# Log Modification

Quick command to log when a consultant manually modifies an agent's output. This data feeds into the Flywheel's autonomous improvement system.

## Usage

```
/log-modification <agent-name> <output-file> <reason> <time-spent-minutes>
```

## Example

```
/log-modification capability-assessment capability_assessment.md "Added missing APAC wealth benchmarks to 3 capabilities" 15
```

## What to Do

1. Parse the user's input to extract:
   - `agent_name`: Which agent produced the output that was modified
   - `output_file`: Which file was modified
   - `reason`: Why the modification was needed (free text)
   - `time_spent`: How many minutes the modification took

2. Calculate severity from time spent:
   - < 10 minutes → `minor`
   - 10-30 minutes → `moderate`
   - > 30 minutes → `significant`

3. Find the engagement's `ENGAGEMENT_JOURNAL.md` in the current engagement directory

4. Append this entry to the journal:

```markdown
---

### [CURRENT_TIMESTAMP] — Consultant Modification

**Modified Output:** [output_file]
**Original Agent:** [agent_name]
**Reason:** [reason]
**Time Spent:** [time_spent] minutes

<!-- MODIFICATION_LOG -->
Type: Manual Revision
Agent: [agent_name]
File: [output_file]
Reason: [reason]
Duration: [time_spent] minutes
Severity: [calculated severity]
<!-- END_MODIFICATION_LOG -->
```

5. Confirm to the consultant: "Modification logged. The Flywheel will analyze this to improve the [agent_name] agent."

## If No Journal Found

If there's no ENGAGEMENT_JOURNAL.md in the current directory or parent directories:
- Create a standalone modification log file: `.telemetry_modifications.jsonl`
- Append a JSON line with the modification data
- Tell the consultant: "No engagement journal found. Logged to .telemetry_modifications.jsonl instead."
