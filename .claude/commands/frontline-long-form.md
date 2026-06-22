# Frontline Long Form — HTML Document Builder

You are generating a professional long-form business document HTML using the **Frontline 2026 Long-Form design system** — a sidebar-navigated, navy/blue, Libre Franklin scrollable document used for value cases, ROI summaries, executive briefings, and proposal support documents.

This is the **document-format** sibling of `/frontline-slides-html` (decks). Same brand, different deliverable.

## MANDATORY FIRST STEP

Read the canonical token file and the template before writing a single line of HTML, in this order:

1. **`presentations/frontline-2026/design-tokens.json`** — the source of truth for all hex values, typography, geometry. Do not invent or override these.
2. **`templates/long-form/document-template.html`** — the complete CSS + class library. Clone its `<style>` block verbatim into your output.
3. **`knowledge/banking_os.md`** — Banking OS product substance (control plane · Nexus + Sentinel · 2 domains → 4 solutions [Digital Banking, Conversational Banking, Relationship Intelligence, Customer Operations] · Factory/Missions · three value pools). Where other repo files diverge, banking_os.md wins.
4. **`knowledge/banking_os.md`** — voice (operating-model thesis, From→To, vocabulary). Retire "engagement banking" / "better channels".

Do not rewrite, simplify, or replace the CSS. The classes are the contract.

> **Canon — read first.** This is the most positioning-sensitive long document. Open on From→To, anchor on the AI-Native Banking OS, and use the **three value pools** (cost-to-serve ↓ 20–40% · conversion/cross-sell/retention ↑ 10–25% · AI approval-to-production 3–5× faster) as the hero-stat vocabulary.

## When to Use This Skill

Use this for any standalone scrolling business document:
- Value cases and business cases
- ROI summaries
- Executive briefings (long-form, read-async)
- Capability assessments (short-form)
- Proposal support documents
- Any deliverable that gets PDF-printed and emailed

**Do NOT use this for:**
- Slide decks → `/frontline-slides-html` (HTML preview) or `/frontline-slides-pptx` (Google Slides PPTX)
- Bespoke hand-authored scenes → `/executive-briefing`
- Interactive dashboards with sidebar navigation → `/generate-assessment-html`

## Design System at a Glance

Read full tokens from `presentations/frontline-2026/design-tokens.json`. Quick reference:

- `--navy: #041326` — hero, top nav, table headers, dark CTA, metric cards
- `--blue: #3367FF` — accents, part numbers, links, lever tags, sidebar active state
- `--off: #F3F6F9` — page background, soft surfaces
- `--text: #041326` — body text
- `--border: #CED2D7` — card borders, table dividers
- Font: **Libre Franklin** (Google Fonts CDN)

## Component Library (use these class names exactly)

| Component | Class | Notes |
|-----------|-------|-------|
| Top nav | `.top-nav` + `.top-nav__logo` + `.top-nav__title` + `.top-nav__badge` | Fixed navy bar |
| Sidebar | `.sidebar` + `.sidebar__group-label` + `<a>` links with `.active` | Anchor navigation |
| Hero | `.hero` + `.hero-inner` + `.hero__stats` + `.hero__stat` | Navy bg, 4 glassmorphism stat boxes |
| Section header | `.sh` + `.sh-eyebrow` + `h2` + `.lead` | Always inside `.outer` |
| Outer container | `.outer` (max-width 1080px) | Wraps all section content |
| 2-card grid | `.grid-2` + `.card` | Comparison cards |
| 3-card grid | `.grid-3` + `.card` | Feature/benefit cards |
| 4-card grid | `.grid-4` + `.card` | Dense card layouts |
| Compact card | `.card.card--compact` + `.card-hdr-flex` | Tight feature list cards |
| Data table | `.dt` (inside `.table-wrap`) | Navy header, striped rows |
| Callout | `.callout.blue/green/amber/red` | Highlighted note |
| Badge | `.bb-badge.red/amber/green/blue/purple` | Status / category chips |
| Stakeholder org | `.sr-org-header` + `.sr-org-header__logo` | Org branding row |

(See `templates/long-form/document-template.html` for the complete class list — many more components are defined including lever cards, scenario cards, value tables, assumption tables, timelines.)

## Page Break Rules (for PDF output)

Apply `.page-break` to `.part-label` elements to start each major part on a new PDF page. Apply to `.inner-part` for sub-section breaks.

```html
<div class="part-label page-break" id="part02">
```

PDF is generated with Puppeteer: A4 landscape, 5mm margins, `printBackground: true`.

## Document Structure

```
top-nav (fixed)
sidebar (fixed left)
main
  hero (navy, 4 stats)
    part-label [Part 01]                  ← no page-break on first part
      section > outer > sh + content
    part-label.page-break [Part 02]
      section > outer > sh + content
      inner-part (sub-sections within Part 02)
    part-label.page-break [Part 03]
      section > outer > sh + content
  dark-cta
  doc-footer
```

## Output Rules

1. Read `presentations/frontline-2026/design-tokens.json` first — verify the canonical hex values
2. Read `templates/long-form/document-template.html` — clone its `<style>` block verbatim
3. Replace all `{{PLACEHOLDER}}` tokens with engagement-specific content
4. Add content sections using only the documented component classes
5. Output a single self-contained HTML file
6. File size should be 40–120 KB for a typical business case

## Stat Color Coding

Use these `.val` color classes in `.hero__stat` to signal sentiment:
- `.blue` — neutral / platform metrics
- `.green` — positive ROI, efficiency gains
- `.cyan` — combined / total figures
- `.purple` — financial value (€, $)
- `.amber` — risk or caution figures

## Lineage

This skill is the long-form sibling of the Frontline 2026 slides system. It originated as the Sparekassen Danmark DSD (Micha Kroes, Apr 2026) and was integrated into the Frontline family with reconciled tokens on 2026-04-29.
