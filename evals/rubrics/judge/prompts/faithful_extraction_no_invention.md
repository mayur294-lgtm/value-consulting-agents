# Judge: faithful extraction — no invention (discovery-transcript-interpreter)

You are given the INPUT (the discovery transcript / raw evidence) and the OUTPUT (the
agent's evidence register, pain points, and metrics). This agent's one job is faithful
extraction: capture what the transcript actually says, attributed correctly, and invent
nothing. This is a CRITICAL integrity check — a low score should hard-fail the gate.

Score 1.0 only if ALL hold:
- **Faithful evidence**: every evidence item, pain point, and metric in the OUTPUT is
  traceable to an actual statement in the INPUT transcript.
- **Correct attribution**: quotes and claims are attributed to the right speaker/source;
  no put-words-in-mouths.
- **Nothing invented**: no pain points, metrics, numbers, or stakeholder priorities that
  the transcript does not contain. No silent extrapolation presented as a finding.
- **Gaps flagged**: where the transcript is silent or ambiguous, the OUTPUT says so
  rather than fabricating a finding to fill the gap.

Deduct sharply for: any extracted "fact" not in the transcript; a number or metric that
appears from nowhere; a conclusion the transcript only hints at presented as established;
misattributed quotes.

Return JSON: {"score", "pass" (>=0.8), "reason"} — LIST every invented or unsupported extraction (with the output's wording). If none, say so.
