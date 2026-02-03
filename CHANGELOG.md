# Changelog

All notable changes to Value Consulting AgenticOS are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning follows [Semantic Versioning](https://semver.org/).

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
