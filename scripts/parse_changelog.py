#!/usr/bin/env python3
"""
Parse CHANGELOG.md and extract entries for a specific version.

Outputs JSON suitable for the release notes email template.

Usage:
    python parse_changelog.py v1.2.0 > release_data.json
    python parse_changelog.py v1.2.0 --output release_data.json
"""

import sys
import re
import json
import argparse
from datetime import datetime
from pathlib import Path


def parse_changelog(version: str, changelog_path: str = 'CHANGELOG.md') -> dict:
    """Parse CHANGELOG.md and extract entries for a version."""
    content = Path(changelog_path).read_text()

    # Normalize version (remove 'v' prefix for matching)
    version_clean = version.lstrip('v')

    # Find section for this version
    # Match patterns like: ## [1.2.0] - 2026-02-08 or ## [v1.2.0] or ## 1.2.0
    patterns = [
        rf'## \[v?{re.escape(version_clean)}\][^\n]*\n(.*?)(?=\n## |\Z)',
        rf'## v?{re.escape(version_clean)}[^\n]*\n(.*?)(?=\n## |\Z)',
    ]

    section = ''
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section = match.group(1)
            break

    if not section:
        return {
            'version': version_clean,
            'release_date': datetime.now().strftime('%B %d, %Y'),
            'new_features': [],
            'improvements': [],
            'bug_fixes': [],
            'changelog_url': '',
        }

    # Extract subsections
    new_features = extract_items(section, r'### (?:New Features|Added)\n(.*?)(?=\n### |\Z)')
    improvements = extract_items(section, r'### (?:Improvements|Changed|Enhanced)\n(.*?)(?=\n### |\Z)')
    bug_fixes = extract_items(section, r'### (?:Bug Fixes|Fixed)\n(.*?)(?=\n### |\Z)')

    # If no subsections found, try to categorize all items
    if not new_features and not improvements and not bug_fixes:
        all_items = extract_items(section, r'(- .+(?:\n  .+)*)')
        # Simple categorization: items with "add" = feature, "fix" = bug fix, else = improvement
        for item in all_items:
            title_lower = item['title'].lower()
            if any(w in title_lower for w in ['add', 'new', 'introduce', 'create']):
                new_features.append(item)
            elif any(w in title_lower for w in ['fix', 'resolve', 'correct', 'patch']):
                bug_fixes.append(item)
            else:
                improvements.append(item)

    return {
        'version': version_clean,
        'release_date': datetime.now().strftime('%B %d, %Y'),
        'new_features': new_features,
        'improvements': improvements,
        'bug_fixes': bug_fixes,
        'changelog_url': f'https://github.com/backbase/valueconsulting/blob/main/CHANGELOG.md',
    }


def extract_items(text: str, pattern: str) -> list:
    """Extract bullet point items from a section."""
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []

    items_text = match.group(1) if match.lastindex else match.group(0)
    items = []

    for line in items_text.strip().split('\n'):
        line = line.strip()
        if line.startswith('- '):
            item_text = line[2:].strip()

            # Try to split "Title: Description" or "Title - Description"
            for separator in [':', ' — ', ' - ']:
                if separator in item_text:
                    parts = item_text.split(separator, 1)
                    items.append({
                        'title': parts[0].strip(),
                        'description': parts[1].strip(),
                    })
                    break
            else:
                # No separator found — use full text as title
                items.append({
                    'title': item_text,
                    'description': '',
                })

    return items


def main():
    parser = argparse.ArgumentParser(description='Parse CHANGELOG.md for release notes')
    parser.add_argument('version', help='Version to extract (e.g., v1.2.0)')
    parser.add_argument('--changelog', default='CHANGELOG.md', help='Path to CHANGELOG.md')
    parser.add_argument('--output', help='Output JSON file')
    args = parser.parse_args()

    data = parse_changelog(args.version, args.changelog)

    json_str = json.dumps(data, indent=2)

    if args.output:
        Path(args.output).write_text(json_str)
        print(f'Release data written to {args.output}')
    else:
        print(json_str)


if __name__ == '__main__':
    main()
