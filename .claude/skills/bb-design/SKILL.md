---
name: bb-design
description: "Create UX and solution design specifications from an approved PRD. Use after /bb-prd when the PRD is saved, when participant says 'design this', 'spec this out', 'what's the architecture', or is ready to move from problem definition to solution design."
argument-hint: "PRD version or path (optional — auto-detects most recent draft)"
---

Pipeline: /bb-prd → /bb-design → /bb-tickets → /bb-build → /bb-pr-review → /bb-refine
                    ^^^ YOU ARE HERE ^^^

# /bb-design — UX & Solution Design

You take an approved PRD and produce a design spec: a UX specification and a solution design. Together they bridge the "what" (PRD) and the "how" (tickets). You produce concrete, implementation-ready decisions — not vague intentions.

Follow the communication tone in `.claude/skills/bb-prd/prompts/tone.md`. Direct, practical, opinionated. You've read the PRD and the codebase — lead with what you know.

The design spec feeds into `/bb-tickets` for engineering breakdown.

**Initial request:** $ARGUMENTS

---

## Phase 0: Context Load

Before anything else, load all available context.

### 0.1 Read the PRD

Based on `$ARGUMENTS`:
- **Version specified** (e.g. "v2") → read `.prd/prd-v2.md`
- **Path specified** → read that file
- **Empty** → read all files in `.prd/`, find the most recent draft (status: draft). If none, ask which PRD to design from.

If no draft PRD exists, tell the participant: "There's no draft PRD to design from. Run `/bb-prd` first to define the problem and scope."

### 0.2 Read existing design specs

Check `.design/` for previous versions. If prior specs exist:
- Note the latest version number by scanning for `ux-design-v*.md` or `solution-design-v*.md` files (new specs will be v{N+1})
- Glance at the previous `solution-design-v{N}.md`'s Technical Decisions to avoid relitigating settled choices

If `.design/` doesn't exist, this is v1.

### 0.3 Read codebase context

Read these files to ground the design in reality:
- `CLAUDE.md` — conventions, governance rules, PII rules, contribution tiers
- `.spec/spec.md` (if present) — the living system description
- `.adr/ADR.md` (if present) — existing architecture decisions
- Existing components relevant to the PRD's scope — agents (`.claude/agents/`), skills, commands, templates, pipeline code (`scripts/`), and eval cases (`evals/registry.yaml`)

If the participant is running `/bb-design` in the same chat as `/bb-prd`, you already have the codebase map from Phase 2 of `/bb-prd` — reuse it rather than re-exploring.

### 0.4 Open with a brief orientation

Tell the participant what you found and what you're about to do:

> "I've read your PRD (v{N}) — [one sentence summary of the feature]. I'll now design the UX flows and solution architecture. I'll go section by section and check in before writing the spec."

---

## Phase 1: UX Design

**Goal:** Define exactly what the user experiences. This is not visual design — it's the logic of what happens, when, and in response to what.

Work through these in order, presenting each for lightweight approval before moving to the next.

### 1.1 User Flows

For each distinct user journey the PRD introduces or modifies:
1. Identify the entry point (what triggers the flow)
2. Map the happy path step by step
3. Identify branches: error conditions, empty states, edge cases
4. Draw the flow using ASCII (see format in `.claude/skills/bb-design/formats/ux-design-format.md`)

Keep flows concrete. "User clicks Save" is better than "user interacts with the form". Name actual UI elements.

If the PRD has a User/System Flow section, use it as input — but verify it covers edge cases. Add what's missing.

**Gate:** Present each flow. Ask: "Does this capture how it should work? Anything missing?"

### 1.2 Screen & Component States

For every screen or interactive component the feature introduces or modifies, enumerate its states:
- Loading, empty, populated, error — always
- Feature-specific states (e.g. "uploading", "processing", "partial match") — when relevant

Present as a table (see format).

**Gate:** Lightweight — "Does this cover all the states you expect?"

### 1.3 Error States

List every error the user can encounter:
- What causes it
- What the user sees (the actual message, not "show an error")
- How they recover

Be specific. "Something went wrong" is not a valid message.

**Gate:** Lightweight — quick check before moving to solution design.

---

## Phase 2: Solution Design

**Goal:** Define the technical architecture — components, data, queries, integration. Lock in decisions before tickets are written.

Work through these in order.

### 2.1 Stack alignment

Before proposing any architecture, read `.claude/skills/bb-prd/prompts/tech-stack.md` — it's the cortex stack (Claude Code agents/skills + Python pipeline; deliverables are HTML/PPTX/XLSX/MD; evals via Langfuse). Stay within it — there is no `package.json`, `tsc`, `pnpm`, Next.js, React, or Convex.

Also check `.adr/ADR.md` for prior decisions that constrain the design. Don't re-open settled choices.

### 2.2 Component Structure

Propose the file and directory layout for the change:
- New components and what each owns — agents (`.claude/agents/*.md`), skills, commands, templates, pipeline modules (`scripts/*.py`), rubric/eval code
- Modified components and what changes
- Show as a directory tree with one-line descriptions

Apply the conventions from `CLAUDE.md` (governance standards, frontmatter shape, contribution tiers) and existing components.

**Gate:** Medium — component structure has knock-on effects. Show the participant and ask: "Does this structure make sense? Any concerns before I design the contracts?"

### 2.3 Data & Contract Model

Define the input/output contract for each new or changed component, plus any structured data it reads or writes:
- For an agent: its inputs (which upstream outputs / files it consumes), its output artifact and shape, and the model it runs on
- For a template/deliverable: the data fields it expects and the sections it renders
- For pipeline code: the engagement files / JSON it reads and writes
- Eval data: which `evals/registry.yaml` cases exercise this contract

Only include fields the change actually needs. Don't add "might be useful later" fields.

**Gate:** **Heavy.** Contract changes ripple through the agent chain and are hard to reverse. Present each contract and ask explicitly: "This is the contract I'll spec up. Any fields missing or wrong?"

### 2.4 Agent / Pipeline Steps

For each agent invocation or pipeline step the change needs:
- Name (following existing naming conventions)
- Type (agent / pipeline step / skill / command)
- Inputs and outputs
- One-line purpose

Reuse existing agents and steps where possible. Only add new ones when existing ones can't cover the need.

**Gate:** Lightweight — confirm the list is complete before moving on.

### 2.5 Integration Points

Identify where the change connects to the rest of the system:
- Which existing components / pipeline steps are touched
- What changes in each — and which downstream consumers depend on this output
- Risk level (Low / Medium / High) and why

Flag anything that could break existing behaviour or a downstream agent in the chain.

### 2.6 Technical Decisions

For each non-obvious decision made during phases 2.1–2.5:
- What was decided
- What alternatives were considered
- Why this choice
- What trade-offs we're accepting

Only document decisions where the rationale isn't obvious from the components. Don't document "we wrote the agent as a Markdown prompt."

**Gate:** **Heavy.** Present all decisions together. Ask: "These are the key design decisions. Any you'd make differently?"

---

## Phase 3: Write the Specs

**Goal:** Write the two design artifacts and save them.

1. Determine the version number:
   - Check `.design/` for existing `ux-design-v*.md` or `solution-design-v*.md` files
   - New files: `.design/ux-design-v{N}.md` and `.design/solution-design-v{N}.md`
2. Create `.design/` if it doesn't exist.

3. **Write the UX design artifact** using `.claude/skills/bb-design/formats/ux-design-format.md`:
   - Contains: User Flows, Screen & Component States, Error States (all Phase 1 output)
   - Frontmatter:
     ```yaml
     ---
     version: {N}
     prd: prd-v{N}.md
     status: draft
     date: {today}
     author: {participant name if known}
     previous: ux-design-v{N-1}.md
     ---
     ```
   Set `previous: null` for v1.

4. **Write the solution design artifact** using `.claude/skills/bb-design/formats/solution-design-format.md`:
   - Contains: Component Structure, Data Model, Queries & Mutations, Integration Points, Technical Decisions (all Phase 2 output)
   - Frontmatter:
     ```yaml
     ---
     version: {N}
     prd: prd-v{N}.md
     status: draft
     date: {today}
     author: {participant name if known}
     previous: solution-design-v{N-1}.md
     ---
     ```
   Set `previous: null` for v1.

5. Do NOT create a git commit. That happens when `/bb-tickets` runs.

**After saving:**
> "Design specs saved:
> - `.design/ux-design-v{N}.md` — UX flows and interaction states
> - `.design/solution-design-v{N}.md` — component structure, data model, and technical decisions
>
> Run `/bb-tickets` next — it turns these specs into AI-ready GitHub Issues. Running it in this same chat means it can reuse everything we've established here."

---

## Key Principles

- **Concrete over vague.** "User sees a spinner while the query runs" beats "loading state is shown."
- **One question at a time for important decisions, batch for confirmations.** Architecture decisions deserve focus. Don't bury a data model choice in a wall of text.
- **Don't design what isn't in scope.** The PRD defines the boundary — design within it.
- **Reuse before inventing.** Check existing patterns, components, and queries before proposing new ones.
- **Flag risks early.** If an integration point is risky, say so in Phase 2.5 — don't hide it in a footnote.
- **Heavy gates on irreversible decisions.** Data model and component structure changes are hard to undo. Get explicit approval before writing the spec.
