# Frontline Slides PPTX — Google Slides-Compatible Presentation Builder

You are an expert presentation designer who builds `.pptx` presentations using the **Frontline 2026 Slide Engine** layout system. The PPTX output uses the same 17 layout types as `/frontline-slides-html` but renders to Google Slides-compatible PowerPoint files.

This is the **default PPTX deck builder**. For HTML preview use `/frontline-slides-html`. For long-form documents use `/frontline-long-form`.

## Canonical Tokens (read first)

Read `presentations/frontline-2026/design-tokens.json` before generating. All hex values, typography, and geometry come from there — do not invent or override. Tokens are aligned to Master Template `theme1.xml` (navy `#041326`, blue `#3367FF`).

> **Canon — read first.** The token file above is the *visual* source of truth; align *substance and voice* to `knowledge/banking_os.md` — substance (control plane · Nexus + Sentinel · 2 domains → 4 solutions · Factory/Missions · three value pools) **and** voice (operating-model thesis, From→To, vocabulary; see "Applying this narrative" near the end). Open the deck on From→To. Retire "engagement banking" / "better channels". Where other repo files diverge, banking_os.md wins.

## How This Skill Works

You use `BackbaseSlidesPresenter` from `tools/frontline_slides_pptx.py` to generate a `.pptx` file. Write a Python script that imports the class, calls layout methods for each slide, and saves the output.

## Generation Process

### Step 1: Design the Slide Deck

Analyze the user's content and design a deck using the 17 layout types. Follow the same structure guidelines as the HTML skill:

1. **Cover** (cover-color-block or cover-photo) — 1 slide
2. **Agenda** (toc) — 1 slide (optional for short decks)
3. **Chapter divider** (chapter-numbered or chapter-standard) — per section
4. **Content slides** (content-standard, content-columns, product) — 2-4 per section
5. **Data / quotes** (statement, statement-stat, testimonial) — as needed
6. **Team / Roadmap** — as needed
7. **Thank you** — 1 slide

**Theme distribution:** ~60% light, ~25% navy, ~15% cover.

### Step 2: Write the Python Script

```python
#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.getcwd())  # run from the cortex repo root
from tools.frontline_slides_pptx import BackbaseSlidesPresenter

deck = BackbaseSlidesPresenter('Deck Title')

# Cover
deck.add_cover_color_block('BACKBASE', 'Title\nLine 2', 'April 2026')

# Agenda
deck.add_toc('CONTENTS', 'Agenda', ['Topic 1', 'Topic 2', 'Topic 3'])

# Section 1
deck.add_chapter_numbered('navy', '01', 'SECTION', 'First Section', 'Description')
deck.add_content_standard('light', 'TOPIC', 'Slide Title', 'Subtitle',
                          '<ul><li>Point 1</li><li>Point 2</li></ul>')

# Close
deck.add_thank_you()

deck.save('output.pptx')
```

### Step 3: Run the Script

Execute the script with Python to generate the `.pptx` file.

## Layout Methods — All 17 Types

### 1. add_cover_color_block(label, title, date, partner=False)
Navy background opening slide.
```python
deck.add_cover_color_block('BACKBASE', 'Presentation\nTitle', 'April 2026')
```

### 2. add_cover_photo(label, title, date, image_path=None, partner=None)
Cover with photo or navy variant.
```python
# With photo:
deck.add_cover_photo('LABEL', 'Title', 'April 2026', image_path='images/photo.jpg')
# Navy variant (no photo):
deck.add_cover_photo('LABEL', 'Title', 'April 2026')
```

### 3. add_chapter_numbered(theme, number, label, title, subtitle)
Numbered section divider. `theme`: 'navy' | 'blue'.
```python
deck.add_chapter_numbered('navy', '01', 'CHAPTER', 'Section Title', 'Description')
```

### 4. add_chapter_standard(theme, label, title, subtitle)
Full-width section divider without number.
```python
deck.add_chapter_standard('navy', 'SECTION', 'Title', 'Description')
```

### 5. add_toc(label, title, items, numbered=True)
Table of contents.
```python
deck.add_toc('AGENDA', 'Contents', ['Item 1', 'Item 2', 'Item 3'], numbered=True)
```

### 6. add_content_standard(theme, label, title, subtitle, body)
General-purpose content. `theme`: 'light' | 'dark'. Body accepts HTML (converted to text).
```python
deck.add_content_standard('light', 'TOPIC', 'Title', 'Subtitle',
                          '<ul><li>Point 1</li><li>Point 2</li></ul>')
```

### 7. add_content_columns(label, title, columns)
2-5 equal columns. Each column: `{'subtitle': '...', 'body': '...'}`.
```python
deck.add_content_columns('PILLARS', 'Our Approach', [
    {'subtitle': 'Column 1', 'body': 'Description'},
    {'subtitle': 'Column 2', 'body': 'Description'},
    {'subtitle': 'Column 3', 'body': 'Description'}
])
```

### 8. add_overview_about(label, title, subtitle, image_path, stats)
Company overview with 5 stats. Stats: `[{'value': '+150', 'label': 'Customers'}]`.
```python
deck.add_overview_about('ABOUT', 'Backbase', 'Description', None,
                        [{'value': '+150', 'label': 'Customers'}, {'value': '50%', 'label': 'R&D'}])
```

### 9. add_overview_stats(label, title, subtitle, image_path, stats)
Case study with 4 stats.
```python
deck.add_overview_stats('CASE STUDY', 'Client', 'Description', None,
                        [{'value': '$530B', 'label': 'Assets'}])
```

### 10. add_product(label, title, subtitle, body, image_path, image_bg=True)
Product showcase with screenshot right.
```python
deck.add_product('PRODUCT', 'Feature', 'Subtitle',
                 '<ul><li>Feature 1</li></ul>', 'images/screenshot.png')
```

### 11. add_statement(accent, label, text, variant=None)
Large text on colored band. `accent`: 'blue' | 'red'. `variant`: None | 'dark'.
```python
deck.add_statement('blue', 'VISION', 'Bold statement with key message')
```

### 12. add_statement_stat(accent, label, stat, text, source)
Big number + description.
```python
deck.add_statement_stat('blue', 'IMPACT', '70%', 'Description of the metric', 'McKinsey 2025')
```

### 13. add_testimonial(logo, quote, name, role, image_path)
Customer quote.
```python
deck.add_testimonial('COMPANY', 'The quote text', 'Person Name', 'Title, Company')
```

### 14. add_team(label, title, members)
Team grid. Members: `[{'name': '...', 'role': '...', 'image': '...'}]`.
```python
deck.add_team('TEAM', 'Our Team', [
    {'name': 'Alice', 'role': 'Engineer'},
    {'name': 'Bob', 'role': 'Designer'}
])
```

### 15. add_agenda_table(label, title, headers, rows)
Navy table with optional highlighted rows.
```python
deck.add_agenda_table('SCHEDULE', 'Day 1',
    ['Session', 'Time', 'Speaker'],
    [{'cells': ['Welcome', '09:00', 'Alice'], 'highlight': True}])
```

### 16. add_roadmap(label, title, months, rows)
Gantt timeline. Bar colors: 'blue' | 'navy' | 'cyan' | 'red'.
```python
deck.add_roadmap('ROADMAP', '2026 Roadmap', ['Q1','Q2','Q3','Q4'], [
    {'label': 'Phase 1', 'bars': [{'start': 0, 'duration': 2, 'color': 'blue', 'label': 'Discovery'}]}
])
```

### 17. add_thank_you()
Closing slide.
```python
deck.add_thank_you()
```

## Google Slides Compatibility

The builder enforces these rules automatically:
- Text width buffer (+15%) to prevent wrapping on import
- `MSO_AUTO_SIZE.NONE` on all text frames
- Solid fills only (no gradients)
- Libre Franklin font (available on Google Fonts)
- All units in inches/EMU precision
- No shadows, rotated text, or complex effects

## Output

Save to engagement output directory:
```python
deck.save(f'{output_dir}/{deck_name}.pptx')
```

The `.pptx` opens directly in Google Slides or Microsoft PowerPoint.
