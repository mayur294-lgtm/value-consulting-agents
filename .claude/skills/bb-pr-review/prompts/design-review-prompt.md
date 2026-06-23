# Design Review Prompt Template

Use this template when `/bb-pr-review` dispatches the `design-reviewer` agent.

## Prompt

> ## Design Review: [PR TITLE]
>
> ### PR Diff
> [Paste the relevant deliverable diff — HTML, CSS in deliverables, output templates, PPTX builder code]
>
> ### Design System (source of truth)
> Backbase Frontline 2026 — `knowledge/design-system.md` + `presentations/frontline-2026/design-tokens.json`. Palette: Navy `#041326`, Action Blue `#3367FF`, Semantic Red `#FF503C`, Background Gray `#F3F6F9`, Success Green `#2ECC71`, Text Muted `#6B7786`, Cyan `#69FEFF`, Surface White `#FFFFFF`. Font: Libre Franklin. Light base theme (pure white body bg).
>
> ### Visual Direction from PRD
> [Paste the Visual Direction section from the PRD, or "Not available — run design-system conformance + anti-slop scan only."]
>
> ### Your Job
> Run all three checks:
> 1. **Design-system conformance** — does the output use the Frontline-2026 palette, Libre Franklin font, light base theme, and brand chrome? Are there any external CDNs other than Google Fonts (Libre Franklin)? Flag any.
> 2. **PRD conformance** — do fonts, colours, theme, and layout match the Visual Direction? (Skip if not available.)
> 3. **Anti-slop scan** — check for these patterns:
>    - Off-palette colours / AI default fonts (Inter, Roboto, Open Sans, system-ui)
>    - Purple-to-blue gradients
>    - Nested card components
>    - Identical repeating card grids
>    - Side-stripe `border-left/right` ribbon accents
>    - Gradient text (`-webkit-background-clip: text` on glyphs)
>    - Uniform spacing everywhere
>    - Pure black (#000) or white that should be navy-tinted
>    - External CDNs (anything beyond Google Fonts Libre Franklin)
>
> Report each finding with: confidence (0-100), severity (high/medium/low), file:line location, what you found, why it matters, and a fix suggestion.
>
> If a check produces zero findings, say so briefly. Don't manufacture issues.

## Usage

Replace `[PR TITLE]` with the PR title. Paste the diff and Visual Direction section. The main model handles extracting the Visual Direction from the PRD before dispatching.
