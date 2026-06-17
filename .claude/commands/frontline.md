---
name: frontline
description: Frontline 2026 design-system launcher. ALWAYS start here for any client-facing visual deliverable (deck, document, presentation). Probes the user for the output format first, explains the options, then routes to the right builder.
---

# /frontline — Design System Launcher

You are the entry point to the **Frontline 2026** design system. A consultant has
asked for a client-facing visual deliverable. **Do NOT assume the format.**

## STEP 0 — Probe for format (ALWAYS do this first)

Before generating anything, present this menu and ask the user to choose. Render
it as a short, friendly question — e.g. *"I can produce this in the Frontline 2026
design system. What output format would you prefer — HTML deck, long-form HTML,
PDF, or PPT?"* — followed by the options with their one-line explanations:

| # | Format | What it is | Best when… |
|---|--------|-----------|-----------|
| **1** | **HTML slide deck** (`frontline-slides-html`) | Self-running, self-contained `.html` deck. 17 layouts, presenter mode (P), overview grid (O). The **Pictet QBR look** — cards, chips, two-tone panels, option cards w/ RECOMMENDED badge, Gantt. | *Presented*/demoed; richest look; no one edits it. **Highest fidelity.** |
| **2** | **Long-form HTML** (`frontline-long-form`) | Scrolling business/value case with sidebar nav, hero stats, lever/scenario cards. | *Read async* (emailed) — business case, ROI summary, exec briefing. |
| **3** | **PDF** (build then export) | A flat, final, **non-editable** file. Built as long-form (documents) or a deck (slides), then exported — Chrome headless for HTML, `soffice` for PPTX. | Sending a locked file for review/sign-off/printing; recipient won't edit. |
| **4** | **PPT** (`frontline-slides-pptx`) | Editable Google Slides / PowerPoint `.pptx`, same brand (~90% of the HTML look). | Team must tweak numbers/scope/pricing first, or it lives in Drive. |

Ask **two quick clarifiers** if not already known:
- **Presented or read async?** → presented ⇒ 1 / 4; async ⇒ 2 / 3.
- **Editable, or final/locked?** → editable ⇒ 4 (PPT); locked ⇒ 3 (PDF); rich & self-running ⇒ 1 (HTML).

If the user already told you the format, skip the menu and confirm in one line.

## STEP 1 — Route

Once chosen, follow the matching path:
- **1 →** `frontline-slides-html.md` (engine: `presentations/backbase-slides-app/engine.js` + `deck-template.html`)
- **2 →** `frontline-long-form.md` (template: `templates/long-form/document-template.html`)
- **3 → PDF:** build as #2 (documents) or #1/#4 (slides), then export to PDF.
- **4 →** `frontline-slides-pptx.md` (builders in `tools/`)

## Non-negotiables (all formats)
- Read tokens from `presentations/frontline-2026/design-tokens.json` — never invent hex/font/geometry.
  Navy `#041326`, blue `#3367FF`, red `#FF503C`, cyan `#69FEFF`, Libre Franklin.
- Apply the narrative spine (`knowledge/banking_os.md`): operating-model thesis,
  From→To framing, outcomes-not-features.
- The **Pictet QBR HTML** (`presentations/backbase-slides-app/examples/pictet_qbr_2026_REFERENCE.html`) is the
  reference look-and-feel. Match it.
