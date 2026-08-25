# Cortex Evals

Evals are the **verify gate** of the bb-* development harness. For a document
factory there is no compiler, so the eval suite *is* the compiler: it is how a
change to an agent/skill/template/pipeline is proven not to have regressed
behaviour — locally, at the gate, and in production.

See the design plan: `~/.claude/plans/peppy-stargazing-swan.md`.

## Layout

```
evals/
  registry.yaml                 # per-component / per-deliverable spec (THE config)
  run_experiment.py             # CLI runner = the gate; local mode needs only stdlib + PyYAML
  requirements.txt
  goldens/                      # scrubbed golden fixtures + negatives (safe for Langfuse Cloud)
    deck_valid_min.html         #   on-palette calibration anchor (good must PASS)
    negatives/                  #   known-bad per check (must FAIL)
  rubrics/
    base.py                     # CheckResult / RubricResult
    deliverable/                # CODE evaluators: decks.py, roi.py, assessment.py
    pipeline/contracts.py       # integration altitude: inter-agent contracts
    component/                  # unit altitude: per-agent behaviour (see "Component evals")
    judge/                      # LLM-as-judge harness (Opus) + prompts/ + standards_snapshot/
```

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

## Three altitudes

1. **Component (unit)** — score an agent's direct output on a fixed input. Fast dev signal.
2. **Pipeline (integration)** — *most important*. Run the chain end-to-end on a golden
   engagement and check inter-agent contracts + final deliverables. Catches "a local
   edit to discovery broke the assembler."
3. **Deliverable** — score the final artifact (decks / ROI / assessment).

Each altitude mixes **code evaluators** (objective, cheap, run first) and **LLM-judge
evaluators** (semantic). Every check maps to a documented defect.

## Run it

```bash
pip install -r evals/requirements.txt

# ad-hoc deck check (no registry/keys needed)
python evals/run_experiment.py --deck path/to/deck.html

# registry deliverable, with negatives (gate passes only if goldens PASS and negatives FAIL)
python evals/run_experiment.py --deliverable deck --negatives

# pipeline integration on the golden engagement
python evals/run_experiment.py --altitude pipeline

# a component's unit eval (used by bb-build verify)
python evals/run_experiment.py --component roi-financial-modeler
```

Exit code is the gate: `0` = pass, `1` = fail. This is what `bb-build` runs as its
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

## Component evals (path-2 → path-1)

Today the suite scores existing artifacts (**path-2**). The **path-1** upgrade — used
by the bb-build inner loop — regenerates a component's output headlessly
(`claude -p`) on a golden input, then scores it, so editing an agent prompt re-scores
live and catches prompt regressions. Wire this once Langfuse keys are in.

## Adding a component/deliverable to the harness

1. Add a row to `registry.yaml` (inputs, code checks, judge rubrics, threshold, golden).
2. Add/extend the evaluator module under `rubrics/`.
3. Add a golden (scrubbed) and a known-bad negative; calibrate the threshold.
4. New agents author their eval cases as part of the `bb-prd` (definition of done).
