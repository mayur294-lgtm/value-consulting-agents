# Judge: synthesis faithful to workshops (ignite-workshop-synthesizer)

The synthesis has two DIFFERENT kinds of content, judged by two DIFFERENT standards:

1. **FINDINGS — must be faithful to the workshop.** Hypothesis-validation statuses
   (Confirmed / Partially / Not Confirmed / Needs More Data), pain points, goals, and
   strategic decisions must trace to what the workshops actually produced. Inventing a
   "Confirmed" the inputs don't support, or a pain/goal nobody raised, is a hard miss.

2. **USE CASES — generative, judged by PLATFORM ACHIEVABILITY, not workshop provenance.**
   It is EXPECTED and GOOD for the synthesis to introduce use cases the client never named:
   the agent reasons from pains/goals to what could solve them, the team takes these to the
   client, gets feedback, and validates later. So do NOT require use cases to derive from
   the workshop discussion. Instead require each proposed use case to be **achievable on the
   Backbase platform** — OOTB or buildable on a named platform layer (reason against the
   FROZEN platform snapshot).

Score 1.0 only if: (a) every validation status / pain / goal is faithful to the workshop
inputs (no upgraded or invented findings), AND (b) every proposed use case is platform-
achievable and ties to a stated pain/goal, AND (c) Quick Win / Foundational / Transformational
/ Defer classifications are reasoned.

Deduct sharply for: a "Confirmed" the inputs don't support; an invented pain/goal/conclusion;
a use case that is NOT achievable on the platform.
Do NOT deduct for: net-new use cases not mentioned in the workshop — that is the intended value.

Return JSON: {"score","pass" (>=0.8),"reason"} — separate any unfaithful FINDINGS from any non-achievable USE CASES.
