# Context Management Protocol

This protocol is MANDATORY for all agents in the Value Consulting system. It prevents context limit failures and ensures engagement continuity.

## Why This Exists

Claude has a finite context window. A single engagement can produce 100,000+ words across transcripts, analysis, and outputs. Without discipline, the system will hit context limits mid-engagement, causing frustration and lost work. This protocol makes that impossible.

## Rule 1: Check Before You Read

Before reading ANY file — input or output — check its size first.

```bash
wc -l /path/to/file
```

**Thresholds:**

| File size | Action |
|-----------|--------|
| Under 500 lines | Read the whole file |
| 500–1500 lines | Read in 2-3 chunks of 500 lines each |
| Over 1500 lines | Use the full chunking protocol (Rule 2) |

This applies to EVERYTHING: transcripts, PDFs, old engagement outputs, domain knowledge files, financial data, annual reports.

## Rule 2: Chunk Large Files

When a file exceeds 500 lines:

1. **Read in chunks of 400-500 lines:**
   ```
   Read file with offset=0, limit=500
   → Process this chunk: extract key findings, data, or relevant content
   → Write extracted findings to disk

   Read file with offset=500, limit=500
   → Process this chunk
   → Append to findings file

   Continue until complete
   ```

2. **Write findings to disk after each chunk.** Never accumulate raw text in context.

3. **After all chunks:** read only the extracted findings file to consolidate.

**For PDFs specifically:**
```bash
pdftotext -layout "/path/to/file.pdf" "/tmp/extracted_text.txt"
wc -l /tmp/extracted_text.txt
```
Then apply the same chunking thresholds.

## Rule 3: One Transcript at a Time

When processing multiple input files (transcripts, reports, documents):

1. **Never load more than one large input file in context at the same time.**
2. Process sequentially:
   ```
   File 1 → Read/chunk → Extract → Write interim output to disk
   File 2 → Read/chunk → Extract → Write interim output to disk
   ...
   File N → Read/chunk → Extract → Write interim output to disk

   Then: Read only interim outputs → Consolidate → Write final output
   ```
3. De-duplicate findings that appear across multiple files.

## Rule 4: Disk-Based Handoff Between Agents

Agents communicate through files, not through context. Every agent:
- **Reads** only the output files from upstream agents (not raw inputs)
- **Writes** its own output to disk before passing to the next agent

```
Discovery Agent    → writes: evidence_register.md, pain_points.md, metrics.md
Capability Agent   → reads: evidence_register.md (NOT raw transcripts)
                   → writes: capability_assessment.md
ROI Agent          → reads: capability_assessment.md, metrics.md (NOT raw transcripts)
                   → writes: roi_report.md
Roadmap Agent      → reads: capability_assessment.md, roi_report.md
                   → writes: roadmap.md
Assembly Agent     → reads: all output .md files (NOT raw inputs)
                   → writes: executive_summary.md, assessment_report.md
```

No agent should ever need raw transcripts after the Discovery Agent has processed them.

## Rule 5: Write Incrementally for Large Outputs

When generating a large deliverable (assessment report, ROI model, roadmap):

1. **Don't build the entire document in context.** Write section by section:
   ```
   Generate Section 1 (Executive Summary) → Write to file
   Generate Section 2 (Capability Matrix) → Append to file
   Generate Section 3 (Gap Analysis) → Append to file
   ...
   ```

2. **For very large outputs** (>2000 lines expected), split into multiple files and combine at the end.

3. **For tables with many rows** (e.g., 50+ evidence items), generate in batches and write each batch to disk.

## Rule 6: Maintain the Engagement Journal

Every engagement has a journal file at `[engagement_dir]/ENGAGEMENT_JOURNAL.md`. This is the system's memory.

**When to write to the journal:**
- At the start of every agent invocation
- After every major decision or finding
- When assumptions are made
- When the consultant approves or rejects something
- At the end of every agent's work
- When the engagement pauses or resumes

**What to log:**
```markdown
## [Date] [Time] — [Agent Name]

**Action:** [What was done]
**Input:** [What files were read]
**Output:** [What files were produced]
**Key Decisions:**
- [Decision 1 and rationale]
- [Decision 2 and rationale]
**Assumptions Made:**
- [Assumption and why]
**Consultant Direction:**
- [What the consultant asked for or approved]
**Status:** [What's done, what's next]
**Open Items:**
- [Anything pending or requiring follow-up]
```

The journal serves three purposes:
1. **Resumability** — any consultant can pick up the engagement months later
2. **Audit trail** — every decision is traceable
3. **Context restoration** — when a new Claude session starts, read the journal instead of re-reading all raw inputs

## Rule 7: Resume Protocol

When an engagement is being resumed (consultant returns to existing work):

1. **Read the Engagement Journal FIRST** — this gives you full context without re-reading raw inputs
2. **Read the engagement intake** — for client context
3. **Read only the latest output files** — not raw transcripts
4. **Confirm status with the consultant:** "Based on the journal, here's where we left off: [summary]. What would you like to work on next?"

**Never re-read raw transcripts on resume.** The processed outputs contain everything needed.

## Rule 8: Context Budget Awareness

Be aware of how much context you're using. Warning signs:
- You've read 3+ large files without writing anything to disk
- You're generating a document that's already 1000+ lines and still growing in memory
- You're about to read a new file but haven't released the previous one

**When in doubt, write to disk and start fresh.** It's always safer to write interim results and re-read the summary than to risk hitting the limit.

## Applying This Protocol

Every agent in the system includes a reference to this protocol. The rules are non-negotiable. They apply to:

- Processing discovery transcripts
- Reading old engagement outputs for reference
- Loading domain knowledge packs
- Reading client-provided documents (annual reports, strategy docs, PDFs)
- Generating large deliverables
- Resuming paused engagements
- Any other file I/O operation

The goal: **a consultant can run an engagement with 10 transcripts, 5 PDFs, and a full deliverable suite, and never hit a context limit.**
