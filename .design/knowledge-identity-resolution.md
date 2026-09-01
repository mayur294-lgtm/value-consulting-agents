---
version: 1
prd: none — design note precedes its PRD
status: draft
date: 2026-08-30
author: Mariam Tahir
previous: solution-design-v6.md (D6, D14 — opaque engagement identity)
---

# Design Note — Knowledge Identity Resolution

**Deliberately outside the numbered `solution-design-vN` sequence.** Those pair
1:1 with a PRD. This note answers an architectural question raised during the
2026-08-30 repo scrub, ahead of any PRD, and is written so a PRD can be drawn
from it. Renumber it into the sequence if and when that happens.

## The Question

> If `knowledge/**` is de-identified before it reaches the repo, and a colleague
> pulls it onto their machine, how does their system know to turn
> `[Client-retail-NAM-2025]` back into the real client? Because when they have a
> question they will ask about the client by name, not by the masked ID.

Restated for the destination we are actually heading to: **the repo moves into
Backbase's enterprise GitHub — protected, SSO-gated, internal-only. What can we
do then?**

## Current State, Measured

There are TWO anonymisation schemes in this repo. They look similar and behave
oppositely, and conflating them is the source of the confusion:

| | Reversible pseudonymisation | Descriptive relabelling |
|---|---|---|
| Where | `scripts/pii/engine.py` | `knowledge-harvester.md` Core Rule 2 |
| Shape | `<PERSON_1>`, `<CLIENT_1>` | `[Client-{domain}-{region}-{year}]` |
| Mapping stored | `.pii_mapping.json` | **none** |
| Round-trips | yes — `artifact_boundary.deanonymize_dir` restores real names before a deliverable goes to the client | **no** |
| Applies to | engagement `inputs/` and `outputs/` | `knowledge/**` |

`extract_telemetry._client_label()` is explicit about the second: it builds the
label from `domain` / `region` / `year` and **discards the client name**. Nothing
writes it down. The transformation is one-way, lossy and **many-to-one**.

Neither map travels. `.pii_mapping.json` and `.engagement_map.json` are both
gitignored and chmod 600 by design, and live on the machine that created them.

So the direct answer to the question is: **it never comes back, and today nothing
could make it come back.**

## Why That Is Intended, and Survives The Move

The reason `knowledge/**` is de-identified is *not primarily* that the repo is
public. It is that **shared knowledge is retrieved on every engagement.** If
Client A's name sits in `retail/benchmarks.md`, then a consultant working on
Client B pulls A's name into B's model context, and potentially into B's
deliverable.

That is not hypothetical here. The synthetic-quarantine incident was exactly this
path: fabricated benchmark data flowed out of shared knowledge and into a real
client's business-case workbook, caught in review.

**This argument is independent of who can read the repo.** It holds identically
on enterprise GitHub. Any design that puts real client names back into
`knowledge/**` has to answer it, and "the repo is internal now" does not.

Two further things the move does not change:

- **Contractual need-to-know.** MSAs typically restrict client material to the
  engagement team, not to everyone employed by the vendor. Internal is not the
  same as licensed.
- **MCP queries leave the network.** `mcp-query-guard.py` and
  `security_protocol.md` §5 are unaffected by repo visibility.

What the move *does* change, and genuinely improves: the audience becomes
authenticated staff, public forks stop being a problem, and `refs/pull/N/head`
exposure becomes internal. The retraction question filed in `.prd/backlog.md`
largely dissolves. **The prevention question — this note — does not.**

## The Decisive Constraint

**GitHub has no path-level read ACL. CODEOWNERS gates review, not read.**

There is no configuration in which `knowledge/client_map.json` lives in this
repository and is readable by five people and not by everyone else who can clone
it. This single fact eliminates the most obvious design and forces the options
below to be about *where the file lives*, not *how it is permissioned*.

## Options Considered

| | How it stays current | Why not / why |
|---|---|---|
| **A. Sibling repo with its own access list** — `cortex-client-index`, VC team only; resolution tooling pulls it | It *is* a repo — `git pull`, same mechanics as today | **Chosen.** See D2 |
| **B. Encrypted file in this repo** — SOPS + age, or git-crypt | Perfectly — same repo, same commit | Trades a permissions problem for a key-custody one. A leaked key is retroactive and cannot be un-leaked; membership removal does not revoke a key someone already holds |
| **C. Real names in `knowledge/`, mask at read time** | n/a | Solves the UX completely and is the one to avoid. See D3 |
| **D. Accept the status quo** — to learn which client, go to the engagement via `find_engagement.sh` | n/a | Leaves the collision defect (D1) unfixed, which is a correctness problem, not a convenience one |

## Technical Decisions

**D1 — Collision-proof the label before anything else.** `[Client-{domain}-{region}-{year}]`
is many-to-one: two NAM retail engagements in the same year receive the
*identical* label and their benchmarks silently merge into one apparent peer. A
consultant comparing against `[Client-retail-NAM-2025]` — 17 occurrences in
`knowledge/` today — has no way to tell whether they are reading one bank or two.
Add a short stable discriminator: `[Client-retail-NAM-2025-a3f2]`, derived from
the engagement ID, not from the client name. *Why first:* this is a data-integrity
defect that corrupts benchmarks. It is worth fixing whether or not any resolution
layer is ever built, and every other item here depends on the label being a real
identifier. *Trade-off:* a migration pass over existing labels; the 2026-08-30
scrub already touched every one of them, so the blast radius is known.

> **BUILT 2026-08-30.** `pii.identity.client_label()`, `label_discriminator()`
> and `engagement_id_for_path()` are the canonical implementation;
> `extract_telemetry.py` calls them and `knowledge-harvester.md` Core Rule 2
> documents the agent-facing form. Four checks added to the
> `engagement-identity` row, mutation-proven 10/10. The label is now
> `[Client-{domain}-{REGION}-{year}-{disc}]`, `{disc}` being the first 4
> characters of the opaque engagement ID — refused, not coerced, when the ID
> is anything client-controlled.

**D2 — The index lives in a sibling repo, not in this one and not encrypted here.**
A small repository — `label → {client, engagement_ids, first_seen}` — with the VC
team as its access list. *Alternative:* encrypt it in place (Option B). *Why:* the
repository is GitHub's actual unit of access control, so using it means no key
distribution, no rotation ceremony, and revocation that is immediate and
retroactive — remove someone from the team and they lose access to history, which
a held key does not give you. It also keeps this repo free of a second secrets
mechanism. *Trade-off:* two repos to clone, and the tooling must degrade
gracefully when the index is absent (D4).

**D3 — `knowledge/**` keeps descriptive labels. Do not invert to store-real,
mask-on-read.** *Alternative:* Option C — real names in knowledge, redacted by the
retrieval layer when composing a prompt for a different client. *Why not:* it makes
the masking layer load-bearing on every read path into `knowledge/`, and there are
many — agents reading files directly, the `/domain-*` retrievers, `grep`, MCP,
manual consultant reads. Gating all of them is the hard version of this problem,
and this system has already been on the wrong side of it once. PRD v6's own
finding: *"We built the strongest gate on the least-used path."* Option C is that
mistake repeated with a worse failure mode, because the leak is silent and lands
in a client deliverable. *Trade-off:* the UX gap stays real, and D4 is what closes
it instead.

**D4 — Resolution is a LOOKUP, mirroring `find_engagement.sh`.** The problem is a
lookup problem, not a storage problem, and this system already solved this exact
shape once: nobody types an opaque engagement ID because a script resolves the
client name for them. Same pattern, two commands:

```bash
./scripts/find_knowledge.sh "XYZ Bank"        # name -> label -> what we know
./scripts/whois.sh "[Client-retail-NAM-2025]" # label -> name, for index holders
```

*Why:* the consultant types the client's name, which is what they were always going
to do. They never learn a label exists. *Trade-off:* none material — but see D5 for
the behaviour that makes it safe.

**D5 — Absent index degrades to reduced output, never to an error.** A consultant
without index access running `find_knowledge.sh "XYZ Bank"` gets the knowledge
that matches, with no client name attached, and a one-line note saying resolution
was unavailable. *Alternative:* fail with a permissions error. *Why:* the knowledge
itself is not restricted — only the name binding is. Erroring would deny people
material they are entitled to in order to protect a label. This is the same
posture as `SKIPPED_NO_MAP` in ticket #223: say plainly that something was not
resolved rather than failing or, worse, pretending.

**D6 — The harvester writes the index entry, as a side effect of the run that
mints the label.** *Alternative:* a separate reconciliation job. *Why:* the label
and its binding are created at the same instant and by the same agent; splitting
them guarantees drift. *Trade-off:* the harvester gains a write to a second repo,
which must be non-fatal when that repo is not present — a consultant without index
access must still be able to harvest.

## Component Sketch

```
cortex-client-index/            NEW REPO — VC team access list
  client_index.json             label -> {client, engagement_ids, first_seen}
  README.md                     what this is, who may read it, why it is separate

scripts/
  find_knowledge.sh             NEW — client name -> label -> knowledge hits.
                                Degrades to name-less output without the index (D5).
  whois.sh                      NEW — label -> client, for index holders
  knowledge_index.py            NEW — read/write the index; stdlib-only and 3.9-clean,
                                matching find_engagement.sh's constraint so resolution
                                never requires the Presidio venv

.claude/agents/
  knowledge-harvester.md        MODIFIED — Core Rule 2 emits the discriminated label
                                (D1) and writes the index entry (D6)

scripts/extract_telemetry.py    MODIFIED — _client_label() gains the discriminator so
                                telemetry and knowledge labels stay identical
```

## Built So Far

**D1 — done 2026-08-30.** Building it surfaced a second defect the note had not
predicted: `extract_telemetry._client_label()` lower-cased BOTH domain and
region, while every label committed in `knowledge/**` uses an UPPER-case region
(`[Client-wealth-APAC-2025]`). So telemetry and knowledge had been emitting
different strings for the same engagement, and the docstring's claim that it used
"the same descriptive label the knowledge harvester uses" was not quite true.
Both now go through one function, so they cannot drift again.

The convention was also restated in seven places (CLAUDE.md ×2,
knowledge-harvester, sync-telemetry, scan-engagement, extract-learnings,
benchmark_evolution.md). All updated together — a convention documented in seven
places and changed in one is how the original drift happened.

## Open Items

1. **Who is on the index's access list?** The only genuinely open question here,
   and it is a people decision rather than a code one. Options range from the
   three Architect-tier collaborators to the whole VC practice.
2. **Do existing labels get migrated or grandfathered?** D1 changes the label
   shape. Migration is mechanical but touches every file the 2026-08-30 scrub
   already rewrote.
3. **Does the index also record the engagement→label binding for engagements a
   consultant did not run?** If yes it becomes the client roster in one file,
   which raises the stakes on item 1 considerably.

## An Honest Caveat On The Whole Scheme

If the index is readable by the entire VC practice, and the entire practice can
read this repo, then nothing here hides a client from a colleague — and it should
not be sold internally as if it does.

What the design actually buys is narrower and worth stating precisely: client
names do not enter model context ambiently on unrelated engagements, and they do
not travel inside the artifact that gets cloned, exported, or forked. Resolution
becomes a deliberate, auditable lookup instead of an ambient property of every
file an agent happens to read.

That is the property worth protecting. Secrecy from colleagues is not the goal,
and claiming it would be the same category of error as a gate named after
something it cannot see.
