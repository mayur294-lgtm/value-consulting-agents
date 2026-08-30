#!/usr/bin/env python3
"""
Extract structured telemetry data from engagement journals.

Parses TELEMETRY_START/END and MODIFICATION_LOG blocks from
ENGAGEMENT_JOURNAL.md files and outputs structured JSON.

Usage:
    python extract_telemetry.py <journal_path> [--output <json_path>]
"""

import sys
import re
import json
import os
from datetime import datetime


def extract_telemetry_blocks(content: str) -> list:
    """Extract all telemetry blocks from journal content."""
    pattern = r'<!-- TELEMETRY_START -->\n(.*?)\n<!-- TELEMETRY_END -->'
    matches = re.finditer(pattern, content, re.DOTALL)

    entries = []
    for match in matches:
        block = match.group(1)
        entry = {}
        for line in block.strip().split('\n'):
            line = line.strip()
            if line.startswith('- ') and ':' in line:
                line = line[2:]
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                # Parse numeric values
                if value.isdigit():
                    value = int(value)
                entry[key] = value
        if entry:
            entries.append(entry)

    return entries


def extract_modification_logs(content: str) -> list:
    """Extract all modification logs from journal content."""
    pattern = r'<!-- MODIFICATION_LOG -->\n(.*?)\n<!-- END_MODIFICATION_LOG -->'
    matches = re.finditer(pattern, content, re.DOTALL)

    modifications = []
    for match in matches:
        block = match.group(1)
        entry = {}
        for line in block.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                if value.isdigit():
                    value = int(value)
                entry[key] = value
        if entry:
            modifications.append(entry)

    return modifications


def extract_engagement_metadata(content: str) -> dict:
    """Extract engagement summary metadata from journal.

    `client` is captured here (from the journal's `**Client:**` line) only
    long enough for `_client_label` below to turn it into the same
    descriptive, non-identifying label `knowledge-harvester.md` Core Rule 2
    uses — `[Client-{domain}-{REGION}-{year}-{disc}]`. The raw value returned by
    this function must never itself be written to `.telemetry_cache.jsonl`
    or a GitHub Issue; see `extract_telemetry()`, which does that
    replacement before the payload is returned (ticket #169 — this backs
    sync-telemetry.md's "telemetry is anonymized" claim, which previously
    had nothing enforcing it)."""
    metadata = {}

    patterns = {
        'client': r'\*\*Client:\*\*\s*(.+)',
        'domain': r'\*\*Domain:\*\*\s*(.+)',
        'region': r'\*\*Region:\*\*\s*(.+)',
        'engagement_type': r'\*\*Engagement Type:\*\*\s*(.+)',
        'started': r'\*\*Started:\*\*\s*(.+)',
        'status': r'\*\*Current Status:\*\*\s*(.+)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            metadata[key] = match.group(1).strip()

    return metadata


def _client_label(metadata: dict, extracted_at_iso: str,
                  engagement_dir: str = "") -> str:
    """Build the descriptive, non-identifying replacement for a raw client
    name. Delegates to `pii.identity.client_label` — the SINGLE definition of
    this convention, shared with `.claude/agents/knowledge-harvester.md` Core
    Rule 2. Telemetry leaves this machine (synced to a shared GitHub issue via
    `/sync-telemetry` or the `post-commit`/`pre-push` git hooks), so the raw
    client string must never reach the payload this function's caller writes.

    `domain`/`region` come from the same journal metadata already extracted
    (never PII on their own). `year` is parsed from `**Started:**` when
    present (`YYYY-...`), falling back to the extraction timestamp's year so
    this never raises on a journal missing that field.

    D1 (`.design/knowledge-identity-resolution.md`): the label now carries a
    DISCRIMINATOR taken from the engagement's opaque ID, because
    domain+region+year alone is many-to-one and silently merged two banks into
    one apparent peer. `engagement_dir` is how the ID is resolved; when it
    cannot be (a legacy client-named directory), the label is emitted
    undiscriminated and a warning goes to stderr. It is NEVER derived from the
    client's name — see `identity.client_label`.

    Fails soft: if `pii.identity` cannot be imported at all, this still
    returns a name-free label rather than raising inside a git hook. The
    privacy property holds either way; only the discriminator is lost.
    """
    domain = metadata.get('domain') or 'unknown'
    region = metadata.get('region') or 'unknown'
    started = metadata.get('started') or ''
    year_match = re.match(r'(20\d{2})', started)
    year = year_match.group(1) if year_match else extracted_at_iso[:4]

    try:
        from pii import identity
    except ImportError as exc:  # pragma: no cover - defensive, hook path
        print("warning: pii.identity unavailable (%s); emitting an "
              "UNDISCRIMINATED client label, which may collide with another "
              "engagement in the same domain/region/year." % exc,
              file=sys.stderr)
        return '[Client-%s-%s-%s]' % (
            re.sub(r'[^A-Za-z0-9]+', '', domain).lower() or 'unknown',
            re.sub(r'[^A-Za-z0-9]+', '', region).upper() or 'UNKNOWN',
            year,
        )

    engagement_id = identity.engagement_id_for_path(engagement_dir) if engagement_dir else None
    if engagement_id is None:
        print("warning: no opaque engagement ID resolved from %r — emitting an "
              "UNDISCRIMINATED client label, which may collide with another "
              "engagement in the same domain/region/year. Migrate the "
              "engagement with scripts/migrate_engagement_ids.sh to fix."
              % (engagement_dir or "<no path>"), file=sys.stderr)
    return identity.client_label(domain, region, year, engagement_id)


def extract_session_id(engagement_dir: str) -> str:
    """Read session ID from .engagement_session_id file."""
    session_file = os.path.join(engagement_dir, '.engagement_session_id')
    if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            return f.read().strip()
    return 'unknown'


def extract_telemetry(journal_path: str) -> dict:
    """Full telemetry extraction from a journal file."""
    with open(journal_path, 'r') as f:
        content = f.read()

    engagement_dir = os.path.dirname(journal_path)
    extracted_at = datetime.utcnow().isoformat() + 'Z'
    engagement_metadata = extract_engagement_metadata(content)

    # Never let the raw client name leave this machine in the telemetry
    # payload — replace it with the same descriptive label the knowledge
    # harvester uses. See `_client_label` above and PRD v6 §3.1 /
    # sync-telemetry.md.
    if engagement_metadata.get('client'):
        engagement_metadata['client'] = _client_label(
            engagement_metadata, extracted_at, engagement_dir)

    payload = {
        'extracted_at': extracted_at,
        'journal_path': journal_path,
        'session_id': extract_session_id(engagement_dir),
        'engagement': engagement_metadata,
        'telemetry_entries': extract_telemetry_blocks(content),
        'modifications': extract_modification_logs(content),
    }

    # Compute summary stats
    entries = payload['telemetry_entries']
    if entries:
        durations = [e.get('duration', 0) for e in entries if isinstance(e.get('duration'), int)]
        payload['summary'] = {
            'total_agents_run': len(entries),
            'total_duration_seconds': sum(durations),
            'agents_with_errors': sum(1 for e in entries if e.get('errors_encountered', 'none') != 'none'),
            'total_modifications': len(payload['modifications']),
        }

    return payload


def main():
    if len(sys.argv) < 2:
        print('Usage: python extract_telemetry.py <journal_path> [--output <json_path>]')
        sys.exit(1)

    journal_path = sys.argv[1]

    if not os.path.exists(journal_path):
        print(f'Error: File not found: {journal_path}')
        sys.exit(1)

    telemetry = extract_telemetry(journal_path)

    # Output
    output_path = None
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    json_str = json.dumps(telemetry, indent=2)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(json_str)
        print(f'Telemetry extracted to {output_path}')
    else:
        print(json_str)


if __name__ == '__main__':
    main()
