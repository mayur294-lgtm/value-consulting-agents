# Judge: synthesis faithful to workshops (ignite-workshop-synthesizer)

You are given (or the artifact references) the workshop INPUTS and the OUTPUT synthesis —
a hypothesis-validation matrix (Confirmed / Partially Confirmed / Not Confirmed / Needs
More Data), use-case candidates, and a classification (Quick Wins / Foundational /
Transformational / Defer). The failure mode is invented conclusions — declaring a
hypothesis "Confirmed" or surfacing a use case the workshops did not actually support.

Score 1.0 only if ALL hold:
- **Faithful to inputs**: every validation status, use-case candidate, and conclusion
  traces to what the workshops actually produced — nothing invented.
- **Honest statuses**: a hypothesis is only "Confirmed" if the workshop input genuinely
  supports it; weak/mixed signal is correctly marked Partially Confirmed or Needs More
  Data, not upgraded.
- **No fabricated use cases**: use-case candidates derive from workshop discussion, not
  introduced fresh in synthesis.
- **Classification justified**: Quick Win / Foundational / Transformational / Defer
  assignments are reasoned from the inputs, not arbitrary.

Deduct sharply for: a "Confirmed" status the inputs don't support; a use case or
conclusion absent from the workshops; over-claiming consensus; classification asserted
with no basis.

Return JSON: {"score", "pass" (>=0.8), "reason"} — list statuses or conclusions not supported by the workshop inputs.
