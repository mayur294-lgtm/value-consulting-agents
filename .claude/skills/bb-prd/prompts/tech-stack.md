# Cortex Stack

Cortex is a consulting-deliverable generation system, not a web application. Its "code" is prompt-based AI agents and skills plus a Python orchestration pipeline. Design every PRD and solution against this stack.

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Components | Claude Code agents (`.claude/agents/*.md`), skills (`.claude/skills/*/SKILL.md`), slash commands (`.claude/commands/*.md`) | The system's behaviour lives in prompts with YAML frontmatter (name, description, model, color) |
| Orchestration | Python 3.11 pipeline — `scripts/orchestrate.py`, `scripts/*.py` | Deterministic engine that drives the agent chain (Discovery → Block-A agents → Roadmap → Assembly → HTML → Excel → Validation) |
| Output templates | `templates/**`, `presentations/**` | Reusable scaffolds for deliverables |
| Deliverables | Self-contained HTML dashboards/decks, PPTX, XLSX ROI models, Markdown reports | Executive-ready consulting outputs — NOT a deployed app |
| Quality / evals | Langfuse-scored eval harness at `evals/` (`python evals/run_experiment.py`) + structural checks (`python scripts/test_agent.py`) | "Done" is defined by eval thresholds and structural validation, not by tests/typecheck |
| Visual system | Frontline-2026 (`knowledge/design-system.md`, `presentations/frontline-2026/design-tokens.json`) | All visual outputs must conform |

## Rules

- **There is NO `package.json`, `tsc`, `pnpm`, Next.js, React, Convex, or Tailwind.** Do not propose any of them. If a PRD idea seems to need a web app, restate it as a deliverable or a pipeline/agent change.
- **Default to editing components.** A change is almost always: edit an agent definition, a skill, a command, a template, or rubric/eval code — and update `evals/registry.yaml`.
- **Respect governance.** Every agent must comply with the Mandatory Governance Standards (journal, telemetry, dual checkpoints, evidence tracing, provenance) — see `CLAUDE.md`.
- **Respect contribution tiers.** Agents/skills/tools/templates are Architect-only; consultants contribute knowledge. Note the tier impact in the PRD when relevant.

## When This Stack Doesn't Fit

If a participant genuinely needs something outside this stack, note it explicitly in the PRD with a brief reason — but the default is always the cortex agents/skills/pipeline model above.
