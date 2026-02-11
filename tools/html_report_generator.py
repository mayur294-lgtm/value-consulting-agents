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
            --bg: #F8FAFC;
            --card: #FFFFFF;
            --text: #0F172A;
            --muted: #64748B;
            --border: #E2E8F0;
            --positive: #059669;
            --negative: #DC2626;
            --warning: #EA580C;
            --accent: #2563EB;
            --accent-light: #DBEAFE;
            --L0: #DC2626; --L1: #EA580C; --L2: #0891B2; --L3: #059669; --L4: #2563EB;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
            --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
            --shadow-lg: 0 10px 25px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
            --radius: 12px; --radius-lg: 16px;
            --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --nav-height: 70px;
        }}

        *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--bg);
            font-size: 15px;
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
            font-weight: 800;
            font-size: 1.1rem;
            margin-right: 3rem;
            letter-spacing: -0.3px;
        }}

        .nav-brand-icon {{
            width: 36px;
            height: 36px;
            background: var(--primary);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            font-weight: 900;
        }}

        .nav-links {{
            display: flex;
            gap: 0.5rem;
            list-style: none;
            flex: 1;
            overflow-x: auto;
        }}

        .nav-link {{
            color: rgba(255,255,255,0.55);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 10px;
            font-size: 0.82rem;
            font-weight: 600;
            transition: all 0.25s ease;
            white-space: nowrap;
        }}

        .nav-link:hover {{
            color: rgba(255,255,255,0.9);
            background: rgba(255,255,255,0.06);
        }}

        .nav-link.active {{
            color: white;
            background: var(--primary);
            box-shadow: 0 2px 8px rgba(26,86,255,0.3);
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
            max-width: 1360px;
            margin: 0 auto;
            background: var(--card);
            padding: 3rem 4rem;
            margin-top: var(--nav-height);
            border-radius: 0 0 var(--radius-lg) var(--radius-lg);
        }}

        section {{
            scroll-margin-top: calc(var(--nav-height) + 1rem);
        }}

        h1 {{
            color: var(--text);
            font-size: 2.5rem;
            font-weight: 900;
            letter-spacing: -1px;
            margin-bottom: 0.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid;
            border-image: linear-gradient(90deg, #1A56FF, #7B2FFF) 1;
        }}

        h2 {{
            color: var(--text);
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
            position: relative;
        }}

        h3 {{
            color: var(--primary);
            font-size: 1.2rem;
            font-weight: 700;
            letter-spacing: -0.2px;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}

        h4 {{
            color: var(--text);
            font-size: 0.95rem;
            font-weight: 700;
            margin-top: 1.25rem;
            margin-bottom: 0.5rem;
        }}

        p {{ margin-bottom: 1rem; color: var(--muted); line-height: 1.7; }}
        p strong {{ color: var(--text); }}

        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 1.5rem 0;
            font-size: 0.85rem;
            border-radius: var(--radius);
            overflow: hidden;
            border: 1px solid var(--border);
        }}

        th {{
            font-weight: 700;
            color: var(--muted);
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 14px 20px;
            text-align: left;
            background: #F8FAFC;
            border-bottom: 2px solid var(--border);
        }}

        td {{
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
            font-size: 0.85rem;
        }}

        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #F8FAFC; }}

        code {{
            background: #F1F5F9;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-family: 'Fira Code', monospace;
            font-size: 0.85em;
            color: var(--primary);
        }}

        pre {{
            background: var(--dark);
            color: #E0E0E0;
            padding: 1.5rem;
            border-radius: var(--radius);
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
            border-left: 4px solid;
            border-image: linear-gradient(to bottom, #1A56FF, #7B2FFF) 1;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            color: var(--muted);
            font-style: italic;
            background: var(--accent-light);
            border-radius: 0 var(--radius) var(--radius) 0;
        }}

        ul, ol {{ margin: 1rem 0 1rem 2rem; }}
        li {{ margin-bottom: 0.5rem; color: var(--muted); }}

        a {{ color: var(--primary); text-decoration: none; font-weight: 600; }}
        a:hover {{ text-decoration: underline; }}

        hr {{
            border: none;
            border-top: 2px solid var(--border);
            margin: 2rem 0;
        }}

        strong {{ color: var(--text); font-weight: 700; }}

        /* Confidence badges */
        .conf-high {{ background: #D1FAE5; color: #059669; padding: 6px 16px; border-radius: 10px; font-size: 0.72rem; font-weight: 800; letter-spacing: 1px; }}
        .conf-med {{ background: #FEF3C7; color: #D97706; padding: 6px 16px; border-radius: 10px; font-size: 0.72rem; font-weight: 800; letter-spacing: 1px; }}
        .conf-low {{ background: #FEF2F2; color: #DC2626; padding: 6px 16px; border-radius: 10px; font-size: 0.72rem; font-weight: 800; letter-spacing: 1px; }}

        /* Score badges */
        .score-badge {{ display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 8px; font-weight: 800; font-size: 0.85rem; color: #fff; }}
        .score-badge.s0 {{ background: var(--L0); }}
        .score-badge.s1 {{ background: var(--L1); }}
        .score-badge.s2 {{ background: var(--L2); }}
        .score-badge.s3 {{ background: var(--L3); }}
        .score-badge.s4 {{ background: var(--L4); }}

        /* Metric cards */
        .metric-card {{ background: #0F172A; border: 1px solid #1E293B; border-radius: 20px; padding: 28px 20px; text-align: center; transition: all 0.35s ease; }}
        .metric-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.15); }}
        .metric-val {{ font-size: 2rem; font-weight: 900; line-height: 1; margin-bottom: 6px; letter-spacing: -1px; color: #FFFFFF; }}
        .metric-lbl {{ font-size: 0.65rem; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }}
        .card-grid {{ display: grid; gap: 16px; }}
        .card-grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
        .card-grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
        .card-grid-4 {{ grid-template-columns: repeat(4, 1fr); }}

        /* Card component */
        .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 28px; box-shadow: var(--shadow-sm); transition: all 0.35s ease; }}
        .card:hover {{ box-shadow: 0 8px 30px rgba(0,0,0,0.08); transform: translateY(-3px); }}

        /* Dark feature section */
        .dark-feature {{ background: #0B0F1A; border-radius: 28px; padding: 72px 56px; margin: 56px 0; position: relative; overflow: hidden; }}
        .dark-feature h3 {{ font-size: 2.8rem; font-weight: 900; letter-spacing: -2px; line-height: 1.05; color: #FFFFFF; }}
        .dark-feature p {{ color: rgba(255,255,255,0.4); }}

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
            background: #F8FAFC;
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 1.5rem 2rem;
            margin: 2rem 0;
        }}

        .toc-title {{
            font-weight: 800;
            color: var(--text);
            margin-bottom: 1rem;
            font-size: 1.1rem;
            letter-spacing: -0.3px;
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
            color: var(--text);
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem;
            border-radius: 10px;
            transition: all 0.25s ease;
        }}

        .toc-item a:hover {{ background: white; color: var(--primary); }}

        .toc-number {{
            background: var(--primary);
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 800;
            flex-shrink: 0;
        }}

        /* Custom scrollbar */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(26,86,255,0.15); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(26,86,255,0.3); }}
        ::selection {{ background: rgba(26,86,255,0.12); color: inherit; }}

        /* Print styles */
        @media print {{
            .nav {{ display: none; }}
            .back-to-top {{ display: none; }}
            body {{ background: white; font-size: 11px; }}
            .container {{
                box-shadow: none;
                padding: 0;
                margin-top: 0;
            }}
        }}

        /* Responsive */
        @media (max-width: 900px) {{
            .nav-links {{ display: none; }}
            .nav-toggle {{ display: block; }}
            .container {{ padding: 2rem; }}
            .card-grid-3, .card-grid-4 {{ grid-template-columns: 1fr 1fr; }}
        }}

        @media (max-width: 600px) {{
            .container {{ padding: 1rem; }}
            .card-grid-2, .card-grid-3, .card-grid-4 {{ grid-template-columns: 1fr; }}
            h1 {{ font-size: 1.8rem; }}
            h2 {{ font-size: 1.4rem; }}
            table {{ font-size: 0.78rem; }}
            th, td {{ padding: 10px 14px; }}
            .dark-feature {{ padding: 36px 24px; border-radius: 20px; }}
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
