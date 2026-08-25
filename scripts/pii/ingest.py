#!/usr/bin/env python3
"""
Document ingest — PDF / DOCX / PPTX / XLSX / CSV to anonymised text.

WHAT THIS IS (ticket #162, .prd/prd-v6.md §3, .design/solution-design-v6.md D11)
  The PII gate used to see `.md/.txt/.vtt/.srt/.json/.csv/.log` only. Real
  engagement `inputs/` directories hold 43 PDFs, 10 spreadsheets, 8 Word
  documents, 2 decks — and 3 markdown files. Roughly 3 of 77 real files were
  in scope; annual reports, RFPs, client decks and pricing spreadsheets were
  read into context unscrubbed. This module converts the other 74.

  Extract text -> anonymise through `scripts/pii/engine.py` -> write a
  `.anon_` sibling. Agents read only the `.anon_` artifact; the raw document
  is never read by any agent, in any mode.

ONE ANONYMISATION SCHEME (this is the point of the cycle, not an aside)
  Every extractor returns TEXT, and every byte of that text goes through the
  same `PIISession` that transcripts go through. There is no second scheme,
  no per-format placeholder convention and no per-format mapping. Pass one
  session (or one shared `entity_mapping`) across a whole engagement and the
  same email in a PDF and in a spreadsheet gets the same placeholder — which
  is what `artifact_boundary.deanonymize_dir` depends on when it restores the
  deliverable from a single mapping.

  This is also why `presidio-structured` is NOT used for the XLSX/CSV path —
  see "D11 DECISION" below.

⚠️ THE RENDERING FORMAT IS A DETECTION DECISION, NOT A READABILITY ONE
  Read this before "tidying up" the table rendering into a markdown table.

  spaCy's `en_core_web_lg` misses person names in a SHAPE-DEPENDENT way
  (#159/#161; engine.py's "MEASURED DETECTION LIMITS"). In a markdown table
  cell `| Aisha Rahman | CFO |` it tags the name ORGANIZATION, which is not
  an enabled entity type (enabling it would strip "Backbase", "Temenos" and
  every other vendor name a deliverable depends on), so the name passes
  straight through the gate. The same name on a label line is detected.

  This module turns every spreadsheet row, every Word table and every
  PowerPoint table into text. A markdown pipe table is the natural, readable
  choice and it is exactly the one shape the detector fails on — a client's
  stakeholder or customer list in an XLSX would render as a pipe table and
  leak. So the format was chosen on measurement:

      30 synthetic person names in tabular data, same content, same engine.
      "run-on spans" counts detected entities whose span ran past the value
      into the next line; "labels lost" counts field labels swallowed by one
      of those spans (see `_terminate`):

        rendering                                  PERSON  run-on  labels lost
        ------------------------------------------ ------  ------  -----------
        markdown pipe table (4-col)                 28/30       0            0
        markdown pipe table (2-col)                 28/30       0            0
        tab-separated columns                       28/30       0            0
        one-line-per-row, labelled                  30/30       0            0
        record-per-row label lines (no terminator)  30/30       2            1
        record-per-row label lines + terminator     30/30       0            0

      Every pipe-table and TSV miss included "Aisha Rahman" — the same name
      #159 recorded as tagged ORGANIZATION in a table cell.

  CHOSEN: record-per-row label lines with a sentence terminator
  (`_render_records` + `_terminate`) — the bottom row. It detects every
  name, loses no field labels, is a shape `pii/denylist.py`'s label-line
  extractor already understands, and a record with one field per line is
  genuinely readable: a row's fields stay together and stay labelled, which
  a wall of text would not.

  NOTE — this applies to the formats where the text is CONSTRUCTED from
  structured data: DOCX/PPTX tables, XLSX sheets, CSV rows. A PDF has no
  structured table to re-render; its text is extracted as laid out, so a
  pipe-formatted table inside a PDF stays pipe-formatted and carries that
  shape's detection risk. That is a seam, not an oversight: reflowing a
  PDF's visual layout into records is a guess, and a wrong guess would
  scramble the document.

  If you change `_render_records`, re-run the measurement first. The eval
  check `document_formats_converted_and_scrubbed` plants a person name in
  tabular data in every format specifically so a regression here fails the
  gate rather than passing it.

D11 DECISION — `presidio-structured` 0.0.8 REJECTED for the XLSX/CSV path
  PRD §8 and design D11 asked for this to be settled on evidence, with the
  plain text path as the recorded fallback. Measured against 0.0.8:

  1. **It cannot use our operator, so it cannot share our mapping.**
     `PandasDataProcessor._generate_operator_mapping` constructs its own
     `OperatorsFactory()` as a local, with no injection point, so
     `InstanceCounterAnonymizer` ("entity_counter") is unregistered there:

         InvalidParamError: Invalid operator class 'entity_counter'.

     Using it would mean a SECOND anonymisation scheme with its own
     placeholders and its own mapping, for spreadsheets only — the exact
     fragmentation this cycle exists to remove, and it would break
     cross-file placeholder consistency.

  2. **Its column-level typing is wrong on our data.** It assigns ONE entity
     type per column from a sample. On a 4-column stakeholder sheet:

         StructuredAnalysis(entity_mapping={'Name': 'PERSON',
                                            'Email': 'URL',
                                            'Account': 'DATE_TIME'})

     Email typed as URL, a 10-digit account number typed as DATE_TIME.
     DATE_TIME and URL are both deliberately NOT anonymised here
     (engine.py's DEFAULT_ENTITIES: dates drive every ROI model; the URL
     recogniser partial-matches inside email local parts) — so those two
     columns would have been passed through in cleartext.

  FALLBACK TAKEN (as D11 prescribes): extract cell strings and run them
  through the plain text analyzer/anonymizer — the inverse of what
  `deanonymize_dir` already does for restore. `pandas` and
  `presidio-structured` are not imported by this module at all.

OUTPUT NAMING — `.anon_<full original filename>.md`
  `report.pdf` -> `.anon_report.pdf.md`, not `.anon_report.md`. The source
  extension is KEPT because a real `inputs/` directory holds `Pricing.pdf`
  and `Pricing.xlsx` side by side, and dropping the extension would have one
  anonymised artifact silently overwrite the other. Keeping it also makes the
  mapping raw-path <-> anon-path a pure, invertible function of the
  filename, which is what the guard rewrite (#164) needs to answer "is this
  document scrubbed?" without a directory scan.

  Plain-text inputs (`.md`, `.txt`, `.vtt`, `.srt`, `.log`, `.json`) are NOT
  handled here — they keep going through
  `scripts/anonymize_transcript.anonymize_transcript_file`, which writes
  `.anon_<name>` (no added `.md`). Routing them through both would produce
  two differently-named anonymised artifacts for one input.

NEVER SILENT, NEVER DESTRUCTIVE
  - An unsupported format raises `UnsupportedFormatError` naming the format.
  - A password-protected or corrupt document raises `ExtractionFailedError`.
  - A document that yields NO text raises `EmptyExtractionError` — a scanned
    PDF must not be reported as "successfully anonymised, 0 bytes".
  Nothing is ever skipped silently and no empty `.anon_` file is ever
  written. Every error carries a plain-language `.message` the guard can
  print verbatim (ux-design-v6.md copy rules: consequence before
  instruction, no tool names in the consequence).
  - Extraction is READ-ONLY. The original file is opened for reading and
    never written, moved or re-saved; `.anon_` is a sibling artifact.

DETERMINISTIC
  The same bytes in produce byte-identical text out: extractors walk
  documents in document order, no dict-ordering, no timestamps, no absolute
  paths, and line endings are normalised. `document_formats_converted_and_scrubbed`
  asserts this — a second ingest of the same file must match the first byte
  for byte.

IMAGES ARE OUT OF SCOPE (#163)
  No OCR is attempted, here or anywhere in this module. Where a DOCX or PPTX
  carries an embedded image, the renderer leaves a visible seam
  (`IMAGE_SEAM_MARKER`) at the image's position in document order so a
  reader — and #163 — can see exactly what was not read. An image passed
  directly to `extract_text` raises `ImageIngestNotSupportedError`, which is
  an `UnsupportedFormatError`.

INTERPRETER
  This module is importable and its EXTRACTORS are runnable on plain Python
  3.9 (matching `scripts/artifact_boundary.py`'s importability contract):
  every optional library is imported LAZILY inside its own extractor branch,
  and `scripts/pii/engine.py` is imported lazily too, only on the
  anonymisation path. `import scripts.pii.ingest` pulls in nothing but the
  standard library. Anonymisation itself needs `.venv` (Presidio, 3.10-3.13).
"""
from __future__ import annotations

import csv
import io
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "SUPPORTED_SUFFIXES",
    "IMAGE_SUFFIXES",
    "IMAGE_SEAM_MARKER",
    "IngestError",
    "UnsupportedFormatError",
    "ImageIngestNotSupportedError",
    "ExtractorUnavailableError",
    "ExtractionFailedError",
    "EmptyExtractionError",
    "IngestResult",
    "anon_path_for",
    "extract_text",
    "ingest_file",
    "is_supported",
]

# Formats this module converts. Keep in sync with the extractor dispatch in
# `extract_text` and with the eval's per-format fixture set.
SUPPORTED_SUFFIXES: Tuple[str, ...] = (".pdf", ".docx", ".pptx", ".xlsx", ".csv")

# Recognised so the error can name #163 instead of saying "unsupported".
IMAGE_SUFFIXES: Tuple[str, ...] = (
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic",
)

# Left in the text where an embedded image sits, in document order. Never
# OCR'd (#163). Visible on purpose: a silent drop would make an image-only
# slide indistinguishable from an empty one.
IMAGE_SEAM_MARKER = "[embedded image — not read; image ingest is not enabled]"


# --- typed errors ----------------------------------------------------------

class IngestError(RuntimeError):
    """Base for every ingest failure.

    Carries the offending `path` and `format` so a caller — the guard, most
    of all — can render a plain-language message without re-deriving them
    from the exception text.
    """

    def __init__(self, message: str, *, path=None, fmt: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.path = Path(path) if path is not None else None
        self.format = fmt

    def __str__(self) -> str:  # keep the plain-language text as the str form
        return self.message


class UnsupportedFormatError(IngestError):
    """The file's format has no extractor. Names the format in the message."""


class ImageIngestNotSupportedError(UnsupportedFormatError):
    """An image was passed directly. Out of scope for #162 — see #163."""


class ExtractorUnavailableError(IngestError):
    """The extractor's library is not installed under this interpreter."""


class ExtractionFailedError(IngestError):
    """The document could not be read — encrypted, password-protected or
    corrupt. Distinct from `EmptyExtractionError`: the file was rejected,
    not merely textless."""


class EmptyExtractionError(IngestError):
    """The document was read successfully but yielded no text at all (a
    scanned PDF, an image-only deck). Never reported as a successful scrub —
    an empty `.anon_` file would be indistinguishable from a clean one."""


# --- rendering: the detection-driven shape ---------------------------------
#
# See the module docstring's measurement table. Do not replace this with a
# markdown pipe table.

def _clean_cell(value) -> str:
    """One cell as a single-line string. Newlines inside a cell would break
    the one-field-per-line contract the detector (and denylist.py's
    label-line extractor) relies on."""
    if value is None:
        return ""
    text = value if isinstance(value, str) else str(value)
    return re.sub(r"\s+", " ", text).strip()


def _terminate(value: str) -> str:
    """End a field value with sentence punctuation.

    Not cosmetic — measured. Without a terminator, spaCy runs the PERSON span
    on past the newline and swallows the NEXT field's label: `Name: Aisha
    Rahman` / `Role: CFO` anonymises to `Name: <PERSON_2>: Chief Financial
    Officer`, because the detected entity was literally `"Aisha Rahman\\nRole"`.
    Detection is still correct and the round-trip is still exact, but the
    record loses a label, and the placeholder is bound to a value that would
    not match the same person written anywhere else — breaking the cross-file
    placeholder identity this module exists to preserve.

    With the terminator: 30/30 names detected, 0 run-on spans, and every
    entity key is the clean value (`'Aisha Rahman'`, not `'Aisha Rahman\\nRole'`)
    — verified to leave email/phone/account spans byte-identical to the
    unterminated rendering, so a value seen in a spreadsheet and in a
    transcript still shares one placeholder.
    """
    value = value.rstrip(" ,;:")
    if not value:
        return value
    if value[-1] in ".!?":
        return value
    return value + "."


def _render_records(
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    *,
    label: str = "Record",
) -> List[str]:
    """Tabular data as record-per-row label lines — the measured-best shape.

        ### Record 1
        Name: Aisha Rahman.
        Role: CFO.

        ### Record 2
        ...

    Empty rows are dropped; empty cells are dropped from their record (a
    `Role:` line with nothing after it is noise, and a bare label is not a
    detection surface). A column with no header takes a positional name so
    every value stays attributable.
    """
    safe_headers = [
        _clean_cell(h) or "Column %d" % (i + 1) for i, h in enumerate(headers)
    ]
    lines: List[str] = []
    index = 0
    for row in rows:
        cells = [_clean_cell(c) for c in row]
        if not any(cells):
            continue
        index += 1
        lines.append("### %s %d" % (label, index))
        for i, cell in enumerate(cells):
            if not cell:
                continue
            header = safe_headers[i] if i < len(safe_headers) else "Column %d" % (i + 1)
            lines.append("%s: %s" % (header, _terminate(cell)))
        lines.append("")
    return lines


def _normalise(lines: Iterable[str]) -> str:
    """Join rendered lines into the final text: CRLF normalised, trailing
    whitespace stripped per line, at most one trailing newline. Determinism
    depends on this — same bytes in, same bytes out."""
    out: List[str] = []
    for line in lines:
        for part in str(line).replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            out.append(part.rstrip())
    # Collapse 3+ blank lines to 2; a document's own spacing is not signal.
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip("\n") + "\n"


# --- extractors ------------------------------------------------------------
#
# Each imports its library LAZILY, inside its own branch, so this module stays
# importable on plain Python 3.9 without every optional library present.

def _extract_pdf(path: Path) -> str:
    try:
        from pdfminer.high_level import extract_pages  # noqa: PLC0415 - lazy by contract
        from pdfminer.layout import LAParams, LTTextContainer
        from pdfminer.pdfdocument import PDFPasswordIncorrect
        from pdfminer.pdfparser import PDFSyntaxError
    except ImportError as exc:
        raise ExtractorUnavailableError(
            "This PDF cannot be prepared for review because the PDF reader is "
            "not installed. Run `bash scripts/setup_pii.sh`, then try again.",
            path=path, fmt="pdf",
        ) from exc

    lines: List[str] = []
    try:
        for page_number, page in enumerate(extract_pages(str(path), laparams=LAParams()), 1):
            lines.append("## Page %d" % page_number)
            lines.append("")
            for element in page:
                if isinstance(element, LTTextContainer):
                    lines.append(element.get_text())
            lines.append("")
    except PDFPasswordIncorrect as exc:
        raise ExtractionFailedError(
            "This PDF is password-protected, so nothing could be read from it "
            "and it has not been prepared for review. Save an unprotected copy "
            "into the same folder and use that instead.",
            path=path, fmt="pdf",
        ) from exc
    except PDFSyntaxError as exc:
        raise ExtractionFailedError(
            "This PDF could not be read — the file looks damaged or is not "
            "really a PDF. It has not been prepared for review.",
            path=path, fmt="pdf",
        ) from exc
    except Exception as exc:  # noqa: BLE001 - any reader fault becomes a typed, actionable error
        raise ExtractionFailedError(
            "This PDF could not be read (%s), so it has not been prepared for "
            "review." % type(exc).__name__,
            path=path, fmt="pdf",
        ) from exc
    return _normalise(lines)


def _docx_heading_prefix(style_name: str) -> str:
    """`Heading 2` -> `###` (one deeper than the sheet/page level, so a
    document's own hierarchy nests under the structural markers this module
    emits). Title -> `##`. Anything else -> no prefix."""
    name = (style_name or "").strip().lower()
    if name == "title":
        return "## "
    match = re.match(r"^heading (\d+)$", name)
    if not match:
        return ""
    level = min(int(match.group(1)), 5)
    return "#" * (level + 1) + " "


def _extract_docx(path: Path) -> str:
    try:
        import docx  # noqa: PLC0415 - lazy by contract
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise ExtractorUnavailableError(
            "This Word document cannot be prepared for review because the Word "
            "reader is not installed. Run `bash scripts/setup_pii.sh`, then try "
            "again.",
            path=path, fmt="docx",
        ) from exc

    try:
        document = docx.Document(str(path))
    except Exception as exc:  # noqa: BLE001
        raise ExtractionFailedError(
            "This Word document could not be read — it may be password-protected "
            "or damaged. It has not been prepared for review.",
            path=path, fmt="docx",
        ) from exc

    lines: List[str] = []
    table_index = 0
    # Walk the body in DOCUMENT ORDER. `document.paragraphs` and
    # `document.tables` are separate sequences, so using them would silently
    # reorder a document into "all prose, then all tables" and detach every
    # table from the heading that gives it meaning.
    body = document.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            paragraph = Paragraph(child, document)
            text = _clean_cell(paragraph.text)
            has_image = bool(child.findall(
                ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
            )) or bool(child.findall(
                ".//{urn:schemas-microsoft-com:vml}imagedata"
            ))
            if text:
                lines.append(_docx_heading_prefix(paragraph.style.name if paragraph.style else "") + text)
            if has_image:
                lines.append(IMAGE_SEAM_MARKER)
            if text or has_image:
                lines.append("")
        elif tag == "tbl":
            table_index += 1
            table = Table(child, document)
            rows = [[cell.text for cell in row.cells] for row in table.rows]
            if not rows:
                continue
            lines.append("## Table %d" % table_index)
            lines.append("")
            lines.extend(_render_records(rows[0], rows[1:], label="Row"))
    return _normalise(lines)


def _extract_pptx(path: Path) -> str:
    try:
        from pptx import Presentation  # noqa: PLC0415 - lazy by contract
        from pptx.enum.shapes import MSO_SHAPE_TYPE
    except ImportError as exc:
        raise ExtractorUnavailableError(
            "This presentation cannot be prepared for review because the "
            "PowerPoint reader is not installed. Run `bash scripts/setup_pii.sh`, "
            "then try again.",
            path=path, fmt="pptx",
        ) from exc

    try:
        presentation = Presentation(str(path))
    except Exception as exc:  # noqa: BLE001
        raise ExtractionFailedError(
            "This presentation could not be read — it may be password-protected "
            "or damaged. It has not been prepared for review.",
            path=path, fmt="pptx",
        ) from exc

    lines: List[str] = []
    for slide_number, slide in enumerate(presentation.slides, 1):
        lines.append("## Slide %d" % slide_number)
        lines.append("")
        table_index = 0
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                lines.append(IMAGE_SEAM_MARKER)
                lines.append("")
                continue
            if getattr(shape, "has_table", False) and shape.has_table:
                table_index += 1
                rows = [[cell.text for cell in row.cells] for row in shape.table.rows]
                if not rows:
                    continue
                lines.append("### Table %d" % table_index)
                lines.append("")
                lines.extend(_render_records(rows[0], rows[1:], label="Row"))
                continue
            if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = _clean_cell("".join(run.text for run in paragraph.runs))
                    if text:
                        lines.append(text)
                lines.append("")
        # Speaker notes carry stakeholder names as often as the slide does.
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notes = _clean_cell(slide.notes_slide.notes_text_frame.text)
            if notes:
                lines.append("### Speaker notes")
                lines.append("")
                lines.append(notes)
                lines.append("")
    return _normalise(lines)


def _extract_xlsx(path: Path) -> str:
    try:
        import openpyxl  # noqa: PLC0415 - lazy by contract
    except ImportError as exc:
        raise ExtractorUnavailableError(
            "This spreadsheet cannot be prepared for review because the "
            "spreadsheet reader is not installed. Run `bash scripts/setup_pii.sh`, "
            "then try again.",
            path=path, fmt="xlsx",
        ) from exc

    try:
        # read_only: never touches the original beyond reading it.
        # data_only: formula RESULTS, not formula text — a formula string is
        # not the value a reader (or the detector) needs to see.
        workbook = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001
        raise ExtractionFailedError(
            "This spreadsheet could not be read — it may be password-protected "
            "or damaged. It has not been prepared for review.",
            path=path, fmt="xlsx",
        ) from exc

    lines: List[str] = []
    try:
        for sheet in workbook.worksheets:
            lines.append("## Sheet: %s" % _clean_cell(sheet.title))
            lines.append("")
            rows = [
                [_clean_cell(c) for c in row]
                for row in sheet.iter_rows(values_only=True)
            ]
            rows = [r for r in rows if any(r)]
            if not rows:
                lines.append("(no data)")
                lines.append("")
                continue
            # First non-empty row is the header row when it looks like one
            # (>=2 labelled columns, none of them purely numeric). Otherwise
            # every row is data and columns take positional names.
            header = rows[0]
            looks_like_header = (
                sum(1 for c in header if c) >= 2
                and not any(re.fullmatch(r"-?\d+(\.\d+)?", c) for c in header if c)
            )
            if looks_like_header:
                lines.extend(_render_records(header, rows[1:], label="Row"))
            else:
                width = max(len(r) for r in rows)
                lines.extend(_render_records([""] * width, rows, label="Row"))
    finally:
        workbook.close()
    return _normalise(lines)


def _extract_csv(path: Path) -> str:
    # stdlib only — no lazy import needed, and no pandas (see D11 DECISION).
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ExtractionFailedError(
            "This file could not be read, so it has not been prepared for "
            "review.",
            path=path, fmt="csv",
        ) from exc
    text = raw.decode("utf-8-sig", errors="replace")

    delimiter = ","
    try:
        # Deterministic: the sniff reads a fixed prefix of the same bytes, and
        # falls back to comma on any doubt.
        delimiter = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|").delimiter
    except Exception:  # noqa: BLE001 - a sniff failure is normal, not an error
        delimiter = ","

    rows = [row for row in csv.reader(io.StringIO(text), delimiter=delimiter)]
    rows = [[_clean_cell(c) for c in row] for row in rows]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""

    lines: List[str] = ["## %s" % _clean_cell(path.name), ""]
    header = rows[0]
    looks_like_header = (
        sum(1 for c in header if c) >= 2
        and not any(re.fullmatch(r"-?\d+(\.\d+)?", c) for c in header if c)
    )
    if looks_like_header:
        lines.extend(_render_records(header, rows[1:], label="Row"))
    else:
        width = max(len(r) for r in rows)
        lines.extend(_render_records([""] * width, rows, label="Row"))
    return _normalise(lines)


_EXTRACTORS = {
    ".pdf": _extract_pdf,
    ".docx": _extract_docx,
    ".pptx": _extract_pptx,
    ".xlsx": _extract_xlsx,
    ".csv": _extract_csv,
}


# --- public API ------------------------------------------------------------

def is_supported(path) -> bool:
    """True when `extract_text` has an extractor for this file's format."""
    return Path(path).suffix.lower() in _EXTRACTORS


def anon_path_for(path, output_dir=None) -> Path:
    """The `.anon_` sibling for `path` — `report.pdf` -> `.anon_report.pdf.md`.

    A pure, invertible function of the filename; see the module docstring's
    OUTPUT NAMING note for why the source extension is kept.
    """
    path = Path(path)
    directory = Path(output_dir) if output_dir is not None else path.parent
    return directory / (".anon_%s.md" % path.name)


def extract_text(path) -> str:
    """Document -> plain text, with structure preserved and NO anonymisation.

    Read-only: the original file is never modified. Raises
    `UnsupportedFormatError` (including `ImageIngestNotSupportedError`),
    `ExtractorUnavailableError`, `ExtractionFailedError` or
    `EmptyExtractionError` — never returns empty, never silently skips.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    fmt = suffix.lstrip(".") or "(no extension)"

    if not path.is_file():
        raise ExtractionFailedError(
            "There is no file at %s, so nothing could be prepared for review."
            % path.name,
            path=path, fmt=fmt,
        )

    if suffix in IMAGE_SUFFIXES:
        raise ImageIngestNotSupportedError(
            "Images are not prepared for review yet, so this %s file has been "
            "left alone and must not be opened. Describe what it shows instead, "
            "or export the text into a document." % fmt,
            path=path, fmt=fmt,
        )

    extractor = _EXTRACTORS.get(suffix)
    if extractor is None:
        raise UnsupportedFormatError(
            "%s files cannot be prepared for review, so this one has been left "
            "alone and must not be opened. Save it as PDF, Word, PowerPoint, "
            "Excel or CSV into the same folder and use that copy instead."
            % (fmt.upper() if suffix else "Extensionless"),
            path=path, fmt=fmt,
        )

    text = extractor(path)
    if not text or not text.strip():
        raise EmptyExtractionError(
            "No text could be read out of this %s file — it may hold only "
            "pictures, scans or empty cells. It has not been prepared for "
            "review and must not be opened." % fmt,
            path=path, fmt=fmt,
        )
    return text


class IngestResult(object):
    """What one ingest produced. `session` is returned so a caller can keep
    feeding the SAME session to the next document — that is what makes
    placeholders consistent across an engagement's whole input set."""

    def __init__(self, source: Path, anon_path: Path, fmt: str,
                 extracted_chars: int, anonymized_chars: int, session):
        self.source = source
        self.anon_path = anon_path
        self.format = fmt
        self.extracted_chars = extracted_chars
        self.anonymized_chars = anonymized_chars
        self.session = session

    @property
    def entity_mapping(self) -> Dict[str, Dict[str, str]]:
        return self.session.entity_mapping

    def mapping_file_dict(self) -> Dict:
        return self.session.mapping_file_dict()

    def __repr__(self) -> str:
        return "IngestResult(%s -> %s, %s, %d chars)" % (
            self.source.name, self.anon_path.name, self.format, self.anonymized_chars,
        )


def ingest_file(
    path,
    *,
    engagement_dir=None,
    session=None,
    entity_mapping: Optional[Dict[str, Dict[str, str]]] = None,
    output_dir=None,
) -> IngestResult:
    """Extract, anonymise through `scripts/pii/engine.py`, write `.anon_X.md`.

    Exactly one anonymisation scheme: the text goes through a `PIISession`,
    the same one transcripts go through (module docstring). Supply either a
    live `session` (to keep placeholders consistent across documents) or an
    `engagement_dir` (to resolve the deny-list from the engagement's own
    documents, as `anonymize_transcript_file` does).

    The original file is never modified. A failure raises before anything is
    written — no partial or empty `.anon_` artifact is ever left behind.
    """
    path = Path(path)
    text = extract_text(path)

    # The FILENAME is anonymised too, not just the body: `HDFC_Annual_Report.pdf`
    # names the client in the one line a reader is guaranteed to read. Folding
    # it into the same anonymisation pass means the deny-list catches it.
    document = "# Anonymised extract of `%s` (%s)\n\n%s" % (
        path.name, path.suffix.lower().lstrip("."), text,
    )

    session = _resolve_session(session, engagement_dir, entity_mapping)
    anonymized = session.anonymize(document)

    target = anon_path_for(path, output_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(anonymized, encoding="utf-8")

    return IngestResult(
        source=path,
        anon_path=target,
        fmt=path.suffix.lower().lstrip("."),
        extracted_chars=len(text),
        anonymized_chars=len(anonymized),
        session=session,
    )


def _resolve_session(session, engagement_dir, entity_mapping):
    """Open (or reuse) the ONE session this text is anonymised through.

    `engine` is imported lazily so this module stays importable — and its
    extractors runnable — on plain Python 3.9, where Presidio cannot import
    at all (engine.py's INTERPRETER SPLIT note).
    """
    if session is not None:
        return session
    from . import engine as _engine  # noqa: PLC0415 - lazy by contract
    if engagement_dir is not None:
        return _engine.PIISession.for_engagement(
            engagement_dir, entity_mapping=entity_mapping
        )
    raise ValueError(
        "ingest_file needs either a `session` or an `engagement_dir` — "
        "anonymisation without a resolved deny-list would produce a vacuous "
        "scrub (see engine.py's EMPTY_DENY_LIST_WARNING)."
    )


# --- CLI -------------------------------------------------------------------

def _main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse  # noqa: PLC0415 - CLI only

    parser = argparse.ArgumentParser(
        description="Convert a document to anonymised text (.anon_<name>.md).",
    )
    parser.add_argument("--file", required=True, help="Path to the document")
    parser.add_argument("--engagement-dir", required=True,
                         help="Engagement directory (resolves the client deny-list)")
    parser.add_argument("--output-dir", default=None,
                         help="Where to write the .anon_ file (default: alongside the source)")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        result = ingest_file(
            Path(args.file),
            engagement_dir=Path(args.engagement_dir),
            output_dir=Path(args.output_dir) if args.output_dir else None,
        )
    except IngestError as exc:
        sys.stderr.write("%s\n" % exc.message)
        return 1
    print("Anonymised: %s" % result.anon_path)
    return 0


if __name__ == "__main__":
    sys.exit(_main())
