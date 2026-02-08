---
description: "Manually sync telemetry data to the central repository as a GitHub Issue. Use this if automatic sync via git hooks isn't set up."
---

# Sync Telemetry

Manually sync accumulated telemetry data from local engagement journals to the central GitHub repository. This creates a GitHub Issue with structured telemetry data that the Flywheel's Triage Agent will process.

## Usage

```
/sync-telemetry [engagement_directory]
```

If no directory is specified, scan the current directory and parent directories for engagement journals.

## What to Do

### Step 1: Find Telemetry Data

Look for telemetry sources in this order:
1. `.telemetry_cache.jsonl` in the repo root (accumulated by git hooks)
2. `ENGAGEMENT_JOURNAL.md` files in the specified or current engagement directory
3. `.telemetry_modifications.jsonl` (standalone modification logs)

### Step 2: Extract Telemetry

For each journal found, run the extraction:

```bash
python scripts/extract_telemetry.py [journal_path] --output /tmp/telemetry_extract.json
```

If the Python script isn't available, manually extract:
- All blocks between `<!-- TELEMETRY_START -->` and `<!-- TELEMETRY_END -->`
- All blocks between `<!-- MODIFICATION_LOG -->` and `<!-- END_MODIFICATION_LOG -->`
- Engagement metadata (domain, region, type)

### Step 3: Create GitHub Issue

Use the `gh` CLI to create a telemetry issue:

```bash
gh issue create \
  --repo [REPO_OWNER/REPO_NAME] \
  --title "[Telemetry] $(date +%Y-%m-%d) — [domain] [engagement_type]" \
  --label "telemetry" \
  --body "$(python scripts/format_telemetry_issue.py --input /tmp/telemetry_extract.json)"
```

**Important:** The repo should be the central Value Consulting AgenticOS repository, not the consultant's fork.

### Step 4: Clean Up

After successful issue creation:
- Clear `.telemetry_cache.jsonl` if it exists
- Confirm to the consultant: "Telemetry synced as GitHub Issue #[number]. The Flywheel will process it in the next triage cycle."

### Step 5: Verify

List recent telemetry issues to confirm:

```bash
gh issue list --repo [REPO_OWNER/REPO_NAME] --label telemetry --limit 5
```

## If gh CLI Not Configured

If the `gh` CLI is not authenticated:
1. Tell the consultant to run: `gh auth login`
2. As a fallback, save the telemetry to `.telemetry_cache.jsonl` for later sync
3. Explain: "Telemetry saved locally. It will sync automatically on your next `git push` once git hooks are set up. Run `./scripts/setup_telemetry.sh` to set up automatic syncing."

## Notes

- Telemetry is anonymized — no client names or sensitive data should be in the telemetry blocks
- The telemetry data feeds the Flywheel's Triage Agent, which groups similar issues across consultants
- High-frequency issues get prioritized for the Dev Agent to fix automatically
