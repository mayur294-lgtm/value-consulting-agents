# The Flywheel: Self-Improving Value Consulting AgenticOS

The Flywheel is the autonomous improvement system for VC AgenticOS. It tracks how consultants use the system, identifies problems, builds fixes, and delivers them — with human approval before anything ships.

## How It Works

```
Consultant uses system → Telemetry logged automatically
     ↓
Engagement ends → Detected automatically (zero human action):
  Layer 1: Orchestrator runs gh issue create directly
  Layer 2: Post-commit hook detects all 5 output files → syncs immediately
  Layer 3: Pre-push hook syncs any cached telemetry
     ↓
Telemetry issue created (label: "telemetry")
     ↓
Triage Agent (REACTIVE) → Triggers immediately on new telemetry issue
                           (also runs weekly as a catch-all)
     ↓
Groups duplicates, scores by frequency × severity
     ↓
Labels top issue "ready-for-dev"
     ↓
Dev Agent (event-triggered) → Analyzes root cause, implements fix
     ↓
Test Agent → Quality checks (structural validation)
     ↓
Review Agent → Code review (approach validation)
     ↓
PR created → Email sent to mayur@backbase.com
     ↓
Mayur approves on GitHub
     ↓
Release Agent → Merge, tag, release notes email to vc@backbase.com
```

### Engagement Completion Detection (Zero Human Action)

The system detects engagement completion passively. No consultant command, no manual sync, no `/close-engagement`. Three independent layers ensure telemetry reaches the Flywheel:

| Layer | How it detects completion | When it fires |
|-------|--------------------------|---------------|
| **Primary** | Orchestrator finishes Step 7 review, runs `gh issue create` in Step 8c | Immediately at end of engagement |
| **Backup** | Post-commit hook sees all 5 output files exist in an engagement dir | On next git commit |
| **Fallback** | Pre-push hook drains `.telemetry_cache.jsonl` | On next git push |

**Completion markers** (what the post-commit hook looks for):
- `executive_summary.md` + `assessment_report.md` + `roi_report.md` + `roadmap.md` + `capability_assessment.md` all present in the same engagement directory
- A `.telemetry_synced` marker prevents double-syncing the same engagement

## The Agent Team

| Agent | Role | Trigger | Cost |
|-------|------|---------|------|
| **Triage Agent** | Groups and prioritizes telemetry issues | Weekly cron | $0 (Python) |
| **Dev Agent** | Implements fixes | `ready-for-dev` label | ~$5-15 (API) |
| **Test Agent** | Validates changes structurally | After Dev Agent | $0 (Python) |
| **Review Agent** | Code reviews changes | After Test Agent | ~$2-5 (API) |
| **Release Agent** | Handles releases and notes | PR merge | $0 (Python) |
| **Coach Agent** | Sends productivity tips to consultants | Monthly | ~$2-5 (API) |

## For Consultants

### One-Time Setup

```bash
# From your local VC AgenticOS directory:
./scripts/setup_telemetry.sh
```

This configures the `gh` CLI for telemetry sync. After setup, **everything is automatic**:
- The orchestrator syncs telemetry to GitHub at the end of every engagement
- No git push needed — it uses `gh issue create` directly
- Git hooks provide a backup sync on push (if the orchestrator sync fails)

### Optional: Log Manual Modifications

If you manually edit an agent's output, log it so the system can learn:

```
/log-modification <agent-name> <file> <reason> <minutes-spent>
```

Example:
```
/log-modification capability-assessment output.md "Missing APAC benchmarks" 15
```

### Optional: Manual Telemetry Sync

If automatic sync isn't working:

```
/sync-telemetry
```

## For Mayur (Approver)

### Approval Flow

1. You receive an email from the Flywheel when a PR is ready
2. The email shows: problem, evidence, solution, risk level, quality gate results
3. Click "Review Pull Request" to open GitHub
4. Review the changes and either Approve or Request Changes
5. On approval + merge, release notes are automatically emailed to vc@backbase.com

### What You Control

- **Approval threshold**: Only YOU can merge PRs. Nothing ships without your review.
- **Frequency**: The Dev Agent only runs when issues exist. No spam.
- **Scope limits**: The Dev Agent can only modify agent definitions, knowledge files, and templates. It cannot change scripts, workflows, or core configuration.

## GitHub Infrastructure

### Labels

| Label | Purpose |
|-------|---------|
| `telemetry` | Raw telemetry from consultant engagements |
| `improvement` | Deduplicated improvement items |
| `ready-for-dev` | Triggers the Dev Agent |
| `dev-agent` | PRs created by the Dev Agent |
| `needs-review` | Awaiting Mayur's approval |
| `needs-human-review` | Escalated — too complex for automation |

### Workflows

| Workflow | File | Trigger |
|----------|------|---------|
| Triage Agent | `triage-weekly.yml` | Telemetry issue created (reactive) + weekly cron (catch-all) |
| Dev Agent | `dev-agent.yml` | `ready-for-dev` label applied |
| Test Agent | `test-agents.yml` | PRs modifying agents/knowledge |
| Release | `version-release.yml` | Git tag pushed |

### Secrets Required

| Secret | Purpose |
|--------|---------|
| `ANTHROPIC_API_KEY` | Dev Agent + Review Agent API calls |
| `EMAIL_USERNAME` | SMTP for sending emails |
| `EMAIL_PASSWORD` | SMTP app password |

## Cost

- **$0** when no issues exist (no scheduled API calls)
- **~$7-20** per issue processed (Dev Agent + Review Agent)
- **~$14-80/month** with typical 2-4 issues/week
- All non-LLM components run for free (Python + GitHub Actions)

## File Map

```
scripts/
  extract_telemetry.py     — Parse journal → JSON
  format_telemetry_issue.py — Format telemetry as GitHub Issue
  aggregate_issues.py      — Triage: dedup + score + prioritize
  dev_agent.py             — Dev Agent orchestrator
  review_agent.py          — Review Agent orchestrator
  test_agent.py            — Quality check runner
  render_email.py          — HTML email renderer
  parse_changelog.py       — CHANGELOG → release data
  setup_telemetry.sh       — One-time consultant setup
  setup_github_project.sh  — One-time board setup

.claude/agents/
  dev-agent.md             — Dev Agent system prompt
  review-agent.md          — Review Agent system prompt
  release-agent.md         — Release Agent system prompt
  coach-agent.md           — Coach Agent system prompt

.claude/commands/
  log-modification.md      — /log-modification skill
  sync-telemetry.md        — /sync-telemetry skill

.github/workflows/
  triage-weekly.yml        — Weekly triage cron
  dev-agent.yml            — Event-triggered dev workflow
  test-agents.yml          — PR quality guard
  version-release.yml      — Release + email pipeline

.githooks/
  post-commit              — Extract telemetry on commit
  pre-push                 — Sync telemetry on push

templates/emails/
  approval_request.html    — PR approval email template
  release_notes.html       — Release announcement email

tests/
  quality_metrics.yaml     — Structural quality checks
```
