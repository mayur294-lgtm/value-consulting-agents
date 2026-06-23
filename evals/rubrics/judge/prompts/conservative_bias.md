# Judge: ROI conservative bias

Cortex's standing rule (CLAUDE.md, README): ROI models must be conservative and
defensible — never optimistic math to "help" the case.

Score 1.0 only if ALL hold:
- Three scenarios present with a clearly labelled CONSERVATIVE/base case, and the
  headline recommendation leans on the conservative-to-moderate range, not the upside.
- Scenario probabilities or rationale are stated (not just three arbitrary columns).
- Benefit ramps build over time (no full benefit in Year 1); adoption/effectiveness
  curves are < 100% early.
- A downside / "where the case breaks" or sensitivity analysis exists.
- Assumptions carry sources and confidence; no naked optimistic numbers.

Deduct heavily for: headline driven by the aspirational case; Year-1 full benefit;
missing downside; assumptions without sources.

Return JSON: {"score", "pass" (>=0.8), "reason"}.
