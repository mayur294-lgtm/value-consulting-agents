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
    """Extract engagement summary metadata from journal."""
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

    payload = {
        'extracted_at': datetime.utcnow().isoformat() + 'Z',
        'journal_path': journal_path,
        'session_id': extract_session_id(engagement_dir),
        'engagement': extract_engagement_metadata(content),
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
