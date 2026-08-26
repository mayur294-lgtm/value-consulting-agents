---
version: 6
prd: prd-v6.md
status: draft
date: 2026-08-25
author: Mariam Titus George
previous: solution-design-v5.md
---

# Solution Design v6 — Presidio PII Gate

## Component Structure

```
scripts/
  anonymize_transcript.py       MODIFIED — public facade only. CLI surface and the four
                                public functions (anonymize_text, anonymize_transcript_file,
                                deanonymize_text, deanonymize_file) keep their exact
                                signatures. Implementation delegates to scripts/pii/.
                                Preserving this interface is what makes rollback a revert.
  pii/
    __init__.py                 NEW — lazy exports; importing must not load spaCy
    engine.py                   NEW — Presidio AnalyzerEngine + AnonymizerEngine assembly:
                                recognizer registry, engagement deny-list recognizer,
                                generic-banking allow-list, instance-counter operators,
                                legacy-mapping compatibility shim
    ingest.py                   NEW — document → anonymised text. PDF, DOCX, PPTX, XLSX,
                                CSV, and images (OCR → text sidecar + redacted copy).
                                Images embedded in DOCX/PPTX route through the same path.
    identity.py                 NEW — opaque engagement IDs, the local ID↔client map,
                                and neutral-workspace materialisation for pipeline runs
  artifact_boundary.py          MODIFIED — deanonymize_dir: recursive walk, .xlsx restore,
                                `unrestored` report field, client_ready:false  (salvaged #125)
  orchestrate.py                MODIFIED — step_discovery materialises the neutral
                                workspace; cwd and all path params point at it, never at a
                                client-named directory. Per-transcript mapping hygiene.
  init_engagement.sh            MODIFIED — creates opaque directories, writes the map entry
  find_engagement.sh            NEW — resolve client name → engagement path
  migrate_engagement_ids.sh     NEW — one-shot migration of the 7 existing directories
  setup_pii.sh                  NEW — the single command the preflight prints

.claude/hooks/
  anonymize-guard.py            MODIFIED — Presidio detection, document + image coverage,
                                fail-closed scoped to inputs/, plain-language messages
  pii-preflight.sh              NEW — SessionStart dependency check
  mcp-query-guard.py            NEW — PreToolUse on mcp__* ; §5 enforcement

evals/
  goldens/pii_roundtrip_fixture.md     NEW — synthetic multi-entity transcript
  goldens/pii_fixture_assets/          NEW — synthetic .pdf/.docx/.xlsx/.png
  rubrics/component/pii_anonymizer.py  NEW — 16 deterministic checks
  registry.yaml                        MODIFIED — pii-anonymizer row, threshold 1.00

requirements.txt                MODIFIED — presidio-analyzer, presidio-anonymizer,
                                presidio-structured, spaCy model, pdfminer.six,
                                python-docx, python-pptx, pytesseract, and
                                claude-agent-sdk (imported by orchestrate.py today,
                                declared nowhere)
.claude/settings.json           MODIFIED — register pii-preflight + mcp-query-guard
```

Plus prompt and documentation edits across the 20 rule surfaces catalogued in PRD §3.1.

---

## Data & Contract Model

```yaml
# 1. Mapping file — .pii_mapping.json  (chmod 600, gitignored)
#    Presidio's operator produces a nested structure; we persist it nested and
#    flatten on read so legacy flat mappings restore unchanged.
{
  "version": 2,
  "entities": {
    "PERSON":        {"Priya Nair": "<PERSON_1>"},
    "EMAIL_ADDRESS": {"p.nair@example.test": "<EMAIL_ADDRESS_1>"},
    "CLIENT":        {"Zenith Bank": "<CLIENT_1>", "Zenith": "<CLIENT_1>"}
  }
}
# version 1 (absent key) = legacy flat {placeholder: value} — still restores.
# Both forms are accepted by deanonymize_text forever; only v2 is written.

# 2. Placeholder convention — <ENTITY_N>, not [CLIENT]
#    [CLIENT] is simultaneously a PII placeholder and a filename/prose template
#    token ([CLIENT]_Business_Case_Questionnaire.xlsx; "[Client]'s path from X
#    to Y"). deanonymize_text does an unguarded string replace, so the old
#    convention rewrites templates. Angle brackets end the collision.

# 3. Engagement identity map — .engagement_map.json  (chmod 600, gitignored, repo root)
{
  "e7f3a2c1": {"client": "HDFC", "slug": "hdfc", "created": "2026-08-25"}
}
# The ONLY place the client's real name is bound to a path. Never leaves the machine.

# 4. Deny-list sources (ordered, deduplicated, longest-match-first)
#    inputs/engagement_intake.md · ENGAGEMENT_CONTEXT.md · CLIENT_PROFILE.md
#    · the client slug from .engagement_map.json
#    Single-word terms admitted only when length >= 4 and not in the generic
#    banking stoplist (bank, banking, credit, union, first, national, federal,
#    united, community, citizens, state, financial, savings, trust, group,
#    holdings, capital, mutual, valley, coast, pacific).

# 5. Ingest output contract — for input file X under inputs/
#    text formats  → .anon_X.md
#    images        → .anon_X.md (OCR text, anonymised) + .anon_X.png (redacted copy)
#    Agents read .anon_* only. Raw X is never read by any agent, in any mode.

# 6. Exit-gate report — artifact_boundary.deanonymize_dir
{"gate": "deanonymize_dir", "restored": 12, "unrestored": ["outputs/ROI_Model.xlsx"],
 "client_ready": false}
```

**Non-obvious contract choices.** The mapping is persisted nested because Presidio's operator is entity-typed and flattening on write would recreate the exact collision that made the old scheme lossy (one key per category, last value wins). Reading accepts both shapes forever — mappings on disk are data, and a consultant with a six-month-old engagement must still be able to produce a client-ready deliverable.

---

## Agent / Pipeline Steps

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `pii-preflight.sh` | hook (SessionStart) | environment | notice or silence | Tell the consultant, in plain language, that protection is off and how to fix it |
| `anonymize-guard.py` | hook (PreToolUse: Read, Bash) | tool call | allow / deny | Stop raw client material entering context |
| `mcp-query-guard.py` | hook (PreToolUse: `mcp__*`) | tool call | allow / deny | Stop client identifiers leaving for Infobank (§5) |
| `pii.engine` | module | text + deny-list | anonymised text + mapping | Detection and reversible pseudonymisation |
| `pii.ingest` | module | any input file | `.anon_` artifact(s) | Format coverage, including images and embedded images |
| `pii.identity` | module | engagement dir | opaque ID, workspace | Keep client identity out of paths and prompts |
| `artifact_boundary deanon` | pipeline step | outputs/ + mapping | restored outputs + report | The single point where real names re-enter artifacts |
| `setup_pii.sh` | script | — | working install | One command; absorbs the whole install sequence |
| `migrate_engagement_ids.sh` | script | existing dirs | opaque dirs + map | One-shot migration of the 7 live engagements |

No new agents. Every change is pipeline code, hooks, or prompt edits — consistent with the cortex stack.

---

## Integration Points

| Touched | Change | Downstream | Risk |
| --- | --- | --- | --- |
| `anonymize_transcript.py` | Implementation swapped, interface held | Every agent that reads `.anon_` files | **Medium** — behaviour changes, contract does not |
| `orchestrate.py` `step_discovery` | Workspace materialisation, params repointed | The whole Block-A chain | **High** — every agent's `cwd` and path params change |
| `artifact_boundary.py` | Recursive + xlsx restore | Final deliverables | **Medium** — more files touched than before |
| `.claude/settings.json` | Two new hooks | Every session and pipeline run | **High** — a hook fault affects all work; both fail safe by design |
| Engagement directory names | Opaque IDs | Consultant habits, `CLIENT_PROFILE.md`, docs, journals | **High** — the only consultant-visible breaking change |
| Seven MCP-using agent prompts | §5 rule added | Their outputs | **Low** — additive prompt text |
| `knowledge/platforms/backbase-mcp-integration.md` | §5 added to the snippet source | All *future* agents | **Low**, high leverage — this omission is the root cause |
| `requirements.txt` | Presidio, OCR, document libs, SDK pin | Every consultant machine | **Medium** — install friction is the main adoption risk |
| `evals/registry.yaml`, `evals.yml` | New component row + CI wiring | PR gate | **Low** |

---

## Technical Decisions

**D1 — Presidio behind the existing facade.** `anonymize_transcript.py` keeps its CLI and four public signatures; the engine moves to `scripts/pii/`. *Alternative:* rewrite the module outright. *Why:* rollback becomes a single revert, and no caller — pipeline, agent prompt, or eval — needs to change in lockstep. *Trade-off:* one layer of indirection.

**D2 — `<ENTITY_N>` replaces `[CLIENT]`/`[PERSON-N]`.** *Alternative:* keep the bracket convention. *Why:* `[CLIENT]` is also a filename and prose template token across six components, and `deanonymize_text` string-replaces blindly — the old convention actively corrupts templates. *Trade-off:* a migration note for engagements holding legacy mappings; legacy restore is kept forever.

**D3 — The deny-list is the primary client-identity detector, not Presidio.** Presidio has no reliable ORGANIZATION recognizer, and the client's name is the single most important entity. Sources broaden from `engagement_intake.md` alone to intake + context + profile + the map slug. *Why:* the observed failure was an empty intake list silently producing vacuous scrubbing. *Trade-off:* the system is only as good as the engagement's configured names — hence the mandatory non-blocking warning when the list is empty. **This must never be described internally as "Presidio detects PII for us."**

**D4 — Fail closed on `inputs/`, open everywhere else.** *Alternative:* fail closed globally. *Why:* a globally fail-closed guard wedged every session once already (PR #82); scoping it to raw client material keeps the guarantee where it matters without repeating that failure. *Trade-off:* a Presidio fault leaves non-`inputs/` paths unscanned — acceptable, since those were never in scope.

**D5 — Images always produce both artifacts; no classifier.** One OCR pass yields an anonymised text sidecar and a redacted image copy. *Alternative:* classify each image by text density and route down one branch. *Why:* both branches need OCR anyway, and Presidio's redactor already OCRs → analyses → fills; producing both is nearly free and removes a classifier that would sometimes route a UI screenshot to text-only and destroy its point. *Trade-off:* two artifacts per image. **Accepted limitation:** redaction blanks OCR-detected *text* only — a client **logo** is graphics and reaches the model. This must be stated in the guard message and the rollout instructions.

**D6 — Opaque engagement directories plus a neutral pipeline workspace.** *Alternative:* fix only the pipeline. *Why:* `compose_prompt` renders `engagement_dir` into prompt text on every call and `cwd` is the client-named path, so content scrubbing is defeated by the path envelope on every invocation — in interactive sessions as well as pipeline runs. Fixing only the pipeline would leave the larger surface open. *Trade-off:* the one consultant-visible breaking change; mitigated by `find_engagement.sh`, a migration script, and `engagements/` already being gitignored.

**D7 — Hooks are the enforcement layer, and the SDK gets pinned.** Verified against the Agent SDK docs: `setting_sources` defaults to loading user + project + local settings, `orchestrate.py` passes neither `setting_sources` nor `hooks`, and `permission_mode="bypassPermissions"` bypasses permission checks but **not** hooks. So one hook covers interactive and pipeline alike. *Trade-off:* the guarantee now depends on SDK behaviour, so `claude-agent-sdk` must be declared and version-pinned — it is currently imported by `orchestrate.py` and declared in no requirements file.

**D8 — Hard dependency, venv, one-command install.** Follows Presidio's own guidance (virtual environment, Python 3.10–3.13). *Why one command:* the preflight audience is non-technical; a four-step sequence is where they disengage. *Trade-off:* `setup_pii.sh` becomes a maintained artifact.

**D9 — Eval threshold 1.00 with temp-copy negatives.** A privacy control is pass/fail, not 0.80. Component altitude wires one `input:` per component, so negative cases (over-redaction, fail-closed fault injection, MCP block) use the `overcap_negative_gate_witness` temp-copy pattern. **Gate-bites verification is mandatory:** reverting the detector must make `no_raw_pii_in_anonymized_output` fail, recorded in the PR description. A gate that cannot fail certifies nothing.

**D10 — Start on `en_core_web_lg`, measure `en_core_web_sm` during build.** 382 MB is real install friction, and D3 means the deny-list — not the NER model — carries client identity. If `sm` holds the fixture at 1.00, ship `sm` and cut the download by roughly an order of magnitude. Decide on evidence, in build, not here.

**D11 — `presidio-structured` is 0.0.8; keep a fallback.** For XLSX/CSV, if the pre-1.0 package proves unstable, extract cell strings and run them through the plain text analyzer/anonymizer — the inverse of what `deanonymize_dir` already does for restore. Chosen in build on evidence.

**D12 — Interpreter resolution: a wrapper script settings.json points hooks at, not a per-hook helper or a dependency-free hook policy.** `.claude/settings.json` invokes every hook as `python3 <script>` — the system interpreter (3.9.6 here), which cannot import Presidio (needs 3.10–3.13, installed into `.venv` by `scripts/setup_pii.sh`; see D8). PR 3 rewrites `anonymize-guard.py` onto the Presidio engine, so from that point the hook process itself must run under `.venv`'s interpreter, not the system one. Three options were weighed:

- *(a) a per-hook Python helper each script calls at runtime* — every dependent hook would duplicate (or import) the same "find my venv" logic in Python, but the hook is already the wrong interpreter by the time its own code runs, so the resolution has to happen *before* the process starts, not inside it. Rejected.
- *(b) keep hooks dependency-free; run Presidio only in pipeline/CLI code* — contradicts D7 (hooks are the enforcement layer for both interactive and pipeline paths) and the PRD's own plan to rewrite `anonymize-guard.py` onto Presidio. Rejected — it would mean the guard keeps doing regex detection forever, which is the exact defect this PRD exists to fix.
- *(c) a wrapper script that settings.json invokes in place of `python3`, which execs `.venv/bin/python` when present and falls back to system `python3` otherwise* — resolution happens at process-launch time, in one place, before any hook-specific code runs. **Chosen.**

Implemented now as `.claude/hooks/_resolve_python.sh`: `exec "$VENV_PY" "$@"` if `.venv/bin/python` is executable, else `exec python3 "$@"`. It is a pure interpreter selector — it never inspects *why* the venv is missing and never decides whether to block; that stays each hook's own job (`pii-preflight.sh` warns and continues; `anonymize-guard.py` fails open outside `inputs/` and closed inside it; `mcp-query-guard.py` fails closed) per D4 and the UX spec's per-hook state tables. Because the fallback is unconditional and silent, the script is safe to route *any* hook through, dependency or not — running a stdlib-only hook under system `python3` (no `.venv` yet) or under `.venv/bin/python` (once created) behaves identically.

*Scope of this ticket:* the resolver is implemented and independently verified (both branches: venv present, venv absent) but **not yet wired into `settings.json`** — no hook in this ticket imports Presidio, so pointing `anonymize-guard.py`'s entry at it now would be an inert change that only adds review surface. PR 3 changes exactly one line — `anonymize-guard.py`'s `PreToolUse` command — from `python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/anonymize-guard.py` to `"$CLAUDE_PROJECT_DIR"/.claude/hooks/_resolve_python.sh "$CLAUDE_PROJECT_DIR"/.claude/hooks/anonymize-guard.py`, at the same time the hook itself starts importing `presidio_analyzer`. `mcp-query-guard.py` stays on plain `python3` — D3 keeps it on deny-list string matching, not Presidio NER, so it has no venv dependency to resolve.

*Trade-off:* one more file in `.claude/hooks/`, and a hook's effective interpreter is no longer visually obvious from `settings.json` alone — mitigated by the comment block in `_resolve_python.sh` itself pointing back here.

**D13 — `anonymize-guard.py` does NOT import the Presidio engine; it stays a purely path/timestamp-based gate. This supersedes D12's PR-3 plan to wire it onto `_resolve_python.sh`.** Ticket #164 originally called for replacing the guard's inline regexes with `scripts/pii/engine.py` so detection logic existed in exactly one place. Measured before implementing (fresh process, what a hook is on every Read/Bash call):

| | measured |
| --- | --- |
| engine import + first use | 0.67 – 1.12 s |
| pre-#164 stdlib guard | 0.04 s |

*Why not the engine:* this hook fires synchronously on every Read and every Bash call, in every session. Paying ~1s per tool call would make every session feel broken (17-28x the pre-#164 budget). It would also reintroduce the exact fail-open risk the guard exists to prevent: a module-level `import presidio_analyzer` that fails raises *before* `main()`'s try/except, and a PreToolUse hook that exits that way is treated as non-blocking by Claude Code — i.e. it fails OPEN, backwards for a guard whose job is failing closed. This is the same reasoning D3/D7 already applied to keep `mcp-query-guard.py` on deny-list string matching instead of Presidio NER.

*What replaces detection:* the guard was re-scoped from "detect PII in this file's content" to a narrower, purely structural question answerable from paths and timestamps alone — "has this raw file under `engagements/*/inputs/` already been run through the anonymizer, and is that scrubbed copy still current?" Per format:

- Plain text (`.md .txt .text .vtt .srt .json .log`, via `scripts/anonymize_transcript.py`) — sibling is `.anon_<name>` verbatim.
- Documents (`.pdf .docx .pptx .xlsx .csv`, via `scripts/pii/ingest.py`, #162) and images (`.png .jpg .jpeg .gif .bmp .tif .tiff .webp .heic`, via the same module, #163) — sibling is the `.anon_<name>.md` text sidecar (ingest.py's OUTPUT NAMING; the sidecar, not the redacted `.anon_<name>.png`, is what "carries the round-trip").
- No sibling, or a sibling OLDER than the raw file (mtime comparison) — denied, with the raw-vs-stale cases getting distinct messages.
- A format with no extractor — denied outright, never silently passed through.
- Any file already named `.anon_*` — allowed unconditionally, by name only; the guard never opens it to check which placeholder convention (today's `<ENTITY_N>` or a legacy `[CLIENT]`/`[PERSON-N]`/`[X-REDACTED]` engagement) produced its contents, because that distinction is irrelevant to whether it is raw client material.

The extension/naming lists are a hand-copied, self-contained duplicate of `scripts/pii/ingest.py`'s `DOCUMENT_SUFFIXES`/`IMAGE_SUFFIXES`/output-naming convention — not an import, even though `scripts/pii/ingest.py` is itself stdlib-only and fast to import (measured ~15-60ms under system Python 3.9.6). Same rationale as `mcp-query-guard.py` not importing `scripts/pii/denylist.py` (`scripts/pii/drift_check.py`'s header): a guard whose job is failing closed must stay self-contained so a future change anywhere under `scripts/pii/` can never silently change what it allows. The two copies must be kept in sync by hand.

*Consequence for D12:* since this hook never imports Presidio, it has no venv dependency to resolve and stays on plain `python3` in `settings.json`, exactly as `mcp-query-guard.py` does — D12's PR-3 plan to point `anonymize-guard.py` at `_resolve_python.sh` does not happen. `_resolve_python.sh` remains implemented and available for a future hook that does need the venv.

*Alternative considered:* the ticket's original ask (shared engine, one place for detection logic). *Why not:* the timing above, and the fail-open risk. *Trade-off accepted:* detection logic now genuinely exists in two forms — content-based (`scripts/pii/engine.py`, used by the anonymizer tools themselves) and structural (this guard) — rather than one. This is judged acceptable because the guard was never a reliable content detector even before this rewrite (5 regexes covered 3 of 77 real input files); the structural rule is *stricter*, not weaker: previously a raw file whose PII didn't match a regex passed through unchallenged, and now nothing under `inputs/` passes without a scrubbed sibling to point at, regardless of content.

**D14 — Opaque directories do NOT change where `denylist.py` gets its terms. The map stays out of the deny-list resolver in #166; the client slug reaches the engine through the `client_slug=` parameter that already exists, wired by #167.**

D6 makes engagement directories opaque, and `scripts/pii/denylist.py` mines the directory slug for client terms (`extract_terms_from_slug` — this is how `hdfc` becomes a deny-list term). So the obvious next move is to teach `denylist.py` to read `.engagement_map.json`. That move is wrong, and the reason is `scripts/pii/drift_check.py`: it asserts that `pii.denylist` and the hand-copied implementation inside `.claude/hooks/mcp-query-guard.py` produce **identical** deny-lists. Teach one to read the map and not the other, and they diverge by construction. The hook cannot simply import the shared module — its self-containment is load-bearing (a module-level import failure raises before `main()`'s try/except, and a PreToolUse hook that exits that way is treated as non-blocking, i.e. fail-open in a gate built to fail closed), so parity would require hand-copying a *third* copy of privacy-critical logic into the hook.

*Measured before deciding* (synthetic fixture, `CLIENT_PROFILE.md` holding `- **Name:** Zzzplaceholder Meridian Holdings`):

| directory shape | `resolve_deny_list` terms |
| --- | --- |
| today — `engagements/zzzplaceholderclient/` + profile | `Meridian`, `Zzzplaceholder`, `Zzzplaceholder Meridian Holdings`, `zzzplaceholderclient` |
| post-#168 — `engagements/e7f3a2c1/` + profile | `Meridian`, `Zzzplaceholder`, `Zzzplaceholder Meridian Holdings`, `e7f3a2c1` |
| post-#168 — `engagements/e7f3a2c1/`, **no** profile | `e7f3a2c1` only |
| post-#168 — `engagements/e7f3a2c1/`, no profile, `client_slug="hdfc"` passed | `hdfc` |

So going opaque costs the deny-list **one redundant term, not the client's identity**: three of four terms are unchanged, because `CLIENT_PROFILE.md` — which `init_engagement.sh` creates for every client and which stays inside the engagement directory (#166 changes nothing about the directory's internal structure) — is a stronger source than the slug ever was. The slug was a *fallback* for an unfilled profile, and it degrades to a meaningless token rather than disappearing.

*Chosen:* keep #166 to the identity primitives. `denylist.py` and `drift_check.py` are **untouched**, so the drift check still compares two whole-module outputs byte-for-byte with no documented-exception carve-out. The seam for the map already exists and predates this ticket — `resolve_engagement_deny_list(engagement_dir, client_slug=None)`, whose docstring says in as many words "resolved out of `.engagement_map.json` once opaque engagement IDs land". #166 supplies the other half (`identity.client_for_id(...)["slug"]`); #167, which is already repointing every path parameter in `step_discovery`, passes it. Verified above: the seam restores the client term exactly.

*Alternative considered:* wire the map into `denylist.py` now and relax `drift_check.py` to compare only the shared extraction, documenting the map-derived difference as intentional. *Why not:* a drift check that fails, or that partially exempts itself, for a known reason is a drift check nobody reads again — and this repo has already shipped two gates that scored 1.000 while certifying nothing. The alternative also requires editing `.claude/hooks/*`, which #166 is explicitly scoped out of.

*Trade-off accepted:* between #168 (directories go opaque) and #167 (the slug is threaded through), an engagement whose `CLIENT_PROFILE.md` is still an unfilled template has a deny-list of one meaningless token. That combination already produces a near-empty deny-list today, and it is exactly the case D3's mandatory non-blocking "no names configured" warning exists to surface. #167 and #168 must land together or #167 first; a note to that effect belongs in #168's ticket.

**D15 — the workspace lives at `<repo>/.cortex-workspaces/`, not in the system temp directory; `--resume-from` REATTACHES to it rather than re-materialising; and a run's stdout is redacted as a backstop. (#167)**

Three decisions taken while wiring `identity.py` into `orchestrate.py`, all forced by the same observation: `materialise_workspace` guarantees the segments it *creates*, and everything else about how the pipeline uses it is the caller's problem.

*(a) Placement inside the repo.* `identity.py` defaults the workspace to `mkdtemp()`, i.e. `/tmp`. Every pipeline agent prompt also names **repo-relative** knowledge files that carry no `{param}` — `knowledge/standards/capability_taxonomy_{domain}.md`, `knowledge/domains/{domain}/value_drivers.md`, and so on — and those can only resolve relative to a cwd somewhere inside the checkout. Today's cwd (`engagements/<client>/<engagement>`) is inside it; `/tmp/cortex-ws-XXXX` is not. Moving agents to `/tmp` would have silently cut all ten of them off from their own knowledge packs while every path assertion in the ticket still passed. `.cortex-workspaces/` sits at the same depth below the repo root as an engagement directory and contributes no client-derived segment; it is gitignored and removed at the end of a successful run. It deliberately does **not** live under `engagements/`, because `denylist.py` treats every child of `engagements/` as a client directory and mines its name — a workspace there would pollute the deny-list of every session on the machine.

*(b) `--resume-from` reattaches.* The ticket offered "re-materialise deterministically **or** persist it". Re-materialising cannot be made honest: the directory *name* could be, but the workspace's `outputs/` cannot, because everything the interrupted run produced lives there and rebuilding it means copying the real engagement's `outputs/` back in — which, after any previously *completed* run, has already been through `deanonymize_dir` and therefore holds the client's real name. Seeding from it would re-inject the exact identifiers this ticket removes, on the one code path nobody exercises until something has already gone wrong. So the workspace path is persisted in `<engagement>/.pipeline_workspace` (chmod 600, inside the already-gitignored `engagements/`) and resume reattaches to it; the workspace only ever contains placeholder-form artifacts, because that is the only form ever written into it. If it is gone, the pipeline raises and names the fix rather than falling back to a client-named path. To make an interrupted run recoverable rather than stranded, `copy_back()` — which is idempotent and merge-only — is called after every step, not only at the end.

*(c) stdout is a leak surface.* `orchestrate.py` is normally launched with Bash **from inside a Claude Code session**, so everything it prints is read back into a model's context; the consultant's scrollback and any journal capture see it too. The header line `Engagement: {engagement_dir}` has always printed the client-named path. Repointing prompts and `cwd` achieves nothing if the next `log()` call undoes it, so `log`/`log_step`/`log_print` now scrub their output against the engagement's own deny-list. This is a **backstop, not the control** — the control is that no client-named path is constructed into a prompt or a cwd at all, enforced by `_assert_neutral_invocation` at `run_agent`'s choke point, which *raises* rather than warns.

*Two things #167 found that the ticket did not anticipate, both closed:*

- **`.anon_mapping_*.json` files match `materialise_workspace`'s copy filter.** It copies every file under `inputs/` whose name starts with `.anon_`, and a per-transcript mapping file starts with `.anon_`. A mapping file is not a scrubbed artifact — it is the de-anonymisation *key*. On the normal path this never bites, because the mappings are deleted the moment `.pii_mapping.json` exists; but a run killed between those two writes, or a hand-run of the CLI, leaves residue that the *next* run would copy straight into the directory an agent works in. `_sweep_stray_mappings` now runs immediately before materialisation: strays are deleted when the combined mapping supersedes them, and **moved** to `.pii_orphan_mappings/` (never deleted, never left in place) when it does not — deleting them would make an earlier run's deliverable permanently unrestorable. A post-materialisation assertion destroys the workspace and refuses to run if one gets in anyway.
- **`engagement_intake.md` is optional in all eight mode contracts that name it, so the workspace not carrying it degrades rather than fails.** Its content still reaches the workspace, scrubbed through the same shared mapping, as an `.anon_` artifact. But no prompt points at that artifact, and #167 is forbidden from editing prompts — so in practice the eight agents lose their intake context. `_preflight_required_inputs` does not fire (the entry is under `optional:`) and every prompt still composes, which is what "still works" means here; recovering the context needs a prompt edit and belongs in the backlog.

*Consultant-visible side effect, accepted:* `require-checkpoint.py` gates writes on paths containing both `engagements` and `outputs`, so pipeline agents writing into `<workspace>/outputs/` are no longer covered by it. The gate was already satisfied trivially in the pipeline (the orchestrator writes `CHECKPOINT_discovery.md` before any deliverable), and `present_checkpoint` remains the real enforcement, but the hook-level backstop is gone for pipeline runs. Interactive sessions are unaffected.

---

## Build Sequence

Four PRs, each independently reviewable and independently valuable.

| PR | Contents | Rationale |
| --- | --- | --- |
| **1** | `mcp-query-guard.py`, `security_protocol.md` §5 rewrite, seven agent prompts, `backbase-mcp-integration.md` snippet source | **Ships first and standalone.** Unblocks authorising Infobank safely — today the only thing preventing unguarded client-named queries to an external server is that the MCP is unauthenticated, which is accidental, not designed |
| **2** | `pii/engine.py`, facade, `requirements.txt`, `setup_pii.sh`, `pii-preflight.sh`, eval gate | The detector swap, landing with its own gate. Nothing downstream proceeds until this is green |
| **3** | `pii/ingest.py` — documents, images, embedded images; guard rewrite | Coverage. Depends on PR 2's engine |
| **4** | `pii/identity.py`, workspace, `init_engagement.sh`, `find_engagement.sh`, migration | Highest consultant impact, so it lands last and can slip without blocking anything else |

**Sequencing note.** PR 1 inverts the usual order deliberately: it is the smallest change and closes the surface that is currently held open by accident rather than by design.

---

## Open Items for Build

1. **`en_core_web_lg` vs `sm`** — decide on measured fixture performance (D10).
2. **`presidio-structured` viability** — pre-1.0; fall back to the text path if unstable (D11).
3. **Migration rehearsal** — `migrate_engagement_ids.sh` must be dry-run against all 7 live directories before it touches any of them.
4. **Rollout content** — install instructions for the team, and the logo limitation stated plainly. Flagged by Mariam as a deliverable she will author; the guard message and README must agree with it.
