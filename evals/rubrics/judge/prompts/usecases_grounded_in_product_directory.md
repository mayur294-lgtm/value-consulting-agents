# Judge: use cases grounded in the product directory (usecase-designer)

The artifact designs use cases (UC-### IDs), each meant to map to real Backbase product-
directory capabilities (RB.x.x / WB.x.x) and to carry a build classification
(OOTB / Config / Custom) and a priority tier. The failure mode is invented capability —
mapping a use case to a product feature that doesn't exist, or mis-classifying custom
work as out-of-the-box.

Score 1.0 only if ALL hold:
- **Real product-directory mapping**: each use case maps to a plausible, real Backbase
  product-directory capability (RB./WB. IDs) — not an invented or vague feature.
- **Justified OOTB/Config/Custom classification**: the build classification is reasoned,
  not asserted — OOTB claims are credible (the capability genuinely exists out of the
  box), and genuinely bespoke work is honestly marked Config or Custom.
- **No over-promising OOTB**: the failure of claiming "out of the box" for what is really
  custom is penalized hard — it misleads the effort/cost picture.
- **Priority tiers reasoned**: Tablestakes/Differentiating or P1/P2/P3 tiers reflect value
  and fit, not arbitrary ranking.

Deduct sharply for: a use case mapped to a non-existent or fabricated capability; custom
work labelled OOTB; missing or arbitrary build classification; unjustified priority tiers.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name use cases with fabricated mappings or mis-stated OOTB/Config/Custom classification.
