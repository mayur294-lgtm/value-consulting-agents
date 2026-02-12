#!/usr/bin/env python3
"""
Flywheel Test Agent: Validate changes to agent definitions and knowledge files.

Runs structural quality checks against modified files to ensure:
1. Required sections are present
2. Telemetry protocol is intact
3. No broken references
4. Quality metrics pass

Usage:
    python test_agent.py --branch flywheel/issue-42 --base-branch main
    python test_agent.py --files .claude/agents/capability-assessment.md
"""

import argparse
import json
import re
import subprocess
import sys
import yaml
from pathlib import Path


def load_quality_metrics() -> dict:
    """Load quality metrics from YAML."""
    metrics_path = Path('tests/quality_metrics.yaml')
    if not metrics_path.exists():
        print('Warning: tests/quality_metrics.yaml not found')
        return {}

    with open(metrics_path) as f:
        return yaml.safe_load(f)


def get_changed_files(branch: str, base_branch: str) -> list:
    """Get list of files changed between branches."""
    result = subprocess.run(
        ['git', 'diff', '--name-only', f'{base_branch}...{branch}'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        # Try simpler diff
        result = subprocess.run(
            ['git', 'diff', '--name-only', base_branch, branch],
            capture_output=True, text=True
        )
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def check_file(filepath: str, checks: list) -> list:
    """Run quality checks against a file."""
    try:
        content = Path(filepath).read_text()
    except FileNotFoundError:
        return [{'name': 'File exists', 'passed': False, 'reason': f'File not found: {filepath}'}]

    results = []
    for check in checks:
        name = check['name']
        pattern = check['pattern']
        min_matches = check.get('min_matches', 0)
        max_matches = check.get('max_matches', None)

        matches = len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))

        passed = True
        reason = ''

        if min_matches > 0 and matches < min_matches:
            passed = False
            reason = f'Expected >= {min_matches} matches, found {matches}'

        if max_matches is not None and matches > max_matches:
            passed = False
            reason = f'Expected <= {max_matches} matches, found {matches}'

        results.append({
            'name': name,
            'passed': passed,
            'matches': matches,
            'reason': reason,
        })

    return results


def determine_file_type(filepath: str) -> str:
    """Determine what type of file this is for check selection."""
    if '.claude/agents/' in filepath:
        return 'agent_definition'
    elif 'knowledge/' in filepath:
        return 'knowledge'
    elif 'templates/outputs/' in filepath:
        return 'template'
    else:
        return 'other'


def get_agent_name(filepath: str) -> str:
    """Extract agent name from filepath."""
    # .claude/agents/capability-assessment.md -> capability-assessment
    name = Path(filepath).stem
    return name


def run_checks(files: list, metrics: dict) -> dict:
    """Run all applicable checks against changed files."""
    all_results = {}
    total_passed = 0
    total_failed = 0

    for filepath in files:
        file_type = determine_file_type(filepath)
        checks_to_run = []

        if file_type == 'agent_definition':
            # Run agent definition structural checks (all agents)
            checks_to_run.extend(metrics.get('agent_definitions', {}).get('structural', []))

            # Run consulting-specific checks (only consulting agents need checkpoints)
            agent_name = get_agent_name(filepath)
            consulting_config = metrics.get('consulting_agent_definitions', {})
            consulting_agents = consulting_config.get('agents', [])
            if agent_name in consulting_agents:
                checks_to_run.extend(consulting_config.get('structural', []))

            # Also run agent-specific output checks if they exist
            agent_metrics = metrics.get('agents', {}).get(agent_name, {})
            # Note: These are for outputs, not definitions.
            # We only check definition structure here.

        elif file_type == 'knowledge':
            checks_to_run.extend(metrics.get('knowledge_files', {}).get('structural', []))

        if not checks_to_run:
            continue

        results = check_file(filepath, checks_to_run)
        all_results[filepath] = results

        for r in results:
            if r['passed']:
                total_passed += 1
            else:
                total_failed += 1

    return {
        'files_checked': len(all_results),
        'total_passed': total_passed,
        'total_failed': total_failed,
        'results': all_results,
    }


def print_results(results: dict):
    """Print test results in a readable format."""
    print('\n=== Flywheel Test Agent Results ===\n')

    for filepath, checks in results['results'].items():
        print(f'File: {filepath}')
        for check in checks:
            status = 'PASS' if check['passed'] else 'FAIL'
            icon = '+' if check['passed'] else 'X'
            line = f'  [{icon}] {check["name"]}'
            if not check['passed'] and check.get('reason'):
                line += f' — {check["reason"]}'
            print(line)
        print()

    total = results['total_passed'] + results['total_failed']
    print(f'Total: {results["total_passed"]}/{total} checks passed')
    print(f'Files checked: {results["files_checked"]}')

    if results['total_failed'] > 0:
        print('\nRESULT: FAILED')
    else:
        print('\nRESULT: PASSED')


def main():
    parser = argparse.ArgumentParser(description='Flywheel Test Agent')
    parser.add_argument('--branch', help='Feature branch to test')
    parser.add_argument('--base-branch', default='main', help='Base branch for comparison')
    parser.add_argument('--files', nargs='+', help='Specific files to test')
    parser.add_argument('--output', help='Output JSON file')
    args = parser.parse_args()

    metrics = load_quality_metrics()
    if not metrics:
        print('No quality metrics loaded. Skipping tests.')
        sys.exit(0)

    # Get files to check
    if args.files:
        files = args.files
    elif args.branch:
        files = get_changed_files(args.branch, args.base_branch)
    else:
        print('Error: Provide --branch or --files')
        sys.exit(1)

    if not files:
        print('No files to check.')
        sys.exit(0)

    print(f'Checking {len(files)} files...')

    # Run checks
    results = run_checks(files, metrics)
    print_results(results)

    # Save output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

    # Set exit code and GitHub Actions output
    exit_code = 0 if results['total_failed'] == 0 else 1

    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f'passed={exit_code}\n')

    sys.exit(exit_code)


# Fix missing import
import os

if __name__ == '__main__':
    main()
