# Chunk Large Document

Break down a large document (PDF, CSV, or text file) into manageable chunks for processing.

## Usage

Invoke with a file path:
```
/chunk-document /path/to/large-file.pdf
```

## Instructions

When the user provides a large document that exceeds context limits, follow this procedure:

### For PDF Files:

**IMPORTANT:** Never read PDFs directly with the Read tool — large PDFs will fail with `API Error: 400 Could not process PDF`. Always extract text first.

Follow `knowledge/standards/context_management_protocol.md` Rule 9 for full details. Quick reference:

1. **Create extraction directory:**
   ```bash
   mkdir -p "[engagement_dir]/extracted/"
   ```

2. **Extract text** (try in order until one works):
   ```bash
   # Method A: pdftotext (preferred)
   pdftotext -layout "/path/to/file.pdf" "[engagement_dir]/extracted/filename.txt"

   # Method B: Python fallback
   python3 -c "
   import subprocess; subprocess.run(['pip3', 'install', 'pymupdf'], capture_output=True)
   import fitz; doc = fitz.open('/path/to/file.pdf')
   text = '\n--- Page Break ---\n'.join(p.get_text() for p in doc)
   open('[engagement_dir]/extracted/filename.txt', 'w').write(text)
   print(f'Extracted {doc.page_count} pages')
   "

   # Method C: macOS textutil
   textutil -convert txt -output "[engagement_dir]/extracted/filename.txt" "/path/to/file.pdf"
   ```

3. **Validate extraction:**
   ```bash
   wc -l "[engagement_dir]/extracted/filename.txt"
   head -20 "[engagement_dir]/extracted/filename.txt"
   ```
   If empty or garbled → try next method. If all fail → ask consultant for text version.

4. **Read in chunks** of 500-800 lines at a time:
   ```
   Read extracted file with offset=0, limit=500
   Read extracted file with offset=500, limit=500
   ... continue until complete
   ```

5. **Summarize each chunk** and build a cumulative understanding.

### For CSV Files:

1. **Check the file size**:
   ```bash
   wc -l /path/to/file.csv
   ```

2. **If over 200 rows**, read in chunks:
   ```
   Read /path/to/file.csv with offset=1, limit=150  # Header + first chunk
   Read /path/to/file.csv with offset=150, limit=200
   ... continue until complete
   ```

3. **Always preserve the header row** context when processing subsequent chunks.

### For Large Text/Markdown Files:

1. **Check the file size**:
   ```bash
   wc -l /path/to/file.md
   ```

2. **If over 2000 lines**, read in chunks of 500-800 lines.

3. **Track section headers** to maintain document structure context.

## Output

After processing all chunks, provide:

1. **Document Summary**: High-level overview of contents
2. **Key Sections**: List of major sections/topics covered
3. **Extracted Data**: Any specific data points or metrics found
4. **Recommendations**: How this content should be used in the knowledge base

## For Value Consulting Documents

When processing ROI models, assessment reports, or business cases, extract:

### From Assessment/Solutioning Reports:
- Customer persona mappings
- Journey analysis (current state and to-be state)
- Capability assessment findings
- Architecture diagrams/descriptions
- Delivery roadmap phases
- Benefits case levers and values

### From ROI/Business Case Documents:
- Value levers (revenue uplift, cost avoidance)
- Baseline metrics and assumptions
- Scenario definitions (Conservative/Moderate/Aggressive)
- Implementation timelines
- Investment breakdowns (license, implementation)
- Servicing task analysis
- Backbase impact percentages

### From Discovery Transcripts:
- Pain points with evidence quotes
- Metrics mentioned
- Constraints and risks
- Stakeholder priorities

## Context Limit Prevention

To avoid reaching context limits:

1. **Process in focused chunks**: 300-500 lines per read
2. **Extract key data immediately**: Don't hold raw text, summarize and discard
3. **Build incremental output**: Write findings to a file after each chunk
4. **Use structured extraction**: Focus on tables, metrics, and specific sections

## Example

User: `/chunk-document /Users/me/Documents/large_report.pdf`