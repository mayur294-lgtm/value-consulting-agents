# BACKBASE DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
# Extracted from: Backbase Master Template - 2022 (September 2022 Update)
# Source: Backbase Master Slides Template (Google Slides / PPTX)
# Last Updated: 2026-02-08
# ═══════════════════════════════════════════════════════════════════════════════

## IMPORTANT: This file is the SINGLE SOURCE OF TRUTH for all Backbase branding.
## All agents generating HTML, PPTX, or any visual output MUST reference this file.

---

## 1. COLOR PALETTE

### Primary Colors (from Theme + Slide 56 "Brand Components")

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Primary Dark** | `#091C35` | rgb(9, 28, 53) | Dark backgrounds, primary text on light, section fills |
| **Primary Blue** | `#3366FF` | rgb(51, 102, 255) | Primary accent, CTAs, links, highlights, header fills |
| **White** | `#FFFFFF` | rgb(255, 255, 255) | Text on dark, light backgrounds |

### Accent Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Cyan** | `#69FEFF` | rgb(105, 254, 255) | Highlights, data viz accent, attention items |
| **Red/Coral** | `#FF7262` | rgb(255, 114, 98) | Alerts, negative indicators, pain points |
| **Red (alt)** | `#FF503C` / `#FF6047` | — | Alternative reds used in charts |

### Supporting Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Navy Heading** | `#181E41` | rgb(24, 30, 65) | Alternative heading color (darker navy) |
| **Muted Blue-Grey** | `#3A495D` | rgb(58, 73, 93) | Card fills, secondary backgrounds, shapes |
| **Light Blue** | `#E5EBFF` | rgb(229, 235, 255) | Light accent fills, table alternation |
| **Off-White** | `#F5FAFF` | rgb(245, 250, 255) | Near-white backgrounds, subtle contrast |
| **Light Grey** | `#F3F6F9` | rgb(243, 246, 249) | Content area backgrounds |
| **Mid Blue** | `#7D9DFF` | rgb(125, 157, 255) | Secondary blue, hover states |

### Data Visualization / Chart Colors

| Token | Hex | Usage |
|-------|-----|-------|
| **Green** | `#26BC71` | Positive, success, growth, "Scheduled" badges |
| **Amber** | `#FFAC09` | Warning, caution, pending items |
| **Coral** | `#FF6047` | Negative, risk, blockers |
| **Cyan** | `#69FEFF` | Highlight, differentiation |
| **Light Blue** | `#E5EBFF` | Tertiary chart color |

### Theme Color Scheme (Official)

```
dk1 (Dark 1):     #091C35   — Primary dark / backgrounds
lt1 (Light 1):    #FFFFFF   — White
dk2 (Dark 2):     #3366FF   — Primary blue
lt2 (Light 2):    #000000   — Black
accent1:          #69FEFF   — Cyan
accent2:          #FF503C   — Red
accent3:          #E5EBFF   — Light blue
accent4:          #C2FBFF   — Pale cyan
accent5:          #F3F6F9   — Off-white
accent6:          #FAE0DE   — Pale pink
hlink:            #264EC7   — Hyperlink blue
folHlink:         #0097A7   — Followed link teal
```

---

## 2. TYPOGRAPHY

### Primary Font: Libre Franklin

| Weight | Usage | Occurrences in Template |
|--------|-------|------------------------|
| **Libre Franklin** (Regular, 400) | Body text, descriptions | 267 uses |
| **Libre Franklin Light** (300) | Subtitles, secondary text | 96 uses |
| **Libre Franklin Black** (900) | Major headings, cover titles | 14 uses |
| **Libre Franklin SemiBold** (600) | Sub-headings, labels | 7 uses |

### Secondary Font: Inter

| Weight | Usage |
|--------|-------|
| **Inter** (Regular) | Alternative body text, smaller text |
| **Inter Light** | Supplementary text |

### Font Size Scale

| Level | Size | Usage | Count |
|-------|------|-------|-------|
| **Mega Title** | 90pt | Appendix/divider single words | Rare |
| **Cover Title** | 45-55pt | Cover slide main title | 21+ uses |
| **Section Title** | 32-36pt | Chapter/section headers | 35+ uses |
| **Slide Title** | 24-25pt | Standard slide titles | 32+ uses |
| **Body Large** | 20pt | Primary body text, descriptions | 155 uses |
| **Body** | 16-18pt | Secondary body text, bullet points | 107+ uses |
| **Small** | 12pt | Captions, labels, footnotes | 66 uses |

### Typography Rules
- **Titles**: Libre Franklin Black (900) or SemiBold (600)
- **Body**: Libre Franklin Regular (400)
- **Light/secondary**: Libre Franklin Light (300)
- **All caps labels**: Libre Franklin SemiBold, letter-spacing: 1-2px, font-size: 10-12pt
- **Never** use more than 2 font families on a single slide
- **Line height**: 1.4–1.6 for body text

### CSS Font Stack
```css
font-family: 'Libre Franklin', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

---

## 3. LOGO

### Backbase Wordmark
The Backbase logo is a **text-based wordmark** rendered in the **Libre Franklin** font family. It is NOT a raster image — it is a styled text element.

**Rendering:**
- Font: Libre Franklin (regular or light weight)
- The "B" has a distinctive styling — use the font as-is
- Color: White on dark backgrounds, `#091C35` on light backgrounds
- Always accompanied by a **vertical divider line** (1px, same color as text)
- Slide number appears to the right of the divider

**Placement (Standard):**
- Bottom-right corner of every content slide
- Pattern: `Backbase  |  [slide number]`
- Position: ~0.8" from right edge, ~0.4" from bottom

**Placement (Cover Slides):**
- Not shown separately — the word "Backbase" may appear in the cover subtitle area

### HTML Logo Implementation
```html
<!-- Standard footer logo for dark backgrounds -->
<div class="bb-footer">
  <span class="bb-wordmark">Backbase</span>
  <span class="bb-divider"></span>
  <span class="bb-page-num">[n]</span>
</div>

<style>
.bb-footer {
  position: absolute;
  bottom: 28px;
  right: 48px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.bb-wordmark {
  font-family: 'Libre Franklin', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #FFFFFF; /* or #091C35 on light bg */
  letter-spacing: 0.5px;
}
.bb-divider {
  width: 1px;
  height: 16px;
  background: rgba(255,255,255,0.4); /* or rgba(9,28,53,0.3) on light bg */
}
.bb-page-num {
  font-family: 'Libre Franklin', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: rgba(255,255,255,0.5); /* or rgba(9,28,53,0.4) on light bg */
}
</style>
```

---

## 4. SLIDE LAYOUTS

### Layout Patterns (from Template)

#### Cover Slide (Layout 0: "TITLE")
- Background: `#091C35` (Primary Dark)
- Blue accent square: top-left, approx 16x16px, `#3366FF`
- Title: Libre Franklin Black, 45-55pt, White
- Subtitle: Libre Franklin Light, 20-24pt, White or `#F5FAFF`
- Backbase wordmark: bottom-right (text, not image)
- Optional: Client logo placeholder (center-right)

#### Section/Chapter Divider (BLUE background — primary for Ignite)
- **Background**: `#3366FF` (Primary Blue)
- **"Backbase" wordmark**: top-left, 32pt, white, Libre Franklin Regular
- **Ghost number**: top-right, 120pt, bold, faded blue (`#5C85FF`), e.g. "01"
- **Horizontal line**: white, with cyan `#69FEFF` accent square at left end
- **Section label**: uppercase, 12pt, `#69FEFF` (cyan)
- **Title**: 48pt, bold, white, below the line
- **Subtitle** (optional): 18pt, `#69FEFF` (cyan)
- **Footer**: "Backbase" bottom-right in light blue/white
- Alternative dark variant (`#091C35`) exists but BLUE is the standard for Ignite

#### Content Slide (WHITE background — DEFAULT for all content)
- **Background**: `#FFFFFF` (White) — **this is the default, NOT dark**
- **Title area**: top-left with blue accent square
- **Title text**: `#091C35` (Primary Dark)
- **Body text**: `#3A495D` (Muted Blue-Grey)
- **Cards**: `#F3F6F9` background, `#E5EBFF` border, 12-16px border-radius
- **Tables**: Blue `#3366FF` header, alternating white/`#F3F6F9` rows
- **Content area**: below title, 4-column grid alignment
- **Footer**: "Backbase | [n]" bottom-right in `#3A495D`

> **IMPORTANT**: Content slides use WHITE backgrounds by default. Dark backgrounds
> are reserved for cover/closing slides only. Section dividers use BLUE backgrounds.

### Blue Accent Square
A key Backbase brand element:
- Small filled square: `#3366FF`
- Size: ~16-20px
- Position: Left of the title text, vertically centered with first line
- Present on ALL slide types

---

## 5. SLIDE DIMENSIONS

| Property | Value |
|----------|-------|
| Width | 20.00 inches (1920px) |
| Height | 11.25 inches (1080px) |
| Aspect | 16:9 widescreen |
| Pixel | 1920 × 1080 |

---

## 6. COMPONENT PATTERNS

### Cards
- Background: `#3A495D` (on dark slides) or `#F3F6F9` (on light slides)
- Border: none (or 1px `rgba(255,255,255,0.06)` on dark)
- Border-radius: 12-16px
- Padding: 24-32px
- Title: Libre Franklin SemiBold, 16-20pt
- Body: Libre Franklin Regular/Light, 12-16pt

### Tables
- Header row: `#3366FF` background, white text, 10-12pt uppercase
- Body rows: alternating `#091C35` and `#0D1528` (dark) or white/`#F3F6F9` (light)
- Text: 12-16pt, `#FFFFFF` (dark) or `#091C35` (light)
- Border: 1px `rgba(255,255,255,0.06)` (dark) or `#E5EBFF` (light)

### Badges/Status Tags
- Scheduled/Done: `#26BC71` background with low opacity, green text
- Pending/TBD: `#FFAC09` background with low opacity, amber text
- Blocked/Risk: `#FF6047` background with low opacity, red text
- Font: 10-11pt, uppercase, bold

### Numbered Circles
- Size: 36-48px
- Background: `#3366FF`
- Text: White, 15-18pt, Libre Franklin Bold
- Used for objectives, step numbers

### Divider Lines
- Horizontal: 1px, `rgba(255,255,255,0.1)` (dark) or `#E5EBFF` (light)
- Blue accent line: 3px height, `#3366FF`, width ~60-100px

---

## 7. DARK VS LIGHT MODES

### Dark Mode (Primary for Ignite Engagements)
```
Background:       #091C35
Card/Shape fill:   #3A495D or rgba(255,255,255,0.05)
Primary text:      #FFFFFF
Secondary text:    #F5FAFF or rgba(255,255,255,0.7)
Muted text:        rgba(255,255,255,0.5)
Accent:            #3366FF
Highlight:         #69FEFF
Borders:           rgba(255,255,255,0.06)
```

### Light Mode
```
Background:       #FFFFFF
Card/Shape fill:   #F3F6F9
Primary text:      #091C35
Secondary text:    #3A495D
Muted text:        rgba(9,28,53,0.5)
Accent:            #3366FF
Highlight:         #69FEFF
Borders:           #E5EBFF
```

---

## 8. CSS VARIABLES (Ready-to-Use)

```css
:root {
  /* Primary */
  --bb-dark: #091C35;
  --bb-blue: #3366FF;
  --bb-white: #FFFFFF;

  /* Accent */
  --bb-cyan: #69FEFF;
  --bb-red: #FF7262;
  --bb-green: #26BC71;
  --bb-amber: #FFAC09;

  /* Supporting */
  --bb-navy-heading: #181E41;
  --bb-muted: #3A495D;
  --bb-light-blue: #E5EBFF;
  --bb-off-white: #F5FAFF;
  --bb-light-grey: #F3F6F9;
  --bb-mid-blue: #7D9DFF;

  /* Typography */
  --bb-font-primary: 'Libre Franklin', 'Inter', -apple-system, sans-serif;
  --bb-font-size-mega: 90px;
  --bb-font-size-cover: 45px;
  --bb-font-size-section: 32px;
  --bb-font-size-title: 24px;
  --bb-font-size-body-lg: 20px;
  --bb-font-size-body: 16px;
  --bb-font-size-small: 12px;

  /* Dark mode surfaces */
  --bb-surface-dark: #091C35;
  --bb-surface-card-dark: #3A495D;
  --bb-border-dark: rgba(255, 255, 255, 0.06);
  --bb-text-primary-dark: #FFFFFF;
  --bb-text-secondary-dark: #F5FAFF;
  --bb-text-muted-dark: rgba(255, 255, 255, 0.5);

  /* Light mode surfaces */
  --bb-surface-light: #FFFFFF;
  --bb-surface-card-light: #F3F6F9;
  --bb-border-light: #E5EBFF;
  --bb-text-primary-light: #091C35;
  --bb-text-secondary-light: #3A495D;
  --bb-text-muted-light: rgba(9, 28, 53, 0.5);
}
```

---

## 9. MAPPING: OLD (Approximate) → NEW (Correct)

The following colors were used in earlier outputs and need to be corrected:

| What We Used | Correct Backbase Color | Notes |
|--------------|----------------------|-------|
| `#0B0F1A` (dark bg) | `#091C35` | Official primary dark |
| `#141929` (navy) | `#091C35` | Use primary dark, not custom navy |
| `#1C2238` (navy-2) | `#3A495D` | Official muted blue-grey for cards |
| `#3B6BF5` (blue) | `#3366FF` | Official primary blue |
| `#5A8AFF` (blue-light) | `#7D9DFF` | Mid-blue from template |
| `#1A56FF` (old accent) | `#3366FF` | Correct to official blue |
| `#1A1F36` (old dark) | `#091C35` | Correct to official dark |

---

## 10. DO's AND DON'Ts

### DO:
- Use `#091C35` as the primary dark background (not approximate navies)
- Use `#3366FF` as the primary accent blue
- Use Libre Franklin as the primary font (fall back to Inter if unavailable)
- Include the blue accent square left of titles
- Include "Backbase | [n]" footer on content slides
- Use the 4-column grid alignment
- Keep generous white space
- Use the data viz palette consistently (green/amber/red/cyan)

### DON'T:
- Use gradients on backgrounds (flat colors only)
- Use drop shadows on cards (clean, flat design)
- Mix more than 2-3 colors on a single slide
- Use fonts other than Libre Franklin / Inter
- Place the Backbase wordmark as an image (it's always text)
- Use rounded corners on the overall slide (only on cards/elements within)
- Add borders to the outer slide frame in HTML outputs

---

## 11. GOOGLE FONTS IMPORT

```html
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;600;900&display=swap" rel="stylesheet">
```

Or for fully self-contained HTML:
```css
@import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;600;900&display=swap');
```

---

*End of Backbase Design System*
