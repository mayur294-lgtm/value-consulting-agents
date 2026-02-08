#!/usr/bin/env python3
"""
Flywheel Dev Agent: Analyze improvement issues and implement fixes.

Uses the Anthropic API to read the codebase, understand the problem,
and generate targeted file changes.

Usage:
    python dev_agent.py --issue-number 42 --issue-title "..." --issue-body "..."
"""

import anthropic
import json
import os
import sys
import subprocess
import argparse
from pathlib import Path


def load_agent_prompt() -> str:
    """Load the dev agent system prompt."""
    agent_path = Path('.claude/agents/dev-agent.md')
    if agent_path.exists():
        content = agent_path.read_text()
        # Strip frontmatter
        if content.startswith('---'):
            end = content.index('---', 3)
            content = content[end + 3:].strip()
        return content
    return "You are a developer agent that fixes issues in agent definitions and knowledge files."


def read_file(path: str) -> str:
    """Read a file from the repository."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return f"[File not found: {path}]"


def list_relevant_files(issue_body: str) -> list:
    """Identify files likely relevant to the issue."""
    files = []

    # Always include these
    files.append('.claude/agents/')

    # Check for agent mentions
    agents = [
        'capability-assessment', 'roi-business-case-builder',
        'discovery-transcript-interpreter', 'executive-narrative-assembler',
        'roadmap-prioritization', 'benchmark-librarian',
        'market-context-researcher', 'value-consulting-orchestrator',
    ]

    for agent in agents:
        if agent in issue_body.lower():
            files.append(f'.claude/agents/{agent}.md')

    # Check for domain mentions
    domains = ['retail', 'wealth', 'sme', 'commercial', 'corporate']
    for domain in domains:
        if domain in issue_body.lower():
            files.append(f'knowledge/domains/{domain}/')

    # Check for knowledge mentions
    if 'benchmark' in issue_body.lower():
        files.append('knowledge/domains/')
    if 'template' in issue_body.lower():
        files.append('templates/outputs/')

    return list(set(files))


def build_context(issue_body: str) -> str:
    """Build context by reading relevant files."""
    context_parts = []
    relevant = list_relevant_files(issue_body)

    for path in relevant:
        full_path = Path(path)
        if full_path.is_file():
            content = full_path.read_text()
            if len(content) < 10000:  # Don't include huge files
                context_parts.append(f"### File: {path}\n```\n{content}\n```")
        elif full_path.is_dir():
            # List directory contents
            try:
                entries = list(full_path.rglob('*.md'))[:10]
                context_parts.append(f"### Directory: {path}")
                for entry in entries:
                    context_parts.append(f"  - {entry}")
            except Exception:
                pass

    return '\n\n'.join(context_parts)


def call_dev_agent(client: anthropic.Anthropic, system_prompt: str,
                   issue_number: str, issue_title: str, issue_body: str,
                   context: str) -> dict:
    """Call Claude to analyze and implement a fix."""

    user_prompt = f"""## Improvement Issue #{issue_number}

**Title:** {issue_title}

**Issue Body:**
{issue_body}

## Repository Context

{context}

## Your Task

1. Analyze the issue and identify the root cause
2. Design a minimal, focused fix
3. Specify the exact file changes needed

Respond with a JSON object:
```json
{{
  "root_cause": "Why this problem occurs",
  "fix_description": "What the fix does",
  "risk_level": "LOW|MEDIUM|HIGH",
  "files_to_modify": [
    {{
      "path": "relative/path/to/file.md",
      "action": "edit|create",
      "search": "exact text to find (for edits)",
      "replace": "exact replacement text",
      "description": "what this change does"
    }}
  ],
  "pr_description": "Full markdown PR description",
  "testing_notes": "How to verify this fix works"
}}
```

IMPORTANT:
- For edits, provide exact text matches (search/replace)
- Keep changes minimal — one problem, one fix
- Be conservative — if unsure, set risk_level to HIGH
"""

    message = client.messages.create(
        model='claude-sonnet-4-5-20250929',
        max_tokens=4000,
        system=system_prompt,
        messages=[{'role': 'user', 'content': user_prompt}]
    )

    # Extract JSON from response
    response_text = message.content[0].text
    json_match = None

    # Try to find JSON block
    import re
    json_patterns = [
        r'```json\n([\s\S]*?)\n```',
        r'```\n([\s\S]*?)\n```',
        r'\{[\s\S]*\}',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, response_text)
        if match:
            try:
                json_match = json.loads(match.group(1) if '```' in pattern else match.group(0))
                break
            except json.JSONDecodeError:
                continue

    if not json_match:
        return {'error': 'Could not parse Dev Agent response', 'raw': response_text}

    return json_match


def apply_changes(changes: list) -> list:
    """Apply file changes to the repository."""
    applied = []

    for change in changes:
        path = change['path']
        action = change.get('action', 'edit')

        try:
            if action == 'create':
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).write_text(change.get('replace', ''))
                applied.append({'path': path, 'action': 'created', 'success': True})

            elif action == 'edit':
                content = Path(path).read_text()
                search = change.get('search', '')
                replace = change.get('replace', '')

                if search and search in content:
                    new_content = content.replace(search, replace, 1)
                    Path(path).write_text(new_content)
                    applied.append({'path': path, 'action': 'edited', 'success': True})
                else:
                    applied.append({
                        'path': path,
                        'action': 'edit_failed',
                        'success': False,
                        'reason': 'Search text not found in file'
                    })

        except Exception as e:
            applied.append({'path': path, 'action': action, 'success': False, 'reason': str(e)})

    return applied


def create_branch_and_commit(issue_number: str, applied_changes: list) -> str:
    """Create a feature branch and commit changes."""
    branch_name = f'flywheel/issue-{issue_number}'

    subprocess.run(['git', 'checkout', '-b', branch_name], check=True)

    # Stage changed files
    for change in applied_changes:
        if change['success']:
            subprocess.run(['git', 'add', change['path']], check=True)

    # Commit
    subprocess.run(
        ['git', 'commit', '-m',
         f'fix: automated improvement for issue #{issue_number}\n\n'
         f'Co-Authored-By: Flywheel Dev Agent <flywheel@backbase.com>'],
        check=True
    )

    # Push
    subprocess.run(['git', 'push', '-u', 'origin', branch_name], check=True)

    return branch_name


def main():
    parser = argparse.ArgumentParser(description='Flywheel Dev Agent')
    parser.add_argument('--issue-number', required=True)
    parser.add_argument('--issue-title', required=True)
    parser.add_argument('--issue-body', required=True)
    args = parser.parse_args()

    # Initialize Anthropic client
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('Error: ANTHROPIC_API_KEY not set', file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Load agent prompt
    system_prompt = load_agent_prompt()

    # Build context
    print(f'Analyzing issue #{args.issue_number}...')
    context = build_context(args.issue_body)

    # Call Dev Agent
    print('Calling Dev Agent...')
    result = call_dev_agent(
        client, system_prompt,
        args.issue_number, args.issue_title, args.issue_body, context
    )

    if 'error' in result:
        print(f'Error: {result["error"]}', file=sys.stderr)
        sys.exit(1)

    # Check risk level
    if result.get('risk_level') == 'HIGH':
        print('HIGH risk change detected. Escalating to human review.')
        # Write output but don't apply
        with open('dev_agent_output.json', 'w') as f:
            json.dump(result, f, indent=2)
        # Set outputs for GitHub Actions
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write('changes_made=false\n')
        sys.exit(0)

    # Apply changes
    print('Applying changes...')
    applied = apply_changes(result.get('files_to_modify', []))

    successful = [c for c in applied if c['success']]
    failed = [c for c in applied if not c['success']]

    if not successful:
        print('No changes could be applied.', file=sys.stderr)
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write('changes_made=false\n')
        sys.exit(1)

    print(f'Applied {len(successful)} changes, {len(failed)} failed.')

    # Create branch and commit
    print('Creating branch and committing...')
    branch_name = create_branch_and_commit(args.issue_number, applied)

    # Write PR description
    pr_desc = result.get('pr_description', 'Automated improvement by Flywheel Dev Agent.')
    with open('dev_plan.md', 'w') as f:
        f.write(pr_desc)

    # Save full output
    result['applied_changes'] = applied
    result['branch_name'] = branch_name
    with open('dev_agent_output.json', 'w') as f:
        json.dump(result, f, indent=2)

    # Set GitHub Actions outputs
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f'branch_name={branch_name}\n')
        f.write('changes_made=true\n')
        f.write(f'pr_description={pr_desc[:200]}\n')

    print(f'Done. Branch: {branch_name}')


if __name__ == '__main__':
    main()
