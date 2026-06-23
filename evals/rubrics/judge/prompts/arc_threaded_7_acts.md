# Judge: transformation arc threaded across all 7 acts

The artifact is a consulting assessment (7-act narrative or its HTML dashboard). A
recurring failure is that the central transformation arc (e.g. "Unified Frontline")
is stated once in Act 2 and then dropped — the acts read as disconnected sections.

Score 1.0 only if the SAME transformation arc is woven through **every** act, each
framing its content through that lens:
- Act 1 — why the transformation is needed (the disconnected current state)
- Act 2 — what the transformation looks like (the vision)
- Act 3 — how it is proven (the lighthouse / pilot)
- Act 4 — where today's system breaks (lifecycle gaps)
- Act 5 — what capabilities the transformation requires
- Act 6 — how it is built (roadmap phases)
- Act 7 — why it pays for itself (benefits case)

Deduct for: the arc named in only 1–2 acts; acts that read as standalone with no
callback to the arc; a different/looser theme substituted partway through.

Return JSON: {"score", "pass" (>=0.8), "reason"} — name which acts carry the arc and which drop it.
