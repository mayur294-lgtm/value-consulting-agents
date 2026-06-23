# Judge: assumption discipline

Inspect EVERY assumption the output relies on (in an assumptions register, inline, or
baked into a calculation). Per CLAUDE.md, a sound assumption is sourced, conservative,
and confidence-labelled — never optimistic-to-help-the-case.

For each assumption, check:
- **Sourced**: cites CLIENT DATA / DERIVED / BENCHMARK / ESTIMATE (not naked).
- **Conservative**: leans downside, not aggressive; doesn't inflate the result.
- **Labelled**: has a confidence level (low/medium/high).
- **Visible**: not hidden inside a number presented as fact.

Score 1.0 only if assumptions are consistently sourced, conservative, and labelled.
Deduct sharply for: aggressive/optimistic assumptions that inflate ROI; hidden
assumptions (a number with no stated basis); missing sources or confidence.

Return JSON: {"score", "pass" (>=0.8), "reason"} — flag the most aggressive or unsourced assumptions by name.
