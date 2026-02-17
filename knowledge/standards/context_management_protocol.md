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

**For PDFs:** See Rule 9 below — NEVER read PDFs directly with the Read tool. Always extract text first.

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

## Rule 9: PDF and Binary File Handling

PDFs are common inputs (annual reports, strategy docs, prior assessments). The Claude Read tool has a size limit for PDFs — large files will fail with `API Error: 400 Could not process PDF`. To prevent this, **NEVER attempt to read a PDF directly with the Read tool.** Always extract text first.

### Step 1: Extract Text from PDF

Try these methods in order. Use the first one that succeeds:

**Method A — pdftotext (preferred):**
```bash
pdftotext -layout "/path/to/file.pdf" "[engagement_dir]/extracted/[filename].txt"
```

**Method B — Python fallback (if pdftotext not installed):**
```bash
python3 -c "
import subprocess
subprocess.run(['pip3', 'install', 'pymupdf'], capture_output=True)
import fitz
doc = fitz.open('/path/to/file.pdf')
text = ''
for page in doc:
    text += page.get_text() + '\n--- Page Break ---\n'
with open('[engagement_dir]/extracted/[filename].txt', 'w') as f:
    f.write(text)
print(f'Extracted {doc.page_count} pages')
"
```

**Method C — macOS textutil fallback:**
```bash
textutil -convert txt -output "[engagement_dir]/extracted/[filename].txt" "/path/to/file.pdf"
```

**If all methods fail:** Inform the consultant that the PDF cannot be extracted automatically. Ask them to provide a text or markdown version, or to copy-paste the relevant sections.

### Step 2: Validate Extraction

After extraction, verify the output is usable:

```bash
wc -l "[engagement_dir]/extracted/[filename].txt"
head -20 "[engagement_dir]/extracted/[filename].txt"
```

Check for:
- **Empty file** → extraction failed silently; try next method
- **Garbled text** → PDF may be scanned/image-based; inform consultant
- **Very short output from a long PDF** → likely image-heavy; inform consultant

### Step 3: Apply Standard Chunking

Once text is extracted, apply Rule 1 and Rule 2 thresholds:
- Under 500 lines → read whole file
- 500–1500 lines → chunk in 2-3 reads
- Over 1500 lines → full chunking protocol

### Step 4: Log in Engagement Journal

Record the extraction in the engagement journal:
```markdown
**PDF Processed:** [filename.pdf]
**Extraction Method:** [pdftotext / pymupdf / textutil]
**Pages:** [N] | **Extracted Lines:** [N]
**Quality:** [Good / Partial — describe issues]
**Output:** [engagement_dir]/extracted/[filename].txt
```

### Important Rules

- **NEVER use `/tmp/` for extracted files.** Always write to `[engagement_dir]/extracted/` so files persist across sessions and are auditable.
- **Create the `extracted/` subdirectory** if it doesn't exist: `mkdir -p "[engagement_dir]/extracted/"`
- **Preserve the original PDF.** The extracted text is a working copy — never delete the source.
- **For scanned PDFs** (image-based with no selectable text): inform the consultant immediately. OCR is out of scope for this system. The consultant must provide a text alternative.
- **For password-protected PDFs**: inform the consultant. Do not attempt to bypass encryption.

## Rule 10: Use Domain-Indexed Knowledge Files

Large knowledge files have been split into domain-specific slices. **Always load the domain slice, not the full master file.**

| Full File | Lines | Domain Slice | Lines |
|-----------|-------|-------------|-------|
| `knowledge/domains/Product Directory (1).csv` | 3,117 | `knowledge/domains/product_directory_{domain}.md` | 87-285 |
| `knowledge/standards/capability_taxonomy.md` | 2,109 | `knowledge/standards/capability_taxonomy_{domain}.md` | 204-758 |

**Rules:**
- **Narrative Assembler, Capability Agent, ROI Agent, Roadmap Agent, Market Context, Benchmark Librarian:** Load the domain slice only. Never load the full CSV or full taxonomy.
- **Use Case Designer:** The ONLY agent authorized to load the full Product Directory CSV (needed for feature-level validation).
- **Multi-domain engagements:** Load multiple domain slices (e.g., `capability_taxonomy_retail.md` + `capability_taxonomy_investing.md`). Still cheaper than the full 2,109-line master.
- **Domain slices are regenerated** by running `python3 scripts/index_product_directory.py` and `python3 scripts/split_capability_taxonomy.py`. Regenerate when the source files are updated.

Replace `{domain}` with the engagement domain: `retail`, `wealth`, `sme`, `commercial`, or `investing`.

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
