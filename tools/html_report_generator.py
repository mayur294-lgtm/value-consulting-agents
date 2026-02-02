#!/usr/bin/env python3
"""
HTML Report Generator for Value Consulting

Converts markdown reports to professional HTML with Backbase styling,
navigation, and interactive features.
"""

import markdown
import argparse
import re
from pathlib import Path

# Navigation-enabled HTML template
HTML_TEMPLATE_WITH_NAV = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: #1A56FF;
            --dark: #1A1F36;
            --positive: #00B386;
            --negative: #FF4444;
            --warning: #FFC107;
            --light-blue: #E8F0FF;
            --light-gray: #F5F5F5;
            --text: #333;
            --border: #E0E0E0;
            --nav-height: 70px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        html {{ scroll-behavior: smooth; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--light-gray);
        }}

        /* Navigation */
        .nav {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--nav-height);
            background: var(--dark);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}

        .nav-brand {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: white;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.2rem;
            margin-right: 3rem;
        }}

        .nav-brand-icon {{
            width: 36px;
            height: 36px;
            background: var(--primary);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }}

        .nav-links {{
            display: flex;
            gap: 0.5rem;
            list-style: none;
            flex: 1;
            overflow-x: auto;
        }}

        .nav-link {{
            color: rgba(255,255,255,0.7);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .nav-link:hover {{
            color: white;
            background: rgba(255,255,255,0.1);
        }}

        .nav-link.active {{
            color: white;
            background: var(--primary);
        }}

        .nav-toggle {{
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }}

        /* Container */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 3rem 4rem;
            margin-top: var(--nav-height);
        }}

        section {{
            scroll-margin-top: calc(var(--nav-height) + 1rem);
        }}

        h1 {{
            color: var(--primary);
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid var(--primary);
        }}

        h2 {{
            color: var(--dark);
            font-size: 1.8rem;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }}

        h3 {{
            color: var(--primary);
            font-size: 1.4rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}

        h4 {{
            color: var(--dark);
            font-size: 1.1rem;
            margin-top: 1.25rem;
            margin-bottom: 0.5rem;
        }}

        p {{ margin-bottom: 1rem; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.9rem;
        }}

        th {{
            background: var(--dark);
            color: white;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
        }}

        tr:nth-child(even) {{ background: var(--light-gray); }}
        tr:hover {{ background: var(--light-blue); }}

        code {{
            background: var(--light-gray);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
            font-size: 0.85em;
        }}

        pre {{
            background: var(--dark);
            color: #E0E0E0;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
            font-size: 0.85rem;
            line-height: 1.5;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}

        blockquote {{
            border-left: 4px solid var(--primary);
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            color: #555;
            font-style: italic;
            background: var(--light-blue);
            border-radius: 0 8px 8px 0;
        }}

        ul, ol {{ margin: 1rem 0 1rem 2rem; }}
        li {{ margin-bottom: 0.5rem; }}

        a {{ color: var(--primary); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}

        hr {{
            border: none;
            border-top: 2px solid var(--border);
            margin: 2rem 0;
        }}

        strong {{ color: var(--dark); }}

        /* Confidence badges */
        .conf-high {{ background-color: #D4EDDA; padding: 2px 6px; border-radius: 3px; }}
        .conf-med {{ background-color: #CCE5FF; padding: 2px 6px; border-radius: 3px; }}
        .conf-low {{ background-color: #FFF3CD; padding: 2px 6px; border-radius: 3px; }}

        /* Back to top */
        .back-to-top {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 48px;
            height: 48px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
            box-shadow: 0 4px 12px rgba(26, 86, 255, 0.3);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s;
            z-index: 999;
        }}

        .back-to-top.visible {{
            opacity: 1;
            visibility: visible;
        }}

        .back-to-top:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(26, 86, 255, 0.4);
        }}

        /* Table of Contents */
        .toc {{
            background: var(--light-gray);
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin: 2rem 0;
        }}

        .toc-title {{
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }}

        .toc-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.5rem;
            list-style: none;
            margin: 0;
            padding: 0;
        }}

        .toc-item a {{
            color: var(--primary);
            text-decoration: none;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem;
            border-radius: 6px;
            transition: background 0.2s;
        }}

        .toc-item a:hover {{ background: white; }}

        .toc-number {{
            background: var(--primary);
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
            flex-shrink: 0;
        }}

        /* Print styles */
        @media print {{
            .nav {{ display: none; }}
            .back-to-top {{ display: none; }}
            body {{ background: white; }}
            .container {{
                box-shadow: none;
                padding: 0;
                margin-top: 0;
            }}
        }}

        /* Mobile responsive */
        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .nav-toggle {{ display: block; }}
            .container {{ padding: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="nav">
        <a href="#" class="nav-brand">
            <span class="nav-brand-icon">B</span>
            <span>Value Consulting</span>
        </a>
        <ul class="nav-links">
            {nav_links}
        </ul>
        <button class="nav-toggle">☰</button>
    </nav>

    <div class="container">
        {toc}
        {content}
    </div>

    <!-- Back to top button -->
    <button class="back-to-top" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})">↑</button>

    <script>
        // Scroll-based navigation highlighting
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('section[id]');

        function updateActiveNav() {{
            const scrollPos = window.scrollY + 100;

            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                const sectionId = section.getAttribute('id');

                if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {{
                    navLinks.forEach(link => {{
                        link.classList.remove('active');
                        if (link.getAttribute('href') === '#' + sectionId) {{
                            link.classList.add('active');
                        }}
                    }});
                }}
            }});

            // Back to top button visibility
            const backToTop = document.querySelector('.back-to-top');
            if (window.scrollY > 300) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }}

        window.addEventListener('scroll', updateActiveNav);
        updateActiveNav();

        // Mobile nav toggle
        const navToggle = document.querySelector('.nav-toggle');
        const navLinksContainer = document.querySelector('.nav-links');

        navToggle.addEventListener('click', () => {{
            navLinksContainer.style.display = navLinksContainer.style.display === 'flex' ? 'none' : 'flex';
        }});

        // Add confidence styling to table cells
        document.querySelectorAll('td').forEach(td => {{
            const text = td.textContent;
            if (text.includes('HIGH') || text.includes('🟢')) {{
                td.style.backgroundColor = '#D4EDDA';
            }} else if (text.includes('MED') || text.includes('🔵')) {{
                td.style.backgroundColor = '#CCE5FF';
            }} else if (text.includes('LOW') || text.includes('🟡')) {{
                td.style.backgroundColor = '#FFF3CD';
            }} else if (text.includes('CRITICAL') || text.includes('🔴')) {{
                td.style.backgroundColor = '#F8D7DA';
            }}
        }});
    </script>
</body>
</html>
"""

# Simple template without navigation (for short reports)
HTML_TEMPLATE_SIMPLE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: #1A56FF;
            --dark: #1A1F36;
            --positive: #00B386;
            --negative: #FF4444;
            --warning: #FFC107;
            --light-blue: #E8F0FF;
            --light-gray: #F5F5F5;
            --text: #333;
            --border: #E0E0E0;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--light-gray);
            padding: 2rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 3rem 4rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}

        h1 {{
            color: var(--primary);
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid var(--primary);
        }}

        h2 {{
            color: var(--dark);
            font-size: 1.8rem;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }}

        h3 {{
            color: var(--primary);
            font-size: 1.4rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}

        h4 {{
            color: var(--dark);
            font-size: 1.1rem;
            margin-top: 1.25rem;
            margin-bottom: 0.5rem;
        }}

        p {{ margin-bottom: 1rem; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.9rem;
        }}

        th {{
            background: var(--dark);
            color: white;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
        }}

        tr:nth-child(even) {{ background: var(--light-gray); }}
        tr:hover {{ background: var(--light-blue); }}

        code {{
            background: var(--light-gray);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
            font-size: 0.85em;
        }}

        pre {{
            background: var(--dark);
            color: #E0E0E0;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
            font-size: 0.85rem;
            line-height: 1.5;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}

        blockquote {{
            border-left: 4px solid var(--primary);
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            color: #555;
            font-style: italic;
            background: var(--light-blue);
            border-radius: 0 8px 8px 0;
        }}

        ul, ol {{ margin: 1rem 0 1rem 2rem; }}
        li {{ margin-bottom: 0.5rem; }}

        a {{ color: var(--primary); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}

        hr {{
            border: none;
            border-top: 2px solid var(--border);
            margin: 2rem 0;
        }}

        strong {{ color: var(--dark); }}

        .conf-high {{ background-color: #D4EDDA; padding: 2px 6px; border-radius: 3px; }}
        .conf-med {{ background-color: #CCE5FF; padding: 2px 6px; border-radius: 3px; }}
        .conf-low {{ background-color: #FFF3CD; padding: 2px 6px; border-radius: 3px; }}

        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
    <script>
        document.querySelectorAll('td').forEach(td => {{
            const text = td.textContent;
            if (text.includes('HIGH') || text.includes('🟢')) {{
                td.style.backgroundColor = '#D4EDDA';
            }} else if (text.includes('MED') || text.includes('🔵')) {{
                td.style.backgroundColor = '#CCE5FF';
            }} else if (text.includes('LOW') || text.includes('🟡')) {{
                td.style.backgroundColor = '#FFF3CD';
            }} else if (text.includes('CRITICAL') || text.includes('🔴')) {{
                td.style.backgroundColor = '#F8D7DA';
            }}
        }});
    </script>
</body>
</html>
"""


def slugify(text: str) -> str:
    """Convert heading text to URL-friendly slug."""
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace whitespace with hyphens
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug


def extract_sections(md_content: str) -> list:
    """Extract H2 headings for navigation."""
    sections = []
    for line in md_content.split('\n'):
        if line.startswith('## '):
            title = line[3:].strip()
            slug = slugify(title)
            sections.append({'title': title, 'slug': slug})
    return sections


def wrap_sections(html_content: str, sections: list) -> str:
    """Wrap H2 sections with section tags for scroll targeting."""
    for section in sections:
        # Find the h2 tag and wrap it with a section
        pattern = f'<h2[^>]*>{re.escape(section["title"])}</h2>'
        replacement = f'</section><section id="{section["slug"]}"><h2>{section["title"]}</h2>'
        html_content = re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)

    # Clean up the first </section> and add closing section at end
    html_content = html_content.replace('</section><section', '<section', 1)
    html_content += '</section>'

    return html_content


def generate_nav_links(sections: list) -> str:
    """Generate navigation link HTML."""
    links = []
    for i, section in enumerate(sections):
        active = ' active' if i == 0 else ''
        links.append(f'<li><a href="#{section["slug"]}" class="nav-link{active}">{section["title"]}</a></li>')
    return '\n            '.join(links)


def generate_toc(sections: list) -> str:
    """Generate table of contents HTML."""
    if len(sections) < 3:
        return ''

    items = []
    for i, section in enumerate(sections, 1):
        items.append(f'''<li class="toc-item"><a href="#{section["slug"]}"><span class="toc-number">{i}</span> {section["title"]}</a></li>''')

    return f'''
        <div class="toc">
            <div class="toc-title">Quick Navigation</div>
            <ul class="toc-list">
                {chr(10).join(items)}
            </ul>
        </div>
    '''


def convert_md_to_html(md_path: str, output_path: str = None, with_nav: bool = True):
    """Convert markdown file to styled HTML with optional navigation."""
    md_path = Path(md_path)

    if not md_path.exists():
        print(f"File not found: {md_path}")
        return None

    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Extract title from first heading
    title = "Value Consulting Report"
    for line in md_content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Extract sections for navigation
    sections = extract_sections(md_content)

    # Convert to HTML
    md_extensions = ['tables', 'fenced_code', 'toc']
    html_content = markdown.markdown(md_content, extensions=md_extensions)

    # Decide which template to use
    if with_nav and len(sections) >= 3:
        # Wrap sections for navigation
        html_content = wrap_sections(html_content, sections)

        # Generate navigation
        nav_links = generate_nav_links(sections)
        toc = generate_toc(sections)

        # Generate full HTML with navigation
        full_html = HTML_TEMPLATE_WITH_NAV.format(
            title=title,
            content=html_content,
            nav_links=nav_links,
            toc=toc
        )
    else:
        # Use simple template without navigation
        full_html = HTML_TEMPLATE_SIMPLE.format(title=title, content=html_content)

    # Determine output path
    if output_path is None:
        output_path = md_path.with_suffix('.html')
    else:
        output_path = Path(output_path)

    # Write HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"Generated: {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description='Convert markdown reports to HTML')
    parser.add_argument('input', help='Input markdown file or directory')
    parser.add_argument('-o', '--output', help='Output HTML file (optional)')
    parser.add_argument('--no-nav', action='store_true', help='Disable navigation bar')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        convert_md_to_html(str(input_path), args.output, with_nav=not args.no_nav)
    elif input_path.is_dir():
        # Convert all markdown files in directory
        for md_file in input_path.glob('*.md'):
            convert_md_to_html(str(md_file), with_nav=not args.no_nav)
    else:
        print(f"Invalid path: {input_path}")


if __name__ == '__main__':
    main()
