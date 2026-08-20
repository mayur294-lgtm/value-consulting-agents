# Proposal Builder Pilot — Test Findings

**Companion to:** `TEST_GUIDE.md` (same folder) · PRD `.prd/prd-v5.md` · PR #153
**Purpose:** Running log of findings from the pilot window. Objective signal from real sessions + analysis. Feeds the end-of-window synthesis that decides GA (merge) or another refine round.
**How findings accumulate:** one entry per notable session or pattern. Tag each against a component and type. Mark whether it's a design, implementation, model-limit, or methodology issue.
**Testers:** Shyam (lead) · Aniket (methodology) · Mariam
**Last updated:** —

---

## Status board

| # | Finding | Component | Type | Severity | Sessions | Action |
|---|---|---|---|---|---|---|
| — | *(no findings logged yet)* | | | | | |

Components: cockpit (`/proposal-builder`) · engine (`tools/proposal_builder.py` + `pricing_model.py`) · renderer (`/proposal-longform`) · loop (round-N / deal state) · deal-notes · knowledge (tactics / narrative / pricing methodology) · evals.
Types: design · implementation · model-limit · methodology. Positive findings welcome — they are ship signal.

---

## Entry template (copy per finding)

### Finding #N — <one-line title>

**Session:** <deal or scenario, date, tester>
**Build:** `pilot/proposal-builder-test` @ <commit>
**Scenario:** <1 / 2 / 3 / 4 / other>
**Component / Type / Severity:** <…>

#### What happened
<objective sequence: what was asked, what the system did, in what order — facts before interpretation>

#### What worked (keep)
<…>

#### What failed
| Failure | Type | Note |
|---|---|---|
| | | |

#### Caveats
<n=?, confounds, whether the model's own explanation was verified>

#### Fix direction (drafted, not applied)
<…>

---

## Known limits going into the pilot (don't re-discover these)

- The engine exits 0 with zeroed output on a fully empty `deal: {}` block (per-FIELD omissions now hard-stop; the empty-block case is backlogged).
- `templates/proposal-longform/template.html`'s own demo content would fail the deliverable gate (3 scenario cards, no markers) — the cockpit supplies compliant sections; rendering the raw demo near-verbatim is a known trap (backlogged).
- Voice checks are deterministic heuristics, not a calibrated judge.
- The round-N loop is skill-behavior, gated by contract checks only — the delta report's quality is exactly what this pilot measures.
- `pricing_model.py` has no CI wiring yet (backlogged) — treat its outputs with normal skepticism and log any wrong number immediately.
- Full backlog: `.prd/backlog.md` (PR #153 review section).

## Synthesis (end of window — leave empty until then)

**Verdict:** —
**Trigger/calibration changes before release:** —
**Refine tickets raised:** —
