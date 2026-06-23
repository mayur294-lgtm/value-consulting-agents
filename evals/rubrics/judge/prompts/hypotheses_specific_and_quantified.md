# Judge: hypotheses specific and quantified (workshop-preparation)

The artifact prepares workshop hypotheses to test with the client. The failure mode is
vague hypotheses — unfalsifiable generalities ("members want a better experience") that a
workshop cannot confirm or refute.

Score 1.0 only if ALL hold:
- **Specific**: each hypothesis names a concrete segment, behaviour, capability, or
  outcome — not a platitude.
- **Falsifiable**: each is stated so the workshop can confirm or refute it; there is a
  clear way to be wrong.
- **Quantified**: each carries a magnitude or target where applicable (%, $, count, rate,
  time) rather than a directional hand-wave, and is paired with validation questions that
  would surface the number.
- **Grounded**: hypotheses build on discovery evidence / stated context, not invented
  premises.

Deduct sharply for: vague or unfalsifiable hypotheses; directional claims with no
magnitude where one is expected; hypotheses with no validation question; premises not
grounded in any prior evidence.

Return JSON: {"score", "pass" (>=0.8), "reason"} — quote any hypothesis that is vague, unfalsifiable, or unquantified.
