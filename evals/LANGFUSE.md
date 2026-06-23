# Langfuse — how cortex uses it

git is the **source of truth** (rulebook); Langfuse is the **scoreboard + live engine**.
Everything below is mirrored from git, automatically, on merge to `main`
(`.github/workflows/langfuse-sync.yml`).

## What's on Langfuse

| Langfuse area | What's there | Wired by |
|---|---|---|
| **Prompts** | the 20 LLM-judge rubrics (`cortex-eval/*`, versioned, label `production`) | `sync_to_langfuse.py` |
| **Datasets** | golden + negative cases (`cortex-deck`, …) | `sync_to_langfuse.py` |
| **Tracing** | every run → a `run:<engagement>` trace with a child observation per **agent** and per **deliverable**, each carrying its eval score (A1); plus a live `agent:<name>` observation per agent call with prompt/output/cost/turns (A2) | `runtime.py` + `orchestrate.py` |
| **Scores** | per-agent / per-deliverable / pipeline scores on every run | `runtime.py` |

So Langfuse "Prompts" shows ~20 (the judges only) — the **code** evaluators
(deck/ROI/assessment/report/governance/contracts/per-agent) are Python in git and
never appear as prompts. Total suite ≈ 80+ checks across ~18 evaluators + 20 judges.

## Optional: server-side auto-evaluators (the last 10%)

Today cortex RUNS the judges itself (in `runtime.py` / CI) and pushes scores to
Langfuse. If you also want Langfuse to **auto-run a judge on every incoming trace**
(no code path needed), enable it in the UI — it references the prompts we already sync:

1. Langfuse → **Evaluators** → New LLM-as-a-judge.
2. Pick the prompt `cortex-eval/<judge>` (e.g. `cortex-eval/report_tone`).
3. Target = **Traces** (or a Dataset for regression experiments).
4. Map the trace input/output to the rubric variables; set the score name.

This is additive — our git-side scoring already covers dev-gate + runtime.

## Keys
Set `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` (EU:
`https://cloud.langfuse.com`) in `evals/.env` (local) and repo secrets (CI). Shared
dev keys distribute out-of-band via `evals/.env.shared` (see `setup_dev.sh`).
