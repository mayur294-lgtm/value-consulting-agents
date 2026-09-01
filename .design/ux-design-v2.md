---
version: 2
prd: prd-v2.md
status: draft
date: 2026-07-23
author: Mariam Titus George
previous: ux-design-v1.md
---

# UX Design — Critical Thought Partner + `/critty`

The "user" here is the **consultant** working in a Claude Code chat. There is no GUI; the interaction surface is (a) Cortex's in-conversation challenge behaviour and (b) the `/critty` slash command. UX = the *logic* of when Cortex speaks, what it returns, and how the consultant recovers/overrides.

## User Flows

### Flow A — Always-on governed challenge (passive)

```
[consultant asserts something / asks for an artifact]
        │
        ▼
[Cortex runs the Governor silently]
        │
        ├──[no trigger fires OR a suppression rule applies]──▶ [do the work, zero challenges]
        │                                                              │
        │                                                              ▼
        │                                                     (this is the common case)
        │
        └──[≥1 trigger fires AND not suppressed]──▶ [ONE batched, structured push]
                                                            │
                                    ┌───────────────────────┼───────────────────────┐
                                    ▼                       ▼                       ▼
                          [inline question         [batched structured     [stop & align on the
                           — single concern]         push — several]         problem — foundational]
                                    │                       │                       │
                                    └───────────────────────┴───────────────────────┘
                                                            │
                                                            ▼
                                          [consultant defends / corrects / closes topic]
                                                            │
                          ┌─────────────────────────────────┼─────────────────────────────────┐
                          ▼                                  ▼                                   ▼
              [informed call made ──▶ S1:                [correction given ──▶            [topic closed ──▶ S3:
               do not relitigate]                         metabolize: restate,             stay silent]
                                                          sweep for repeats]
```

### Flow B — `/critty` on-demand hard pressure-test (active escalation)

```
[consultant types  /critty  (optionally /critty <file|section|free text>)]
        │
        ▼
[Step 1: force-load knowledge/standards/critical_thought_partner_protocol.md IN FULL]
        │
        ├──[protocol file missing on branch]──▶ [say so; fall back to CLAUDE.md CTP section; note the limitation] ──┐
        │                                                                                                            │
        ▼                                                                                                            │
[Step 2: scope the target]                                                                                          │
        │                                                                                                            │
        ├──[target named]────────▶ use it                                                                            │
        ├──[no target]───────────▶ use current / most-recent substantive artifact                                   │
        └──[genuinely ambiguous]─▶ ask ONE short scoping question ──▶ [consultant answers] ──┐                       │
                                                                                             │                       │
        ┌────────────────────────────────────────────────────────────────────────────────────┘                     │
        ▼                                                                                                            │
[Step 3: align — state read of purpose/audience/"good" + the standard; ask to confirm/correct]                      │
        │                                                                                                            │
        ▼                                                                                                            │
[consultant confirms or corrects framing]                                                                           │
        │                                                                                                            │
        ▼                                                                                                            │
[Step 4: HUNT — run all 5 functions regardless of triggers (silence bias suspended)] ◀──────────────────────────────┘
        │
        ▼
[Step 5: proactive provenance — flag each weak/unverifiable figure at point of appearance;
         split "I can challenge this" vs "I can't verify this without source data"]
        │
        ▼
[Step 6: OUTPUT — one challenge register, most-serious-first, calibrated confidence]
        │
        ▼
[Step 7: flag where a genuinely independent check would bite harder]
        │
        ▼
[consultant decides per item ──▶ Cortex offers to fix on request; then returns to normal governed behaviour]
```

## Screen & Component States

The "component" is Cortex's response. States enumerated as response modes:

| State | Trigger | What the consultant sees |
| --- | --- | --- |
| Silent (do the work) | No Governor trigger, or a suppression rule applies | The requested work, no challenge. **The common case.** |
| Inline question | Exactly one concern crosses a trigger | A single, short question embedded near the relevant point |
| Batched push | Several related concerns cross triggers | ONE structured block of concerns — never serial nags |
| Stop-and-align | Foundational disagreement on the problem itself | Cortex pauses before producing; proposes a re-frame and asks to align |
| `/critty` aligning | `/critty` invoked | Cortex's read of purpose/audience/standard + a "confirm or correct?" prompt |
| `/critty` scoping | `/critty` with ambiguous target | One short scoping question |
| `/critty` register | `/critty` hunt complete | A ranked challenge register table + independence flag |
| Fallback | `/critty` run where protocol file is absent | Notice that it's running from the CLAUDE.md summary, with the stated limitation |

## Error States

| Error | Cause | User-facing message | Recovery |
| --- | --- | --- | --- |
| Protocol file missing | `/critty` on a branch without `knowledge/standards/critical_thought_partner_protocol.md` | "The full CTP protocol file isn't on this branch — I'll run from the CLAUDE.md summary, which is lighter. Depth (exact triggers, worked example) is unavailable." | Proceed in fallback; note limitation |
| Ambiguous target | `/critty` with no clear current artifact | "What should I pressure-test — the ROI model, the deck, or something else?" | Consultant names the target; proceed |
| Over-challenge risk (design guardrail, not a runtime error) | Governor mis-fires and challenges cosmetic/closed items | (Prevented, not surfaced) — suppression rules S1–S4 gate it out | Consultant can say "you already made the call / topic closed"; S1/S3 silence it |
| Verification overreach | Consultant asks `/critty` to *confirm* a figure | "I can flag the reasoning around this number, but I can't verify the figure itself without the source data — that's a gap, not a green light." | Named as unverifiable in the register; consultant supplies source or accepts the gap |
