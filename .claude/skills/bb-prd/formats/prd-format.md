# PRD Template

Use this template when writing PRDs in Phase 4 of `/bb-prd`. Core sections are always included. Optional sections are added based on what was learned during discovery and exploration.

---

## Core Sections (always include)

### 1. Problem
What problem does this solve? Who has this problem? What happens if we don't solve it?

### 2. Solution
One-paragraph summary of what we're building. What does it do, at the highest level?

### 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| ... | ... |

### 4. Success Metrics

| Metric | Target |
| --- | --- |
| ... | ... |

Metrics should be verifiable — either observable in the deliverable or measurable by the eval harness (rubric scores, structural checks, pipeline correctness).

### 5. Eval Acceptance Criteria (mandatory for any component change)

For any PRD that changes a cortex component (agent, skill, command, template, rubric, or pipeline code), define what "done" means in eval terms. **No component PRD is complete without this section.**

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| ... | ... | ... | unit / pipeline / deliverable |

- Name the existing registry cases (and thresholds) that must stay green.
- **For a NEW component:** fresh eval cases MUST be authored as part of this work — list the cases to add and their target thresholds.
- State whether the change can affect downstream consumers; if so, the deliverable-structural-altitude experiment must stay green (it lints output-file contracts; it does not run the pipeline).

### 6. Out of Scope
Explicit list of things this PRD does NOT cover. Prevents scope creep during implementation.

---

## Optional Sections (include when relevant)

### User/System Flow
Include when the feature is user-facing. Step-by-step flow of what the user sees/does, or what the system does in response to events.

```
Step 1 → Step 2 → Step 3
  │         │
  ▼         ▼
 ...       ...
```

### Dependencies & Risks
Include when external dependencies were detected during codebase exploration, or when the feature depends on things outside our control.

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| ... | ... | ... |

### Testing Strategy
Include when the feature needs cross-platform testing, has complex integration points, or when the testing approach isn't obvious from CLAUDE.md.

### Privacy & Security
Include when data is sent, stored, accessed, or when authentication/authorization is involved.

### Rollback Plan
Include when modifying existing production behavior. How do we undo this if it goes wrong?

---

## Formatting Rules

- **Version:** Save as `.prd/prd-v{N}.md` (sequential version number)
- **Frontmatter:** Include the full YAML frontmatter block (matches what `/bb-prd` Phase 4 writes):
  ```yaml
  ---
  version: {N}
  status: draft
  date: {YYYY-MM-DD}
  author: {participant name}
  previous: prd-v{N-1}.md
  ---
  ```
  Set `previous: null` for the first PRD (v1).
- **No architecture diagrams:** Architecture and UX design belong in `/bb-design`, not the PRD
- **No implementation detail:** PRDs describe what and why, not how the agent prompt / template / rubric is edited
- **No file-level detail:** Exact file paths and line numbers belong in tickets, not PRDs
- **Scope table:** Always include both columns — what's in AND what's out
