"""
Frontline 2026 HTML Builder — Interactive presentation preview.

Design system: Backbase Unified Frontline 2026
Purpose: Brainstorm and iterate on content before converting to PPTX.
Output: Single-file HTML with all CSS/JS inline, keyboard navigation.
"""

import os
import json
from datetime import datetime


class Frontline2026HTML:
    """Generates single-file HTML presentations in the Backbase 2026 style.

    Features:
    - Libre Franklin font (Google Fonts)
    - Navy/Blue/White color palette
    - Keyboard navigation (← → Space Home End)
    - Dot navigation on right edge
    - Smooth transitions between slides
    - Components: cover, divider, content, split, showcase, architecture, stats, case study
    """

    def __init__(self, title: str = "Backbase Presentation"):
        self.title = title
        self.scenes = []
        # Load Backbase wordmark PNGs (with correct notched B) as base64
        self._logo_dark_b64 = ""
        self._logo_white_b64 = ""
        import base64
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for variant, attr in [("backbase-wordmark-dark.png", "_logo_dark_b64"),
                               ("backbase-wordmark-white.png", "_logo_white_b64")]:
            path = os.path.join(base, "knowledge", "Ignite Inspire", "brand-assets", variant)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    setattr(self, attr, base64.b64encode(f.read()).decode())

    def _escape(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))

    # ──────────────────────────────────────────
    # Scene Builders
    # ──────────────────────────────────────────

    def add_cover(self, section_label: str, title: str, subtitle: str = ""):
        lines = title.split("|")
        title_html = "<br>".join(self._escape(l.strip()) for l in lines)
        self.scenes.append(f'''
    <section class="slide slide--dark">
      <div class="slide__inner slide__inner--cover">
        <span class="label">{self._escape(section_label.upper())}</span>
        <h1 class="cover-title">{title_html}</h1>
        <p class="cover-date">{self._escape(subtitle)}</p>
      </div>
    </section>''')

    def add_section_divider(self, section_label: str, title: str, tagline: str = ""):
        lines = title.split("|")
        title_html = "<br>".join(self._escape(l.strip()) for l in lines)
        tagline_html = f'<p class="tagline">{self._escape(tagline)}</p>' if tagline else ""
        self.scenes.append(f'''
    <section class="slide slide--dark">
      <div class="slide__inner slide__inner--divider">
        <span class="label">{self._escape(section_label.upper())}</span>
        <h1>{title_html}</h1>
        {tagline_html}
      </div>
    </section>''')

    def add_agenda(self, section_label: str, title: str,
                   customer_name: str, items: list):
        items_html = "\n".join(
            f'        <div class="agenda-item"><span class="agenda-num">{str(i+1).zfill(2)}</span>{self._escape(item)}</div>'
            for i, item in enumerate(items)
        )
        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--agenda">
        <div class="agenda-left">
          <span class="label label--dark">{self._escape(section_label.upper())}</span>
          <h1 class="agenda-title">{self._escape(title)}</h1>
          <p class="agenda-customer">{self._escape(customer_name)}</p>
        </div>
        <div class="agenda-right">
{items_html}
        </div>
      </div>
    </section>''')

    def add_content(self, title: str, subtitle: str = "", body_lines: list = None):
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""
        body_html = ""
        if body_lines:
            items = "\n".join(f'          <li>{self._escape(l)}</li>' for l in body_lines)
            body_html = f'''
        <ul class="content-list">
{items}
        </ul>'''
        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div class="content-area">
          {body_html}
        </div>
      </div>
    </section>''')

    def add_split_comparison(self, title: str, section_label: str = "",
                             left_title: str = "", left_items: list = None,
                             right_title: str = "", right_items: list = None):
        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ""
        left_list = "\n".join(f'            <li>{self._escape(l)}</li>' for l in (left_items or []))
        right_list = "\n".join(f'            <li>{self._escape(l)}</li>' for l in (right_items or []))
        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--split">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        <div class="split">
          <div class="split__from">
            <h3>{self._escape(left_title.upper())}</h3>
            <ul>
{left_list}
            </ul>
          </div>
          <div class="split__to">
            <h3>{self._escape(right_title.upper())}</h3>
            <ul>
{right_list}
            </ul>
          </div>
        </div>
      </div>
    </section>''')

    def add_architecture(self, title: str, subtitle: str = "",
                         customer_channels: list = None,
                         employee_workspaces: list = None,
                         platform_label: str = "AI-native Banking OS",
                         enablement_systems: list = None,
                         core_systems: list = None):
        channels = customer_channels or ["Online", "Mobile", "Conversational"]
        workspaces = employee_workspaces or ["Teller", "CSR", "RM / Advisor", "Operations"]
        enablement = enablement_systems or ["CRM", "CDP", "KYC", "AML", "Fraud", "Risk", "LMS"]
        core = core_systems or ["Ledger", "Cards", "Payments", "Back Office"]

        def boxes(items, css_class=""):
            return "\n".join(f'            <div class="arch-box {css_class}">{self._escape(i)}</div>' for i in items)

        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""
        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div class="arch-stack">
          <div class="arch-label">Customers</div>
          <div class="arch-row">
{boxes(channels)}
          </div>
          <div class="arch-label">Employees</div>
          <div class="arch-row">
{boxes(workspaces)}
          </div>
          <div class="arch-bar">{self._escape(platform_label)}</div>
          <div class="arch-label arch-label--muted">Enablement Systems</div>
          <div class="arch-row">
{boxes(enablement, "arch-box--muted")}
          </div>
          <div class="arch-label arch-label--muted">Core Systems</div>
          <div class="arch-row">
{boxes(core, "arch-box--muted")}
          </div>
        </div>
      </div>
    </section>''')

    def add_stat_cards(self, title: str, subtitle: str = "", stats: list = None):
        stats = stats or []
        cards_html = ""
        for s in stats:
            trend = s.get("trend", "")
            trend_class = "trend--up" if ("+" in trend or "↑" in trend) else "trend--neutral"
            trend_html = f'<span class="stat-trend {trend_class}">{self._escape(trend)}</span>' if trend else ""
            cards_html += f'''
            <div class="stat-card">
              <span class="stat-number">{self._escape(s.get("number", ""))}</span>
              <span class="stat-label">{self._escape(s.get("label", ""))}</span>
              {trend_html}
            </div>'''
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""
        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div class="stat-grid">
          {cards_html}
        </div>
      </div>
    </section>''')

    def add_case_study(self, title: str, body_lines: list = None, legal_text: str = None):
        body_html = ""
        if body_lines:
            items = "\n".join(f'          <li>{self._escape(l)}</li>' for l in body_lines)
            body_html = f'<ul class="content-list">\n{items}\n        </ul>'
        legal = legal_text or "Restricted use. This case study is intended solely for use in 1:1 discussions with prospective clients."
        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        <span class="case-label">CUSTOMER CASE</span>
        <h2 class="slide-title">{self._escape(title)}</h2>
        <div class="content-area">
          {body_html}
        </div>
        <p class="legal-footer">{self._escape(legal)}</p>
      </div>
    </section>''')

    def add_showcase(self, section_label: str, title: str, description: str,
                     image_url: str = ""):
        img_html = f'<img src="{self._escape(image_url)}" alt="Product screenshot" />' if image_url else '<div class="showcase__placeholder">[ Product Screenshot ]</div>'
        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--showcase">
        <div class="showcase__text">
          <span class="label label--dark">{self._escape(section_label.upper())}</span>
          <h2>{self._escape(title)}</h2>
          <p>{self._escape(description)}</p>
        </div>
        <div class="showcase__image">
          {img_html}
        </div>
      </div>
    </section>''')

    def add_statement(self, text: str, highlight_words: list = None):
        """Statement slide — large centered text in navy. Key words highlighted in action blue."""
        highlight_words = highlight_words or []
        escaped = self._escape(text)
        for word in highlight_words:
            ew = self._escape(word)
            escaped = escaped.replace(ew, f'<span class="statement__highlight">{ew}</span>')
        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--statement">
        <p class="statement__text">{escaped}</p>
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Rich Tile Components (from executive briefing, adapted to 2026 style)
    # ──────────────────────────────────────────

    def _render_rich_text(self, text: str) -> str:
        """Render **bold** markers within escaped text."""
        import re
        escaped = self._escape(text)
        return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)

    def add_tiles(self, title: str, subtitle: str = "", section_label: str = "",
                  tiles: list = None, columns: int = 3, footer_text: str = ""):
        """Grid of cards/tiles. Each tile: {title, body, accent, summary?, summary_accent?}
        Body items support **bold** markers for inline emphasis."""
        tiles = tiles or []
        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ""
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""

        cards = ""
        for t in tiles:
            accent = t.get("accent", "blue")
            pill = f'<span class="tile__pill tile__pill--{accent}">{self._escape(t.get("pill", ""))}</span>' if t.get("pill") else ""
            stat = f'<div class="tile__stat tile__stat--{accent}">{self._escape(t.get("stat", ""))}</div>' if t.get("stat") else ""
            body = t.get("body", "")
            if isinstance(body, list):
                body_html = "<br>".join(self._render_rich_text(b) for b in body)
            else:
                body_html = self._render_rich_text(body)
            # Optional summary box at bottom of tile
            summary = t.get("summary", "")
            summary_accent = t.get("summary_accent", accent)
            if summary:
                accent_colors = {"blue": "#1A5AFF", "red": "#DC2626", "green": "#16A34A", "amber": "#D97706", "purple": "#7C3AED", "cyan": "#0891B2"}
                bg_colors = {"blue": "#EBF0FF", "red": "#FFF5F5", "green": "#F0FDF4", "amber": "#FFFBEB", "purple": "#F5F3FF", "cyan": "#F0FDFA"}
                sc = accent_colors.get(summary_accent, "#1A5AFF")
                sb = bg_colors.get(summary_accent, "#EBF0FF")
                summary_html = f'<div style="background:{sb};border:1px solid {sc}30;border-radius:8px;padding:8px 12px;margin-top:auto;text-align:center;font-size:10px;"><div style="font-size:9px;font-weight:800;letter-spacing:1.5px;color:{sc};text-transform:uppercase;margin-bottom:2px;">{self._render_rich_text(summary.split("|")[0].strip()) if "|" in summary else ""}</div><div style="font-size:12px;font-weight:800;color:var(--text-main);">{self._render_rich_text(summary.split("|")[1].strip()) if "|" in summary else self._render_rich_text(summary)}</div></div>'
            else:
                summary_html = ""
            cards += f'''
            <div class="tile tile--{accent}" style="{'display:flex;flex-direction:column;' if summary else ''}">
              {pill}
              {stat}
              <div class="tile__title">{self._escape(t.get("title", ""))}</div>
              <div class="tile__body">{body_html}</div>
              {summary_html}
            </div>'''

        footer_html = f'<div style="background:#F0F4FF;border-radius:8px;padding:10px 16px;margin-top:12px;font-size:11px;color:var(--text-main);text-align:center;line-height:1.5;">{self._render_rich_text(footer_text)}</div>' if footer_text else ""

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div class="tile-grid tile-grid--{columns}">
          {cards}
        </div>
        {footer_html}
      </div>
    </section>''')

    def add_process_rows(self, title: str, subtitle: str = "", section_label: str = "",
                         rows: list = None, footer_text: str = ""):
        """Before → After process comparison rows. Each row: {label, before, after, saving}"""
        rows = rows or []
        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ""
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""

        rows_html = ""
        for r in rows:
            rows_html += f'''
            <div class="proc-row">
              <div class="proc-row__label">{self._escape(r.get("label", ""))}</div>
              <div class="proc-row__before">{self._escape(r.get("before", ""))}</div>
              <div class="proc-row__arrow">&rarr;</div>
              <div class="proc-row__after">{self._escape(r.get("after", ""))}</div>
              <div class="proc-row__saving">{self._escape(r.get("saving", ""))}</div>
            </div>'''

        footer_html = f'<div class="proc-footer">{self._escape(footer_text)}</div>' if footer_text else ""

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div class="proc-rows">
          {rows_html}
        </div>
        {footer_html}
      </div>
    </section>''')

    def add_bar_chart_rows(self, title: str, subtitle: str = "", section_label: str = "",
                           rows: list = None, summary_boxes: list = None,
                           footer_text: str = ""):
        """Horizontal bar chart rows showing before/after with proportional bars.
        Each row: {label, before_mins, after_mins, saving}
        summary_boxes: [{label, stat, source}] or [{label, items: [{stat, label}]}]
        """
        rows = rows or []
        summary_boxes = summary_boxes or []
        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ""
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""

        # Calculate max for proportional widths
        max_mins = max((r.get("before_mins", 0) for r in rows), default=1) or 1

        bars_html = ""
        for r in rows:
            before = r.get("before_mins", 0)
            after = r.get("after_mins", 0)
            before_pct = (before / max_mins) * 100
            after_pct = (after / max_mins) * 100
            label = self._escape(r.get("label", ""))
            saving = self._escape(r.get("saving", ""))
            bars_html += f'''
              <div style="display:flex;align-items:center;gap:12px">
                <div style="width:250px;font-size:11px;font-weight:700;color:var(--text-main);text-align:right">{label}</div>
                <div style="flex:1;display:flex;flex-direction:column;gap:2px">
                  <div style="display:flex;align-items:center;gap:8px">
                    <div style="width:{before_pct:.0f}%;height:14px;background:#F4A6A0;border-radius:3px"></div>
                    <span style="font-size:9px;color:#C0564F;font-weight:700;white-space:nowrap">{before} mins</span>
                  </div>
                  <div style="display:flex;align-items:center;gap:8px">
                    <div style="width:{after_pct:.0f}%;height:14px;background:#93B5FF;border-radius:3px"></div>
                    <span style="font-size:9px;color:#1A5AFF;font-weight:700;white-space:nowrap">{after} mins <span style="color:#16A34A">({saving})</span></span>
                  </div>
                </div>
              </div>'''

        # Legend
        bars_html += '''
              <div style="display:flex;gap:20px;font-size:10px;color:var(--text-muted);margin-top:4px">
                <div style="display:flex;align-items:center;gap:4px"><div style="width:12px;height:12px;border-radius:3px;background:#F4A6A0"></div> Current state</div>
                <div style="display:flex;align-items:center;gap:4px"><div style="width:12px;height:12px;border-radius:3px;background:#93B5FF"></div> With Backbase</div>
              </div>'''

        # Summary boxes
        summary_html = ""
        if summary_boxes:
            box_parts = []
            for box in summary_boxes:
                if "stat" in box:
                    source_tag = f'<div style="font-size:10px;color:var(--text-muted);margin-top:4px">{self._escape(box.get("source", ""))}</div>' if box.get("source") else ""
                    box_parts.append(f'''
                      <div style="flex:1;background:rgba(51,102,255,0.06);border:1px solid rgba(51,102,255,0.15);border-radius:10px;padding:14px;text-align:center">
                        <div style="font-size:11px;font-weight:800;letter-spacing:2px;color:var(--accent)">{self._escape(box["label"])}</div>
                        <div style="font-size:36px;font-weight:900;color:var(--accent);margin-top:4px">{self._escape(box["stat"])}</div>
                        {source_tag}
                      </div>''')
                elif "items" in box:
                    items_html = ""
                    for item in box["items"]:
                        items_html += f'<div><div style="font-size:28px;font-weight:900;color:var(--accent)">{self._escape(item["stat"])}</div><div style="font-size:10px;color:var(--text-muted);font-weight:700">{self._escape(item["label"])}</div></div>'
                    items_source = box.get("source", "Redeployed to higher-value work, not headcount reduction")
                    box_parts.append(f'''
                      <div style="flex:1;background:rgba(51,102,255,0.06);border:1px solid rgba(51,102,255,0.15);border-radius:10px;padding:14px;text-align:center">
                        <div style="font-size:11px;font-weight:800;letter-spacing:2px;color:var(--accent)">{self._escape(box["label"])}</div>
                        <div style="display:flex;justify-content:center;gap:20px;margin-top:8px">{items_html}</div>
                        <div style="font-size:9px;color:var(--text-muted);margin-top:6px">{self._escape(items_source)}</div>
                      </div>''')
            summary_html = f'<div style="display:flex;gap:16px;margin-top:16px">{"".join(box_parts)}</div>'

        footer_html = f'<div class="proc-footer">{self._escape(footer_text)}</div>' if footer_text else ""

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide-accent">
        <div class="slide-accent-y"></div>
        <div class="slide-accent-x"></div>
      </div>
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div style="display:flex;flex-direction:column;gap:10px;margin-top:12px">
          {bars_html}
        </div>
        {summary_html}
        {footer_html}
      </div>
    </section>''')

    def add_pillar_rows(self, title: str, subtitle: str = "", section_label: str = "",
                        columns: list = None, rows: list = None):
        """Three-column pillar rows (What's Happening → Why → What To Do).
        columns: [left_header, mid_header, right_header]
        rows: [{left, left_detail, mid, mid_detail, right, right_detail, left_accent, right_accent}]
        """
        columns = columns or ["What's Happening", "Why It's Happening", "What To Do"]
        rows = rows or []
        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ""
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""

        rows_html = ""
        for r in rows:
            la = r.get("left_accent", "red")
            ra = r.get("right_accent", "blue")
            rows_html += f'''
            <div class="pillar-row">
              <div class="pillar-cell pillar-cell--{la}">
                <div class="pillar-cell__title">{self._escape(r.get("left", ""))}</div>
                <div class="pillar-cell__detail">{self._escape(r.get("left_detail", ""))}</div>
              </div>
              <div class="pillar-arrow">&rarr;</div>
              <div class="pillar-cell pillar-cell--neutral">
                <div class="pillar-cell__title">{self._escape(r.get("mid", ""))}</div>
                <div class="pillar-cell__detail">{self._escape(r.get("mid_detail", ""))}</div>
              </div>
              <div class="pillar-arrow" style="color:var(--action-blue)">&rarr;</div>
              <div class="pillar-cell pillar-cell--{ra}">
                <div class="pillar-cell__title">{self._escape(r.get("right", ""))}</div>
                <div class="pillar-cell__detail">{self._escape(r.get("right_detail", ""))}</div>
              </div>
            </div>'''

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div class="pillar-headers">
          <div class="pillar-header pillar-header--red">{self._escape(columns[0])}</div>
          <div style="width:20px"></div>
          <div class="pillar-header">{self._escape(columns[1])}</div>
          <div style="width:20px"></div>
          <div class="pillar-header pillar-header--blue">{self._escape(columns[2])}</div>
        </div>
        <div class="pillar-rows">
          {rows_html}
        </div>
      </div>
    </section>''')

    def add_financial_table(self, title: str, subtitle: str = "", section_label: str = "",
                            headers: list = None, rows: list = None,
                            total_row: list = None, footer_text: str = ""):
        """Financial table with headers and rows. total_row is bold/highlighted."""
        headers = headers or []
        rows = rows or []
        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ""
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""

        th_html = "".join(f'<th>{self._escape(h)}</th>' for h in headers)
        rows_html = ""
        for row in rows:
            highlight = ' class="fin-highlight"' if row.get("highlight") else ""
            cells = "".join(f'<td>{self._escape(str(c))}</td>' for c in row.get("cells", []))
            rows_html += f'<tr{highlight}>{cells}</tr>\n'

        total_html = ""
        if total_row:
            cells = "".join(f'<td>{self._escape(str(c))}</td>' for c in total_row)
            total_html = f'<tr class="fin-total">{cells}</tr>'

        footer_html = f'<div class="fin-footer">{self._escape(footer_text)}</div>' if footer_text else ""

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div class="fin-table-wrap">
          <table class="fin-table">
            <thead><tr>{th_html}</tr></thead>
            <tbody>
              {rows_html}
              {total_html}
            </tbody>
          </table>
        </div>
        {footer_html}
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Comparison Matrix (criteria left, options across)
    # ──────────────────────────────────────────

    def add_comparison_matrix(self, title: str, subtitle: str = "", section_label: str = "",
                               options: list = None, criteria: list = None,
                               summaries: list = None, footer_text: str = ""):
        """Horizontal comparison matrix: criteria rows × option columns.
        options: [{name, accent (hex)}]
        criteria: [{label, cells: [str per option]}]  — supports **bold** in cells
        summaries: [{label, sub?, accent}] per option — bottom boxes
        """
        options = options or []
        criteria = criteria or []
        summaries = summaries or []
        n = len(options)

        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ""
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""

        # Accent map
        accent_map = {"red": "#DC2626", "blue": "#1A5AFF", "green": "#16A34A", "amber": "#D97706", "cyan": "#0891B2", "purple": "#7C3AED"}

        # Header row
        hdr_cells = '<div style="flex:0 0 200px"></div>'
        for opt in options:
            ac = opt.get('accent', 'blue')
            color = accent_map.get(ac, ac)
            border = f'border-bottom:3px solid {color};' if ac == 'blue' else f'border-bottom:2px solid #E0E4E8;'
            hdr_cells += f'<div style="flex:1;text-align:center;padding:8px 4px;{border}"><span style="font-size:13px;font-weight:800;color:{color};text-transform:uppercase;letter-spacing:0.05em">{self._escape(opt["name"])}</span></div>'
        header_html = f'<div style="display:flex;gap:8px;margin-bottom:4px">{hdr_cells}</div>'

        # Criteria rows
        rows_html = ""
        for ri, cr in enumerate(criteria):
            bg = "#FAFBFC" if ri % 2 == 0 else "#FFFFFF"
            cells = f'<div style="flex:0 0 200px;font-size:11px;font-weight:700;color:var(--text-main);padding:10px 12px;display:flex;align-items:center">{self._escape(cr["label"])}</div>'
            for ci, cell_text in enumerate(cr.get("cells", [])):
                # Render rich text
                rendered = self._render_rich_text(cell_text)
                cells += f'<div style="flex:1;font-size:11px;color:var(--text-main);padding:10px 12px;line-height:1.5">{rendered}</div>'
            rows_html += f'<div style="display:flex;gap:8px;background:{bg};border-radius:6px;margin-bottom:2px">{cells}</div>'

        # Summary boxes
        summary_html = ""
        if summaries:
            summary_cells = '<div style="flex:0 0 200px"></div>'
            for si, sm in enumerate(summaries):
                ac = sm.get('accent', 'blue')
                color = accent_map.get(ac, ac)
                bg_color = f'{color}0D'  # 5% opacity
                border_color = f'{color}30'
                label = self._escape(sm.get('label', ''))
                sub = self._escape(sm.get('sub', ''))
                fill = f'background:rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.06);border:1.5px solid rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.2);'
                summary_cells += f'''<div style="flex:1;{fill}border-radius:8px;padding:10px;text-align:center">
                    <div style="font-size:9px;font-weight:800;letter-spacing:0.08em;color:{color};text-transform:uppercase">{label}</div>
                    <div style="font-size:13px;font-weight:800;color:var(--text-main);margin-top:4px">{sub}</div>
                </div>'''
            summary_html = f'<div style="display:flex;gap:8px;margin-top:12px">{summary_cells}</div>'

        # Footer
        footer_html = ""
        if footer_text:
            rendered_footer = self._render_rich_text(footer_text)
            footer_html = f'<div style="background:#F0F4FF;border-radius:8px;padding:10px 16px;margin-top:14px;font-size:11px;color:#001C3D;text-align:center;line-height:1.5">{rendered_footer}</div>'

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide-accent">
        <div class="slide-accent-y"></div>
        <div class="slide-accent-x"></div>
      </div>
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div style="margin-top:12px">
          {header_html}
          {rows_html}
          {summary_html}
        </div>
        {footer_html}
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Alert / Flag Cards (severity-coded)
    # ──────────────────────────────────────────

    def add_alert_cards(self, title: str, subtitle: str = "", section_label: str = "",
                        alerts: list = None):
        """Color-coded alert cards with left border accent.
        Each alert: {severity: red|amber|blue|green, title, body}"""
        alerts = alerts or []
        severity_colors = {
            'red': ('#E02020', '#FDF0F0', 'RED'),
            'amber': ('#D97706', '#FEF9E7', 'AMBER'),
            'blue': ('#1A5AFF', '#EEF2FF', 'BLUE'),
            'green': ('#2ECC71', '#EAFAF1', 'GREEN'),
        }
        cards_html = ''
        for a in alerts:
            sev = a.get('severity', 'blue')
            color, bg, label = severity_colors.get(sev, severity_colors['blue'])
            cards_html += f'''
        <div style="background:{bg}; border-left:4px solid {color}; border-radius:var(--radius); padding:28px 32px; margin-bottom:16px;">
          <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
            <span style="background:{color}; color:#fff; font-size:11px; font-weight:700; padding:3px 10px; border-radius:4px; letter-spacing:0.05em;">{label}</span>
            <span style="font-weight:700; font-size:18px; color:var(--text-main);">{self._escape(a.get("title", ""))}</span>
          </div>
          <p style="font-size:15px; color:var(--text-main); line-height:1.65; margin:0;">{self._escape(a.get("body", ""))}</p>
        </div>'''

        label_html = f'<div class="slide-label">{self._escape(section_label.upper())}</div>' if section_label else ''
        sub_html = f'<p style="font-size:15px; color:var(--text-muted); margin-bottom:28px;">{self._escape(subtitle)}</p>' if subtitle else ''

        self.scenes.append(f'''
    <section class="slide">
      <div style="padding:5% 6%;">
        {label_html}
        <h2 class="slide-title" style="margin-bottom:8px;">{self._escape(title)}</h2>
        {sub_html}
        <div style="margin-top:16px;">
          {cards_html}
        </div>
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Architecture Stack (layered rows with pills)
    # ──────────────────────────────────────────

    def add_architecture_stack(self, title: str, subtitle: str = "", section_label: str = "",
                                layers: list = None):
        """Layered architecture diagram with pills.
        Each layer: {label, items: [{name, color, border}], bg, dark}
        color/border: hex color for pill text/border. bg: row background. dark: navy bg with white text."""
        layers = layers or []
        layers_html = ''
        for layer in layers:
            is_dark = layer.get('dark', False)
            bg = layer.get('bg', '#F0F4FF' if not is_dark else '#001C3D')
            text_color = '#FFFFFF' if is_dark else '#001C3D'
            border_left_color = layer.get('accent', '#1A5AFF')
            label = layer.get('label', '')
            sub_label = layer.get('sub_label', '')

            pills_html = ''
            for item in layer.get('items', []):
                pill_border = item.get('border', '#D1D5DB')
                pill_color = item.get('color', text_color)
                pill_bg = item.get('bg', 'rgba(255,255,255,0.9)' if not is_dark else 'rgba(255,255,255,0.15)')
                name = item.get('name', '')
                pills_html += f'''
              <span style="display:inline-flex; align-items:center; gap:6px; padding:8px 18px; border:1.5px solid {pill_border}; border-radius:8px; font-size:13px; font-weight:500; color:{pill_color}; background:{pill_bg}; white-space:nowrap;">{self._escape(name)}</span>'''

            sub_html = f'<div style="font-size:11px; font-weight:700; letter-spacing:0.08em; color:{text_color}; opacity:0.6; margin-bottom:8px;">{self._escape(sub_label.upper())}</div>' if sub_label else ''

            layers_html += f'''
          <div style="background:{bg}; border-left:3px solid {border_left_color}; border-radius:var(--radius); padding:20px 28px; margin-bottom:12px;">
            <div style="font-size:13px; font-weight:700; letter-spacing:0.08em; color:{text_color}; text-transform:uppercase; margin-bottom:12px;">{self._escape(label)}</div>
            {sub_html}
            <div style="display:flex; flex-wrap:wrap; gap:10px;">
              {pills_html}
            </div>
          </div>'''

        label_html = f'<div class="slide-label">{self._escape(section_label.upper())}</div>' if section_label else ''
        subtitle_html = f'<p style="font-size:15px; color:var(--text-muted); margin-bottom:20px;">{self._escape(subtitle)}</p>' if subtitle else ''

        self.scenes.append(f'''
    <section class="slide">
      <div style="padding:5% 6%;">
        {label_html}
        <h2 class="slide-title" style="margin-bottom:8px;">{self._escape(title)}</h2>
        {subtitle_html}
        <div style="margin-top:12px;">
          {layers_html}
        </div>
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Pillar-to-Platform Map (pillars left → platform boxes right)
    # ──────────────────────────────────────────

    def add_pillar_platform_map(self, title: str, subtitle: str = "", section_label: str = "",
                                 pillars: list = None, footer_left: str = "", footer_right: str = ""):
        """Pillar-to-platform visual: pillars on left with arrows pointing to platform capability boxes on right.
        Each pillar: {name, sub (optional), accent (hex), items: [{name, sub (optional)}]}
        Items within a pillar are rendered as blue-bordered boxes.
        Use accent to color the pillar label pill on the left."""
        pillars = pillars or []
        rows_html = ''
        for p in pillars:
            accent = p.get('accent', '#1A5AFF')
            name = p.get('name', '')
            sub = p.get('sub', '')
            items = p.get('items', [])
            is_wide = len(items) <= 1  # single wide box vs multiple boxes

            # Left pillar pill
            sub_html = f'<div style="font-size:10px; color:#5C6E84; margin-top:2px;">{self._escape(sub)}</div>' if sub else ''
            left_pill = f'''<div style="background:#F5F7F9; border:1.5px solid {accent}; border-radius:10px; padding:10px 16px; min-width:160px;">
              <div style="font-size:13px; font-weight:700; color:{accent};">{self._escape(name)}</div>
              {sub_html}
            </div>'''

            # Right boxes
            if is_wide and items:
                item = items[0]
                item_sub = f'<div style="font-size:10px; color:#5C6E84; margin-top:2px;">{self._escape(item.get("sub", ""))}</div>' if item.get('sub') else ''
                boxes_html = f'''<div style="flex:1; background:#EBF0FF; border:1.5px solid #1A5AFF; border-radius:10px; padding:12px 20px; text-align:center;">
                  <div style="font-size:13px; font-weight:600; color:#001C3D;">{self._escape(item.get("name", ""))}</div>
                  {item_sub}
                </div>'''
            else:
                boxes_inner = ''
                for item in items:
                    item_sub = f'<div style="font-size:10px; color:#5C6E84; margin-top:2px;">{self._escape(item.get("sub", ""))}</div>' if item.get('sub') else ''
                    boxes_inner += f'''<div style="flex:1; background:#EBF0FF; border:1.5px solid #1A5AFF; border-radius:10px; padding:10px 14px; text-align:center; min-width:120px;">
                    <div style="font-size:12px; font-weight:600; color:#001C3D;">{self._escape(item.get("name", ""))}</div>
                    {item_sub}
                  </div>'''
                boxes_html = f'<div style="display:flex; gap:8px; flex:1;">{boxes_inner}</div>'

            # Optional section label above boxes (e.g. "SINGLE PANE OF GLASS")
            section_above = ''
            if p.get('section_above'):
                section_above = f'<div style="font-size:10px; font-weight:700; letter-spacing:0.08em; color:#5C6E84; text-transform:uppercase; margin-bottom:6px; padding-left:4px;">{self._escape(p["section_above"])}</div>'

            rows_html += f'''
          <div style="display:flex; align-items:center; gap:16px; margin-bottom:10px;">
            {left_pill}
            <div style="color:#1A5AFF; font-size:18px; flex-shrink:0;">&#8594;</div>
            <div style="flex:1;">
              {section_above}
              {boxes_html}
            </div>
          </div>'''

        # Footer boxes
        footer_html = ''
        if footer_left or footer_right:
            fl = f'<div style="flex:1; font-size:11px; color:#001C3D; line-height:1.5;"><strong>Schroders retains:</strong> {self._escape(footer_left)}</div>' if footer_left else ''
            fr = f'<div style="flex:1; background:#FFF5F5; border:1px solid #FCA5A5; border-radius:8px; padding:10px 14px; font-size:11px; color:#DC2626; line-height:1.5;"><strong>What gets retired:</strong> {self._escape(footer_right)}</div>' if footer_right else ''
            footer_html = f'<div style="display:flex; gap:16px; margin-top:16px;">{fl}{fr}</div>'

        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ''
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ''

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div style="margin-top:8px;">
          {rows_html}
        </div>
        {footer_html}
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Architecture Boxes — Current State vs Target State (side-by-side box diagrams)
    # ──────────────────────────────────────────

    def add_architecture_boxes(self, title: str, subtitle: str = "", section_label: str = "",
                                left_title: str = "Current State", right_title: str = "Target State",
                                left_layers: list = None, right_layers: list = None,
                                legend: list = None, footer_text: str = ""):
        """Side-by-side architecture comparison with colored box diagrams.
        Each side has layers: [{label, items: [{name, sub, color, bg, border}]}]
        color defaults: left uses soft reds/grays, right uses soft blues.
        legend: [{label, color}] for the bottom legend bar."""
        left_layers = left_layers or []
        right_layers = right_layers or []

        def render_side(layers, side='left'):
            html = ''
            for layer in layers:
                label = layer.get('label', '')
                items = layer.get('items', [])
                is_banner = layer.get('banner', False)
                banner_color = layer.get('banner_color', '#1A5AFF' if side == 'right' else '#DC2626')
                banner_bg = layer.get('banner_bg', '#EBF0FF' if side == 'right' else '#FFF5F5')
                banner_border = layer.get('banner_border', '#1A5AFF' if side == 'right' else '#FCA5A5')

                if label:
                    html += f'<div style="font-size:10px; font-weight:700; letter-spacing:0.06em; color:{banner_color if side == "right" else "#DC2626" if "No " in label or "X " in label else "#5C6E84"}; text-transform:uppercase; margin:10px 0 5px 0;">{self._escape(label)}</div>'

                if is_banner:
                    banner_text_color = layer.get('banner_text_color', banner_color)
                    html += f'''<div style="background:{banner_bg}; border:1.5px solid {banner_border}; border-radius:8px; padding:10px 16px; margin-bottom:6px; text-align:center;">
                      <div style="font-size:12px; font-weight:700; color:{banner_text_color};">{self._escape(items[0].get("name", "") if items else "")}</div>
                      <div style="font-size:10px; color:#5C6E84; margin-top:2px;">{self._escape(items[0].get("sub", "") if items else "")}</div>
                    </div>'''
                else:
                    boxes = ''
                    for item in items:
                        bg = item.get('bg', '#EBF0FF' if side == 'right' else '#F5F7F9')
                        border = item.get('border', '#1A5AFF' if side == 'right' else '#D1D5DB')
                        color = item.get('color', '#001C3D')
                        is_dark_box = item.get('dark', False)
                        if is_dark_box:
                            bg = item.get('bg', '#001C3D')
                            color = '#FFFFFF'
                            border = item.get('border', '#001C3D')
                        is_retired = item.get('retired', False)
                        retired_bg = '#FFF5F5' if is_retired else bg
                        retired_border = '#FCA5A5' if is_retired else border
                        retired_color = '#DC2626' if is_retired else color
                        sub = f'<div style="font-size:9px; color:{"#FBBF24" if is_dark_box else "#5C6E84"}; margin-top:1px;">{self._escape(item.get("sub", ""))}</div>' if item.get('sub') else ''
                        boxes += f'''<div style="flex:1; min-width:80px; background:{retired_bg if is_retired else bg}; border:1.5px solid {retired_border if is_retired else border}; border-radius:8px; padding:8px 10px; text-align:center;">
                        <div style="font-size:11px; font-weight:600; color:{retired_color if is_retired else color};">{self._escape(item.get("name", ""))}</div>
                        {sub}
                      </div>'''
                    html += f'<div style="display:flex; gap:6px; margin-bottom:6px;">{boxes}</div>'
            return html

        left_html = render_side(left_layers, 'left')
        right_html = render_side(right_layers, 'right')

        # Legend
        legend_html = ''
        if legend:
            items = ''.join(f'<span style="display:inline-flex; align-items:center; gap:5px; margin-right:16px;"><span style="display:inline-block; width:12px; height:12px; border-radius:3px; background:{l.get("color", "#D1D5DB")}; border:1px solid {l.get("border", l.get("color", "#D1D5DB"))};"></span><span style="font-size:10px; color:#5C6E84;">{self._escape(l.get("label", ""))}</span></span>' for l in legend)
            legend_html = f'<div style="display:flex; flex-wrap:wrap; justify-content:center; gap:4px; margin-top:12px;">{items}</div>'

        footer_html = f'<div style="background:#F0F4FF; border-radius:8px; padding:10px 16px; margin-top:10px; font-size:11px; color:#001C3D; text-align:center; line-height:1.5;">{self._escape(footer_text)}</div>' if footer_text else ''

        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ''
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ''

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div style="display:flex; gap:24px; margin-top:8px;">
          <div style="flex:1;">
            <div style="font-size:12px; font-weight:700; letter-spacing:0.06em; color:#DC2626; text-transform:uppercase; margin-bottom:8px; text-align:center;">{self._escape(left_title)}</div>
            {left_html}
          </div>
          <div style="display:flex; align-items:center; font-size:24px; color:#5C6E84; padding:0 4px;">&#8594;</div>
          <div style="flex:1;">
            <div style="font-size:12px; font-weight:700; letter-spacing:0.06em; color:#1A5AFF; text-transform:uppercase; margin-bottom:8px; text-align:center;">{self._escape(right_title)}</div>
            {right_html}
          </div>
        </div>
        {legend_html}
        {footer_html}
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Clean Stat Cards (lightweight)
    # ──────────────────────────────────────────

    def add_context_stats(self, title: str, subtitle: str = "", section_label: str = "",
                          body: str = "", stats: list = None):
        """Context section with body text and clean stat cards.
        Each stat: {number, label}"""
        stats = stats or []
        label_html = f'<div class="slide-label">{self._escape(section_label.upper())}</div>' if section_label else ''
        body_html = f'<p style="font-size:17px; color:var(--text-main); line-height:1.7; margin-bottom:28px; max-width:90%;">{self._escape(body)}</p>' if body else ''

        cards_html = ''
        n = len(stats)
        for s in stats:
            cards_html += f'''
          <div style="flex:1; min-width:180px; background:var(--bg-gray); border-radius:var(--radius); padding:28px 24px;">
            <div style="font-size:36px; font-weight:700; color:var(--action-blue); margin-bottom:6px;">{self._escape(str(s.get("number", "")))}</div>
            <div style="font-size:14px; color:var(--text-muted);">{self._escape(s.get("label", ""))}</div>
          </div>'''

        subtitle_html = f'<p style="font-size:15px; color:var(--text-muted); margin-bottom:20px;">{self._escape(subtitle)}</p>' if subtitle else ''

        self.scenes.append(f'''
    <section class="slide">
      <div style="padding:5% 6%;">
        {label_html}
        <h2 class="slide-title" style="margin-bottom:8px;">{self._escape(title)}</h2>
        {subtitle_html}
        {body_html}
        <div style="display:flex; gap:16px; flex-wrap:wrap;">
          {cards_html}
        </div>
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Proven Impact (3 value dimensions + trusted logos)
    # ──────────────────────────────────────────

    def add_proven_impact(self, title: str, subtitle: str = "", section_label: str = "",
                           dimensions: list = None, trusted_logos: list = None):
        """3 value dimension boxes with multiple stats each, plus trusted logo row.
        dimensions: [{title, accent, stats: [{value, label}], source}]
        trusted_logos: list of brand name strings (rendered as styled text)
        """
        dimensions = dimensions or []
        trusted_logos = trusted_logos or []
        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ""
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ""

        accent_colors = {"green": "#16A34A", "blue": "#1A5AFF", "purple": "#7C3AED", "cyan": "#0891B2", "red": "#DC2626", "amber": "#D97706"}
        bg_colors = {"green": "#F0FDF4", "blue": "#EBF0FF", "purple": "#F5F3FF", "cyan": "#F0FDFA", "red": "#FFF5F5", "amber": "#FFFBEB"}

        dims_html = ""
        for d in dimensions:
            accent = d.get("accent", "blue")
            ac = accent_colors.get(accent, "#1A5AFF")
            bg = bg_colors.get(accent, "#EBF0FF")
            stats_html = ""
            for s in d.get("stats", []):
                stats_html += f'<div style="text-align:center;flex:1;"><div style="font-size:min(3vw, 28px);font-weight:900;color:{ac};">{self._escape(s.get("value",""))}</div><div style="font-size:9px;color:var(--text-muted);margin-top:2px;">{self._escape(s.get("label",""))}</div></div>'
            source = d.get("source", "")
            source_html = f'<div style="font-size:8px;color:var(--text-muted);margin-top:8px;font-style:italic;">{self._escape(source)}</div>' if source else ""
            dims_html += f'''
              <div style="flex:1;border:1.5px solid {ac}30;border-radius:12px;padding:14px 16px;background:{bg}20;border-top:3px solid {ac};">
                <div style="font-size:10px;font-weight:800;letter-spacing:1.5px;color:{ac};text-transform:uppercase;margin-bottom:10px;">{self._escape(d.get("title",""))}</div>
                <div style="display:flex;gap:8px;align-items:flex-start;">{stats_html}</div>
                {source_html}
              </div>'''

        # Trusted logos as styled text
        logos_html = ""
        if trusted_logos:
            logo_items = ""
            fonts = {"Coutts": "font-family:Georgia,serif;font-style:italic;font-weight:700;color:#1B3A4B;font-size:22px;",
                      "Evelyn": "font-family:'Inter',sans-serif;font-weight:400;color:#5C6E84;font-size:20px;letter-spacing:1px;",
                      "Pictet": "font-family:'Inter',sans-serif;font-weight:800;color:#001C3D;font-size:20px;letter-spacing:2px;text-transform:uppercase;"}
            for logo in trusted_logos:
                style = fonts.get(logo, "font-weight:700;color:#5C6E84;font-size:20px;")
                logo_items += f'<span style="{style}">{self._escape(logo)}</span>'
            logos_html = f'''
              <div style="margin-top:20px;padding-top:14px;border-top:1px solid #E0E4E8;text-align:center;">
                <div style="font-size:9px;font-weight:700;letter-spacing:2px;color:var(--text-muted);text-transform:uppercase;margin-bottom:12px;">Trusted by leading wealth & private banks</div>
                <div style="display:flex;justify-content:center;align-items:center;gap:50px;">{logo_items}</div>
              </div>'''

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div style="display:flex;gap:16px;margin-top:16px;">
          {dims_html}
        </div>
        {logos_html}
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Before → After Metric Cards (2×3 grid)
    # ──────────────────────────────────────────

    def add_before_after_cards(self, title: str, subtitle: str = "", section_label: str = "",
                                cards: list = None, footer_text: str = ""):
        """Grid of before→after metric cards. 2×3 layout.
        Each card: {title, before, before_label, after, after_label, improvement, improvement_color}
        improvement_color: green (positive) or red (negative), default green."""
        cards = cards or []
        label_html = f'<span class="label label--dark">{self._escape(section_label.upper())}</span>' if section_label else ''
        subtitle_html = f'<p class="slide-subtitle">{self._escape(subtitle)}</p>' if subtitle else ''
        footer_html = f'''
        <div style="background:var(--bg-gray); border-radius:var(--radius); padding:16px 24px; margin-top:20px; text-align:center;">
          <p style="font-size:13px; color:var(--text-muted); margin:0; line-height:1.6;">{self._escape(footer_text)}</p>
        </div>''' if footer_text else ''

        cards_html = ''
        for c in cards:
            imp_color = c.get('improvement_color', 'green')
            color_map = {'green': '#0D7C3D', 'red': '#D93025', 'blue': '#1A5AFF'}
            imp_css_color = color_map.get(imp_color, '#0D7C3D')
            before_color = c.get('before_color', '#D93025')
            after_color = c.get('after_color', '#0D7C3D')

            cards_html += f'''
            <div style="background:#FFFFFF; border:1.5px solid #E5E7EB; border-radius:var(--radius); padding:24px 20px; text-align:center;">
              <div style="font-size:11px; font-weight:700; letter-spacing:0.08em; color:var(--text-muted); text-transform:uppercase; margin-bottom:16px;">{self._escape(c.get("title", ""))}</div>
              <div style="display:flex; align-items:baseline; justify-content:center; gap:12px; margin-bottom:4px;">
                <div style="font-size:32px; font-weight:700; color:{before_color};">{self._escape(c.get("before", ""))}</div>
                <div style="font-size:16px; color:var(--text-muted);">→</div>
                <div style="font-size:32px; font-weight:700; color:{after_color};">{self._escape(c.get("after", ""))}</div>
              </div>
              <div style="display:flex; justify-content:center; gap:24px; margin-bottom:10px;">
                <span style="font-size:10px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em;">{self._escape(c.get("before_label", "Today"))}</span>
                <span style="font-size:10px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em;">{self._escape(c.get("after_label", "With Platform"))}</span>
              </div>
              <div style="font-size:13px; font-weight:600; color:{imp_css_color};">{self._escape(c.get("improvement", ""))}</div>
            </div>'''

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content">
        {label_html}
        <h2 class="slide-title">{self._escape(title)}</h2>
        {subtitle_html}
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:16px;">
          {cards_html}
        </div>
        {footer_html}
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Recommendation / Summary Slide
    # ──────────────────────────────────────────

    def add_recommendation(self, section_label: str, title: str, body: str = "",
                            stats: list = None, next_step: str = "", closing: str = ""):
        """Rich recommendation slide with summary stats and next steps.
        stats: [{value, label, sub?}] — displayed as large numbers in a row
        """
        stats = stats or []
        stats_html = ""
        accent_colors = ["#16A34A", "#1A5AFF", "#7C3AED", "#0891B2"]
        for i, s in enumerate(stats):
            ac = accent_colors[i % len(accent_colors)]
            sub_html = f'<div style="font-size:8px;color:var(--text-muted);margin-top:1px;">{self._escape(s.get("sub",""))}</div>' if s.get("sub") else ""
            stats_html += f'''
              <div style="flex:1;text-align:center;{'border-left:1px solid #E0E4E8;' if i > 0 else ''}padding:0 12px;">
                <div style="font-size:min(4vw, 36px);font-weight:900;color:{ac};">{self._escape(s.get("value",""))}</div>
                <div style="font-size:10px;font-weight:700;letter-spacing:1.5px;color:var(--text-muted);text-transform:uppercase;margin-top:4px;">{self._escape(s.get("label",""))}</div>
                {sub_html}
              </div>'''

        next_html = ""
        if next_step:
            next_html = f'''
            <div style="margin-top:24px;padding-top:16px;border-top:2px solid #E0E4E8;text-align:center;">
              <p style="font-size:13px;color:var(--text-muted);line-height:1.7;max-width:75%;margin:0 auto;">{self._render_rich_text(next_step)}</p>
            </div>'''

        closing_html = ""
        if closing:
            closing_html = f'<p style="font-size:12px;color:var(--text-muted);text-align:center;margin-top:12px;font-style:italic;">{self._escape(closing)}</p>'

        self.scenes.append(f'''
    <section class="slide slide--light">
      <div class="slide__inner slide__inner--content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;min-height:80vh;">
        <span class="label label--dark" style="margin-bottom:8px;">{self._escape(section_label.upper())}</span>
        <h2 class="slide-title" style="text-align:center;max-width:80%;">{self._escape(title)}</h2>
        <p style="font-size:14px;color:var(--text-muted);max-width:70%;margin:12px auto 28px;line-height:1.7;text-align:center;">{self._escape(body)}</p>
        <div style="display:flex;align-items:flex-start;gap:0;width:80%;max-width:700px;margin:0 auto;">
          {stats_html}
        </div>
        {next_html}
        {closing_html}
      </div>
    </section>''')

    # ──────────────────────────────────────────
    # Render
    # ──────────────────────────────────────────

    def render(self) -> str:
        n = len(self.scenes)

        # Inject chrome into each scene: top bar + blue accent (light), footer (all)
        scenes_with_footer = []
        for i, scene in enumerate(self.scenes):
            is_dark = 'slide--dark' in scene
            logo_color = '#FFFFFF' if is_dark else '#001C3D'
            num_color = 'rgba(255,255,255,0.5)' if is_dark else 'var(--text-muted)'

            # Chrome: blue accent square (light slides only) — no top bar
            chrome = ''
            if not is_dark:
                chrome = '''
      <div class="slide-accent">
        <div class="slide-accent-y"></div>
        <div class="slide-accent-x"></div>
      </div>'''

            # Footer: Backbase wordmark SVG (correct notched B) + page number
            logo_fill = "#FFFFFF" if is_dark else "#001C3D"
            footer = f'''
      <div class="slide-footer">
        <svg xmlns="http://www.w3.org/2000/svg" height="20" fill="none" viewBox="0 0 142 24" class="slide-footer__logo">
          <g clip-path="url(#bb{i})">
            <path fill="{logo_fill}" d="M3.457 7.552h3.457V.689H0v3.413h3.457v3.45Z"></path>
            <path fill="{logo_fill}" d="M14.193 11.909v-.545c3.384-.472 4.257-2.687 4.257-4.901 0-2.724-1.856-5.665-6.477-5.774H9.207v3.45h2.766c2.438.036 2.947 1.597 2.911 2.868-.073 2.796-1.347 2.869-3.494 2.905H3.457v13.797h8.26c5.569 0 7.425-3.159 7.425-6.427 0-2.832-.983-4.865-4.95-5.373Zm-2.366 8.315H6.951v-6.972h4.84c2.911 0 3.857.545 3.857 3.522.037 2.505-.91 3.413-3.82 3.45Zm10.007-2.142c0-2.94 1.929-5.918 6.077-5.918 2.366 0 3.712.69 4.695 2.033V9.804h-8.807v-3.05H35.99V20.26h2.038v3.376h-5.422V21.93c-1.02 1.343-2.33 2.033-4.695 2.033-4.148.037-6.077-2.94-6.077-5.882Zm10.772 0c0-1.706-1.201-2.868-3.712-2.868s-3.712 1.198-3.712 2.868 1.2 2.869 3.712 2.869c2.511 0 3.712-1.162 3.712-2.869Zm6.951-2.869c0-5.302 2.62-8.787 7.605-8.787 4.44 0 7.06 2.723 7.06 6.753h-3.384c-.145-2.106-.837-3.703-3.494-3.703-3.166 0-4.367 1.343-4.367 5.736 0 4.394 1.201 5.737 4.367 5.737 2.657 0 3.349-1.634 3.494-3.703h3.384c0 4.03-2.62 6.753-7.06 6.753-4.985 0-7.605-3.485-7.605-8.786Zm21.251 1.562v6.898h-3.384V0h3.384v13.725h2.657l4.73-6.972h4.113l-5.823 8.497 5.787 8.423h-4.113l-4.73-6.898h-2.62Zm29.879-1.562c0 4.975-1.929 8.787-7.424 8.787-2.365 0-4.04-.908-5.058-2.36v2.033H74.82V0h3.385v8.787c1.019-1.453 2.693-2.36 5.058-2.36 5.495 0 7.424 3.812 7.424 8.786Zm-3.384 0c0-4.066-1.238-5.736-4.55-5.736-3.311 0-4.548 1.67-4.548 5.736 0 4.067 1.237 5.737 4.549 5.737 3.311 0 4.549-1.67 4.549-5.737Zm5.568 2.869c0-2.94 1.929-5.918 6.078-5.918 2.365 0 3.675.69 4.694 2.033V9.804h-8.807v-3.05h12.191V20.26h2.038v3.376h-5.422V21.93c-1.019 1.343-2.329 2.033-4.695 2.033-4.148.037-6.077-2.94-6.077-5.882Zm10.772 0c0-1.706-1.237-2.868-3.675-2.868-2.439 0-3.676 1.198-3.676 2.868s1.237 2.869 3.675 2.869c2.439 0 3.676-1.162 3.676-2.869Zm7.97 3.738v-3.412c3.094 1.924 4.695 2.541 7.169 2.541 2.184 0 2.985-.944 2.985-1.997 0-1.198-.874-1.815-4.004-2.505-4.84-1.053-6.15-2.65-6.15-5.301 0-2.796 2.402-4.72 6.041-4.72 2.257 0 4.513.617 6.15 1.743v3.05c-2.474-1.235-4.658-1.743-6.514-1.743-1.746 0-2.292.726-2.292 1.597 0 .944.436 1.598 3.311 2.36 5.022 1.344 6.842 2.397 6.842 5.52 0 2.868-2.402 5.082-6.369 5.082-2.62-.036-4.694-.544-7.169-2.214Zm15.758-6.607c0-5.302 2.111-8.787 7.315-8.787 5.204 0 7.315 3.159 7.315 8.46v1.851h-11.173c.219 2.36 1.201 4.212 5.132 4.212 1.346 0 2.692 0 4.876-.617v2.977c-2.657.69-3.603.69-4.876.69-7.643 0-8.589-5.446-8.589-8.786Zm11.245-1.525c-.073-2.942-1.201-4.212-3.93-4.212-2.73 0-3.749 1.488-3.93 4.211h7.86Z"></path>
          </g>
          <defs><clipPath id="bb{i}"><path fill="#fff" d="M0 0h142v24H0z"/></clipPath></defs>
        </svg>
        <span class="slide-footer__num" style="color:{num_color}">{i+1}</span>
      </div>'''
            # Insert chrome after opening <section...> and footer before closing </section>
            # Find first > after <section to insert chrome
            first_close = scene.index('>') + 1
            scene_with_chrome = scene[:first_close] + chrome + scene[first_close:]
            scene_parts = scene_with_chrome.rstrip().rsplit('</section>', 1)
            scenes_with_footer.append(scene_parts[0] + footer + '\n    </section>')

        scenes_html = "\n".join(scenes_with_footer)

        dots = "\n".join(
            f'      <div class="dot{" active" if i == 0 else ""}" data-idx="{i}"></div>'
            for i in range(n)
        )

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self._escape(self.title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

:root {{
  --navy: #001C3D;
  --action-blue: #1A5AFF;
  --white: #FFFFFF;
  --bg-gray: #F5F7F9;
  --text-main: #001C3D;
  --text-muted: #5C6E84;
  --green: #2ECC71;
  --radius: 16px;
  --radius-pill: 30px;
  --glass-bg: rgba(255, 255, 255, 0.7);
  --card-shadow: 0 10px 30px -5px rgba(0, 28, 61, 0.08);
}}

html, body {{
  height: 100%;
  overflow: hidden;
  font-family: 'Libre Franklin', Helvetica, Arial, sans-serif;
  background: #E8ECF0;
  -webkit-font-smoothing: antialiased;
  display: flex;
  align-items: center;
  justify-content: center;
}}

/* ─── Slide Frame — looks like a slide, centered with border ─── */
.deck {{
  position: relative;
  width: 90vw;
  max-width: 1280px;
  aspect-ratio: 16 / 9;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 40px rgba(0, 28, 61, 0.15), 0 0 0 1px rgba(0, 28, 61, 0.08);
}}

/* In fullscreen, fill the entire screen */
.deck:fullscreen,
.deck:-webkit-full-screen {{
  width: 100vw;
  max-width: none;
  height: 100vh;
  border-radius: 0;
  box-shadow: none;
  background: #FFFFFF;
}}
::backdrop {{ background: #FFFFFF; }}
::-webkit-backdrop {{ background: #FFFFFF; }}

.slide {{
  position: absolute;
  inset: 0;
  display: flex;
  align-items: stretch;
  opacity: 0;
  visibility: hidden;
  transition: none;
  background: var(--white);
  color: var(--text-main);
}}
.slide.active {{
  opacity: 1;
  visibility: visible;
}}

.slide--dark {{ background: var(--navy); color: var(--white); }}
.slide--light {{ background: var(--white); color: var(--text-main); }}

.slide__inner {{
  width: 100%;
  padding: 4% 5% 8% 5%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}}

/* ─── Slide Chrome — blue accent + footer ─── */
/* Stepped accent block (inverted-L: top block + bottom-right step) + axis lines */
/* L-shape accent + axis lines share the same intersection point */
/* L-shape accent — axes are CHILDREN of this element, guaranteed to align */
.slide-accent {{
  position: absolute;
  top: 5%;
  left: 1.8%;
  z-index: 6;
  width: 24px;
  height: 24px;
}}
.slide-accent::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 12px;
  width: 12px;
  height: 12px;
  background: var(--action-blue);
}}
.slide-accent::after {{
  content: '';
  position: absolute;
  top: 12px;
  left: 0;
  width: 24px;
  height: 12px;
  background: var(--action-blue);
}}
/* Axes originate from bottom-RIGHT corner of the L (24px, 24px) */
.slide-accent-y {{
  position: absolute;
  top: 24px;
  left: 24px;
  width: 1px;
  height: 2000px;
  background: rgba(0,28,61,0.06);
  z-index: 4;
}}
.slide-accent-x {{
  position: absolute;
  top: 24px;
  left: 24px;
  width: 2000px;
  height: 1px;
  background: rgba(0,28,61,0.06);
  z-index: 4;
}}

/* ─── Slide Footer — logo + page number, right-aligned ─── */
.slide-footer {{
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  padding: 0 3.5%;
  z-index: 10;
}}
.slide-footer__logo {{
  height: 20px;
  width: auto;
  display: block;
}}
.slide-footer__num {{
  font-size: 14px;
  font-weight: 600;
  opacity: 0.4;
}}

/* ─── Labels ─── */
.label {{
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 3px;
  text-transform: uppercase;
  opacity: 0.7;
  margin-bottom: 16px;
  display: block;
}}
.label--dark {{ color: var(--text-muted); }}

/* ─── Cover ─── */
.slide__inner--cover {{ justify-content: center; }}
.cover-title {{ font-size: clamp(40px, 5vw, 72px); font-weight: 900; line-height: 1.08; margin-bottom: 24px; }}
.cover-date {{ font-size: 16px; opacity: 0.6; }}

/* ─── Divider ─── */
.slide__inner--divider h1 {{ font-size: clamp(32px, 4.5vw, 56px); font-weight: 900; line-height: 1.15; margin-bottom: 40px; }}
.tagline {{ font-size: 16px; opacity: 0.6; position: absolute; bottom: 12%; left: 5%; }}

/* ─── Agenda ─── */
.slide__inner--agenda {{
  flex-direction: row;
  align-items: stretch;
  padding: 0;
}}
.agenda-left {{
  width: 40%;
  padding: 5%;
  padding-bottom: 6%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}
.agenda-title {{ font-size: clamp(28px, 3.5vw, 48px); font-weight: 900; color: var(--text-main); margin-bottom: 16px; }}
.agenda-customer {{ font-size: 16px; color: var(--text-muted); }}
.agenda-right {{
  width: 60%;
  padding: 4% 5%;
  padding-bottom: 6%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}}
.agenda-item {{
  font-size: clamp(16px, 2vw, 22px);
  font-weight: 700;
  color: var(--text-main);
  padding: 16px 0;
  border-bottom: 1px solid #E5E9F0;
  display: flex;
  align-items: center;
  gap: 16px;
}}
.agenda-num {{
  font-size: 12px;
  color: var(--action-blue);
  font-weight: 600;
  min-width: 28px;
}}

/* ─── Content ─── */
.slide__inner--content {{ justify-content: flex-start; padding-top: 7%; overflow-y: auto; }}
.slide-title {{ font-size: clamp(24px, 3vw, 40px); font-weight: 700; margin-bottom: 8px; }}
.slide-subtitle {{ font-size: clamp(14px, 1.5vw, 20px); color: var(--text-muted); margin-bottom: 24px; }}
.content-area {{ flex: 1; }}
.content-list {{ list-style: none; padding: 0; }}
.content-list li {{
  font-size: clamp(14px, 1.3vw, 18px);
  line-height: 1.6;
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
}}
.content-list li::before {{
  content: '';
  position: absolute;
  left: 0;
  top: 16px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--action-blue);
}}

/* ─── Split Comparison ─── */
.slide__inner--split {{ justify-content: flex-start; padding-top: 7%; }}
.split {{
  display: flex;
  gap: 0;
  flex: 1;
  margin-top: 24px;
}}
.split__from, .split__to {{
  flex: 1;
  padding: 24px 32px;
}}
.split__from {{ border-right: 1px solid #E5E9F0; }}
.split h3 {{
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 24px;
}}
.split__from h3 {{ color: #E02020; }}
.split__to h3 {{ color: var(--action-blue); }}
.split ul {{ list-style: none; padding: 0; }}
.split li {{
  font-size: 15px;
  line-height: 1.7;
  padding: 6px 0;
  padding-left: 16px;
  position: relative;
}}
.split__from li::before {{
  content: '\u2715';
  position: absolute;
  left: 0;
  color: #E02020;
  font-size: 11px;
  top: 10px;
}}
.split__to li::before {{
  content: '\u2713';
  position: absolute;
  left: 0;
  color: var(--green);
  font-size: 12px;
  top: 9px;
}}

/* ─── Architecture ─── */
.arch-stack {{ margin-top: 16px; display: flex; flex-direction: column; gap: 6px; }}
.arch-label {{ font-size: 12px; color: var(--text-muted); font-weight: 600; margin-top: 8px; }}
.arch-label--muted {{ opacity: 0.7; }}
.arch-row {{ display: flex; gap: 6px; }}
.arch-box {{
  flex: 1;
  background: var(--navy);
  color: var(--white);
  font-size: 13px;
  font-weight: 600;
  padding: 14px 12px;
  border-radius: 10px;
  text-align: center;
}}
.arch-box--muted {{
  background: var(--bg-gray);
  color: var(--text-main);
  font-weight: 400;
}}
.arch-bar {{
  background: var(--action-blue);
  color: var(--white);
  font-size: clamp(16px, 2vw, 24px);
  font-weight: 700;
  padding: 14px 24px;
  border-radius: 10px;
  text-align: center;
  margin: 4px 0;
}}

/* ─── Stat Cards ─── */
.stat-grid {{ display: flex; gap: 20px; margin-top: 24px; }}
.stat-card {{
  flex: 1;
  background: var(--bg-gray);
  border-radius: var(--radius);
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: var(--card-shadow);
}}
.stat-number {{ font-size: clamp(36px, 4vw, 56px); font-weight: 900; color: var(--action-blue); margin-bottom: 12px; }}
.stat-label {{ font-size: 15px; color: var(--text-main); margin-bottom: 8px; }}
.stat-trend {{ font-size: 12px; font-weight: 700; }}
.trend--up {{ color: var(--green); }}
.trend--neutral {{ color: var(--text-muted); }}

/* ─── Case Study ─── */
.case-label {{
  position: absolute;
  top: 4%;
  right: 5%;
  font-size: 11px;
  font-weight: 700;
  color: #CC0000;
  letter-spacing: 2px;
}}
.legal-footer {{
  position: absolute;
  bottom: 50px;
  left: 5%;
  right: 5%;
  font-size: 9px;
  color: var(--text-muted);
}}

/* ─── Showcase ─── */
.slide__inner--showcase {{
  flex-direction: row;
  align-items: center;
  padding: 0;
}}
.showcase__text {{
  width: 40%;
  padding: 5%;
  padding-bottom: 6%;
}}
.showcase__text h2 {{ font-size: clamp(24px, 3vw, 40px); font-weight: 900; margin: 12px 0; }}
.showcase__text p {{ font-size: 15px; color: var(--text-muted); line-height: 1.6; }}
.showcase__image {{
  width: 60%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3%;
}}
.showcase__image img {{ max-width: 100%; max-height: 100%; border-radius: var(--radius); box-shadow: var(--card-shadow); }}
.showcase__placeholder {{
  width: 80%;
  height: 70%;
  background: var(--bg-gray);
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 16px;
}}

/* ─── Statement Slide ─── */
.slide__inner--statement {{
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 8% 12%;
}}
.statement__text {{
  font-size: clamp(28px, 3.5vw, 48px);
  font-weight: 700;
  line-height: 1.3;
  color: var(--navy);
  max-width: 85%;
}}
.statement__highlight {{
  color: var(--action-blue);
}}

/* ─── Tiles / Cards Grid ─── */
.tile-grid {{ display: grid; gap: 12px; margin-top: 16px; }}
.tile-grid--2 {{ grid-template-columns: 1fr 1fr; }}
.tile-grid--3 {{ grid-template-columns: repeat(3, 1fr); }}
.tile-grid--4 {{ grid-template-columns: repeat(4, 1fr); }}
.tile-grid--5 {{ grid-template-columns: repeat(5, 1fr); }}
.tile {{
  border-radius: 12px;
  padding: 20px 18px;
  border: 1px solid #E5E9F0;
  background: var(--white);
  display: flex;
  flex-direction: column;
  gap: 6px;
}}
.tile--blue {{ border-color: rgba(26,90,255,0.2); background: rgba(26,90,255,0.03); }}
.tile--red {{ border-color: rgba(204,51,51,0.2); background: rgba(204,51,51,0.03); }}
.tile--green {{ border-color: rgba(46,204,113,0.2); background: rgba(46,204,113,0.03); }}
.tile--amber {{ border-color: rgba(217,119,6,0.2); background: rgba(217,119,6,0.04); }}
.tile--purple {{ border-color: rgba(123,47,255,0.2); background: rgba(123,47,255,0.03); }}
.tile--cyan {{ border-color: rgba(8,145,178,0.2); background: rgba(8,145,178,0.03); }}
.tile__pill {{
  display: inline-block;
  font-size: 9px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  width: fit-content;
}}
.tile__pill--blue {{ background: rgba(26,90,255,0.1); color: var(--action-blue); }}
.tile__pill--red {{ background: rgba(204,51,51,0.1); color: #E02020; }}
.tile__pill--green {{ background: rgba(46,204,113,0.1); color: var(--green); }}
.tile__pill--amber {{ background: rgba(217,119,6,0.12); color: #D97706; }}
.tile__pill--purple {{ background: rgba(123,47,255,0.1); color: #7B2FFF; }}
.tile__pill--cyan {{ background: rgba(8,145,178,0.1); color: #0891B2; }}
.tile__stat {{
  font-size: clamp(28px, 3vw, 40px);
  font-weight: 900;
  line-height: 1;
}}
.tile__stat--blue {{ color: var(--action-blue); }}
.tile__stat--red {{ color: #E02020; }}
.tile__stat--green {{ color: var(--green); }}
.tile__stat--amber {{ color: #D97706; }}
.tile__stat--purple {{ color: #7B2FFF; }}
.tile__stat--cyan {{ color: #0891B2; }}
.tile__title {{ font-size: 14px; font-weight: 700; color: var(--text-main); }}
.tile__body {{ font-size: 13px; color: var(--text-muted); line-height: 1.5; }}

/* ─── Process Rows (Before → After) ─── */
.proc-rows {{ display: flex; flex-direction: column; gap: 6px; margin-top: 12px; }}
.proc-row {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--white);
  border: 1px solid #E5E9F0;
}}
.proc-row__label {{ flex: 1; font-size: 14px; font-weight: 700; color: var(--text-main); }}
.proc-row__before {{ font-size: 13px; font-weight: 800; color: #E02020; min-width: 80px; text-align: center; }}
.proc-row__arrow {{ font-size: 14px; color: var(--text-muted); }}
.proc-row__after {{ font-size: 13px; font-weight: 800; color: var(--green); min-width: 80px; text-align: center; }}
.proc-row__saving {{ font-size: 11px; font-weight: 700; color: #0891B2; min-width: 70px; text-align: right; }}
.proc-footer {{ font-size: 11px; color: var(--text-muted); text-align: center; margin-top: 10px; padding: 10px; background: rgba(26,90,255,0.03); border-radius: 10px; border: 1px solid rgba(26,90,255,0.1); }}

/* ─── Pillar Rows (Three Column) ─── */
.pillar-headers {{
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  margin-top: 12px;
}}
.pillar-header {{
  flex: 1;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  text-align: center;
  color: var(--text-main);
}}
.pillar-header--red {{ color: #E02020; }}
.pillar-header--blue {{ color: var(--action-blue); }}
.pillar-rows {{ display: flex; flex-direction: column; gap: 6px; }}
.pillar-row {{
  display: flex;
  gap: 8px;
  align-items: stretch;
}}
.pillar-cell {{
  flex: 1;
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid #E5E9F0;
}}
.pillar-cell--red {{ background: rgba(204,51,51,0.04); border-color: rgba(204,51,51,0.15); }}
.pillar-cell--blue {{ background: rgba(26,90,255,0.04); border-color: rgba(26,90,255,0.15); }}
.pillar-cell--cyan {{ background: rgba(8,145,178,0.04); border-color: rgba(8,145,178,0.15); }}
.pillar-cell--green {{ background: rgba(46,204,113,0.04); border-color: rgba(46,204,113,0.15); }}
.pillar-cell--neutral {{ background: rgba(0,28,61,0.02); }}
.pillar-cell__title {{ font-size: 14px; font-weight: 700; color: var(--text-main); }}
.pillar-cell__detail {{ font-size: 11px; color: var(--text-muted); margin-top: 3px; line-height: 1.4; }}
.pillar-arrow {{ display: flex; align-items: center; font-size: 14px; color: var(--text-muted); min-width: 16px; justify-content: center; }}

/* ─── Financial Table ─── */
.fin-table-wrap {{ margin-top: 12px; overflow-x: auto; }}
.fin-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
.fin-table th {{
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 10px 12px;
  text-align: left;
  border-bottom: 2px solid #E5E9F0;
}}
.fin-table td {{
  padding: 10px 12px;
  border-bottom: 1px solid #E5E9F0;
  color: var(--text-main);
  vertical-align: top;
}}
.fin-table tr:last-child td {{ border-bottom: none; }}
.fin-table .fin-total td {{ font-weight: 800; border-top: 2px solid var(--navy); color: var(--navy); }}
.fin-table .fin-highlight td {{ background: rgba(26,90,255,0.03); }}
.fin-footer {{ font-size: 10px; color: var(--text-muted); text-align: center; margin-top: 10px; font-style: italic; }}

/* ─── Dot Nav ─── */
.dot-nav {{
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: row;
  gap: 8px;
  z-index: 100;
}}
.dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(0,28,61,0.2);
  cursor: pointer;
  transition: all 0.3s ease;
}}
.dot.active {{ background: var(--action-blue); transform: scale(1.4); }}

/* ─── Fullscreen hint ─── */
.fs-hint {{
  position: fixed;
  bottom: 36px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: rgba(0,28,61,0.35);
  z-index: 50;
}}
.deck:fullscreen ~ .fs-hint,
.deck:-webkit-full-screen ~ .fs-hint {{ display: none; }}
.deck:fullscreen ~ .dot-nav,
.deck:-webkit-full-screen ~ .dot-nav {{ bottom: 12px; }}
/* Backbase wordmark — inline SVG, no PNG dependency */
</style>
</head>
<body>

<div class="deck" id="deck">
{scenes_html}
</div>

<div class="dot-nav" id="dotNav">
{dots}
</div>

<div class="fs-hint">Press <strong>F</strong> for fullscreen</div>

<script>
(function() {{
  const deck = document.getElementById('deck');
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  let current = 0;
  const total = slides.length;

  function goTo(idx) {{
    if (idx < 0 || idx >= total) return;
    slides[current].classList.remove('active');
    dots[current].classList.remove('active');
    current = idx;
    slides[current].classList.add('active');
    dots[current].classList.add('active');
  }}

  // Initialize
  if (slides.length > 0) slides[0].classList.add('active');

  // Keyboard
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); goTo(current + 1); }}
    if (e.key === 'ArrowLeft') {{ e.preventDefault(); goTo(current - 1); }}
    if (e.key === 'Home') {{ e.preventDefault(); goTo(0); }}
    if (e.key === 'End') {{ e.preventDefault(); goTo(total - 1); }}
    if (e.key === 'f' || e.key === 'F') {{
      if (!document.fullscreenElement) deck.requestFullscreen();
      else document.exitFullscreen();
    }}
  }});

  // Dot clicks
  dots.forEach(function(dot) {{
    dot.addEventListener('click', function() {{
      goTo(parseInt(this.dataset.idx));
    }});
  }});

  // Click to advance (left third = back, rest = forward)
  deck.addEventListener('click', function(e) {{
    if (e.target.closest('.dot-nav')) return;
    const rect = deck.getBoundingClientRect();
    const x = e.clientX - rect.left;
    if (x < rect.width / 3) goTo(current - 1);
    else goTo(current + 1);
  }});
}})();
</script>
</body>
</html>'''

    def save(self, path: str = None) -> str:
        out = path or f"frontline_2026_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(self.render())
        return out


# ──────────────────────────────────────────────
# Quick test / CLI usage
# ──────────────────────────────────────────────

if __name__ == "__main__":
    h = Frontline2026HTML("Backbase — AI-Native Banking OS")

    h.add_cover("Introduction", "AI-Native | Banking OS", "March 2026")

    h.add_agenda(
        "AI-NATIVE BANKING OS", "Agenda", "Backbase x <Customer>",
        ["Unified Frontline", "Modernizing Segments + Channels",
         "Banking OS", "Customer Cases", "Next Steps"]
    )

    h.add_section_divider(
        "INTRODUCTION TO BACKBASE", "Unified Frontline",
        "What problem are we trying to solve?"
    )

    h.add_content(
        "Challenge \u2022 50% of Banking work lives between systems",
        "The expensive whitespace between systems: handoffs, exceptions, manual coordination.",
        ["Customers face 20-40 disconnected touchpoints across their banking journey",
         "Employees spend 60% of time on non-value activities",
         "Manual coordination creates risk, delays, and cost overruns"]
    )

    h.add_split_comparison(
        "Trusted partner for 100+ Banks",
        section_label="UNIFIED FRONTLINE",
        left_title="Fragmented Frontline",
        left_items=[
            "20-40 disconnected apps, workflows + tools",
            "Manual steps everywhere \u2192 high cost-to-serve",
            "Banker spends 60% of time on non-value activities"
        ],
        right_title="Unified Frontline",
        right_items=[
            "Consistent, modern experiences across all channels",
            "3\u00d7 faster change velocity with reusable components",
            "AI-augmented workflows reduce manual effort by 40%"
        ]
    )

    h.add_architecture(
        "Banking OS for the AI era",
        "Where we play; one platform to unify + orchestrate the banks frontline business."
    )

    h.add_stat_cards(
        "Impact \u2022 Measurable business outcomes",
        "Results from leading banking transformations.",
        stats=[
            {"number": "3\u00d7", "label": "Faster time-to-market", "trend": "+200%"},
            {"number": "40%", "label": "Reduction in cost-to-serve", "trend": "\u2193 OpEx"},
            {"number": "60%", "label": "Less manual processing", "trend": "+Automation"},
        ]
    )

    h.add_case_study(
        "Global Bank \u2014 Unified Frontline Transformation",
        body_lines=[
            "Replaced 35 legacy applications with a single unified platform.",
            "Reduced customer onboarding time from 14 days to 2 days.",
            "Achieved 98% straight-through processing for standard requests.",
            "Enabled AI-assisted advisory for relationship managers."
        ]
    )

    out = h.save("frontline_2026_sample.html")
    print(f"Saved: {out}")
