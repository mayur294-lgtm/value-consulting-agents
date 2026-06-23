# Design Context — Cortex Deliverables

Project-specific design defaults for the `bb-design` skill. Inject this into the design spec when a change produces a visual deliverable (HTML dashboard/deck, PPTX, output template).

## Source of truth

All visual outputs MUST follow `knowledge/design-system.md` and `presentations/frontline-2026/design-tokens.json`. Copy brand chrome and templates verbatim from the source tool — never invent your own version.

## Brand & tone

Backbase Unified Frontline 2026: trustworthy, precise, executive-ready. Consulting deliverables for a C-level audience — not a consumer app. No playfulness, no urgency patterns.

## Colour tokens (Frontline 2026, verified)

| Token | Hex | Use |
| --- | --- | --- |
| Navy | `#041326` | sidebars, dark-feature sections, metric cards, body text on light |
| Action Blue | `#3367FF` | accents, CTAs, links, active states |
| Semantic Red | `#FF503C` | warnings, "from" state labels |
| Background Gray | `#F3F6F9` | "from" state cards, page background |
| Text Muted | `#6B7786` | captions, disclaimers |
| Success Green | `#2ECC71` | positive metrics |
| Cyan | `#69FEFF` | combined/total figures, bright accent on navy |
| Surface White | `#FFFFFF` | clean backgrounds (body bg is always pure white) |

## Typography

Libre Franklin (Google Fonts), Helvetica/Arial fallback. Inter is retired. Max ~5 sizes, ~1.25 ratio.

## Anti-slop rules

- No purple-blue gradients
- No nested cards
- No gradient text (no `-webkit-background-clip: text` on glyphs)
- No `border-left` ribbon accents — use top gradient accents on hover
- No external CDNs except Google Fonts (Libre Franklin)
- Light base theme — body bg always pure white `#FFFFFF`
- Brand chrome: blue inverted-L corner accent + Backbase wordmark footer + page number
