# UX Design Spec Template

Use this template when writing the UX design artifact in Phase 3 of `/bb-design`. All sections are written based on what was agreed during Phase 1 (UX Design).

---

## Frontmatter

```yaml
---
version: {N}
prd: prd-v{N}.md
status: draft
date: {YYYY-MM-DD}
author: {participant name}
previous: ux-design-v{N-1}.md
---
```

Set `previous: null` for the first design spec (v1).

---

## User Flows

Narrative step-by-step flow for each user journey this feature introduces or modifies.

```
[trigger / entry point]
        │
        ▼
[step 1: what user sees / does]
        │
        ├──[happy path]──▶ [step 2a]
        │                       │
        │                       ▼
        │                  [step 3: outcome]
        │
        └──[error / edge case]──▶ [error state]
                                        │
                                        ▼
                                  [recovery action]
```

Include one flow per distinct journey. Skip trivial flows (single-step actions).

---

## Screen & Component States

For each screen or interactive component involved:

| State | Trigger | What the user sees |
| --- | --- | --- |
| Loading | Data fetch in progress | Skeleton / spinner |
| Empty | No data exists yet | Empty state message + CTA |
| Populated | Data loaded | Normal content |
| Error | Fetch failed | Error message + retry |
| [feature-specific states] | ... | ... |

---

## Error States

List every error the user can encounter and how it's handled:

| Error | Cause | User-facing message | Recovery |
| --- | --- | --- | --- |
| ... | ... | ... | ... |
