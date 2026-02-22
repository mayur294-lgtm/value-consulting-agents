# Generate Assessment HTML Dashboard

Generate a premium interactive HTML dashboard from the engagement's markdown deliverables and upstream JSON artifacts. This skill produces a single self-contained HTML file with a Future UI-inspired design — dark sidebar navigation, bento grids, dark feature sections, phone-frame prototypes, journey visualizations, scroll-reveal animations, and business line differentiation.

**Do NOT use this skill for general presentations.** For slide decks, Innovation Day pitches, or any non-assessment deliverable, use `/presentation` instead. This skill is exclusively for Detailed Assessment / Ignite Assess engagements that follow the 7-act narrative structure.

**CRITICAL DESIGN RULE:** This dashboard uses a **LIGHT base theme** (`#F8FAFC` background). The body background is NEVER dark. Dark colors are used ONLY for:
- The sidebar (`#1A1F36`)
- Dark feature accent sections (`.dark-feature` with `#0B0F1A`)
- Metric cards (`.metric-card` with `#0F172A`)
- Journey swimlanes (`.journey-swimlane` with `#0F172A`)
- Waterfall containers (`.waterfall-container` with `#0F172A`)

If you find yourself setting `body { background: #0a1628 }` or any dark color as the page background — **STOP. You are not following the design system.**

## When to Invoke

- After the assembler agent has produced `assessment_report.md` and `executive_summary.md`
- For every Detailed Assessment / Ignite Assess engagement (MANDATORY)
- Can also be invoked standalone to regenerate the HTML from existing markdown

## Input Contract

The skill reads the following from the engagement outputs directory:

1. `assessment_report.md` — The 7-act narrative (canonical source)
2. `executive_summary.md` — The executive summary
3. `*_capability_assessment.json` or capability markdown — Capability scores
4. `*_roi_*.json` or ROI markdown — Financial model data
5. `*_roadmap_*.json` or roadmap markdown — Phased initiatives
6. `*_persona_*.json` or persona markdown — Persona library
7. `*_use_case_*.json` or use case markdown — Use case library
8. `market_context_validated.md` or `*_Market_Research.md` — Market context (if available)
9. `journey_maps.json` — Journey maps with swimlane data, friction callouts, and value leakage (if available, from Journey Builder Agent)

## Output

A single self-contained HTML file: `{engagement_code}_Consolidated_Assessment_Interactive.html`

---

## CSS, JS & HTML Template

The complete CSS, JavaScript, and HTML skeleton are in the template file. **Do NOT write CSS or JS yourself.**

### Step 0: Read the Template File (MANDATORY FIRST STEP)

Before doing ANYTHING else, read the template file using the Read tool:

**File:** `templates/presentations/assessment-dashboard-template.html`

This file is your complete HTML starting point. It contains:
- **~400 lines of CSS** — the full Future UI design system (sidebar, hero, bento, dark-feature, cards, metric-cards, personas, expandables, heatmap, timeline, phone-frames, journey-rail, swimlanes, friction-callouts, waterfall, ROI, scenario-toggle, confidence badges, traceability, scrollbar, animations, responsive breakpoints, print support)
- **~130 lines of JavaScript** — switchTab, expandable sections, scroll reveal, renderHeatmap, selectCell, traceability engine, journey swimlane toggle, floating particles
- **HTML skeleton** — sidebar with 10 tab buttons, hero section, and 10 panel containers with `{{PLACEHOLDER}}` markers

**Clone this file's content as your output HTML.** Then replace the `{{PLACEHOLDER}}` markers with engagement-specific content built using the Component Registry below.

**Rules:**
- **Do NOT modify the CSS.** Use the classes exactly as defined in the template.
- **Do NOT write your own CSS.** Do NOT add `<style>` blocks. Do NOT add inline styles that override the design system.
- **Do NOT add new colors.** The color palette is defined in `:root` CSS custom properties.
- **Do NOT modify the JavaScript functions.** You MAY add inline `<script>` blocks after the main `<script>` to populate heatmap data arrays and call `renderHeatmap()`.
- **Do NOT change the page background.** It MUST remain `var(--bg)` which is `#F8FAFC` (light).

---

<!--
  REMOVED: The CSS, HTML Structure, and JavaScript sections that were previously here
  have been moved to the template file (templates/presentations/assessment-dashboard-template.html).
  This prevents the model from paraphrasing CSS and ensures exact reproduction.

  The template file is the SINGLE SOURCE OF TRUTH for design.
  The skill file below contains the COMPONENT REGISTRY (how to build panel content)
  and the GENERATION PROCESS (step-by-step instructions).
-->

## Component Registry

Mapping from content types to HTML component patterns. When building each act panel, select the appropriate component based on the content type.

### 5.1 Section Header
Every act panel starts with this:
```html
<div class="section-header">
  <div class="overline">Act {{N}} — {{ACT_LABEL}}</div>
  <h2>{{ACT_TITLE}}</h2>
  <p>{{ACT_DESCRIPTION}}</p>
</div>
```

### 5.2 Metric Cards (for headline KPIs)
```html
<div class="card-grid card-grid-4">
  <div class="metric-card"><div class="metric-val" style="color:#DC2626">{{VALUE}}</div><div class="metric-lbl">{{LABEL}}</div></div>
</div>
```

### 5.3 Bento Grid (for overview stats)
```html
<div class="bento">
  <div class="bento-item bento-dark bento-2x1 bento-stat"><div class="bento-stat-val" style="color:#1A56FF">{{VALUE}}</div><div class="bento-stat-lbl">{{LABEL}}</div></div>
  <!-- Mix: bento-item, bento-2x1, bento-1x2, bento-2x2, bento-dark, bento-accent -->
</div>
```

### 5.4 Dark Feature Section (for strategic themes / pillars)
```html
<div class="dark-feature reveal">
  <div class="dark-feature-overline">{{OVERLINE}}</div>
  <h3>{{TITLE}} <span>{{HIGHLIGHTED_WORD}}</span></h3>
  <div class="dark-feature-sub">{{SUBTITLE}}</div>
  <div class="dark-feature-grid">
    <div class="dark-feature-card"><h4>{{CARD_TITLE}}</h4><p>{{CARD_DESC}}</p></div>
  </div>
</div>
```

### 5.5 Persona Cards
```html
<div class="card-grid card-grid-2">
  <div class="persona-card" data-trace-id="PERSONA-{{ID}}">
    <div class="persona-header">
      <div class="persona-avatar" style="background:linear-gradient(135deg,{{COLOR1}},{{COLOR2}})">{{INITIALS}}</div>
      <div><div class="persona-name">{{NAME}}</div><div class="persona-role">{{ROLE}}</div></div>
    </div>
    <div class="expand-hint">Click to expand</div>
    <div class="persona-body"><p>{{DESCRIPTION}}</p></div>
  </div>
</div>
```

### 5.6 Expandable Sections
```html
<div class="expandable">
  <div class="expand-header">{{HEADER_TEXT}}<span class="expand-arrow">&#9660;</span></div>
  <div class="expand-body"><div class="expand-content"><p>{{CONTENT}}</p></div></div>
</div>
```

### 5.7 Capability Heatmap (Act 5)
```html
<div id="hm-{{BL}}" class="heatmap-grid"></div>
<div id="hm-detail" class="hm-detail-panel"><div id="hm-detail-content"></div></div>
<script>
var caps_hm_{{BL}} = [{id:'{{ID}}', name:'{{NAME}}', score:{{SCORE}}, domain:'{{DOMAIN}}'}];
window['caps_hm-{{BL}}'] = caps_hm_{{BL}};
renderHeatmap('hm-{{BL}}', caps_hm_{{BL}});
</script>
```

### 5.8 Timeline (Roadmap)
```html
<div class="timeline">
  <div class="timeline-phase">
    <div class="phase-dot" style="border-color:{{COLOR}}"></div>
    <div class="phase-card">
      <h4>{{PHASE}}</h4>
      <div class="phase-time">{{TIMELINE}}</div>
      <div class="phase-cost">{{COST}}</div>
      <ul class="phase-items"><li data-trace-id="INI-{{P}}-{{N}}">{{INITIATIVE}}</li></ul>
    </div>
  </div>
</div>
```

### 5.9 Phone Frame Prototypes (top 3 use cases)
```html
<div class="proto-grid">
  <div style="text-align:center;">
    <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--muted);margin-bottom:16px;">{{LABEL}}</div>
    <div class="phone-frame">
      <div class="phone-screen">
        <div style="background:linear-gradient(135deg,{{C1}},{{C2}});padding:20px 16px 16px;color:#fff;">
          <div style="font-size:0.6rem;color:rgba(255,255,255,0.6);">9:41</div>
          <h4 style="font-size:1rem;font-weight:800;color:#fff;">{{TITLE}}</h4>
        </div>
        <div style="padding:16px;">
          <div style="background:#F8FAFC;border-radius:12px;padding:12px;margin-bottom:8px;">
            <div style="font-size:0.75rem;font-weight:700;">{{FEATURE}}</div>
            <div style="font-size:0.68rem;color:var(--muted);">{{DESC}}</div>
          </div>
        </div>
      </div>
    </div>
    <div style="font-size:0.78rem;color:var(--muted);margin-top:16px;">{{CAPTION}}</div>
  </div>
</div>
```

### 5.10 Journey Rail (future state)
```html
<div class="journey-rail">
  <div class="journey-stage reveal">
    <div class="journey-node" style="background:linear-gradient(135deg,{{C1}},{{C2}})">{{NUM}}</div>
    <div class="journey-card">
      <div style="padding:24px 28px;display:flex;align-items:center;gap:16px;">
        <div style="width:48px;height:48px;border-radius:14px;background:{{BG}};display:flex;align-items:center;justify-content:center;font-size:1.2rem;">{{ICON}}</div>
        <div><h4>{{TITLE}}</h4><div style="font-size:0.78rem;color:var(--muted);">{{DESC}}</div></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--border);">
        <div style="padding:20px 28px;border-right:1px solid var(--border);">
          <div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--L0);margin-bottom:8px;">Today</div>
          <div style="font-size:0.8rem;color:var(--muted);">{{BEFORE}}</div>
        </div>
        <div style="padding:20px 28px;">
          <div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--L3);margin-bottom:8px;">Future</div>
          <div style="font-size:0.8rem;color:var(--muted);">{{AFTER}}</div>
        </div>
      </div>
      <div style="padding:16px 28px;border-top:1px solid var(--border);display:flex;flex-wrap:wrap;gap:6px;">
        <span class="bb-layer bb-layer-engagement">Engagement Layer</span>
      </div>
    </div>
  </div>
</div>
```

### 5.11 ROI Lever Items (Act 7)
```html
<div class="scenario-toggle">
  <button class="scenario-btn" onclick="setScenario('conservative',this)">Conservative</button>
  <button class="scenario-btn active" onclick="setScenario('base',this)">Base</button>
  <button class="scenario-btn" onclick="setScenario('aspirational',this)">Aspirational</button>
</div>
<div class="roi-grid">
  <div class="roi-card"><div class="roi-card-val" id="roi-npv">{{NPV}}</div><div class="roi-card-lbl">5-Year NPV</div></div>
  <div class="roi-card"><div class="roi-card-val" id="roi-return">{{ROI}}</div><div class="roi-card-lbl">5-Year ROI</div></div>
  <div class="roi-card"><div class="roi-card-val" id="roi-payback">{{PAYBACK}}</div><div class="roi-card-lbl">Payback Period</div></div>
  <div class="roi-card"><div class="roi-card-val" id="roi-benefits">{{BENEFITS}}</div><div class="roi-card-lbl">5yr Gross Benefits</div></div>
</div>
<!-- Individual levers with expandable MECE breakdown — use .lever-card CSS -->
<div class="lever-card" data-trace-id="BEN-{{ID}}">
  <div class="lever-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="lever-num">{{NUM}}</span>
    <span class="lever-name">{{LEVER_NAME}}</span>
    <span class="lever-value" style="color:{{COLOR}};">{{VALUE}}</span>
    <span class="lever-arrow">&#9660;</span>
  </div>
  <div class="lever-body"><div class="lever-content">
    <div class="lever-mece">
      <div class="lever-mece-box" style="background:#FEF2F2;"><h5 style="color:#DC2626;">Current State</h5>{{CURRENT}}</div>
      <div class="lever-mece-box" style="background:#FFFBEB;"><h5 style="color:#D97706;">Change Driver</h5>{{CHANGE}}</div>
      <div class="lever-mece-box" style="background:#F0FDF4;"><h5 style="color:#059669;">Target State</h5>{{TARGET}}</div>
    </div>
    <div class="lever-benchmark"><strong>Benchmark:</strong> {{BENCHMARK}}</div>
    <div class="lever-capabilities">
      <span class="lever-cap-tag">{{CAP_ID}}</span>
    </div>
  </div></div>
</div>
```

### 5.12 Journey Swimlane (Act 4 — from `journey_maps.json`)
```html
<div id="journey-{{JOURNEY_ID}}" class="journey-swimlane reveal">
  <div class="journey-swimlane-title">{{JOURNEY_NAME}}</div>
  <div class="journey-swimlane-sub">{{LIFECYCLE_STAGE}} &bull; Total Value Leakage: <span style="color:#DC2626;font-weight:800;">{{TOTAL_LEAKAGE}}</span>/year</div>
  <div class="swimlane-toggle-group">
    <button class="swimlane-toggle-btn active-current" onclick="toggleJourney('{{JOURNEY_ID}}','current',this)">Current State</button>
    <button class="swimlane-toggle-btn" onclick="toggleJourney('{{JOURNEY_ID}}','future',this)">Backbase-Enabled</button>
  </div>
  <div class="swimlane-panel active" data-state="current">
    <div class="swimlane-grid" style="grid-template-columns:120px repeat({{PHASE_COUNT}},1fr);">
      <!-- Header row -->
      <div class="swimlane-header"></div>
      <div class="swimlane-header">{{PHASE_1}}</div>
      <div class="swimlane-header">{{PHASE_2}}</div>
      <!-- ... more phases ... -->
      <!-- Actor rows -->
      <div class="swimlane-actor">{{ACTOR_NAME}}</div>
      <div class="swimlane-cell {{FRICTION_CLASS}}" data-trace-id="{{PAIN_POINT_ID}}">
        {{ACTION}}
        <div class="swimlane-time">{{ACTIVE_TIME}} &bull; {{ELAPSED_TIME}}</div>
        <div class="swimlane-systems">{{SYSTEMS}}</div>
        <div class="swimlane-value-lost">-{{VALUE_LOST}}</div>
      </div>
      <!-- ... more cells ... -->
    </div>
  </div>
  <div class="swimlane-panel" data-state="future">
    <div class="swimlane-grid" style="grid-template-columns:120px repeat({{FUTURE_PHASE_COUNT}},1fr);">
      <!-- Future state grid with Backbase products and reduced steps -->
      <div class="swimlane-header"></div>
      <div class="swimlane-header" style="color:#34D399;">{{FUTURE_PHASE}}</div>
      <div class="swimlane-actor">{{ACTOR_NAME}}</div>
      <div class="swimlane-cell">
        {{FUTURE_ACTION}}
        <div class="swimlane-time" style="color:#34D399;">{{FUTURE_TIME}}</div>
        <div class="swimlane-systems" style="color:rgba(52,211,153,0.5);">{{BACKBASE_PRODUCTS}}</div>
      </div>
    </div>
  </div>
</div>
```

### 5.13 Friction Callout Cards (Act 4 — top 3-5 per journey)
```html
<div class="card-grid card-grid-2" style="margin-bottom:32px;">
  <div class="friction-callout severity-{{SEVERITY}}" data-trace-id="{{PAIN_POINT_ID}}">
    <div class="friction-callout-rank">Friction #{{RANK}}</div>
    <div class="friction-callout-title">{{FRICTION_TITLE}}</div>
    <div class="friction-callout-impact">{{DOLLAR_IMPACT}}<span style="font-size:0.65rem;color:var(--muted);font-weight:600;margin-left:4px;">/year</span></div>
    <div class="friction-callout-quote">"{{EVIDENCE_QUOTE}}" — {{ATTRIBUTION}}</div>
    <div class="friction-callout-fix"><strong>Fix:</strong> {{PROPOSED_FIX}} ({{BACKBASE_PRODUCTS}})</div>
    <div class="friction-callout-meta">
      <span class="friction-callout-tag">{{SEVERITY}}</span>
      <span class="friction-callout-tag">{{IMPACT_CATEGORY}}</span>
      <span class="friction-callout-tag">{{CAPABILITY_ID}}</span>
    </div>
  </div>
</div>
```

### 5.15 Journey Experience Map (Act 4 — holistic emotion curve from `journey_maps.json`)

This component renders the holistic journey experience map: headline insight cards, an SVG emotion curve with clickable stage markers, and expandable detail panels per stage. It is the visual centerpiece of Act 4 — the first thing the viewer sees before drilling into individual journey swimlanes.

**When to render:** If `journey_maps.json` contains a `journey_experience` section, render this component at the TOP of Act 4, before any per-journey swimlane content.

```html
<div class="jx reveal">
  <!-- Headline Insights (exactly 3) -->
  <div class="jx-headlines">
    <div class="jx-hl {{SEVERITY}}">
      <div class="jx-hl-icon" style="background:{{ICON_BG}};color:{{ICON_COLOR}};">{{ICON}}</div>
      <div>
        <div class="jx-hl-stat" style="color:{{STAT_COLOR}};">{{STAT}}</div>
        <div class="jx-hl-text">{{DESCRIPTION}}</div>
      </div>
    </div>
    <!-- Repeat for all 3 insights -->
  </div>

  <!-- SVG Emotion Curve Map -->
  <div class="jx-map">
    <svg viewBox="0 0 {{VIEWBOX_WIDTH}} {{VIEWBOX_HEIGHT}}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="emoGrad" x1="0" y1="0" x2="1" y2="0">
          <!-- Gradient stops derived from stage scores: green(high) → red(low) → purple(pending) -->
          <stop offset="{{OFFSET}}%" stop-color="{{COLOR}}"/>
        </linearGradient>
        <linearGradient id="areaFill" x1="0" y1="0" x2="1" y2="0">
          <stop offset="{{OFFSET}}%" stop-color="{{COLOR}}" stop-opacity="{{OPACITY}}"/>
        </linearGradient>
        <filter id="glw"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      </defs>

      <!-- Zone boundary (if stages span multiple zones) -->
      <line x1="{{ZONE_X}}" y1="24" x2="{{ZONE_X}}" y2="170" stroke="rgba(0,0,0,0.06)" stroke-width="1" stroke-dasharray="3,4"/>
      <text x="{{ZONE_1_CENTER}}" y="18" text-anchor="middle" fill="rgba(37,99,235,0.25)" font-size="8" font-weight="700" letter-spacing="2.5">{{ZONE_1_LABEL}}</text>
      <text x="{{ZONE_2_CENTER}}" y="18" text-anchor="middle" fill="rgba(190,24,93,0.25)" font-size="8" font-weight="700" letter-spacing="2.5">{{ZONE_2_LABEL}}</text>

      <!-- Subtle grid lines -->
      <line x1="60" y1="55" x2="960" y2="55" stroke="rgba(0,0,0,0.025)" stroke-width="1"/>
      <line x1="60" y1="100" x2="960" y2="100" stroke="rgba(0,0,0,0.025)" stroke-width="1"/>
      <line x1="60" y1="145" x2="960" y2="145" stroke="rgba(0,0,0,0.025)" stroke-width="1"/>
      <text x="28" y="38" fill="rgba(0,0,0,0.12)" font-size="7.5" font-weight="600">Great</text>
      <text x="30" y="168" fill="rgba(0,0,0,0.12)" font-size="7.5" font-weight="600">Poor</text>

      <!-- Area fill under curve -->
      <path d="{{AREA_PATH}}" fill="url(#areaFill)"/>
      <!-- Glow layer -->
      <path d="{{CURVE_PATH}}" fill="none" stroke="url(#emoGrad)" stroke-width="10" stroke-linecap="round" opacity="0.08"/>
      <!-- Main emotion curve -->
      <path d="{{CURVE_PATH}}" fill="none" stroke="url(#emoGrad)" stroke-width="3" stroke-linecap="round" filter="url(#glw)"/>
      <!-- Pending dashed extension (if pending stages exist) -->
      <path d="{{PENDING_PATH}}" fill="none" stroke="rgba(124,58,237,0.25)" stroke-width="2" stroke-dasharray="6,4" stroke-linecap="round"/>

      <!-- Stage markers (one per stage) -->
      <g class="jx-marker {{ACTIVE_IF_FIRST}}" data-stage="{{STAGE_ID}}" onclick="showStage({{STAGE_ID}})">
        <rect x="{{HIT_X}}" y="24" width="60" height="195" fill="transparent"/>
        <circle class="halo" cx="{{CX}}" cy="{{CY}}" r="18" fill="{{HALO_COLOR}}"/>
        <!-- Mapped stages: solid dot r=5. Pending stages: dashed outline r=4 -->
        <circle class="dot" cx="{{CX}}" cy="{{CY}}" r="{{DOT_R}}" fill="{{DOT_FILL}}" {{PENDING_STROKE}}/>
        <text class="stage-label" x="{{CX}}" y="195" text-anchor="middle" fill="{{LABEL_COLOR}}" font-size="10" font-weight="700">{{STAGE_NAME}}</text>
        <text x="{{CX}}" y="208" text-anchor="middle" fill="#94A3B8" font-size="7.5" font-weight="500">{{STAGE_SUBTITLE}}</text>
      </g>

      <!-- Score labels near dots (faint, unobtrusive) -->
      <text x="{{CX}}" y="{{SCORE_Y}}" text-anchor="middle" fill="{{SCORE_COLOR}}" font-size="8" font-weight="700">{{SCORE}}</text>
    </svg>
  </div>

  <!-- Detail Panels (one per stage, first is active) -->
  <div class="jx-panel {{ACTIVE_IF_FIRST}}" id="jxp-{{STAGE_ID}}">
    <div class="jx-panel-head">
      <div style="height:4px;background:{{STAGE_GRADIENT}};position:absolute;top:0;left:0;right:0;"></div>
      <div class="jx-panel-num" style="background:{{STAGE_GRADIENT}};">{{STAGE_ID}}</div>
      <div class="jx-panel-meta"><h3>{{EVOCATIVE_TITLE}}</h3><p class="sub">{{EVOCATIVE_SUBTITLE}}</p></div>
      <div class="jx-panel-score"><div class="sv" style="color:{{SCORE_COLOR}};">{{SCORE}}/10</div><div class="sl">Experience Score</div></div>
    </div>
    <div class="jx-narrative">{{NARRATIVE}}</div>
    <div class="jx-pains">
      <!-- Pain point cards -->
      <div class="jx-pain {{SEVERITY}}" data-trace-id="{{PAIN_POINT_ID}}">
        <span class="jx-sev {{SEVERITY}}">{{SEVERITY_ICON}} {{SEVERITY_LABEL}}</span>
        <h5>{{PAIN_TITLE}}</h5>
        <p>{{PAIN_DESCRIPTION}}</p>
        <div class="jx-impact">{{IMPACT}}</div>
      </div>
      <!-- UF / transformation arc gap cards -->
      <div class="jx-pain uf">
        <span class="jx-sev uf">{{ARC_ICON}} {{TRANSFORMATION_ARC_NAME}}</span>
        <h5>{{GAP_TITLE}}</h5>
        <p>{{GAP_DESCRIPTION}}</p>
        <div class="jx-impact">{{GAP_IMPACT}}</div>
      </div>
    </div>
    <div class="jx-quote">
      <p>"{{EVIDENCE_QUOTE}}"</p>
      <div class="src">— {{ATTRIBUTION}}</div>
    </div>
  </div>
  <!-- Repeat for each stage -->
</div>
```

**SVG Generation Rules:**
1. **Y-axis mapping:** Score 10 → y=35 (top), Score 1 → y=165 (bottom). Formula: `y = 200 - (score × 16.5)`
2. **X-axis spacing:** Distribute stages evenly across the viewbox width (1000). First stage at x=80, last mapped stage at x=720. Pending stages continue to x=950.
3. **Curve:** Use cubic bezier curves (C command) connecting the score points. The curve should feel organic, not angular.
4. **Area fill:** Close the curve path downward to y=172 to create the area fill polygon.
5. **Colors:** Map score to color — 8+: `#059669`, 5-7: `#7B2FFF`/`#D97706`, 3-4: `#EA580C`, 1-2: `#DC2626`. Pending: `#7C3AED`.
6. **Dot sizes:** Normal stages r=5. Critical stages (lowest score) r=6. Pending stages r=4 with dashed stroke, no fill.
7. **Score labels:** Faint numbers floating near dots. Use the score color at 40-55% opacity. Font size 8, weight 700.

### 5.14 Value Leakage Waterfall (Act 4 — per journey)
```html
<div class="waterfall-container reveal">
  <div class="waterfall-title">Value Leakage — {{JOURNEY_NAME}}</div>
  <div class="waterfall-sub">Step-by-step volume and value loss across the journey</div>
  <!-- One bar per step with friction -->
  <div class="waterfall-bar-row">
    <div class="waterfall-label">{{STEP_NAME}}<br><span style="font-size:0.6rem;color:rgba(255,255,255,0.4);">{{VOLUME_ENTERING}} entering</span></div>
    <div class="waterfall-bar-track">
      <div class="waterfall-bar-remaining" style="width:{{REMAINING_PCT}}%;"></div>
      <div class="waterfall-bar-leaked" style="width:{{LEAKED_PCT}}%;"></div>
    </div>
    <div class="waterfall-value">-{{VALUE_LOST}}</div>
  </div>
  <!-- ... more bars ... -->
  <div class="waterfall-cumulative"><span>Cumulative leakage: </span>{{TOTAL_LEAKAGE}}/year</div>
</div>
```

### Panel-to-Component Mapping

| Panel | Primary Components | Secondary Components |
|---|---|---|
| Executive Summary | Bento Grid, Metric Cards | Dark Feature (transformation pillars) |
| Act 1 — Strategic Alignment | Dark Feature, Expandable | Metric Cards (pain point counts) |
| Act 2 — The Vision | Dark Feature, Cards | Bento Grid (vision stats) |
| Act 3 — The Lighthouse | Persona Cards, Cards | Expandable (persona details) |
| Act 4 — Deep-Dive | **Journey Experience Map (5.15)**, Journey Swimlane, Friction Callouts, Value Waterfall, Expandable, Persona Cards | Before/After Toggle, Metric Cards (deep-dive findings) |
| Act 5 — Capability Map | Heatmap, Score Badges | Expandable (gap details) |
| Act 6 — Roadmap | Timeline, Cards | Metric Cards (investment summary) |
| Act 7 — Benefits Case | ROI Levers, ROI Grid | Scenario Toggle, Bento Grid |
| Future Journey | Journey Rail | Backbase Layer Tags |
| Use Cases | Use Case Cards, Phone Prototypes | Expandable |

---

## Transformation Arc Threading (MANDATORY)

Every act panel MUST include a Transformation Thread card that connects
the act's content to the overarching transformation arc. The thread
uses the transformation arc phrase from the assessment report.

| Act | Thread Focus | Card Content |
|-----|-------------|--------------|
| Exec | Overview | "Why we're here" — the arc phrase + 1-sentence framing |
| Act 1 | Why needed | How disconnected frontlines drive the need for transformation |
| Act 2 | What it looks like | The vision of the unified frontline |
| Act 3 | How we prove it | Phase 1 as proof of the transformation thesis |
| Act 4 | Where it breaks | Journey pain points as evidence of the broken state |
| Act 5 | What it requires | Capability gaps mapped to transformation pillars |
| Act 6 | How we build it | Roadmap phases as transformation milestones |
| Act 7 | Why it pays off | ROI as financial validation of the transformation |

**Format:** A card with gradient-text overline "TRANSFORMATION ARC", the arc
phrase as `<h3>`, and 2-3 sentences connecting the act's theme to the arc.

**Template placeholders:** The HTML template has `{{ACTN_TRANSFORMATION_THREAD}}`
placeholders in each panel. Fill these with the transformation thread card HTML.

---

## Traceability Enforcement

### Trace ID Convention

| Element Type | Pattern | Example |
|---|---|---|
| Pain Point | `PP-{LIFECYCLE}-{NUM}` | `PP-ACQ-01` |
| Capability Gap | `CAP-{LIFECYCLE}-{LAYER}-{NUM}` | `CAP-ACQ-F-01` |
| Use Case | `UC-{NUM}` | `UC-01` |
| ROI Benefit | `BEN-{NUM}` | `BEN-01` |
| Roadmap Initiative | `INI-{PHASE}-{NUM}` | `INI-P1-01` |
| Persona | `PERSONA-{ID}` | `PERSONA-CFO` |

Where:
- `{LIFECYCLE}` = `ACQ` (Acquisition), `ONB` (Onboarding), `SRV` (Servicing), `GRW` (Growth), `RET` (Retention)
- `{LAYER}` = `F` (Engagement), `O` (Orchestration), `I` (Intelligence), `A` (AI), `X` (Integration)
- `{PHASE}` = `P1`, `P2`, `P3`, `P4`

### How It Works

The JavaScript traceability engine adds hover-based cross-referencing. When you hover a pain point in Act 1 (`data-trace-id="PP-ACQ-01"`), ALL elements across the HTML sharing that ID get highlighted with a blue outline and glow.

### Implementation Rules

1. **Act 1**: Assign `PP-{LIFECYCLE}-{NUM}` to each pain point
2. **Act 5**: Assign `CAP-{LIFECYCLE}-{LAYER}-{NUM}` to heatmap cells, cross-reference pain point IDs
3. **Act 7**: Assign `BEN-{NUM}` to ROI levers, link to capability IDs inside lever details
4. **Act 6**: Assign `INI-{PHASE}-{NUM}` to initiatives, reference capability IDs
5. **Use Cases**: Assign `UC-{NUM}`, reference persona and capability IDs

---

## Business Line Differentiation

### Color Assignment

| Position | Color | Gradient | Use For |
|---|---|---|---|
| BL-1 | `#1A56FF` (Blue) | `#1A56FF` → `#3B82F6` | First business line |
| BL-2 | `#059669` (Green) | `#059669` → `#34D399` | Second business line |
| BL-3 | `#7B2FFF` (Purple) | `#7B2FFF` → `#A78BFA` | Third business line |
| BL-4 | `#EA580C` (Orange) | `#EA580C` → `#FB923C` | Fourth (if needed) |

### Consistent Application

- **Persona avatars**: Gradient of persona's primary business line
- **Metric card accents**: Business line color for metric values
- **Capability heatmap**: Group by business line with colored section headers
- **Use case cards**: Business line color as top accent gradient
- **ROI levers**: Progress bar colored by business line
- **Journey nodes**: Colored by primary business line served

### Card Accent Pattern (MANDATORY)

**NEVER use `border-left` colored ribbons on cards.** This creates a harsh, dated look.

Instead, use **top accent gradients** for all card-level color indicators:
```html
<!-- CORRECT: Top accent gradient -->
<div class="card" style="position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{{COLOR_START}},{{COLOR_END}});"></div>
  <!-- card content -->
</div>

<!-- WRONG: Left border ribbon — DO NOT USE -->
<div class="card" style="border-left:4px solid #DC2626;">
```

For comparison/contrast boxes (e.g., "Current vs. Target"):
```html
<!-- Use background tint + top accent, no left border -->
<div style="padding:14px 18px;background:#FEF2F2;border-radius:12px;position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#DC2626,#EF4444);border-radius:12px 12px 0 0;"></div>
  <!-- content -->
</div>
```

For fix/solution cards in Act 4 lifecycle panels, use green gradient:
```html
<div class="card" style="position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#059669,#10B981);"></div>
  <h4 style="color:#059669;">Unified Frontline Fix</h4>
</div>
```

**Exception:** Small inline UI elements inside phone-frame mockups MAY use `border-left` since they mimic mobile app list items.

---

## Market Context Integration

### When Market Context Exists

If `market_context_validated.md` or `*_Market_Research.md` is found:

1. **Competitive Landscape in Act 1**: Include a `dark-feature` section with competitor cards
2. **Industry Benchmark Bento Grid**: In Executive Summary, compare client vs industry averages
3. **Cost of Inaction in Hero Alert**: Surface the calculated cost-of-inaction stat
4. **Executive Metrics Bridge in Act 7**: Connect bottom-up ROI benefits to top-line KPIs

### When Market Context Does Not Exist

1. Do NOT block generation — proceed with all other content
2. Flag the absence in Executive Summary: _"Market context data was not available."_
3. Use ROI total for hero alert instead of cost-of-inaction
4. Skip the Executive Metrics Bridge in Act 7

---

## Incremental Write Protocol (MANDATORY)

Building the full HTML in-context accumulates 2,000-6,000 lines and risks context limits. Instead, build each panel incrementally and write partials to disk:

1. **Create partials directory:** `outputs/partials/` (create if it doesn't exist)
2. **For each panel (Steps 4-8):** Build the panel's HTML content (~200-800 lines), then **immediately write it to disk** as `outputs/partials/panel_{name}.html` before moving to the next panel. This keeps your working context at ~800-1200 lines per panel instead of accumulating the full dashboard.
3. **In Step 9 (Assemble):** Read the template, then read each partial file and inject it into the corresponding `{{PLACEHOLDER}}` marker. Write the final assembled HTML.

**Panel file naming convention:**
- `panel_hero.html` — Hero section + floating cards
- `panel_exec.html` — Executive Summary (Panel 0)
- `panel_act1.html` through `panel_act7.html` — Act panels
- `panel_next.html` — Next Steps panel
- `panel_appendix.html` — Appendix/traceability panel

**Rules:**
- NEVER hold more than 2 panels in working context simultaneously
- Write each partial BEFORE starting the next panel
- If a panel exceeds 1,000 lines, split it into sub-partials (e.g., `panel_act4_journey_experience.html`, `panel_act4_swimlanes.html`)

---

## Generation Process

### Step 1: Inventory
Scan the outputs directory. Report what was found and what's missing. Create `outputs/partials/` directory.

### Step 2: Extract Hero Data
From `executive_summary.md`: 5 headline metrics, transformation arc, cost-of-inaction stat, floating card stats. **Write `outputs/partials/panel_hero.html`.**

### Step 3: Identify Business Lines
From discovery/persona data: identify 2-3 business lines, assign colors.

### Step 4: Build Each Act Panel
For each of the 10 panels: read content from `assessment_report.md`, select components from the registry, inject content, add trace IDs, apply business line tags. **Write each panel to `outputs/partials/panel_{name}.html` immediately after building it.** Do NOT accumulate panels in context.

### Step 5: Build Capability Heatmap Data
Extract scores from assessment JSON. Generate JavaScript arrays per business line. Embed `<script>` blocks calling `renderHeatmap()`.

### Step 6: Build ROI Dashboard
Extract lever data from ROI model. Generate 3 scenario datasets. Wire up scenario toggle.

### Step 7: Build Journey Visualization (Two Layers)

**Layer 1 — Journey Experience Map (holistic):**
If `journey_maps.json` contains a `journey_experience` section: render the Journey Experience Map (5.15) at the TOP of Act 4, before any per-journey content. This is the visual centerpiece — the SVG emotion curve with headline insights and clickable stage detail panels. Generate the SVG using the stage scores and the generation rules in Component 5.15.

**Layer 2 — Per-Journey Swimlanes (individual):**
If `journey_maps.json` contains a `journeys[]` array: parse journey data and build per-journey swimlane components (5.12), friction callout cards (5.13), and value leakage waterfalls (5.14) for Act 4. Wire up the `toggleJourney()` function for before/after switching. Each journey gets its own swimlane container with a unique ID. Place these BELOW the Journey Experience Map.

**Layout within Act 4:**
1. Section header (5.1)
2. Journey Experience Map (5.15) — holistic emotion curve + stage panels
3. Section divider
4. Per-journey swimlanes (5.12) with friction callouts (5.13) and waterfalls (5.14)

**Fallback:** If `journey_maps.json` does NOT exist: fall back to the existing Journey Rail (5.10) for future-state journey visualization with 5-7 stages, before/after, Backbase layers, metrics.

### Step 8: Build Phone Prototypes
Top 3 use cases: phone-frame mockups with key screens.

### Step 9: Assemble from Partials
Read the template file from Step 0. Then read each partial file from `outputs/partials/` and inject its content into the corresponding `{{PLACEHOLDER}}` marker.

**CRITICAL:** When assembling from partials, the final file MUST use the template's CSS and JS EXACTLY as-is. The partials only contain the HTML content that replaces `{{PLACEHOLDER}}` markers. Do NOT regenerate CSS or JavaScript. Do NOT redesign the layout. The template already has all interactive components (heatmap, scenario toggle, journey switcher, scroll reveal, traceability hover, particles). You are only filling in the data.

Also write the final assembled file to `outputs/assessment_dashboard.html`. Delete the `outputs/partials/` directory after successful assembly.

### Step 10: Validate
Run through the Quality Checklist below.

---

## Quality Checklist

- [ ] All 7 act panels have content (no empty panels)
- [ ] Executive Summary panel is complete
- [ ] Hero section has 5 headline stats and alert
- [ ] Business lines identified and color-coded consistently
- [ ] Capability heatmap renders with correct scores
- [ ] ROI scenario toggle switches between 3 scenarios
- [ ] Timeline shows all roadmap phases
- [ ] At least 3 phone-frame prototypes exist
- [ ] Journey rail has all stages with before/after
- [ ] Traceability: hover on pain point highlights linked capabilities
- [ ] Journey Experience Map (5.15) renders at top of Act 4 with SVG emotion curve, 3 headline insights, and clickable stage panels (if `journey_experience` section exists in `journey_maps.json`)
- [ ] SVG emotion curve has correct score-to-Y mapping, gradient stroke, area fill, and glow layer
- [ ] All stage markers are clickable and reveal detail panels with narratives, pain points, and evidence quotes
- [ ] Pending stages (if any) have dashed outlines and "?" score labels
- [ ] Journey swimlanes render with all actors and friction color indicators (if `journey_maps.json` exists)
- [ ] Value leakage waterfall shows running cumulative total per journey (if `journey_maps.json` exists)
- [ ] Before/After toggle switches between current-state and future-state swimlane panels (if `journey_maps.json` exists)
- [ ] Friction callout cards show top 3-5 frictions per journey with $ impact and evidence quotes (if `journey_maps.json` exists)
- [ ] No `{{PLACEHOLDER}}` markers remain
- [ ] Responsive: correct at 1360px, 900px, 600px
- [ ] Print: all panels visible
- [ ] No external CSS/JS dependencies (fully self-contained)
- [ ] File saved as `{engagement_code}_Consolidated_Assessment_Interactive.html`
