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

The PII setup guide is deliberately NOT part of this document. It is a one-time
install that nobody rereads; it lives on its own at docs/rollout/presidio-setup.html.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/rollout/catalog.yaml"
TEMPLATE = ROOT / "templates/long-form/document-template.html"
OUTPUT = ROOT / "docs/rollout/cortex-cheat-sheet.html"
COMMANDS_DIR = ROOT / ".claude/commands"
AGENTS_DIR = ROOT / ".claude/agents"


# ---------------------------------------------------------------- drift check

def on_disk() -> tuple[set[str], set[str]]:
    """Commands and agents actually present, excluding deprecated/ subdirs."""
    cmds = {p.stem for p in COMMANDS_DIR.glob("*.md")}
    agents = {p.stem for p in AGENTS_DIR.glob("*.md")}
    return cmds, agents


def catalog_names(cat: dict) -> tuple[dict[str, str], dict[str, str]]:
    """Map catalog command/agent name -> status ('', 'new', 'pending', ...)."""
    cmds: dict[str, str] = {}
    agents: dict[str, str] = {}
    for job in cat["jobs"]:
        for e in job["entries"]:
            status = e.get("status", "")
            if e.get("cmd"):
                cmds[e["cmd"].lstrip("/")] = status
            if e.get("agent"):
                agents[e["agent"]] = status
    for e in cat["under_the_hood"]["entries"]:
        agents.setdefault(e["agent"], e.get("status", ""))
    return cmds, agents


def check(cat: dict) -> int:
    disk_cmds, disk_agents = on_disk()
    cat_cmds, cat_agents = catalog_names(cat)
    excluded_cmds = set(cat.get("excluded_commands") or [])
    excluded_agents = set(cat.get("excluded_agents") or [])

    problems, pending = [], []

    for name, status in sorted(cat_cmds.items()):
        if name not in disk_cmds:
            (pending if status == "pending" else problems).append(
                f"  catalog lists /{name} but .claude/commands/{name}.md does not exist"
            )
    for name, status in sorted(cat_agents.items()):
        if name not in disk_agents:
            (pending if status == "pending" else problems).append(
                f"  catalog lists agent {name} but .claude/agents/{name}.md does not exist"
            )
    for name in sorted(disk_cmds - set(cat_cmds) - excluded_cmds):
        problems.append(f"  /{name} exists on disk but is not in the catalog")
    for name in sorted(disk_agents - set(cat_agents) - excluded_agents):
        problems.append(f"  agent {name} exists on disk but is not in the catalog")

    if pending:
        print("Pending (declared, waiting on a PR — not a failure):")
        print("\n".join(pending))
        print()
    if problems:
        print("DRIFT — the catalog and the repo disagree:")
        print("\n".join(problems))
        print("\nFix docs/rollout/catalog.yaml, then re-run.")
        return 1
    print(f"Catalog is in sync ({len(cat_cmds)} commands, {len(cat_agents)} agents"
          + (f", {len(pending)} pending)" if pending else ")"))
    return 0


# ------------------------------------------------------------------ rendering

def esc(text: str) -> str:
    """Escape, but keep the small inline HTML the catalog is allowed to use."""
    out = html.escape(str(text), quote=False)
    for tag in ("strong", "em", "span", "code"):
        out = out.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    out = re.sub(r'&lt;span class=&quot;([a-z-]+)&quot;&gt;', r'<span class="\1">', out)
    return out.replace('&lt;span class="', '<span class="').replace('"&gt;', '">')


def tag(status: str) -> str:
    if status == "new":
        return '<span class="cs-new">New</span>'
    if status == "deprecated":
        return '<span class="cs-dep">Deprecated</span>'
    if status == "pending":
        return '<span class="cs-pending">Not yet merged</span>'
    return ""


def run_cell(e: dict) -> str:
    bits = []
    if e.get("cmd"):
        bits.append(f'<span class="cs-cmd">{esc(e["cmd"])}</span>{tag(e.get("status", ""))}')
    if e.get("ask"):
        bits.append(f'Just ask &mdash; <em>&ldquo;{esc(e["ask"])}&rdquo;</em>')
    if e.get("agent") and not e.get("cmd"):
        bits.append(f'<span class="cs-agent">{esc(e["agent"])}</span>')
    return "<br>".join(bits)


def render_job(job: dict, n: int) -> str:
    off = ' class="section--off"' if n % 2 == 0 else ""
    rows = "\n".join(
        f'          <tr><td>{run_cell(e)}</td><td>{esc(e["does"])}</td>'
        f'<td>{esc(e["needs"])}</td><td>{esc(e["gives"])}</td></tr>'
        for e in job["entries"]
    )
    notes = "\n".join(
        f'    <div class="callout {nt["kind"]}"><p>{esc(nt["text"]).strip()}</p></div>'
        for nt in (job.get("notes") or [])
    )
    v = job.get("video") or {}
    if v:
        link = (f'<a href="{v["url"]}" class="cs-vid__link">Watch &rarr;</a>'
                if v.get("url") else '<span>Week {} &middot; link to follow</span>'.format(v.get("week", "—")))
        video = f'''
    <div class="cs-vid">
      <div class="cs-vid__play"></div>
      <div class="cs-vid__txt"><strong>Video &mdash; {esc(v["title"])}</strong>{link}</div>
    </div>'''
    else:
        video = ""

    return f'''
<section id="section-{n}"{off}>
  <div class="outer outer--rel">
    <div class="sh">
      <div class="sh-eyebrow">Job {n:02d}</div>
      <h2>{esc(job["title"])}{tag(job.get("status", ""))}</h2>
      <p class="lead">{esc(job["lead"]).strip()}</p>
    </div>
    <div class="table-wrap">
      <table class="dt">
        <thead><tr><th style="width:21%">Run this</th><th style="width:32%">What it does</th><th style="width:21%">Needs</th><th>You get</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
{notes}{video}
  </div>
</section>
'''


def render(cat: dict) -> str:
    tpl = TEMPLATE.read_text()
    style = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
    logo = re.search(r'<svg class="top-nav__logo".*?</svg>', tpl, re.S).group(0)

    jobs = cat["jobs"]
    n_jobs = len(jobs)
    n_cmds = sum(1 for j in jobs for e in j["entries"] if e.get("cmd"))
    n_agents = len({e["agent"] for j in jobs for e in j["entries"] if e.get("agent")}
                   | {e["agent"] for e in cat["under_the_hood"]["entries"]})
    n_pending = sum(1 for j in jobs for e in j["entries"] if e.get("status") == "pending")

    ver, upd = cat["version"], cat["updated"]

    sidebar = ['  <div class="sidebar__group-label">By the job you\'re doing</div>']
    for i, job in enumerate(jobs, start=1):
        active = ' class="active"' if i == 1 else ""
        sidebar.append(f'  <a href="#section-{i}"{active}>{i}. {esc(job["title"])}</a>')
    ref_start = n_jobs + 1
    sidebar += [
        '\n  <div class="sidebar__group-label">Reference</div>',
        f'  <a href="#section-{ref_start}">Under the hood</a>',
        f'  <a href="#section-{ref_start + 1}">Core team only</a>',
        f'  <a href="#section-{ref_start + 2}">Videos</a>',
        f'  <a href="#section-{ref_start + 3}">What changed in v{ver}</a>',
    ]

    body = "".join(render_job(job, i) for i, job in enumerate(jobs, start=1))

    hood_rows = "\n".join(
        f'          <tr><td><span class="cs-agent">{esc(e["agent"])}</span>{tag(e.get("status", ""))}</td>'
        f'<td>{esc(e["stage"])}</td><td>{esc(e["gives"])}</td></tr>'
        for e in cat["under_the_hood"]["entries"]
    )

    def vid_row(j: dict) -> str:
        v = j["video"]
        if v.get("url"):
            status = '<a href="{}">Watch</a>'.format(v["url"])
        else:
            status = '<span class="bb-badge amber">To record</span>'
        return (
            '          <tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                v.get("week", "&mdash;"), esc(v.get("title", "—")), esc(j["title"]), status
            )
        )

    vid_rows = "\n".join(vid_row(j) for j in jobs if j.get("video"))

    log_rows = "\n".join(
        f'          <tr><td><strong>v{esc(c["version"])}</strong></td><td>{esc(c["date"])}</td>'
        f'<td>{esc(c["note"]).strip()}</td></tr>'
        for c in cat["changelog"]
    )

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
.cs-agent{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;color:var(--muted);white-space:nowrap}}
.cs-vid{{display:flex;align-items:center;gap:12px;border-left:3px solid var(--blue);background:var(--blue-l);padding:14px 18px;margin:var(--sp-4) 0 0}}
.cs-vid__play{{width:26px;height:26px;flex:0 0 26px;border-radius:50%;background:var(--blue);position:relative}}
.cs-vid__play::after{{content:'';position:absolute;top:8px;left:10px;border-left:8px solid #fff;border-top:5px solid transparent;border-bottom:5px solid transparent}}
.cs-vid__txt{{font-size:14px;line-height:1.45}}
.cs-vid__txt strong{{display:block;font-size:14px}}
.cs-vid__txt span{{color:var(--muted);font-size:13px}}
.cs-vid__link{{color:var(--blue);font-size:13px;font-weight:600;text-decoration:none}}
.cs-new,.cs-dep,.cs-pending{{display:inline-block;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#fff;padding:2px 7px;margin-left:8px;vertical-align:2px}}
.cs-new{{background:var(--blue)}}
.cs-dep{{background:var(--muted)}}
.cs-pending{{background:var(--amber)}}
.cs-banner{{background:var(--blue-l);border-left:3px solid var(--blue);padding:16px 20px;margin-bottom:var(--sp-5);font-size:14.5px;line-height:1.5}}
.dt tr.cs-hide{{display:none}}
@media print{{.cs-toolbar{{display:none}}}}
</style>
</head>
<body>

<nav class="top-nav">
  {logo}
  <span class="top-nav__sep">&times;</span>
  <span class="top-nav__logo-client" style="font-weight:500;font-size:14px;">Cortex</span>
  <div class="top-nav__title">Cheat Sheet &mdash; what Cortex can do</div>
  <div><span class="top-nav__badge">v{ver} &mdash; {upd}</span></div>
</nav>

<aside class="sidebar" id="sidebar">
{chr(10).join(sidebar)}
</aside>

<main class="main" id="main-content">

<section class="hero" style="border-bottom:none;">
  <div class="outer outer--rel">
    <svg class="geo-block" viewBox="0 0 16 16" style="position:absolute;top:0;left:-1px;color:var(--blue);"><path d="M16 0V16H8V8H0V0H16Z" fill="currentColor"/></svg>
    <div class="sh-eyebrow" style="color:#fff;letter-spacing:2px;">Living catalog</div>
    <div class="hero__draft">v{ver} &mdash; {upd}</div>
    <h1>Everything Cortex can do</h1>
    <p class="hero__subtitle">Organised by the job you're trying to finish, not by how the system is built. You should never need to know whether the thing you want is a skill, an agent or a pipeline &mdash; ask for the deliverable.</p>
    <div class="hero__stats">
      <div class="hero__stat"><span class="hero__stat-label">Jobs covered</span><span class="hero__stat-value">{n_jobs}</span></div>
      <div class="hero__stat"><span class="hero__stat-label">Commands</span><span class="hero__stat-value">{n_cmds}</span></div>
      <div class="hero__stat"><span class="hero__stat-label">Agents</span><span class="hero__stat-value">{n_agents}</span></div>
      <div class="hero__stat"><span class="hero__stat-label">Awaiting merge</span><span class="hero__stat-value">{n_pending}</span></div>
    </div>
    <p class="hero__footer">Backbase internal &middot; regenerated from the repo, not hand-maintained</p>
  </div>
</section>

<div class="cs-toolbar">
  <div class="cs-toolbar__inner">
    <input type="search" class="cs-search" id="cs-search" placeholder="Filter everything &mdash; try 'roi', 'proposal', 'workshop', 'benchmark'" aria-label="Filter commands and agents">
    <span class="cs-count" id="cs-count">Showing everything</span>
  </div>
</div>

<div class="outer">
  <div class="cs-banner">
    <strong>This page changes with every release.</strong> It is generated from the repository, so what
    you see here is what is actually installed &mdash; bookmark it rather than saving a copy.
    Setting up PII protection is a separate one-time job and lives in its own guide.
    Anything tagged <span class="cs-pending" style="margin-left:0;">Not yet merged</span> is documented ahead of the code landing.
  </div>
</div>
{body}
<section id="section-{ref_start}">
  <div class="outer outer--rel">
    <div class="sh">
      <div class="sh-eyebrow">Reference</div>
      <h2>Under the hood</h2>
      <p class="lead">{esc(cat["under_the_hood"]["lead"]).strip()}</p>
    </div>
    <div class="table-wrap">
      <table class="dt">
        <thead><tr><th style="width:27%">Agent</th><th style="width:18%">Runs at</th><th>What it produces</th></tr></thead>
        <tbody>
{hood_rows}
        </tbody>
      </table>
    </div>
    <div class="callout blue"><p><strong>What the split changed.</strong> Each of these agents used to keep its operating instructions inside the orchestrator script, which is why running one on its own wasn't possible. The instructions now live in the agent itself. The pipeline runs exactly as it did &mdash; but every step in it also stands alone.</p></div>
  </div>
</section>

<section id="section-{ref_start + 1}" class="section--off">
  <div class="outer outer--rel">
    <div class="sh">
      <div class="sh-eyebrow">Reference</div>
      <h2>Core team only</h2>
      <p class="lead">Here for completeness. If you use Cortex to do consulting work rather than to build Cortex, none of this affects you.</p>
    </div>
    <div class="grid-2">
      <div class="card">
        <h3>Changing Cortex itself</h3>
        <p>Any change to an agent, a skill, a template or pipeline code goes through the lifecycle &mdash; <span class="cs-cmd">/bb-prd</span>, <span class="cs-cmd">/bb-design</span>, <span class="cs-cmd">/bb-tickets</span>, <span class="cs-cmd">/bb-build</span>, <span class="cs-cmd">/bb-pr-review</span>, <span class="cs-cmd">/bb-refine</span> &mdash; with the eval suite as the gate that decides whether it can merge. A hook blocks direct edits to those paths, so this isn't something you can forget to do.</p>
        <p style="margin-top:10px;">Adding a skill or an agent also means adding it to <span class="cs-cmd">docs/rollout/catalog.yaml</span> and regenerating this page, in the same PR. <strong>CI enforces both</strong> &mdash; <span class="cs-cmd">catalog-drift.yml</span> fails a PR whose catalog disagrees with the repo, or whose generated page is behind the catalog. Run <span class="cs-cmd">python3 tools/build_cheatsheet.py</span> before pushing.</p>
      </div>
      <div class="card">
        <h3>Telemetry</h3>
        <p><span class="cs-cmd">/sync-telemetry</span> pushes journal telemetry up as a GitHub issue, and <span class="cs-cmd">/process-meeting</span> runs the Cortex standup. Telemetry is intake only &mdash; it feeds the backlog that decides what gets built next. Nothing auto-implements; the autonomous development loop was removed in June 2026 because it changed agents outside the gate.</p>
      </div>
    </div>
    <div class="callout blue"><p><strong>Contributing knowledge is open to everyone.</strong> The restriction is on architecture, not content. Anyone can add to <span class="cs-cmd">knowledge/learnings/</span>, <span class="cs-cmd">knowledge/domains/</span> and <span class="cs-cmd">benchmarks/</span> &mdash; and that's the contribution that makes the biggest difference to everyone else's next engagement.</p></div>
  </div>
</section>

<section id="section-{ref_start + 2}">
  <div class="outer outer--rel">
    <div class="sh">
      <div class="sh-eyebrow">Reference</div>
      <h2>Videos</h2>
      <p class="lead">Short walkthroughs, one a week, each against a job above. Links appear here as they land.</p>
    </div>
    <div class="table-wrap">
      <table class="dt">
        <thead><tr><th style="width:8%">Week</th><th style="width:40%">Video</th><th style="width:32%">Job</th><th>Status</th></tr></thead>
        <tbody>
{vid_rows}
        </tbody>
      </table>
    </div>
    <div class="callout blue"><p><strong>Each one is a minute or less</strong> and shows a real run rather than a description of one. They're grouped by job rather than made one-per-command, because forty-odd separate clips would go stale faster than anyone could watch them.</p></div>
  </div>
</section>

<section id="section-{ref_start + 3}" class="section--off">
  <div class="outer outer--rel">
    <div class="sh">
      <div class="sh-eyebrow">Reference</div>
      <h2>What changed in v{ver}</h2>
      <p class="lead">Every version of this page, and what moved.</p>
    </div>
    <div class="table-wrap">
      <table class="dt">
        <thead><tr><th style="width:10%">Version</th><th style="width:14%">Date</th><th>What changed</th></tr></thead>
        <tbody>
{log_rows}
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="dark-cta">
  <div class="dark-cta-inner">
    <h2 style="color:#fff;">If something here is wrong, that's the most useful thing you can tell us</h2>
    <p style="color:#fff;opacity:.85;max-width:640px;margin:var(--sp-3) auto 0;">A command that doesn't exist, an output that doesn't match the description, a step that fails on your machine &mdash; it means this page has drifted from the system. Say so in the team channel, or run <span style="font-family:ui-monospace,monospace;color:var(--cyan);">/log-modification</span> if you had to fix an output by hand.</p>
  </div>
</section>

<section style="background:var(--navy);padding:var(--sp-4) 0;">
  <div class="outer" style="text-align:center;">
    <p style="color:#fff;font-size:13px;margin:0;">Cortex Cheat Sheet v{ver} &mdash; {upd} &middot; Generated from docs/rollout/catalog.yaml &middot; Backbase internal</p>
  </div>
</section>

</main>

<script>
(function() {{
  'use strict';
  var sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  var links = sidebar.querySelectorAll('a[href^="#"]');
  var sections = [];
  links.forEach(function(link) {{
    var id = link.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sections.push({{ id: id, el: el, link: link }});
  }});
  function setActive(id) {{
    links.forEach(function(l) {{ l.classList.remove('active'); }});
    var m = sidebar.querySelector('a[href="#' + id + '"]');
    if (m) m.classList.add('active');
  }}
  if ('IntersectionObserver' in window && sections.length) {{
    var obs = new IntersectionObserver(function(entries) {{
      entries.forEach(function(e) {{ if (e.isIntersecting) setActive(e.target.id); }});
    }}, {{ rootMargin: '-20% 0px -70% 0px' }});
    sections.forEach(function(s) {{ obs.observe(s.el); }});
  }}
  links.forEach(function(link) {{
    link.addEventListener('click', function(e) {{
      e.preventDefault();
      var t = document.getElementById(this.getAttribute('href').slice(1));
      if (t) {{
        var navH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h')) || 65;
        window.scrollTo({{ top: t.getBoundingClientRect().top + window.pageYOffset - navH - 20, behavior: 'smooth' }});
      }}
    }});
  }});

  var search = document.getElementById('cs-search');
  var count  = document.getElementById('cs-count');
  if (!search) return;
  var rows = Array.prototype.slice.call(document.querySelectorAll('.dt tbody tr'));
  var secs = Array.prototype.slice.call(document.querySelectorAll('main section[id^="section-"]'));

  function apply() {{
    var q = search.value.trim().toLowerCase();
    if (!q) {{
      rows.forEach(function(r) {{ r.classList.remove('cs-hide'); }});
      secs.forEach(function(s) {{ s.style.display = ''; }});
      count.textContent = 'Showing everything';
      return;
    }}
    var shown = 0;
    secs.forEach(function(sec) {{
      // A section whose heading matches keeps ALL of its rows — someone searching
      // "proposal" wants the whole proposal job, not only rows repeating the word.
      var head = sec.querySelector('.sh');
      var headHit = head ? head.textContent.toLowerCase().indexOf(q) !== -1 : false;
      var trs = sec.querySelectorAll('.dt tbody tr');
      if (!trs.length) {{ sec.style.display = 'none'; return; }}
      var any = false;
      Array.prototype.forEach.call(trs, function(r) {{
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
