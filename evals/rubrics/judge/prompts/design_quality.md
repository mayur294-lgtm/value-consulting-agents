# Judge: design quality (semantic, on the markup/structure)

Beyond mechanical conformance (palette/font/CDN — covered by code checks), judge
whether the deliverable is actually well-designed against the frozen design system.

Score 1.0 only if ALL hold:
- **Hierarchy**: clear title → section → supporting structure; not a flat wall.
- **Composition**: content-sized blocks, not cramped or stretched; sensible grouping
  (cards/grids used as intended), whitespace present.
- **"So What" framing**: headers state outcomes, not bland labels.
- **On-brand restraint**: uses the design-system components (cards, callouts, badges,
  tables) rather than ad-hoc markup; no AI-slop tells (everything-a-gradient,
  identical filler cards, emoji-as-design).
- **Scannable**: a reader can skim headers/stats and get the story.

Deduct for: flat undifferentiated text; cramped or marooned text; ad-hoc components
that ignore the system; label-headers ("Overview") instead of outcomes; slop patterns.

Note: you are reading the HTML/markup, not a screenshot — judge structure & semantics.
The rendered-pixel check is a separate visual eval.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name the weakest 1-2 areas.
