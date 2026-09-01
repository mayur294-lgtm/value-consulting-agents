#!/usr/bin/env python3
"""
build_cheatsheet.py — generate the Cortex capability cheat sheet from the catalog.

The cheat sheet is a LIVING document: it changes every time a skill or agent is
added, renamed or retired. Hand-maintaining 40+ rows of HTML guarantees it goes
stale, so the content lives in docs/rollout/catalog.yaml and this script renders
it, cloning the Frontline 2026 long-form style block from the canonical template.

    python3 tools/build_cheatsheet.py            # regenerate the HTML
    python3 tools/build_cheatsheet.py --check    # drift check only, no write

--check is the guard: it compares the catalog against what is actually on disk
in .claude/commands/ and .claude/agents/ and exits 1 when they disagree. An entry
marked `status: pending` is expected to be missing (it is waiting on a PR) and is
reported but not failed.

Mascot art in docs/rollout/assets/ is inlined as data URIs so the output is a
single self-contained file anyone can email.

The PII setup guide is deliberately NOT part of this document. It is a one-time
install that nobody rereads; it lives on its own at docs/rollout/presidio-setup.html.
"""
from __future__ import annotations

import argparse
import base64
import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/rollout/catalog.yaml"
TEMPLATE = ROOT / "templates/long-form/document-template.html"
OUTPUT = ROOT / "docs/rollout/cortex-cheat-sheet.html"
ASSETS = ROOT / "docs/rollout/assets"
COMMANDS_DIR = ROOT / ".claude/commands"
AGENTS_DIR = ROOT / ".claude/agents"


# ---------------------------------------------------------------- drift check

def all_entries(cat: dict) -> list[dict]:
    """Every catalog row, from the groups and from the pipelines."""
    rows = [e for g in cat["groups"] for e in g["entries"]]
    rows += list(cat["pipelines"]["entries"])
    return rows


def on_disk() -> tuple[set[str], set[str]]:
    """Commands and agents actually present, excluding deprecated/ subdirs."""
    cmds = {p.stem for p in COMMANDS_DIR.glob("*.md")}
    agents = {p.stem for p in AGENTS_DIR.glob("*.md")}
    return cmds, agents


def catalog_names(cat: dict) -> tuple[dict[str, str], dict[str, str]]:
    """Map catalog command/agent name -> status ('', 'new', 'pending', ...)."""
    cmds: dict[str, str] = {}
    agents: dict[str, str] = {}
    for e in all_entries(cat):
        status = e.get("status", "")
        if e.get("cmd"):
            cmds[e["cmd"].lstrip("/")] = status
        if e.get("agent"):
            agents.setdefault(e["agent"], status)
    return cmds, agents


def check(cat: dict) -> int:
    disk_cmds, disk_agents = on_disk()
    cat_cmds, cat_agents = catalog_names(cat)
    excl_a = set(cat.get("excluded_agents") or [])
    excl_c = set(cat.get("excluded_commands") or [])

    problems: list[str] = []
    pending: list[str] = []

    for name, status in sorted(cat_cmds.items()):
        if name in disk_cmds:
            continue
        line = f"catalog lists /{name} but .claude/commands/{name}.md does not exist"
        (pending if status == "pending" else problems).append(line)
    for name, status in sorted(cat_agents.items()):
        if name in disk_agents:
            continue
        line = f"catalog lists agent {name} but .claude/agents/{name}.md does not exist"
        (pending if status == "pending" else problems).append(line)

    for name in sorted(disk_cmds - set(cat_cmds) - excl_c):
        problems.append(f"/{name} exists in the repo but is missing from the catalog")
    for name in sorted(disk_agents - set(cat_agents) - excl_a):
        problems.append(f"agent {name} exists in the repo but is missing from the catalog")

    # Every visible row needs the four columns the sheet renders.
    for e in all_entries(cat):
        label = e.get("cmd") or e.get("agent") or e.get("name", "?")
        for field in ("name", "does", "eg"):
            if not e.get(field):
                problems.append(f"{label} is missing `{field}`")
        if not e.get("cmd") and not e.get("ask"):
            problems.append(f"{label} has no cmd and no `ask` — nobody can tell how to run it")

    if pending:
        print("Pending (declared, waiting on a PR — not a failure):")
        for p in pending:
            print(f"  {p}")
        print()
    if problems:
        print("Catalog drift — the cheat sheet and the repo disagree:")
        for p in problems:
            print(f"  {p}")
        print("\nFix docs/rollout/catalog.yaml, then rerun `python3 tools/build_cheatsheet.py`.")
        return 1
    print(f"Catalog is in sync ({len(cat_cmds)} commands, {len(cat_agents)} agents, "
          f"{len(pending)} pending)")
    return 0


# ------------------------------------------------------------------ rendering

def esc(text: str) -> str:
    """Escape, but keep the small inline HTML the catalog is allowed to use."""
    out = html.escape(str(text), quote=False)
    for t in ("strong", "em", "span", "code"):
        out = out.replace(f"&lt;{t}&gt;", f"<{t}>").replace(f"&lt;/{t}&gt;", f"</{t}>")
    out = re.sub(r'&lt;span class=&quot;([a-z-]+)&quot;&gt;', r'<span class="\1">', out)
    return out.replace('&lt;span class="', '<span class="').replace('"&gt;', '">')


def tag(status: str) -> str:
    if status == "new":
        return '<span class="cs-new">New</span>'
    if status == "pending":
        return '<span class="cs-pending">Coming</span>'
    return ""


def data_uri(stem: str) -> str:
    """Inline a character figure. PNG (transparent) wins over JPG if both exist."""
    for ext, mime in (("png", "image/png"), ("jpg", "image/jpeg")):
        p = ASSETS / f"{stem}.{ext}"
        if p.exists():
            return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return ""


def how_cell(e: dict) -> str:
    """The 'type this' column. A slash command if it has one, otherwise the ask."""
    if e.get("auto"):
        return '<span class="cs-auto">Automatic</span>'
    if e.get("cmd"):
        out = f'<span class="cs-cmd">{esc(e["cmd"])}</span>{tag(e.get("status", ""))}'
        if e.get("agent"):
            out += f'<span class="cs-sub">{esc(e["agent"])}</span>'
        return out
    out = f'<span class="cs-ask">&ldquo;{esc(e.get("ask", ""))}&rdquo;</span>'
    if e.get("agent"):
        out += f'<span class="cs-sub">{esc(e["agent"])}</span>'
    return out


def row(e: dict) -> str:
    return (f'          <tr><td><strong>{esc(e["name"])}</strong></td>'
            f'<td>{how_cell(e)}</td>'
            f'<td>{esc(e["does"])}</td>'
            f'<td class="cs-eg">{esc(e["eg"])}</td></tr>')


def render_group(g: dict, n: int) -> str:
    off = ' class="section--off"' if n % 2 == 0 else ""
    icon = g.get("icon")
    art = (f'<img class="cs-icon" src="{data_uri(icon)}" alt="">' if icon and data_uri(icon) else "")
    rows = "\n".join(row(e) for e in g["entries"])
    return f'''
<section id="section-{n}"{off}>
  <div class="outer outer--rel">
    <div class="cs-head">
      {art}
      <div>
        <div class="sh-eyebrow">{n:02d}</div>
        <h2 style="margin:0 0 6px;">{esc(g["title"])}{tag(g.get("status", ""))}</h2>
        <p class="cs-blurb">{esc(g["blurb"]).strip()}</p>
      </div>
    </div>
    <div class="table-wrap">
      <table class="dt">
        <thead><tr><th style="width:15%">Name</th><th style="width:20%">Type this</th><th style="width:33%">What it does</th><th>Example</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
  </div>
</section>
'''


def render_pipelines(cat: dict, n: int) -> str:
    off = ' class="section--off"' if n % 2 == 0 else ""
    p = cat["pipelines"]
    rows = []
    for e in p["entries"]:
        cast = "".join(f'<img class="cs-chip" src="{data_uri(c)}" alt="" title="{c}">'
                       for c in (e.get("cast") or []) if data_uri(c))
        cast = f'<div class="cs-cast">{cast}</div>' if cast else ""
        rows.append(f'          <tr><td><strong>{esc(e["name"])}</strong>{cast}</td>'
                    f'<td>{how_cell(e)}</td>'
                    f'<td>{esc(e["does"]).strip()}</td>'
                    f'<td class="cs-eg">{esc(e["eg"])}</td></tr>')
    return f'''
<section id="section-{n}"{off}>
  <div class="outer outer--rel">
    <div class="sh">
      <div class="sh-eyebrow">Pipelines</div>
      <h2>Run the whole thing</h2>
      <p class="lead">{esc(p["lead"]).strip()}</p>
    </div>
    <div class="table-wrap">
      <table class="dt">
        <thead><tr><th style="width:19%">Name</th><th style="width:18%">Type this</th><th style="width:31%">What it does</th><th>Example</th></tr></thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>
  </div>
</section>
'''


def render_rules(cat: dict, n: int) -> str:
    off = ' class="section--off"' if n % 2 == 0 else ""
    r = cat["rules"]
    notes = "\n".join(f'    <div class="callout {x["kind"]}"><p>{esc(x["text"]).strip()}</p></div>'
                      for x in r["entries"])
    return f'''
<section id="section-{n}"{off}>
  <div class="outer outer--rel">
    <div class="sh"><div class="sh-eyebrow">House rules</div><h2>{esc(r["title"])}</h2></div>
{notes}
  </div>
</section>
'''


def render_start(cat: dict, n: int) -> str:
    off = ' class="section--off"' if n % 2 == 0 else ""
    gs = cat["getting_started"]
    steps = []
    for s in gs["steps"]:
        code = (f'<pre class="cs-code">{html.escape(str(s["code"]).strip())}</pre>'
                if s.get("code") else "")
        link = (f'<a class="cs-link" href="{s["link"]["href"]}">{esc(s["link"]["text"])} &rarr;</a>'
                if s.get("link") else "")
        steps.append(f'''    <div class="cs-step">
      <div class="cs-step__n">{s["n"]}</div>
      <div class="cs-step__b">
        <h3>{esc(s["title"])}</h3>
        <p>{esc(s["body"]).strip()}</p>
        {code}{link}
      </div>
    </div>''')
    return f'''
<section id="section-{n}"{off}>
  <div class="outer outer--rel">
    <div class="sh">
      <div class="sh-eyebrow">Start here</div>
      <h2>{esc(gs["title"])}</h2>
      <p class="lead">{esc(gs["lead"]).strip()}</p>
    </div>
{chr(10).join(steps)}
    <div class="callout blue"><p>{esc(gs["closing"]).strip()}</p></div>
  </div>
</section>
'''


def render(cat: dict) -> str:
    tpl = TEMPLATE.read_text()
    style = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
    logo = re.search(r'<svg class="top-nav__logo".*?</svg>', tpl, re.S).group(0)

    groups = cat["groups"]
    rows_all = all_entries(cat)
    n_cmds = len({e["cmd"] for e in rows_all if e.get("cmd")})
    n_agents = len({e["agent"] for e in rows_all if e.get("agent")})
    n_pipes = len(cat["pipelines"]["entries"])
    ver, upd = cat["version"], cat["updated"]
    hero = cat["hero"]

    body = "".join(render_group(g, i) for i, g in enumerate(groups, start=1))
    k = len(groups)
    body += render_pipelines(cat, k + 1)
    body += render_rules(cat, k + 2)
    body += render_start(cat, k + 3)

    sidebar = ["  <div class=\"sidebar__group-label\">Skills &amp; agents</div>"]
    for i, g in enumerate(groups, start=1):
        active = ' class="active"' if i == 1 else ""
        sidebar.append(f'  <a href="#section-{i}"{active}>{esc(g["title"])}</a>')
    sidebar += [
        '\n  <div class="sidebar__group-label">Then</div>',
        f'  <a href="#section-{k + 1}">Pipelines</a>',
        f'  <a href="#section-{k + 2}">House rules</a>',
        f'  <a href="#section-{k + 3}">New here? Start here</a>',
    ]

    log_rows = "\n".join(
        f'          <tr><td><strong>v{esc(c["version"])}</strong></td><td>{esc(c["date"])}</td>'
        f'<td>{esc(c["note"]).strip()}</td></tr>' for c in cat["changelog"])

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cortex Cheat Sheet</title>
<!-- GENERATED FILE — do not edit by hand.
     Source: docs/rollout/catalog.yaml
     Rebuild: python3 tools/build_cheatsheet.py -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700&display=swap" rel="stylesheet">
{style}
<!-- Cheat-sheet-only additions. Scoped cs- prefix; nothing above is modified. -->
<style>
.cs-toolbar{{position:sticky;top:var(--nav-h);z-index:40;background:var(--off);border-bottom:1px solid var(--border);padding:var(--sp-3) 0;margin-bottom:var(--sp-5)}}
.cs-toolbar__inner{{max-width:1080px;margin:0 auto;padding:0 40px;display:flex;gap:var(--sp-3);align-items:center;flex-wrap:wrap}}
.cs-search{{flex:1;min-width:220px;font-family:inherit;font-size:15px;padding:11px 16px;border:1px solid var(--border);background:#fff;color:var(--text)}}
.cs-search:focus{{outline:2px solid var(--blue);outline-offset:-1px}}
.cs-count{{font-size:13px;color:var(--muted);white-space:nowrap}}
.cs-cmd{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13.5px;font-weight:600;color:var(--blue);white-space:nowrap}}
.cs-ask{{font-size:14px;font-style:italic;color:var(--text);line-height:1.4}}
.cs-auto{{font-size:12px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--muted)}}
.cs-sub{{display:block;margin-top:5px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11.5px;color:var(--muted);word-break:normal;overflow-wrap:break-word;hyphens:none}}
.cs-eg{{font-size:13.5px;color:var(--muted)}}
.cs-new,.cs-pending{{display:inline-block;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#fff;padding:2px 7px;margin-left:8px;vertical-align:2px}}
.cs-new{{background:var(--blue)}}
.cs-pending{{background:var(--amber)}}
.cs-head{{display:flex;gap:26px;align-items:flex-end;margin-bottom:var(--sp-4)}}
.cs-icon{{height:122px;width:auto;flex:0 0 auto;align-self:flex-end}}
.cs-blurb{{margin:0;font-size:16px;line-height:1.55;color:var(--muted);max-width:60ch}}
.cs-cast{{display:flex;flex-wrap:wrap;gap:1px;margin-top:8px;align-items:flex-end;max-width:100%}}
.cs-chip{{height:30px;width:auto}}
.cs-hero{{display:flex;gap:44px;align-items:center;flex-wrap:wrap}}
.cs-hero__txt{{flex:1;min-width:300px}}
.cs-hero__art{{flex:0 0 420px;text-align:center}}
.cs-hero__art img{{width:100%;max-width:420px;display:block;margin:0 auto;filter:drop-shadow(0 18px 40px rgba(0,0,0,.45))}}
.cs-hero__cap{{margin-top:18px;font-size:13.5px;line-height:1.5;color:rgba(255,255,255,.75);text-align:left}}
.cs-step{{display:flex;gap:22px;padding:26px 0;border-bottom:1px solid var(--border)}}
.cs-step:last-of-type{{border-bottom:none}}
.cs-step__n{{flex:0 0 42px;height:42px;border-radius:50%;background:var(--blue);color:#fff;font-weight:700;font-size:18px;display:flex;align-items:center;justify-content:center}}
.cs-step__b{{flex:1}}
.cs-step__b h3{{margin:6px 0 8px;font-size:19px}}
.cs-step__b p{{margin:0;font-size:16px;line-height:1.6;max-width:68ch}}
.cs-code{{margin:14px 0 0;background:var(--navy);color:#cfe0ff;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;line-height:1.7;padding:14px 18px;border-radius:8px;overflow-x:auto;white-space:pre}}
.cs-link{{display:inline-block;margin-top:12px;color:var(--blue);font-size:14px;font-weight:600;text-decoration:none}}
.dt tr.cs-hide{{display:none}}
@media print{{.cs-toolbar{{display:none}}}}
@media (max-width:760px){{.cs-hero__art{{flex:1 1 100%}}.cs-icon{{height:76px}}}}
</style>
</head>
<body>

<nav class="top-nav">
  {logo}
  <span class="top-nav__sep">&times;</span>
  <span class="top-nav__logo-client" style="font-weight:500;font-size:14px;">Cortex</span>
  <div class="top-nav__title">Cheat Sheet</div>
  <div><span class="top-nav__badge">v{ver} &mdash; {upd}</span></div>
</nav>

<aside class="sidebar" id="sidebar">
{chr(10).join(sidebar)}
</aside>

<main class="main" id="main-content">

<section class="hero" style="border-bottom:none;">
  <div class="outer outer--rel">
    <svg class="geo-block" viewBox="0 0 16 16" style="position:absolute;top:0;left:-1px;color:var(--blue);"><path d="M16 0V16H8V8H0V0H16Z" fill="currentColor"/></svg>
    <div class="cs-hero">
      <div class="cs-hero__txt">
        <div class="sh-eyebrow" style="color:#fff;letter-spacing:2px;">{esc(hero["kicker"])}</div>
        <h1 style="margin-top:10px;">{esc(hero["title"])}</h1>
        <p class="hero__subtitle">{esc(hero["lead"]).strip()}</p>
        <div class="hero__stats">
          <div class="hero__stat"><span class="hero__stat-label">Skills</span><span class="hero__stat-value">{n_cmds}</span></div>
          <div class="hero__stat"><span class="hero__stat-label">Agents</span><span class="hero__stat-value">{n_agents}</span></div>
          <div class="hero__stat"><span class="hero__stat-label">Pipelines</span><span class="hero__stat-value">{n_pipes}</span></div>
        </div>
      </div>
      <div class="cs-hero__art">
        <img src="{data_uri(hero["mascot"])}" alt="The Cortex Gryphon">
        <p class="cs-hero__cap">{esc(hero["mascot_caption"]).strip()}</p>
      </div>
    </div>
    <p class="hero__footer">Backbase internal &middot; generated from the repo, not hand-maintained</p>
  </div>
</section>

<div class="cs-toolbar">
  <div class="cs-toolbar__inner">
    <input id="cs-search" class="cs-search" type="search" placeholder="Search — try &quot;roi&quot;, &quot;deck&quot;, &quot;benchmark&quot;">
    <span id="cs-count" class="cs-count">Showing everything</span>
  </div>
</div>
{body}
<section id="section-changelog" class="section--off">
  <div class="outer outer--rel">
    <div class="sh"><div class="sh-eyebrow">Changelog</div><h2>What changed</h2></div>
    <div class="table-wrap">
      <table class="dt">
        <thead><tr><th style="width:10%">Version</th><th style="width:14%">Date</th><th>Change</th></tr></thead>
        <tbody>
{log_rows}
        </tbody>
      </table>
    </div>
  </div>
</section>

</main>

<script>
(function () {{
  document.querySelectorAll('.sidebar a').forEach(function (a) {{
    a.addEventListener('click', function (e) {{
      e.preventDefault();
      document.querySelectorAll('.sidebar a').forEach(function (x) {{ x.classList.remove('active'); }});
      a.classList.add('active');
      var t = document.querySelector(a.getAttribute('href'));
      if (t) {{
        var navH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h')) || 65;
        window.scrollTo({{ top: t.getBoundingClientRect().top + window.pageYOffset - navH - 20, behavior: 'smooth' }});
      }}
    }});
  }});

  var search = document.getElementById('cs-search');
  var count  = document.getElementById('cs-count');
  if (!search) return;
  var secs = Array.prototype.slice.call(document.querySelectorAll('main section[id^="section-"]'));

  function apply() {{
    var q = search.value.trim().toLowerCase();
    if (!q) {{
      document.querySelectorAll('.dt tbody tr').forEach(function (r) {{ r.classList.remove('cs-hide'); }});
      secs.forEach(function (s) {{ s.style.display = ''; }});
      count.textContent = 'Showing everything';
      return;
    }}
    var shown = 0;
    secs.forEach(function (sec) {{
      var head = sec.querySelector('.cs-head, .sh');
      var headHit = head ? head.textContent.toLowerCase().indexOf(q) !== -1 : false;
      var trs = sec.querySelectorAll('.dt tbody tr');
      if (!trs.length) {{ sec.style.display = 'none'; return; }}
      var any = false;
      Array.prototype.forEach.call(trs, function (r) {{
        var hit = headHit || r.textContent.toLowerCase().indexOf(q) !== -1;
        r.classList.toggle('cs-hide', !hit);
        if (hit) {{ shown++; any = true; }}
      }});
      sec.style.display = any ? '' : 'none';
    }});
    count.textContent = shown === 0
      ? 'Nothing matches "' + search.value.trim() + '"'
      : shown + (shown === 1 ? ' match' : ' matches');
  }}
  search.addEventListener('input', apply);
  search.addEventListener('search', apply);
}})();
</script>
</body>
</html>
'''


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="drift check only; write nothing")
    args = ap.parse_args()

    cat = yaml.safe_load(CATALOG.read_text())
    rc = check(cat)
    if args.check:
        return rc
    if rc:
        print("\nRefusing to generate a sheet that disagrees with the repo.")
        return rc
    OUTPUT.write_text(render(cat))
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
