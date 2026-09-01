#!/usr/bin/env python3
"""
Cortex Pipeline Orchestrator — Value Consulting Assessment Pipeline.

Supports interactive (consultant checkpoints), express, and non-interactive modes.
Non-interactive mode includes performance optimizations:
- Single-phase Block A (eliminates P1 sync barrier)
- Overlapping stages (Roadmap + Excel in parallel)
- 3-way parallel Assembly sharding (Acts 1-2 / 3-5 / 6-7)
- Per-agent timeouts and output validation
- 6-partial HTML generation with template assembly

Usage:
    python scripts/orchestrate.py <engagement_dir>
    python scripts/orchestrate.py --express <engagement_dir>
    python scripts/orchestrate.py --resume-from <step> <engagement_dir>
    python scripts/orchestrate.py --dry-run <engagement_dir>
    python scripts/orchestrate.py --non-interactive <engagement_dir>
"""

import asyncio
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Ensure output appears immediately even without PYTHONUNBUFFERED
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
from pathlib import Path

from anonymize_transcript import anonymize_transcript_file
from artifact_boundary import cap_roi_config, deanonymize_dir, synthetic_policy, validate_outputs
from typing import Optional

# pii.identity and pii.denylist are STDLIB-ONLY by contract (see
# scripts/pii/__init__.py's IMPORT CONTRACT) — importing them here does not
# pull in Presidio or spaCy. anonymize_transcript.py already put scripts/ on
# sys.path, so `pii` resolves regardless of how this file was reached.
from pii import denylist as _denylist
from pii import identity as _identity

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)
# NOTE: SDK v0.1.39 patched directly to handle unknown message types
# (e.g., rate_limit_event). See message_parser.py case _ and client.py yield.
# When SDK updates to handle this natively, the direct patches can be removed.

# ─── Paths ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"

# ─── Neutral workspace (#167 — solution-design-v6.md D6) ─────────────────────
#
# WHY EVERY AGENT NOW RUNS SOMEWHERE ELSE
#   The engagement directory IS the client's identity (`engagements/hdfc/…`).
#   `compose_prompt` renders `engagement_dir` / `outputs_dir` /
#   `transcript_path` into the invocation prompt as VALUES (its own docstring
#   says so), and `run_agent` sets `cwd` to that same client-named directory.
#   So perfect content anonymisation was defeated by the path envelope on
#   every single agent invocation. `pii.identity.materialise_workspace()`
#   builds a directory in which every path segment is generated locally, and
#   from #167 on that — not the engagement directory — is what agents see.
#
# WHY THE WORKSPACE LIVES INSIDE THE REPO, NOT IN /tmp
#   identity.py defaults to the system temp directory. Every agent prompt
#   also names REPO-RELATIVE knowledge files (`knowledge/standards/…`,
#   `knowledge/domains/{domain}/…`) that carry no `{param}`, so they can only
#   be reached relative to a cwd somewhere inside this repo. Today's cwd
#   (`engagements/<client>/<engagement>`) is inside it; `/tmp/cortex-ws-XXXX`
#   is not, and moving there would silently cut every agent off from its own
#   knowledge pack. `.cortex-workspaces/` keeps the workspace at the same
#   depth-below-repo-root as an engagement directory while contributing no
#   client-derived path segment of its own. It is gitignored.
#
#   It deliberately does NOT live under `engagements/` — `denylist.py`
#   treats every child of `engagements/` as a client directory and mines its
#   name, so a workspace there would pollute the deny-list of every session.
WORKSPACE_ROOT = REPO_ROOT / ".cortex-workspaces"

# Written inside the REAL engagement directory (gitignored with the rest of
# engagements/): the absolute path of the workspace this engagement's current
# run is using, so `--resume-from` reattaches to it. See `_restore_workspace`
# for why resume reattaches rather than re-materialising.
WORKSPACE_POINTER = ".pipeline_workspace"

# An opaque engagement ID as `pii.identity` mints it: secrets.token_hex(4).
_OPAQUE_ID_RE = re.compile(r"^[0-9a-f]{8}$")

# ─── Colors for terminal output ───────────────────────────────────────────────

class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# ─── Helpers ──────────────────────────────────────────────────────────────────

# ─── Log redaction (#167) ────────────────────────────────────────────────────
#
# The pipeline's stdout is NOT a private channel. `orchestrate.py` is normally
# launched with Bash from inside a Claude Code session, so every line printed
# here is read back into a model's context; the journal, the telemetry
# extractor and the consultant's scrollback all see it too. Repointing prompts
# and `cwd` at a neutral workspace achieves nothing if the very next `log()`
# call prints `engagements/hdfc/2026-02_retail_assessment`.
#
# So every line this module prints goes through `_redact` first. The terms are
# the engagement's own deny-list (the same resolution the anonymiser uses) plus
# the engagement/client directory paths themselves. This is a BACKSTOP, not the
# control: the control is that no client-named path is constructed into a
# prompt or a cwd in the first place. A backstop that fires means a real leak
# was caught, so it is deliberately blunt — over-redacting a log line costs
# nothing.
# Two patterns, deliberately not one:
#
#   _CLIENT_RE — things that ARE the client's identity: the deny-list terms,
#     plus the directory segment immediately below `engagements/` (which is the
#     client directory today, and the opaque ID after #168). This is what the
#     hard invocation assertion and the harvest-id check run against, because a
#     match there means a real leak.
#
#   _REDACT_RE — the above PLUS the engagement's absolute paths and its
#     remaining path segments (the `YYYY-MM_domain_type` slug). Blunter, and
#     only ever used to scrub log output, where over-redacting costs nothing.
#     Keeping the engagement slug OUT of _CLIENT_RE matters: it is not a client
#     identifier, and folding it in made the harvest-id guard fire on every
#     engagement and rename the knowledge files for no privacy benefit.
_CLIENT_RE: Optional[re.Pattern] = None
_REDACT_RE: Optional[re.Pattern] = None
_REDACT_TERMS: list = []
_MIN_REDACT_LEN = 3   # below this, a "term" matches half the alphabet


def _compile_terms(terms) -> Optional[re.Pattern]:
    """Longest-first alternation. Ordering is load-bearing: without it the term
    `hdfc` consumes the leading segment of `/…/engagements/hdfc/2026-02_x` and
    leaves the rest of the path exposed."""
    kept = sorted((t for t in terms if t and len(t) >= _MIN_REDACT_LEN),
                  key=len, reverse=True)
    if not kept:
        return None
    return re.compile("|".join(re.escape(t) for t in kept), re.IGNORECASE)


def _install_log_redactions(engagement_dir: Path, client_slug: Optional[str] = None):
    """Build both patterns for this run. Call once, before anything that could
    print an engagement path or compose a prompt.

    Deny-list resolution can raise (denylist.py keeps fail-closed read
    semantics on purpose). We do NOT let that abort the run here: the caller
    that actually needs to fail closed is the anonymiser, which resolves its
    own deny-list and will raise there. What must never happen is losing the
    PATH redactions because the DOCUMENT scan failed — so those are installed
    unconditionally and document-derived terms are added on top.
    """
    global _CLIENT_RE, _REDACT_RE, _REDACT_TERMS
    engagement_dir = Path(engagement_dir)

    client_terms = set()
    candidate = _engagement_id_candidate(engagement_dir)
    if candidate:
        client_terms.add(candidate)
    if client_slug:
        client_terms.add(client_slug)

    path_terms = {str(engagement_dir), str(engagement_dir.parent)}
    parts = [q.lower() for q in engagement_dir.parts]
    if "engagements" in parts:
        path_terms.update(engagement_dir.parts[parts.index("engagements") + 1:])

    failure = None
    try:
        client_terms.update(_denylist.resolve_engagement_deny_list(
            engagement_dir, client_slug=client_slug))
    except Exception as exc:   # noqa: BLE001 — see docstring
        failure = exc

    _CLIENT_RE = _compile_terms(client_terms)
    all_terms = client_terms | path_terms
    _REDACT_TERMS = sorted(
        (t for t in all_terms if len(t) >= _MIN_REDACT_LEN), key=len, reverse=True)
    _REDACT_RE = _compile_terms(all_terms)

    if failure is not None:
        # Emitted through the redactions just installed.
        log(f"  ⚠ deny-list resolution failed ({type(failure).__name__}: "
            f"{failure}) — identifier checks are running on the directory "
            f"name alone", C.YELLOW)


class ClientIdentifierLeak(RuntimeError):
    """A composed prompt or a `cwd` still names the client. Fail closed.

    This is the assertion #167 exists to make true, enforced at the ONE place
    every agent invocation passes through rather than trusted call site by call
    site. It raises rather than warns: the whole ticket is the claim that no
    client-identifying string is sent, and a control that merely logs when that
    claim breaks is the pattern this repo has already shipped twice — a gate
    scoring green while certifying nothing.
    """


def _leaked_terms(text: str) -> list:
    """Deny-list terms present in `text`, with the repo's own path discounted.

    `str(REPO_ROOT)` prefixes every workspace path and every knowledge path in
    a composed prompt. If a client's name happened to share a word with the
    checkout directory (`…/value-consulting-agents` and a client called "Value
    Bank"), matching against it would fail every invocation for a reason that
    has nothing to do with the client. Strip it first, then match.
    """
    if _CLIENT_RE is None:
        return []
    probe = str(text).replace(str(REPO_ROOT), "")
    return sorted(set(_CLIENT_RE.findall(probe)))


def _assert_neutral_invocation(agent_name: str, cwd, system_prompt: str):
    """Refuse to launch an agent whose cwd or prompt names the client."""
    for label, value in (("cwd", str(cwd)), ("composed prompt", system_prompt)):
        hits = _leaked_terms(value)
        if hits:
            raise ClientIdentifierLeak(
                f"REFUSING to invoke '{agent_name}': its {label} still contains "
                f"client identifier(s) {hits}. Every path parameter and the cwd "
                f"must resolve inside the neutral workspace "
                f"(pii.identity.materialise_workspace) — see solution-design-v6.md "
                f"D6. Nothing was sent."
            )


def _dump_composed_prompt(agent_name: str, mode: str, cwd, system_prompt: str):
    """Optional audit trail: write exactly what this invocation would send.

    Off unless `CORTEX_PROMPT_DUMP_DIR` is set. Enabled, it records the cwd and
    the full composed prompt for every agent invocation, which is how the
    "no composed prompt and no cwd contains a client identifier" claim is
    checked against reality instead of against the code that is supposed to
    make it true. Safe to write: `_assert_neutral_invocation` has already run
    and refused anything carrying a client identifier.
    """
    target = os.environ.get("CORTEX_PROMPT_DUMP_DIR")
    if not target:
        return
    try:
        out = Path(target)
        out.mkdir(parents=True, exist_ok=True)
        n = len(list(out.glob("*.prompt.txt"))) + 1
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{n:03d}_{agent_name}_{mode}")
        (out / f"{safe}.prompt.txt").write_text(
            f"AGENT: {agent_name}\nMODE: {mode}\nCWD: {cwd}\n"
            f"{'-' * 60}\n{system_prompt}\n", encoding="utf-8")
    except OSError as exc:
        log(f"  ⚠ prompt dump failed ({type(exc).__name__}: {exc})", C.YELLOW)


def _redact(msg: str) -> str:
    """Replace every known client identifier in `msg` with `<REDACTED>`.

    Longest-first ordering matters: without it, the term `hdfc` would consume
    the leading segment of the full path `/…/engagements/hdfc/2026-02_x` and
    leave the engagement slug exposed.
    """
    if _REDACT_RE is None:
        return msg
    return _REDACT_RE.sub("<REDACTED>", msg)


def log(msg: str, color: str = ""):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.DIM}{ts}{C.RESET} {color}{_redact(str(msg))}{C.RESET}")


def log_step(step: str, desc: str):
    print(f"\n{C.BOLD}{C.CYAN}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {step}: {_redact(desc)}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * 60}{C.RESET}\n")


def log_print(msg: str = ""):
    """`print` for pipeline chrome — same redaction guarantee as `log`.

    Used for the header/summary blocks, which print engagement paths and
    agent-produced content and therefore need the same treatment as `log`.
    """
    print(_redact(str(msg)))


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def file_exists(path: Path, min_size: int = 0) -> bool:
    return path.exists() and path.stat().st_size > min_size


def glob_files(pattern: str, directory: Path) -> list[Path]:
    return sorted(directory.glob(pattern))


# ─── Workspace + engagement identity (#167) ──────────────────────────────────

def _engagement_id_candidate(engagement_dir: Path) -> Optional[str]:
    """The path segment directly below `engagements/` — the thing #168 turns
    into an opaque ID, and therefore the key to look up in the map."""
    parts = engagement_dir.parts
    lowered = [p.lower() for p in parts]
    if "engagements" not in lowered:
        return None
    idx = lowered.index("engagements")
    return parts[idx + 1] if idx + 1 < len(parts) else None


def _resolve_client_slug(engagement_dir: Path) -> Optional[str]:
    """Close the D14 seam: resolve the client slug out of `.engagement_map.json`.

    `denylist.resolve_engagement_deny_list` mines the client DIRECTORY NAME for
    deny-list terms — that is how `hdfc` becomes a term. Once #168 makes those
    directories opaque IDs, the name degrades to a meaningless token and the
    client's own name would silently fall off the deny-list. D14 deliberately
    did NOT teach `denylist.py` to read the map (that would break
    `drift_check.py`'s byte-for-byte parity with the self-contained copy inside
    `mcp-query-guard.py`); it left the existing `client_slug=` parameter as the
    seam and made #167 responsible for threading it. This is that thread.

    Returns None when there is no map yet — pre-#168 the directory name IS the
    client slug, which is exactly what the deny-list already mines, so None is
    the CORRECT value and not a degradation.

    Fails loudly, rather than returning None, when the directory name already
    LOOKS like an opaque ID but the map cannot resolve it. That combination is
    the dangerous one: an opaque directory with no map entry yields a deny-list
    of one meaningless token, and carrying on would ship an unscrubbed client
    name while every log line said the run succeeded. `MapUnreadableError`
    propagates in every case — a corrupt map is never treated as "no map".
    """
    candidate = _engagement_id_candidate(engagement_dir)
    if candidate is None:
        return None
    looks_opaque = bool(_OPAQUE_ID_RE.match(candidate))
    try:
        record = _identity.client_for_id(candidate)
    except (_identity.MapNotFoundError, _identity.UnknownEngagementIdError):
        if looks_opaque:
            raise
        return None
    return record.get("slug") or record.get("client") or None


def _clear_recorded_workspace(engagement_dir: Path):
    """Drop a previous run's workspace (and its pointer) if one is recorded.

    Called only when a NEW workspace is being materialised, so a re-run never
    accumulates orphaned copies of scrubbed client material under
    `.cortex-workspaces/`.
    """
    pointer = engagement_dir / WORKSPACE_POINTER
    if not pointer.exists():
        return
    try:
        stale = Path(pointer.read_text(encoding="utf-8").strip())
    except OSError:
        stale = None
    if stale is not None and stale.name.startswith(_identity.WORKSPACE_PREFIX) \
            and stale.parent == WORKSPACE_ROOT and stale.is_dir():
        shutil.rmtree(str(stale), ignore_errors=True)
    pointer.unlink(missing_ok=True)


def _sweep_stray_mappings(engagement_dir: Path):
    """Get every `.anon_mapping_*.json` out of `inputs/` before the workspace
    is built. THIS IS A LEAK GATE, not tidying.

    `materialise_workspace` copies every file under `inputs/` whose name starts
    with `.anon_` — and `.anon_mapping_<name>.json` starts with `.anon_`. But a
    mapping file is not a scrubbed artifact: it is the OPPOSITE of one. It holds
    the real values keyed by their placeholders, chmod 600, and copying it into
    the directory an agent runs in would hand the model the entire
    de-anonymisation key alongside the scrubbed text.

    The normal path never reaches here with anything to do — this run's mappings
    are deleted the moment `.pii_mapping.json` exists. What this catches is the
    residue: a previous run killed between writing a per-transcript mapping and
    writing the combined one, or an engagement anonymised by hand through the
    CLI. Two cases, two answers:

      - `.pii_mapping.json` exists -> the strays are superseded by it. Delete.
      - it does not -> those files are the ONLY record of some earlier run's
        substitutions, so deleting them would make that run's deliverable
        permanently unrestorable. Move them somewhere outside `inputs/`
        (mode preserved) and say so loudly. Never leave them where they would
        be copied.
    """
    inputs_dir = engagement_dir / "inputs"
    strays = sorted(inputs_dir.glob(".anon_mapping_*.json"))
    if not strays:
        return
    if (engagement_dir / ".pii_mapping.json").exists():
        for p in strays:
            p.unlink(missing_ok=True)
        log(f"  🔒 Removed {len(strays)} superseded per-transcript mapping "
            f"file(s) from inputs/ before building the workspace", C.DIM)
        return
    quarantine = engagement_dir / ".pii_orphan_mappings"
    quarantine.mkdir(exist_ok=True)
    quarantine.chmod(0o700)
    for p in strays:
        target = quarantine / p.name
        shutil.move(str(p), str(target))
        target.chmod(0o600)
    log(f"  ⚠ {len(strays)} per-transcript PII mapping file(s) were still in "
        f"inputs/ with no combined .pii_mapping.json — an earlier run was "
        f"interrupted. They hold real client values, so they have been moved to "
        f".pii_orphan_mappings/ rather than deleted or copied into the "
        f"workspace.", C.YELLOW)


def _materialise_run_workspace(engagement_dir: Path):
    """Build THE workspace for this run and record where it is.

    One workspace per RUN, not per step (identity.py's constraint): agents
    accumulate their output in `<workspace>/outputs/`, and `copy_back()`
    returns the whole tree to the real engagement at the end.
    """
    _sweep_stray_mappings(engagement_dir)
    _clear_recorded_workspace(engagement_dir)
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    ws = _identity.materialise_workspace(engagement_dir, workspace_root=WORKSPACE_ROOT)

    # Belt-and-braces on the gate above: prove no mapping file made it in.
    # `materialise_workspace` renames everything it copies, so the check is on
    # the SOURCE each workspace file came from, not the neutral name.
    smuggled = sorted(
        neutral for neutral, source in ws.input_names.items()
        if source.name.startswith(".anon_mapping_")
    )
    if smuggled:
        ws.cleanup()
        raise ClientIdentifierLeak(
            "REFUSING to run: PII mapping file(s) were copied into the neutral "
            f"workspace as {smuggled}. A mapping file is the de-anonymisation "
            "key, not a scrubbed artifact. The workspace has been destroyed and "
            "nothing was sent."
        )

    pointer = engagement_dir / WORKSPACE_POINTER
    pointer.write_text(str(ws.path) + "\n", encoding="utf-8")
    pointer.chmod(0o600)
    log(f"  🔒 Neutral workspace ready ({len(ws.input_names)} scrubbed input(s)): {ws.path}",
        C.CYAN)
    return ws


def _restore_workspace(engagement_dir: Path):
    """Reattach `--resume-from` to the workspace the interrupted run was using.

    THE DECISION (`--resume-from`): REATTACH to the persisted workspace; do not
    re-materialise. Recorded here because the two options are not equivalent.

    Re-materialising cannot be made deterministic in the way that matters. The
    directory NAME could be (mkdtemp's randomness is incidental), but the
    workspace's `outputs/` cannot: everything the interrupted run produced
    lives there, and rebuilding it would mean copying the real engagement's
    `outputs/` back in. Those files may already have been through
    `deanonymize_dir` on a previous completed run — i.e. they hold the client's
    REAL name — so seeding from them would re-inject into the workspace exactly
    the identifiers this ticket exists to keep out of it, on the one code path
    nobody exercises until something has already gone wrong. Reattaching has no
    such failure mode: the workspace holds placeholder-form artifacts because
    that is the only form ever written into it.

    If the workspace is gone (temp reaped, different machine, cleaned up after a
    successful run), this raises and names the fix rather than silently falling
    back to a client-named path — identity.py's no-silent-fallbacks rule.
    """
    pointer = engagement_dir / WORKSPACE_POINTER
    hint = ("Re-run with `--resume-from discovery` (or with no --resume-from) to "
            "rebuild it; the pipeline will re-anonymise the inputs and start a "
            "fresh workspace.")
    if not pointer.exists():
        raise RuntimeError(
            "--resume-from needs the workspace this engagement's previous run "
            f"used, but no {WORKSPACE_POINTER} record exists. " + hint
        )
    path = Path(pointer.read_text(encoding="utf-8").strip())
    if not (path / "outputs").is_dir():
        raise RuntimeError(
            "--resume-from needs the workspace this engagement's previous run "
            f"used, but it no longer exists on disk. " + hint
        )
    # `input_names` maps neutral workspace filename -> the client-named artifact
    # it came from. It is in-memory-only by design and is NOT reconstructed here:
    # its single consumer is discovery's `transcript_path`, and resuming from any
    # step at or after `parallel_a` never invokes discovery. Resuming discovery
    # itself re-materialises instead of restoring.
    ws = _identity.Workspace(path, engagement_dir, {})
    log(f"  🔒 Reattached to the run's neutral workspace: {ws.path}", C.CYAN)
    return ws


def _publish_workspace_outputs(ws) -> int:
    """Copy everything the workspace produced back to the real engagement's
    `outputs/`, preserving relative structure.

    Delegates to `Workspace.copy_back()`, whose atomicity guarantee is stated
    precisely in identity.py: staging inside the engagement directory (same
    filesystem) for all the real I/O, then metadata-only `os.replace` renames.
    Not reimplemented here. Idempotent — safe to call after every step, which is
    what keeps an interrupted run's work out of the workspace-only limbo.
    """
    try:
        report = ws.copy_back()
    except _identity.CopyBackInterrupted as exc:
        log(f"  ✗ COPY-BACK INTERRUPTED — {exc}", C.RED)
        raise
    if report["count"]:
        log(f"  📤 Published {report['count']} file(s) to the engagement's outputs/",
            C.GREEN)
    return report["count"]


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Strip YAML frontmatter from agent markdown. Returns (body, model)."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2].strip()
            # Extract model from frontmatter
            model_match = re.search(r"^model:\s*(\w+)", frontmatter, re.MULTILINE)
            model = model_match.group(1) if model_match else "sonnet"
            return body, model
    return text, "sonnet"


def parse_agent_md(agent_name: str) -> tuple[str, str]:
    """Read agent .md file, return (system_prompt_body, model)."""
    path = AGENTS_DIR / f"{agent_name}.md"
    return _split_frontmatter(read_file(path))


# ─── Mode Composer (skill-first contracts — .design/solution-design-v3.md) ────
#
# Extracted agents carry their operating contracts as `### Mode: <name>` blocks
# inside a `## Modes` section of their own .md file. The composer builds the
# invocation prompt from core identity + ONE selected mode + runtime params.
# All 10 pipeline agents are mode-extracted; the legacy inline-prompt path in
# run_agent was deleted with the final extraction (narrative-assembler, #114).
# parse_agent_modes still returns {} for agent files without a `## Modes`
# section (Inspire/standalone-only agents — never invoked by this script).

_MODES_HEADING = re.compile(r"(?m)^##\s+Modes\s*$")
_NEXT_H2 = re.compile(r"(?m)^##[ \t]+(?!Modes\s*$)\S")
_MODE_SPLIT = re.compile(r"(?m)^###\s+Mode:\s*")
_MODE_NAME = re.compile(r"^([A-Za-z0-9_-]+)")
_YAML_FENCE = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)
_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

# Complete key set per the design — no speculative fields.
_MODE_CONTRACT_KEYS = {
    "inputs", "degraded", "knowledge", "outputs",
    "checkpoint", "phases", "gates", "params",
}
_INPUTS_KEYS = {"required", "optional"}


def _import_yaml():
    try:
        import yaml
        return yaml
    except ImportError as e:
        raise RuntimeError(
            "parse_agent_modes requires PyYAML (`pip install pyyaml`) — "
            "only needed for mode-extracted agents; legacy inline prompts are unaffected."
        ) from e


def parse_agent_modes(path) -> dict:
    """Parse the `## Modes` section of an agent .md file.

    Returns {mode_name: {"contract": dict, "prose": str, "raw": str}} where
    `contract` is the parsed fenced-YAML block, `prose` is the remaining
    behavior text, and `raw` is the full mode block (heading + yaml + prose)
    as written. A file without a `## Modes` section returns {} (legacy agent).
    """
    path = Path(path)
    body, _ = _split_frontmatter(read_file(path))

    heading = _MODES_HEADING.search(body)
    if not heading:
        return {}
    section = body[heading.end():]
    # The Modes section ends at the next level-2 heading, if any.
    nxt = _NEXT_H2.search(section)
    if nxt:
        section = section[:nxt.start()]

    yaml = _import_yaml()
    modes: dict = {}
    blocks = _MODE_SPLIT.split(section)[1:]  # drop preamble before first mode
    for block in blocks:
        name_match = _MODE_NAME.match(block.strip())
        if not name_match:
            raise ValueError(f"{path.name}: malformed '### Mode:' heading in ## Modes section")
        name = name_match.group(1)
        if name in modes:
            raise ValueError(f"{path.name}: duplicate mode '{name}' in ## Modes section")

        fence = _YAML_FENCE.search(block)
        contract = {}
        if fence:
            contract = yaml.safe_load(fence.group(1)) or {}
        if not isinstance(contract, dict):
            raise ValueError(f"{path.name}: mode '{name}' YAML contract must be a mapping")

        unknown = set(contract) - _MODE_CONTRACT_KEYS
        if unknown:
            raise ValueError(
                f"{path.name}: mode '{name}' has unknown contract key(s): {sorted(unknown)} "
                f"(allowed: {sorted(_MODE_CONTRACT_KEYS)})"
            )
        inputs = contract.get("inputs", {})
        if inputs and (not isinstance(inputs, dict) or set(inputs) - _INPUTS_KEYS):
            raise ValueError(
                f"{path.name}: mode '{name}' inputs must be a mapping with keys "
                f"{sorted(_INPUTS_KEYS)} only"
            )

        prose = _YAML_FENCE.sub("", block)
        # Drop the name line (incl. trailing comments) — keep behavior prose only.
        prose = "\n".join(prose.strip().split("\n")[1:]).strip()
        modes[name] = {
            "contract": contract,
            "prose": prose,
            "raw": f"### Mode: {name}\n" + "\n".join(block.strip().split("\n")[1:]).strip(),
        }
    return modes


def _substitute_params(text: str, params: dict, context: str) -> str:
    """Substitute {placeholder} tokens with param VALUES. Unknown placeholders raise."""
    def repl(m):
        key = m.group(1)
        if key not in params:
            raise KeyError(
                f"Unknown placeholder '{{{key}}}' in {context} — not provided in params "
                f"(available: {sorted(params)})"
            )
        return str(params[key])
    return _PLACEHOLDER.sub(repl, text)


def _preflight_required_inputs(contract: dict, params: dict, agent_name: str, mode: str):
    """Check the mode's required input files exist before spending an agent run.

    degraded: refuse  -> missing required input is a hard error (pipeline behavior)
    otherwise         -> warn and proceed (the agent handles degradation per its prose)
    """
    required = (contract.get("inputs") or {}).get("required") or []
    missing = []
    for entry in required:
        resolved = _substitute_params(str(entry), params, f"{agent_name}/{mode} inputs.required")
        p = Path(resolved)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.exists():
            missing.append(str(p))
    if not missing:
        return
    degraded = contract.get("degraded", "refuse")
    if degraded == "refuse":
        raise RuntimeError(
            f"REQUIRED INPUT MISSING: agent '{agent_name}' mode '{mode}' (degraded: refuse) "
            f"cannot run — missing: {missing}"
        )
    log(f"  ⚠ {agent_name}/{mode}: missing optional-degradable required input(s): {missing} "
        f"(degraded: {degraded} — proceeding)", C.YELLOW)


def compose_prompt(agent_name: str, mode: str, params: Optional[dict] = None) -> str:
    """Compose an invocation prompt: core identity + ONE mode block + params table.

    `agent_name` is an agent in .claude/agents/, or a direct path to a .md file
    (used by fixtures/tests). Core identity is everything above `## Modes`
    (frontmatter stripped); unselected modes are stripped entirely. Placeholder
    substitution applies to the selected mode block only, and params carry
    VALUES only (paths, domain) — never instructions.
    """
    params = dict(params or {})
    candidate = Path(agent_name)
    if candidate.suffix == ".md" and candidate.exists():
        path = candidate
    else:
        path = AGENTS_DIR / f"{agent_name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Agent file not found: {path}")

    modes = parse_agent_modes(path)
    if mode not in modes:
        available = ", ".join(sorted(modes)) if modes else "none (no ## Modes section — legacy inline agent)"
        raise ValueError(
            f"Agent '{agent_name}' does not declare mode '{mode}'. Available modes: {available}"
        )

    body, _ = _split_frontmatter(read_file(path))
    core = body[:_MODES_HEADING.search(body).start()].rstrip()

    block = _substitute_params(modes[mode]["raw"], params, f"{agent_name}/{mode} mode block")
    _preflight_required_inputs(modes[mode]["contract"], params, str(agent_name), mode)

    lines = [
        "## Runtime Parameters",
        "",
        "These are runtime VALUES only (paths, domain) — never instructions.",
        "",
        "| Parameter | Value |",
        "| --- | --- |",
    ]
    for key in sorted(params):
        lines.append(f"| {key} | {params[key]} |")
    params_table = "\n".join(lines) if params else "## Runtime Parameters\n\n(none)"

    return f"{core}\n\n## Active Mode\n\n{block}\n\n{params_table}\n"


def assert_file_exists(path: Path, agent_name: str, min_size: int = 0):
    if not file_exists(path, min_size):
        size = path.stat().st_size if path.exists() else 0
        raise RuntimeError(
            f"VALIDATION FAILED: {agent_name} did not produce {path.name} "
            f"(exists={path.exists()}, size={size}, min_required={min_size})"
        )
    log(f"  ✓ {path.name} ({path.stat().st_size:,} bytes)", C.GREEN)


def _sum_costs(results) -> float:
    """Sum costs from agent results, handling exceptions in gather results."""
    total = 0.0
    for r in results:
        if isinstance(r, ResultMessage) and r.total_cost_usd:
            total += r.total_cost_usd
    return total


# ROI capping/validation logic (MAX_BACKBASE_IMPACT, SEGMENT_ROI_RANGES,
# _compute_5yr_roi, _validate_roi_config) moved to artifact_boundary.py so the
# same gates run in both the pipeline and standalone skill paths.


# ─── Resilient Query Wrapper ──────────────────────────────────────────────────

async def _resilient_query(prompt: str, options: ClaudeAgentOptions, label: str):
    """Wrap SDK query() for resilience (e.g., filtering, retry logic)."""
    async for message in query(prompt=prompt, options=options):
        yield message


# ─── Agent Runner ─────────────────────────────────────────────────────────────

async def run_agent(
    agent_name: str,
    cwd: Optional[Path] = None,
    model: str = "sonnet",
    max_turns: int = 50,
    label: str = "",
    *,
    mode: str,
    params: Optional[dict] = None,
) -> ResultMessage:
    """Run a single agent via the SDK. Returns the ResultMessage.

    The invocation prompt is ALWAYS composed from the agent's own ## Modes
    contract (core identity + the selected mode block + a runtime-params
    table). The legacy inline-prompt branch was deleted after the tenth and
    final extraction (narrative-assembler, ticket #114) left zero callers.
    """
    if cwd is None:
        raise ValueError("run_agent: 'cwd' is required")

    display = label or agent_name
    start = time.time()
    log(f"  ▶ Launching {display}...", C.YELLOW)

    # Prompt composed from core identity + selected mode + params.
    system_prompt = compose_prompt(agent_name, mode, params)
    _, agent_model = parse_agent_md(agent_name)
    prompt = (
        f"Execute your '{mode}' mode contract now. All runtime parameter values "
        "are listed in the Runtime Parameters table of your instructions."
    )
    use_model = model or agent_model

    # V5: Inject tool constraint into system prompt to prevent Task tool usage
    system_prompt = (
        "IMPORTANT: You MUST NOT use the Task tool to spawn sub-agents. "
        "Do all work directly using Read, Write, Edit, Bash, Glob, Grep. "
        "Using Task wastes turns and risks hitting output limits.\n\n"
        + system_prompt
    )

    # #167 CHOKE POINT — the last thing before anything leaves this machine.
    # Every agent in the chain passes through here, so this is where the
    # ticket's guarantee is enforced rather than asserted: if the composed
    # prompt or the cwd still names the client, nothing is sent.
    _assert_neutral_invocation(agent_name, cwd, system_prompt)
    _dump_composed_prompt(agent_name, mode, cwd, system_prompt)

    # Map model names to Claude model IDs
    model_map = {
        "sonnet": "claude-sonnet-4-6",
        "opus": "claude-opus-4-6",
        "haiku": "claude-haiku-4-5-20251001",
    }
    model_id = model_map.get(use_model, use_model)

    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep",
                        "WebSearch", "WebFetch"],
        permission_mode="bypassPermissions",
        cwd=str(cwd),
        model=model_id,
        max_turns=max_turns,
        # Unset CLAUDECODE to allow nested sessions when running inside Claude Code
        env={"CLAUDECODE": ""},
        # Explicit, not left to the SDK default: makes project .claude/settings.json
        # hooks (anonymize-guard.py, mcp-query-guard.py, ...) load independently of
        # the setting_sources=None-vs-[] serialization change across SDK 0.1.59 —
        # see the claude-agent-sdk pin comment in requirements.txt for the full story.
        setting_sources=["user", "project", "local"],
    )

    result = None
    _trace_text: list[str] = []
    async for message in _resilient_query(prompt, options, display):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    preview = block.text.strip()[:120].replace("\n", " ")
                    log(f"  [{display}] {preview}", C.DIM)
                    _trace_text.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    tool_preview = str(block.input)[:80] if block.input else ""
                    log(f"  [{display}] >> {block.name}({tool_preview})", C.DIM)
        elif isinstance(message, ResultMessage):
            result = message

    elapsed = time.time() - start
    cost = result.total_cost_usd if result and result.total_cost_usd else 0
    turns = result.num_turns if result else 0
    log(f"  ✓ {display} done — {elapsed:.0f}s, {turns} turns, ${cost:.3f}", C.GREEN)
    # A2: live per-call Langfuse trace (non-blocking, no-op without LANGFUSE keys)
    try:
        import sys as _sys
        _ev = REPO_ROOT / "evals"
        if str(_ev) not in _sys.path:
            _sys.path.insert(0, str(_ev))
        from runtime import log_agent_call as _lac
        _lac(agent_name, prompt, "\n".join(_trace_text), model_id, cost, turns, elapsed)
    except Exception:
        pass
    return result


# ─── Checkpoint Management ────────────────────────────────────────────────────

def present_checkpoint(
    agent_name: str,
    outputs_dir: Path,
    express: bool = False,
    non_interactive: bool = False,
    cp_suffix: str = "",
) -> str:
    """Read checkpoint file, present to consultant (or auto-approve), write approval."""
    cp_name = f"CHECKPOINT_{agent_name}{cp_suffix}"
    cp_file = outputs_dir / f"{cp_name}.md"

    if not cp_file.exists():
        log(f"  ⚠ No checkpoint file: {cp_file.name}", C.YELLOW)
        return "No checkpoint produced — proceeding."

    content = read_file(cp_file)

    if express or non_interactive:
        mode = "EXPRESS" if express else "NON-INTERACTIVE"
        log(f"  ⚡ {mode}: Auto-approving {cp_name}", C.YELLOW)
        # Print summary so Claude Code can show it to consultant
        summary_lines = content.strip().split("\n")[:20]
        print(f"\n  [CHECKPOINT SUMMARY: {agent_name}{cp_suffix}]")
        for line in summary_lines:
            print(f"  | {line}")
        if len(content.strip().split("\n")) > 20:
            print(f"  | ... ({len(content)} chars total)")
        print()
        approval = f"{mode}: Auto-approved with agent recommendations."
    else:
        print(f"\n{C.BOLD}{'─' * 60}{C.RESET}")
        print(f"{C.BOLD}CHECKPOINT: {agent_name}{cp_suffix}{C.RESET}")
        print(f"{'─' * 60}")
        # Show full checkpoint content
        print(content)
        print(f"{'─' * 60}")
        approval = input(f"\n{C.BOLD}Your feedback (or press Enter to approve): {C.RESET}")
        if not approval.strip():
            approval = "APPROVED — proceed with recommendations."

    approval_file = outputs_dir / f"{cp_name}_APPROVED.md"
    write_file(approval_file, f"# {cp_name} — Approved\n\n{approval}\n")
    return approval


def present_checkpoints_batched(
    agents: list[str],
    outputs_dir: Path,
    express: bool = False,
    non_interactive: bool = False,
) -> dict[str, str]:
    """Present multiple checkpoints at once. Returns dict of agent->approval."""
    approvals = {}

    if express or non_interactive:
        for agent in agents:
            approvals[agent] = present_checkpoint(agent, outputs_dir, express=True, non_interactive=non_interactive)
        return approvals

    print(f"\n{C.BOLD}{C.CYAN}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  CHECKPOINTS READY: {len(agents)} agents completed{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * 60}{C.RESET}")

    for agent in agents:
        cp_file = outputs_dir / f"CHECKPOINT_{agent}.md"
        if cp_file.exists():
            content = read_file(cp_file)
            print(f"\n{C.BOLD}── {agent} ──{C.RESET}")
            # Show first 800 chars as summary
            print(content[:800])
            if len(content) > 800:
                print(f"{C.DIM}  ... ({len(content)} chars total){C.RESET}")

    print(f"\n{'─' * 60}")
    feedback = input(
        f"{C.BOLD}Type 'approve all' or provide feedback per agent: {C.RESET}"
    )

    if "approve all" in feedback.lower() or not feedback.strip():
        for agent in agents:
            approval_file = outputs_dir / f"CHECKPOINT_{agent}_APPROVED.md"
            write_file(approval_file, f"# CHECKPOINT_{agent} — Approved\n\nAPPROVED — proceed.\n")
            approvals[agent] = "APPROVED"
    else:
        # Individual feedback mode
        for agent in agents:
            agent_feedback = input(f"  Feedback for {agent} (Enter=approve): ")
            if not agent_feedback.strip():
                agent_feedback = "APPROVED — proceed."
            approval_file = outputs_dir / f"CHECKPOINT_{agent}_APPROVED.md"
            write_file(approval_file, f"# CHECKPOINT_{agent} — Approved\n\n{agent_feedback}\n")
            approvals[agent] = agent_feedback

    return approvals


# ─── Pipeline Steps ───────────────────────────────────────────────────────────

def _generate_discovery_checkpoint(outputs_dir: Path, transcripts: list[Path]) -> Path:
    """Generate checkpoint by concatenating interim summaries. No LLM needed."""
    checkpoint_path = outputs_dir / "CHECKPOINT_discovery.md"
    sections = []
    sections.append("# Discovery Checkpoint\n")
    sections.append(f"**Transcripts processed:** {len(transcripts)}\n")

    for i, t in enumerate(transcripts, 1):
        interim = outputs_dir / f"interim_transcript_{i}.md"
        if interim.exists():
            content = interim.read_text()
            # Extract Summary section (first lines until ## Evidence Table)
            lines = content.split('\n')
            summary_lines = []
            for line in lines:
                if line.startswith('## Evidence') or line.startswith('## Pain') or len(summary_lines) > 40:
                    break
                summary_lines.append(line)
            sections.append(f"\n---\n## Transcript {i}: {t.name}\n")
            sections.append('\n'.join(summary_lines))
            sections.append(f"\n*Full interim: interim_transcript_{i}.md ({interim.stat().st_size:,} bytes)*\n")

    sections.append("\n---\n## Consultant Action Required\n")
    sections.append("Review the summaries above. Full interim files are available for detail.\n")
    sections.append("Approve to proceed with finalize phase, or provide feedback.\n")

    checkpoint_path.write_text('\n'.join(sections))
    log(f"  ✓ Checkpoint generated ({checkpoint_path.stat().st_size:,} bytes)", C.GREEN)
    return checkpoint_path


# The lean extraction format (formerly the `_LEAN_FORMAT` f-string shared by the
# single- and multi-transcript discovery prompts) now lives in the agent's own
# contract: .claude/agents/discovery-transcript-interpreter.md, core section
# "Lean Interim Extraction Format" — carried into every composed pipeline prompt.
# _generate_discovery_checkpoint() below still depends on its heading contract
# ("## Summary" ... breaks at "## Evidence"/"## Pain").


async def step_discovery(
    engagement_dir: Path,
    express: bool,
    non_interactive: bool = False,
    client_slug: Optional[str] = None,
) -> tuple:
    """Run Discovery: anonymise inputs -> materialise the neutral workspace ->
    parallel lean extraction -> Python checkpoint -> finalize from interims.

    Returns `(timing_dict, workspace)`. Discovery owns workspace creation
    because the workspace can only be built once the `.anon_` artifacts exist,
    and this is where they are produced. ONE workspace per run, not per step —
    every later step receives this same object.
    """
    start = time.time()
    cost = 0.0
    inputs_dir = engagement_dir / "inputs"
    transcripts = sorted(inputs_dir.glob("transcript_*.md"))
    # (engagement_intake.md is now carried by the agent's pipeline mode contract
    #  via the {engagement_dir} param — no inline prompt references it here.)

    if not transcripts:
        log("  ⚠ No transcripts found in inputs/", C.YELLOW)
        # Still materialise: Block A reads discovery OUTPUTS, not transcripts,
        # and every downstream step needs somewhere neutral to run.
        return {"elapsed": 0, "cost": 0}, _materialise_run_workspace(engagement_dir)

    log(f"  Found {len(transcripts)} transcript(s)")

    # --- PII Anonymization: strip client names, emails, phones before sending to API ---
    # Ticket #161 fix: one SHARED entity_mapping dict threads through the whole
    # transcript loop instead of each transcript anonymizing standalone. Two bugs,
    # fixed together — fixing only one reintroduces the other:
    #   1. A shallow `combined_mapping.update(json.loads(...))` across per-transcript
    #      v2 mappings ({"version": 2, "entities": {...}}) REPLACES the whole
    #      `entities` sub-dict each time, discarding every earlier transcript's
    #      mapping. Fixed by accumulating in one dict instead of merging N files.
    #   2. Each transcript anonymized standalone restarts Presidio's instance
    #      counter at 1, so transcript A's <EMAIL_ADDRESS_1> and transcript B's
    #      <EMAIL_ADDRESS_1> would be DIFFERENT values — a deep merge of `entities`
    #      would then bind one placeholder to two different values, the exact
    #      one-key-per-category collision this whole engine exists to eliminate.
    #      Fixed by sharing one entity_mapping dict (mutated in place by
    #      engine.py's instance-counter operator) so numbering is continuous and a
    #      repeated value reuses its existing placeholder across every file.
    #
    # NOT THREAD-SAFE — this shared dict is mutated with no locking (see
    # scripts/pii/engine.py's module docstring). Anonymization MUST stay
    # sequential; do not parallelize this loop without replacing the operator.
    entity_mapping: dict = {}
    anon_transcripts = []
    per_transcript_mappings: list = []
    for t in transcripts:
        try:
            # per-transcript mapping_path is written to disk (chmod 0600) but not
            # used here — the combined .pii_mapping.json below is built directly
            # from the shared entity_mapping dict, which is the authoritative state.
            # #167: it is DELETED once that combined file exists, and only then —
            # see the cleanup below.
            anon_path, mapping_path = anonymize_transcript_file(
                t, engagement_dir, output_dir=inputs_dir,
                entity_mapping=entity_mapping, client_slug=client_slug,
            )
            anon_transcripts.append(anon_path)
            per_transcript_mappings.append(mapping_path)
            log(f"    Anonymized: {t.name} → {anon_path.name}")
        except Exception as e:
            # FAIL CLOSED: never send raw PII to the API. Skip this transcript and
            # surface the failure loudly rather than silently leaking the original.
            # Unchanged by #167 — and structurally reinforced by it: the workspace
            # below copies ONLY `.anon_` artifacts, so a transcript that failed
            # here has no scrubbed sibling and therefore cannot reach an agent
            # even by accident.
            log(f"    ✗ Anonymization FAILED for {t.name} ({type(e).__name__}: {e}) — "
                f"SKIPPING (raw transcript will NOT be sent to the API).", C.RED)

    # Use anonymized transcripts for all downstream processing
    transcripts = anon_transcripts

    # engagement_intake.md is a deny-list SOURCE — it exists to hold the client's
    # name — so the raw file must never enter a directory an agent runs in
    # (identity.py's materialise_workspace docstring leaves it no exemption).
    # Scrub it through the SAME shared mapping instead, so its content reaches
    # the workspace only in `.anon_` form and any client name it holds gets the
    # same placeholder it gets everywhere else.
    intake_file = inputs_dir / "engagement_intake.md"
    if intake_file.exists():
        try:
            anon_intake, intake_mapping = anonymize_transcript_file(
                intake_file, engagement_dir, output_dir=inputs_dir,
                entity_mapping=entity_mapping, client_slug=client_slug,
            )
            per_transcript_mappings.append(intake_mapping)
            log(f"    Anonymized: {intake_file.name} → {anon_intake.name}")
        except Exception as e:
            log(f"    ✗ Anonymization FAILED for {intake_file.name} "
                f"({type(e).__name__}: {e}) — SKIPPING (the raw intake will NOT "
                f"be sent to the API).", C.RED)

    # Save combined mapping for de-anonymization of final outputs. `entity_mapping`
    # is already the full accumulated state (every transcript that succeeded above,
    # continuously numbered, one placeholder per distinct value) — write it
    # directly in the v2 nested-by-entity-type shape rather than re-merging files.
    if entity_mapping:
        combined_mapping = {
            "version": 2,
            "entities": {etype: dict(values) for etype, values in sorted(entity_mapping.items())},
        }
        mapping_file = engagement_dir / ".pii_mapping.json"
        mapping_file.write_text(json.dumps(combined_mapping, indent=2))
        mapping_file.chmod(0o600)  # Restrict access — this file contains PII
        substitution_count = sum(len(values) for values in entity_mapping.values())
        log(f"    PII mapping saved ({substitution_count} substitutions)")

        # ONLY NOW: drop the per-transcript mappings. Each is a chmod-600 file
        # holding real PII, superseded byte-for-byte by the combined file just
        # written (the shared entity_mapping IS their union). Deleting them any
        # earlier would open a window where an interrupted run has real values on
        # disk in neither place and the deliverable can never be restored.
        # `--resume-from` reads only `.pii_mapping.json`.
        removed = 0
        for mp in per_transcript_mappings:
            try:
                Path(mp).unlink(missing_ok=True)
                removed += 1
            except OSError as e:
                log(f"    ⚠ could not remove per-transcript mapping {Path(mp).name} "
                    f"({type(e).__name__}: {e}) — it still holds real PII", C.YELLOW)
        if removed:
            log(f"    Per-transcript mappings cleaned up ({removed} file(s))")

    # ── THE NEUTRAL WORKSPACE ────────────────────────────────────────────────
    # Built here, after anonymisation, because it copies `.anon_` artifacts and
    # nothing else. Every path parameter and every `cwd` from this point on
    # resolves inside it; the client-named engagement directory is never named
    # to an agent again.
    workspace = _materialise_run_workspace(engagement_dir)
    outputs_dir = workspace.outputs
    # Real `.anon_` artifact path -> the neutral name it was copied in under.
    ws_name_for = {v.resolve(): k for k, v in workspace.input_names.items()}
    transcripts = [
        workspace.inputs / ws_name_for[t.resolve()]
        for t in transcripts if t.resolve() in ws_name_for
    ]

    # discovery-transcript-interpreter is mode-extracted (skill-first contracts):
    # prompts are composed from .claude/agents/discovery-transcript-interpreter.md
    # (## Modes -> pipeline) via compose_prompt — no inline f-strings. Params
    # carry VALUES only; out-of-phase params are explicit "(n/a — ...)" markers
    # per the mode contract. The agent's inputs here are the ALREADY-anonymized
    # .anon_transcript_* files produced above — anonymization stays
    # orchestrator-owned (fail-closed, see the loop above), never agent-run.
    def _interim_params(transcript: Path, index: int) -> dict:
        return {
            "engagement_dir": workspace.path,
            "outputs_dir": outputs_dir,
            "phase": "interim",
            "transcript_path": transcript,
            "transcript_index": index,
            "transcript_count": len(transcripts),
            "interim_files": "(n/a — interim phase)",
        }

    if len(transcripts) == 1:
        # Single transcript: lean extraction -> Python checkpoint
        result = await run_agent(
            "discovery-transcript-interpreter",
            cwd=workspace.path,
            label="Discovery (1 transcript)",
            max_turns=15,
            mode="pipeline",
            params=_interim_params(transcripts[0], 1),
        )
        cost += result.total_cost_usd if result and result.total_cost_usd else 0
    else:
        # Multiple transcripts: extract ALL in parallel with lean format
        log(f"  Launching {len(transcripts)} transcript extractions in parallel...")
        extract_tasks = []
        for i, transcript in enumerate(transcripts, 1):
            extract_tasks.append(run_agent(
                "discovery-transcript-interpreter",
                cwd=workspace.path,
                label=f"Discovery (T{i}/{len(transcripts)})",
                max_turns=15,
                mode="pipeline",
                params=_interim_params(transcript, i),
            ))

        # Fire all transcript extractions simultaneously
        results = await asyncio.gather(*extract_tasks, return_exceptions=True)
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                log(f"  ✗ Transcript {i} extraction FAILED: {result}", C.RED)
        cost += _sum_costs(results)

    # Generate checkpoint in Python (no LLM) — instant
    _generate_discovery_checkpoint(outputs_dir, transcripts)

    # Checkpoint review — T2 FIX: was express=False, now express=express
    present_checkpoint("discovery", outputs_dir, express=express, non_interactive=non_interactive)

    # Phase 2: Finalize registers — reads interims directly (NOT original transcripts).
    # Composed from the same ## Modes -> pipeline contract, phase "finalize";
    # the enumerated interim list travels as a VALUES-only param.
    interim_files = sorted(outputs_dir.glob("interim_transcript_*.md"))
    interim_list = ", ".join(str(f) for f in interim_files)

    # T1 FIX: added max_turns=15
    result = await run_agent(
        "discovery-transcript-interpreter",
        cwd=workspace.path,
        label="Discovery (finalize)",
        max_turns=15,
        mode="pipeline",
        params={
            "engagement_dir": workspace.path,
            "outputs_dir": outputs_dir,
            "phase": "finalize",
            "transcript_path": "(n/a — finalize phase)",
            "transcript_index": "n/a",
            "transcript_count": len(interim_files),
            "interim_files": interim_list,
        },
    )
    cost += result.total_cost_usd if result and result.total_cost_usd else 0

    # Validate
    assert_file_exists(outputs_dir / "evidence_register.md", "Discovery")
    assert_file_exists(outputs_dir / "pain_points.md", "Discovery")
    assert_file_exists(outputs_dir / "metrics.md", "Discovery")

    return {"elapsed": time.time() - start, "cost": cost}, workspace


async def step_parallel_block_a(
    ws,
    express: bool,
    domain: str,
    non_interactive: bool = False,
) -> dict:
    """Run 5 agents in parallel after Discovery: JB, MC, Cap, ROI, Bench.

    S1: In non-interactive mode, uses single-phase (combined P1+P2) per agent
    to eliminate the P1 synchronization barrier and context reload overhead.
    Interactive mode preserves the existing P1 -> checkpoint -> P2 flow.
    """
    # #167: `engagement_dir` here is the NEUTRAL WORKSPACE, not the client-named
    # engagement directory — that is the whole point of the ticket. It is bound
    # once, at the top, so that every `cwd=` and every `"engagement_dir"` param
    # below resolves to the workspace with no per-call-site opportunity to miss
    # one. The real engagement directory is reachable only as `ws.engagement_dir`
    # and is deliberately not used in this function.
    engagement_dir = ws.path
    outputs_dir = ws.outputs
    start = time.time()
    cost = 0.0

    # The old `shared_context` f-string block (engagement dir + discovery
    # outputs + intake + domain) is gone: all Block A agents are now
    # mode-extracted, and each agent's ## Modes pipeline contract carries the
    # discovery-output/intake/domain context as inputs + params instead.

    if non_interactive:
        # ── S1: SINGLE-PHASE (non-interactive) ──────────────────────────
        # Each agent runs ONE session: analyze -> checkpoint (audit) -> final output
        # No pause, no re-launch, no context reload

        log_step("2", "PARALLEL BLOCK A — Single-Phase (5 agents, non-interactive)")

        # journey-builder is mode-extracted (skill-first contracts): its
        # prompt is composed from .claude/agents/journey-builder.md
        # (## Modes -> pipeline) via compose_prompt — no inline f-string.
        jb_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
            "phase": "single",
        }

        # market-context-researcher is mode-extracted (skill-first contracts):
        # its prompt is composed from .claude/agents/market-context-researcher.md
        # (## Modes -> pipeline) via compose_prompt — no inline f-string.
        mc_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
            "phase": "single",
        }

        # capability-assessment is mode-extracted (skill-first contracts): its
        # prompt is composed from .claude/agents/capability-assessment.md
        # (## Modes -> pipeline) via compose_prompt — no inline f-string.
        cap_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
            "phase": "single",
        }

        # roi-hypothesis-builder is mode-extracted (skill-first contracts):
        # its prompt is composed from .claude/agents/roi-hypothesis-builder.md
        # (## Modes -> pipeline) via compose_prompt — no inline f-string.
        # model="opus" is NOT passed here (matching legacy: this call site
        # never overrode the model, unlike the interactive Phase 1 call
        # below) — see the extraction commit message for the discrepancy.
        roi_hyp_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
            "phase": "single",
        }

        # benchmark-librarian is mode-extracted (skill-first contracts): its
        # prompt is composed from .claude/agents/benchmark-librarian.md
        # (## Modes -> pipeline) via compose_prompt — no inline f-string.
        bench_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
            "phase": "single",
        }

        # Fire all 5 simultaneously — single-phase with agent-specific turn caps
        # V5: Per-agent timeout of 40 min to prevent hung agents blocking the pipeline
        BLOCK_A_TIMEOUT = 40 * 60  # 40 minutes

        async def _timed_agent(name, label, max_turns, *, mode, params=None):
            """Wrap agent in timeout — returns result or raises TimeoutError.

            The prompt is composed from the agent's own ## Modes contract
            (mode= / params=) — there is no inline-prompt form anymore.
            """
            try:
                return await asyncio.wait_for(
                    run_agent(name, engagement_dir,
                              label=label, max_turns=max_turns,
                              mode=mode, params=params),
                    timeout=BLOCK_A_TIMEOUT,
                )
            except asyncio.TimeoutError:
                log(f"  ✗ {label} TIMED OUT after {BLOCK_A_TIMEOUT//60} min", C.RED)
                raise

        # Block A1: 5 agents in parallel (hypothesis builder replaces monolithic ROI)
        results = await asyncio.gather(
            _timed_agent("journey-builder", "Journey Builder", 30,
                         mode="pipeline", params=jb_params),
            _timed_agent("market-context-researcher", "Market Context", 30,
                         mode="pipeline", params=mc_params),
            _timed_agent("capability-assessment", "Capability", 25,
                         mode="pipeline", params=cap_params),
            _timed_agent("roi-hypothesis-builder", "ROI Hypothesis", 20,
                         mode="pipeline", params=roi_hyp_params),
            _timed_agent("benchmark-librarian", "Benchmark", 25,
                         mode="pipeline", params=bench_params),
            return_exceptions=True,
        )

        # V5: Validate Block A1 outputs
        agent_labels = ["Journey Builder", "Market Context", "Capability", "ROI Hypothesis", "Benchmark"]
        required_files = {
            "Journey Builder": ["journey_maps.json", "journey_maps_summary.md"],
            "Market Context": ["market_context_validated.md"],
            "Capability": ["capability_assessment.md"],
            "ROI Hypothesis": ["lever_candidates.md"],
            "Benchmark": ["benchmarks_validated.md"],
        }
        for label, result in zip(agent_labels, results):
            if isinstance(result, Exception):
                log(f"  ✗ {label} FAILED: {result}", C.RED)
            else:
                # Check required output files exist
                for fname in required_files.get(label, []):
                    fpath = outputs_dir / fname
                    if not fpath.exists() or fpath.stat().st_size < 100:
                        log(f"  ⚠ {label}: missing or empty output {fname}", C.YELLOW)

        cost += _sum_costs(results)

        # Block A2: Financial modeler (sequential — depends on A1 lever_candidates.md)
        if file_exists(outputs_dir / "lever_candidates.md"):
            log_step("2B", "ROI FINANCIAL MODEL — Sequential (reads Block A1 outputs)")

            # roi-financial-modeler is mode-extracted (skill-first contracts):
            # its prompt is composed from .claude/agents/roi-financial-modeler.md
            # (## Modes -> pipeline) via compose_prompt — no inline f-string.
            roi_model_params = {
                "engagement_dir": engagement_dir,
                "outputs_dir": outputs_dir,
                "domain": domain,
                "phase": "single",
            }

            result_a2 = await _timed_agent(
                "roi-financial-modeler", "ROI Financial Model", 25,
                mode="pipeline", params=roi_model_params,
            )
            cost += result_a2.total_cost_usd if result_a2 and result_a2.total_cost_usd else 0

            # Validate financial model outputs
            for fname in ["roi_report.md", "roi_config.json"]:
                fpath = outputs_dir / fname
                if not fpath.exists() or fpath.stat().st_size < 100:
                    log(f"  ⚠ ROI Financial Model: missing or empty output {fname}", C.YELLOW)
        else:
            log("  ⚠ Skipping ROI Financial Model — lever_candidates.md not found", C.YELLOW)

    else:
        # ── INTERACTIVE: Keep existing P1 -> checkpoint -> P2 flow ───────

        # ── Phase 1: Launch all 5 simultaneously ─────────────────────────
        log_step("2A", "PARALLEL BLOCK A — Phase 1 (5 agents simultaneously)")

        # journey-builder is mode-extracted: prompt composed from its own
        # ## Modes contract (mode="pipeline", phase carried as a param).
        jb_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
        }

        # market-context-researcher is mode-extracted: prompt composed from its
        # own ## Modes contract (mode="pipeline", phase carried as a param).
        mc_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
        }

        # capability-assessment is mode-extracted: prompt composed from its own
        # ## Modes contract (mode="pipeline", phase carried as a param).
        cap_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
        }

        # roi-hypothesis-builder is mode-extracted: prompt composed from its
        # own ## Modes contract (mode="pipeline", phase carried as a param).
        # No phase-2 continuation of its own — Phase 2 below runs
        # roi-financial-modeler, not roi-hypothesis-builder again.
        roi_hyp_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
        }

        # benchmark-librarian is mode-extracted: prompt composed from its own
        # ## Modes contract (mode="pipeline", phase carried as a param).
        bench_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
        }

        # Fire all 5 simultaneously (hypothesis builder replaces monolithic ROI)
        results = await asyncio.gather(
            run_agent("journey-builder", cwd=engagement_dir, label="Journey Builder P1",
                      mode="pipeline", params={**jb_params, "phase": "1"}),
            run_agent("market-context-researcher", cwd=engagement_dir, label="Market Context P1",
                      mode="pipeline", params={**mc_params, "phase": "1"}),
            run_agent("capability-assessment", cwd=engagement_dir, label="Capability P1",
                      mode="pipeline", params={**cap_params, "phase": "1"}),
            run_agent("roi-hypothesis-builder", cwd=engagement_dir, label="ROI Hypothesis",
                      model="opus", mode="pipeline", params={**roi_hyp_params, "phase": "1"}),
            run_agent("benchmark-librarian", cwd=engagement_dir, label="Benchmark P1",
                      mode="pipeline", params={**bench_params, "phase": "1"}),
            return_exceptions=True,
        )

        agent_names = ["journey-builder", "market-context", "capability", "roi_levers", "benchmark"]
        for name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                log(f"  ✗ {name} Phase 1 FAILED: {result}", C.RED)
        cost += _sum_costs(results)

        # ── Checkpoints (batched) ────────────────────────────────────────
        checkpoint_agents = ["journey-builder", "market-context", "capability", "roi_levers", "benchmark"]
        available = [a for a in checkpoint_agents if (outputs_dir / f"CHECKPOINT_{a}.md").exists()]
        present_checkpoints_batched(available, outputs_dir, express=express, non_interactive=non_interactive)

        # ── Phase 2: Launch all 5 again ──────────────────────────────────
        log_step("2B", "PARALLEL BLOCK A — Phase 2 (5 agents simultaneously)")

        # roi-financial-modeler is mode-extracted (skill-first contracts): its
        # prompt is composed from .claude/agents/roi-financial-modeler.md
        # (## Modes -> pipeline, phase "2") via compose_prompt — no inline
        # f-string. The modeler has no pipeline phase "1" of its own — the ROI
        # pair's Phase 1 above was roi-hypothesis-builder.
        roi_model_params = {
            "engagement_dir": engagement_dir,
            "outputs_dir": outputs_dir,
            "domain": domain,
        }

        results = await asyncio.gather(
            run_agent("journey-builder", cwd=engagement_dir, label="Journey Builder P2",
                      mode="pipeline", params={**jb_params, "phase": "2"}),
            run_agent("market-context-researcher", cwd=engagement_dir, label="Market Context P2",
                      mode="pipeline", params={**mc_params, "phase": "2"}),
            run_agent("capability-assessment", cwd=engagement_dir, label="Capability P2",
                      mode="pipeline", params={**cap_params, "phase": "2"}),
            run_agent("roi-financial-modeler", cwd=engagement_dir, label="ROI Financial Model",
                      mode="pipeline", params={**roi_model_params, "phase": "2"}),
            run_agent("benchmark-librarian", cwd=engagement_dir, label="Benchmark P2",
                      mode="pipeline", params={**bench_params, "phase": "2"}),
            return_exceptions=True,
        )

        for name, result in zip(["JB", "MC", "Cap", "ROI", "Bench"], results):
            if isinstance(result, Exception):
                log(f"  ✗ {name} Phase 2 FAILED: {result}", C.RED)
        cost += _sum_costs(results)

    # ── Validate required outputs (both modes) ───────────────────────────
    assert_file_exists(outputs_dir / "capability_assessment.md", "Capability")
    assert_file_exists(outputs_dir / "roi_report.md", "ROI")
    assert_file_exists(outputs_dir / "roi_config.json", "ROI")

    # ── ROI Reasonableness Gate ───────────────────────────────────────────
    cap_roi_config(outputs_dir / "roi_config.json")

    for f, name in [
        ("journey_maps.json", "Journey Builder"),
        ("market_context_validated.md", "Market Context"),
        ("benchmarks_validated.md", "Benchmark"),
    ]:
        if file_exists(outputs_dir / f):
            log(f"  ✓ {f} ({(outputs_dir / f).stat().st_size:,} bytes)", C.GREEN)
        else:
            log(f"  ⚠ {f} not produced by {name} (non-blocking)", C.YELLOW)

    return {"elapsed": time.time() - start, "cost": cost}


async def step_roadmap(
    ws,
    express: bool,
    non_interactive: bool = False,
) -> dict:
    """Run Roadmap agent (depends on ROI + Capability).

    S4: Single-pass in both express AND non-interactive mode.
    """
    engagement_dir = ws.path      # #167: the neutral workspace — see step_parallel_block_a
    outputs_dir = ws.outputs
    start = time.time()
    cost = 0.0

    # roadmap-prioritization is mode-extracted (skill-first contracts): its
    # prompt is composed from .claude/agents/roadmap-prioritization.md
    # (## Modes -> pipeline) via compose_prompt — no inline f-string.
    roadmap_params = {
        "engagement_dir": engagement_dir,
        "outputs_dir": outputs_dir,
    }

    # S4 FIX: Single-pass in express OR non-interactive mode
    if express or non_interactive:
        result = await run_agent("roadmap-prioritization", cwd=engagement_dir,
                                 label="Roadmap (single-pass)", max_turns=20,
                                 mode="pipeline", params={**roadmap_params, "phase": "single"})
        cost += result.total_cost_usd if result and result.total_cost_usd else 0
    else:
        # Phase 1
        result = await run_agent("roadmap-prioritization", cwd=engagement_dir, label="Roadmap P1",
                                 mode="pipeline", params={**roadmap_params, "phase": "1"})
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

        # T2 FIX: was express=False, now express=express
        present_checkpoint("roadmap", outputs_dir, express=express, non_interactive=non_interactive)

        # Phase 2
        result = await run_agent("roadmap-prioritization", cwd=engagement_dir, label="Roadmap P2",
                                 mode="pipeline", params={**roadmap_params, "phase": "2"})
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

    assert_file_exists(outputs_dir / "roadmap.md", "Roadmap")
    return {"elapsed": time.time() - start, "cost": cost}


async def step_assembly(
    ws,
    express: bool,
    non_interactive: bool = False,
) -> dict:
    """Run Narrative Assembler.

    S3: In non-interactive mode, uses parallel sharding:
      P1 (plan) -> P2a (Acts 1-3) + P2b (Acts 4-7) parallel -> Python merge -> exec summary

    Interactive mode: preserves existing 3-phase flow with CP2 consultant review.
    """
    engagement_dir = ws.path      # #167: the neutral workspace — see step_parallel_block_a
    outputs_dir = ws.outputs
    start = time.time()
    cost = 0.0

    # narrative-assembler is mode-extracted (skill-first contracts): every
    # assembler prompt here is composed from .claude/agents/narrative-assembler.md
    # (## Modes -> pipeline-report | pipeline-shard) via compose_prompt — no
    # inline f-strings. File lists stay Python-built (existence-filtered) and
    # travel as VALUES-only params; shard identity + act assignment are carried
    # by the shard_id param against the mode's shard table.
    upstream_files = ", ".join(
        str(outputs_dir / f)
        for f in [
            "evidence_register.md", "pain_points.md", "metrics.md",
            "stakeholder_intelligence.md", "capability_assessment.md",
            "roi_report.md", "roadmap.md",
            "journey_maps_summary.md", "market_context_validated.md",
            "benchmarks_validated.md",
        ]
        if (outputs_dir / f).exists()
    )
    report_params = {
        "engagement_dir": engagement_dir,
        "outputs_dir": outputs_dir,
    }

    # Resume guard: if both assembly outputs exist, skip entirely
    if file_exists(outputs_dir / "assessment_report.md") and file_exists(outputs_dir / "executive_summary.md"):
        log("  ⚡ Both assembly outputs exist — skipping assembly", C.YELLOW)
        return {"elapsed": 0, "cost": 0}

    if non_interactive:
        # ── S3: PARALLEL ASSEMBLY SHARDING (non-interactive) ─────────────

        # Phase 1: Quick structure plan (V5: capped to concise briefing)
        result = await run_agent("narrative-assembler", cwd=engagement_dir,
                                 label="Assembly P1 (plan)", max_turns=15,
                                 mode="pipeline-report",
                                 params={**report_params, "phase": "plan",
                                         "upstream_files": upstream_files})
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

        present_checkpoint("assembly_CP1", outputs_dir, express=express, non_interactive=non_interactive)

        # Phase 2: V5 3-way parallel shard writing (balanced workload).
        # Shard sources (existence-filtered here; the mode's shard table
        # assigns the acts): A = Acts 1-2 (Strategic Narrative),
        # B = Acts 3-5 (Lighthouse + Journey + Capability),
        # C = Acts 6-7 + Appendix (Roadmap + ROI).
        shard_source_names = {
            "A": ["evidence_register.md", "pain_points.md", "metrics.md",
                  "stakeholder_intelligence.md", "market_context_validated.md"],
            "B": ["evidence_register.md", "pain_points.md",
                  "capability_assessment.md", "journey_maps_summary.md",
                  "market_context_validated.md", "benchmarks_validated.md"],
            "C": ["roadmap.md", "roi_report.md", "roi_config.json",
                  "capability_assessment.md", "benchmarks_validated.md",
                  "evidence_register.md"],
        }
        shard_labels = {
            "A": "Assembly P2A (Acts 1-2)",
            "B": "Assembly P2B (Acts 3-5)",
            "C": "Assembly P2C (Acts 6-7)",
        }

        results = await asyncio.gather(
            *[
                run_agent("narrative-assembler", cwd=engagement_dir,
                          label=shard_labels[sid], max_turns=25,
                          mode="pipeline-shard",
                          params={"engagement_dir": engagement_dir,
                                  "outputs_dir": outputs_dir,
                                  "shard_id": sid,
                                  "source_files": ", ".join(
                                      str(outputs_dir / f) for f in names
                                      if (outputs_dir / f).exists())})
                for sid, names in shard_source_names.items()
            ],
            return_exceptions=True,
        )

        for label, result in zip(["P2A", "P2B", "P2C"], results):
            if isinstance(result, Exception):
                log(f"  ✗ Assembly {label} FAILED: {result}", C.RED)
        cost += _sum_costs(results)

        # Python merge (instant — no LLM needed)
        shard_a_path = outputs_dir / "assembly_shard_A.md"
        shard_b_path = outputs_dir / "assembly_shard_B.md"
        shard_c_path = outputs_dir / "assembly_shard_C.md"

        shard_paths = [shard_a_path, shard_b_path, shard_c_path]
        existing_shards = [p for p in shard_paths if p.exists()]
        if len(existing_shards) == 3:
            parts = [p.read_text(encoding="utf-8") for p in existing_shards]
            merged = parts[0].rstrip() + "\n\n" + parts[1].strip() + "\n\n" + parts[2].lstrip()
            merged_path = outputs_dir / "assessment_report.md"
            merged_path.write_text(merged, encoding="utf-8")
            log(f"  ✓ Merged 3 shards → assessment_report.md ({merged_path.stat().st_size:,} bytes)", C.GREEN)
        else:
            missing = [p.name for p in shard_paths if not p.exists()]
            log(f"  ✗ Cannot merge — missing shards: {', '.join(missing)}", C.RED)

        # Executive summary (quick agent pass — pipeline-report phase exec-summary)
        result = await run_agent("narrative-assembler", cwd=engagement_dir,
                                 label="Executive Summary", max_turns=15,
                                 mode="pipeline-report",
                                 params={**report_params, "phase": "exec-summary",
                                         "upstream_files": "(n/a — exec-summary reads the merged report)"})
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

    else:
        # ── INTERACTIVE: Keep existing 3-phase flow with CP2 review ──────

        # Phase 1: Assembly plan
        result = await run_agent("narrative-assembler", cwd=engagement_dir, label="Assembly P1",
                                 mode="pipeline-report",
                                 params={**report_params, "phase": "1",
                                         "upstream_files": upstream_files})
        cost += result.total_cost_usd if result and result.total_cost_usd else 0
        present_checkpoint("assembly_CP1", outputs_dir, express=express, non_interactive=non_interactive)

        # Phase 2: Draft report
        result = await run_agent("narrative-assembler", cwd=engagement_dir, label="Assembly P2",
                                 mode="pipeline-report",
                                 params={**report_params, "phase": "2",
                                         "upstream_files": upstream_files})
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

        # Assembly CP2 ALWAYS pauses for interactive — this is the final report review
        present_checkpoint("assembly_CP2", outputs_dir, express=False, non_interactive=non_interactive)

        # Phase 3: Finalize
        result = await run_agent("narrative-assembler", cwd=engagement_dir, label="Assembly P3",
                                 mode="pipeline-report",
                                 params={**report_params, "phase": "3",
                                         "upstream_files": "(n/a — phase 3 reads the approved CP2 draft)"})
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

    assert_file_exists(outputs_dir / "assessment_report.md", "Assembly")
    assert_file_exists(outputs_dir / "executive_summary.md", "Assembly")
    return {"elapsed": time.time() - start, "cost": cost}


# The inline design rules (formerly the `_DESIGN_RULES_INLINE` constant, T3)
# and the 6-partial placeholder-by-placeholder spec now live VERBATIM in the
# agent's own contract: .claude/agents/narrative-assembler.md, mode
# "html-partial" (the single literal template token sits in that file's core
# "HTML Template Token Reference" section — composer constraint). The frozen
# standards snapshot / deliverable evals continue to enforce the same rules.


def _prepare_html_source_pack(outputs_dir: Path) -> Path:
    """Concatenate upstream files into ONE source pack for HTML agent. Pure Python — no LLM."""
    pack_path = outputs_dir / "html_source_pack.md"
    sections = [
        ("Executive Summary", "executive_summary.md", 0),        # 10KB — full
        ("Assessment Report", "assessment_report.md", 800),      # 228KB → first 800 lines
        ("Capability Assessment", "capability_assessment.md", 500),  # 85KB → first 500 lines
        ("ROI Report", "roi_report.md", 400),                    # 44KB → first 400 lines
        ("ROI Config JSON", "roi_config.json", 0),               # 51KB — full (scenario data)
        ("Roadmap", "roadmap.md", 400),                          # 80KB → first 400 lines
        ("Journey Maps", "journey_maps_summary.md", 400),        # 46KB → first 400 lines
    ]
    parts = []
    for title, filename, max_lines in sections:
        filepath = outputs_dir / filename
        if not filepath.exists():
            continue
        text = filepath.read_text(encoding="utf-8", errors="replace")
        if max_lines > 0:
            lines = text.splitlines()
            if len(lines) > max_lines:
                text = "\n".join(lines[:max_lines]) + f"\n\n[... truncated at {max_lines} lines ...]"
        parts.append(f"\n{'='*60}\n## SOURCE: {title} ({filename})\n{'='*60}\n\n{text}")
    pack_path.write_text("\n".join(parts), encoding="utf-8")
    log(f"  📦 Source pack: {pack_path.name} ({pack_path.stat().st_size:,} bytes)", C.DIM)
    return pack_path


def _assemble_html_dashboard(template_path: Path, partials_dir: Path, output_path: Path) -> bool:
    """Read template + partials, replace {{PLACEHOLDER}} markers. Pure Python — no LLM."""
    template = template_path.read_text(encoding="utf-8")
    replacements = {}

    for partial_file in sorted(partials_dir.glob("[Pp][Aa][Rr][Tt][Ii][Aa][Ll]_*.html")):
        content = partial_file.read_text(encoding="utf-8")
        # Parse <!-- PLACEHOLDER_NAME --> ... content ... <!-- NEXT --> format
        markers = re.findall(r'<!--\s*([A-Z][A-Z0-9_]+)\s*-->', content)
        for i, marker in enumerate(markers):
            # Content from this marker to next marker or EOF
            if i + 1 < len(markers):
                next_marker = markers[i + 1]
                pattern = (
                    r'<!--\s*' + re.escape(marker) + r'\s*-->\s*\n?'
                    r'(.*?)'
                    r'(?=<!--\s*' + re.escape(next_marker) + r'\s*-->)'
                )
            else:
                pattern = r'<!--\s*' + re.escape(marker) + r'\s*-->\s*\n?(.*)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                value = match.group(1).strip()
                if value:
                    replacements[marker] = value

    replaced = 0
    # Triple-brace first (JS objects): {{{KEY}}} → {value} (preserves outer braces for JS)
    for key, value in replacements.items():
        triple = "{{{" + key + "}}}"
        if triple in template:
            template = template.replace(triple, "{" + value + "}")
            replaced += 1
    # Double-brace: {{KEY}} → value
    for key, value in replacements.items():
        placeholder = "{{" + key + "}}"
        if placeholder in template:
            template = template.replace(placeholder, value)
            replaced += 1

    remaining = re.findall(r'\{\{([A-Z][A-Z0-9_]+)\}\}', template)
    if remaining:
        log(f"  ⚠ {len(remaining)} unfilled placeholders: {', '.join(remaining[:8])}", C.YELLOW)

    output_path.write_text(template, encoding="utf-8")
    size = output_path.stat().st_size
    log(f"  ✓ Assembled: {output_path.name} ({size:,} bytes, {replaced} placeholders filled)", C.GREEN)
    return size > 100_000  # sanity: should be >100KB


async def step_generate_html(ws) -> dict:
    """Generate HTML dashboard. V5: Python pre-pack + assembly, 6 macro-partials."""
    engagement_dir = ws.path      # #167: the neutral workspace — see step_parallel_block_a
    outputs_dir = ws.outputs
    start = time.time()
    cost = 0.0

    if not file_exists(outputs_dir / "assessment_report.md"):
        log("  ⚠ Skipping HTML — assessment_report.md not found", C.YELLOW)
        return {"elapsed": 0, "cost": 0}

    # ── Step 1: Python pre-packs all upstream data into one file ──
    source_pack = _prepare_html_source_pack(outputs_dir)
    partials_dir = outputs_dir / "partials"
    partials_dir.mkdir(exist_ok=True)

    template_path = REPO_ROOT / "templates/presentations/assessment-dashboard-template.html"

    # narrative-assembler is mode-extracted (skill-first contracts): the
    # 6-partial HTML re-invocation is composed from
    # .claude/agents/narrative-assembler.md (## Modes -> html-partial) via
    # compose_prompt — no inline f-string. The design rules + placeholder spec
    # travel inside the mode block verbatim; Python keeps ownership of the
    # source pack (above), the template, assembly, and validation (below).
    html_params = {
        "source_pack": source_pack,
        "partials_dir": partials_dir,
    }

    result = await run_agent(
        "narrative-assembler", cwd=engagement_dir,
        label="HTML Dashboard", max_turns=25,
        mode="html-partial", params=html_params,
    )
    cost += result.total_cost_usd if result and result.total_cost_usd else 0

    # ── Step 3: Python assembles template + partials → final HTML ──
    partials_exist = list(partials_dir.glob("[Pp][Aa][Rr][Tt][Ii][Aa][Ll]_*.html"))
    if partials_exist:
        log(f"  📎 Found {len(partials_exist)} partials, assembling...", C.DIM)
        ok = _assemble_html_dashboard(template_path, partials_dir, outputs_dir / "assessment_dashboard.html")
        if not ok:
            log("  ⚠ Assembly produced undersized file — agent may not have written all partials", C.YELLOW)
    else:
        # Fallback: check if agent wrote the full HTML directly
        log("  ⚠ No partials found — checking for direct HTML output", C.YELLOW)

    html_files = glob_files("*.html", outputs_dir)
    if html_files:
        for h in html_files:
            log(f"  ✓ {h.name} ({h.stat().st_size:,} bytes)", C.GREEN)
    else:
        log("  ✗ No HTML dashboard produced", C.RED)

    return {"elapsed": time.time() - start, "cost": cost}


async def step_generate_excel(ws) -> dict:
    """Generate ROI Excel model. Extracted for S2 overlapping."""
    engagement_dir = ws.path      # #167: the neutral workspace — see step_parallel_block_a
    outputs_dir = ws.outputs
    start = time.time()
    cost = 0.0

    if not file_exists(outputs_dir / "roi_config.json"):
        log("  ⚠ Skipping Excel — roi_config.json not found", C.YELLOW)
        return {"elapsed": 0, "cost": 0}

    # roi-financial-modeler is mode-extracted (skill-first contracts): the
    # Excel re-invocation is composed from .claude/agents/roi-financial-modeler.md
    # (## Modes -> excel-source) via compose_prompt — no inline f-string. The
    # mode reads and follows .claude/commands/generate-roi-excel.md, which
    # re-runs the cap gate (idempotent backstop) before generating.
    excel_params = {
        "engagement_dir": engagement_dir,
        "outputs_dir": outputs_dir,
    }

    result = await run_agent(
        "roi-financial-modeler", cwd=engagement_dir,
        label="ROI Excel", max_turns=30,
        mode="excel-source", params=excel_params,
    )
    cost += result.total_cost_usd if result and result.total_cost_usd else 0

    xlsx_files = glob_files("*.xlsx", outputs_dir)
    if xlsx_files:
        for x in xlsx_files:
            log(f"  ✓ {x.name} ({x.stat().st_size:,} bytes)", C.GREEN)

    return {"elapsed": time.time() - start, "cost": cost}


async def step_validate(engagement_dir: Path, outputs_dir: Path) -> bool:
    """Run the validation gate script (moved to artifact_boundary.validate_outputs)."""
    return validate_outputs(engagement_dir, "assessment")["passed"]


# ─── T4: Pipeline Summary ────────────────────────────────────────────────────

def _print_pipeline_summary(timings: dict, pipeline_start: float):
    """Print timing + cost summary table at pipeline end."""
    total_time = time.time() - pipeline_start
    total_cost = sum(t.get("cost", 0) for t in timings.values())

    print(f"\n{C.BOLD}{C.GREEN}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}  PIPELINE COMPLETE{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'═' * 60}{C.RESET}")
    print(f"\n  {'Stage':<25s} {'Time':>8s}  {'Cost':>8s}")
    print(f"  {'─' * 45}")
    for stage, data in timings.items():
        elapsed = data.get("elapsed", 0)
        cost = data.get("cost", 0)
        print(f"  {stage:<25s} {elapsed/60:>5.1f} min  ${cost:>7.2f}")
    print(f"  {'─' * 45}")
    print(f"  {'TOTAL':<25s} {total_time/60:>5.1f} min  ${total_cost:>7.2f}")

    return total_time, total_cost


# ─── Main Pipeline ────────────────────────────────────────────────────────────

async def run_pipeline(
    engagement_dir: Path,
    express: bool = False,
    non_interactive: bool = False,
    resume_from: Optional[str] = None,
    dry_run: bool = False,
):
    outputs_dir = engagement_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    pipeline_start = time.time()
    timings: dict[str, dict] = {}

    # ── #167: identity first, before anything can print or compose a path ──
    # `client_slug` closes the D14 seam (the map's slug keeps the client's name
    # on the deny-list once #168 makes directories opaque); the same value seeds
    # the log-redaction backstop.
    client_slug = _resolve_client_slug(engagement_dir)
    _install_log_redactions(engagement_dir, client_slug=client_slug)

    # ── Detect domain from intake ─────────────────────────────────────────
    # Host-side only: this reads the RAW intake in Python and yields one of six
    # fixed enum values. Neither the file nor its text ever reaches a prompt.
    intake_file = engagement_dir / "inputs" / "engagement_intake.md"
    domain = "retail"  # default
    if intake_file.exists():
        intake_text = read_file(intake_file)
        # Look for explicit "**Domain:** <value>" field first
        domain_match = re.search(r"\*\*Domain:\*\*\s*(\w+)", intake_text)
        if domain_match and domain_match.group(1).lower() in [
            "retail", "sme", "commercial", "corporate", "wealth", "investing"
        ]:
            domain = domain_match.group(1).lower()
        else:
            # Fallback: scan for domain keywords in the text
            for d in ["investing", "wealth", "commercial", "sme", "retail"]:
                if d.lower() in intake_text.lower():
                    domain = d
                    break

    # ── Pipeline header ───────────────────────────────────────────────────
    print(f"\n{C.BOLD}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}  CORTEX PIPELINE ORCHESTRATOR{C.RESET}")
    print(f"{C.BOLD}{'═' * 60}{C.RESET}")
    # `log_print`, not `print`: this line has always rendered the client-named
    # engagement path, and this process's stdout is read back into a Claude Code
    # session's context whenever the pipeline is launched from one.
    log_print(f"  Engagement: {engagement_dir}")
    print(f"  Domain:     {domain}")
    mode = "EXPRESS" if express else ("NON-INTERACTIVE" if non_interactive else "STANDARD")
    print(f"  Mode:       {mode}")
    if resume_from:
        print(f"  Resuming:   from {resume_from}")
    if dry_run:
        print(f"  DRY RUN:    showing plan only")
    print(f"{'═' * 60}\n")

    if dry_run:
        print("Steps that would execute:")
        if non_interactive:
            print("  1. Discovery (parallel extraction + finalize, max_turns=15)")
            print("  2. Block A: Single-phase (5 agents, 40-min timeout each)")
            print("  3. Roadmap (single-pass) + Excel (overlapping)")
            print("  4. Assembly (P1 plan -> 3-way parallel shards -> merge)")
            print("  5. HTML Dashboard (6 partials + Python assembly, max_turns=25)")
            print("  6. Validation gate")
        else:
            print("  1. Discovery (parallel extraction + finalize)")
            print("  2. Block A: P1 (5 agents) -> checkpoint -> P2 (5 agents)")
            print("  3. Roadmap (2-phase with checkpoint)")
            print("  4. Assembly (3-phase with CP2 review)")
            print("  5. HTML + Excel generation (parallel)")
            print("  6. Validation gate")
        return

    steps = ["discovery", "parallel_a", "roadmap", "assembly", "generate", "validate"]
    if resume_from and resume_from in steps:
        steps = steps[steps.index(resume_from):]

    # ── Step 1: Discovery ─────────────────────────────────────────────────
    # Discovery both anonymises the inputs and materialises the ONE workspace
    # this run uses. Everything after it receives that workspace; `outputs_dir`
    # is rebound to the workspace's own outputs/ and the client-named engagement
    # directory is not named to an agent again.
    if "discovery" in steps:
        log_step("1", "DISCOVERY")
        timings["discovery"], ws = await step_discovery(
            engagement_dir, express, non_interactive, client_slug=client_slug)
    else:
        ws = _restore_workspace(engagement_dir)
    outputs_dir = ws.outputs
    if "discovery" in steps:
        _publish_workspace_outputs(ws)

    # ── Step 2: Parallel Block A ──────────────────────────────────────────
    if "parallel_a" in steps:
        # log_step is called inside step_parallel_block_a based on mode
        timings["parallel_a"] = await step_parallel_block_a(
            ws, express, domain, non_interactive
        )
        _publish_workspace_outputs(ws)

    # ── S2: Overlapping stages (non-interactive) ─────────────────────────
    if non_interactive:
        # In non-interactive mode: Roadmap + Excel start in parallel after Block A,
        # then Assembly starts after Roadmap completes

        if "roadmap" in steps or "assembly" in steps or "generate" in steps:
            log_step("3", "ROADMAP + EXCEL (overlapping)")

            # Start Roadmap and Excel in parallel
            roadmap_and_excel = []
            if "roadmap" in steps:
                roadmap_and_excel.append(("roadmap", step_roadmap(
                    ws, express, non_interactive)))
            if "generate" in steps and file_exists(outputs_dir / "roi_config.json"):
                roadmap_and_excel.append(("excel", step_generate_excel(ws)))

            if roadmap_and_excel:
                tasks = [t[1] for t in roadmap_and_excel]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for (name, _), result in zip(roadmap_and_excel, results):
                    if isinstance(result, Exception):
                        log(f"  ✗ {name} FAILED: {result}", C.RED)
                        timings[name] = {"elapsed": 0, "cost": 0}
                    else:
                        timings[name] = result
                _publish_workspace_outputs(ws)

        # Assembly (needs roadmap.md from above)
        if "assembly" in steps:
            log_step("4", "ASSEMBLY (parallel shards)")
            timings["assembly"] = await step_assembly(ws, express, non_interactive)
            _publish_workspace_outputs(ws)

        # HTML (needs assessment_report.md from assembly)
        if "generate" in steps:
            log_step("5", "HTML DASHBOARD")
            timings["html"] = await step_generate_html(ws)

    else:
        # ── Standard/Interactive flow (sequential) ───────────────────────

        if "roadmap" in steps:
            log_step("3", "ROADMAP")
            timings["roadmap"] = await step_roadmap(ws, express, non_interactive)
            _publish_workspace_outputs(ws)

        if "assembly" in steps:
            log_step("4", "ASSEMBLY")
            timings["assembly"] = await step_assembly(ws, express, non_interactive)
            _publish_workspace_outputs(ws)

        if "generate" in steps:
            log_step("5", "GENERATE HTML + EXCEL (parallel)")
            # Run HTML and Excel in parallel (original behavior)
            gen_tasks = []
            gen_names = []
            if file_exists(outputs_dir / "assessment_report.md"):
                gen_tasks.append(step_generate_html(ws))
                gen_names.append("html")
            if file_exists(outputs_dir / "roi_config.json"):
                gen_tasks.append(step_generate_excel(ws))
                gen_names.append("excel")
            if gen_tasks:
                results = await asyncio.gather(*gen_tasks, return_exceptions=True)
                for name, result in zip(gen_names, results):
                    if isinstance(result, Exception):
                        log(f"  ✗ {name} FAILED: {result}", C.RED)
                        timings[name] = {"elapsed": 0, "cost": 0}
                    else:
                        timings[name] = result

    # ── Step 5b: PUBLISH — workspace outputs -> the real engagement ───────
    # Everything the agents produced lives in the workspace. It has to come home
    # BEFORE the validation gate (which inspects the engagement's own
    # deliverables) and before the de-anonymisation gate (which is the single
    # point where real names re-enter artifacts, and which reads and rewrites
    # the engagement's outputs/, not the workspace's). Delegated to
    # Workspace.copy_back() with its stated atomicity guarantee — staged inside
    # the engagement directory, published by atomic rename. Idempotent, so the
    # per-step calls above are a durability measure, not a duplicate publish.
    _publish_workspace_outputs(ws)

    # ── Step 6: Validation Gate ───────────────────────────────────────────
    # Runs against the REAL engagement — these are the consultant's deliverables.
    real_outputs_dir = engagement_dir / "outputs"
    if "validate" in steps:
        log_step("6", "VALIDATION GATE")
        passed = await step_validate(engagement_dir, real_outputs_dir)
        if not passed:
            log("  Pipeline completed with validation warnings.", C.YELLOW)

    # ── Step 6b: De-anonymize final outputs ─────────────────────────────
    # Moved to artifact_boundary.deanonymize_dir — a missing .pii_mapping.json
    # is reported loudly as NOT client-ready, never silently skipped.
    # The workspace copy is deliberately NOT restored: it stays placeholder-form
    # for as long as it exists, so nothing an agent can still reach ever carries
    # a real client name.
    deanonymize_dir(real_outputs_dir, engagement_dir / ".pii_mapping.json")

    # Clean up anonymized transcript copies (keep mapping for audit trail).
    # `.anon_engagement_intake.md` goes too — it is a scrubbed copy of a
    # deny-list source and has no life beyond this run.
    for pattern in (".anon_transcript_*", ".anon_engagement_intake.md"):
        for anon_file in (engagement_dir / "inputs").glob(pattern):
            anon_file.unlink(missing_ok=True)

    # ── Step 7: Knowledge Harvest (silent, non-blocking) ─────────────────
    log_step("7", "KNOWLEDGE HARVEST")
    # `engagement_dir.name` is the `YYYY-MM_domain_type` slug by convention, one
    # level BELOW the client directory — but conventions are not guarantees, and
    # this value is rendered into the harvester's prompt and into the knowledge
    # filenames it writes. Check it against the deny-list rather than trusting
    # the layout.
    engagement_id = engagement_dir.name
    if _leaked_terms(engagement_id):
        engagement_id = "engagement-" + hashlib.sha256(
            engagement_id.encode("utf-8")).hexdigest()[:8]
        log("  ⚠ engagement id matched a client identifier — using a neutral id "
            "for harvest instead", C.YELLOW)
    await step_harvest(ws, engagement_id)

    # ── T4: Summary with timing + costs ──────────────────────────────────
    total_time, total_cost = _print_pipeline_summary(timings, pipeline_start)

    # The consultant's deliverables now live in the REAL engagement, not the
    # workspace — list those.
    print(f"\n  Output files:")
    for f in sorted(real_outputs_dir.iterdir()):
        if not f.name.startswith("CHECKPOINT") and not f.name.startswith("interim"):
            log_print(f"    {f.name:40s} {f.stat().st_size:>8,} bytes")

    # Write timing to journal
    journal = engagement_dir / "ENGAGEMENT_JOURNAL.md"
    if journal.exists():
        timing_entry = f"""
---

### {datetime.now().strftime('%Y-%m-%d %H:%M')} — Pipeline Orchestrator V4 (Python)

**Mode:** {'Express' if express else ('Non-Interactive' if non_interactive else 'Standard')}
**Total Duration:** {total_time:.0f}s ({total_time/60:.1f} min)
**Total Cost:** ${total_cost:.2f}

| Step | Duration | Cost |
|------|----------|------|
"""
        for step_name, data in timings.items():
            elapsed = data.get("elapsed", 0)
            step_cost = data.get("cost", 0)
            timing_entry += f"| {step_name} | {elapsed:.0f}s ({elapsed/60:.1f} min) | ${step_cost:.2f} |\n"

        with open(journal, "a") as f:
            f.write(timing_entry)

    # Runtime evals (non-blocking): score this run's agent outputs + deliverables +
    # deliverable-structural contracts into .pipeline_run_report.json and flag anything below
    # threshold. Never breaks the engagement — wrapped so any eval error is swallowed.
    try:
        import sys as _sys
        _evals = REPO_ROOT / "evals"
        if str(_evals) not in _sys.path:
            _sys.path.insert(0, str(_evals))
        from runtime import write_report as _write_eval_report, score_engagement as _score
        _rep = _score(engagement_dir)
        _path = _write_eval_report(engagement_dir, _rep)
        print(f"  📊 Eval report → {_path.name}"
              + (f"  ⚑ {len(_rep['flags'])} flag(s)" if _rep.get("flags") else "  ✓ clean"))
    except Exception as _e:  # never let evals break a run
        log_print(f"  (runtime evals skipped: {_e})")

    # ── Tear down the workspace ──────────────────────────────────────────
    # Only here, at the end of a run that reached this line. An earlier
    # exception leaves it standing on purpose (identity.Workspace.__exit__ takes
    # the same position): a failed run's agent output may not have been
    # published yet, and `--resume-from` reattaches to exactly this directory.
    ws.cleanup()
    (engagement_dir / WORKSPACE_POINTER).unlink(missing_ok=True)

    print()


# ─── Knowledge Harvest ────────────────────────────────────────────────────────

def _harvest_outputs_hash(outputs_dir: Path) -> str:
    """Hash key output files to detect changes since last harvest."""
    files = ["roi_config.json", "evidence_register.md", "journey_maps.json",
             "capability_assessment.md", "roi_report.md"]
    h = hashlib.sha256()
    for fname in files:
        f = outputs_dir / fname
        if f.exists():
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _load_env_file(cortex_dir: Path) -> dict:
    """Load .env file from cortex root into a dict (does not override os.environ)."""
    env = {}
    env_path = cortex_dir / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def _git_push_harvest(branch: str, token: str, cortex_dir: Path, engagement_id: str) -> bool:
    """Commit knowledge/ changes and push harvest branch using the harvest token."""
    github_owner = os.environ.get("CORTEX_GITHUB_OWNER", "mayur294-lgtm")
    github_repo = os.environ.get("CORTEX_GITHUB_REPO", "value-consulting-agents")
    remote_url = f"https://github.com/{github_owner}/{github_repo}.git"

    # Use GIT_ASKPASS to supply the token without embedding it in the URL or process args
    askpass_script = cortex_dir / ".git_askpass.sh"
    askpass_script.write_text("#!/bin/sh\necho \"$GIT_HARVEST_TOKEN\"\n")
    askpass_script.chmod(0o700)

    env = {**os.environ,
           "GIT_AUTHOR_NAME": "Cortex Harvester",
           "GIT_AUTHOR_EMAIL": "harvest@cortex.ai",
           "GIT_COMMITTER_NAME": "Cortex Harvester",
           "GIT_COMMITTER_EMAIL": "harvest@cortex.ai",
           "GIT_ASKPASS": str(askpass_script),
           "GIT_HARVEST_TOKEN": token,
           "GIT_TERMINAL_PROMPT": "0"}

    def run(cmd):
        return subprocess.run(cmd, cwd=cortex_dir, capture_output=True, text=True, env=env)

    try:
        # Create and switch to harvest branch from current main
        run(["git", "fetch", "origin", "main", "--quiet"])
        run(["git", "checkout", "-B", branch, "origin/main"])

        # Stage only knowledge/ and EXTRACTION_REGISTRY.md
        run(["git", "add", "knowledge/"])

        status = run(["git", "status", "--porcelain"])
        if not status.stdout.strip():
            return False  # Nothing to commit

        msg = f"harvest: {engagement_id} → knowledge (auto)"
        result = run(["git", "commit", "-m", msg])
        if result.returncode != 0:
            return False

        push = run(["git", "push", remote_url, f"{branch}:{branch}", "--quiet"])
        return push.returncode == 0
    finally:
        # Clean up the askpass script so the token helper doesn't linger on disk
        askpass_script.unlink(missing_ok=True)


def _open_harvest_pr(branch: str, token: str, engagement_id: str, summary: str) -> str:
    """Open a GitHub PR for the harvest branch. Returns PR URL."""
    github_owner = os.environ.get("CORTEX_GITHUB_OWNER", "mayur294-lgtm")
    github_repo = os.environ.get("CORTEX_GITHUB_REPO", "value-consulting-agents")

    payload = json.dumps({
        "title": f"harvest: {engagement_id} knowledge update",
        "head": branch,
        "base": "main",
        "body": (
            f"## Auto-harvest: `{engagement_id}`\n\n"
            f"{summary}\n\n"
            "_Generated automatically by Cortex pipeline. Review and merge to update shared knowledge base._\n\n"
            "🤖 Auto-opened by `orchestrate.py`"
        ),
    }).encode()

    req = urllib.request.Request(
        f"https://api.github.com/repos/{github_owner}/{github_repo}/pulls",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("html_url", "")
    except Exception:
        return ""


async def step_harvest(ws, engagement_id: str):
    """
    Post-pipeline knowledge harvest — runs silently after validation.
    - Always extracts knowledge locally (no setup required)
    - Optionally pushes harvest/* branch + opens PR if CORTEX_HARVEST_TOKEN is set
    - Skips if outputs haven't changed since last harvest

    #167: the harvester is an agent like any other, so its `cwd` and its path
    params are the neutral workspace. It therefore reads the PLACEHOLDER-form
    outputs (`<CLIENT_1>`, `<PERSON_2>`) rather than the de-anonymised
    deliverables — which is the form the harvester's own contract requires it to
    write into shared knowledge anyway, so this tightens the guarantee instead of
    relying on the agent to re-anonymise. Host-side state
    (`.harvest_state`, the synthetic-quarantine policy) stays anchored on the
    REAL engagement directory, which is where it has always lived.
    """
    engagement_dir = ws.engagement_dir   # REAL — host-side state only
    workspace_dir = ws.path              # what the agent is told
    outputs_dir = ws.outputs
    cortex_dir = REPO_ROOT

    # Synthetic-engagement gate — single source of truth (artifact_boundary.
    # synthetic_policy). "real" falls through unchanged; "quarantine" routes
    # the harvester into its own quarantine mode and suppresses auto-push;
    # "never" skips harvest entirely (real source material must not be
    # extracted).
    policy, reason = synthetic_policy(engagement_dir)
    if policy == "never":
        log("  🧪 Synthetic engagement (harvest_policy: never) — harvest skipped entirely (real source material, must not be extracted)", C.YELLOW)
        log(f"  {reason}", C.DIM)
        return
    if policy == "quarantine":
        log("  🧪 Synthetic engagement (harvest_policy: quarantine) — harvest redirected to outputs/knowledge_harvest/; shared knowledge untouched", C.CYAN)
        log(f"  {reason}", C.DIM)

    # Check if outputs changed since last harvest
    hash_file = engagement_dir / ".harvest_state"
    current_hash = _harvest_outputs_hash(outputs_dir)
    if hash_file.exists() and hash_file.read_text().strip() == current_hash:
        log("  ✓ Knowledge up to date — no changes since last harvest", C.GREEN)
        return

    log("  🧠 Harvesting knowledge from engagement outputs...", C.CYAN)

    # knowledge-harvester is mode-extracted (skill-first contracts): its
    # prompt is composed from .claude/agents/knowledge-harvester.md
    # (## Modes -> pipeline | quarantine) via compose_prompt — no inline f-string.
    harvest_params = {
        "engagement_dir": workspace_dir,
        "outputs_dir": outputs_dir,
        "engagement_id": engagement_id,
    }

    result = await run_agent(
        "knowledge-harvester", cwd=workspace_dir,
        label="Harvest", max_turns=25,
        mode=("quarantine" if policy == "quarantine" else "pipeline"), params=harvest_params,
    )

    # Read summary written by agent — into the workspace, per the params above.
    summary_file = workspace_dir / ".harvest_summary.txt"
    summary = summary_file.read_text().strip() if summary_file.exists() else "Knowledge updated."

    # Save hash so next run skips if nothing changes (dedup applies to
    # repeated quarantine runs too, so re-running a test engagement doesn't
    # re-harvest every time).
    hash_file.write_text(current_hash)

    if policy == "quarantine":
        log("  ✓ Quarantined harvest complete — shared knowledge untouched, auto-push skipped", C.DIM)
        return

    # Auto-push if harvest token is available (optional — knowledge is already saved locally)
    env_vars = _load_env_file(cortex_dir)
    token = os.environ.get("CORTEX_HARVEST_TOKEN") or env_vars.get("CORTEX_HARVEST_TOKEN")

    if not token:
        log("  ✓ Knowledge extracted locally. Will be included in your next git push.", C.GREEN)
        log("  ℹ️  Optional: set up auto-push with ./scripts/setup-harvest.sh <token>", C.DIM)
        return

    # Push harvest branch and open PR
    branch = f"harvest/{engagement_id}-{datetime.now().strftime('%Y%m%d')}"
    log(f"  📤 Pushing harvest branch: {branch}", C.CYAN)

    pushed = _git_push_harvest(branch, token, cortex_dir, engagement_id)
    if not pushed:
        log("  ⚠  Nothing new to push (knowledge already up to date)", C.YELLOW)
        return

    pr_url = _open_harvest_pr(branch, token, engagement_id, summary)

    if pr_url:
        log(f"  ✅ Harvest PR opened: {pr_url}", C.GREEN)
    else:
        log(f"  ✅ Harvest branch pushed: {branch} (PR creation failed — open manually)", C.YELLOW)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cortex Pipeline Orchestrator V4 — optimized agent workflow engine"
    )
    parser.add_argument("engagement_dir", type=Path, help="Path to engagement directory")
    parser.add_argument("--express", action="store_true",
                        help="Auto-approve intermediate checkpoints (keeps Discovery + Assembly CP2)")
    parser.add_argument("--resume-from", choices=[
        "discovery", "parallel_a", "roadmap", "assembly", "generate", "validate"
    ], help="Resume from a specific pipeline step")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show pipeline plan without executing")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Auto-approve ALL checkpoints with summaries (for Claude Code /run-pipeline)")
    args = parser.parse_args()

    engagement_dir = args.engagement_dir.resolve()
    if not engagement_dir.exists():
        print(f"Error: {engagement_dir} does not exist", file=sys.stderr)
        sys.exit(1)
    if not (engagement_dir / "inputs").exists():
        print(f"Error: {engagement_dir}/inputs/ does not exist", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_pipeline(
        engagement_dir,
        express=args.express,
        non_interactive=args.non_interactive,
        resume_from=args.resume_from,
        dry_run=args.dry_run,
    ))


if __name__ == "__main__":
    main()
