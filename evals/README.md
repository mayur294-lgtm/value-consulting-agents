# Cortex Evals

Evals are the **verify gate** of the bb-* development harness. For a document
factory there is no compiler, so the eval suite stands in for one — but unlike
a compiler, it does not prove the same thing for every check. What a green
score means depends entirely on which **tier** produced it: some checks run
real repo code against a fixture and can genuinely fail; others score a fixed
piece of frozen text and cannot see the agent prompt at all. Read "Three
tiers" below before trusting any number this suite prints.

See the design plan: `~/.claude/plans/peppy-stargazing-swan.md`.

## Layout

```
evals/
  registry.yaml                 # per-component / per-deliverable spec (THE config)
  check_registry.py             # preflight: gating goldens resolve + mutation law (see below)
  run_experiment.py             # CLI runner = the gate; local mode needs only stdlib + PyYAML
  mutations.py                  # --mutate harness: fixture/file mutation + shadow scoring
  path1.py                      # path-1 regeneration runner — orphaned, see "Billing" below
  requirements.txt
  goldens/                      # scrubbed golden fixtures + negatives (safe for Langfuse Cloud)
    deck_valid_min.html         #   on-palette calibration anchor (good must PASS)
    negatives/                  #   known-bad per check (must FAIL)
  rubrics/
    base.py                     # CheckResult / RubricResult
    deliverable/                # CODE evaluators: decks.py, roi.py, assessment.py
    structural/contracts.py     # deliverable-structural altitude: inter-agent
                                 #   contract lint over output FILES (no agent runs)
    component/                  # component (unit) altitude: per-agent checks — a MIX of
                                 #   executable modules and rubric-calibration adapters
                                 #   over specifics.py (see "Three tiers")
    judge/                      # LLM-as-judge harness (judge.py) + prompts/ + standards_snapshot/
```

The tiers are now separated in the registry itself. **#201 landed:** the eleven
prose-golden rows moved out of `components:` into their own
`rubric_calibration:` section, keyed by RUBRIC (`market-context-rubric`, not
`market-context-researcher`), each with a per-check fixture-mutation negative,
and each printing a standing "scores the RUBRIC, not the component" banner on
every run. The eleven agent names they used to be keyed by keep a
`retired: true` REDIRECT row in `components:` that always hard-fails with the
mapping — see "Rubric-calibration" below.

## Developer onboarding (one-time) — developers only

If you're going to **change agents/skills/components**, configure your eval keys once:

```bash
bash evals/setup_dev.sh
```

It prompts for **your own Anthropic API key** (for the LLM-judges) and seeds the
**shared Langfuse eval keys**. People who only *run* agents to generate outputs do
**not** need this and are never prompted (it's wired into the `bb-prd` lifecycle and
the `require-harness` hook — dev-only entry points).

- **Anthropic key**: each developer brings their own (`console.anthropic.com`).
- **Shared Langfuse keys**: distributed out-of-band as `evals/.env.shared` (gitignored)
  — get it from the team; `setup_dev.sh` picks it up automatically. (Never committed.)

## Three tiers

Before this epic the suite was described as "three altitudes" — component,
pipeline, deliverable — as if a PASS at any of them meant the same kind of
thing. It doesn't. The load-bearing distinction is **tier**: what the check
actually touches when it runs.

### 1. Executable — invokes real repo code, can genuinely fail

Five `components:` rows call real code against a fixture and inspect a real
result:

- **`mcp-query-guard`** — subprocesses the actual hook script (`.claude/hooks/mcp-query-guard.py`)
  and pipes it real stdin, the only way to prove the shipped hook (not a
  reimplementation of it) behaves correctly.
- **`pii-anonymizer`** — real Presidio round-trips through `scripts/pii/engine.py`.
- **`run-experiment-runner`** — self-gate: the runner's own behavior, proven
  by mutating itself (#185).
- **`mutation-harness`** — self-gate: `mutations.py` proving itself (#187).
- **`roi-excel-generator`** — imports `tools.roi_excel_generator.ROIModelGenerator`,
  generates a real `.xlsx` from a golden config, reopens it with `openpyxl`,
  and inspects the actual workbook.

A PASS on one of these is real evidence about the code that changed. It is the
only tier where that is true.

### 2. Rubric-calibration — a regex over a frozen golden, not the agent

Eleven rows under the `rubric_calibration:` key (#201) are thin adapters over
`rubrics.component.specifics` — pure string/regex matching against a **frozen
golden** markdown or text fixture. They are keyed by RUBRIC, not by agent:

| row (`--calibration <row>`) | `covers_agent:` (inert documentation) |
|---|---|
| `market-context-rubric` | market-context-researcher |
| `roi-hypothesis-rubric` | roi-hypothesis-builder |
| `discovery-evidence-rubric` | discovery-transcript-interpreter |
| `capability-maturity-rubric` | capability-assessment |
| `roadmap-rubric` | roadmap-prioritization |
| `narrative-arc-rubric` | narrative-assembler |
| `journey-map-rubric` | journey-builder |
| `benchmark-shortlist-rubric` | benchmark-librarian |
| `usecase-design-rubric` | usecase-designer |
| `workshop-prep-rubric` | workshop-preparation |
| `workshop-synthesis-rubric` | ignite-workshop-synthesizer |

None of these checks ever open the agent's `.claude/agents/<name>.md` prompt.
They score a fixed piece of text that was written once and frozen. **Measured
directly:** the entire 45 KB `market-context-researcher` prompt was replaced
with one line of garbage, and its own gate —
`run_experiment.py --component market-context-researcher` — still returned
**1.000 PASS** (`.prd/prd-v7.md`). The gate named after an agent cannot see
that agent. That is why the agent name no longer names the row.

A PASS here proves the frozen golden still parses the way the regex expects.
It is a calibration check on the rubric — it is **not** evidence that the
agent prompt behind that name does the right thing, was verified, or was even
touched. Every run prints that sentence as a banner
(`rubrics/component/_calibration.py`), and every one of the 38 checks across
these rows carries its own per-check **fixture-mutation** negative under
`negatives:` (dict form), all bite-proven by `--mutate <row>`.

Why the rows were kept rather than deleted: `evals/runtime.py` — wired at
`scripts/orchestrate.py:2242` and `.claude/settings.json:74` — routes LIVE
engagement outputs through the same `specifics.py` check functions on every
pipeline run and every consultant session. The golden is the calibration
anchor that keeps those thresholds falsifiable, and the only regression test
on rubric code.

**Neither an agent name nor a rubric name resolves under `--component`.** The
rows live in their own `rubric_calibration:` section and are run with their own
flag, `--calibration <row>` — #201 had to alias them back into `components:` for
dispatch while `run_experiment.py` was owned by a concurrent ticket (#204), and
that shim is now gone. A separate flag is the point: a row that answers to
`--component` reads as a component gate to every reader and every quoted number.
`--component <rubric>` prints a redirect instead of scoring, and each retired
agent name keeps a `retired: true` redirect row in `components:` pointing at
`rubrics.component.moved_to_rubric_calibration`, which always HARD-FAILS and
prints the agent → rubric mapping. `check_registry.py` asserts both halves: a
calibration row must not appear in `components:`, and the runner must still carry
the `--calibration` dispatch (an unrunnable row never fails, which reads as
"nothing failed"). `.github/workflows/evals.yml`
reads the same flag and skips those rows with a notice instead of running them
— because running a calibration rubric on a changed prompt would score a fixture
the prompt cannot affect.

### 3. Deliverable / deliverable-structural — score the final artifact

- **`deliverable`** (`--deliverable deck|roi|assessment`) scores a rendered
  output file directly with a code evaluator (`rubrics/deliverable/*.py`) —
  on-palette checks, structural presence, etc. This is the closest thing to
  an executable check the deliverable side has: it inspects the actual file.
- **`deliverable-structural`** (`--altitude deliverable-structural`) lints
  the inter-agent structural contracts across a set of engagement **output
  files that already exist on disk** (expected deliverables present, evidence
  IDs shared, deliverables clear their hard gates). It reads files that
  already exist: it does **not** run `orchestrate.py`, never invokes an
  agent, and never reads the component you changed — so a green here is
  **not** integration evidence (#188; the altitude used to be called
  `pipeline`, which is exactly what made a 1.000 read as an end-to-end run
  when it was scoring frozen fixture files in ~5 seconds). A real end-to-end
  run is `scripts/orchestrate.py` on a synthetic engagement — that is out of
  scope for the gate.

### Mixed case: `roi-financial-modeler`

`roi-financial-modeler` was counted as a twelfth rubric-calibration row before
#201 and was deliberately **left in `components:`**. Its subject is a
machine-readable `roi_config.json`, not prose: the checks assert a schema and
contract (three scenarios, NPV/payback, per-field `_source`/`_confidence`
provenance, operating costs as a live formula), and
`overcap_negative_gate_witness` genuinely **executes**
`scripts/artifact_boundary.py`'s `cap_roi_config()` against a real overcap
fixture — the same shared-gate situation as `knowledge-harvester` below. It
also carries a LIST-form `negatives:` (`roi_config_overcap.json`, the #180
threshold-0.90 gate), and a row can only have one `negatives:` key: converting
it to the per-check dict form would have deleted a real cross-fixture gate to
gain a weaker one. Its per-check mutation coverage stays in the counted DEBT
list until it is authored in its own change.

### Mixed case: `knowledge-harvester`

`knowledge-harvester` doesn't fit either bucket cleanly. Three of its four
checks really execute `scripts/artifact_boundary.py`'s `synthetic_policy()`
directly, deterministically, against committed fixtures — that part is
genuinely executable. But `synthetic_policy()` is a **shared gate function**,
not this agent's prompt. The fourth check, `quarantine_mode_outputs_local`,
does read `.claude/agents/knowledge-harvester.md` (it parses for a
`### Mode: quarantine` block), but it currently **SKIPs, pending #131** — a
skip counts as neither pass nor fail evidence. Net result: a green
`--component knowledge-harvester` is still not evidence the agent's `.md` was
verified — for a different reason than the eleven `rubric_calibration:` rows
above (a real-but-unrelated gate, plus one still-skipped prompt check). That
is why #201 left it, like `roi-financial-modeler`, in `components:`.

### The one question a reader should be able to answer

**Does this green score say anything about an agent prompt?** Only for the
five executable rows, and even then only for the four whose subject *is*
prompt-adjacent code (`mcp-query-guard`, `pii-anonymizer` gate hook/engine
code, not a prompt at all) or the row's own harness code
(`run-experiment-runner`, `mutation-harness`, `roi-excel-generator` gate
their own module, not an agent). **No row in this suite today verifies an
agent's `.claude/agents/*.md` prompt.** For the eleven `rubric_calibration:`
rows and the one prompt-reading check inside `knowledge-harvester`, the
answer is no — and the local, unwired alternative is `evals/path1.py` (see
"Billing" below).

## The mutation law

**A check with no mutation proof fails preflight.** This is enforced in
`evals/check_registry.py`, run first in the eval CI job:

- Any row named in `MUTATION_PROOF_REQUIRED_ROWS` (the two self-gates, the six
  `.claude/hooks/*` rows, the four artifact/engagement rows, and — since #201 —
  the eleven `rubric_calibration:` rows; the allow-list is durable:
  once a row is added it is hard-enforced even if its `mutations:` key is
  later deleted or broken) is checked immediately: every name in its `code:`
  list must resolve to a `mutations:` entry (or dict-form
  `negatives: {check: {strip: ...}}`), or preflight is a **hard error**
  (exit 1) — the gate does not run in CI.
- Any row that currently declares a `mutations:` key at all, or a dict-form
  `negatives:`, is hard-enforced the same way the moment it declares that key
  — no grace period, no allow-list entry required.
- Every other row with a `code:` list and no mutation declaration at all is
  reported as **DEBT**: loud, counted, non-fatal. Run today
  (`python3 evals/check_registry.py`), this prints **65 uncovered checks
  across 7 rows** (was 103 across 18 before #201 covered the calibration tier) — a prominent total up front, one aggregated line per row
  by default, full per-check detail behind `--verbose`. `--strict` turns DEBT
  into a hard failure for whoever wants that locally.
- `MUTATIONS_ENFORCED_FOR_ALL_ROWS` (in `check_registry.py`, currently
  `False`) is the one-line flip to universal enforcement, once every row is
  migrated — it turns every remaining uncovered check into a hard error with
  no other code change.

The rationale, stated as law: **a check that cannot be proven to fail
certifies nothing.** A `code:` check with no mutation entry might be checking
the right thing, or might be a tautology that would pass against an empty
string — nobody has proven which. `--mutate <row>` is how you prove it:

```bash
python evals/run_experiment.py --mutate run-experiment-runner   # 6/6 proven
python evals/run_experiment.py --mutate mutation-harness        # 5/5 proven
```

It applies each declared mutation, rescoring under a shadow copy, and requires
every declared check to actually go red — exiting non-zero if any check is
unproven or has no mutation entry at all.

### The reachability canary: three states, one harness-limitation escape hatch

When a mutation does *not* prove a check (the check stayed green), `--mutate`
runs a **reachability canary** — deletes a fresh shadow copy of the mutated
file entirely and rescores — to distinguish a genuinely inert check from a
mutation that never reached the code under test. It reports one of three
verdicts (plus `INCONCLUSIVE` if the canary itself can't run):

- **`REACHABLE` (direct — "reddened")** — the check's own result changed once
  its subject file vanished (score/passed/skipped/unscorable moved), so the
  check reads the shadow copy. Direct, targeted proof: the check itself needs
  fixing, not the harness.
- **`REACHABLE-indirect` (`REACHABLE_INDIRECT` — "vanished")** — the check
  didn't change state, it disappeared from the evaluator's output entirely.
  That proves the *evaluator* noticed the file's absence, not that *this*
  check specifically reads it — deleting one file can collapse an entire
  evaluator (e.g. an early parse failure) and take unrelated checks down with
  it. Reported with a **collateral ratio** (how many of the row's other
  declared checks also vanished in the same rescore) — a large simultaneous
  vanish fraction is the collapse signature, not a wiring proof for any one
  check.
- **`UNREACHABLE`** — the check's result is byte-identical whether the
  shadow's copy of the file exists or not: it never reads the shadow copy at
  all (a hardcoded absolute path, `Path.cwd()` captured at import, ...). This
  is a **harness limitation**, not evidence the check itself is broken — the
  fix is "make the rubric resolve through `repo_root()`", never "weaken or
  delete the mutation."

## Run it

```bash
pip install -r evals/requirements.txt

# ad-hoc deck check (no registry/keys needed)
python evals/run_experiment.py --deck path/to/deck.html

# registry deliverable, with negatives (gate passes only if goldens PASS and negatives FAIL)
python evals/run_experiment.py --deliverable deck --negatives

# deliverable-structural contract lint over the golden engagement's output files
# (fixture files on disk — not an end-to-end run; see tier 3 above)
python evals/run_experiment.py --altitude deliverable-structural

# a component's unit eval (used by bb-build verify)
python evals/run_experiment.py --component roi-financial-modeler

# a rubric_calibration row — scores the RUBRIC against a frozen golden,
# NOT the agent in its covers_agent: (prints that as a banner every run)
python evals/run_experiment.py --calibration market-context-rubric

# prove every check a row declares actually goes red under mutation
python evals/run_experiment.py --mutate run-experiment-runner

# preflight: gating goldens resolve + mutation-law enforcement (run first in CI)
python3 evals/check_registry.py
```

Full current flag list (`evals/run_experiment.py`'s argparse — verify against
the source before trusting any other list, including this one): `--component
<row>`, `--calibration <row>`, `--deliverable <deck|roi|assessment>`,
`--altitude {unit,deliverable-structural,deliverable}`, `--deck <file>`,
`--mutate <row>`, `--negatives`, `--target <path>`, `--threshold <float>`,
`--regenerate` (path-1, local only, refuses under CI — see `evals/path1.py`). There is
**no** standalone `--deliverable-structural` flag — that mode is
`--altitude deliverable-structural`. Passing the retired altitude name (the
one this mode was renamed from, #188) as `--altitude` **hard-errors**
(exit 2) with the rename rationale — never run it.

Exit code is the gate: `0` = pass, `1` = fail (`2` = usage/argument error,
including the retired-altitude guard). This is what `bb-build` runs as its
verify step and what `.github/workflows/evals.yml` runs as a required check.

## Langfuse (optional, Cloud)

Local mode works with zero setup. To log scores + history and enable LLM-judge:

```bash
# .env (gitignored) or CI secrets
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com      # or EU host
ANTHROPIC_API_KEY=sk-ant-...                  # enables judge rubrics
pip install "langfuse>=2.0" "anthropic>=0.40"
```

**PII:** datasets are curated golden fixtures — scrub once with
`scripts/anonymize_transcript.py --file <path> --engagement-dir <dir>` and they
are safe for Cloud. The script is a facade over `scripts/pii/engine.py`
(Presidio), which needs Python 3.10–3.13 — run it through `.venv/bin/python`
(`bash scripts/setup_pii.sh` once if `.venv` doesn't exist) or
`.claude/hooks/_resolve_python.sh scripts/anonymize_transcript.py ...`, not
plain system `python3`. Only the Loop-3 monitor touches live outputs
(scrub-on-ingest, or keep it off until needed).

## Calibration

Thresholds in `registry.yaml` are set so every golden scores **above** and every
matched negative scores **below**. An eval not calibrated against a real failure is
decoration. Findings so far: most pre-2026-06-22 engagement artifacts (NFIS v2 deck,
ROI, assessment) drift from the PR #71 design system — they are **monitor** targets,
not goldens. The judge `standards_snapshot/` is a FROZEN copy of the design rules;
bump it deliberately when the live standard changes, or green scores start lying.

Calibration against a real negative is what makes a check meaningful *within*
its tier — it is a separate concern from the mutation law above. A
rubric-calibration check can be perfectly calibrated (every golden above
threshold, every negative below) and still tell you nothing about the agent
prompt, because calibration only proves the regex distinguishes good text
from bad text — never that it read the prompt that generated either.

## Billing: what costs money and what doesn't

Stated plainly, because the three tiers above have three different billing
stories:

- **CI (`.github/workflows/evals.yml`) is $0 and key-free.** It runs
  `check_registry.py` plus the code-only checks — executable-tier `code:`
  and deliverable/deliverable-structural code evaluators. None of that needs
  an API key.
- **`evals/rubrics/judge/judge.py` currently uses the `anthropic` Python SDK**
  (`import anthropic`, `anthropic.Anthropic()`), gated on `ANTHROPIC_API_KEY`
  — this is a **metered API key**, always, whenever a judge actually runs.
  Re-routing `judge()` through `claude -p` so judges run on a Claude
  subscription instead is **#203**, tracked, **not yet landed**.
- **`evals/path1.py`** shells out to `claude -p` (`run_agent()` — no API key,
  reuses the caller's Claude subscription via the CLI) to regenerate a
  component's output headlessly on a golden input, then scores it — this is
  what would let an agent-prompt edit re-score live and catch prompt
  regressions. It is **orphaned today**: nothing in `run_experiment.py`, CI,
  or the `bb-build` verify step invokes it. Wiring it in as a local-only tier
  with a CI guard is **#204**, tracked, **not yet landed**. Until then, the
  only way to exercise path-1 is to run `evals/path1.py` yourself, locally,
  outside the harness.
- The 11 `rubric_calibration:` rows each declare a `path1_judge:`
  list (renamed from `judge:` in #182) — semantic LLM-as-judge checks meant
  to apply only when the component is regenerated via path-1. **This key
  does not gate anything today.** The component gate's thin adapters
  (`rubrics/component/<name>.py`) call only `specifics._<fn>` and never
  reach `path1_judge:` checks, by design — a metered judge must never sit on
  a gating path, which is exactly why CI stays $0 and key-free. These rows
  are consumed once #204 lands, not before.

Net: run the gate today (`--component`, `--deliverable`,
`--altitude deliverable-structural`, `check_registry.py`, `--mutate`) and it
costs nothing and needs no key. Run a judge, or `path1.py` by hand, and it
runs against your own Claude subscription/API key locally — never in CI.

## Adding a component to the harness

1. **Decide the tier before writing anything.** If the evaluator will invoke
   real repo code (import a real module, subprocess a real script, generate
   and inspect a real artifact) against a fixture that can actually fail —
   it's executable-tier; write it that way, and note the new row in the
   executable list above (this README and `bb-build`'s SKILL.md both name
   the five explicitly — keep them in sync). If it will score a frozen
   golden fixture with a regex/string-match adapter over
   `rubrics.component.specifics`, it's rubric-calibration: write it that
   way, and do not describe its PASS as agent-prompt verification anywhere
   — in the registry comments, in the PRD, or in a PR description.
2. Add a row to `registry.yaml` (inputs, `code:` checks, `path1_judge:`
   rubrics if rubric-calibration, threshold, golden).
3. Add a **mutation entry** (`mutations:`, or dict-form `negatives:`) for
   every `code:` check the row declares — this is now required by the
   mutation law above, not optional polish. A row with no mutation proof at
   all fails `--mutate <row>` outright; a row with partial coverage is
   counted as DEBT by `check_registry.py` until every check is covered.
   Prove it: `python evals/run_experiment.py --mutate <row>` should show
   every declared check proven.
4. Add a golden (scrubbed) and, for rubric-calibration rows, a **known-bad
   negative per check** — not just one negative for the whole row. (Today
   most rubric-calibration rows share a single golden with no per-check
   negatives; re-filing them with per-check negatives is tracked as **#201**
   and has not landed — a *new* component should not repeat that gap.)
   Calibrate the threshold so the golden scores above it and every negative
   scores below.
5. New agents author their eval cases as part of the `bb-prd` (definition of
   done) — including which tier the new component's checks belong to.
