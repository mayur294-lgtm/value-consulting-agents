# Authoring guide — proposal-longform

How the template works and how to adapt it safely. The template is
`templates/proposal-longform/template.html`; everything below refers to it.

## 1. Document structure

Sections (each `<section id="s-...">`, linked from the sidebar):
`s-exec` executive summary · `s-value` value levers (3 KPI cards) · `s-scope` phases ·
`s-invest` the slider module · `s-scenarios` conservative/base/upside cards ·
`s-assump` assumptions table · `s-next` next steps + dark CTA. Plus the `#readout`
block (hidden on screen, prints via the button). Add/remove sections freely — keep ids,
sidebar links, and both language variants in sync.

Design tokens are Frontline 2026 Theme 1 (`--navy:#041326`, `--blue:#3367FF`, Libre
Franklin). Do not restyle; on Cortex the canonical source is
`knowledge/design-system/frontline-tokens.json`.

## 2. The language system

- Every translatable node exists per language: `<span lang="en">…</span><span lang="ar">…</span>`.
  CSS shows only the active language (`html[data-lang="en"] [lang="ar"]{display:none}`).
- `setLang()` flips `data-lang`, `lang`, and `dir` on `<html>`, so RTL mirroring is automatic;
  explicit `[dir="rtl"]` overrides exist for the sidebar, main margin, and callout borders.
- Locales live in the `LANGS` object. Default Arabic locale is `ar-SA-u-nu-latn`
  (Western digits for figures — the usual convention in Gulf financial documents);
  use plain `ar-SA` for Arabic-Indic numerals.
- Arabic body font: IBM Plex Sans Arabic (loaded alongside Libre Franklin).
- Other pairs (EN/FR, EN/DA…): change the `lang` attributes, the `LANGS` entry, the toggle
  buttons, and every paired block. For a third language, add a third button + spans.
- **Script-side branches (easy to miss):** the script also carries language logic outside
  the paired spans — search it for `lang === 'ar'` and update every branch (the term unit,
  the `userLine`/`swLine` formula labels, the tier table's "above" band, `roConfig`) plus
  the footer-date lines at the bottom (`LANGS.ar.locale` → your second language). Also
  re-pair any hand-typed display values whose convention differs by language (the KPI
  cards, the slider scale endpoints like "€300K") — computed `data-out` values localize
  themselves; hand-typed ones do not.
- **Discipline:** translations must be reviewed by a native speaker before client delivery.
  The demo Arabic is competent MSA but ships as illustrative copy. Never let the two
  languages drift out of sync on numbers — computed values come from `data-out` spans,
  which update in both languages automatically; hand-typed numbers do not.

## 3. The pricing engine

All commercial math lives in one place:

```js
const PRICING = {
  currency: 'EUR',
  baseFee: 450000,                       // platform base fee / yr
  tiers: [                               // published volume tiers (per unit / yr)
    {upTo: 150000, rate: 2.40},
    {upTo: 300000, rate: 2.10},
    {upTo: Infinity, rate: 1.90},
  ],
  presets: {
    conservative: {users: 100000, term: 3, services: 500000},
    base:         {users: 150000, term: 5, services: 650000},
    upside:       {users: 300000, term: 5, services: 800000},
  },
};
```

- Sliders are `<input type="range" id="drv-...">`; `recompute()` reads them, applies the
  tier, and writes every `[data-out]` span (hero TCV, math panel, readout mirror).
- The math panel lines print their own formula with live numbers ("User fee: 150,000 ×
  €2.40 /user/yr"). Keep that property when changing the model — transparency is the point.
- Different pricing basis (AUM, accounts, interactions): rename the driver, adjust min/max/
  step and `recompute()`, keep the tier table + formula lines pattern.
- Rates format with 2 decimals (`fmtRate`), totals with 0 (`fmtMoney`).
- Client-safe rule: tiers shown must be *published/list* structures. No negotiation
  corridors, no floors, no internal targets. The disclaimer block must survive every edit.

## 4. The executive readout

- The button calls `recompute()`, stamps the date, adds `print-readout` to `<body>`, and
  calls `window.print()`; print CSS then shows ONLY `#readout` (A4, 13mm margins).
  `afterprint` removes the class.
- The readout mirrors live state via the same `data-out` names (`roTcv`, `roConfig`…), so
  it always matches what the client configured. Keep it to one page; two max.
- Headless generation (for emailing a PDF without opening the file):

```bash
chrome --headless --print-to-pdf=readout.pdf --no-pdf-header-footer \
  "file:///path/proposal.html?readout=1"            # add &lang=ar for Arabic
```

- Normal browser printing (no button) prints the full document with nav/sidebar hidden —
  that is the "whole proposal as PDF" path.

## 5. Known behaviors

- Opening via `file://` works fully (fonts need internet once; they cache).
- `localStorage` remembers the language across visits; ignored gracefully if blocked.
- The preset highlight clears automatically when a slider moves off a preset — by design.
- Hero stats: TCV/term are live; the other two (time-to-value, value-at-stake) are authored
  copy — update them per deal.
