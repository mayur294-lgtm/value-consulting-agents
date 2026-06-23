# Judge: use cases achievable on the Backbase platform (usecase-designer)

Use cases are GENERATIVE — the agent derives them from the client's problem statements
and goals and proposes what could solve them. They are NOT expected to come from the
transcript, and a use case the client never raised is GOOD (clients often don't know what
the platform can do; it gets validated with them later). Do NOT penalise a use case for
being net-new.

The real guardrail is **achievability on the Backbase platform** — reason each use case
against the FROZEN platform snapshot. A use case is sound if it is either:
- **OOTB** — delivered by a product line (Digital Onboarding / Lending / Banking / Engage /
  Assist, Grand Central, Platform Identity), OR
- **Buildable** — on a named platform layer: Flow Foundation (low-code journeys/forms/rules),
  Orchestration (Process Studio workflows / Agent Studio agents / Banking Capabilities
  microservices), Nexus (shared customer truth), Intelligence (models/SLMs), Sentinel
  (authority for agentic actions).

Score 1.0 only if EVERY use case (a) traces to a stated problem or goal, AND (b) is clearly
achievable OOTB or names a plausible platform-layer build path, AND (c) its OOTB / Config /
Custom classification is honest (custom work not mislabelled OOTB).

Deduct sharply for: use cases requiring capability OUTSIDE the platform (core replacement,
hand-wavy "AI does it" with no layer it runs on); use cases with no link to a problem/goal;
custom work claimed as OOTB.
Do NOT deduct for: net-new use cases the client didn't mention — that is the point.

Return JSON: {"score","pass" (>=0.8),"reason"} — for any unsound use case, name it and say which platform layer (if any) could actually deliver it, or why it is not achievable.
