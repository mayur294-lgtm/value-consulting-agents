# Judge: benchmarks defensible, not hallucinated (benchmark-librarian)

The artifact is a benchmark shortlist: each benchmark should carry a credible source, a
confidence level, and a match type. The failure mode is invented numbers — a clean-looking
benchmark with no real provenance, presented with false precision.

Score 1.0 only if ALL hold:
- **Credible source on every benchmark**: each benchmark cites a real, nameable source
  (annual report, investor presentation, regulator, industry report, consultant-provided)
  — never a bare number.
- **Confidence levels present and honest**: each benchmark is labelled High/Medium/Low
  confidence, and the level is consistent with the strength of the source (a proxy or
  estimate is NOT High confidence).
- **No fabrication**: no invented statistics; where a real benchmark is unavailable the
  entry is marked "not available" / estimated / proxy rather than fabricated.
- **Match type stated**: the benchmark's relevance to the client (segment/region/match
  type) is stated, not assumed.

Deduct sharply for: any benchmark with no source; a number labelled High confidence on a
weak/proxy basis; suspiciously round figures presented as fact; missing confidence labels.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name benchmarks that are unsourced, over-confident, or look fabricated.
