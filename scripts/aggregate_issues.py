#!/usr/bin/env python3
"""
Flywheel Triage Agent: Aggregate and deduplicate telemetry issues.

Reads telemetry GitHub Issues, groups similar problems by keyword matching,
scores by frequency x severity x recency, and outputs prioritized canonical issues.

This runs as part of the weekly triage GitHub Action.

Usage:
    python aggregate_issues.py --repo OWNER/REPO [--output aggregated.json] [--dry-run]
"""

import json
import subprocess
import sys
import re
from datetime import datetime, timedelta
from collections import defaultdict


SEVERITY_WEIGHTS = {
    'critical': 10,
    'high': 5,
    'moderate': 2,
    'low': 1,
}


def fetch_telemetry_issues(repo: str) -> list:
    """Fetch all open telemetry issues from GitHub."""
    result = subprocess.run(
        ['gh', 'issue', 'list',
         '--repo', repo,
         '--label', 'telemetry',
         '--state', 'open',
         '--limit', '100',
         '--json', 'number,title,body,createdAt,labels'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f'Error fetching issues: {result.stderr}', file=sys.stderr)
        return []

    return json.loads(result.stdout)


def parse_telemetry_from_issue(issue: dict) -> dict:
    """Parse structured telemetry data from issue body."""
    body = issue.get('body', '')
    data = {
        'issue_number': issue['number'],
        'title': issue['title'],
        'created_at': issue['createdAt'],
        'agent_entries': [],
        'modifications': [],
        'issues_found': [],
    }

    # Try to extract JSON from collapsed section
    json_match = re.search(r'```json\n([\s\S]*?)\n```', body)
    if json_match:
        try:
            raw = json.loads(json_match.group(1))
            if isinstance(raw, list):
                for entry in raw:
                    data['agent_entries'].extend(entry.get('telemetry_entries', []))
                    data['modifications'].extend(entry.get('modifications', []))
            elif isinstance(raw, dict):
                data['agent_entries'] = raw.get('telemetry_entries', [])
                data['modifications'] = raw.get('modifications', [])
        except json.JSONDecodeError:
            pass

    # Extract issues from markdown list
    issue_pattern = r'\d+\.\s+\*\*\[(\w+)\]\*\*\s+`([^`]+)`\s+[—–-]\s+(.+)'
    for match in re.finditer(issue_pattern, body):
        data['issues_found'].append({
            'severity': match.group(1).lower(),
            'agent': match.group(2),
            'description': match.group(3).strip(),
        })

    return data


def extract_actionable_issues(parsed_issues: list) -> list:
    """Extract all individual actionable items from parsed telemetry."""
    items = []

    for parsed in parsed_issues:
        created_at = parsed['created_at']

        # From explicit issues
        for issue in parsed.get('issues_found', []):
            items.append({
                'agent': issue.get('agent', 'unknown'),
                'description': issue.get('description', ''),
                'severity': issue.get('severity', 'moderate'),
                'source_issue': parsed['issue_number'],
                'created_at': created_at,
            })

        # From modifications (consultant had to fix something)
        for mod in parsed.get('modifications', []):
            items.append({
                'agent': mod.get('agent', 'unknown'),
                'description': mod.get('reason', 'Manual modification required'),
                'severity': mod.get('severity', 'moderate'),
                'source_issue': parsed['issue_number'],
                'created_at': created_at,
                'time_spent': mod.get('duration', 'unknown'),
            })

        # From agent errors
        for entry in parsed.get('agent_entries', []):
            errors = entry.get('errors_encountered', 'none')
            if errors != 'none':
                items.append({
                    'agent': entry.get('agent', 'unknown'),
                    'description': errors,
                    'severity': 'high',
                    'source_issue': parsed['issue_number'],
                    'created_at': created_at,
                })

    return items


def generate_group_key(item: dict) -> str:
    """Generate a grouping key for deduplication."""
    agent = item.get('agent', 'unknown').lower().strip()
    desc = item.get('description', '').lower().strip()

    # Extract key terms (first 5 meaningful words)
    stop_words = {'the', 'a', 'an', 'is', 'was', 'were', 'to', 'for', 'of', 'in',
                  'on', 'at', 'and', 'or', 'but', 'not', 'with', 'had', 'has', 'have'}
    words = [w for w in re.findall(r'\w+', desc) if w not in stop_words][:5]

    return f'{agent}|{"|".join(words)}'


def deduplicate_and_score(items: list) -> list:
    """Group similar items and compute priority scores."""
    groups = defaultdict(list)

    for item in items:
        key = generate_group_key(item)
        groups[key].append(item)

    now = datetime.utcnow()
    canonical_issues = []

    for key, group in groups.items():
        # Use the first item as representative
        representative = group[0]

        # Calculate recency bonus
        recency_scores = []
        for item in group:
            try:
                created = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                age_days = (now - created.replace(tzinfo=None)).days
                if age_days <= 7:
                    recency_scores.append(1.5)
                elif age_days <= 30:
                    recency_scores.append(1.0)
                else:
                    recency_scores.append(0.5)
            except (ValueError, TypeError):
                recency_scores.append(1.0)

        avg_recency = sum(recency_scores) / len(recency_scores) if recency_scores else 1.0

        # Get severity weight
        severities = [item.get('severity', 'moderate') for item in group]
        max_severity = max(severities, key=lambda s: SEVERITY_WEIGHTS.get(s, 1))
        severity_weight = SEVERITY_WEIGHTS.get(max_severity, 1)

        # Calculate priority
        occurrence_count = len(group)
        priority_score = occurrence_count * severity_weight * avg_recency

        # Compute total consultant time wasted
        total_time = 0
        for item in group:
            time_str = str(item.get('time_spent', '0'))
            try:
                total_time += int(re.search(r'\d+', time_str).group())
            except (AttributeError, ValueError):
                pass

        canonical_issues.append({
            'title': f'{representative["agent"]} — {representative["description"][:80]}',
            'agent': representative['agent'],
            'description': representative['description'],
            'severity': max_severity,
            'occurrence_count': occurrence_count,
            'priority_score': round(priority_score, 1),
            'source_issues': list(set(item['source_issue'] for item in group)),
            'total_consultant_minutes': total_time,
            'group_key': key,
        })

    # Sort by priority (highest first)
    canonical_issues.sort(key=lambda x: x['priority_score'], reverse=True)
    return canonical_issues


def create_improvement_issue(repo: str, canonical: dict, dry_run: bool = False) -> str:
    """Create a GitHub Issue for a prioritized improvement item."""
    title = f'[Improvement] {canonical["title"]}'

    body = f"""## Problem

**Agent:** `{canonical['agent']}`
**Severity:** {canonical['severity'].upper()}
**Occurrences:** {canonical['occurrence_count']} reports across consultants
**Consultant time wasted:** {canonical['total_consultant_minutes']} minutes total
**Priority Score:** {canonical['priority_score']}

### Description

{canonical['description']}

### Evidence

Reported in telemetry issues: {', '.join(f'#{n}' for n in canonical['source_issues'])}

## Suggested Action

Analyze the `{canonical['agent']}` agent definition and related knowledge/template files to address this issue.

---
_Auto-generated by the Flywheel Triage Agent_
"""

    labels = f'improvement,{canonical["severity"]},{canonical["agent"]}'

    if dry_run:
        print(f'[DRY RUN] Would create issue: {title}')
        print(f'  Labels: {labels}')
        print(f'  Priority: {canonical["priority_score"]}')
        return 'dry-run'

    result = subprocess.run(
        ['gh', 'issue', 'create',
         '--repo', repo,
         '--title', title,
         '--label', labels,
         '--body', body],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        url = result.stdout.strip()
        print(f'Created: {url}')
        return url
    else:
        print(f'Error creating issue: {result.stderr}', file=sys.stderr)
        return ''


def label_for_dev(repo: str, issue_url: str, dry_run: bool = False):
    """Add 'ready-for-dev' label to trigger the Dev Agent."""
    if dry_run:
        print(f'[DRY RUN] Would label {issue_url} as ready-for-dev')
        return

    # Extract issue number from URL
    issue_number = issue_url.rstrip('/').split('/')[-1]

    subprocess.run(
        ['gh', 'issue', 'edit', issue_number,
         '--repo', repo,
         '--add-label', 'ready-for-dev'],
        capture_output=True, text=True
    )


def close_processed_telemetry(repo: str, issue_numbers: list, dry_run: bool = False):
    """Close telemetry issues that have been processed."""
    for num in issue_numbers:
        if dry_run:
            print(f'[DRY RUN] Would close telemetry issue #{num}')
            continue

        subprocess.run(
            ['gh', 'issue', 'close', str(num),
             '--repo', repo,
             '--comment', 'Processed by Flywheel Triage Agent. Issues extracted and prioritized.'],
            capture_output=True, text=True
        )


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Flywheel Triage Agent')
    parser.add_argument('--repo', required=True, help='GitHub repo (OWNER/REPO)')
    parser.add_argument('--output', help='Output JSON file for aggregated issues')
    parser.add_argument('--dry-run', action='store_true', help='Preview without creating issues')
    parser.add_argument('--max-issues', type=int, default=3, help='Max improvement issues to create per run')
    args = parser.parse_args()

    print(f'Fetching telemetry issues from {args.repo}...')
    raw_issues = fetch_telemetry_issues(args.repo)
    print(f'Found {len(raw_issues)} telemetry issues')

    if not raw_issues:
        print('No telemetry issues to process.')
        return

    # Parse telemetry from each issue
    parsed = [parse_telemetry_from_issue(issue) for issue in raw_issues]

    # Extract actionable items
    items = extract_actionable_issues(parsed)
    print(f'Extracted {len(items)} actionable items')

    if not items:
        print('No actionable items found.')
        return

    # Deduplicate and score
    canonical = deduplicate_and_score(items)
    print(f'Grouped into {len(canonical)} canonical issues')

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(canonical, f, indent=2)
        print(f'Aggregated issues written to {args.output}')

    # Print priority list
    print('\n=== Priority Ranking ===')
    for i, issue in enumerate(canonical, 1):
        print(f'{i}. [{issue["severity"].upper()}] (score={issue["priority_score"]}) '
              f'{issue["agent"]} — {issue["description"][:60]}...')

    # Create improvement issues for top items
    print(f'\nCreating top {args.max_issues} improvement issues...')
    created_urls = []
    for issue in canonical[:args.max_issues]:
        url = create_improvement_issue(args.repo, issue, dry_run=args.dry_run)
        if url:
            created_urls.append(url)

    # Label the #1 issue as ready-for-dev (triggers Dev Agent)
    if created_urls and created_urls[0] != 'dry-run':
        label_for_dev(args.repo, created_urls[0], dry_run=args.dry_run)

    # Close processed telemetry issues
    all_source_issues = set()
    for issue in canonical:
        all_source_issues.update(issue['source_issues'])
    close_processed_telemetry(args.repo, list(all_source_issues), dry_run=args.dry_run)

    print('\nTriage complete.')


if __name__ == '__main__':
    main()
