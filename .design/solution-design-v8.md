---
version: 8
prd: prd-v8.md
status: draft
date: 2026-08-27
author: Mariam
previous: solution-design-v7.md
---

# Solution Design v8 — Direct-skill path naming policy + gate repairs

Builds directly on v6's D3, D4, D7, D13 and D14. None of those are reopened;
D13 in particular *determines* the shape of the new hook.

## Component Structure

```
.claude/hooks/
  output-naming-guard.py        — NEW. PreToolUse(Write|Edit). Stdlib only, no
                                  imports from scripts/pii/. Asserts the opaque
                                  prefix and the engagement breadcrumb. ~0.04s.
  mcp-query-guard.py            — MODIFIED. _iter_strings walks dict KEYS as well
                                  as values; _add_term stops producing unbalanced
                                  bracket terms.
.claude/settings.json           — MODIFIED. Registers output-naming-guard on
                                  PreToolUse(Write|Edit), on plain `python3`
                                  (no venv dependency — D13).

scripts/
  apply_output_naming.sh        — NEW. Consultant-invoked fixer, DRY RUN default,
                                  confirmation prompt on --apply. Wrapper only.
  apply_output_naming.py        — NEW. The fixer proper. MAY import
                                  scripts/pii/denylist.py — it is a CLI, not a
                                  hook, so D13's self-containment rule does not
                                  bind it and the ~1s import is irrelevant.
  pii/engine.py                 — MODIFIED. Phrase-scoped vendor allow-list;
                                  UK_NHS removed from DEFAULT_ENTITIES and a
                                  US account-number path put in its place.
  pii/vendors.py                — NEW. The vendor phrase list, one place.
  test_agent.py                 — MODIFIED. Client-name check resolves real terms;
                                  reports a LOUD skip when no map is present.
tests/
  quality_metrics.yaml          — MODIFIED. The six-foreign-bank regex is replaced
                                  by a resolver-backed check.

.claude/commands/               — MODIFIED (4): generate-roi-questionnaire.md,
.claude/agents/                   generate-roi-excel.md, prototype.md,
                                  usecase-doc.md, roi-financial-modeler.md.
                                  Filename prescriptions change from
                                  [CLIENT]_… to {engagement_id}_… .

evals/
  registry.yaml                 — MODIFIED. New row `output-naming-guard`
                                  (fully mutation-covered at authoring).
                                  mcp-query-guard: +2 checks, mutations for all 19.
                                  pii-anonymizer: +2 checks, mutations for all 21.
  rubrics/component/hooks/
    output_naming_guard.py      — NEW. Evaluator for the new row.
```

**What each new component owns.**

- `output-naming-guard.py` owns exactly one question, answerable from paths:
  *is this write allowed to land under this name?* It never resolves a client
  name, never opens a file's contents, never renames anything.
- `apply_output_naming.py` owns the opposite half: it resolves client terms,
  finds what carries them, renames, rewrites intra-engagement references, and
  drops the breadcrumb the hook reads.
- `pii/vendors.py` owns the phrase list and nothing else, so the eval row can
  mutate one file to prove the allow-list is load-bearing.

## Data & Contract Model

```yaml
# 1. The breadcrumb — engagements/<id>/.naming_policy_applied
#    Written ONLY by apply_output_naming.py, only after a successful apply.
#    chmod 600, inside the gitignored engagement tree.
{ "applied": "2026-08-27T14:02:11Z",
  "renamed": 41,          # files renamed
  "rewritten": 17,        # in-document references rewritten
  "unresolved": 2,        # references reported, not rewritten
  "tool_version": 1 }
#    The hook reads EXISTENCE ONLY — never the contents. A corrupt or truncated
#    breadcrumb must not be able to change what the guard allows.

# 2. The naming contract for engagement outputs
#    <engagement_id>_<descriptive_name>.<ext>     e.g. 5a057b98_Renewal_Proposal_v8.html
#    engagement_id: ^[0-9a-f]{8}$  — exactly as pii.identity mints it
#                                    (secrets.token_hex(4); the same regex
#                                    orchestrate.py already carries as _OPAQUE_ID_RE)
#    NO bracket token anywhere in the name. This is the reason this scheme was
#    chosen over the descriptive label: v6/D2 ended the [CLIENT] collision by
#    removing bracket tokens from the placeholder space, and a bracketed
#    filename convention walks back into it.

# 3. The exempt set — hand-maintained, greppable, in the hook
EXEMPT_NAMES  = {ENGAGEMENT_JOURNAL.md, CLIENT_PROFILE.md, ENGAGEMENT_CONTEXT.md,
                 roi_config.json, .engagement_session_id, .pipeline_run_report.json,
                 .pipeline_workspace, .naming_policy_applied, .migrated_from}
EXEMPT_PREFIX = {inputs/, .anon_}     # inputs/ is anonymize-guard's territory (D4)
EXEMPT_RULE   = any basename starting with "."
#    Everything else written under engagements/<id>/ needs the prefix.

# 4. Vendor allow-list — scripts/pii/vendors.py
VENDOR_PHRASES = ["Temenos T24", "Finacle", "nCino", "Mambu", "Backbase", ...]
#    PHRASE-scoped, never word-scoped. "Temenos" alone is NOT on the list, so a
#    person surnamed Temenos is still redacted. This is asserted by a check.

# 5. Structural client-name check contract
#    terms  <- .engagement_map.json (client field) + each CLIENT_PROFILE.md
#    result <- PASS | FAIL(file, line, term) | SKIPPED_NO_MAP
#    SKIPPED_NO_MAP is a THIRD state, never folded into the pass total.
```

**Non-obvious contract choices.**

*The hook reads the breadcrumb's existence, not its contents.* A JSON parse in a
hook is a failure mode: malformed JSON either raises (fail-open per D13) or
needs a try/except whose fallback is a policy decision made in an error path.
`Path.exists()` has neither problem. The counters in the file are for the
consultant and for `--recheck`, not for the gate.

*The prefix regex is the one `orchestrate.py` already carries.* `_OPAQUE_ID_RE`
exists and means "an opaque engagement ID as `pii.identity` mints it". Two
regexes for one concept would drift; the hook restates it as a literal for
D13 self-containment, and an eval check asserts the two stay identical — the
same hand-copy-with-a-parity-check pattern `drift_check.py` already uses for
`denylist.py` versus `mcp-query-guard.py`.

## Agent / Pipeline Steps

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `output-naming-guard` | hook (PreToolUse: Write, Edit) | tool payload path | allow / deny + message | Enforce the naming contract on the direct-skill path |
| `apply_output_naming` | CLI (consultant-invoked) | engagement dir | renames, rewrites, breadcrumb | Apply the policy to one engagement, dry-run by default |
| `mcp-query-guard` | hook (PreToolUse: `mcp__.*`) | tool payload | allow / deny | Unchanged role; now scans dict keys and builds balanced terms |
| `pii.engine` | library | text | anonymised text | Unchanged role; vendors survive, account numbers typed correctly |
| `test_agent` client-name check | structural check | `knowledge/**` | pass / fail / loud skip | Detect real client identifiers in shared knowledge |

No agent is added. No pipeline step changes — `copy_back()` is Python I/O and
fires no hook, which is stated here so a later reader does not infer that
pipeline outputs were gated.

## Integration Points

| Existing component / step | How it's touched | Risk |
| --- | --- | --- |
| `.claude/settings.json` | One new `PreToolUse` registration. Hook registration is itself gated by evals (#191) | **Medium** — a wrong matcher fires the guard on every Write everywhere |
| `scripts/pii/denylist.py` | Read by the fixer only. Not modified | Low |
| `.claude/hooks/mcp-query-guard.py` | Two behaviour changes; `drift_check.py` asserts parity with `denylist.py` and must stay green | **Medium** — the hand-copied deny-list logic is privacy-critical (D14) |
| `scripts/pii/engine.py` | `DEFAULT_ENTITIES` changes; every existing mapping file used `UK_NHS` for account numbers | **High** — a stored `.pii_mapping.json` containing `<UK_NHS_n>` must still de-anonymise. Backward compatibility is mandatory, exactly as v6 kept legacy flat mappings readable forever |
| Four commands + `roi-financial-modeler` | Filename prescriptions change | **Medium** — prompts; no eval row verifies a prompt, so the guard is the real enforcement |
| `tests/quality_metrics.yaml` | The client-name pattern is replaced | **Medium** — the check currently passes vacuously; making it real will fail on the six pre-existing knowledge files until they are cleaned, so the cleanup must land in the same change |
| `deliverable-structural` altitude | Lints output files by name | **Medium** — must stay green after the naming change |
| `.cortex-workspaces/` + `copy_back()` | Untouched | Low — no hook fires on Python I/O |

## Technical Decisions

**D1 — The guard asserts the required prefix; it never looks for a client name.**
*Alternatives:* have the hook resolve the deny-list and match basenames against
it (the obvious reading of the PRD); or import `scripts/pii/denylist.py`.
*Rationale:* v6/D13 measured the cost of a content-aware hook at 0.67–1.12s
against a 0.04s budget, and established the sharper danger — a module-level
import that raises exits a PreToolUse hook in a way Claude Code treats as
**non-blocking**, i.e. a guard built to block fails open. A positive assertion
(`^[0-9a-f]{8}_`) is answerable from the path alone: no deny-list, no imports,
no "I couldn't tell" branch, so failing closed is safe rather than a re-run of
PR #82's session-wedging. *Trade-off:* the guard cannot tell a client-named file
from any other unprefixed name — it blocks both. Accepted: the policy is the
prefix, not the absence of a name, and a stricter rule with no error path beats
a smarter rule with one.

**D2 — The breadcrumb, not a filesystem scan, answers "has this engagement been fixed?"**
*Alternatives:* scan the engagement's basenames on every write; keep a repo-level
state file. *Rationale:* the user's requirement is "apply the policy when I touch
an engagement", and a scan of 125 files per Write blows the budget. A breadcrumb
is one `stat()`, and `migrate_engagements.py` already establishes the pattern
with `.migrated_from` — including its resumability property, with no state file
to corrupt. *Trade-off:* deleting the breadcrumb re-arms the block. That is the
correct direction to fail.

**D3 — The fixer rewrites intra-engagement references and reports the rest.**
*Alternatives:* rename only and report; rename only and ignore.
*Rationale:* breaking the `.html`/`.zip` pairs and in-document links is exactly
why auto-rename-on-touch was rejected; moving that breakage into the fixer would
have kept the defect and only changed who triggered it. *Trade-off:* the fixer
edits document contents, so the dry run must show content edits as well as
renames, and a reference pointing outside the engagement is reported rather than
followed.

**D4 — `UK_NHS` leaves `DEFAULT_ENTITIES`, and old mappings still de-anonymise.**
*Alternatives:* leave it and document; add a higher-scoring US account recognizer
and let UK_NHS lose. *Rationale:* Cortex is a banking-consulting system with no
UK health data in scope, and the entity is actively mistyping US account numbers.
*Trade-off:* a genuine NHS number would stop being detected. Accepted for this
domain — but **every existing `.pii_mapping.json` containing `<UK_NHS_n>` must
still restore**, the same forever-compatibility promise v6 made to legacy flat
mappings. De-anonymisation reads whatever the mapping holds; only what is
*written* changes.

**D5 — The vendor allow-list is phrase-scoped and lives in its own module.**
*Alternatives:* a word-level stoplist; a regex in `engine.py`.
*Rationale:* a word-level list containing `Temenos` would stop redacting a person
with that surname — a privacy regression introduced by a quality fix, which is
the worst possible trade here. Phrases (`Temenos T24`) cannot do that. Its own
module means `--mutate` can strip one file and prove the list is load-bearing.
*Trade-off:* hand-maintained, and a vendor referred to by bare name in prose
still gets redacted. That is the safe direction.

**D6 — The structural client-name check gets a third result state: a loud skip.**
*Alternatives:* hardcode Cortex's client roster (rejected — that is a client list
committed to a **public** repo, a disclosure in itself); silently pass when no
map exists. *Rationale:* the check must resolve real terms from
`.engagement_map.json` and `CLIENT_PROFILE.md`, which are gitignored — so in CI
it has nothing to resolve. A silent pass there is precisely the v7 failure this
whole programme exists to close: a green that verified nothing. `SKIPPED_NO_MAP`
is reported on its own line, excluded from the pass total, and the eval row
asserts the *skip is reported* rather than asserting the check passed — the same
shape as `knowledge-harvester`'s pending `quarantine_mode_outputs_local` SKIP.
*Trade-off:* the check genuinely does not run in CI. Stated plainly rather than
hidden behind a number.

**D7 — The prefix regex is hand-copied into the hook with a parity check.**
*Alternatives:* import `_OPAQUE_ID_RE` from `orchestrate.py` or `pii.identity`.
*Rationale:* D13's self-containment rule — a guard that must fail closed cannot
carry an import whose failure makes it fail open. *Trade-off:* two copies of one
regex. Mitigated exactly as `drift_check.py` mitigates the deny-list duplication:
an eval check asserts they are identical, and it is mutation-proven.

**D8 — The knowledge-file cleanup and the check repair land together.**
*Alternatives:* clean the six files now, fix the check later.
*Rationale:* the files are only findable *because* the check was made real; ship
the cleanup alone and the check still cannot see the next one. Ship the check
alone and CI goes red on six pre-existing files. *Trade-off:* one larger change
instead of two small ones, deliberately.
