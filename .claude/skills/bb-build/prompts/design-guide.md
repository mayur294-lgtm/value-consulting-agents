# Design Guide for Implementers

Read this before implementing any ticket that produces a visual deliverable — an HTML dashboard/deck, a PPTX builder, or an output template (`templates/**`, `presentations/**`). Every visual output MUST follow the cortex design system.

---

## Source of truth

- `knowledge/design-system.md` — the visual single source of truth (brand colours, typography, layout patterns).
- `presentations/frontline-2026/design-tokens.json` — the canonical Frontline-2026 tokens.

When in doubt, read those files. Copy brand chrome and templates verbatim from the source tool — never invent your own version.

---

## Non-negotiable rules

1. **Palette (Frontline 2026):** Navy `#041326`, Action Blue `#3367FF`, Semantic Red `#FF503C`, Background Gray `#F3F6F9`, Success Green `#2ECC71`, Text Muted `#6B7786`, Cyan `#69FEFF`, Surface White `#FFFFFF`. Do not introduce off-palette colours.
2. **Font:** Libre Franklin (Google Fonts), Helvetica/Arial fallback. Inter is retired.
3. **Light base theme:** body background always pure white `#FFFFFF`. Navy is for sidebars, dark-feature sections, and metric cards only.
4. **No gradient text** — solid colours only on glyphs. No `-webkit-background-clip: text`. Gradients are fine on decorative bars/lines.
5. **No external CDNs** — outputs are self-contained. The only allowed external resource is Google Fonts (Libre Franklin).
6. **Card accents:** top gradient accents on hover, never `border-left` ribbons.
7. **Brand chrome:** blue inverted-L corner accent (top-left) + Backbase wordmark footer (bottom-right) + page number.

---

## Quick checklist

Before marking a deliverable-output ticket as done:

- [ ] Colours come from the Frontline-2026 palette only
- [ ] Font is Libre Franklin (no Inter/Roboto defaults)
- [ ] Body background is pure white; navy used only for dark sections/cards
- [ ] No gradient text anywhere
- [ ] No external CDNs (Google Fonts only)
- [ ] Brand chrome present (corner accent + wordmark footer)
