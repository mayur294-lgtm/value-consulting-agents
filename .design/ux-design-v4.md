---
version: 4
prd: prd-v4.md
status: draft
date: 2026-08-18
author: Mariam Titus George
previous: ux-design-v3.md
---

# UX Design v4 — Synthetic-Engagement Quarantine Enforcement

There is no screen UI in this feature. The "user experience" is what a consultant sees in four situations: running a pipeline against a test engagement, harvesting manually, querying knowledge retrieval, and hitting the CI backstop. All messages below are the actual strings (or their fixed skeletons), not placeholders.

## User Flows

### Flow 1 — Pipeline run against a test engagement (automatic path)

```
CLAUDECODE= python3 scripts/orchestrate.py tests/engagements/<name>/<engagement>
        │
        ▼
[pipeline runs all steps normally — discovery, Block A, roadmap, assembly…]
        │
        ▼
[Step 7: KNOWLEDGE HARVEST]
        │
        ▼
[gate: synthetic_policy(engagement_dir) — checks .synthetic marker, then tests/ path]
        │
        ├──["real"]──────────▶ [current behavior, unchanged: pipeline-mode harvest
        │                       into shared knowledge/, optional auto-push PR]
        │
        ├──["quarantine"]────▶ log: "🧪 Synthetic engagement (harvest_policy: quarantine)
        │                       — harvest redirected to outputs/knowledge_harvest/;
        │                       shared knowledge untouched"
        │                           │
        │                           ▼
        │                      [harvester runs in quarantine mode; every file lands
        │                       under {engagement_dir}/outputs/knowledge_harvest/;
        │                       .harvest_summary.txt still written to engagement dir]
        │                           │
        │                           ▼
        │                      [auto-push / harvest-PR block SKIPPED unconditionally]
        │
        └──["never"]─────────▶ log: "🧪 Synthetic engagement (harvest_policy: never)
                                — harvest skipped entirely (real source material,
                                must not be extracted)"
                                    │
                                    ▼
                               [no agent run, no files written, step ends]
```

Fail-safe rule (no user action required): an engagement under `tests/` with **no** `.synthetic` marker, or with a marker that can't be parsed, is treated as `quarantine` — never as real. A `.synthetic` marker anywhere (even under `engagements/`) is honored: marker wins over location.

### Flow 2 — Manual harvest pointed at a test engagement

Covers `knowledge-harvester` backfill mode and `/extract-learnings` — the two paths with no Python driver.

```
[consultant asks: "backfill harvest from tests/engagements/X/…/outputs"
 or runs /extract-learnings on a test engagement]
        │
        ▼
[prompt-side self-check (mandatory first step, before ANY write):
 look for .synthetic in the engagement dir & parents; check for tests/ path segment]
        │
        ├──[no marker, not tests/]──▶ [normal extraction into shared knowledge/]
        │
        ├──[harvest_policy: quarantine or tests/ default]
        │        │
        │        ▼
        │   [same extraction, all writes under <engagement>/outputs/knowledge_harvest/;
        │    reply states: "This is a synthetic/test engagement — harvest quarantined
        │    to outputs/knowledge_harvest/. Nothing was written to shared knowledge."]
        │
        └──[harvest_policy: never]
                 │
                 ▼
            [polite refusal: "This engagement is marked harvest_policy: never in its
             .synthetic file (it contains real source material used as test input).
             Nothing was extracted. See tests/engagements/README.md."]
```

### Flow 3 — Retrieval that encounters synthetic data

```
[consultant runs /domain-benchmarks retail (or benchmark-librarian / an ROI agent
 reads knowledge/learnings/roi_models/*)]
        │
        ▼
[surface reads its normal sources; any entry tagged [Synthetic-Test] — or any
 value that would be sourced from a tests/ path — is EXCLUDED from results]
        │
        ▼
[results end with a one-line note whenever anything was excluded:
 "Note: N synthetic-test entr(y/ies) excluded — fabricated pipeline-test data,
  never citable in client work (see knowledge/standards/benchmark_evolution.md)."]
        │
        └──[nothing synthetic encountered] ──▶ [no note — output identical to today]
```

The note is deliberate (owner decision): consultants should see the filter working, and a sudden jump in N is itself a contamination alarm.

### Flow 4 — CI backstop on a contaminated PR

```
[PR touches knowledge/** with synthetic contamination]
        │
        ▼
[test-agents.yml → scripts/test_agent.py structural checks]
        │
        ├──[[Synthetic-Test] found in knowledge/domains/**]──▶ FAIL:
        │     "No [Synthetic-Test] data in domain knowledge — fabricated test-engagement
        │      values must stay quarantined. See tests/engagements/README.md."
        │
        ├──["Harborlight" found anywhere in knowledge/**]──▶ FAIL (same message family)
        │
        └──[clean]──▶ PASS (comment on PR as today)
```

## Screen & Component States

No screens. Component states that matter:

| Component | State | Trigger | What the consultant sees |
| --- | --- | --- | --- |
| `step_harvest` gate | real | no marker, not under tests/ | Nothing new — identical to today |
| `step_harvest` gate | quarantine | `.synthetic` (quarantine) or bare tests/ path | One 🧪 log line naming the redirect target |
| `step_harvest` gate | never | `.synthetic` with `harvest_policy: never` | One 🧪 log line saying harvest skipped and why |
| `step_harvest` gate | marker unparseable | malformed `.synthetic` | Treated as quarantine + log line notes "marker unreadable — failing safe to quarantine" |
| Retrieval surfaces | clean | no synthetic entries in sources | Output identical to today (no note) |
| Retrieval surfaces | filtered | ≥1 `[Synthetic-Test]` entry excluded | Exclusion note with count |
| PreToolUse hook | pass | write to knowledge/** without contamination markers | Nothing (hook is silent on allow) |
| PreToolUse hook | deny | write to `knowledge/domains/**` containing `[Synthetic-Test]`, or `knowledge/**` containing "Harborlight" | Deny message naming the file, the matched marker, and pointing to `tests/engagements/README.md` |

## Error States

| Error | Cause | User-facing message | Recovery |
| --- | --- | --- | --- |
| Harvest refused | `harvest_policy: never` engagement | "This engagement is marked harvest_policy: never … Nothing was extracted." | Intended behavior; if the marker is wrong, edit `.synthetic` |
| Marker unreadable | Malformed `.synthetic` file | "🧪 .synthetic marker unreadable — failing safe to quarantine" | Fix the marker file (format in tests/engagements/README.md); rerun if `real` was intended (requires removing the marker AND the dir not being under tests/) |
| Hook deny on legitimate work | Consultant editing the four banner-marked `knowledge/learnings/roi_models/` files | Does not occur — the `[Synthetic-Test]` content check is scoped to `knowledge/domains/**` only; "Harborlight" never legitimately appears in knowledge/ | If a future false positive appears: hook is fail-open by design and the deny message names the exact matched pattern for diagnosis |
| CI check fails a PR | `[Synthetic-Test]` in domains/ or "Harborlight" in knowledge/ | Named structural check failure in the PR comment with README pointer | Remove/quarantine the flagged content and push |
| Quarantine dir collision | `outputs/knowledge_harvest/` already has files from an earlier test run | None — harvester overwrites/updates its own quarantine files exactly as it would shared knowledge | n/a (quarantine is per-engagement, self-contained) |
