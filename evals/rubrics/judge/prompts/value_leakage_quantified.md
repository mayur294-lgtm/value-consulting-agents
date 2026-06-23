# Judge: value leakage quantified (journey-builder)

The artifact maps customer journeys across lifecycle stages (Acquire/Activate/Expand/
Retain) with As-Is and Future-State, surfacing friction and value leakage. The failure
mode is hand-waved friction — "this is a pain point" with no magnitude, so the leakage
can't feed the ROI model.

Score 1.0 only if ALL hold:
- **Quantified leakage**: friction and value leakage are quantified with a magnitude
  ($, %, count, time, or conversion drop) — not just qualitatively described.
- **Tied to journey stages**: each leakage point is anchored to a specific lifecycle
  stage / journey step, not floated as a generic complaint.
- **Grounded**: the magnitudes trace to client evidence (PP-/CAP-/E# references or stated
  data) or are clearly flagged as labelled assumptions/benchmarks — not invented.
- **Waterfall logic**: where a value-leakage waterfall is shown, the steps add up and the
  cumulative leakage is coherent.

Deduct sharply for: friction described with no number; a leakage figure that appears from
nowhere with no source or assumption label; leakage not attached to any journey stage;
a waterfall whose numbers don't reconcile.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name the unquantified or ungrounded leakage points.
