---
version: 8
prd: prd-v8.md
status: draft
date: 2026-08-27
author: Mariam
previous: ux-design-v7.md
---

# UX Design v8 — Direct-skill path naming policy

The "user" here is the consultant at a Claude Code session. Every surface in
this spec is terminal text: a hook denial, a fixer's dry-run plan, a structural
check's verdict. There is no screen.

## User Flows

### Flow 1 — Writing an output in an engagement that has never been fixed

```
Consultant runs /frontline-long-form, /proposal-builder, or asks Claude
to write a file under engagements/<id>/
        │
        ▼
PreToolUse(Write|Edit) → output-naming-guard.py
        │
        ├──[path is exempt: journal, profile, inputs/, dotfile]──▶ ALLOW (silent)
        │
        ├──[engagement has .naming_policy_applied breadcrumb]
        │        │
        │        ├──[basename matches ^[0-9a-f]{8}_ ]──▶ ALLOW (silent)
        │        │
        │        └──[no prefix]──▶ DENY "E2 — output name needs the engagement prefix"
        │                                │
        │                                ▼
        │                     Consultant renames in the write itself
        │                     (the message gives the exact filename)
        │
        └──[no breadcrumb]──▶ DENY "E1 — this engagement hasn't had the naming policy applied"
                                     │
                                     ▼
                          Consultant runs the fixer (Flow 2)
                                     │
                                     ▼
                          Breadcrumb written → retry the write → ALLOW
```

The denial is the entire interaction. The guard never renames, never edits,
never writes anything except its own refusal.

### Flow 2 — Applying the policy to one engagement (the fixer)

```
./scripts/apply_output_naming.sh <engagement>          # DRY RUN — default
        │
        ▼
Resolve deny-list terms for that engagement (scripts/pii/denylist.py)
        │
        ├──[deny-list is EMPTY]──▶ REFUSE, exit non-zero
        │                          "cannot tell which names to remove"
        │
        ▼
Scan basenames under the engagement; plan each rename
        │
        ▼
Scan .html/.md/.json in the same engagement for references to
each old name; plan each in-document rewrite
        │
        ▼
PRINT THE PLAN — renames, in-document edits, and unresolved references
        │
        ├──[no --apply]──▶ exit 0, nothing changed
        │
        └──[--apply]──▶ re-print plan ──▶ prompt "type 'rename' to proceed"
                              │
                              ├──[anything else]──▶ "Cancelled. Nothing changed."
                              │
                              └──['rename']──▶ rename pairs atomically,
                                               rewrite references,
                                               write .naming_policy_applied,
                                               print unresolved-reference report
```

### Flow 3 — The structural knowledge check finds a real client name

```
python scripts/test_agent.py   (or the same check in CI)
        │
        ▼
Resolve real client terms from .engagement_map.json + CLIENT_PROFILE.md
        │
        ├──[no map present — CI]──▶ REPORT "SKIPPED (no engagement map)"
        │                            loudly, as its own line, never as a pass
        │
        └──[map present]──▶ scan knowledge/** for those terms
                                 │
                                 ├──[none found]──▶ PASS
                                 │
                                 └──[found]──▶ FAIL, naming file, line and term
```

## Screen & Component States

### `output-naming-guard.py` (PreToolUse: Write, Edit)

| State | Trigger | What the consultant sees |
| --- | --- | --- |
| Silent allow | Path outside `engagements/`, or exempt, or correctly prefixed | Nothing — the write proceeds |
| Block: policy not applied | Engagement has no `.naming_policy_applied` breadcrumb | E1 message with the exact fixer command for this engagement |
| Block: missing prefix | Breadcrumb present, basename lacks `^[0-9a-f]{8}_` | E2 message with the suggested corrected filename |
| Block: unresolvable engagement | Path is under `engagements/` but no engagement root can be determined | E3 message; fails closed |
| Silent allow (pipeline) | `copy_back()` publishing from the neutral workspace | Nothing — this is Python file I/O, not a tool call. **No hook fires.** Stated so nobody reads pipeline outputs as "passed the guard" |

### `apply_output_naming.sh` (consultant-invoked CLI)

| State | Trigger | What the consultant sees |
| --- | --- | --- |
| Dry run (default) | No `--apply` | Full plan: renames, in-document rewrites, unresolved references. Ends "Nothing was changed." |
| Refused: empty deny-list | No resolvable client terms for the engagement | Refusal naming which sources were checked and found empty |
| Refused: no engagement | Path is not an engagement directory | Refusal with `find_engagement.sh` as the way to locate one |
| Confirming | `--apply` given | Plan re-printed, then `Type 'rename' to proceed:` |
| Cancelled | Anything other than `rename` typed | "Cancelled. Nothing was changed." |
| Applied | Confirmed | Per-file rename lines, rewrite count, breadcrumb written, unresolved-reference report |
| Applied with unresolved refs | Confirmed, some references outside the engagement | Applied lines **plus** a clearly separated "references I could not rewrite" block |
| Already applied | Breadcrumb exists | "Already applied on {date}. Re-run with --recheck to rescan." |

### The structural client-name check

| State | Trigger | What the consultant sees |
| --- | --- | --- |
| Pass | Map resolvable, no terms found in `knowledge/**` | `[+] No client names (anonymization check)` |
| Fail | A real client term found | `[-]` with file, line, and the matched term |
| **Skipped, loudly** | No engagement map (CI, fresh clone) | `[~] SKIPPED — no engagement map; this check verified NOTHING in this run` — counted as neither pass nor fail, printed in the summary, never folded into the pass total |

## Error States

| Error | Cause | User-facing message | Recovery |
| --- | --- | --- | --- |
| **E1 — policy not applied** | Writing into an engagement with no breadcrumb | "🛑 This engagement hasn't had the output-naming policy applied yet.<br><br>Files here may still carry the client's name, which reaches the model whenever a skill opens one by path.<br><br>Apply it (dry run first — it changes nothing):<br>`./scripts/apply_output_naming.sh engagements/{id}`" | Run the fixer, then retry the write |
| **E2 — missing prefix** | Basename lacks `^[0-9a-f]{8}_` | "🛑 Engagement outputs need the engagement prefix.<br><br>You wrote: `{basename}`<br>Expected:  `{id}_{basename}`<br><br>The prefix is the opaque engagement ID. `./scripts/find_engagement.sh` resolves it back to the client." | Rewrite with the suggested name |
| **E3 — engagement root unresolvable** | Path under `engagements/` but no engagement root found | "🛑 Cannot determine which engagement this path belongs to, so the naming policy cannot be checked. Refusing the write.<br><br>Path: `{path}`" | Write inside a proper engagement directory |
| **E4 — fixer: empty deny-list** | No client terms resolvable for that engagement | "⛔ REFUSED: no client names could be resolved for this engagement, so there is nothing to rename against.<br>Checked: inputs/engagement_intake.md · ENGAGEMENT_CONTEXT.md · CLIENT_PROFILE.md · the map slug.<br>Renaming blind would produce opaque names that hide nothing." | Fill `CLIENT_PROFILE.md`, or pass `--name` |
| **E5 — fixer: rename collision** | Two files would resolve to the same new name | "⛔ REFUSED: `{a}` and `{b}` both become `{new}`. Nothing was renamed." | Disambiguate by hand, re-run |
| **E6 — fixer: interrupted mid-apply** | Process killed between renames | "⚠️ INTERRUPTED — {n} renamed, {m} pending, references NOT rewritten. No breadcrumb was written; re-run to finish." | Re-run; it is resumable and idempotent |
| **E7 — check skipped in CI** | No engagement map present | "[~] SKIPPED — no engagement map; this check verified NOTHING in this run" | None needed — but it must never read as a pass |
