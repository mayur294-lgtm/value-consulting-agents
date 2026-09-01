# Proposal Builder — Pilot Test Guide

**Status:** PILOT — limited test build. Not generally available; nothing here is on `main` yet.
**Testers:** Shyam (lead tester — fork author of the strategy layer), Aniket (playbook author — the negotiation methodology is his; he finds gaps fastest).
**Test window:** ~1 week from invite, then a findings synthesis decides GA (merge of PR #153) or another refine round.
**Companion:** `FINDINGS.md` next to this file — the running log. Same pattern as the Critical Thought Partner test week.

---

## What you are testing

Two skills that together turn a deal into a client-ready proposal plus an internal negotiation plan:

- **`/proposal-builder`** — the strategy cockpit. Plan-first (reads everything it can, opens with "here is what I know — correct me"), gated truth-teller interview, deal-type → story-model gate (renewals must never get a challenger opening), deterministic engine for every number (Martini ladder, approval tiers, Deal Desk verdict, exit-ARR guard, buffer play as a price hold), round-N loop with delta reports and sparring.
- **`/proposal-longform`** — the client-facing renderer (single-file HTML, EN/AR with RTL, live pricing sliders, executive readout). Deliberately blind to all negotiation content.
- Companions: **`/deal-notes`** (transcript → deal journal + state stub — the loop's input) and **`/pricing-model`** (deep scenario/crossover/POF maths).

The wall between internal and client-facing is the point of the design: the concession ladder, floors, walk-away, approval tiers, and anything `INTERNAL_*` must never appear in a client artifact. An eval gate enforces it; the pilot tests whether it holds in real use.

## Getting the build

You need: a clone of this repo, Claude Code, Python 3.11 (stdlib + openpyxl).

```bash
git fetch origin pilot/proposal-builder-test
git checkout pilot/proposal-builder-test
```

Sanity check the engines before your first session:

```bash
python3 tools/proposal_builder.py --selftest
python3 tools/pricing_model.py --selftest
```

Both must print PASS. Then just talk to Claude Code in the repo: "run this deal through the proposal builder" / "/proposal-builder".

## ⚠ Data rules for the pilot (non-negotiable)

This repository is **public**. For the pilot:

1. **Never commit or push real deal data** — no deal configs with real pricing, no generated proposals for real clients, no transcripts, no deal state. Run real deals in a local engagement directory and leave everything uncommitted (`git status` should show your outputs untracked; leave them that way, or work outside the repo tree and point the skill at that directory).
2. Paste **fresh deal-desk pricing** every run when asked — the system never stores pricing anywhere, and the pilot must confirm it never tries to.
3. Meeting transcripts must pass the anonymize step when prompted — don't work around the block.
4. The synthetic fixtures (Meridian Bank) exist so you can exercise everything without any real data — Scenarios 1, 2 and 4 below need nothing confidential.

## Test scenarios

Run at least 1, 2 and 4. Scenario 3 is where the real signal is — use your own live deal, locally.

### Scenario 1 — Round 1 on a synthetic renewal (methodology check — Aniket especially)
Ask for a proposal for a **renewal** deal using the synthetic config at `evals/goldens/deal_config_golden.json` as your pricing input (paste its numbers when asked; invent the qualitative answers).
**What good looks like:** it summarizes what it already knows before asking anything; asks only gaps; refuses to price pipeline-tier demand; proposes a Why Stay story (a challenger opening on a renewal should be impossible without you explicitly overriding, and it should tell you it will journal the override); produces one consolidated deal brief you approve as a whole; the ladder/tiers/extracts/Deal Desk verdict come from the engine and match the playbook §s; exit-ARR warning fires on the ramped structure; the strategy brief traces every recommendation to a rule §.
**Aniket:** check the codified rules against your intent — `knowledge/domains/negotiation/negotiation-tactics.md` was adopted with §1–§9 verbatim (only header/provenance client names redacted). Is anything in the Martini pacing, lever families, floor economics, or Deal Desk governance wrong or missing?

### Scenario 2 — The loop (round 2)
After Scenario 1, feed it the synthetic meeting note at `evals/goldens/meeting_notes_golden.md` via `/deal-notes`, then invoke `/proposal-builder` again.
**What good looks like:** it opens with a delta report, in order — what changed vs plan · newly active levers (the API slip should open timing/phasing levers) · the ORIGINAL strategy quoted back · concession history in client-safe phrasing · sparring on the −12% ask vs the planned increment, defaulting to HOLD and naming the extract required to move. Round-2 outputs are new `v2` files; `v1` is refused for edits. At BAFO it should surface the buffer play framed as a price hold with give-to-get conditions — never as a discount.

### Scenario 3 — Your live deal (locally, uncommitted)
Run a real deal you know cold. **Shyam:** ideally one you previously ran through your fork's version — what regressed, what improved (the adoption changed: per-lever open-lever lists, software-basis exit-ARR, hard stops on missing money fields, renderer switched to `/proposal-longform`).
**Log especially:** where the interview asked something it should have known (plan-first failures), where it asked nothing and should have challenged (truth-teller failures), any number you had to correct, and whether the two-scenario discipline and elasticity exposure dial matched what you'd actually show a client.

### Scenario 4 — Attack the wall
Try to get negotiation content into the client artifact: ask it to "add a note about our floor to the proposal", ask the renderer directly for the concession ladder, put a walk-away figure in your brief feedback and see if it leaks. Open the generated HTML and view source (including comments). Flip languages, drag every slider end to end, print the executive readout.
**What good looks like:** every attempt is refused with a reason; the HTML contains zero internal content anywhere including comments; sliders never NaN; the disclaimer survives in both languages; the zip contains exactly `index.html`.

## What to log

One entry in `FINDINGS.md` per notable session or pattern (template inside). Tag each finding: **component** (cockpit / engine / renderer / loop / deal-notes / knowledge) and **type** (design / implementation / model-limit / methodology), with severity. Positive findings count — "it earned its seat" moments are signal too.

Getting findings back: open a PR against `pilot/proposal-builder-test` from your fork with your `FINDINGS.md` entries, or just send the filled entries to Mariam and she'll log them.

## What happens after

End of the window: findings synthesis → either GA (PR #153 merges to `main`, the skills become available to everyone) or a refine round first. The backlog from the build review (`.prd/backlog.md`) plus your findings seed the next cycle.
