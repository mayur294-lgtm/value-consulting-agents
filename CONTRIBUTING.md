# Contributing to Value Consulting AgenticOS

## Owners

| Name | GitHub | Role |
|------|--------|------|
| Mayur | @mayur294-lgtm | Owner |
| Shobhit | @shobhitonnet | Owner |

## How Changes Work

### If you are an owner (Mayur or Shobhit)

- **Small changes** (typos, minor updates): push directly to `main`
- **Significant changes** (new agents, domain packs, methodology updates): create a branch, open a PR, self-merge after review
- Both workflows are valid. Use your judgment.

### If you are a contributor

1. Create a feature branch from `main`
2. Make your changes
3. Open a Pull Request
4. Mayur or Shobhit will be auto-assigned as reviewers (via CODEOWNERS)
5. One approval required to merge
6. Squash-merge into `main`

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
