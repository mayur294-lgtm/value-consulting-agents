# Changelog

All notable changes to Value Consulting AgenticOS are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.3.0] - 2026-05-05 — Backbase Unified Frontline 2026 design system migration

Replaces the ENGAGE Americas 2026 palette with the **Backbase Unified Frontline 2026** brand system (colors + typography). Layouts, dashboard components, and agent behavior are unchanged — only the visual tokens and a new pair of presentation skills.

### Added

- **`/frontline-html` skill** — single-file HTML deck builder using `tools/frontline_2026_html.py`. Keyboard + dot navigation, 17 slide layouts (Cover, Section Divider, Agenda, Content, Split Comparison, Showcase, Architecture, Stat Cards, Case Study, Statement, Tiles, Process Rows, Pillar Rows, Financial Table, Alert Cards, Architecture Stack, Context Stats). For brainstorming and previewing decks before final PPTX.
- **`/frontline-slides` skill** — Google-Slides-compatible PPTX builder using `tools/frontline_2026_presenter.py`. 20"×11.25" canvas, 15% text-width buffer, autofit disabled, Libre Franklin throughout, no gradients/shadows/rotated text.
- **`presentations/frontline-2026/`** — design tokens (`design-tokens.json`), layout positions (`slide-layouts.md`), Google Slides compat rules (`google-slides-rules.md`), and HTML component catalog (`html-components.md`).
- **Brand chrome patterns** in `knowledge/design-system.md` Section 5: blue inverted-L corner accent (top-left of light panels) + Backbase wordmark footer (bottom-right with notched-B SVG + page number).

### Changed (visual only — no functional changes to agents)

- **Brand palette** swapped repo-wide:
  - Primary dark: `#0F172A` → `#001C3D` (Frontline navy)
  - Primary blue: `#3366FF` → `#1A5AFF` (Action Blue)
  - Coral → Semantic Red: `#FF6B5E` → `#E02020`
  - Sage → Success Green: `#93C47D` → `#2ECC71`
  - Gold → Amber: `#E8B931` → `#D97706`
  - Muted: `#334155` → `#5C6E84`
  - Off-white body bg: `#F8FAFC` → pure white `#FFFFFF`
- **Primary font**: Inter → **Libre Franklin** (Google Fonts)
- **Card radius**: 12px → 16px (Frontline standard); pill buttons 30px
- **Maturity scale L0–L4** rebuilt on new palette — gold removed, replaced by amber for L1
- `knowledge/design-system.md` rewritten — Sections 1–4 (tokens, deprecation map, typography, CSS vars) updated; Sections 5–7 (layout patterns, components, breakpoints) retain bento grids, dark feature sections, heatmaps, swimlanes, phone frames, journey maps, value waterfalls — all auto-inherit new colors
- Agent line-17 color hint updated in 5 agent files (`workshop-preparation`, `usecase-designer`, `ignite-workshop-synthesizer`, `roi-financial-modeler`, deprecated `roi-business-case-builder` left as-is)
- 17 templates re-skinned: `templates/presentations/*.html`, `knowledge/Ignite Inspire/*-template.html`, `knowledge/Ignite Inspire/example-*-deck.html`, `knowledge/Ignite Inspire/agent-[0-6]-*.md`, `knowledge/Ignite Inspire/design-system.md`, `knowledge/Ignite Inspire/CLAUDE.md`
- Web app: `web/src/index.css`, `web/src/data/mockData.ts`, `web/src/pages/Pipeline.tsx`, all `web/ontology*.html`
- Standalone outputs re-skinned: `Cortex_Sales_ROI_Calculator.html`
- `CLAUDE.md` "Custom Skills Available" section now documents `/frontline-html` and `/frontline-slides` (replaces `/presentation` documentation)

### Deprecated

- **`/presentation` and `/presentation-v2` skills** — moved to `.claude/commands/deprecated/`. Both now display a deprecation banner pointing to `/frontline-html` (preview) and `/frontline-slides` (final PPTX). Kept on disk only so historical engagements that linked to them still resolve.

### Migration notes

- Existing engagement outputs in `outputs/` and `engagements/*/` are intentionally NOT retroactively re-skinned — they are historical deliverables and should remain as published.
- Agents read `knowledge/design-system.md` at runtime; future generations automatically pick up Frontline 2026 tokens.
- Re-skin script: `/tmp/reskin_frontline2026.py` (idempotent; safe to re-run on any HTML/CSS/MD file).

---

## [1.2.0] - 2026-04-13

Major release covering 45 commits since v1.1.0 (Feb 3 → Apr 13). Three headline themes:
**(1)** comprehensive security hardening + PII anonymization, **(2)** ROI pipeline v2 — two-agent architecture with hypothesis-driven lever identification, **(3)** ENGAGE Americas 2026 design system refresh (colors + font).

### Security & Privacy

- **PII anonymization pipeline** (`scripts/anonymize_transcript.py`) — strips client names, person names, emails, phone numbers, SSNs, account numbers, and client URLs from transcripts before they are sent to the Anthropic API. Round-trip de-anonymization restores real names in final deliverables. Wired automatically into `step_discovery()` in orchestrator; agent prompts also instructed to invoke it when run standalone.
- **Prompt injection defense protocol** (`knowledge/standards/security_protocol.md`) — 8-section mandatory standard covering untrusted data handling, web search validation, MCP query anonymization (no client names/financials in Backbase MCP queries), tone calibration bounds, unconsidered needs validation, and checkpoint security tables.
- **14 code-level security vulnerabilities fixed** across 8 files:
  - **Critical:** Removed credential from git URL (orchestrate.py) — now uses `GIT_ASKPASS` helper. Added path traversal protection to dev_agent.py with `REPO_ROOT` sandboxing — blocks absolute paths, `../` traversal, `.git/`, and `.github/workflows/` writes.
  - **High:** LLM response schema validation, CI/CD input sanitization (`ACTIONS_STEP_DEBUG: false`), `.env` added to `.gitignore`, retry-with-exponential-backoff for GitHub API.
  - **Medium/Low:** Configurable repo owner/name via env vars, sanitized error messages, GitHub API token validation, `chmod 600` on `.env`.
- **Security protocol referenced** by 9 agent files (discovery, market-context, narrative-assembler, workshop-prep, journey-builder, capability-assessment, roi-business-case-builder, roi-financial-modeler, roi-hypothesis-builder) plus `CLAUDE.md` governance table.

### Added

- **ROI Pipeline v2** — two-agent architecture: `roi-hypothesis-builder` (defines problem, builds hypothesis tree, derives lever candidates) and `roi-financial-modeler` (receives validated levers, computes gap-based impacts, builds financial model). Orchestrated by new `/build-roi` skill outside the full pipeline.
- **Hypothesis-driven lever identification** with three new methodology docs: `value_lever_framework.md`, `hypothesis_tree_decomposition.md`, `capability_driven_patterns.md`.
- **Gap-based `backbase_impact` methodology** — replaces static ranges with capability-gap-driven calculation. Capped at 60% to prevent inflated ROI ([Client-creditunion-NAM-2025] root cause).
- **Knowledge harvest auto-runs without token** — silent post-pipeline PR flow, zero consultant setup required. Engagement-level knowledge writes back to shared knowledge base via auto-opened harvest PR.
- **Two-phase agent protocol** — phased execution with checkpoint files, context reduction, pipeline hardening (per-agent timeouts, 3-way sharding for capability heatmap).
- **Journey Experience Map pipeline** — two-layer pipeline with strengthened checkpoint enforcement.
- **Lifecycle-stage capability heatmap** — new `02e` lifecycle pipeline architecture.
- **`/build-roi` skill** — standalone orchestrator for the new two-agent ROI architecture.
- **`/generate-roi-questionnaire` skill** — Phase A questionnaire generation, separated from the calculation engine.
- **Mariam promoted to architect** — full path access granted.
- **[Client-investing-NAM-2026], [Client-retail-APAC-2026], and Managed Hosting Commercial test suites** added under `tests/` — fixture transcripts + expected outputs for ROI pipeline regression testing.
- **ROI Pipeline Redesign Presentation** (`tests/roi_pipeline_v2/ROI_Pipeline_Redesign_Presentation.html`).

### Changed

- **Design System refreshed to ENGAGE Americas 2026 keynote palette:**
  - Primary dark: `#091C35` → `#0F172A` (darker, more neutral navy)
  - Primary blue: `#3366FF` (unchanged — verified against keynote slides 7, 9, 10)
  - Red/Coral: `#FF7262` → `#FF6B5E` (warmer)
  - Green: `#26BC71` → `#93C47D` (vibrant → muted sage)
  - Amber: `#FFAC09` → `#E8B931` (amber → gold)
  - Background: `#F5FAFF`/`#F8FAFC` → `#FFFFFF` (pure white base)
  - Primary font: Libre Franklin → **Inter** (geometric, uniform strokes — matches keynote)
  - All deprecated colors documented in `knowledge/design-system.md` migration table.
- **ROI agent split:** old monolithic `roi-business-case-builder.md` deprecated and preserved at `.claude/agents/deprecated/`. New two-agent split is canonical.
- **Phase A questionnaire converted from agent to skill** (`/generate-roi-questionnaire`) — universal across all engagement types.
- **Phase B always routes to Mariam's calculation engine** (`roi-financial-modeler`).
- **Orchestrator slimmed** — `value-consulting-orchestrator` agent reduced to thin router; logic moved to `scripts/orchestrate.py`.
- **`orchestrate_v4.py` consolidated into `orchestrate.py`** — single canonical orchestrator.
- **V5 pipeline** — 3-way sharding, per-agent timeouts, HTML template optimization.
- **`<checkpoint>` tag instructions** added to all 9 agent prompts.
- **"Read the Room" tone calibration protocol** added across 4 agents — direct/measured/opportunity-framed framings without changing conclusions.
- **Consultant Interaction Model** renamed to **Consultant Checkpoint** (market-context-researcher).

### Removed

- **Cyan** (`#69FEFF`) and **Purple** (`#7B2FFF`) — no longer in Backbase brand palette.
- **`html_report_generator.py`** — replaced by `/generate-assessment-html` skill.

### Fixed

- **Knowledge harvest token requirement** — pipeline now runs without it; harvest is best-effort.
- **Systemic ROI bugs:** investment lever calculation, scenario switching, calibrator integration.
- **ROI agent ↔ assembler ↔ HTML dashboard data contracts** synced.
- **`backbase_impact` cap at 60%** — prevents inflated ROI seen in [Client-creditunion-NAM-2025] engagement.
- **Flywheel quality check failures** — binary file skip in test agent, bash syntax error in workflow, `.md`-only filter for changed files in CI.
- **Post-commit hook** — resolves `outputs/` subdirectory to engagement root.
- **V4 version label** removed from orchestrator banner.
- **ROI routing** — Phase A questionnaire universal, Phase B always Mariam's engine.

### Infrastructure

- **CI gating tightened** — `check-scope` enforces contribution tier permissions on every PR.
- **Test agent** validates agent definition structure on every PR.
- **`.gitignore`** expanded to exclude `.env`, `.env.local`, `.git_askpass.sh`, `.pii_mapping.json`, `.anon_*` artifacts.

---

## [1.1.0] - 2026-02-03

### Added
- Git infrastructure: `.gitignore`, CODEOWNERS, PR template, GitHub Actions workflows
- `CONTRIBUTING.md` with branching conventions, commit format, and versioning workflow
- `CHANGELOG.md` for release tracking
- `VERSION` file for machine-readable version
- Context management protocol (`knowledge/standards/context_management_protocol.md`)
- Engagement Journal template (`templates/outputs/engagement_journal.md`)
- `requirements.txt` for Python dependencies
- Push notification workflow (GitHub Actions)
- Version release workflow (GitHub Actions)

### Changed
- Renamed project to **Value Consulting AgenticOS**
- Rewrote `QUICKSTART.md` as practical consultant onboarding guide with setup instructions, transcript handling, slash command reference, and engagement workspace setup
- Updated all 6 core agents (Discovery, Capability, ROI, Roadmap, Assembly, Orchestrator) with:
  - Context management protocol reference
  - Mandatory engagement journal entries
  - Disk-based handoff rules (agents read upstream outputs, never raw transcripts)
  - Large file chunking protocol
- Updated Orchestrator with engagement journal lifecycle management and multi-transcript sequential processing
- Updated Discovery agent with automatic file size detection and chunking thresholds

### Removed
- Tracked `.DS_Store` files from repository

## [1.0.0] - 2026-02-03

### Added
- 10 specialized agents: Orchestrator, Discovery, Capability Assessment, ROI Builder, Roadmap, Executive Assembler, Workshop Preparation, Workshop Synthesizer, Use Case Designer, Benchmark Librarian
- 11 slash commands: `/presentation`, `/prototype`, `/generate-roi-excel`, `/usecase-doc`, `/chunk-document`, `/domain-context`, `/domain-benchmarks`, `/domain-pain-points`, `/domain-journeys`, `/domain-usecases`, `/domain-value-props`
- 5 domain knowledge packs: retail, SME, commercial, corporate, wealth
- Ignite Inspire workshop system with 7 specialized agents
- Complete example engagement (retail bank, Southeast Asia)
- Output templates: executive summary, assessment report, capability assessment, ROI report, roadmap
- Input contracts: discovery input, financial data schema, transcript interpretation guide
- Python tools: ROI Excel generator, HTML report generator
- Core documentation: README.md (philosophy), CLAUDE.md (agent behavior), QUICKSTART.md, STRUCTURE.md
- Consulting knowledge base: principles, methodologies, standards
- Competitor intelligence and discovery question bank
- Backbase platform lexicon
