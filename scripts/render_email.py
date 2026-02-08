#!/usr/bin/env python3
"""
Flywheel Email Renderer: Render HTML emails from Jinja2 templates.

Usage:
    python render_email.py --template templates/emails/approval_request.html \
                           --data approval_data.json \
                           --output approval_email.html

    python render_email.py --template templates/emails/release_notes.html \
                           --data release_data.json \
                           --output release_email.html
"""

import json
import sys
import argparse
from pathlib import Path

try:
    from jinja2 import Template
except ImportError:
    # Fallback: simple string replacement if Jinja2 not available
    class Template:
        def __init__(self, source):
            self.source = source

        def render(self, **kwargs):
            result = self.source
            for key, value in kwargs.items():
                result = result.replace('{{ ' + key + ' }}', str(value))
                result = result.replace('{{' + key + '}}', str(value))
            # Handle basic conditionals by keeping content
            import re
            result = re.sub(r'\{%.*?%\}', '', result)
            return result


def render_email(template_path: str, data_path: str, output_path: str):
    """Render an HTML email from template and data."""
    template_text = Path(template_path).read_text()
    template = Template(template_text)

    with open(data_path, 'r') as f:
        data = json.load(f)

    html = template.render(**data)

    Path(output_path).write_text(html)
    print(f'Email rendered: {output_path}')


def main():
    parser = argparse.ArgumentParser(description='Flywheel Email Renderer')
    parser.add_argument('--template', required=True, help='Path to HTML template')
    parser.add_argument('--data', required=True, help='Path to JSON data file')
    parser.add_argument('--output', required=True, help='Output HTML file path')
    args = parser.parse_args()

    if not Path(args.template).exists():
        print(f'Error: Template not found: {args.template}', file=sys.stderr)
        sys.exit(1)

    if not Path(args.data).exists():
        print(f'Error: Data file not found: {args.data}', file=sys.stderr)
        sys.exit(1)

    render_email(args.template, args.data, args.output)


if __name__ == '__main__':
    main()
