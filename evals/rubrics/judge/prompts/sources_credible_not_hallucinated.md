# Judge: sources credible, not hallucinated (market-context-researcher)

The artifact is outside-in market context: annual-report metrics, peer/competitor
capability benchmarks, and CX research used to strengthen the case for change. The
core failure mode is fabricated authority — invented stats, made-up competitors, or
sources that don't exist dressed up as fact.

Score 1.0 only if ALL hold:
- **Real sources**: every cited source (annual report, investor deck, regulator filing,
  NCUA/call report, industry report) is a plausibly real, nameable document — not a
  vague "studies show" or an invented title.
- **No fabricated stats**: numbers, market shares, and growth rates are attributed to a
  source, not conjured. Round/suspiciously convenient figures with no source are a flag.
- **Real competitors/peers**: named competitors and peer institutions actually exist and
  are relevant to the client's market/segment — no invented banks or mismatched peers.
- **Gaps flagged, not filled**: where public data is unavailable (common in wealth/MEA),
  the agent says so explicitly rather than fabricating a number.

Deduct sharply for: any statistic without an attributable source; a competitor or
report you cannot verify as real; "industry average" figures presented as fact with no
citation; confident numbers where the agent should have flagged a data gap.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name the specific stats/sources/competitors that look fabricated or unsourced.
