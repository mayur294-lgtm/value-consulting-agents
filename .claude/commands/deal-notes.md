# Deal Notes — meeting transcript → deal-state record + live deal journal

Turn a raw meeting transcript or messy notes into a structured **deal-state record**
(action items, strategic reads, stakeholder map, next steps) and **append it to a
persistent per-deal journal**, so deal context compounds across meetings instead of
scattering across files.

This is the commercial/close counterpart to the `discovery-transcript-interpreter`
agent. Discovery extracts an *Evidence Register* for a value assessment. Deal Notes
captures *deal state* for a negotiation: who said what, what moved, what's blocked,
what's next, and what it means. Run it after **every** commercial / POC / legal touchpoint.

## When to Use

- After any client meeting, procurement session, POC playback, legal call, or internal deal-strategy call
- Triggers: "summarise this transcript", "deal notes from today", "update the deal journal"

## Usage

```
/deal-notes <path-to-transcript>   (and the engagement folder, if not obvious)
```

### Step 1 — Archive the source, then clear the anonymization gate (before any processing)

Copy the raw transcript into the engagement's `inputs/meetings/` subfolder **first** —
never extract from a file sitting only in Downloads, and never work from a copy of the
transcript pasted inline in chat as a shortcut. Then **Read the archived copy**. This
Read is automatically gated by the `anonymize-guard` PreToolUse hook
(`.claude/hooks/anonymize-guard.py`): if the transcript still contains unscrubbed PII
(names, emails, phones, account numbers), the Read is **blocked**.

**If blocked:** surface the hook's remediation and STOP — do not bypass it, and do not
substitute a pasted unscrubbed copy to work around it:

```
python3 scripts/anonymize_transcript.py --file <path> --engagement-dir <engagement-dir>
# -> writes a sibling .anon_<name> file (and a .anon_mapping_<stem>.json)
```

Once the `.anon_` version exists, resume from that file. This gate runs before speaker
resolution, before extraction, before anything else in this workflow.

### Step 2 — Resolve speakers
Map speaker labels to named Backbase vs client roles. Where a label is ambiguous,
**flag it as low-confidence — do not guess.** If the consultant gives an attribution
hint ("unnamed speakers are client-side"), apply it but still mark inferred names.

### Step 3 — Checkpoint 1 (pre-write)
Show the consultant the structured note + the one-line journal append you intend to
write. Confirm before writing anything.

### Step 4 — Extract into the fixed schema (below) and write the strategic read
The strategic read is the judgement layer — 3–6 "so-what" bullets — that makes this
worth more than minutes.

### Step 5 — Append to the deal journal
Append (never overwrite) to `outputs/DEAL_JOURNAL.md` (create if absent) in reverse-
chronological order.

### Step 6 — Checkpoint 2 (post-write)
Confirm the note + journal append with the consultant.

### Step 7 — Update the deal-state stub (if present)
After appending to `DEAL_JOURNAL.md`, check whether `outputs/INTERNAL_deal_state.json`
exists (it's written once round 1 of `/proposal-builder` has run). If it does, append a
dated state-delta stub — do **not** restructure the file and do **not** touch its
`rounds[]` or `current{}`:

```json
{
  "date": "YYYY-MM-DD",
  "meeting_ref": "<DEAL_JOURNAL.md anchor or heading for this entry>",
  "headline": "<one line — the single most important thing this meeting changed>"
}
```

pushed onto a top-level `pending_meeting_notes` array (create the array if absent).
This is a stub only — the round-N loop in `/proposal-builder` is what consumes these
into the ladder/rounds record; `/deal-notes` never writes to `rounds[]` or `current{}`
itself. If `INTERNAL_deal_state.json` doesn't exist yet, skip this step silently (round
1 of `/proposal-builder` hasn't run).

## Output schema (one block per meeting)

```markdown
# <Deal> · <Meeting type> — <date>
**Attendees:** <Backbase / client, named, with roles>   ·   **Source:** <archived path>

## Headline state of play
<2–4 sentences: where the deal is now>

## What was covered / demonstrated

## Key exchanges & tensions
<issue → position(s) → resolution or open item>

## Action items
| Owner | Action | When |
|---|---|---|

## Strategic reads
<3–6 so-what bullets: leverage, risk, who to protect, what it means for the close>

## Next milestones

<!-- TELEMETRY_START -->
agent: deal-notes
date: <YYYY-MM-DD>
source: <archived transcript path>
attendees_resolved: <n named / n total>
low_confidence_attributions: <n>
journal_appended: true
<!-- TELEMETRY_END -->
```

## Guardrails

- Every attribution and claim traces to the transcript; low-confidence ones are flagged, never asserted as fact.
- Strategic reads are clearly separated from what was actually said.
- Anonymise before any harvest to `knowledge/learnings/` (no client or stakeholder names).

## Governance (mandatory — per CLAUDE.md)

- **Deal journal** — `outputs/DEAL_JOURNAL.md` carries the narrative record (above) with its own telemetry block.
- **Governance journal** — also append a short entry to `ENGAGEMENT_JOURNAL.md` with a
  `<!-- TELEMETRY_START -->` block, per CLAUDE.md's Mandatory Governance Standards
  (this applies to every skill, not just `.claude/agents/*`).
- Dual checkpoint (pre-write + post-write).
- Recurring stakeholder-archetype / objection patterns may feed `knowledge/learnings/` (anonymised).

## Reference quality bar

Output should match or exceed hand-built commercial meeting notes: named attendees with
resolved roles, tensions stated as issue → position(s) → resolution/open-item (not
paraphrased into blandness), a strategic-reads section that reads as judgement rather
than a recap, and an action-item table a deal owner could work from without rereading
the transcript. If a note reads like a summary a client could see, it hasn't earned its
place in the deal journal.

## Origin

`knowledge/domains/negotiation/negotiation-tactics.md` ·
`knowledge/domains/negotiation/proposal-narrative.md`
