# Judge: faithful — no invention (governance baseline)

You are given the INPUT (the evidence/data the agent worked from) and the OUTPUT
(the agent's result). This is the governance-baseline faithfulness check applied to
EVERY agent: the output must not invent data or assert conclusions the input doesn't
support.

Score 1.0 only if every material claim, number, and conclusion in the OUTPUT is
either (a) traceable to the INPUT, or (b) explicitly labelled as an assumption/
benchmark. Deduct sharply for any fact, figure, or strong conclusion that is not in
the input and not flagged as an assumption.

This is the lighter, universal sibling of `evidence_grounding` (which is the deeper,
report-specific version). Keep it strict but fast.

Return JSON: {"score", "pass" (>=0.8), "reason"} — list any invented/unsupported claims.
