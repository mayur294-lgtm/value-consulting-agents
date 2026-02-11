# Generate Assessment HTML Dashboard

Generate a premium interactive HTML dashboard from the engagement's markdown deliverables and upstream JSON artifacts. This skill produces a single self-contained HTML file with a Future UI-inspired design — dark sidebar navigation, bento grids, dark feature sections, phone-frame prototypes, journey visualizations, scroll-reveal animations, and business line differentiation.

**Do NOT use this skill for general presentations.** For slide decks, Innovation Day pitches, or any non-assessment deliverable, use `/presentation-v2` instead. This skill is exclusively for Detailed Assessment / Ignite Assess engagements that follow the 7-act narrative structure.

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

## Output

A single self-contained HTML file: `{engagement_code}_Consolidated_Assessment_Interactive.html`

---

## CSS Design System

The complete CSS below is extracted from the proven NFIS reference design and generalized for reuse. Copy it verbatim into the `<style>` tag of the output HTML.

```css
/* ══════════════════════════ CSS CUSTOM PROPERTIES ══════════════════════════ */
:root {
  --bg: #F8FAFC; --card: #FFFFFF; --border: #E2E8F0; --text: #0F172A; --muted: #64748B; --dim: #94A3B8;
  --L0: #DC2626; --L1: #EA580C; --L2: #0891B2; --L3: #059669; --L4: #2563EB;
  --accent: #2563EB; --accent-light: #DBEAFE;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04); --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --shadow-lg: 0 10px 25px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
  --radius: 12px; --radius-lg: 16px;
  --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ══════════════════════════ RESET & BASE ══════════════════════════ */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; font-size: 15px; }
.wrap { max-width: 1360px; margin: 0 auto; padding: 0 48px 100px; margin-left: 260px; }
h2 { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 8px; }
h3 { font-size: 1.2rem; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.2px; }
h4 { font-size: 0.95rem; font-weight: 700; margin-bottom: 4px; }

/* ══════════════════════════ LEFT SIDEBAR NAV ══════════════════════════ */
.sidebar { position: fixed; top: 0; left: 0; width: 250px; height: 100vh; background: #1A1F36; z-index: 200; display: flex; flex-direction: column; overflow-y: auto; box-shadow: 4px 0 24px rgba(0,0,0,0.12); }
.sidebar-brand { padding: 28px 24px 20px; border-bottom: 1px solid rgba(255,255,255,0.08); background: linear-gradient(180deg, rgba(26,86,255,0.08) 0%, transparent 100%); }
.sidebar-brand-logo { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px; color: rgba(255,255,255,0.4); margin-bottom: 6px; }
.sidebar-brand-title { font-size: 1.1rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px; line-height: 1.3; }
.sidebar-brand-sub { font-size: 0.7rem; color: rgba(255,255,255,0.35); margin-top: 4px; }
.sidebar-nav { flex: 1; padding: 16px 0; }
.tab-btn { display: flex; align-items: center; gap: 12px; width: 100%; padding: 12px 24px; font-size: 0.82rem; font-weight: 600; color: rgba(255,255,255,0.55); cursor: pointer; border: none; background: none; white-space: nowrap; transition: all 0.25s ease; font-family: inherit; text-align: left; position: relative; border-left: 3px solid transparent; }
.tab-btn:hover { color: rgba(255,255,255,0.9); background: rgba(255,255,255,0.04); border-left-color: rgba(26,86,255,0.3); }
.tab-btn.active { color: #FFFFFF; background: rgba(26,86,255,0.12); border-left-color: #1A56FF; }
.tab-btn .tab-num { display: inline-flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.4); font-size: 0.6rem; font-weight: 800; width: 22px; height: 22px; border-radius: 6px; flex-shrink: 0; transition: all 0.25s ease; }
.tab-btn:hover .tab-num { background: rgba(26,86,255,0.2); color: rgba(255,255,255,0.7); }
.tab-btn.active .tab-num { background: #1A56FF; color: #fff; box-shadow: 0 0 12px rgba(26,86,255,0.4); }
.tab-btn .tab-label { line-height: 1.3; }
.tab-btn.active::after { content: ''; position: absolute; right: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 20px; background: #1A56FF; border-radius: 3px 0 0 3px; box-shadow: 0 0 8px rgba(26,86,255,0.5); }
.sidebar-footer { padding: 16px 24px; border-top: 1px solid rgba(255,255,255,0.06); }
.sidebar-footer-text { font-size: 0.62rem; color: rgba(255,255,255,0.2); line-height: 1.4; }
.sidebar-divider { height: 1px; background: rgba(255,255,255,0.06); margin: 8px 20px; }

/* ══════════════════════════ PANELS ══════════════════════════ */
.panel { display: none; opacity: 0; transform: translateY(16px); transition: opacity 0.5s ease, transform 0.5s ease; padding-top: 48px; }
.panel.active { display: block; opacity: 1; transform: translateY(0); }
.section-header { margin-bottom: 48px; padding-bottom: 28px; border-bottom: 1px solid var(--border); position: relative; }
.section-header::after { content: ''; position: absolute; bottom: -1px; left: 0; width: 100px; height: 3px; background: linear-gradient(90deg, #1A56FF, #7B2FFF); border-radius: 2px; }
.section-header h2 { font-size: 2.2rem; font-weight: 900; letter-spacing: -1px; line-height: 1.1; }
.section-header .overline { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 3px; color: var(--accent); margin-bottom: 10px; background: linear-gradient(90deg, #1A56FF, #7B2FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.section-header p { max-width: 640px; font-size: 0.9rem; color: var(--muted); line-height: 1.7; }

/* ══════════════════════════ HERO — FUTURE UI STYLE ══════════════════════════ */
.hero { margin-left: 250px; position: relative; overflow: hidden; }
.hero-dark { background: #FAFAF8; padding: 0; position: relative; overflow: hidden; min-height: 90vh; display: flex; flex-direction: column; }
.hero-dark::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px; background: var(--border); z-index: 2; }
.hero-dark-inner { max-width: 1360px; margin: 0 auto; padding: 80px 48px 0; display: grid; grid-template-columns: 1fr 520px; gap: 32px; align-items: start; flex: 1; position: relative; z-index: 3; }
.hero-overline { font-size: 0.58rem; font-weight: 700; text-transform: uppercase; letter-spacing: 3px; color: var(--muted); margin-bottom: 28px; }
.hero-content h1 { font-size: 5.5rem; font-weight: 900; letter-spacing: -4px; line-height: 0.92; margin-bottom: 0; color: #0F172A; }
.hero-content h1 span { display: block; letter-spacing: -3px; color: #0F172A; }
.hero-sub { color: var(--muted); font-size: 0.92rem; margin: 28px 0 32px; line-height: 1.7; max-width: 420px; }
.hero-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 36px; }
.hero-tag { display: inline-block; padding: 8px 18px; border-radius: 24px; font-size: 0.68rem; font-weight: 600; border: 1px solid #D1D5DB; color: #6B7280; background: transparent; transition: all 0.25s ease; letter-spacing: 0.3px; }
.hero-tag:hover { border-color: #1A56FF; color: #1A56FF; }
.hero-alert { padding: 18px 22px; background: #FEF2F2; border: 1px solid #FECACA; border-radius: 16px; font-size: 0.84rem; color: #6B7280; line-height: 1.7; }
.hero-alert strong { color: #DC2626; }
.hero-visual { position: relative; overflow: hidden; border-radius: 24px 24px 0 0; height: 100%; min-height: 520px; }
.hero-visual-img { width: 100%; height: 100%; object-fit: cover; object-position: center 20%; display: block; border-radius: 24px 24px 0 0; }
.hero-float { position: absolute; z-index: 3; background: rgba(255,255,255,0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.6); border-radius: 14px; padding: 12px 18px; text-align: center; transition: transform 0.3s ease, box-shadow 0.3s ease; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.hero-float:hover { transform: translateY(-4px) scale(1.03); box-shadow: 0 8px 32px rgba(0,0,0,0.12); }
.hero-float-val { font-size: 1.2rem; font-weight: 800; color: #0F172A; line-height: 1.2; }
.hero-float-lbl { font-size: 0.56rem; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-top: 3px; }
.hero-stats-strip { background: #FFFFFF; border-bottom: 1px solid var(--border); padding: 0; }
.hero-stats-inner { max-width: 1360px; margin: 0 auto; padding: 0 48px; display: grid; grid-template-columns: repeat(5, 1fr); }
.hero-stat { text-align: center; padding: 32px 16px; position: relative; transition: background 0.2s ease; }
.hero-stat:hover { background: #F8FAFC; }
.hero-stat:not(:last-child)::after { content: ''; position: absolute; right: 0; top: 20%; height: 60%; width: 1px; background: var(--border); }
.hero-stat-val { font-size: 2rem; font-weight: 900; line-height: 1.1; transition: transform 0.3s ease; letter-spacing: -1px; }
.hero-stat:hover .hero-stat-val { transform: scale(1.08); }
.hero-stat-lbl { font-size: 0.58rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; margin-top: 6px; font-weight: 600; }

/* ── Bento Grid System ── */
.bento { display: grid; grid-template-columns: repeat(4, 1fr); grid-auto-rows: 180px; gap: 16px; margin-bottom: 48px; }
.bento-item { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 28px; overflow: hidden; position: relative; transition: all 0.35s cubic-bezier(0.4,0,0.2,1); }
.bento-item:hover { box-shadow: var(--shadow-lg); transform: translateY(-3px); }
.bento-2x1 { grid-column: span 2; } .bento-1x2 { grid-row: span 2; }
.bento-2x2 { grid-column: span 2; grid-row: span 2; }
.bento-stat { display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
.bento-stat-val { font-size: 3rem; font-weight: 900; letter-spacing: -2px; line-height: 1; }
.bento-stat-lbl { font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; font-weight: 600; }
.bento-dark { background: #0F172A; border-color: #1E293B; color: #FFFFFF; }
.bento-dark .bento-stat-lbl { color: rgba(255,255,255,0.4); }
.bento-accent { background: linear-gradient(135deg, #1A56FF, #3B82F6); border: none; color: #FFFFFF; }
.bento-accent .bento-stat-lbl { color: rgba(255,255,255,0.6); }

/* ── Dark Feature Section (Future UI style) ── */
.dark-feature { background: #0B0F1A; border-radius: 28px; padding: 72px 56px; margin: 56px 0; position: relative; overflow: hidden; }
.dark-feature::before { content: ''; position: absolute; top: -120px; right: -80px; width: 400px; height: 400px; background: radial-gradient(circle, rgba(26,86,255,0.12) 0%, transparent 70%); pointer-events: none; }
.dark-feature::after { content: ''; position: absolute; bottom: -100px; left: -60px; width: 300px; height: 300px; background: radial-gradient(circle, rgba(123,47,255,0.08) 0%, transparent 70%); pointer-events: none; }
.dark-feature-overline { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 3px; color: #1A56FF; margin-bottom: 16px; }
.dark-feature h3 { font-size: 2.8rem; font-weight: 900; letter-spacing: -2px; line-height: 1.05; color: #FFFFFF; margin-bottom: 12px; }
.dark-feature h3 span { background: linear-gradient(135deg, #1A56FF, #7B61FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.dark-feature-sub { color: rgba(255,255,255,0.4); font-size: 0.9rem; max-width: 520px; line-height: 1.7; margin-bottom: 48px; }
.dark-feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.dark-feature-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 20px; padding: 32px 28px; transition: all 0.35s ease; position: relative; overflow: hidden; }
.dark-feature-card:hover { background: rgba(255,255,255,0.07); border-color: rgba(26,86,255,0.25); transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.3); }
.dark-feature-card h4 { font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px; letter-spacing: -0.3px; }
.dark-feature-card p { font-size: 0.78rem; color: rgba(255,255,255,0.4); line-height: 1.6; }

/* ── Cards ── */
.card { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 28px; box-shadow: var(--shadow-sm); transition: all 0.35s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden; }
.card:hover { box-shadow: 0 8px 30px rgba(0,0,0,0.08); transform: translateY(-3px); }
.card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #1A56FF, #7B2FFF, #1A56FF); transform: scaleX(0); transform-origin: left; transition: transform 0.4s ease; opacity: 0.7; }
.card:hover::before { transform: scaleX(1); }
.card-grid { display: grid; gap: 16px; }
.card-grid-2 { grid-template-columns: repeat(2, 1fr); }
.card-grid-3 { grid-template-columns: repeat(3, 1fr); }
.card-grid-4 { grid-template-columns: repeat(4, 1fr); }

/* ── Metric Cards (dark) ── */
.metric-card { background: #0F172A; border: 1px solid #1E293B; border-radius: 20px; padding: 28px 20px; text-align: center; transition: all 0.35s ease; position: relative; overflow: hidden; }
.metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(26,86,255,0.08); border-color: rgba(26,86,255,0.15); }
.metric-val { font-size: 2rem; font-weight: 900; line-height: 1; margin-bottom: 6px; letter-spacing: -1px; color: #FFFFFF; transition: transform 0.3s ease; }
.metric-card:hover .metric-val { transform: scale(1.05); }
.metric-lbl { font-size: 0.65rem; color: rgba(255,255,255,0.35); line-height: 1.4; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }

/* ── Persona Cards ── */
.persona-card { background: var(--card); border: 1px solid var(--border); border-radius: 20px; overflow: hidden; cursor: pointer; transition: all 0.35s ease; }
.persona-card:hover { box-shadow: 0 12px 32px rgba(0,0,0,0.08); transform: translateY(-4px); }
.persona-header { padding: 24px 28px; display: flex; align-items: center; gap: 18px; transition: background 0.3s ease; }
.persona-card:hover .persona-header { background: rgba(26,86,255,0.02); }
.persona-avatar { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: 800; color: #fff; flex-shrink: 0; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: box-shadow 0.3s ease, transform 0.3s ease; }
.persona-card:hover .persona-avatar { box-shadow: 0 6px 20px rgba(0,0,0,0.25); transform: scale(1.08); }
.persona-name { font-weight: 800; font-size: 1rem; letter-spacing: -0.2px; }
.persona-role { font-size: 0.75rem; color: var(--muted); font-weight: 600; }
.persona-body { padding: 0 28px 24px; display: none; }
.persona-card.open .persona-body { display: block; }
.expand-hint { font-size: 0.68rem; color: var(--accent); font-weight: 700; padding: 0 28px 14px; text-transform: uppercase; letter-spacing: 0.5px; }
.persona-card.open .expand-hint { display: none; }

/* ── Expandable Sections ── */
.expandable { border: 1px solid var(--border); border-radius: 16px; overflow: hidden; margin-bottom: 12px; background: var(--card); transition: all 0.35s ease; }
.expandable:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.05); border-color: rgba(26,86,255,0.15); }
.expand-header { padding: 18px 24px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.25s ease; font-weight: 700; font-size: 0.9rem; }
.expand-header:hover { background: #F8FAFC; }
.expand-arrow { transition: transform 0.3s; font-size: 0.8rem; color: var(--muted); }
.expandable.open .expand-arrow { transform: rotate(180deg); }
.expandable.open { border-color: rgba(26,86,255,0.2); box-shadow: 0 4px 16px rgba(26,86,255,0.06); }
.expand-body { max-height: 0; overflow: hidden; transition: max-height 0.4s ease, padding 0.3s ease; }
.expandable.open .expand-body { max-height: 2000px; }
.expand-content { padding: 0 24px 24px; }
.expand-content p, .expand-content li { font-size: 0.85rem; color: var(--muted); line-height: 1.7; }

/* ── Score Badges ── */
.score-badge { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 8px; font-weight: 800; font-size: 0.85rem; color: #fff; transition: transform 0.2s ease, box-shadow 0.2s ease; }
.score-badge:hover { transform: scale(1.15); }
.score-badge.s0 { background: var(--L0); } .score-badge.s1 { background: var(--L1); }
.score-badge.s2 { background: var(--L2); } .score-badge.s3 { background: var(--L3); }
.score-badge.s4 { background: var(--L4); }
.score-bar { height: 8px; border-radius: 4px; background: var(--border); overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease; }

/* ── Heatmap Grid (Capability Map) ── */
.heatmap-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }
.hm-cell { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 16px 12px; text-align: center; cursor: pointer; transition: all 0.3s ease; }
.hm-cell:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,0.08); }
.hm-cell.selected { outline: 2px solid var(--accent); outline-offset: -1px; box-shadow: 0 0 0 4px rgba(26,86,255,0.1); }
.hm-cell .hm-score { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 900; font-size: 0.95rem; color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.15); transition: transform 0.3s ease; }
.hm-cell:hover .hm-score { transform: scale(1.15); }
.hm-cell .hm-id { font-size: 0.62rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.hm-cell .hm-name { font-size: 0.72rem; font-weight: 700; color: var(--text); margin-top: 4px; line-height: 1.3; }
.hm-detail-panel { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 28px; margin-top: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); display: none; }
.hm-detail-panel.visible { display: block; }

/* ── Timeline (Roadmap) ── */
.timeline { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; position: relative; }
.timeline::before { content: ''; position: absolute; top: 40px; left: 5%; right: 5%; height: 3px; background: linear-gradient(90deg, var(--L1), var(--L2), var(--L3), var(--L4)); border-radius: 2px; z-index: 0; }
.timeline-phase { position: relative; z-index: 1; }
.phase-dot { width: 28px; height: 28px; border-radius: 50%; border: 3px solid; margin: 0 auto 16px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: box-shadow 0.3s ease, transform 0.3s ease; }
.timeline-phase:hover .phase-dot { transform: scale(1.3); }
.phase-card { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 24px; box-shadow: var(--shadow-sm); cursor: pointer; transition: all 0.35s ease; overflow: hidden; position: relative; }
.phase-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-3px); }
.phase-card h4 { font-size: 0.92rem; margin-bottom: 4px; font-weight: 800; letter-spacing: -0.2px; }
.phase-card .phase-time { font-size: 0.72rem; color: var(--muted); font-weight: 600; }
.phase-card .phase-cost { font-size: 0.88rem; font-weight: 800; color: var(--accent); margin-top: 8px; }
.phase-items { display: none; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.phase-card.open .phase-items { display: block; }
.phase-items li { font-size: 0.8rem; color: var(--muted); margin-bottom: 6px; padding-left: 16px; position: relative; line-height: 1.5; }
.phase-items li::before { content: ''; position: absolute; left: 0; top: 8px; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }

/* ── Phone Frame Prototypes ── */
.proto-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; }
.phone-frame { width: 280px; height: 580px; margin: 0 auto; background: #0D1117; border-radius: 36px; padding: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05); position: relative; overflow: hidden; }
.phone-frame::before { content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 120px; height: 28px; background: #0D1117; border-radius: 0 0 16px 16px; z-index: 10; }
.phone-screen { width: 100%; height: 100%; background: #FFFFFF; border-radius: 26px; overflow: hidden; position: relative; }

/* ── Journey Rail ── */
.journey-hero { background: linear-gradient(160deg, #0B0F1A 0%, #111827 50%, #0F172A 100%); border-radius: 28px; padding: 72px 56px; margin-bottom: 56px; position: relative; overflow: hidden; }
.journey-hero::before { content: ''; position: absolute; top: -50%; right: -20%; width: 600px; height: 600px; background: radial-gradient(circle, rgba(26,86,255,0.15) 0%, transparent 60%); pointer-events: none; }
.journey-rail { position: relative; padding-left: 72px; }
.journey-rail::before { content: ''; position: absolute; left: 29px; top: 0; bottom: 0; width: 3px; background: linear-gradient(to bottom, #1A56FF 0%, #059669 35%, #7B2FFF 70%, #EA580C 100%); border-radius: 2px; }
.journey-stage { position: relative; margin-bottom: 0; padding-bottom: 48px; }
.journey-stage:last-child { padding-bottom: 0; }
.journey-node { position: absolute; left: -72px; top: 0; width: 58px; height: 58px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: 900; color: #fff; z-index: 2; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
.journey-card { background: var(--card); border: 1px solid var(--border); border-radius: 20px; overflow: hidden; transition: all 0.35s ease; }
.journey-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-3px); }

/* ── Backbase Layer Tags ── */
.bb-layer { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 8px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin: 0 6px 6px 0; }
.bb-layer-engagement { background: rgba(26,86,255,0.08); color: #1A56FF; border: 1px solid rgba(26,86,255,0.15); }
.bb-layer-orchestration { background: rgba(5,150,105,0.08); color: #059669; border: 1px solid rgba(5,150,105,0.15); }
.bb-layer-intelligence { background: rgba(123,47,255,0.08); color: #7B2FFF; border: 1px solid rgba(123,47,255,0.15); }
.bb-layer-ai { background: rgba(234,88,12,0.08); color: #EA580C; border: 1px solid rgba(234,88,12,0.15); }
.bb-layer-integration { background: rgba(100,116,139,0.08); color: #64748B; border: 1px solid rgba(100,116,139,0.15); }

/* ── Use Case Cards ── */
.uc-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.uc-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; cursor: pointer; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); position: relative; }
.uc-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #1A56FF, #3B82F6); opacity: 0; transition: opacity 0.3s ease; }
.uc-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-3px); }
.uc-card:hover::before { opacity: 1; }

/* ── ROI Dashboard ── */
.roi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 20px; }
.roi-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; text-align: center; transition: all 0.3s ease; }
.roi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(26,86,255,0.08); }
.roi-card-val { font-size: 1.8rem; font-weight: 800; color: var(--accent); transition: transform 0.3s ease; }
.roi-card:hover .roi-card-val { transform: scale(1.06); }
.roi-card-lbl { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }

/* ── Scenario Toggle ── */
.scenario-toggle { display: inline-flex; background: #F1F5F9; border-radius: 10px; padding: 4px; gap: 4px; margin-bottom: 24px; }
.scenario-btn { padding: 8px 20px; border-radius: 8px; border: none; font-size: 0.82rem; font-weight: 700; cursor: pointer; background: none; color: var(--muted); transition: var(--transition); font-family: inherit; }
.scenario-btn.active { background: #fff; color: var(--accent); box-shadow: var(--shadow-sm); }

/* ── Confidence Badges ── */
.conf-badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; }
.conf-high { background: #D1FAE5; color: #059669; }
.conf-medium { background: linear-gradient(135deg, #FEF3C7, #FDE68A); color: #B45309; }
.conf-low { background: #FEF2F2; color: #DC2626; }

/* ── Scroll Reveal ── */
.reveal { opacity: 0; transform: translateY(40px); transition: opacity 0.8s cubic-bezier(0.16,1,0.3,1), transform 0.8s cubic-bezier(0.16,1,0.3,1); }
.reveal.visible { opacity: 1; transform: translateY(0); }

/* ── Traceability Highlight ── */
[data-trace-id] { cursor: pointer; transition: outline 0.2s ease, box-shadow 0.2s ease; }
.trace-highlight { outline: 2px solid #1A56FF !important; outline-offset: 2px; box-shadow: 0 0 12px rgba(26,86,255,0.2) !important; }

/* ── Custom Scrollbar ── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(26,86,255,0.15); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(26,86,255,0.3); }
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
::selection { background: rgba(26,86,255,0.12); color: inherit; }

/* ── Animations ── */
@keyframes fadeSlideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes floatParticle { 0%,100% { transform: translateY(0) translateX(0); } 25% { transform: translateY(-20px) translateX(10px); } 50% { transform: translateY(-10px) translateX(-5px); } 75% { transform: translateY(-30px) translateX(15px); } }
.bg-particle { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; opacity: 0.04; animation: floatParticle 20s ease-in-out infinite; }

/* ── Print Support ── */
@media print {
  .sidebar { display: none; }
  .hero { margin-left: 0; }
  .wrap { margin-left: 0; }
  .panel { display: block !important; opacity: 1 !important; transform: none !important; page-break-inside: avoid; }
  .expand-body { max-height: none !important; }
  body { font-size: 11px; }
}

/* ── Responsive ── */
@media (max-width: 1100px) {
  .sidebar { width: 200px; }
  .wrap { margin-left: 210px; }
  .hero { margin-left: 200px; }
  .hero-dark-inner { grid-template-columns: 1fr 360px; gap: 24px; padding: 60px 32px 0; }
  .hero-content h1 { font-size: 3.8rem; letter-spacing: -3px; }
  .bento { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 900px) {
  .sidebar { width: 60px; overflow: hidden; }
  .sidebar-brand-title, .sidebar-brand-sub, .sidebar-brand-logo, .tab-btn .tab-label, .sidebar-footer, .sidebar-divider { display: none; }
  .tab-btn { padding: 14px 0; justify-content: center; gap: 0; border-left: none; }
  .tab-btn .tab-num { width: 32px; height: 32px; font-size: 0.7rem; border-radius: 8px; }
  .wrap { margin-left: 70px; }
  .hero { margin-left: 60px; }
  .hero-dark-inner { grid-template-columns: 1fr; padding: 40px 24px 0; }
  .hero-content h1 { font-size: 3rem; }
  .bento { grid-template-columns: repeat(2, 1fr); }
  .card-grid-3, .card-grid-4 { grid-template-columns: 1fr 1fr; }
  .timeline { grid-template-columns: repeat(2, 1fr); }
  .roi-grid { grid-template-columns: repeat(2, 1fr); }
  .uc-grid { grid-template-columns: 1fr; }
  .proto-grid { grid-template-columns: 1fr; }
  .dark-feature-grid { grid-template-columns: 1fr 1fr; }
  .dark-feature { padding: 48px 32px; }
}
@media (max-width: 600px) {
  .sidebar { display: none; }
  .wrap { margin-left: 0; padding: 0 16px 60px; }
  .hero { margin-left: 0; }
  .hero-content h1 { font-size: 1.8rem; letter-spacing: -1px; }
  .hero-float { display: none; }
  .card-grid-2, .card-grid-3, .card-grid-4 { grid-template-columns: 1fr; }
  .bento { grid-template-columns: 1fr; grid-auto-rows: auto; }
  .timeline { grid-template-columns: 1fr; }
  .roi-grid { grid-template-columns: 1fr 1fr; }
  .dark-feature-grid { grid-template-columns: 1fr; }
  .dark-feature { padding: 36px 24px; margin: 32px 0; border-radius: 20px; }
}
```

---

## HTML Structure Template

Use this parameterized skeleton. Replace all `{{PLACEHOLDER}}` markers with engagement-specific content.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{CLIENT_NAME}} 7-Act Consolidated Assessment — Interactive Report</title>
<style>
/* [Insert full CSS from the CSS Design System section above] */
</style>
</head>
<body>

<!-- LEFT SIDEBAR NAVIGATION -->
<nav class="sidebar">
  <div class="sidebar-brand">
    <div class="sidebar-brand-logo">Backbase</div>
    <div class="sidebar-brand-title">{{CLIENT_NAME}} Assessment</div>
    <div class="sidebar-brand-sub">{{REPORT_SUBTITLE}}</div>
  </div>
  <div class="sidebar-nav">
    <button class="tab-btn active" data-tab="exec" onclick="switchTab('exec')">
      <span class="tab-num" style="background:rgba(255,255,255,0.15);">&#9670;</span>
      <span class="tab-label">Executive Summary</span>
    </button>
    <div class="sidebar-divider"></div>
    <button class="tab-btn" data-tab="act1" onclick="switchTab('act1')"><span class="tab-num">1</span><span class="tab-label">Strategic Alignment</span></button>
    <button class="tab-btn" data-tab="act2" onclick="switchTab('act2')"><span class="tab-num">2</span><span class="tab-label">The Vision</span></button>
    <button class="tab-btn" data-tab="act3" onclick="switchTab('act3')"><span class="tab-num">3</span><span class="tab-label">The Lighthouse</span></button>
    <button class="tab-btn" data-tab="act4" onclick="switchTab('act4')"><span class="tab-num">4</span><span class="tab-label">Deep-Dive</span></button>
    <button class="tab-btn" data-tab="act5" onclick="switchTab('act5')"><span class="tab-num">5</span><span class="tab-label">Capability Map</span></button>
    <button class="tab-btn" data-tab="act6" onclick="switchTab('act6')"><span class="tab-num">6</span><span class="tab-label">Roadmap</span></button>
    <button class="tab-btn" data-tab="act7" onclick="switchTab('act7')"><span class="tab-num">7</span><span class="tab-label">Benefits Case</span></button>
    <div class="sidebar-divider"></div>
    <button class="tab-btn" data-tab="journey" onclick="switchTab('journey')"><span class="tab-num" style="background:rgba(5,150,105,0.15);color:rgba(52,211,153,0.8);">&#10140;</span><span class="tab-label">Future Journey</span></button>
    <button class="tab-btn" data-tab="usecases" onclick="switchTab('usecases')"><span class="tab-num" style="background:rgba(123,47,255,0.15);color:rgba(167,139,250,0.8);">&#9733;</span><span class="tab-label">Use Cases</span></button>
  </div>
  <div class="sidebar-footer">
    <div class="sidebar-footer-text">Prepared by Backbase Value Consulting<br>{{ASSESSMENT_DATE}} | Confidential</div>
  </div>
</nav>

<!-- HERO SECTION -->
<section class="hero">
  <div class="hero-dark">
    <div class="hero-dark-inner">
      <div class="hero-content">
        <div class="hero-overline">Value Consulting Assessment &bull; {{ASSESSMENT_DATE}}</div>
        <h1>{{HERO_H1}}</h1>
        <p class="hero-sub">{{HERO_SUBTITLE}}</p>
        <div class="hero-tags">{{HERO_TAGS}}</div>
        <div class="hero-alert">{{HERO_ALERT}}</div>
      </div>
      <div class="hero-visual">
        <img class="hero-visual-img" src="{{HERO_IMAGE_URL}}" alt="Assessment Visual" loading="eager">
        {{HERO_FLOATS}}
      </div>
    </div>
  </div>
  <div class="hero-stats-strip">
    <div class="hero-stats-inner">{{HERO_STATS}}</div>
  </div>
</section>

<!-- MAIN CONTENT -->
<div class="wrap">
  <div class="panel active" id="panel-exec">{{EXEC_CONTENT}}</div>
  <div class="panel" id="panel-act1">{{ACT_1_CONTENT}}</div>
  <div class="panel" id="panel-act2">{{ACT_2_CONTENT}}</div>
  <div class="panel" id="panel-act3">{{ACT_3_CONTENT}}</div>
  <div class="panel" id="panel-act4">{{ACT_4_CONTENT}}</div>
  <div class="panel" id="panel-act5">{{ACT_5_CONTENT}}</div>
  <div class="panel" id="panel-act6">{{ACT_6_CONTENT}}</div>
  <div class="panel" id="panel-act7">{{ACT_7_CONTENT}}</div>
  <div class="panel" id="panel-journey">{{JOURNEY_CONTENT}}</div>
  <div class="panel" id="panel-usecases">{{USECASES_CONTENT}}</div>
</div>

<script>
/* [Insert full JavaScript from the JavaScript section below] */
</script>
</body>
</html>
```

---

## JavaScript

Include this JavaScript verbatim in the `<script>` tag.

```javascript
/* ── TAB SWITCHING ── */
function switchTab(id) {
  document.querySelectorAll('.tab-btn').forEach(function(b){ b.classList.remove('active'); });
  document.querySelectorAll('.panel').forEach(function(p){ p.classList.remove('active'); });
  document.querySelector('[data-tab="'+id+'"]').classList.add('active');
  var panel = document.getElementById('panel-'+id);
  panel.classList.add('active');
  document.querySelectorAll('.section-divider').forEach(function(d){ d.style.display = 'none'; });
  window.scrollTo({top: 0, behavior:'smooth'});
  setTimeout(function(){
    panel.querySelectorAll('.reveal').forEach(function(el){ el.classList.remove('visible'); });
    setTimeout(function(){
      panel.querySelectorAll('.reveal').forEach(function(el){
        var rect = el.getBoundingClientRect();
        if(rect.top < window.innerHeight) el.classList.add('visible');
      });
    }, 100);
  }, 50);
}

/* ── EXPANDABLE SECTIONS ── */
document.addEventListener('click', function(e) {
  var header = e.target.closest('.expand-header');
  if (header) { header.closest('.expandable').classList.toggle('open'); }
  var persona = e.target.closest('.persona-card');
  if (persona && !e.target.closest('a')) { persona.classList.toggle('open'); }
  var phaseCard = e.target.closest('.phase-card');
  if (phaseCard) { phaseCard.classList.toggle('open'); }
  var ucCard = e.target.closest('.uc-card');
  if (ucCard && !e.target.closest('a')) { ucCard.classList.toggle('open'); }
});

/* ── SCROLL REVEAL (IntersectionObserver) ── */
(function initReveal(){
  var els = document.querySelectorAll('.reveal, .card, .metric-card, .persona-card, .pillar-card, .expandable, .hm-cell, .uc-card, .uc-stat-card, .proto-wrap');
  if(!('IntersectionObserver' in window)){ els.forEach(function(e){e.classList.add('visible');}); return; }
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if(entry.isIntersecting){
        entry.target.classList.add('visible');
        entry.target.style.opacity='1';
        entry.target.style.transform='translateY(0)';
      }
    });
  }, {threshold: 0.05, rootMargin: '0px 0px -30px 0px'});
  els.forEach(function(el){
    if(!el.closest('.hero')){ el.style.opacity='0'; el.style.transform='translateY(30px)'; el.style.transition='opacity 0.7s cubic-bezier(0.16,1,0.3,1), transform 0.7s cubic-bezier(0.16,1,0.3,1)'; io.observe(el); }
  });
})();

/* ── CAPABILITY HEATMAP ENGINE ── */
var scoreColors = ['#DC2626','#EA580C','#0891B2','#059669','#2563EB'];
var scoreLabels = ['L0: Non-Existent','L1: Ad-Hoc','L2: Developing','L3: Defined','L4: Optimized'];

function renderHeatmap(containerId, caps) {
  var container = document.getElementById(containerId);
  if (!container || !caps) return;
  var html = '';
  caps.forEach(function(c, i) {
    html += '<div class="hm-cell" data-idx="'+i+'" onclick="selectCell(this,\''+containerId+'\','+i+')">';
    html += '<div class="hm-score" style="background:'+scoreColors[c.score]+';">'+c.score+'</div>';
    html += '<div class="hm-id">'+c.id+'</div>';
    html += '<div class="hm-name">'+c.name+'</div>';
    html += '</div>';
  });
  container.innerHTML = html;
}

function selectCell(el, src, idx) {
  document.querySelectorAll('.hm-cell').forEach(function(c){ c.classList.remove('selected'); });
  el.classList.add('selected');
  var allCaps = window['caps_'+src] || [];
  var cap = allCaps[idx];
  if (!cap) return;
  var panel = document.getElementById('hm-detail');
  var content = document.getElementById('hm-detail-content');
  content.innerHTML = '<div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">'+
    '<div class="score-badge s'+cap.score+'">'+cap.score+'</div>'+
    '<div><strong style="font-size:1.05rem;">'+cap.id+': '+cap.name+'</strong>'+
    '<div style="font-size:0.8rem;color:var(--muted);">Domain: '+cap.domain+' | Score: '+scoreLabels[cap.score]+'</div></div></div>'+
    '<div style="margin-top:8px;"><div class="score-bar" style="width:100%;max-width:300px;"><div class="score-bar-fill" style="width:'+(cap.score/4*100)+'%;background:'+scoreColors[cap.score]+';"></div></div></div>';
  panel.classList.add('visible');
  panel.scrollIntoView({behavior:'smooth', block:'nearest'});
}

/* ── TRACEABILITY ENGINE ── */
document.addEventListener('mouseover', function(e) {
  var traced = e.target.closest('[data-trace-id]');
  if (traced) {
    var traceId = traced.getAttribute('data-trace-id');
    document.querySelectorAll('[data-trace-id="'+traceId+'"]').forEach(function(el){
      el.classList.add('trace-highlight');
    });
  }
});
document.addEventListener('mouseout', function(e) {
  var traced = e.target.closest('[data-trace-id]');
  if (traced) {
    document.querySelectorAll('.trace-highlight').forEach(function(el){
      el.classList.remove('trace-highlight');
    });
  }
});

/* ── FLOATING BACKGROUND PARTICLES ── */
(function initParticles(){
  var colors = ['rgba(26,86,255,0.08)','rgba(123,47,255,0.06)','rgba(5,150,105,0.05)'];
  for(var i=0;i<6;i++){
    var p = document.createElement('div');
    p.className = 'bg-particle';
    p.style.width = (6+Math.random()*12)+'px';
    p.style.height = p.style.width;
    p.style.left = (10+Math.random()*80)+'%';
    p.style.top = (10+Math.random()*80)+'%';
    p.style.background = colors[i%3];
    p.style.animationDelay = (Math.random()*10)+'s';
    p.style.animationDuration = (15+Math.random()*15)+'s';
    document.body.appendChild(p);
  }
})();
```

---

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
  <button class="scenario-btn active" onclick="switchScenario('conservative',this)">Conservative</button>
  <button class="scenario-btn" onclick="switchScenario('base',this)">Base Case</button>
  <button class="scenario-btn" onclick="switchScenario('aggressive',this)">Aggressive</button>
</div>
<div class="roi-grid">
  <div class="roi-card"><div class="roi-card-val">{{NPV}}</div><div class="roi-card-lbl">Net Present Value</div></div>
  <div class="roi-card"><div class="roi-card-val">{{ROI}}</div><div class="roi-card-lbl">ROI</div></div>
  <div class="roi-card"><div class="roi-card-val">{{PAYBACK}}</div><div class="roi-card-lbl">Payback Period</div></div>
  <div class="roi-card"><div class="roi-card-val">{{IRR}}</div><div class="roi-card-lbl">IRR</div></div>
</div>
<!-- Individual levers with expandable MECE breakdown -->
<div style="margin-top:32px;">
  <div style="border:1px solid var(--border);border-radius:16px;margin-bottom:12px;overflow:hidden;background:var(--card);" data-trace-id="BEN-{{ID}}">
    <div onclick="this.parentElement.classList.toggle('open')" style="padding:18px 24px;display:flex;align-items:center;gap:12px;cursor:pointer;">
      <span style="font-size:0.7rem;font-weight:800;color:var(--accent);min-width:28px;">{{NUM}}</span>
      <span style="font-weight:700;font-size:0.9rem;flex:1;">{{LEVER_NAME}}</span>
      <span style="font-weight:800;font-size:0.95rem;color:{{COLOR}};min-width:80px;text-align:right;">{{VALUE}}</span>
      <span style="color:var(--muted);font-size:0.8rem;">&#9660;</span>
    </div>
    <div style="max-height:0;overflow:hidden;transition:max-height 0.4s ease;">
      <div style="padding:0 24px 24px;">
        <!-- Current → Change → Target MECE boxes + linked capabilities -->
      </div>
    </div>
  </div>
</div>
```

### Panel-to-Component Mapping

| Panel | Primary Components | Secondary Components |
|---|---|---|
| Executive Summary | Bento Grid, Metric Cards | Dark Feature (transformation pillars) |
| Act 1 — Strategic Alignment | Dark Feature, Expandable | Metric Cards (pain point counts) |
| Act 2 — The Vision | Dark Feature, Cards | Bento Grid (vision stats) |
| Act 3 — The Lighthouse | Persona Cards, Cards | Expandable (persona details) |
| Act 4 — Deep-Dive | Expandable, Cards | Metric Cards (deep-dive findings) |
| Act 5 — Capability Map | Heatmap, Score Badges | Expandable (gap details) |
| Act 6 — Roadmap | Timeline, Cards | Metric Cards (investment summary) |
| Act 7 — Benefits Case | ROI Levers, ROI Grid | Scenario Toggle, Bento Grid |
| Future Journey | Journey Rail | Backbase Layer Tags |
| Use Cases | Use Case Cards, Phone Prototypes | Expandable |

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

## Generation Process

### Step 1: Inventory
Scan the outputs directory. Report what was found and what's missing.

### Step 2: Extract Hero Data
From `executive_summary.md`: 5 headline metrics, transformation arc, cost-of-inaction stat, floating card stats.

### Step 3: Identify Business Lines
From discovery/persona data: identify 2-3 business lines, assign colors.

### Step 4: Build Each Act Panel
For each of the 10 panels: read content from `assessment_report.md`, select components from the registry, inject content, add trace IDs, apply business line tags.

### Step 5: Build Capability Heatmap Data
Extract scores from assessment JSON. Generate JavaScript arrays per business line. Embed `<script>` blocks calling `renderHeatmap()`.

### Step 6: Build ROI Dashboard
Extract lever data from ROI model. Generate 3 scenario datasets. Wire up scenario toggle.

### Step 7: Build Journey Visualization
Map future-state journey: 5-7 stages, before/after, Backbase layers, metrics.

### Step 8: Build Phone Prototypes
Top 3 use cases: phone-frame mockups with key screens.

### Step 9: Assemble
Combine into HTML template. Replace all `{{PLACEHOLDER}}` markers. Save as `{engagement_code}_Consolidated_Assessment_Interactive.html`.

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
- [ ] No `{{PLACEHOLDER}}` markers remain
- [ ] Responsive: correct at 1360px, 900px, 600px
- [ ] Print: all panels visible
- [ ] No external CSS/JS dependencies (fully self-contained)
- [ ] File saved as `{engagement_code}_Consolidated_Assessment_Interactive.html`
