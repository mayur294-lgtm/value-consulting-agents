#!/usr/bin/env python3
"""
Transcript PII Anonymizer — strips identifying information from client
transcripts before they are sent to the Anthropic API.

Replaces:
  - Client/organization names (from engagement intake)
  - Person names mentioned in transcripts
  - Email addresses
  - Phone numbers
  - Account/member numbers
  - SSNs/Tax IDs
  - URLs containing client domains

Keeps:
  - Business concepts, pain points, processes
  - Financial figures (amounts, percentages) — needed for ROI analysis
  - Product names (Backbase, vendor names)
  - Roles/titles (CIO, VP Digital, etc.)

A mapping file is written alongside the anonymized transcript so outputs
can be de-anonymized later for the final deliverable.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional


# PII regex patterns
_EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
_PHONE_RE = re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
_SSN_RE = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
_ACCOUNT_RE = re.compile(r'\b(?:account|member|acct|ID)[\s#:]*\d{6,}\b', re.IGNORECASE)
_URL_RE = re.compile(r'https?://[^\s)<>]+')

# Generic single-word short forms that are too common to safely redact on
# their own (e.g. "First" in "First Bank") — a single-word client short form
# is only redacted if it is NOT in this stoplist.
_GENERIC_SHORT_NAME_STOPLIST = {
    'bank', 'banking', 'credit', 'union', 'first', 'national', 'federal',
    'united', 'community', 'citizens', 'state', 'financial', 'savings',
    'trust', 'group', 'holdings', 'capital', 'mutual', 'valley', 'coast',
    'pacific',
}


def _next_index_for_category(category: str, *mappings: dict) -> int:
    """Find the highest numbered [CATEGORY-N] placeholder across the given
    mapping dicts and return the next index to allocate (starting at 1).

    Legacy `[CATEGORY-REDACTED]` keys don't parse as numbered placeholders
    and are ignored for numbering purposes (never re-emitted).
    """
    pattern = re.compile(r'^\[' + re.escape(category) + r'-(\d+)\]$')
    max_index = 0
    for mapping in mappings:
        for placeholder in mapping:
            m = pattern.match(placeholder)
            if m:
                max_index = max(max_index, int(m.group(1)))
    return max_index + 1


def _replace_numbered_category(
    result: str,
    values_in_order: list[str],
    category: str,
    shared_mapping: dict,
    new_mapping: dict,
) -> str:
    """Assign numbered placeholders to distinct values (reusing any already
    present in shared_mapping or new_mapping) and replace ALL occurrences of
    each value in `result`. Returns the updated text; `new_mapping` is
    updated in place with reused + newly-allocated entries relevant to this
    text (pruned to exactly what's actually present in the returned text —
    see the substring note below).
    """
    # value -> placeholder, built from existing numbered entries in both maps
    value_to_placeholder = {}
    numbered_re = re.compile(r'^\[' + re.escape(category) + r'-\d+\]$')
    for mapping in (shared_mapping, new_mapping):
        for placeholder, value in mapping.items():
            if numbered_re.match(placeholder):
                value_to_placeholder[value] = placeholder

    # Pass 1: assign placeholder indices in FIRST-APPEARANCE order (this is
    # the numbering semantics — [CAT-1] is whichever distinct value appears
    # first in the text). This does NOT touch `result` yet: index assignment
    # must stay independent of which value happens to be a textual substring
    # of another (e.g. account "5551234" vs "55512345").
    next_idx = _next_index_for_category(category, shared_mapping, new_mapping)
    for value in values_in_order:
        if value not in value_to_placeholder:
            value_to_placeholder[value] = f"[{category}-{next_idx}]"
            next_idx += 1

    # Pass 2: substitute LONGEST value first. A plain first-appearance-order
    # `str.replace` would let a shorter value's blanket replace mangle a
    # longer value that contains it as a substring (e.g. account "5551234"
    # is a substring of "55512345"; a bare phone number can be a substring
    # of one with a country code; a URL can be a prefix of a longer URL),
    # leaving an unreplaced remainder of real PII in the anonymized text.
    # Replacing longest-first consumes the longer occurrence completely
    # before the shorter value's pass runs, so it can only match genuine
    # standalone occurrences of the shorter value.
    for value in sorted(set(values_in_order), key=len, reverse=True):
        placeholder = value_to_placeholder[value]
        result = result.replace(value, placeholder)
        new_mapping[placeholder] = value

    # A value allocated an index in pass 1 may turn out to be entirely
    # consumed as a substring of a longer value already replaced in pass 2
    # (no standalone occurrence survives) — its placeholder never actually
    # appears in `result`. Keep the mapping exactly one-to-one with what's
    # in the text: drop any such dead entry.
    for value in values_in_order:
        placeholder = value_to_placeholder[value]
        if placeholder in new_mapping and placeholder not in result:
            del new_mapping[placeholder]

    return result


def _load_entity_names(intake_path: Path) -> list[str]:
    """Extract organization and person names from engagement intake."""
    names = []
    if not intake_path.exists():
        return names

    content = intake_path.read_text()

    # Extract client/organization name from common intake patterns
    for pattern in [
        r'(?:Client|Organization|Institution|Bank|Credit Union|Company)\s*:\s*(.+)',
        r'(?:client_name|org_name)\s*:\s*(.+)',
    ]:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            name = match.group(1).strip().strip('"\'')
            if name and len(name) > 2:
                names.append(name)

    # Extract stakeholder names
    for pattern in [
        r'(?:Name|Contact|Stakeholder|Attendee)\s*:\s*([A-Z][a-z]+ [A-Z][a-z]+)',
        r'(?:with|from|by)\s+([A-Z][a-z]+ [A-Z][a-z]+)\s*(?:,|\(|—|-)',
    ]:
        for match in re.finditer(pattern, content):
            name = match.group(1).strip()
            if name and len(name) > 3:
                names.append(name)

    return list(set(names))


def _load_context_file(context_path: Path) -> list[str]:
    """Extract additional entity names from ENGAGEMENT_CONTEXT.md."""
    names = []
    if not context_path.exists():
        return names

    content = context_path.read_text()
    for pattern in [
        r'(?:Client|Organization)\s*:\s*(.+)',
        r'(?:Key Stakeholders|Participants).*?\n((?:[-*]\s+.+\n)+)',
    ]:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            text = match.group(1).strip()
            # If it's a list block, extract individual names
            if '\n' in text:
                for line in text.split('\n'):
                    line = re.sub(r'^[-*]\s+', '', line).strip()
                    name_match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+)', line)
                    if name_match:
                        names.append(name_match.group(1))
            else:
                if len(text) > 2:
                    names.append(text.strip('"\''))

    return list(set(names))


def anonymize_text(
    text: str,
    entity_names: list[str],
    client_label: str = "[CLIENT]",
    shared_mapping: Optional[dict] = None,
) -> tuple[str, dict]:
    """Anonymize PII in text. Returns (anonymized_text, mapping).

    The mapping dict can be used to de-anonymize outputs later.

    `shared_mapping` is an optional read-only `{placeholder: value}` map
    accumulated from prior transcripts in the same run. When provided,
    already-seen values reuse their existing numbered placeholder and
    per-category numbering continues past the highest existing index,
    so mappings from multiple transcripts can be merged without collisions.
    The returned mapping contains only the entries relevant to THIS text
    (reused + newly allocated), so it de-anonymizes this transcript
    standalone.
    """
    if shared_mapping is None:
        shared_mapping = {}
    mapping = {}
    result = text

    # 1. Replace known entity names (longest first to avoid partial matches)
    sorted_names = sorted(entity_names, key=len, reverse=True)
    for i, name in enumerate(sorted_names):
        if not name or len(name) < 3:
            continue
        # Determine placeholder
        if i == 0:
            placeholder = client_label
        else:
            placeholder = f"[PERSON-{i}]"

        # Case-insensitive replacement
        pattern = re.compile(re.escape(name), re.IGNORECASE)
        if pattern.search(result):
            mapping[placeholder] = name
            result = pattern.sub(placeholder, result)

        # For the client org name: also replace acronyms and common short forms
        # Use distinct placeholders so de-anonymization restores the original form
        if i == 0:
            words = name.split()
            if len(words) >= 2:
                # Acronym (e.g., "NFCU" for "Navy Federal Credit Union")
                acronym = ''.join(w[0].upper() for w in words if w[0].isupper() or len(w) > 3)
                if len(acronym) >= 2:
                    acr_placeholder = "[CLIENT-ABBR]"
                    acr_pattern = re.compile(r'\b' + re.escape(acronym) + r'\b')
                    if acr_pattern.search(result):
                        mapping[acr_placeholder] = acronym
                        result = acr_pattern.sub(acr_placeholder, result)

                # Partial name variants — drop common suffixes and try shorter forms
                # e.g., "Navy Federal Credit Union" → also match "Navy Federal"
                name_lower = name.lower()
                multi_suffixes = ['credit union', 'savings bank', 'mutual bank',
                                  'financial group', 'financial services']
                single_suffixes = ['bank', 'corporation', 'corp', 'inc',
                                   'limited', 'ltd', 'group', 'holdings',
                                   'financial', 'services', 'bancorp',
                                   'bancshares', 'co', 'plc', 'sa', 'ag']

                short_name = name
                # First strip multi-word suffixes
                for suffix in multi_suffixes:
                    if name_lower.endswith(suffix):
                        short_name = name[:-(len(suffix))].strip()
                        break
                else:
                    # Then try single-word suffixes
                    for suffix in single_suffixes:
                        if words[-1].lower() == suffix:
                            short_name = ' '.join(words[:-1])
                            break

                short_words = short_name.split()
                is_distinctive_single_word = (
                    len(short_words) == 1
                    and len(short_words[0]) >= 4
                    and short_words[0].lower() not in _GENERIC_SHORT_NAME_STOPLIST
                )
                if short_name != name and (len(short_words) >= 2 or is_distinctive_single_word):
                    short_placeholder = "[CLIENT-SHORT]"
                    if len(short_words) >= 2:
                        # Multi-word short form — unchanged behavior.
                        short_pattern = re.compile(re.escape(short_name), re.IGNORECASE)
                    else:
                        # Single-word short form — word-boundary match so it
                        # doesn't clobber substrings (e.g. "Zenithal").
                        short_pattern = re.compile(r'\b' + re.escape(short_name) + r'\b', re.IGNORECASE)
                    if short_pattern.search(result):
                        mapping[short_placeholder] = short_name
                        result = short_pattern.sub(short_placeholder, result)

    # 2. Replace emails
    emails = list(dict.fromkeys(m.group(0) for m in _EMAIL_RE.finditer(result)))
    result = _replace_numbered_category(result, emails, "EMAIL", shared_mapping, mapping)

    # 3. Replace phone numbers
    phones = list(dict.fromkeys(m.group(0) for m in _PHONE_RE.finditer(result)))
    result = _replace_numbered_category(result, phones, "PHONE", shared_mapping, mapping)

    # 4. Replace SSNs / Tax IDs
    ssns = list(dict.fromkeys(m.group(0) for m in _SSN_RE.finditer(result)))
    result = _replace_numbered_category(result, ssns, "SSN", shared_mapping, mapping)

    # 5. Replace account/member numbers
    accounts = list(dict.fromkeys(m.group(0) for m in _ACCOUNT_RE.finditer(result)))
    result = _replace_numbered_category(result, accounts, "ACCOUNT", shared_mapping, mapping)

    # 6. Replace URLs that contain client domain names
    client_urls = []
    for match in _URL_RE.finditer(result):
        url = match.group(0)
        # Check if URL contains any entity name
        url_lower = url.lower()
        for name in entity_names:
            name_parts = name.lower().split()
            if any(part in url_lower for part in name_parts if len(part) > 3):
                client_urls.append(url)
                break
    client_urls = list(dict.fromkeys(client_urls))
    result = _replace_numbered_category(result, client_urls, "CLIENT-URL", shared_mapping, mapping)

    return result, mapping


def anonymize_transcript_file(
    transcript_path: Path,
    engagement_dir: Path,
    output_dir: Optional[Path] = None,
    shared_mapping: Optional[dict] = None,
) -> tuple[Path, Path]:
    """Anonymize a transcript file in-place (or to output_dir).

    `shared_mapping` is an optional read-only `{placeholder: value}` map
    accumulated from prior transcripts in the same run — see `anonymize_text`.

    Returns (anonymized_transcript_path, mapping_path).
    """
    # Collect entity names from intake and context files
    entity_names = []
    entity_names.extend(_load_entity_names(engagement_dir / "inputs" / "engagement_intake.md"))
    entity_names.extend(_load_context_file(engagement_dir / "ENGAGEMENT_CONTEXT.md"))
    entity_names = list(set(entity_names))

    if not entity_names:
        # No names found — still strip generic PII (emails, phones, SSNs),
        # but warn loudly since client/person names will reach the API
        # in plaintext.
        print(
            "⚠ No client/person names found in inputs/engagement_intake.md or "
            "ENGAGEMENT_CONTEXT.md — only generic PII (emails, phones, SSNs, "
            "accounts) was stripped. Client and person names may reach the "
            "API in plaintext. Check inputs/engagement_intake.md.",
            file=sys.stderr,
        )

    # Read transcript
    original_text = transcript_path.read_text()

    # Anonymize
    anonymized_text, mapping = anonymize_text(
        original_text, entity_names, shared_mapping=shared_mapping
    )

    # Determine output paths
    if output_dir is None:
        output_dir = transcript_path.parent

    anon_path = output_dir / f".anon_{transcript_path.name}"
    mapping_path = output_dir / f".anon_mapping_{transcript_path.stem}.json"

    # Write anonymized transcript
    anon_path.write_text(anonymized_text)

    # Write mapping (for de-anonymization of final outputs)
    mapping_path.write_text(json.dumps(mapping, indent=2))
    mapping_path.chmod(0o600)  # Restrict access — this file contains PII

    return anon_path, mapping_path


def deanonymize_text(text: str, mapping: dict) -> str:
    """Restore original names/PII from anonymized text using the mapping."""
    result = text
    # Replace longest placeholders first to avoid partial matches
    for placeholder in sorted(mapping.keys(), key=len, reverse=True):
        result = result.replace(placeholder, mapping[placeholder])
    return result


def deanonymize_file(file_path: Path, mapping_path: Path) -> str:
    """De-anonymize a file using a mapping file. Returns de-anonymized text."""
    mapping = json.loads(mapping_path.read_text())
    text = file_path.read_text()
    return deanonymize_text(text, mapping)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Anonymize transcript PII')
    parser.add_argument('--file', required=True, help='Path to transcript file')
    parser.add_argument('--engagement-dir', required=True, help='Path to engagement directory')
    parser.add_argument('--deanonymize', action='store_true', help='De-anonymize a file instead')
    parser.add_argument('--mapping', help='Path to mapping file (for --deanonymize)')
    args = parser.parse_args()

    if args.deanonymize:
        if not args.mapping:
            print('Error: --mapping required for --deanonymize', file=sys.stderr)
            sys.exit(1)
        result = deanonymize_file(Path(args.file), Path(args.mapping))
        print(result)
    else:
        anon_path, mapping_path = anonymize_transcript_file(
            Path(args.file), Path(args.engagement_dir)
        )
        print(f'Anonymized: {anon_path}')
        print(f'Mapping: {mapping_path}')
