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
# COLOR SOURCE: Official Backbase Master Template 2022 (Shobhit's extraction)
# Last Updated: 2026-02-16
# ═══════════════════════════════════════════════════════════════════════════════

---

## IMPORTANT RULES

1. **ALL visual outputs** (HTML dashboards, interactive reports, workshop decks, prototypes, engagement plans) MUST follow this design system.
2. **Colors** are from the official Backbase brand palette — no approximations.
3. **Layout patterns** (bento grids, dark feature sections, sidebar nav, glass morphism, SVG journey maps, heatmaps) are from the assessment dashboard template — the most sophisticated layout system available.
4. **Card accents**: Use top accent gradients. NEVER use `border-left` ribbons.
5. **Self-contained**: All HTML outputs must be self-contained with zero external CDN dependencies (no React CDN, no Tailwind CDN). Google Fonts for Libre Franklin is the ONLY acceptable external resource.
6. **Dark accents on light base**: Body background is ALWAYS light (`#F5FAFF` or `#F8FAFC`). Dark colors are used for sidebar, dark-feature sections, metric cards, journey swimlanes, and waterfall containers only.

---

## 1. COLOR PALETTE — Official Backbase Brand

### Primary Colors

| Token | CSS Variable | Hex | Usage |
|-------|-------------|-----|-------|
| **Primary Dark** | `--bb-dark` | `#091C35` | Dark backgrounds, sidebar, dark-feature sections, primary text on light |
| **Primary Blue** | `--bb-blue` | `#3366FF` | Primary accent, CTAs, links, active states, gradients |
| **White** | `--bb-white` | `#FFFFFF` | Text on dark, card backgrounds |

### Accent Colors

| Token | CSS Variable | Hex | Usage |
|-------|-------------|-----|-------|
| **Cyan** | `--bb-cyan` | `#69FEFF` | Highlights, data viz accent, attention items |
| **Red/Coral** | `--bb-red` | `#FF7262` | Alerts, negative indicators, pain points |
| **Purple** | `--bb-purple` | `#7B2FFF` | Gradient endpoints, visual richness accents |
| **Green** | `--bb-green` | `#26BC71` | Positive, success, growth indicators |
| **Amber** | `--bb-amber` | `#FFAC09` | Warning, caution, pending items |

### Supporting Colors

| Token | CSS Variable | Hex | Usage |
|-------|-------------|-----|-------|
| **Navy Heading** | `--bb-navy-heading` | `#181E41` | Alternative heading color |
| **Muted Blue-Grey** | `--bb-muted` | `#3A495D` | Card fills on dark, secondary backgrounds |
| **Light Blue** | `--bb-light-blue` | `#E5EBFF` | Light accent fills, table alternation |
| **Off-White** | `--bb-off-white` | `#F5FAFF` | Near-white backgrounds |
| **Light Grey** | `--bb-light-grey` | `#F3F6F9` | Content area backgrounds |
| **Mid Blue** | `--bb-mid-blue` | `#7D9DFF` | Secondary blue, hover states |

### Maturity / RAG Scale (Data Visualization)

| Level | CSS Variable | Hex | Meaning |
|-------|-------------|-----|---------|
| L0 | `--L0` | `#DC2626` | Non-Existent / Critical |
| L1 | `--L1` | `#EA580C` | Ad-Hoc / High Risk |
| L2 | `--L2` | `#0891B2` | Developing / Moderate |
| L3 | `--L3` | `#059669` | Defined / Good |
| L4 | `--L4` | `#2563EB` | Optimized / Excellent |

### Alpha Color References (for rgba usage)

When using the primary blue in transparent/alpha contexts:
- `rgba(51,102,255, ...)` — derived from `#3366FF`
- `rgba(9,28,53, ...)` — derived from `#091C35`
- `rgba(123,47,255, ...)` — derived from `#7B2FFF`

**NEVER use approximate values** like `rgba(26,86,255,...)` (old `#1A56FF`) or `rgba(26,31,54,...)` (old `#1A1F36`).

---

## 2. DEPRECATED COLORS — DO NOT USE

These colors appeared in earlier outputs and must be replaced:

| Deprecated | Replacement | Notes |
|-----------|-------------|-------|
| `#1A56FF` | `#3366FF` | Old approximate blue → official primary blue |
| `#1A1F36` | `#091C35` | Old approximate dark → official primary dark |
| `#0B0F1A` | `#091C35` | Old dark feature bg → official primary dark |
| `#141929` | `#091C35` | Old navy → official primary dark |
| `#1C2238` | `#3A495D` | Old navy-2 → official muted blue-grey |
| `#3B6BF5` | `#3366FF` | Old blue → official primary blue |
| `#5A8AFF` | `#7D9DFF` | Old blue-light → official mid-blue |
| `rgba(26,86,255,...)` | `rgba(51,102,255,...)` | Old blue alpha → correct blue alpha |

---

## 3. TYPOGRAPHY

### Primary Font: Libre Franklin (Official Backbase)

| Weight | CSS | Usage |
|--------|-----|-------|
| **Black (900)** | `font-weight: 900` | Major headings, hero titles, stat values |
| **SemiBold (600)** | `font-weight: 600` | Sub-headings, labels, overlines |
| **Regular (400)** | `font-weight: 400` | Body text, descriptions |
| **Light (300)** | `font-weight: 300` | Subtitles, secondary text |

### Fallback Stack
```css
font-family: 'Libre Franklin', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Font Import (only external dependency allowed)
```css
@import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;600;900&display=swap');
```

### Size Scale for Interactive Dashboards

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| Hero H1 | 5.5rem | 900 | Main dashboard title |
| Section H2 | 2.2rem | 900 | Panel headers |
| Dark Feature H3 | 2.8rem | 900 | Immersive section titles |
| Card H3 | 1.2rem | 700 | Card titles |
| Body | 0.9rem | 400 | Content text |
| Overline | 0.62rem | 700, uppercase, 3px tracking | Section labels |
| Caption | 0.65rem | 600, uppercase | Small labels, meta |

### Typography Rules
- **Negative letter-spacing** on display text: -4px (hero), -2px (dark feature), -1px (section headers, stats)
- **Positive letter-spacing** on overlines/labels: +2-3px
- **Line height**: 1.6 for body, 1.7 for paragraphs, 0.92 for hero titles
- **Gradient text**: Use `background: linear-gradient(90deg, #3366FF, #7B2FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;` for overlines and accent text

---

## 4. CSS CUSTOM PROPERTIES — Master Token Set

```css
:root {
  /* ── Backbase Brand ── */
  --bb-dark: #091C35;
  --bb-blue: #3366FF;
  --bb-white: #FFFFFF;
  --bb-cyan: #69FEFF;
  --bb-red: #FF7262;
  --bb-purple: #7B2FFF;
  --bb-green: #26BC71;
  --bb-amber: #FFAC09;
  --bb-muted: #3A495D;
  --bb-light-blue: #E5EBFF;
  --bb-off-white: #F5FAFF;
  --bb-light-grey: #F3F6F9;
  --bb-mid-blue: #7D9DFF;

  /* ── Semantic Tokens (Dashboard) ── */
  --bg: #F8FAFC;
  --card: #FFFFFF;
  --border: #E2E8F0;
  --text: #091C35;
  --muted: #64748B;
  --dim: #94A3B8;
  --accent: #3366FF;
  --accent-light: #E5EBFF;

  /* ── Maturity Scale ── */
  --L0: #DC2626;
  --L1: #EA580C;
  --L2: #0891B2;
  --L3: #059669;
  --L4: #2563EB;

  /* ── Shadows ── */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --shadow-lg: 0 10px 25px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);

  /* ── Spacing & Shape ── */
  --radius: 12px;
  --radius-lg: 16px;
  --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  /* ── Font ── */
  --font: 'Libre Franklin', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

---

## 5. LAYOUT PATTERNS (from Assessment Dashboard Template)

The assessment-dashboard-template.html (`templates/presentations/`) is the LAYOUT source of truth. All interactive outputs must use these patterns:

### Page Structure
- **Fixed sidebar** (250px, dark `#091C35`) with numbered tab navigation
- **Scrollable content area** with max-width 1360px
- **Hero section** with 2-column grid (text + visual)
- **Panel switching** via JavaScript (tab-based SPA)

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
|-----------|-------------|
| **Card** | 20px radius, top gradient accent on hover (scaleX animation), lift on hover |
| **Metric Card** | Dark bg (`#091C35`), centered stat, scale on hover |
| **Dark Feature Section** | Immersive `#091C35` bg, radial gradient orbs, gradient text fills |
| **Persona Card** | Avatar + expandable body, click to reveal |
| **Expandable** | Accordion with animated max-height, glow border on open |
| **Heatmap Cell** | Interactive selection with detail panel |
| **Phone Frame** | 280x580 with notch, status bar, embedded screens |
| **Friction Callout** | Severity-based top gradient (red/orange/yellow) |
| **Journey Experience Map** | SVG emotion curve with clickable stage markers |
| **Value Waterfall** | Dark bg, gradient bar segments showing leakage |
| **Score Badge** | Maturity-colored circle with hover scale |
| **Backbase Layer Tags** | Color-coded tags for engagement/orchestration/intelligence/integration |

### Dark Feature Section Pattern
```css
.dark-feature {
  background: #091C35;
  border-radius: 28px;
  padding: 72px 56px;
  position: relative;
  overflow: hidden;
}
.dark-feature::before {
  /* Top-right ambient blue orb */
  background: radial-gradient(circle, rgba(51,102,255,0.12) 0%, transparent 70%);
}
.dark-feature::after {
  /* Bottom-left ambient purple orb */
  background: radial-gradient(circle, rgba(123,47,255,0.08) 0%, transparent 70%);
}
```

### Card Accent Pattern (NEVER use border-left ribbons)
```css
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3366FF, #7B2FFF, #3366FF);
  transform: scaleX(0);
  transition: transform 0.4s ease;
}
.card:hover::before { transform: scaleX(1); }
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
6 floating background particles with brand-tinted colors at 0.04 opacity, 15-30s animation duration.

### Custom Scrollbar
```css
::-webkit-scrollbar-thumb { background: rgba(51,102,255,0.15); }
::selection { background: rgba(51,102,255,0.12); }
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
- Target file size: 50-400 KB depending on content density

### Accessibility
- Minimum contrast: `rgba(255,255,255,0.55)` for sub-labels on dark backgrounds
- Never use `rgba(255,255,255,0.3)` or lower for readable text on dark
- Blue text on dark navy: use `#60A5FA` (not `#3366FF`) for WCAG AA compliance
- Green text on dark navy: use `#34D399` (not `#059669`)

---

## 9. ENGAGEMENT TYPE ROUTING

This design system applies to ALL engagement types:

| Engagement Type | Output Format | Design System |
|----------------|---------------|---------------|
| **Ignite Assess** | Interactive HTML dashboard (sidebar + panels) | This file |
| **Ignite Inspire** | Interactive HTML dashboard (sidebar + panels) | This file |
| **Hybrid (Assess + Inspire)** | Single interactive HTML dashboard | This file |
| **Workshop Decks** | Slide-format HTML | This file (colors only; layout follows slide conventions) |
| **Prototypes** | Phone/browser frame HTML | This file (colors + component patterns) |

For slide-format outputs (workshop decks), use the brand colors from this file but adapt the layout to the slide structure defined in `knowledge/Ignite Inspire/design-system.md` (Section 4: Slide Layouts).

---

*End of Unified Design System*
