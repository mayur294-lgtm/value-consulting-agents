# Frontline 2026 — Slide Layout Specifications

Canvas: 20.0" x 11.25" (Google Slides widescreen)

All positions in inches from top-left origin. All text boxes include 15% width buffer for Google Slides compatibility.

---

## Layout 1: Title / Cover

Navy background (`#001C3D`), white text.

| Element | Left | Top | Width | Height | Style |
|---------|------|-----|-------|--------|-------|
| Section Label | 1.5" | 3.67" | 6.3" | 0.34" | Libre Franklin Regular 14pt, white, uppercase, letter-spacing |
| Title | 1.5" | 4.51" | 8.5" | 2.0" | Libre Franklin Bold 32pt, white |
| Date / Subtitle | 1.5" | 7.31" | 8.5" | 0.4" | Libre Franklin Regular 14pt, white |

---

## Layout 2: Section Divider

Navy background (`#001C3D`), white text. Used to introduce new sections.

| Element | Left | Top | Width | Height | Style |
|---------|------|-----|-------|--------|-------|
| Section Label | 1.67" | 3.32" | 6.3" | 0.34" | Libre Franklin Regular 12pt, white, uppercase |
| Title | 1.67" | 4.15" | 13.0" | 1.0" | Libre Franklin Bold 32pt, white |
| Tagline | 1.67" | 8.23" | 10.0" | 0.4" | Libre Franklin Regular 14pt, white |

---

## Layout 3: Agenda

Left side: branding + title. Right side: stacked agenda items.

| Element | Left | Top | Width | Height | Style |
|---------|------|-----|-------|--------|-------|
| Section Label | 1.48" | 1.55" | 5.13" | 0.3" | Libre Franklin Regular 10pt, navy, uppercase |
| Title | 1.41" | 2.22" | 5.62" | 0.76" | Libre Franklin Bold 32pt, navy |
| Customer Name | 1.47" | 5.25" | 5.62" | 0.4" | Libre Franklin Regular 14pt, navy |
| Agenda Item 1 | 9.69" | 1.59" | 8.9" | 0.37" | Libre Franklin Bold 18pt, navy |
| Agenda Item 2 | 9.69" | 3.46" | 8.9" | 0.37" | Libre Franklin Bold 18pt, navy |
| Agenda Item 3 | 9.69" | 5.40" | 8.9" | 0.37" | Libre Franklin Bold 18pt, navy |
| Agenda Item 4 | 9.69" | 7.30" | 8.9" | 0.37" | Libre Franklin Bold 18pt, navy |
| Agenda Item 5 | 9.69" | 9.22" | 8.9" | 0.37" | Libre Franklin Bold 18pt, navy |

---

## Layout 4: Challenge / Content (Full Width)

White background with title bar area at top.

| Element | Left | Top | Width | Height | Style |
|---------|------|-----|-------|--------|-------|
| Title | 1.17" | 1.14" | 17.68" | 0.76" | Libre Franklin Bold 24pt, navy |
| Subtitle | 1.17" | 2.0" | 17.58" | 0.4" | Libre Franklin Regular 14pt, text_muted |
| Content Area | 1.17" | 3.0" | 17.68" | 7.5" | Flexible — used for diagrams, cards, text |

---

## Layout 5: Split Comparison (From / To)

Two-column layout for before/after comparisons.

| Element | Left | Top | Width | Height | Style |
|---------|------|-----|-------|--------|-------|
| Title | 1.42" | 1.93" | 17.2" | 0.76" | Libre Franklin Bold 24pt, navy |
| Section Label | 1.44" | 1.30" | 8.18" | 0.3" | Libre Franklin Regular 10pt, navy, uppercase |
| Left Column Label | 1.36" | 4.27" | 8.07" | 0.4" | Libre Franklin Bold 14pt, navy, uppercase |
| Left Column Body | 1.36" | 5.17" | 8.07" | 3.23" | Libre Franklin Regular 14pt, navy |
| Right Column Label | 10.55" | 4.27" | 8.07" | 0.4" | Libre Franklin Bold 14pt, action_blue, uppercase |
| Right Column Body | 10.55" | 5.17" | 8.07" | 3.23" | Libre Franklin Regular 14pt, navy |

Left column background: `#F5F7F9`. Right column background: `#FFFFFF`.

---

## Layout 6: Product Showcase

Left: text description. Right: product screenshot/image.

| Element | Left | Top | Width | Height | Style |
|---------|------|-----|-------|--------|-------|
| Section Label | 1.48" | 1.82" | 5.13" | 0.3" | Libre Franklin Regular 10pt, navy, uppercase |
| Title | 1.41" | 2.49" | 6.23" | 0.76" | Libre Franklin Bold 32pt, navy |
| Description | 1.41" | 6.31" | 6.23" | 0.87" | Libre Franklin Regular 14pt, navy |
| Image | 9.16" | 1.40" | 9.21" | 8.45" | Product screenshot, right-aligned |

---

## Layout 7: Architecture Diagram

Full-width layered diagram. All shapes grouped for Google Slides stability.

| Element | Left | Top | Width | Height | Style |
|---------|------|-----|-------|--------|-------|
| Title | 1.17" | 1.14" | 17.68" | 0.76" | Libre Franklin Bold 24pt, navy |
| Subtitle | 1.17" | 2.0" | 17.58" | 0.4" | Libre Franklin Regular 14pt, text_muted |
| Diagram Area | 1.5" | 3.0" | 17.0" | 7.5" | Grouped shapes — see component specs |

Architecture layers (top to bottom):
1. **Customers** row — segment labels (Online, Mobile, Conversational)
2. **Employees** row — workspace labels (Teller, CSR, RM, Operations)
3. **Platform bar** — "AI-native Banking OS" (action_blue background)
4. **Enablement row** — system labels (CRM, CDP, KYC, etc.)
5. **Core row** — system labels (Ledger, Cards, Payments, etc.)

Each box: rounded rectangle, Libre Franklin Regular 14pt white text on navy/blue fill.

---

## Layout 8: Customer Case Study

| Element | Left | Top | Width | Height | Style |
|---------|------|-----|-------|--------|-------|
| Case Label | top-right | 1.0" | auto | 0.3" | Libre Franklin Bold 10pt, red, uppercase |
| Content Area | 1.5" | 2.0" | 17.0" | 7.5" | Flexible |
| Legal Footer | 1.5" | 10.0" | 17.0" | 0.5" | Libre Franklin Regular 8pt, text_muted |

Footer text: "Restricted use. This case study is intended solely for use in 1:1 discussions..."
