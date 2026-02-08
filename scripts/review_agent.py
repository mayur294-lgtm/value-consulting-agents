#!/usr/bin/env python3
"""
Flywheel Review Agent: Code review changes made by the Dev Agent.

Uses Claude to review diffs against the original issue and provide
APPROVED / REQUEST_CHANGES / ESCALATE decisions.

Usage:
    python review_agent.py --diff changes.diff --issue-body "..." --dev-plan dev_plan.md
"""

import anthropic
import json
import os
import sys
import argparse
import re
from pathlib import Path


def load_review_prompt() -> str:
    """Load the review agent system prompt."""
    agent_path = Path('.claude/agents/review-agent.md')
    if agent_path.exists():
        content = agent_path.read_text()
        if content.startswith('---'):
            end = content.index('---', 3)
            content = content[end + 3:].strip()
        return content
    return "You are a code review agent. Review changes for correctness, safety, and minimality."


def call_review_agent(client: anthropic.Anthropic, system_prompt: str,
                      diff: str, issue_body: str, dev_plan: str) -> dict:
    """Call Claude to review the changes."""

    user_prompt = f"""## Review Request

### Original Issue
{issue_body}

### Dev Agent's Plan
{dev_plan}

### Code Diff
```diff
{diff}
```

## Your Task

Review these changes using your checklist:
1. Problem-Solution Alignment
2. Agent Instruction Quality
3. Knowledge Accuracy
4. Template Integrity
5. Side Effects
6. Risk Assessment

Respond with a JSON decision:

For APPROVED:
```json
{{
  "decision": "APPROVED",
  "confidence": "HIGH or MEDIUM",
  "notes": "Why this change is safe and correct",
  "risk_level": "LOW or MEDIUM"
}}
```

For REQUEST_CHANGES:
```json
{{
  "decision": "REQUEST_CHANGES",
  "issues": ["issue 1", "issue 2"],
  "suggestions": ["fix 1", "fix 2"]
}}
```

For ESCALATE (too risky for auto-merge):
```json
{{
  "decision": "ESCALATE",
  "reason": "Why this needs human judgment",
  "risk_level": "HIGH"
}}
```
"""

    message = client.messages.create(
        model='claude-sonnet-4-5-20250929',
        max_tokens=2000,
        system=system_prompt,
        messages=[{'role': 'user', 'content': user_prompt}]
    )

    response_text = message.content[0].text

    # Parse JSON from response
    json_patterns = [
        r'```json\n([\s\S]*?)\n```',
        r'\{[\s\S]*?\}',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, response_text)
        if match:
            try:
                text = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(text)
            except json.JSONDecodeError:
                continue

    # Default to escalate if can't parse
    return {
        'decision': 'ESCALATE',
        'reason': 'Could not parse review agent response',
        'raw_response': response_text
    }


def main():
    parser = argparse.ArgumentParser(description='Flywheel Review Agent')
    parser.add_argument('--diff', required=True, help='Path to diff file')
    parser.add_argument('--issue-body', required=True, help='Original issue body')
    parser.add_argument('--dev-plan', required=True, help='Path to dev plan markdown')
    args = parser.parse_args()

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('Error: ANTHROPIC_API_KEY not set', file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = load_review_prompt()

    # Read inputs
    diff = Path(args.diff).read_text() if Path(args.diff).exists() else ''
    dev_plan = Path(args.dev_plan).read_text() if Path(args.dev_plan).exists() else ''

    if not diff:
        print('No diff found. Nothing to review.')
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write('decision=ESCALATE\n')
        sys.exit(0)

    # Truncate long diffs
    if len(diff) > 5000:
        diff = diff[:5000] + '\n\n[... diff truncated for review ...]'

    print('Running Review Agent...')
    result = call_review_agent(client, system_prompt, diff, args.issue_body, dev_plan)

    decision = result.get('decision', 'ESCALATE')
    print(f'Decision: {decision}')
    print(json.dumps(result, indent=2))

    # Save review output
    with open('review_output.json', 'w') as f:
        json.dump(result, f, indent=2)

    # Set GitHub Actions output
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f'decision={decision}\n')

    if decision == 'APPROVED':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
