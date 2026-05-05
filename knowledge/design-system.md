# UNIFIED DESIGN SYSTEM — Backbase Value Consulting
# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE SOURCE OF TRUTH for ALL visual outputs across ALL engagement types
# (Ignite Assess, Ignite Inspire, hybrid engagements, any future products)
#
# AUTHORITY: This file overrides any agent-level design rules.
# All agents generating HTML, interactive dashboards, decks, or any visual
# output MUST reference this file.
#
# LAYOUT SOURCE: templates/presentations/assessment-dashboard-template.html
# COLOR SOURCE: Backbase Unified Frontline 2026 Design System
# Last Updated: 2026-05-05
# ═══════════════════════════════════════════════════════════════════════════════

---

## IMPORTANT RULES

1. **ALL visual outputs** (HTML dashboards, interactive reports, workshop decks, prototypes, engagement plans) MUST follow this design system.
2. **Colors** are from the Backbase Unified Frontline 2026 brand palette — no approximations, no off-brand hues, no colors from prior systems.
3. **Layout patterns** (bento grids, dark feature sections, sidebar nav, glass morphism, SVG journey maps, heatmaps, phone-frame prototypes, value waterfalls) remain as before — only the colors and typography are updated to Frontline 2026.
4. **Card accents**: Use top accent gradients (`#1A5AFF` → lighter blue) on hover. NEVER use `border-left` ribbons.
5. **Self-contained**: All HTML outputs must be self-contained with zero external CDN dependencies (no React CDN, no Tailwind CDN). Google Fonts for Libre Franklin is the ONLY acceptable external resource.
6. **Light base, navy accents**: Body background is ALWAYS `#FFFFFF` (pure white). Navy `#001C3D` is used for sidebar, dark-feature sections, metric cards, journey swimlanes, and waterfall containers only.
7. **Brand chrome on light slides**: Blue inverted-L corner accent (top-left) + Backbase wordmark footer (bottom-right, notched B SVG) + page number. No top bar.

---

## 1. COLOR PALETTE — Backbase Unified Frontline 2026

**Source:** Backbase Unified Frontline 2026 Design System (Master Template _ 2026.pptx + Gemini Agentic Blueprint). This is the ONLY permitted palette. No other colors may be used.

### Core Brand Tokens

| Token | CSS Variable | Hex | Usage |
|-------|--------------|-----|-------|
| **Primary Navy** | `--bb-navy` | `#001C3D` | Dark backgrounds, sidebar, dark-feature sections, primary text on light, headings, Banking OS platform blocks |
| **Action Blue** | `--bb-blue` | `#1A5AFF` | Primary accent, CTAs, links, active states, AI-assist icons, integration bars |
| **Semantic Red** | `--bb-red` | `#E02020` | Alerts, "from" state labels, critical pain points, must-fix friction |
| **Success Green** | `--bb-green` | `#2ECC71` | Positive metrics, "to" state labels, growth indicators |
| **Background Gray** | `--bb-bg-gray` | `#F5F7F9` | "From" state cards, soft surfaces, table alternation |
| **Surface White** | `--bb-white` | `#FFFFFF` | Light backgrounds, "to" state cards, content surfaces |
| **Text Main** | `--bb-text` | `#001C3D` | Primary text on light backgrounds |
| **Text Muted** | `--bb-muted` | `#5C6E84` | Captions, disclaimers, secondary text, sub-labels |

### Extended Utility Palette (used by `tools/frontline_2026_html.py` for tile/alert accents)

These are NOT for reskinning the brand — they exist for severity-coded tiles, alert cards, and gradient layers. Use only for the documented purposes below.

| Token | CSS Variable | Hex | Usage |
|-------|--------------|-----|-------|
| **Deep Red** | `--bb-red-deep` | `#DC2626` | Tile/alert "red" accent (slightly deeper than semantic red for legibility) |
| **Light Red Tint** | `--bb-red-tint` | `#FFF5F5` | Background fill behind red alert cards |
| **Red Border** | `--bb-red-border` | `#FCA5A5` | Border for red alert cards |
| **Amber** | `--bb-amber` | `#D97706` | Tile/alert "amber" accent — replaces previous gold for L1/warning states |
| **Amber Tint** | `--bb-amber-tint` | `#FEF9E7` | Background fill behind amber alert cards |
| **Deep Green** | `--bb-green-deep` | `#16A34A` | Tile/alert "green" accent (slightly deeper for legibility on light backgrounds) |
| **Green Tint** | `--bb-green-tint` | `#EAFAF1` | Background fill behind green alert cards |
| **Purple** | `--bb-purple` | `#7C3AED` | Tile accent only (rare — for visual variety in 6-up tile grids) |
| **Cyan** | `--bb-cyan` | `#0891B2` | Tile accent only (rare — for visual variety in 6-up tile grids) |
| **Light Blue Tint** | `--bb-blue-tint` | `#EBF0FF` | Light accent fills, tile backgrounds, table alternation, "to" state cells |
| **Pale Blue** | `--bb-blue-pale` | `#F0F4FF` | Lightest blue tier — architecture stack layer fills, layered diagrams |
| **Mid Blue** | `--bb-blue-mid` | `#93B5FF` | Secondary blue — progress bars in process-row "after" state |

### Maturity / RAG Scale (Data Visualization)

Five distinct levels using the new palette only. **Gold is replaced by amber.**

| Level | CSS Variable | Hex | Meaning |
|-------|--------------|-----|---------|
| L0 | `--L0` | `#E02020` | Non-Existent / Critical (semantic red) |
| L1 | `--L1` | `#D97706` | Ad-Hoc / High Risk (amber — replaces previous gold) |
| L2 | `--L2` | `#93B5FF` | Developing / Moderate (mid blue) |
| L3 | `--L3` | `#16A34A` | Defined / Good (deep green) |
| L4 | `--L4` | `#1A5AFF` | Optimized / Excellent (action blue) |

### Alpha Color References (for rgba usage)

When using brand colors in transparent/alpha contexts:
- `rgba(26,90,255, ...)` — derived from `#1A5AFF` (action blue)
- `rgba(0,28,61, ...)` — derived from `#001C3D` (primary navy)
- `rgba(224,32,32, ...)` — derived from `#E02020` (semantic red)
- `rgba(46,204,113, ...)` — derived from `#2ECC71` (success green)
- `rgba(217,119,6, ...)` — derived from `#D97706` (amber)

**NEVER use values from prior palettes.** See Section 2 for the full deprecation map.

---

## 2. DEPRECATED COLORS — DO NOT USE

**ALL colors not listed in Section 1 are banned.** This includes the previous ENGAGE 2026 palette, the original 2024 palette, and any ad-hoc colors. If a color is not in Section 1, it must not appear in any output.

### ENGAGE 2026 → Frontline 2026 Migration (May 2026)

| Deprecated (ENGAGE 2026) | Replacement (Frontline 2026) | Notes |
|--------------------------|------------------------------|-------|
| `#0F172A` | `#001C3D` | Slate dark → deep brand navy |
| `#3366FF` | `#1A5AFF` | Old primary blue → Action Blue |
| `#FF6B5E` | `#E02020` | Coral → Semantic Red |
| `#93C47D` | `#2ECC71` | Sage green → Success Green |
| `#E8B931` | `#D97706` | Gold → Amber (only for tile/alert accents and L1) |
| `#334155` | `#5C6E84` | Slate muted → brand muted |
| `#F8FAFC` | `#FFFFFF` | Off-white → pure white body bg |
| `#EDF2FF` | `#EBF0FF` | Old light-blue tint → Frontline light-blue tint |
| `#7D9DFF` | `#93B5FF` | Old mid-blue → Frontline mid-blue |
| `#B8CDFF` | `#F0F4FF` | Pale blue → architecture stack pale blue |
| `Inter` (font) | `Libre Franklin` | Inter retired — Libre Franklin is the corporate font |

### Pre-2026 Deprecated (still seen in legacy outputs)

| Deprecated | Replacement | Notes |
|-----------|-------------|-------|
| `#091C35` | `#001C3D` | Old "Backbase dark" → Frontline navy |
| `#181E41` | `#001C3D` | Old navy heading → Frontline navy |
| `#3A495D` | `#5C6E84` | Old muted → Frontline muted |
| `#E5EBFF` | `#EBF0FF` | Old light blue → Frontline light-blue tint |
| `#F5FAFF` | `#FFFFFF` | Old off-white → pure white |
| `#F3F6F9` | `#F5F7F9` | Old light grey → Frontline background gray |
| `#69FEFF` | **REMOVED** | Cyan accent — not in brand. Use `#1A5AFF` instead |
| `#7B2FFF` | **REMOVED** | Purple — not in brand for headlines. Use `#1A5AFF` (utility purple `#7C3AED` is allowed for tile accents only) |
| `#1A56FF` | `#1A5AFF` | Old approximate blue → exact Action Blue |
| `#1A1F36` | `#001C3D` | Old approximate dark → Frontline navy |
| `#0B0F1A` | `#001C3D` | Old dark feature bg → Frontline navy |
| `#141929` | `#001C3D` | Old navy → Frontline navy |
| `#1C2238` | `#5C6E84` | Old navy-2 → Frontline muted |
| `#3B6BF5` | `#1A5AFF` | Old blue → Action Blue |
| `#5A8AFF` | `#93B5FF` | Old blue-light → Frontline mid-blue |
| `#FFAC09` | `#D97706` | Old amber → Frontline amber |
| `#26BC71` | `#2ECC71` | Old vibrant green → Success Green |
| `#FF7262` | `#E02020` | Old red → Semantic Red |
| `rgba(123,47,255,...)` | **REMOVED** | Purple alpha — not in palette |

---

## 3. TYPOGRAPHY

### Primary Font: Libre Franklin (Frontline 2026)

| Weight | CSS | Usage |
|--------|-----|-------|
| **ExtraBold (800)** | `font-weight: 800` | Hero titles, mega display |
| **Bold (700)** | `font-weight: 700` | Section headings, card titles, slide titles |
| **SemiBold (600)** | `font-weight: 600` | Sub-headings, labels, overlines |
| **Medium (500)** | `font-weight: 500` | Active nav items, emphasised body |
| **Regular (400)** | `font-weight: 400` | Body text, descriptions |
| **Light (300)** | `font-weight: 300` | Subtitles, secondary text, large display numbers |

### Fallback Stack
```css
font-family: 'Libre Franklin', Helvetica, Arial, sans-serif;
```

### Font Import (only external dependency allowed)
```css
@import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700;800&display=swap');
```

### Size Scale for Interactive Dashboards

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| Hero H1 | 5.5rem | 800 | Main dashboard title |
| Section H2 | 2.2rem | 700 | Panel headers |
| Dark Feature H3 | 2.8rem | 800 | Immersive section titles |
| Card H3 | 1.2rem | 700 | Card titles |
| Body | 0.9rem | 400 | Content text |
| Overline | 0.62rem | 700, uppercase, 3px tracking | Section labels |
| Caption | 0.65rem | 600, uppercase | Small labels, meta |

### Size Scale for Slide-Format Outputs (Frontline 2026 PPTX/HTML)

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| Level 1 Label | 18 pt | 400, UPPERCASE | Captions, tags above title |
| Level 2 Title | 45 pt | 700 (Bold) | Slide headings |
| Level 3 Subtitle | 24 pt | 400 | Supporting headings |
| Level 4 Body | 20 pt | 400 | General slide content |

### Typography Rules
- **Negative letter-spacing** on display text: -4px (hero), -2px (dark feature), -1px (section headers, stats)
- **Positive letter-spacing** on overlines/labels: +2–3px
- **Line height**: 1.6 for body, 1.7 for paragraphs, 0.92 for hero titles
- **Never use gradient fills on text.** Solid colors only on glyphs — no `-webkit-background-clip: text` patterns. For accent words within a heading, use a solid-color span (e.g. `<span style="color: #1A5AFF;">word</span>`). Gradients are still permitted on non-text decorative elements (e.g. a 3px section-header underline bar).

---

## 4. CSS CUSTOM PROPERTIES — Master Token Set

```css
:root {
  /* ── Backbase Unified Frontline 2026 ── */
  --bb-navy:          #001C3D;
  --bb-blue:          #1A5AFF;
  --bb-red:           #E02020;
  --bb-green:         #2ECC71;
  --bb-bg-gray:       #F5F7F9;
  --bb-white:         #FFFFFF;
  --bb-text:          #001C3D;
  --bb-muted:         #5C6E84;

  /* Extended utility palette (tiles/alerts/layered diagrams only) */
  --bb-red-deep:      #DC2626;
  --bb-red-tint:      #FFF5F5;
  --bb-red-border:    #FCA5A5;
  --bb-amber:         #D97706;
  --bb-amber-tint:    #FEF9E7;
  --bb-green-deep:    #16A34A;
  --bb-green-tint:    #EAFAF1;
  --bb-purple:        #7C3AED;
  --bb-cyan:          #0891B2;
  --bb-blue-tint:     #EBF0FF;
  --bb-blue-pale:     #F0F4FF;
  --bb-blue-mid:      #93B5FF;

  /* ── Semantic Tokens (Dashboard) ── */
  --bg:               #FFFFFF;
  --card:             #FFFFFF;
  --border:           #E2E8F0;
  --text:             #001C3D;
  --muted:            #5C6E84;
  --dim:              #94A3B8;
  --accent:           #1A5AFF;
  --accent-light:     #EBF0FF;

  /* ── Maturity Scale (brand colors only) ── */
  --L0: #E02020;
  --L1: #D97706;
  --L2: #93B5FF;
  --L3: #16A34A;
  --L4: #1A5AFF;

  /* ── Shadows ── */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow:    0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --shadow-lg: 0 10px 25px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);

  /* ── Spacing & Shape ── */
  --radius:      16px;     /* cards (Frontline 2026 standard) */
  --radius-sm:   12px;     /* small UI elements */
  --radius-pill: 30px;     /* pill buttons (Frontline 2026 standard) */
  --transition:  0.3s cubic-bezier(0.4, 0, 0.2, 1);

  /* ── Font ── */
  --font: 'Libre Franklin', Helvetica, Arial, sans-serif;
}
```

---

## 5. LAYOUT PATTERNS (from Assessment Dashboard Template)

The assessment-dashboard-template.html (`templates/presentations/`) is the LAYOUT source of truth. All interactive outputs must use these patterns. **Layouts are unchanged from the prior system — only colors and typography are updated to Frontline 2026.**

### Page Structure
- **Fixed sidebar** (250px, navy `#001C3D`) with numbered tab navigation
- **Scrollable content area** with max-width 1360px, white `#FFFFFF` background
- **Hero section** with 2-column grid (text + visual)
- **Panel switching** via JavaScript (tab-based SPA)
- **Brand chrome (NEW)**: Blue inverted-L accent at top-left of light panels, Backbase wordmark footer at bottom-right with page number

### Grid Systems
| Pattern | CSS | Usage |
|---------|-----|-------|
| **Bento Grid** | `grid: repeat(4, 1fr) / auto-rows 180px` | Executive summary, overview sections |
| **Card Grid** | `repeat(2-4, 1fr)` | Standard content grids |
| **Heatmap** | `auto-fill minmax(140px, 1fr)` | Capability maps |
| **Timeline** | `repeat(4, 1fr)` with gradient connector | Roadmap phases |
| **Swimlane** | Dynamic columns with 1px gap | Journey before/after |
| **Proto Grid** | `repeat(3, 1fr)` | Phone frame prototypes |
| **ROI Grid** | `repeat(4, 1fr)` | Benefits dashboard |

### Component Library
| Component | Key Features |
|-----------|--------------|
| **Card** | 16px radius, top gradient accent on hover (scaleX animation), lift on hover |
| **Metric Card** | Navy bg (`#001C3D`), centered stat, scale on hover |
| **Dark Feature Section** | Immersive `#001C3D` bg, radial gradient orbs (action blue), gradient text fills |
| **Persona Card** | Avatar + expandable body, click to reveal |
| **Expandable** | Accordion with animated max-height, glow border on open |
| **Heatmap Cell** | Interactive selection with detail panel, maturity-coloured |
| **Phone Frame** | 280x580 with notch, status bar, embedded screens |
| **Friction Callout** | Severity-based top gradient (red/amber/blue) |
| **Journey Experience Map** | SVG emotion curve with clickable stage markers |
| **Value Waterfall** | Navy bg, gradient bar segments showing leakage |
| **Score Badge** | Maturity-coloured circle with hover scale |
| **Backbase Layer Tags** | Color-coded tags for engagement/orchestration/intelligence/integration |
| **Brand Corner Accent (NEW)** | Blue inverted-L at top-left of light panels (see snippet below) |
| **Backbase Wordmark Footer (NEW)** | Bottom-right SVG wordmark + page number |

### Dark Feature Section Pattern
```css
.dark-feature {
  background: #001C3D;
  border-radius: 28px;
  padding: 72px 56px;
  position: relative;
  overflow: hidden;
}
.dark-feature::before {
  /* Top-right ambient action-blue orb */
  background: radial-gradient(circle, rgba(26,90,255,0.14) 0%, transparent 70%);
}
.dark-feature::after {
  /* Bottom-left ambient lighter-blue orb */
  background: radial-gradient(circle, rgba(147,181,255,0.08) 0%, transparent 70%);
}
```

### Card Accent Pattern (NEVER use border-left ribbons)
```css
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #1A5AFF, #93B5FF, #1A5AFF);
  transform: scaleX(0);
  transition: transform 0.4s ease;
}
.card:hover::before { transform: scaleX(1); }
```

### Brand Corner Accent (Frontline 2026 — light panels)
A subtle inverted-L mark sits in the top-left of light panels and slides; complementary axis lines drop in from the bottom-right corner.

```css
.panel { position: relative; }
.panel::before {
  /* top-left inverted-L */
  content: '';
  position: absolute;
  top: 24px;
  left: 24px;
  width: 28px;
  height: 28px;
  border-top: 3px solid #1A5AFF;
  border-left: 3px solid #1A5AFF;
  border-top-left-radius: 4px;
  pointer-events: none;
}
.panel::after {
  /* bottom-right axis lines (subtle) */
  content: '';
  position: absolute;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-bottom: 1px solid rgba(0,28,61,0.08);
  border-right: 1px solid rgba(0,28,61,0.08);
  pointer-events: none;
}
```

### Backbase Wordmark Footer
```html
<footer class="bb-footer">
  <svg class="bb-wordmark" viewBox="0 0 120 24" aria-label="Backbase">
    <!-- notched B + 'ackbase' wordmark; embed inline SVG, never link -->
  </svg>
  <span class="bb-page">Page <span data-page>1</span></span>
</footer>
```
```css
.bb-footer {
  position: absolute;
  bottom: 16px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #5C6E84;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
}
.bb-wordmark { height: 14px; width: auto; fill: #001C3D; }
```

### Glass Morphism (Hero floating cards)
```css
.hero-float {
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.6);
  border-radius: 14px;
}
```

---

## 6. VISUAL EFFECTS

### Micro-interactions
- Card hover: `translateY(-3px)` + shadow expansion + top accent reveal
- Stat values: `scale(1.08)` on hover
- Heatmap scores: `scale(1.15)` on hover
- Phase dots: `scale(1.3)` on hover
- Glass cards: `translateY(-4px) scale(1.03)` on hover

### Animations
- `fadeSlideIn`: opacity + translateY(10px)
- `floatParticle`: 4-keyframe ambient float (20s cycle)
- `jxSlide`: Panel entrance (opacity + translateY 12px)
- Scroll reveal: IntersectionObserver with `0.8s cubic-bezier(0.16,1,0.3,1)`

### Ambient Particles
6 floating background particles tinted with action blue at 0.04 opacity, 15–30s animation duration. **Do NOT use purple, cyan, gold, or coral tints — those are removed from the palette for ambient/decorative use.**

### Custom Scrollbar
```css
::-webkit-scrollbar-thumb { background: rgba(26,90,255,0.15); }
::selection { background: rgba(26,90,255,0.12); }
```

---

## 7. RESPONSIVE BREAKPOINTS

| Breakpoint | Sidebar | Grid | Hero |
|------------|---------|------|------|
| > 1100px | 250px full | 4-col bento | 2-col (1fr + 520px) |
| 900-1100px | 200px | 3-col bento | 2-col (1fr + 360px) |
| 600-900px | 60px icon-only | 2-col bento | 1-col |
| < 600px | Hidden | 1-col | 1-col, reduced type |

---

## 8. OUTPUT REQUIREMENTS

### Self-Contained HTML
- ALL CSS inline in `<style>` tags
- ALL JavaScript inline in `<script>` tags
- Only external resource: Google Fonts for Libre Franklin
- Print stylesheet included (`@media print`)
- Target file size: 50–400 KB depending on content density

### Accessibility
- Minimum contrast: `rgba(255,255,255,0.55)` for sub-labels on dark backgrounds
- Never use `rgba(255,255,255,0.3)` or lower for readable text on dark
- Action blue text on navy (`#001C3D`): `#1A5AFF` passes WCAG AA at body sizes; use `#93B5FF` (mid-blue) for small text on navy
- Success green on navy: use `#86E1A6` (lightened green) for WCAG AA compliance — derive from `#2ECC71`
- Amber `#D97706` on navy passes WCAG AA at large text sizes only; use `#F59E0B` lightened for body copy on navy

### Google Slides Compatibility (slide-format outputs only)
For PPTX outputs (`/frontline-slides`), follow the rules in `presentations/frontline-2026/google-slides-rules.md`:
- 20"×11.25" canvas
- 15% text-width buffer (prevents wrapping on import)
- Autofit disabled
- No gradients, drop shadows, or rotated text
- Libre Franklin with Helvetica/Arial fallback
- All shapes grouped; 0.75" minimum edge margin

---

## 9. ENGAGEMENT TYPE ROUTING

This design system applies to ALL engagement types:

| Engagement Type | Output Format | Skill / Template |
|----------------|---------------|------------------|
| **Ignite Assess** | Interactive HTML dashboard (sidebar + panels) | `/generate-assessment-html` — uses Section 5 layouts + Frontline 2026 colors |
| **Ignite Inspire** | Interactive HTML dashboard (sidebar + panels) | `/generate-assessment-html` |
| **Hybrid (Assess + Inspire)** | Single interactive HTML dashboard | `/generate-assessment-html` |
| **Workshop / Sales Decks (HTML preview)** | Single-file `.html` deck | `/frontline-html` — uses Frontline 2026 slide layouts |
| **Workshop / Sales Decks (final PPTX)** | Google-Slides-compatible `.pptx` | `/frontline-slides` |
| **Prototypes** | Phone/browser frame HTML | This file (colors + component patterns from Section 5) |

For slide-format outputs, the brand colors and typography in this file are authoritative; layout positions are defined in `presentations/frontline-2026/slide-layouts.md`.

---

*End of Unified Design System*
