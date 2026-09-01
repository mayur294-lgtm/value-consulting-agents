"""Executable eval rows for the `.claude/hooks/*` enforcement layer (#197).

`.claude/settings.json` registers seven Python hooks. Before this package only
ONE of them (`mcp-query-guard`) had a registry row, and `anonymize-guard` was
covered by a single check buried inside the `pii-anonymizer` row. Hooks are the
enforcement layer for every governance rule this repo claims to hold
(solution-design-v6 D7) — an ungated enforcement layer is a rule that exists
only in prose.

One module per hook, one registry row per module, threshold 1.00:

    anonymize_guard             .claude/hooks/anonymize-guard.py
    require_checkpoint          .claude/hooks/require-checkpoint.py
    require_harness             .claude/hooks/require-harness.py
    enforce_journal             .claude/hooks/enforce-journal.py
    synthetic_knowledge_guard   .claude/hooks/synthetic-knowledge-guard.py
    eval_on_stop                .claude/hooks/eval-on-stop.py

Every check in every module invokes the REAL hook SCRIPT as a subprocess,
through `rubrics._harness.run_hook_subprocess`, under the interpreter
`.claude/settings.json` actually registers for it (bare `python3` — 3.9.6 on
most consultant machines). Nothing here imports a hook module and monkeypatches
it: the contract under test is the PROCESS one (stdout JSON shape, exit code),
and an in-process call proves only that some Python functions behave.

Fixtures are synthesized inside a `tempfile.TemporaryDirectory()` and pointed at
via `CLAUDE_PROJECT_DIR`. NOTHING here ever reads or writes `engagements/` in
the real checkout — that tree is real, gitignored client material. Per the
repo's synthetic-quarantine programme no fixture uses a fictional bank name;
obviously-placeholder `zzz`-prefixed tokens stand in for a client identity.

FAIL-CLOSED vs FAIL-OPEN IS PER-HOOK, AND THE ROWS SAY SO
---------------------------------------------------------
Only `anonymize-guard` has a fail-CLOSED contract, and only inside
`engagements/*/inputs/` — a globally fail-closed guard wedged every session
once already (PR #82). Every other hook here documents itself as fail-OPEN
("never wedge a session on a hook bug"). So the ticket's
`fails_closed_under_injected_fault` is authored ONLY on `anonymize_guard`; the
other five carry `fails_open_under_injected_fault`, which asserts the contract
those hooks actually have. Writing the fail-closed check on a fail-open hook
would have certified the opposite of the design.
"""
