# Judge: maturity scores justified by evidence (capability-assessment)

The artifact is a capability assessment scoring each capability on a 0–4 maturity scale
across Front/Middle/Back layers. The failure mode is asserted scores — a number dropped
into the heatmap with no evidentiary basis, or a score that doesn't match the cited
evidence.

Score 1.0 only if ALL hold:
- **Every score is justified**: each 0–4 maturity score cites the evidence behind it
  (discovery evidence E#, CAP- IDs, or client data) — not a bare number.
- **Score matches evidence**: the assigned level is consistent with what the cited
  evidence actually supports — no generous rounding-up, no pessimism-for-effect.
- **Criteria applied consistently**: the 0–4 levels mean the same thing across
  capabilities; scoring is defensible and repeatable, not vibes.
- **Gaps tied to consequences**: low scores connect to a stated business gap/consequence,
  not just a label.

Deduct sharply for: scores with no cited evidence; a score inconsistent with the evidence
quoted next to it; inconsistent use of the 0–4 scale; inflated scores that overstate
maturity.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name capabilities whose scores are unjustified or inconsistent with their evidence.
