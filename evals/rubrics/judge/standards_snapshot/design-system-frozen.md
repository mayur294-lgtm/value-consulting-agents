# FROZEN design-system snapshot (judge context)

Snapshot of the load-bearing Frontline-2026 rules as of 2026-06-23 (post PR #71).
Bump deliberately when the live standard changes — do NOT auto-sync, or green judge
scores will silently start lying. Live source of truth:
knowledge/design-system.md + presentations/frontline-2026/design-tokens.json.

## Palette (verified Theme 1)
Navy #041326 · Action Blue #3367FF · Cyan #69FEFF · Semantic Red #FF503C ·
Success Green #2ECC71 · BG Gray #F3F6F9 · Surface White #FFFFFF · Text Muted #6B7786.
Deprecated (never use): #001C3D, #1A5AFF, #3366FF (Theme-2/old blue), ENGAGE-2026
(#0F172A, #FF6B5E, #93C47D, #E8B931), v1 drift (#5C6E84, #F5F7F9, #E02020).

## Hard rules
- Light base theme: body background ALWAYS #FFFFFF. Navy only for sidebar / dark
  feature sections / metric cards.
- Font: Libre Franklin (Google Fonts). No other webfont.
- No gradient text (`-webkit-background-clip: text` banned). Gradients OK on bars/lines.
- Self-contained output: zero external CDNs except Google Fonts.
- Card accents: top gradient accents, NEVER border-left ribbons.

## Slide tone
- Max 4 key points per slide. One idea per slide.
- "So What" headers — outcomes, not labels.
- Open on From→To; anchor on the AI-Native Banking OS.
- Three Operational Powers framing: Nexus (data) · Orchestration (workflows) · Sentinel (intelligence).
