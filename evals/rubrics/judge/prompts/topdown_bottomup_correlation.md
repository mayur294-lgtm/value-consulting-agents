# Judge: top-down ↔ bottom-up correlation

A strong ROI bridges the client's own top-down financials (annual report / 10-K /
NCUA call report — e.g. investment-services revenue as a % of total revenue vs.
industry benchmark) to the bottom-up, transcript-derived lever estimates.

Score 1.0 only if the report explicitly connects a top-down baseline metric to the
bottom-up findings — e.g. "investment services is X% of total revenue vs. Y% at
peers, confirming the bottom-up finding that the client is underweight in wealth."

Deduct for: bottom-up levers with no top-down anchor; an annual-report section that
is present but never tied to the lever logic; a claimed correlation with no numbers.

Return JSON: {"score", "pass" (>=0.75), "reason"}.
