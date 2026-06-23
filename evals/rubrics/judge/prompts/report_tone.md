# Judge: report tone & executive readiness

Score the deliverable's VOICE against the frozen Output Quality Standards.

Score 1.0 only if ALL hold:
- **Executive-ready**: written for a C-level reader — concise, plain English, no
  unexplained acronyms/vendor jargon, action-oriented.
- **Decisive**: states a clear recommendation / go-no-go; doesn't hedge endlessly.
- **Conservative, not hype**: no breathless/optimistic language ("revolutionary",
  "massive", "guaranteed"); claims are measured and defensible.
- **Shows its work**: methodology and key numbers are explained, not asserted.
- **Not academic**: business-consulting voice, not a research paper.

Deduct for: jargon soup; buried recommendation; hype/superlatives; wall-of-text with
no "so what"; passive over-hedging.

Return JSON: {"score", "pass" (>=0.8), "reason"} — quote 1-2 offending phrases if any.
