# bare_tests_case fixture

Deliberately has **no** `.synthetic` marker. It documents the third branch of
`synthetic_policy()` in `scripts/artifact_boundary.py`: no marker found anywhere
in the walk, and the path itself has no `tests` segment relative to the repo
root (this directory lives under `evals/goldens/synthetic_gate/`, not under a
`tests/` path) — so `synthetic_policy()` resolves it to `"real"`.

The path-based **fail-safe** (`no marker + a real `tests/` path segment →
"quarantine"`) cannot be exercised by pointing at this fixture's own location,
since committing it under `tests/` would collide with the existing
`tests/engagements/` synthetic-engagement convention. Instead, the
`bare_tests_fails_safe` check in
`evals/rubrics/component/knowledge_harvester.py` calls `synthetic_policy()`
directly on a simulated path — `<repo_root>/tests/engagements/<name>` — that
need not exist on disk (the gate's marker walk only checks for a `.synthetic`
file; a nonexistent path simply has none) and asserts the fallback resolves to
`"quarantine"`. This directory stays committed alongside `quarantine_case/`
and `never_case/` so the fixture set is a symmetric, self-documenting trio.
