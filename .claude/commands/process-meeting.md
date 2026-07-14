# Process Cortex Weekly Standup

Process a weekly Cortex team meeting transcript: produce a Change Brief, checkpoint with Mariam, execute approved changes, commit audit trail.

## Usage

```
/process-meeting
```

Then paste the transcript in the next message (or paste it inline with the command).

---

## Workflow

### Step 0 — Pre-flight: Context cost check

**Before reading anything**, report the size of files about to be loaded:

```bash
ls -la "/Users/mariamtbackbase.com/VS Code manual inputs/Cortex PM/Cortex_Context.md" \
       "/Users/mariamtbackbase.com/VS Code manual inputs/Cortex PM/"Cortex_Release_Plan_*.md 2>&1
```

Sum the file sizes. Report:
- Total KB about to be read
- Whether any file exceeds 10 KB (soft limit — flag for refactoring if so)

If total > 30 KB, **stop and ask Mariam** whether to proceed or refactor first. The whole point of this workflow is to stay bounded.

### Step 1 — Ingest transcript

The transcript is in Mariam's message. If not present, ask for it.

Save a dated archive at:
```
/Users/mariamtbackbase.com/VS Code manual inputs/Cortex PM/meetings/YYYY-MM-DD_standup.md
```

Use today's date from system context. Include a one-line header (`# Cortex Standup — YYYY-MM-DD`) above the verbatim transcript.

### Step 2 — Read context

Read in order:
1. `Cortex_Context.md` — glossary, team, concepts, standing decisions
2. Latest `Cortex_Release_Plan_*.md` — current release plan + open items
3. Query live board state:
   ```bash
   gh issue list --repo mayur294-lgtm/value-consulting-agents --state open --limit 60 \
     --json number,title,assignees,milestone,labels
   gh api repos/mayur294-lgtm/value-consulting-agents/milestones --jq '.[] | "\(.number) \(.title) — due \(.due_on) — \(.state)"'
   ```

Do NOT read prior meeting archives unless something in this week's transcript references a prior decision you can't verify from current state.

### Step 3 — Produce Change Brief

Output a structured brief covering ALL sections below. Use this exact template:

```markdown
## Change Brief — YYYY-MM-DD Standup

### Decisions made
- [Decision] (cross-ref: issue # / prior commitment)

### New commitments
| Owner | Commitment | By when |
|---|---|---|

### Status changes needed
| # | Current | New | Reason |
|---|---|---|---|

### Schedule/milestone changes
- [Specific change with date]

### New issues to create
| Title | Owner | Milestone | Body summary |
|---|---|---|---|

### Doc edits needed
| File | Section | Change |
|---|---|---|

### Open questions / ambiguities
1. [Question Mariam must answer before execution]

### Knowledge to capture in Cortex_Context.md
- [New concept / acronym / decision]
```

Save the brief to:
```
/Users/mariamtbackbase.com/VS Code manual inputs/Cortex PM/meetings/YYYY-MM-DD_change_brief.md
```

### Step 4 — Checkpoint (MANDATORY)

**STOP.** Wait for Mariam to:
- Answer open questions
- Correct anything misread
- Say "execute" (or equivalent confirmation)

**Do NOT proceed without explicit confirmation.** If she modifies the brief, update it before executing.

### Step 5 — Execute

In one pass, batched in parallel where possible:

- **Board updates** (status, dates) via GraphQL batched mutation
- **Milestone updates** (rename, due_on, state) via REST API
- **Issue moves** between milestones via REST API
- **New issues** created via REST API with proper assignees + milestone, then added to project board + dates set
- **Plan doc updated** — Edit in place. Do not append. Keep size stable.
- **Cortex_Context.md updated** — Edit in place. Curate. Size budget < 10 KB.

Use the field IDs and option IDs from prior sessions:
- Project ID: `PVT_kwHOD3TEE84BSp-9`
- Status field: `PVTSSF_lAHOD3TEE84BSp-9zhAIERg`
  - Backlog: `f75ad846` | In Progress: `47fc9ee4` | In Review: `6fa38225` | Done: `98236657`
- Start Date field: `PVTF_lAHOD3TEE84BSp-9zhAIPN4`
- Target Date field: `PVTF_lAHOD3TEE84BSp-9zhAIPQA`

### Step 6 — Report back

Concise summary:
- What changed (with issue/PR/milestone links)
- What's outstanding for the week
- New open items added to plan doc Section 4

### Step 7 — Finalize audit trail in the repo

Produce a polished public meeting record at:
```
docs/meetings/YYYY-MM-DD.md
```
(in the current worktree, NOT in main)

This is the team-readable version. Lighter than the working draft — decisions, actions, what changed. No raw transcript.

Stage, commit, and push:
```bash
git add docs/meetings/YYYY-MM-DD.md "Cortex_Release_Plan_*.md if also changed"
git commit -m "docs: archive YYYY-MM-DD standup record"
git push
```

If there is no existing PR for this worktree branch, open one. If there IS an existing PR, just push to it.

**Do NOT auto-merge.** PRs need at least one human approval per repo policy.

---

## Rules

- **NEVER skip the checkpoint** (Step 4). The workflow is worthless without it.
- **NEVER make changes Mariam hasn't approved.**
- **NEVER append to natural-language files.** Edit in place to keep size stable. If a file exceeds its budget, refactor.
- **ALWAYS report Step 0 file sizes** before reading. Catches bloat early.
- **ALWAYS query live board state from GitHub.** Don't trust file snapshots for what's currently true.
- **NEVER touch other branches** — main, mariam/WIP-*, etc. Work only on the current worktree branch unless Mariam explicitly says otherwise.
- **NEVER use `git add -A` or `git add .`** — stage by name only.
