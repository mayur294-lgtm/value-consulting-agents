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
import os
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
        content = Path(filepath).read_text(encoding='utf-8')
    except FileNotFoundError:
        return []  # Skip deleted files
    except (UnicodeDecodeError, ValueError):
        return []  # Skip binary files (images, etc.)

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
        if filepath.endswith('.md'):
            return 'knowledge'
        return 'other'
    elif 'templates/outputs/' in filepath:
        return 'template'
    else:
        return 'other'


def get_agent_name(filepath: str) -> str:
    """Extract agent name from filepath."""
    # .claude/agents/capability-assessment.md -> capability-assessment
    name = Path(filepath).stem
    return name


# ─── Mode structural checks (ticket #103 — skill-first contracts) ────────────
#
# Extracted agents carry their operating contracts as `### Mode: <name>`
# blocks inside a `## Modes` section (see .design/solution-design-v3.md and
# scripts/orchestrate.py's Mode Composer, ticket #101). This reuses
# orchestrate.py's parse_agent_modes() rather than writing a second
# YAML/mode parser here — it only validates structure, never invokes agents.

_MODES_HEADING_RE = re.compile(r'(?m)^##\s+Modes\s*$')
_MODE_PLACEHOLDER_RE = re.compile(r'\{[A-Za-z_][A-Za-z0-9_]*\}')
_REQUIRED_MODE_KEYS = ('inputs', 'outputs', 'checkpoint')

# Agents this repo has decided will never carry a `## Modes` section
# (Ignite Inspire workshop-driven agents + the pipeline router), plus
# anything under .claude/agents/deprecated/. Mode checks never fire for
# these, even if a `## Modes` heading were accidentally added.
_MODE_CHECK_EXCLUDED_AGENTS = {
    'workshop-preparation',
    'ignite-workshop-synthesizer',
    'usecase-designer',
    'upgrade-analysis',
    'value-consulting-orchestrator',
}

_parse_agent_modes_fn = None  # lazy-imported + cached


def _get_parse_agent_modes():
    """Guarded import of parse_agent_modes from scripts/orchestrate.py.

    orchestrate.py imports `claude_agent_sdk` at module level, which these
    structural checks don't need (no agent is ever invoked here). Stub the
    module before import if it's not installed, mirroring the established
    pattern in tests/fixtures/mode_composer_selftest.py. Otherwise
    orchestrate.py imports fine under Python 3.10+ (CI runs 3.11).
    """
    global _parse_agent_modes_fn
    if _parse_agent_modes_fn is not None:
        return _parse_agent_modes_fn

    try:
        import claude_agent_sdk  # noqa: F401
    except ImportError:
        import types
        stub = types.ModuleType('claude_agent_sdk')
        for name in ('query', 'ClaudeAgentOptions', 'AssistantMessage',
                     'ResultMessage', 'TextBlock', 'ToolUseBlock'):
            setattr(stub, name, type(name, (), {}))
        sys.modules['claude_agent_sdk'] = stub

    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    try:
        from orchestrate import parse_agent_modes
    except Exception as e:
        raise RuntimeError(
            "Could not import parse_agent_modes from scripts/orchestrate.py "
            f"({e.__class__.__name__}: {e}). The mode structural check "
            "requires Python 3.10+ (CI runs 3.11)."
        ) from e

    _parse_agent_modes_fn = parse_agent_modes
    return _parse_agent_modes_fn


def check_agent_modes(filepath: str, content: str, expected_modes_map: dict) -> list:
    """Structural checks for the `## Modes` skill-first contract.

    Returns [] (no new check fires) for:
      - files without a `## Modes` section — legacy inline agents
      - agents in _MODE_CHECK_EXCLUDED_AGENTS or under .claude/agents/deprecated/

    For files that declare modes:
      - the `## Modes` section must parse (reuses orchestrate.py's
        parse_agent_modes — malformed YAML or duplicate/unknown-key modes
        fail here, naming the file and the underlying parse error)
      - each `### Mode:` block's contract must carry inputs/outputs/checkpoint,
        plus params if the block uses any {placeholder}
      - if the agent has a declared expected-modes set in quality_metrics.yaml
        (tests/quality_metrics.yaml: agent_modes), the parsed mode set must
        match exactly — a renamed/missing mode fails, naming the agent and
        the missing/unexpected mode(s)
    """
    if not _MODES_HEADING_RE.search(content):
        return []

    agent_name = get_agent_name(filepath)
    if agent_name in _MODE_CHECK_EXCLUDED_AGENTS or '.claude/agents/deprecated/' in filepath:
        return []

    try:
        parse_agent_modes = _get_parse_agent_modes()
    except RuntimeError as e:
        return [{
            'name': f'Modes: {agent_name} — parse_agent_modes importable',
            'passed': False,
            'matches': 0,
            'reason': str(e),
        }]

    try:
        modes = parse_agent_modes(filepath)
    except Exception as e:
        return [{
            'name': f'Modes: {agent_name} — "## Modes" section parses',
            'passed': False,
            'matches': 0,
            'reason': f'{filepath}: {e}',
        }]

    results = [{
        'name': f'Modes: {agent_name} — "## Modes" section parses',
        'passed': True,
        'matches': len(modes),
        'reason': '',
    }]

    for mode_name, mode_data in sorted(modes.items()):
        contract = mode_data.get('contract', {}) or {}
        raw = mode_data.get('raw', '') or ''

        required_keys = list(_REQUIRED_MODE_KEYS)
        if _MODE_PLACEHOLDER_RE.search(raw):
            required_keys.append('params')

        for key in required_keys:
            has_key = key in contract
            results.append({
                'name': f'Modes: {agent_name}/{mode_name} — has "{key}"',
                'passed': has_key,
                'matches': 1 if has_key else 0,
                'reason': '' if has_key else
                    f'{filepath}: mode "{mode_name}" missing required key "{key}"',
            })

    expected = expected_modes_map.get(agent_name)
    if expected is not None:
        found = set(modes)
        expected_set = set(expected)
        ok = found == expected_set
        reason = ''
        if not ok:
            missing = sorted(expected_set - found)
            extra = sorted(found - expected_set)
            parts = []
            if missing:
                parts.append(f'missing: {missing}')
            if extra:
                parts.append(f'unexpected: {extra}')
            reason = (
                f'{filepath}: agent "{agent_name}" declares modes {sorted(found)}, '
                f'expected {sorted(expected_set)} ({"; ".join(parts)})'
            )
        results.append({
            'name': f'Modes: {agent_name} — declares expected mode set',
            'passed': ok,
            'matches': len(found & expected_set),
            'reason': reason,
        })

    return results


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

        # Mode structural checks (ticket #103) — only meaningful for agent
        # definition files, and only when the file actually declares a
        # `## Modes` section (check_agent_modes no-ops otherwise).
        if file_type == 'agent_definition':
            try:
                content = Path(filepath).read_text(encoding='utf-8')
            except (FileNotFoundError, UnicodeDecodeError, ValueError):
                content = ''
            if content:
                modes_map = metrics.get('agent_modes', {}) or {}
                results = results + check_agent_modes(filepath, content, modes_map)

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


if __name__ == '__main__':
    main()
