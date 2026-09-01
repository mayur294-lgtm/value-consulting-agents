# What changed in Cortex

*Last updated: 2026-08-27*

Cortex has had a substantial amount of work land since the last time most of the
team pulled. This note covers all of it, grouped by whether it needs anything
from you.

Read section 2. It is the only part that asks you to do something.

---

## 1. Changes to how Cortex is built — no action needed

If you use Cortex to do consulting work, you can skip this section entirely.

The development harness (`bb-prd → bb-design → bb-tickets → bb-build →
bb-pr-review → bb-refine`) and the eval suite behind it were substantially
rebuilt. Evals are now the gate that decides whether a change to an agent or a
skill is allowed to merge, and the gate itself is now provably able to fail — a
mutation harness checks each eval by breaking the thing it is meant to catch and
confirming it goes red.

This matters to anyone changing Cortex's own agents, skills or pipeline code.
It changes nothing about how you run an engagement.

---

## 2. PII protection — one command, about ten minutes

**What you need to do:** pull `main`, then run one command.

> **Full instructions: [presidio-setup.html](presidio-setup.html)** — a standalone
> one-time guide. It is not part of the cheat sheet, because it is a job you do
> once and never reopen.

**Why.** Cortex has always had a gate meant to stop raw client material reaching
the model. When we measured it, it covered 3 of the 77 real files sitting in
engagement input folders. Annual reports, RFPs, client decks and pricing
spreadsheets — the PDFs, Word files and spreadsheets that make up almost all of
what we actually work from — were being read in unscrubbed. Name detection was
five hand-written patterns plus whatever someone had typed into an intake form;
when that form was empty, client and stakeholder names went out in plaintext
with no warning.

**What is different now.** Detection uses a real named-entity engine instead of
regular expressions. Coverage extends from three markdown files to every
text-bearing document in an engagement's `inputs/`. The gate moved to where you
actually work — it used to live only in the assessment pipeline, which almost no
live engagement runs, so we had built the strongest control on the least-used
path. Client names are now also stopped on the way out to Backbase Infobank.
And engagement folders are opaque IDs rather than client names, because the
folder name is sent to the model on every call.

**What it costs you.** One setup command, once. After that it is invisible.

## 3. The pipeline is now a set of skills you can use individually

**What you need to do:** nothing. This is new capability, not a migration.

**The problem it solves.** The assessment pipeline was all-or-nothing. Every
agent's operating instructions lived inside `orchestrate.py`, so the only way to
get a capability assessment or an ROI model was to run the entire ten-agent
sequence — hours, and real cost, for one artifact. In practice almost nobody did
that. Engagements were being done in single skills or in raw Claude, which meant
none of the methodology, evidence tracing or governance applied.

**What is different now.** Each agent's contract lives in the agent itself
rather than in the pipeline script. The pipeline still runs exactly as before,
but every step in it also works on its own. If you need one ROI model, you ask
for one ROI model.

The practical version: you no longer have to know whether the thing you want is
an agent, a skill or a pipeline step. Ask for the deliverable.

**Where to find what's available.** The cheat sheet
([cortex-cheat-sheet.html](cortex-cheat-sheet.html)) lists every pipeline, skill
and agent, organised by the job you're trying to finish. Unlike the PII guide,
it is a living document — it is generated from the repository and changes with
every release, so bookmark it rather than saving a copy. Short walkthrough
videos are released against it one a week.

---

---

## The three documents

| Document | What it is | How often it changes |
|---|---|---|
| This brief | What landed in this release | Once |
| [presidio-setup.html](presidio-setup.html) | The one-time install | Never — it's a finite job |
| [cortex-cheat-sheet.html](cortex-cheat-sheet.html) | Everything Cortex can do | Every release |

## Where to ask

Anything that does not work as described here, or anything in the cheat sheet
that turns out to be wrong, is worth flagging — it means the documentation
drifted from the system, which is the failure we most want to catch early.
