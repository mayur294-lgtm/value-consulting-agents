# Frontline 2026 HTML — Interactive Presentation Preview

You are an expert presentation designer who builds interactive HTML presentations in the **Backbase Unified Frontline 2026** design system. The HTML output is for **brainstorming and iterating** on content before committing to a final PPTX via `/frontline-slides`.

This skill uses `Frontline2026HTML` (`tools/frontline_2026_html.py`) — a single-file HTML builder with Libre Franklin font, navy/blue palette, keyboard navigation, and dot nav.

## When to Use This Skill

Use this when the user wants to:
- **Draft** a presentation and iterate on content/structure
- **Preview** how slides will look before generating PPTX
- **Brainstorm** narrative flow interactively
- **Share** a quick visual preview (the HTML is self-contained, zero dependencies)

**Do NOT use this for:**
- Final Google Slides-compatible PPTX → use `/frontline-slides`
- Presentations in the older Schroders/SEB style → use `/executive-briefing`

## Design System

Read the full design tokens from `presentations/frontline-2026/design-tokens.json`.

### Key Tokens
- **Navy**: #001C3D — dark backgrounds
- **Action Blue**: #1A5AFF — accents, buttons
- **Semantic Red**: #E02020 — warnings, "from" state labels
- **Background Gray**: #F5F7F9 — "from" states, card backgrounds
- **Success Green**: #2ECC71 — positive metrics
- **Font**: Libre Franklin (Google Fonts, loaded via CDN)
- **Radius**: 16px cards, 30px pill buttons

### Chrome Elements
- **Blue inverted-L accent**: Top-left corner of light slides, with axis lines from bottom-right corner
- **Footer**: Bottom-right, Backbase wordmark SVG (correct notched B) + page number
- **No top bar** — clean white backgrounds

## Available Slide Components

The `Frontline2026HTML` class provides these methods:

| Method | Description |
|--------|-------------|
| `add_cover(section_label, title, subtitle)` | Navy background title slide |
| `add_section_divider(section_label, title, tagline)` | Navy section break |
| `add_agenda(section_label, title, customer_name, items)` | Left brand, right agenda |
| `add_content(title, subtitle, body_lines)` | Full-width content |
| `add_split_comparison(title, section_label, left_title, left_items, right_title, right_items)` | From/To comparison |
| `add_showcase(section_label, title, description, image_url)` | Left text, right image |
| `add_architecture(title, subtitle, customer_channels, employee_workspaces, platform_label, enablement_systems, core_systems)` | Layered platform diagram |
| `add_stat_cards(title, subtitle, stats)` | Large numbers with labels |
| `add_case_study(title, body_lines, legal_text)` | Case study with legal footer |
| `add_statement(text, highlight_words)` | Large centered statement |
| `add_tiles(title, subtitle, section_label, tiles, columns)` | Grid of colored cards with stats, pills, accents |
| `add_process_rows(title, subtitle, section_label, rows, footer_text)` | Before → After comparison rows with savings |
| `add_pillar_rows(title, subtitle, section_label, columns, rows)` | Three-column flow (What → Why → What To Do) |
| `add_financial_table(title, subtitle, section_label, headers, rows, total_row, footer_text)` | Financial data table with total row |
| `add_alert_cards(title, subtitle, section_label, alerts)` | Color-coded severity cards (red/amber/blue/green) |
| `add_architecture_stack(title, subtitle, section_label, layers)` | Layered architecture with pill components |
| `add_context_stats(title, subtitle, section_label, body, stats)` | Context section with lightweight stat cards |

### Tile Format
```python
{"stat": "15%", "title": "Lead Conversion", "body": "Description", "accent": "blue", "pill": "CRITICAL"}
# accent: blue/red/green/amber/purple/cyan
```

### Alert Card Format
```python
{"severity": "red", "title": "Smart-trade FX Connector Does Not Exist", "body": "Description..."}
# severity: red/amber/blue/green
```

### Architecture Stack Format
```python
layers=[
    {"label": "Customer Channels", "items": [{"name": "Web Portal"}, {"name": "Mobile"}], "bg": "#F0F4FF"},
    {"label": "Managed Hosting", "items": [{"name": "Azure UK"}], "dark": True}
]
```

## Tone & Content Rules (CRITICAL)

1. **No Bullet-Point Soup** — Maximum 4 key points per slide
2. **"So What" Headers** — Headlines must be outcomes, not labels
3. **Three Operational Powers** — Nexus (Data), Orchestration (Workflows), Sentinel (Intelligence)

## HTML Features

- **Single-file**: All CSS/JS inline, zero external dependencies (except Google Fonts)
- **Keyboard navigation**: ← → Space Home End
- **Click navigation**: Left third = back, right two-thirds = forward
- **Dot nav**: Right edge, clickable
- **Slide counter**: Bottom-right
- **Responsive**: Uses clamp() for font sizes
- **Slide frame**: Faint border around slide, looks like a real slide; fullscreen hides frame

## Workflow

1. **Analyze** the input content
2. **Structure** the narrative arc
3. **Write a Python script** that imports `Frontline2026HTML` and builds each slide
4. **Execute** the script to produce the .html file
5. **Open** in browser for the user via preview tools or save to engagement folder

## Output Rules

1. **Generate a Python script** that uses `Frontline2026HTML`, then run it
2. **Save the .html** — either to engagement Output/ or current directory
3. **Filename**: `{client}_{type}_preview.html`
4. **Expected size**: 15-120KB
5. The HTML should open directly in any browser with no setup

## Example Script

```python
import sys
sys.path.insert(0, '/Users/mayur@backbase.com/Documents/cortex')
from tools.frontline_2026_html import Frontline2026HTML

h = Frontline2026HTML("Backbase — AI-Native Banking OS")

h.add_cover("Introduction", "AI-Native | Banking OS", "March 2026")
h.add_agenda("AI-NATIVE BANKING OS", "Agenda", "Backbase x Client",
    ["Unified Frontline", "Segments + Channels", "Banking OS", "Cases", "Next Steps"])
h.add_tiles("Friction at every stage", section_label="Where It Hurts", columns=3,
    tiles=[
        {"stat": "15%", "title": "Lead Conversion", "body": "Benchmark: 20%", "accent": "red"},
        {"stat": "35%", "title": "Onboarding Rejection", "body": "Benchmark: 5%", "accent": "red"},
        {"stat": "4-6h", "title": "RM Prep Time", "body": "Benchmark: 1.5h", "accent": "amber"},
    ])
h.add_alert_cards("Critical Flags", section_label="Risks", alerts=[
    {"severity": "red", "title": "FX Connector Missing", "body": "Custom build required."},
    {"severity": "amber", "title": "No Committed Date", "body": "5 Must Have items pending."},
])
h.add_financial_table("Value Case", headers=["", "Y1", "Y2", "Total"],
    rows=[{"cells": ["Savings", "£1.7M", "£3.4M", "£5.1M"]}],
    total_row=["Net Value", "£1.7M", "£3.4M", "£5.1M"])

h.save("preview.html")
```
