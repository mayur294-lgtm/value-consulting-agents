---
version: 7
prd: prd-v7.md
status: draft
date: 2026-08-26
author: Mariam Titus George
previous: solution-design-v6.md
---

# Solution Design v7 — Executable evals, honest altitudes, calibrated goldens

## Component Structure

```
evals/
  registry.yaml                  MODIFIED  three tiers + `mutations:` + `negatives:`; `pipeline:` → `deliverable_structural:`
  run_experiment.py              MODIFIED  tier dispatch, negatives at component altitude, no vacuous skip,
                                           declared-check coverage assert, old-flag hard error, --mutate
  mutations.py                   NEW       the mutation harness: source-mutation (executable) + fixture-mutation
                                           (calibration), both in a temp copy; never writes the working tree
  check_registry.py              MODIFIED  preflight fails when a declared check has no mutation entry
  path1.py                       MODIFIED  CI refusal guard; scores the row's real rubric, not just governance
  rubrics/
    _harness.py                  NEW       shared kit: build_fixture_engagement(), run_hook_subprocess(),
                                           registered_interpreter(), inject_fault() — extracted from the
                                           pii_anonymizer / mcp_query_guard duplication
    base.py                      MODIFIED  CheckResult gains `exercised` + `unscorable`; skipped no longer implies passed
    judge/judge.py               MODIFIED  `claude -p` subprocess replaces the anthropic SDK; _available() checks CLI auth
    component/
      hooks/                     NEW       one module per registered hook, all via _harness
        anonymize_guard.py · require_checkpoint.py · require_harness.py
        enforce_journal.py · synthetic_knowledge_guard.py · eval_on_stop.py
      artifact_boundary.py       NEW       cap_roi_config, synthetic_policy, deanonymize_dir contracts
      pipeline_workspace.py      NEW       closes :134 — no composed prompt / cwd names the client
      engagement_identity.py     NEW       init_engagement_identity + map binding
      engagement_migration.py    NEW       migrate_engagements dry-run + deny-term-loss refusal
      roi_calibrator.py          NEW       scenario curves + cap parity
      frontline_builders.py      NEW       pptx/html builders emit valid, on-token artifacts
      mcp_query_guard.py         MODIFIED  interpreter from settings.json (:116); + scan-limit fail-closed (:117)
      pii_anonymizer.py          MODIFIED  interpreter parity; fixture gains a markdown table + attendee bullets (:107)
      specifics.py               UNCHANGED shared by runtime.py — behaviour frozen except the roi parser fix
    deliverable/
      roi.py                     MODIFIED  parse current value_lever_groups schema (:41); unscorable ≠ 0/0
      visual_render.py           MODIFIED  wired to a registry row, or deleted (:16)
    structural/                  RENAMED   was rubrics/pipeline/ — contracts.py moves, import path follows the altitude
.github/workflows/evals.yml      MODIFIED  paths += .claude/hooks/** (:114); adds changed-component runs +
                                           `report` deliverable (:15); adds the mutation-proof job
.claude/skills/bb-build/SKILL.md MODIFIED  verify step no longer claims a frozen-fixture score verifies a prompt change
evals/README.md                  MODIFIED  three tiers documented; the mutation requirement stated as law
```

**Contribution tier:** all paths are Architect-only (`evals/**`, `.github/**`, `.claude/**`). `enforce-contribution-scope.yml` is unaffected.

---

## Data & Contract Model

### 1. Registry — three explicit tiers, replacing one overloaded `components:`

```yaml
# TIER 1 — executable. Builds its own fixture, runs the real code. $0, CI-blocking.
executable:
  anonymize-guard:
    module: .claude/hooks/anonymize-guard.py
    threshold: 1.00
    code: [fails_closed_on_inputs_path, allows_outside_inputs, stale_sibling_denied,
           runs_under_registered_interpreter]
    mutations:                        # REQUIRED — preflight fails without one per check
      fails_closed_on_inputs_path:
        file: .claude/hooks/anonymize-guard.py
        find: "return DENY"
        replace: "return ALLOW"
      runs_under_registered_interpreter:
        file: evals/rubrics/_harness.py
        find: "registered_interpreter()"
        replace: "sys.executable"
      # ... one per declared check

# TIER 2 — rubric calibration. Scores a frozen golden. Proves the RUBRIC, not the component.
rubric_calibration:
  market-context-rubric:            # keyed by RUBRIC, never by agent name
    rubric: rubrics.component.market_context_researcher
    golden: evals/goldens/market_context_golden.md
    threshold: 0.80
    covers_agent: market-context-researcher   # documentation only — NOT a verification claim
    code: [annual_report_attempted, module1_metrics_present, competitor_benchmark_section]
    negatives:                       # fixture mutation, per check — no new files
      annual_report_attempted:   {strip: "(?is)##\\s*Annual report.*?(?=\\n##|\\Z)"}
      module1_metrics_present:   {strip: "(?is)##\\s*Module 1.*?(?=\\n##|\\Z)"}
      competitor_benchmark_section: {strip: "(?is)##\\s*(Competitor|Benchmark).*?(?=\\n##|\\Z)"}

# TIER 3 — deliverable + deliverable-structural. Final artifacts and inter-agent contracts.
deliverables: { deck: {...}, roi: {...}, assessment: {...}, report: {...} }
deliverable_structural:              # was `pipeline:` — same checks, honest name
  evaluator: rubrics.structural.contracts
  threshold: 0.90
  target: evals/goldens/pipeline_engagement/outputs
```

**Contract invariants** (each enforced by a check in the `run-experiment-runner` row):
- Every name in a `code:` / `judge:` list MUST appear in the run's executed set, or the run fails.
- Every name in a `code:` list MUST have a `mutations:` entry, or preflight fails.
- A `rubric_calibration` row MUST NOT be keyed by an agent name, and its `covers_agent` field is inert documentation — the runner never treats it as a verification claim.
- Only `executable` and `deliverable*` rows may gate in CI. `rubric_calibration` rows gate too, but their output always carries the tier banner.

### 2. Mutation record — the harness's unit of work

```python
Mutation = {
  "check":   str,            # the check this must make red
  "file":    Path,           # source (executable tier) or the golden (calibration tier)
  "find":    str,            # literal or regex
  "replace": str,            # "" for a strip
  "kind":    "source" | "fixture",
}
MutationResult = {
  "check": str, "proven": bool,
  "before": float,           # check score unmutated  (must pass)
  "after":  float,           # check score mutated    (must fail)
  "detail": str,             # why, when not proven
}
```

**Isolation contract (D2):** the harness copies the target file's module tree into a `TemporaryDirectory`, prepends that path to `sys.path`, mutates the copy, imports fresh (`importlib.invalidate_caches()`), scores, and discards. **The working tree is never written to.** A crash or SIGKILL leaves nothing behind — which matters because this runs inside `bb-build` subagents and in CI.

### 3. `CheckResult` — two new fields

```python
CheckResult(
  name, score, passed, detail,
  skipped:    bool = False,   # EXISTING — but no longer implies passed
  hard_fail:  bool = False,   # EXISTING
  exercised:  str | None = None,   # NEW: "scripts/pii/engine.py via python3 (3.9.6)"
  unscorable: bool = False,   # NEW: parser could not read the artifact — never rendered 0/0 (:41)
)
```

`RubricResult.score` continues to average non-skipped checks. `unscorable` checks are excluded from the average **and** surfaced in `runtime.py`'s report as `unscorable`, never as a flag.

### 4. Judge transport — same JSON contract, different pipe

```
BEFORE: anthropic.Anthropic().messages.create(...)      → metered API key, always
AFTER:  subprocess.run(["claude","-p",prompt,           → Claude subscription
                        "--append-system-prompt",sys])
```

Response contract is unchanged and still strict: `{"score": 0..1, "pass": bool, "reason": str}`. `_available()` changes from "`ANTHROPIC_API_KEY` is set" to "`claude` is on PATH and authenticated". A declared-but-unavailable judge now **fails the run** (D5).

---

## Agent / Pipeline Steps

No agents change. The units of work are eval rows and runner modes:

| Name | Type | Inputs | Outputs | Purpose |
| --- | --- | --- | --- | --- |
| `run_experiment --executable <n>` | runner mode | registry row | RubricResult + `exercised` | Build fixture, run real code, score |
| `run_experiment --calibration <n>` | runner mode | registry row + golden | RubricResult + tier banner | Prove the rubric still accepts good and rejects broken |
| `run_experiment --mutate <n>` | runner mode | registry row + `mutations:` | MutationResult[] | Prove each check can fail |
| `run_experiment --deliverable-structural` | runner mode | fixture outputs dir | RubricResult | Inter-agent contract lint (renamed) |
| `path1 --agent <n>` | local-only mode | agent prompt + golden input | fresh output + score | Regenerate and score; refuses under CI |
| `check_registry` | preflight | registry | pass / fail / DEBT | Reject uncovered checks before scoring |

---

## Integration Points

| Touchpoint | What changes | Risk | Why |
| --- | --- | --- | --- |
| `runtime.py` → `orchestrate.py:2242` + `eval-on-stop` (`settings.json:74`) | Shares `specifics.py` and the deliverable rubrics with the dev gate | **HIGH** | Tightening a rubric to bite in CI can start false-flagging live client engagements. Every check-function change is re-scored against a real past engagement's committed outputs before its ticket closes |
| `.claude/settings.json` hook registrations | Read (not written) by `_harness.registered_interpreter()` | **MEDIUM** | The rubric now derives its interpreter from the registration, so the two cannot drift (:116). If a registration changes shape, the harness must fail loudly, not fall back |
| `evals.yml` `paths:` filter | Gains `.claude/hooks/**` | **MEDIUM** | Closes :114. Widening the filter means more PRs run the gate — intended, but CI minutes rise |
| `bb-build/SKILL.md` verify step | Instruction corrected; adds the uncovered-prose branch | **MEDIUM** | This is the artifact that manufactured the false "verified". Changing it changes what every future ticket claims |
| `rubrics/pipeline/` → `rubrics/structural/` | Package rename; import paths follow | **LOW** | Mechanical, but `registry.yaml`, `runtime.py`, and README all reference it |
| `judge.py` transport | SDK → CLI subprocess | **LOW** | Same JSON contract; `_available()` gates it. Reverting one function restores present behaviour |
| `evals/goldens/*` | Unchanged bytes; re-filed under a new registry section | **LOW** | Deliberately no content edits — re-filing is a labelling fix, and editing goldens in the same PR would confound the calibration |

---

## Technical Decisions

**D1 — Three named tiers replace one overloaded `components:` section.** *Alternative:* keep `components:` and add a `tier:` field. *Why:* the section name is what people read in the registry and in `bb-build`'s instructions; `components: market-context-researcher:` reads as "this gates that agent" no matter what a `tier:` field says underneath. The failure was a naming failure, so the fix has to be structural naming. *Trade-off:* a bigger registry diff and every caller of `--component` updates.

**D2 — Mutations run against a temp copy of the module tree, never the working tree.** *Alternative (a):* in-place edit with restore in `finally` — how the v6 gate-bites proofs were done by hand. *Alternative (b):* a throwaway git worktree. *Why:* this harness runs inside `bb-build` subagents and in CI, where a crash or SIGKILL is a normal event; in-place mutation would leave a developer's tree silently corrupted with a deliberately-broken security hook. A worktree is fully isolated but needs clean git state, which mid-ticket builds rarely have. *Trade-off:* import plumbing (`sys.path` juggling plus `importlib.invalidate_caches()`), and mutations must name a file the harness can copy in isolation.

**D3 — Negatives are declarative fixture mutations, per check, not separate negative files.** *Alternative (a):* one malformed negative file per rubric, mirroring `deck`. *Alternative (b):* hand-written witness checks (`overcap_negative_gate_witness`). *Why:* at threshold 0.80 a whole-artifact negative must break more than 20% of checks to drop below the line, so individually inert checks still hide — which is exactly the defect. A per-check fixture mutation proves the specific claim: *this check detects the absence of the thing it says it detects.* And it adds no files. *Trade-off:* the negative is a regex in the registry rather than a readable artifact, so a badly-written `strip` can silently no-op — mitigated by requiring the before/after scores in `MutationResult`, so a mutation that changed nothing is itself a failure.

**D4 — `--altitude pipeline` hard-errors after the rename; no alias, no warning.** *Alternative:* silent alias or a deprecation warning. *Why:* the misreading *is* the bug. An alias preserves it perfectly, and CI warnings get scrolled past — the same mechanism that let DEBT lines sit ignored for six PRs. The error text carries the rationale, so the break teaches. *Trade-off:* any script or muscle-memory invocation breaks loudly on day one. Intended.

**D5 — Declared means required: a check the run didn't execute fails the run.** *Alternative:* tolerate in CI, or report as DEBT. *Why:* `market-context-researcher` declares four checks (three `code`, one `judge`) and silently ran three; the judge returned `passed=True, skipped=True` and vanished. Two different definitions of "green" is how this confusion started, so there is now one. *Trade-off:* CI rows must not declare judges (CI stays key-free), which means the registry now encodes *where* a row can gate — an extra constraint authors must respect, enforced by preflight.

**D6 — The rubric derives its interpreter from `settings.json`, rather than picking a correct one.** *Alternative:* hardcode `python3`, or route rubrics through `_resolve_python.sh`. *Why:* both would be right today and wrong after the next registration change. Reading the registration makes drift structurally impossible, and it is the same reasoning as v6's D12 — resolve at the boundary, in one place. Note the registrations are *correct* today (bare `python3` for stdlib-only hooks, per v6's D13); the bug is that the rubric used `sys.executable` instead. *Trade-off:* the harness must parse `settings.json`'s nested hook shape and fail loudly if it changes.

**D7 — Goldens keep their exact bytes; only their filing changes.** *Alternative:* rewrite them to be more discriminating in the same PR. *Why:* cross-scoring shows `market-context-researcher` scores 0.833 against the *benchmark* golden and vice-versa 0.889 — they detect generic consulting prose. That is real and worth fixing, but editing a golden while simultaneously adding its first negative confounds the calibration: you could not tell whether a new red came from the better negative or the changed golden. *Trade-off:* the weak discrimination survives this cycle, recorded as a follow-up.

**D8 — `unscorable` is a first-class result, distinct from a zero.** *Alternative:* let a parser gap score 0 and rely on humans to interpret it. *Why:* on Harborlight run 7 the `roi` rubric scored a demonstrably-correct config 0/0 because its parser did not recognise `value_lever_groups`. A parser gap is not a quality finding, and rendering it as one trains consultants to ignore flags — the same desensitisation that made false greens survivable. *Trade-off:* one more state everywhere that renders a score.

**D9 — Judges move to `claude -p`; path-1 is wired but hard-guarded out of CI.** *Alternative:* keep the SDK where a developer has a key. *Why:* the founding commit specified "runs locally with no keys," and `judge.py` is the only thing that broke that. Routing through the CLI makes judges subscription-funded and removes the metered key from every path. Path-1 stays local because Max rate limits and CI OAuth make it unsuitable as a gate — and because a personal subscription powering org CI is a licensing question best never raised. *Trade-off:* judge availability now depends on CLI auth state rather than an env var, which is less scriptable — hence D5 making an unavailable judge loud.

**D10 — `specifics.py` behaviour is frozen this cycle except the `roi` parser fix.** *Why:* it is shared with `runtime.py`, which scores live client engagements on every pipeline run and every consultant session. Changing check semantics and adding the negatives infrastructure at once would make any new runtime flag ambiguous in origin. *Trade-off:* known-weak checks stay weak for one more cycle.

---

## Build Sequence

Five PRs, each independently reviewable, each green on its own.

| PR | Contents | Rationale |
| --- | --- | --- |
| **1** | `run_experiment.py` runner fixes: negatives at component altitude, missing-target fails, declared-check coverage, `unscorable`; `base.py` fields | **The foundation and the smallest honest win.** Nothing else can gate until a gate can fail. Lands with its own `run-experiment-runner` row |
| **2** | `mutations.py` + `--mutate` + preflight enforcement | The acceptance mechanism for every later PR. Ships before the rows that depend on it |
| **3** | Altitude rename (`pipeline` → `deliverable-structural`, `rubrics/structural/`), `bb-build/SKILL.md` correction, README rewrite | **Pure honesty, no new machinery.** Highest value per line changed — it stops the harness making false claims even before new coverage exists |
| **4** | CI wiring: `:114` paths, `:116` interpreter parity, `:15` changed-component + `report`, `:16` visual_render; `:107`/`:117` fixture and scan-limit gaps | Closes the backlog's false-green cluster on the now-solid runner |
| **5** | The executable tier: 6 hook rows, `artifact_boundary`, `pipeline_workspace` (:134), identity, migration, calibrator, frontline builders; the 11 calibration re-filings + negatives; `judge()` re-route; path-1 wiring + CI guard | The bulk. Splittable per component if it grows — every row is independent by construction |

**Sequencing note.** PR 3 deliberately precedes the new coverage. Removing a false claim is worth more than adding a true one, and it is the change that stops #118-style rubber stamps immediately.

---

## Open Items for Build

1. **`visual_render.py` — wire or delete (:16).** Decide on evidence: if the deck calibration figures (golden 1.000 / negative 0.364) can be reproduced, wire it to a row; if not, delete it rather than carry dead code.
2. **Mutation regex fragility.** A `find:` string that stops matching after a refactor must fail loudly (mutation changed nothing → not proven), never silently pass. Verify this behaviour explicitly in PR 2.
3. **`frontline_builders` scope.** Three builders (`pptx`, `2026_html`, `presenter`) — confirm during build whether one shared row covers them or each needs its own.
4. **Runtime re-scoring corpus.** Pick the specific past engagements used as the false-red regression check (Harborlight run 7 is the known :41 case); they must be committed and anonymised.
5. **CI minutes.** Widening `paths:` plus a mutation job raises cost; measure in PR 4 and cap if needed.
