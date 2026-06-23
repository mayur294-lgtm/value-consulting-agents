# Judge: evidence grounding — "no wild assumptions from the transcript"

You are given the INPUT (transcript / evidence the agent was working from) and the
OUTPUT (the report / analysis). Verify the output does NOT extrapolate beyond what the
input supports — the failure mode that silently distorts the narrative and inflates ROI.

Check every MATERIAL claim, number, and qualitative conclusion in the OUTPUT:
- Is it traceable to something in the INPUT (a quote, a data point, a stated fact)?
- Or is it a clearly-labelled assumption/benchmark (acceptable)?
- Or is it an UNSUPPORTED leap presented as fact (NOT acceptable)?

Score 1.0 only if every material claim is either grounded in the input OR explicitly
flagged as an assumption. Deduct sharply for:
- numbers/percentages that appear from nowhere (not in input, not labelled an assumption)
- qualitative conclusions the transcript doesn't support ("the client is committed to X"
  when the transcript only hints)
- optimistic framing that overstates what was actually said

Return JSON: {"score", "pass" (>=0.85), "reason"} — LIST the specific unsupported claims you found (with the output's wording). If none, say so.
