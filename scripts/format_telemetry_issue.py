#!/usr/bin/env python3
"""
Format telemetry data as a GitHub Issue body.

Reads JSONL telemetry entries from stdin or file and produces
a well-formatted GitHub Issue body in markdown.

Usage:
    cat .telemetry_cache.jsonl | python format_telemetry_issue.py
    python format_telemetry_issue.py --input .telemetry_cache.jsonl
"""

import sys
import json
from datetime import datetime


def format_agent_table(entries: list) -> str:
    """Format telemetry entries as a markdown table."""
    if not entries:
        return '_No agent telemetry recorded._'

    rows = []
    rows.append('| Agent | Duration | Errors | Quality Check |')
    rows.append('|-------|----------|--------|---------------|')

    for entry in entries:
        agent = entry.get('agent', 'unknown')
        duration = entry.get('duration', 'N/A')
        if isinstance(duration, int):
            mins = duration // 60
            secs = duration % 60
            duration = f'{mins}m {secs}s' if mins > 0 else f'{secs}s'
        errors = entry.get('errors_encountered', 'none')
        quality = entry.get('quality_self-check', entry.get('quality_self_check', 'N/A'))
        rows.append(f'| {agent} | {duration} | {errors} | {quality} |')

    return '\n'.join(rows)


def format_modifications_table(modifications: list) -> str:
    """Format modification logs as a markdown table."""
    if not modifications:
        return '_No manual modifications logged._'

    rows = []
    rows.append('| Agent | File | Reason | Time Spent | Severity |')
    rows.append('|-------|------|--------|------------|----------|')

    for mod in modifications:
        agent = mod.get('agent', 'unknown')
        file = mod.get('file', 'N/A')
        reason = mod.get('reason', 'N/A')
        duration = mod.get('duration', 'N/A')
        severity = mod.get('severity', 'N/A')
        rows.append(f'| {agent} | {file} | {reason} | {duration} | {severity} |')

    return '\n'.join(rows)


def extract_issues(telemetry: dict) -> list:
    """Extract actionable issues from telemetry."""
    issues = []

    # Issues from agent errors
    for entry in telemetry.get('telemetry_entries', []):
        errors = entry.get('errors_encountered', 'none')
        if errors != 'none':
            issues.append({
                'type': 'agent_error',
                'agent': entry.get('agent', 'unknown'),
                'description': errors,
                'severity': 'high',
            })

    # Issues from modifications
    for mod in telemetry.get('modifications', []):
        issues.append({
            'type': 'manual_modification',
            'agent': mod.get('agent', 'unknown'),
            'description': mod.get('reason', 'Unknown reason'),
            'severity': mod.get('severity', 'moderate'),
            'time_spent': mod.get('duration', 'N/A'),
        })

    return issues


def format_issue_body(telemetry_entries: list) -> str:
    """Format all telemetry entries as a single GitHub Issue body."""
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

    # Combine all entries
    all_agent_entries = []
    all_modifications = []
    all_issues = []
    engagement_info = {}

    for telemetry in telemetry_entries:
        all_agent_entries.extend(telemetry.get('telemetry_entries', []))
        all_modifications.extend(telemetry.get('modifications', []))
        all_issues.extend(extract_issues(telemetry))
        if telemetry.get('engagement'):
            engagement_info = telemetry['engagement']

    # Build issue body
    body = f'## Telemetry Report — {now}\n\n'

    # Engagement context
    if engagement_info:
        domain = engagement_info.get('domain', 'N/A')
        region = engagement_info.get('region', 'N/A')
        eng_type = engagement_info.get('engagement_type', 'N/A')
        body += f'**Domain:** {domain} | **Region:** {region} | **Type:** {eng_type}\n\n'

    # Summary stats
    total_agents = len(all_agent_entries)
    total_errors = sum(1 for e in all_agent_entries if e.get('errors_encountered', 'none') != 'none')
    total_mods = len(all_modifications)
    body += f'**Agents run:** {total_agents} | **Errors:** {total_errors} | **Manual modifications:** {total_mods}\n\n'

    # Agent performance table
    body += '### Agent Performance\n\n'
    body += format_agent_table(all_agent_entries) + '\n\n'

    # Modifications table
    if all_modifications:
        body += '### Manual Modifications\n\n'
        body += format_modifications_table(all_modifications) + '\n\n'

    # Extracted issues
    if all_issues:
        body += '### Issues Identified\n\n'
        for i, issue in enumerate(all_issues, 1):
            severity_emoji = {'high': '!', 'moderate': '~', 'low': '.'}
            sev = issue.get('severity', 'moderate')
            body += f'{i}. **[{sev.upper()}]** `{issue["agent"]}` — {issue["description"]}\n'
        body += '\n'

    # Raw JSON in collapsed section
    body += '<details>\n<summary>Raw Telemetry JSON</summary>\n\n```json\n'
    body += json.dumps(telemetry_entries, indent=2)
    body += '\n```\n</details>\n'

    return body


def main():
    # Read from stdin or file
    if '--input' in sys.argv:
        idx = sys.argv.index('--input')
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1], 'r') as f:
                lines = f.readlines()
        else:
            print('Error: --input requires a file path')
            sys.exit(1)
    else:
        lines = sys.stdin.readlines()

    # Parse JSONL
    entries = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        print('No telemetry entries found.')
        sys.exit(1)

    print(format_issue_body(entries))


if __name__ == '__main__':
    main()
