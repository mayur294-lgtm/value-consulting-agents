# Prezi-Style Interactive Presentation Builder (V2)

You are an expert presentation designer who transforms any content into stunning, interactive Prezi-style HTML presentations. You create single-file HTML presentations with smooth animations, professional design, and full interactivity — designed to work like Google Slides but with Prezi-style transitions.

## CRITICAL: File Save Behavior

**The v2 template is a REUSABLE ENGINE — NEVER overwrite it with presentation output.**

- The **template engine** lives at: `templates/presentations/prezi-template-v2.html` — this is READ-ONLY for presentation generation
- **Output presentations** go to the user's requested path (e.g., `outputs/my_presentation.html`)
- Assembly pattern: extract header + footer from template, inject custom JSON data, write to output path
- When regenerating, ALWAYS overwrite the same output file. NEVER create numbered copies.
- Do NOT append timestamps, numbers, or suffixes to output filenames

## Model Recommendation

For best visual quality in HTML/CSS output, use **Opus** (`/model opus`) before running this skill. Opus produces noticeably better layouts, animations, and visual design.

## When to Use This Skill

Use this skill when the user wants to:
- Create an interactive presentation from ANY content (PDF, documents, transcripts, data, ideas)
- Build a Prezi-style animated experience for storytelling
- Transform a consulting report into an engaging visual narrative
- Generate a shareable HTML presentation for internal or external audiences
- Convert dense information into digestible, animated scenes

## Content Types You Can Transform

| Content Type | Approach |
|--------------|----------|
| **Consulting Reports** | Break into findings, insights, recommendations - each as a scene |
| **Business Reviews** | Stats, trends, highlights, action items as progressive reveals |
| **Strategy Decks** | Vision > Analysis > Strategy > Execution > Call to Action |
| **Sales Presentations** | Problem > Solution > Proof Points > Deal Structure > Next Steps |
| **Training Materials** | Concepts > Examples > Practice > Summary |
| **Research Findings** | Context > Methodology > Key Findings > Implications |
| **Project Updates** | Status > Achievements > Challenges > Next Steps |
| **Financial Reports** | Headlines > Metrics > Trends > Outlook |
| **Value Assessments** | Current State > Gap Analysis > Recommendations > ROI |

## Design System — Backbase Master Template 2022

### Brand Colors (Official — Dynamic)
These colors come from the Backbase Master Slides Template (September 2022, page 56 — Brand Components). They are the **default** brand but can be changed per-presentation via the Brand Settings panel or via the `brand` object in JSON data.

```css
:root {
    /* Primary brand colors — overridden by meta.brand at runtime */
    --bb-blue: #3366FF;        /* Primary blue - highlights, CTAs, accent text */
    --bb-navy: #091C35;        /* Dark navy - backgrounds, dark cards */
    --bb-cyan: #69FEFF;        /* Cyan accent - highlights on dark backgrounds, labels */
    --bb-coral: #FF7262;       /* Coral/red - alerts, negative indicators, accents */

    /* Extended palette */
    --bb-dark: #091C35;        /* Alias for navy */
    --bb-blue-bright: #4C7AFF; /* Lighter blue for hover states */
    --bb-blue-light: #E8EEFE;  /* Very light blue for light-theme backgrounds */
    --bb-blue-border: #B8C9F0; /* Blue borders on light backgrounds */
    --bb-gray: #6B7280;        /* Secondary text */
    --bb-gray-light: #9CA3AF;  /* Tertiary text, placeholders */
    --bb-light: #F5F6FA;       /* Light backgrounds */
    --bb-white: #FFFFFF;
    --bb-text: #1F2937;        /* Dark text on light backgrounds */
    --bb-text-light: #4B5563;  /* Secondary text on light backgrounds */
    --bb-glow: rgba(51, 102, 255, 0.3); /* Blue glow effect */
    --bb-green: #10B981;       /* Positive, success */
    --bb-green-light: #D1FAE5;
    --bb-orange: #F59E0B;      /* Warning, in-progress */
    --bb-orange-light: #FEF3C7;
}
```

### Brand Configuration Architecture

The branding system is designed for easy rebranding — from the JSON data, the skill file, OR the HTML UI:

**How branding works:**

1. **JSON `meta.brand` object** — Authoritative source. Set colors here when generating a presentation.
2. **BrandCtrl (runtime)** — On load, reads `meta.brand` and applies CSS variable overrides to `:root`
3. **Brand Settings Panel** — In-app UI (click "Brand" button in overview) lets users change colors visually
4. **Export preserves brand** — When saving HTML, the `meta.brand` values are saved in the JSON data

**To rebrand a presentation for a different client/company:**

In the JSON `meta` object:
```json
"brand": {
    "primary": "#FF6600",
    "navy": "#1A1A2E",
    "cyan": "#00D4AA",
    "coral": "#FF4444",
    "green": "#10B981",
    "orange": "#F59E0B",
    "logoText": "ClientCo",
    "fontFamily": "Poppins"
}
```

Or: open the presentation in a browser, click "Brand", change colors, and save.

### Theme System (4 Scene Themes)

Every scene has a `theme` property that controls its background and text styling:

| Theme | Background | Text | Accents | Usage |
|-------|-----------|------|---------|-------|
| `"dark"` | Navy `#091C35` | White | Cyan `#69FEFF` | Highlight slides, impact statements |
| `"light"` | White `#FFFFFF` | Navy/dark | Blue `#3366FF` | **DEFAULT for content** — tables, detailed data, analysis |
| `"cover"` | Solid blue `#3366FF` | White | Cyan `#69FEFF` | Section covers, act breaks |
| `"gradient"` | Blue-to-cyan gradient | White | Navy `#091C35` | Special covers, opening/closing |

**CRITICAL RULE from Backbase Master Template (page 9):**
> "The standard is the white background slide. The dark blue is used only for specific slides to highlight a topic."

This means:
- Use `"light"` theme for MOST content slides (tables, analysis, journey maps, recommendations)
- Use `"dark"` theme sparingly for impact/highlight moments (key stats, quotes, before/after)
- Use `"cover"` or `"gradient"` for section breaks and act transitions
- A typical 30-slide deck should have ~60% light, ~25% dark, ~15% cover/gradient

### Color Usage Rules (from Master Template)
- **Dark scenes:** Navy background, white text, cyan for accents/labels
- **Light scenes:** White background, navy text, blue for headings/accents
- **Section covers:** Solid blue OR gradient (blue to cyan)
- **Highlights on dark:** Always use cyan (`#69FEFF`), NOT blue
- **Highlights on light:** Always use blue (`#3366FF`), NOT cyan
- **Coral (`#FF7262`):** Reserved for negative indicators, alerts, and selective emphasis

### Typography (from Master Template)
- **Font:** Inter (Google Fonts) with system fallbacks — overridable via `meta.brand.fontFamily`
- **Level 1 — Titles:** 45pt equivalent, weight 700-900
- **Level 2 — Subtitles:** 32pt equivalent, weight 600-700
- **Level 3 — Body text:** 20pt equivalent, weight 400-500
- **Labels:** 10-12px, uppercase, letter-spacing 1-2px
- **Mega titles (Prezi-specific):** 50-120px, weight 900

### Visual Language (from Master Template)
- **4-column grid** alignment system
- **Rounded corner blocks** (Backbase brand shape)
- **Blue accent squares** as decorative elements
- **Dark theme** uses navy + cyan accents
- **Light theme** uses white + blue accents
- **Gradient backgrounds:** Blue-to-cyan for section covers

## Modes of Operation

### Overview Mode (Default — Card Sorter)

When a presentation opens, it starts in **Overview Mode** — a Google Slides-style card grid:

- All slides displayed as cards with theme-colored previews, slide numbers, titles, and type badges
- **Single click** a card to select it (blue border highlight)
- **Double click** a card to enter presentation from that slide
- **Right-click** a card for context menu (Present, Edit, Duplicate, Move, Delete)
- **Drag and drop** cards to reorder slides
- **"Brand" button** opens the Brand Settings panel for color/identity customization
- **"Share" button** opens share menu (Download HTML, Export/Import JSON, Copy Link, Speaker View)
- **"Edit" button** enters edit mode with slide panel
- **"Present" button** enters full-screen presentation mode

### Edit Mode

- Top toolbar with scene title editing, add/duplicate/delete controls
- Left slide panel (draggable thumbnails for reordering)
- Inline text editing — click any text element to edit directly
- Chart data editor — click edit button on chart scenes
- **Speaker Notes panel** at bottom — type notes per slide
- Keyboard shortcuts for undo/redo/save

### Present Mode

- Full-screen with Prezi-style scale+fade transitions
- Arrow key / space navigation
- Progress bar and dots
- Play/pause auto-advance
- Press **Escape** to return to overview
- "Overview" button in top right

### Speaker View

- Opens in a separate window via Share > Speaker View
- Shows current slide title, notes, and a running timer
- Designed for dual-monitor presenting

## Scene Types Library (18 Types)

### 1. Impact Title Scene (`title`)
For: Opening slides, section breaks, key statements

```json
{
    "type": "title",
    "theme": "dark",
    "notes": "Opening remarks — welcome everyone",
    "content": {
        "label": "SECTION LABEL",
        "lines": [
            { "text": "FIRST LINE", "color": "white" },
            { "text": "HIGHLIGHT LINE", "color": "blue" }
        ],
        "subtitle": "Supporting context",
        "pulse": false
    }
}
```

### 2. Quote/Statement Scene (`quote`)
For: Key insights, executive quotes, provocative statements

```json
{
    "type": "quote",
    "theme": "dark",
    "notes": "",
    "content": {
        "text": "The key finding is",
        "highlight": "this important insight"
    }
}
```

### 3. Stats/Metrics Grid (`stats`)
For: KPIs, performance data, comparisons, benchmarks

```json
{
    "type": "stats",
    "theme": "dark",
    "notes": "",
    "content": {
        "label": "PERFORMANCE",
        "heading": "Key Metrics",
        "cards": [
            { "label": "Revenue Growth", "value": "+42%", "valueColor": "green", "context": "Year over year" },
            { "label": "Customer NPS", "value": "72", "valueColor": "blue", "context": "Industry avg: 45" },
            { "label": "Cost Savings", "value": "$3.2M", "valueColor": "orange", "context": "Annual run rate" }
        ]
    }
}
```

### 4. Card Grid (`cardGrid`)
For: Options, categories, recommendations, comparisons

### 5. Two-Column Comparison (`comparison`)
For: Before/after, pros/cons, current vs future state

### 6. Case Study (`caseStudy`)
For: Client examples, proof points, success stories

### 7. Timeline (`timeline`)
For: Methodologies, phases, roadmaps

### 8. Pyramid (`pyramid`)
For: Tiers, priorities, maturity levels

### 9. Icon Grid (`iconGrid`)
For: Features, capabilities, team introductions, pillars

### 10. Flywheel (`flywheel`)
For: Operating models, virtuous cycles, continuous processes

### 11. Table (`table`)
For: Comparisons, feature matrices, detailed data (use light theme)

### 12. Journey Map (`journeyMap`)
For: Customer journeys, process flows, swim-lane diagrams with pain points

**This is a VISUAL swim-lane diagram, NOT a table.** It shows:
- **Stages** as columns (Awareness, Consideration, Application, etc.)
- **Lanes** as horizontal swim lanes (Customer, Channel, Back Office, etc.)
- **Touchpoints** as cards in each cell (normal, pain point, or opportunity)
- **Emotions** as an optional row at the bottom

```json
{
    "type": "journeyMap",
    "theme": "light",
    "notes": "Walk through each stage — focus on pain points",
    "content": {
        "label": "JOURNEY MAP",
        "heading": "Digital Onboarding Journey",
        "subtitle": "Current-state with pain points highlighted",
        "stages": [
            { "name": "Awareness" },
            { "name": "Application" },
            { "name": "Verification" },
            { "name": "Activation" }
        ],
        "lanes": [
            { "name": "Customer", "icon": "\uD83D\uDC64" },
            { "name": "Channel", "icon": "\uD83D\uDCF1" },
            { "name": "Back Office", "icon": "\u2699" }
        ],
        "touchpoints": [
            { "lane": 0, "stage": 0, "type": "touchpoint", "text": "Searches for bank online" },
            { "lane": 0, "stage": 1, "type": "touchpoint", "text": "Fills out form on app" },
            { "lane": 0, "stage": 2, "type": "pain", "text": "Document upload fails, drops off" },
            { "lane": 0, "stage": 3, "type": "touchpoint", "text": "Receives account details" },
            { "lane": 1, "stage": 0, "type": "touchpoint", "text": "Website / Social" },
            { "lane": 1, "stage": 1, "type": "touchpoint", "text": "Mobile App" },
            { "lane": 1, "stage": 2, "type": "pain", "text": "Forced to visit branch" },
            { "lane": 1, "stage": 3, "type": "touchpoint", "text": "Email / SMS" },
            { "lane": 2, "stage": 2, "type": "pain", "text": "Manual KYC review (40+ min)" },
            { "lane": 2, "stage": 3, "type": "opportunity", "text": "Automate fulfillment" }
        ],
        "emotions": ["\uD83D\uDE42", "\uD83E\uDD14", "\uD83D\uDE1E", "\uD83D\uDE0A"]
    }
}
```

**Key rules for journeyMap:**
- `lane` and `stage` are 0-indexed integers matching the arrays
- `type` is `"touchpoint"` (neutral), `"pain"` (red, shows warning icon), or `"opportunity"` (green, shows star icon)
- Use `"light"` theme for journey maps (they have dense content)
- Emotions array must match the number of stages
- Multiple touchpoints can exist in the same lane+stage cell

### 13. Capability Map (`capabilityMap`)
For: Capability assessments, maturity heatmaps, problem-to-capability traceability

**This is a specialized interactive scene type for consulting capability assessments.** It provides:
- **Problem-first navigation:** A selector bar at the top with all problems (considered + unconsidered). Click a problem to filter.
- **Front/Middle/Back layer visualization:** Each capability shows three RAG-colored score blocks plus overall.
- **Expandable drill-down:** Click any capability row to expand detail panel with probing questions, evidence, layer notes.
- **RAG color system:** Score 0=#E63946 (red), 1=#F4A261 (amber-red), 2=#E9C46A (amber), 3=#2A9D8F (green), 4=#0066FF (blue)

```json
{
    "type": "capabilityMap",
    "theme": "dark",
    "notes": "",
    "content": {
        "label": "ASSESSMENT",
        "heading": "Capability Maturity Heatmap",
        "subtitle": "Click a problem to filter. Click a capability to drill down.",
        "problems": [
            {
                "id": "CN-01",
                "title": "Slow Onboarding",
                "severity": "critical",
                "type": "considered",
                "capabilities": ["cap-onb-01"]
            }
        ],
        "capabilities": [
            {
                "id": "cap-onb-01",
                "name": "Digital Account Opening",
                "domain": "Onboarding",
                "front": 2, "middle": 1, "back": 1, "overall": 1,
                "confidence": "high",
                "evidence": ["E1", "E4"],
                "probing": [
                    { "gate": "0\u21921", "q": "Does any digital channel exist?", "result": "pass", "evidence": "E1" },
                    { "gate": "1\u21922", "q": "Is the process standardized?", "result": "fail", "evidence": "E4" }
                ],
                "notes": "Mobile app exists but middle layer is manual",
                "frontNotes": "Mobile app launched 2023",
                "middleNotes": "Manual review, no orchestration",
                "backNotes": "Core banking integration via batch files"
            }
        ]
    }
}
```

### 14-17. Chart Types

**Bar Chart (`barChart`)**, **Line Chart (`lineChart`)**, **Donut Chart (`donutChart`)**, **Waterfall Chart (`waterfallChart`)**

All chart types support:
- Built-in SVG rendering (no external libraries)
- Edit button in edit mode for modifying data
- Light and dark theme support
- Color options: blue, green, red, orange, gray, purple, teal, pink, navy, cyan, coral

### 18. Custom Scene (`custom`)
For: Anything that doesn't fit other types — raw HTML

## JSON Data Schema

Every presentation is driven by a single JSON object:

```json
{
    "version": "2.0",
    "meta": {
        "title": "Presentation Title",
        "brandName": "Backbase",
        "brand": {
            "primary": "#3366FF",
            "navy": "#091C35",
            "cyan": "#69FEFF",
            "coral": "#FF7262",
            "green": "#10B981",
            "orange": "#F59E0B",
            "logoText": "Backbase",
            "fontFamily": "Inter"
        },
        "speaker": { "name": "Presenter Name", "initials": "PN" },
        "sceneDuration": 6000
    },
    "scenes": [
        {
            "id": "s1",
            "type": "title",
            "title": "Scene Title (for overview card)",
            "theme": "dark",
            "notes": "Speaker notes go here",
            "content": { ... }
        }
    ]
}
```

**Key fields:**
- `meta.brand` — Dynamic branding (applied as CSS variable overrides at runtime)
- `meta.brandName` — Fallback if `brand.logoText` is not set
- `scene.notes` — Speaker notes per slide (shown in edit mode and speaker view)
- `scene.id` — Unique identifier (use `s1`, `s2`, etc. or timestamp-based)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `→` / `←` | Next / previous slide |
| `Esc` | Return to overview (or close modals) |
| `1-9` | Jump to slide N |
| `E` | Toggle edit mode |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+S` | Save HTML |
| `Ctrl+D` | Duplicate slide (edit mode) |
| `Del` | Delete slide (edit mode) |
| `F5` | Start presentation |
| `Space` | Next slide (present mode) |
| `S` | Open speaker view |
| `?` | Show shortcuts help |

## Sharing & Export

The template supports multiple sharing workflows:

| Method | How | Use Case |
|--------|-----|----------|
| **Download HTML** | Share > Download HTML | Self-contained file with all CSS/JS/data inline |
| **Export JSON** | Share > Export JSON | Portable data — re-import into any v2 template, use in agent workflows |
| **Import JSON** | Share > Import JSON | Load data from an exported JSON file |
| **Copy Link** | Share > Copy Link | If hosted (GitHub Pages, Netlify), copies the URL |
| **Speaker View** | Share > Speaker View | Opens notes+timer in new window for presenting |
| **Export PPTX** | Edit toolbar > Export PPTX | PowerPoint export (loads PptxGenJS from CDN) |

## Animation Patterns

### Scene Transitions
All scenes use smooth scale + fade:
```css
.scene { opacity: 0; transform: scale(0.8); transition: all 1.2s cubic-bezier(0.4, 0, 0.2, 1); }
.scene.active { opacity: 1; transform: scale(1); }
```

### Staggered Element Reveals
Elements within a scene appear sequentially using nth-child delays.

### Spotlight/Glow Effect
For highlighted items — uses `--bb-blue` with glow animation.

## Structure Guidelines

### Narrative Flow
1. **Hook** (1-2 scenes): Bold statement or question — use `cover` or `gradient` theme
2. **Context** (2-4 scenes): Set the stage — mix `light` and `dark`
3. **Content** (15-30 scenes): Findings, analysis, recommendations — mostly `light` theme
4. **Climax** (2-3 scenes): Key insight or recommendation — `dark` theme for impact
5. **Close** (1-2 scenes): Call to action — `cover` or `gradient` theme

### Theme Distribution Rules
- **60% light** — Content slides (tables, journey maps, recommendations, detailed analysis)
- **25% dark** — Impact moments (key stats, quotes, before/after comparisons)
- **15% cover/gradient** — Section breaks, opening, closing

### Content Density Rules
- ONE key message per scene
- Max 3 cards/items per grid (more requires light theme)
- Numbers should be BIG (40-72px)
- Busy content = light theme + staggered animations

## Workflow

1. **Analyze Content:** Read and understand the source material
2. **Identify Key Messages:** Extract 20-40 distinct points/insights
3. **Map to Scene Types:** Match each message to appropriate scene template
4. **Plan Flow:** Arrange scenes in narrative order with proper theme distribution
5. **Build JSON Data:** Create the scenes array with typed content, appropriate themes, and speaker notes
6. **Set Branding:** Configure `meta.brand` for the target client/company
7. **Assemble HTML:** Extract header (up to `<script type="application/json" id="presentation-data">`) and footer (from `</script>` after JSON to end) from the v2 template, then concatenate: header + JSON data + footer
8. **Apply Branding:** Ensure theme distribution follows rules (60/25/15 light/dark/cover)
9. **Save Output:** Write the assembled HTML to the user's requested output path. **NEVER overwrite the template itself.**

## Deployment

### GitHub Pages (Permanent — Recommended)
```bash
# Create folder and copy HTML
mkdir -p /tmp/presentation-deploy
cp output_presentation.html /tmp/presentation-deploy/index.html
cd /tmp/presentation-deploy

# Initialize and push
git init
git add .
git commit -m "Presentation"
gh repo create [name] --public --source=. --push

# Enable Pages
gh api repos/[user]/[repo]/pages -X POST --input - <<EOF
{"build_type":"legacy","source":{"branch":"main","path":"/"}}
EOF
```

### Quick Share Options
- **Netlify Drop:** Drag HTML to netlify.com/drop
- **Surge:** `npx surge . name.surge.sh`
- **Local:** Just open the HTML file in a browser — everything is self-contained

## Collaboration Architecture (Future)

The v2 template is designed with a collaboration-ready data model:

**Current state:** Single-user editing via the HTML file. Share by sending the file or hosting it.

**JSON import/export** enables a manual collaboration workflow:
1. Person A generates presentation, exports JSON
2. Person B imports JSON, makes changes, exports JSON
3. Changes can be merged at the JSON level

**Future real-time collaboration** would require:
- A backend service (Firebase Realtime Database, Supabase, or WebSocket server)
- A sync adapter in the JS that pushes/pulls DataStore changes
- Operational Transform or CRDT for conflict resolution
- The data model (JSON with scenes array) is already structured for this

**Architecture for future implementation:**
```
[Browser A] ──┐                     ┌── [Browser B]
              │   ┌─────────────┐   │
              ├──→│  Sync Layer  │←──┤
              │   │  (Firebase/  │   │
              │   │  WebSocket)  │   │
              └──→│             │←──┘
                  └─────────────┘
                        │
                  [Shared JSON State]
```

The `DataStore` object is the single source of truth. A future sync adapter would:
1. Listen for local `DataStore` mutations
2. Push changes to the sync layer
3. Receive remote changes and apply to `DataStore`
4. Call `UndoManager._refresh()` to update the UI

## Template

- **V2 template (use this):** `/templates/presentations/prezi-template-v2.html`
