# Judge: visual render (multimodal — you are shown a SCREENSHOT)

You are looking at a rendered screenshot of a Backbase deliverable (deck/report/
dashboard). Judge what TEXT parsing cannot see — the actual visual result against
the frozen design system.

Score 1.0 only if ALL hold:
- **No breakage**: no text overflow/clipping, no overlapping elements, no content
  spilling off-canvas, no marooned text in oversized boxes, no broken grids.
- **Hierarchy & balance**: clear visual hierarchy; sensible whitespace; not cramped,
  not sparse-and-empty.
- **On-brand**: Backbase Frontline look — navy/blue/clean, Libre Franklin, light base;
  not generic AI-slop (rainbow gradients, clip-art, inconsistent cards).
- **Legibility**: contrast is adequate; nothing unreadable; type sizes sensible.

Deduct sharply for: any overflow/clipping/overlap; cramped or empty slides; off-brand
visuals; illegible contrast.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name the specific visual defects you SEE (e.g. "slide 4 body text overflows the card").
