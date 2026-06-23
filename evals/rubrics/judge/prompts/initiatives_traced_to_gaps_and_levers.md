# Judge: initiatives traced to gaps and levers (roadmap-prioritization)

The artifact is a prioritized, phased roadmap (Phases / Now-Next-Later / Waves) of
initiatives. The failure mode is orphan initiatives — work sequenced into the roadmap
with no link back to a capability gap or value lever, or sequencing that ignores
dependencies.

Score 1.0 only if ALL hold:
- **Traceability**: each initiative maps to a specific capability gap and/or value lever
  it addresses — not a generic "modernization" item with no provenance.
- **Sound sequencing rationale**: the phase/wave ordering is justified by value,
  feasibility, and dependencies; foundational work precedes dependent work; quick wins
  vs. foundational are balanced deliberately.
- **Dependencies explicit**: cross-initiative dependencies are stated, and the sequence
  respects them (no initiative scheduled before its prerequisite).
- **Outcome-linked**: each initiative ties to a business outcome / value-realization
  point, not just an activity.

Deduct sharply for: an initiative with no gap/lever it traces to; sequencing asserted
with no rationale; a dependency violated by the ordering; initiatives that read as a
vendor wish-list rather than evidence-driven.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name any initiative lacking a gap/lever trace or any sequencing that violates a dependency.
