# Contributing to Value Consulting AgenticOS

## Contribution Tiers

This project has two contribution tiers. The CI workflow `enforce-contribution-scope.yml` enforces these automatically.

### Architects

Architects design and maintain the system — agents, skills, tools, workflows, and methodology.

| Name | GitHub | Role |
|------|--------|------|
| Mayur | @mayur294-lgtm | Architect |
| Shobhit | @shobhitonnet | Architect |

**Can modify:** Everything — agents, skills, commands, tools, workflows, CLAUDE.md, templates, knowledge, benchmarks

### Domain Leads

Domain Leads are consultants who own a specific area and can modify files within that domain — including agents, tools, and templates scoped to their domain. Their changes still require architect review before merging.

| Name | GitHub | Domain | Additional Access |
|------|--------|--------|-------------------|
| Mariam | @mariamt-coder | **ROI** | `roi-business-case-builder.md`, `tools/roi_excel_generator.py`, `templates/outputs/roi*` |

**Important for Domain Leads:** When you pull the latest code, your domain files may have new sections (e.g., consultant checkpoints). When resolving conflicts, **merge both sides** — keep your improvements AND the new sections. Don't just pick "your version" wholesale.

### Consultants

Consultants use the system for engagements and contribute learnings back.

**Can modify:**
- `knowledge/learnings/**` — extracted benchmarks, pain points, maturity scores, ROI patterns
- `knowledge/domains/**` — domain knowledge expansions (new personas, journeys, use cases)
- `benchmarks/**` — benchmark data corrections and additions

**Cannot modify (PR will be blocked by CI):**
- `.claude/agents/**` — agent definitions (except Domain Lead exceptions above)
- `.claude/commands/**` — skills and slash commands
- `.claude/hooks/**` — git hooks and automation
- `tools/**` — Python code (except Domain Lead exceptions above)
- `.github/**` — CI/CD workflows
- `scripts/**` — automation scripts
- `CLAUDE.md` — root configuration
- `templates/outputs/**` — output templates (except Domain Lead exceptions above)
- `agents/definitions/**` — agent role definitions

**If a consultant needs to suggest changes to restricted paths:** Open an issue describing the change, and an architect will implement it.

## How Changes Work

### If you are an architect

- **Small changes** (typos, minor updates): push directly to `main`
- **Significant changes** (new agents, domain packs, methodology updates): create a branch, open a PR, self-merge after review
- Both workflows are valid. Use your judgment.

### If you are a consultant

The system handles git for you — you never need to run git commands manually.

1. **Start a session** — Claude Code auto-creates a feature branch for you
2. **Do your work** — edit knowledge files, run engagements, extract learnings
3. **Publish** — say "publish my changes" or run `/publish`. Claude commits, pushes, and creates a PR.
4. **Review** — an architect reviews and merges your PR

**Knowledge harvest is enforced:** If your branch contains engagement outputs but no `knowledge/learnings/` entries, `/publish` will block and ask you to run the knowledge harvest first. This ensures every engagement makes the system smarter.

## The Knowledge Learning Loop

After every engagement, the system should extract reusable knowledge:

```
Engagement Complete
  → Orchestrator Step 9: Knowledge Harvest (automatic)
  → Extracts: benchmarks, pain points, maturity scores, ROI patterns
  → Anonymizes: client names → [Client-{domain}-{region}-{YYYY}]
  → Writes to: knowledge/learnings/{category}/
  → Updates: EXTRACTION_REGISTRY.md
  → /publish enforces: no engagement outputs without harvest entries
  → PR reviewed by architect
  → Merged to main
  → Next engagement uses improved knowledge
```

**Manual fallback:** If Step 9 didn't run (e.g., session ended early), consultants can run:
- `/scan-engagement` — identifies extractable knowledge
- `/extract-learnings` — extracts and writes structured knowledge

## Branch Naming

Use these prefixes so it's clear what type of change a branch contains:

| Prefix | Use for | Example |
|--------|---------|---------|
| `content/` | Knowledge packs, domain data, templates | `content/add-wealth-domain` |
| `update/` | Agent changes, methodology updates | `update/discovery-agent-chunking` |
| `fix/` | Corrections, broken references, typos | `fix/roi-formula-rounding` |
| `tool/` | Python tools, slash commands, skills | `tool/excel-generator-v2` |
| `workflow/` | Git process, CI/CD, infrastructure | `workflow/add-linting` |

**Examples:**
```bash
git checkout -b content/add-corporate-domain
git checkout -b update/orchestrator-journal-protocol
git checkout -b fix/quickstart-broken-link
git checkout -b tool/presentation-dark-mode
```

## Commit Messages

Use this format:

```
type: short description

Optional longer explanation of what changed and why.
```

**Types:**
- `add` — new content, agents, tools, domains
- `update` — changes to existing content or behavior
- `fix` — corrections and bug fixes
- `remove` — deleting content or features
- `docs` — documentation-only changes
- `tool` — changes to Python tools or slash commands

**Examples:**
```
add: wealth management domain pack with personas and journeys

update: discovery agent with chunking protocol for large transcripts

fix: ROI formula using wrong discount rate in year 3

remove: deprecated benchmark sources from 2022

docs: rewrite QUICKSTART for consultant onboarding
```

## Versioning

We use [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

| Change type | Version bump | Example |
|-------------|-------------|---------|
| Breaking changes to agent contracts or template structure | MAJOR | 2.0.0 |
| New domains, agents, skills, or significant methodology updates | MINOR | 1.1.0 |
| Fixes, typos, small content corrections | PATCH | 1.0.1 |

### Creating a Release

After merging significant changes:

```bash
# 1. Update CHANGELOG.md with what changed
# 2. Update VERSION file with new version number
# 3. Commit those changes

# 4. Tag and push
git tag -a v1.2.0 -m "Short description of this release"
git push origin main --tags

# 5. GitHub Release is auto-created by the workflow
```

### Rolling Back

```bash
# See all versions
git tag -l

# View what's in a version
git log v1.0.0..v1.1.0 --oneline

# Rollback to a specific version
git checkout v1.0.0

# Create a fix branch from an old version
git checkout -b fix/rollback-issue v1.0.0
```

## What NOT to Commit

These are excluded by `.gitignore`:

- **Client engagement data** (`engagements/` folder) — confidential
- **`.DS_Store`** and OS metadata
- **`.claude/settings.local.json`** — personal Claude Code settings
- **`__pycache__/`** and Python build artifacts
- **`*.webloc`** and temp files

If you need to share engagement examples, sanitize all client data and place them in `examples/`.

## Pull Request Guidelines

When opening a PR, fill out the template:
- Summarize the change in 1-3 bullets
- Check the type of change
- List key files modified
- Confirm the checklist items

## Quality Standards

All contributions must follow the standards in [README.md](README.md):
- Evidence-based, conservative, transparent
- Executive-ready language
- Assumptions documented
- No vendor-led or marketing language

## Questions?

Open an issue or reach out to @mayur294-lgtm or @shobhitonnet.
