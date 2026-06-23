# Judge: value levers grounded in evidence (roi-hypothesis-builder)

The artifact proposes value levers, each meant to trace through a four-link chain:
**evidence → capability (gap) → lever → value** (Root Driver → Operational Change →
Volume/Rate Impact → Financial Impact). The failure mode is invented levers — value
claims with no evidentiary root, or a broken chain that asserts financial impact
without the intervening logic.

Score 1.0 only if ALL hold:
- **Every lever traces to evidence**: each lever roots in a discovery evidence item
  (E#) or a documented capability gap — not a generic "best practice" with no client basis.
- **The 4-link chain holds**: Root Driver → Operational Change → Volume/Rate Impact →
  Financial Impact is present and each link logically follows the prior one. No leaps
  from a problem straight to a dollar figure.
- **No invented levers**: levers not supported by the client's evidence are either absent
  or clearly flagged as creative/speculative (e.g. CL#) and marked for validation.
- **Quantification is conservative**: volume/rate/financial steps don't smuggle in
  optimistic, unsourced magnitudes.

Deduct sharply for: a lever with no evidence root; a chain missing one or more links;
financial impact asserted without the operational/volume logic; speculative levers
presented as grounded fact.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name any lever whose chain is broken or whose evidence root is missing.
