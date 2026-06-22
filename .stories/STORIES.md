# Stories

The living set of current-relevant wants for Cortex, with stable monotonic IDs
(`US-001…`). Built-vs-unbuilt is **not** tracked here — it's derived at cycle
close-out. IDs are never reused; a removed want leaves a permanent gap. The
Sprint Plan references these by ID and never restates the sentence.

## Pipeline Reliability

### US-001: Durable writes for code-owned outputs

As a consultant, I want the pipeline's large and important outputs to be written
atomically, so that a crash or interruption mid-write never leaves a corrupt
partial file that poisons downstream stages or a resume.

**Epic / Parent:** Pipeline Reliability

### US-002: Per-stage content validation

As a consultant, I want each stage's outputs validated for content — not just
existence — so that a stub or "I cannot complete this task" output is caught the
moment it's produced rather than in the final deliverable.

**Epic / Parent:** Pipeline Reliability

### US-003: Trustworthy run report

As a consultant, I want every run to finish by producing a report of what each
agent emitted and whether it passed, so that I can trust a run completed cleanly
or see exactly which artifact failed and why.

**Epic / Parent:** Pipeline Reliability

### US-004: Mode-aware expected outputs

As a consultant, I want validation to respect the run mode (interactive,
express, non-interactive), so that deliberately-skipped or intermediate outputs
are never false-flagged as failures.

**Epic / Parent:** Pipeline Reliability

### US-005: Tested reliability helpers

As an architect, I want the durability and validation helpers covered by unit
tests, so that the machinery the whole pipeline now trusts is itself verified.

**Epic / Parent:** Pipeline Reliability
