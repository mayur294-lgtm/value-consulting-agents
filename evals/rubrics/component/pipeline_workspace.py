"""pipeline-workspace component evaluator — the executable form of #167's
guarantee (ticket #198, backlog :134).

THE GUARANTEE, AND WHY NOTHING WAS RE-RUNNING IT
------------------------------------------------
#167's claim is absolute: **no composed prompt and no `cwd` names the client.**
`compose_prompt` renders `engagement_dir` / `outputs_dir` / `transcript_path`
into the Runtime Parameters table of every agent invocation as VALUES, and
`run_agent` sets `cwd` to the same directory — so perfect CONTENT anonymisation
was defeated by the path envelope on every single call
(.design/solution-design-v6.md D6). The fix repointed every step at
`pii.identity.materialise_workspace()`'s neutral workspace and added
`_assert_neutral_invocation` as the choke point every invocation passes.

That claim was verified ONCE, by a throwaway harness that stubbed
`_resilient_query` and walked every call site. Nothing in `evals/` re-ran it.
The structural altitude scores fixtures and cannot see a regression here at
all: re-binding one step's `engagement_dir = ws.path` back to
`ws.engagement_dir` would leak the client's directory name into that agent's
prompt and cwd on every run, and every existing row would stay green. This
module is that harness, made permanent.

WHAT IT ACTUALLY RUNS
---------------------
A real traversal of `scripts/orchestrate.py`'s pipeline steps against a
SYNTHETIC engagement in a tempdir, with `_resilient_query` stubbed so nothing
leaves the machine. Three traversals, because no single one reaches every call
site:

  ni_multi      non-interactive, 3 transcripts  — single-phase Block A, the
                sharded assembly, the multi-transcript discovery branch
  interactive   interactive, 3 transcripts      — the P1 -> checkpoint -> P2
                Block A, two-phase roadmap, three-phase assembly
  ni_single     non-interactive, 1 transcript   — the `len(transcripts) == 1`
                discovery branch, which the other two never execute

Together they execute EVERY `run_agent(` call site in `orchestrate.py`, and
`traversal_covers_every_agent_call_site` proves that by comparing the line
numbers actually called (captured through a `contextvars` slot set at
coroutine-creation time) against an AST enumeration of the file. A call site
added later without eval coverage turns that check red; so does a branch that
stops being reachable.

THE FIXTURE IS DELIBERATELY PRE-MIGRATION AND CLIENT-NAMED
-----------------------------------------------------------
`engagements/zzzplaceholderclient/2026-01_test_engagement/` — the shape #167
has to neutralise. A fixture that arrived already opaque could not tell a
working neutraliser from a broken one (the same reasoning
`pii_anonymizer._workspace_paths_contain_no_client_identifiers` used for #166).
Nothing here ever touches the real `engagements/` tree.

THE DENY-LIST COMES FIRST, STRUCTURALLY
----------------------------------------
"An empty deny-list makes every other assertion pass vacuously; this is how the
repo twice shipped a gate scoring 1.000 while certifying nothing."
`denylist_nonempty_asserted_first` is not merely the first check in the list —
`evaluate()` cannot proceed without its return value. The traversal subprocess
is handed the resolved terms, and if the vacuity guard raises, the subprocess is
never launched and every other check reports as NOT EVALUATED, hard-failed,
naming this one as the reason. There is no ordering someone can accidentally
reverse.

Two more non-vacuity guards sit under that one:
  * `build_fixture_engagement` refuses a fixture whose declared client identity
    appears nowhere in the tree it wrote (the failure one step earlier).
  * the traversal child runs the term scanner against a control string that
    DOES contain the client name and reports the result; a scanner that found
    nothing there would make "no hits anywhere" meaningless, so
    `no_client_identifier_in_composed_prompt` fails on it.

WHICH INTERPRETER
-----------------
`orchestrate.py` imports `claude_agent_sdk` at module level and `step_discovery`
runs the real Presidio anonymiser, so the traversal needs the Presidio/SDK
interpreter — `.venv/bin/python` locally (CLAUDE.md "Commands"), whatever CI's
`actions/setup-python` + `requirements.txt` produced there. It runs in a
SUBPROCESS rather than in-process, for two reasons: this rubric itself stays
runnable under plain `python3`, and the traversal monkeypatches orchestrate
module globals, which must not survive into any other row's evaluation. The
interpreter is resolved, never assumed, and an unresolvable one is a loud RED
check naming `bash scripts/setup_pii.sh` — never a skip.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from rubrics._harness import (
    assert_deny_list_non_empty,
    build_fixture_engagement,
    FixtureEngagement,
)
from rubrics.base import CheckResult, repo_root

# House rule (see _harness.DEFAULT_CLIENT_*): fixtures use obviously-placeholder
# `zzz`-prefixed non-words, never a fictional bank name — those get mistaken for
# real engagements and cited back. These tokens also appear NOWHERE in
# `.claude/agents/**`, so a hit in a composed prompt can only have come from the
# fixture's own paths, never from the agent contract the prompt is built out of.
CLIENT_NAME = "Zzzplaceholder Meridian Holdings"
CLIENT_SHORT = "Meridian"
CLIENT_SLUG = "zzzplaceholderclient"
STAKEHOLDER = "Zzztestperson Vandermolen"
ENGAGEMENT_SLUG = "2026-01_test_engagement"

TRAVERSAL_TIMEOUT_S = 600.0

# Floor on the number of agent invocations the three traversals must produce.
# Not a pinned equality — the exact count moves with the pipeline's shape — but
# a traversal that recorded (say) four invocations has not walked the pipeline,
# and every "no client identifier anywhere" assertion built on it would be
# nearly vacuous. Measured at 58 (19 + 22 + 17) when this row was authored.
MIN_TRAVERSAL_RECORDS = 40


class TraversalError(RuntimeError):
    """The traversal subprocess could not be run or did not produce records."""


def _transcript(days: int) -> str:
    return (
        "# Discovery call\n\n"
        f"Attendees: {STAKEHOLDER} (CFO, {CLIENT_NAME}), Backbase consultant.\n\n"
        f"{STAKEHOLDER}: Onboarding at {CLIENT_SHORT} takes {days} days end to end. "
        "Reach me at zzztest.person@zzzplaceholderbank.example or +1 555 0100.\n\n"
        "Consultant: Understood. What does that cost to serve?\n\n"
        f"{STAKEHOLDER}: Roughly 40% of the branch's time.\n"
    )


_INTAKE = (
    "# Engagement Intake\n\n"
    f"- **Client:** {CLIENT_NAME}\n"
    "- **Domain:** retail\n"
    f"- **Primary contact:** {STAKEHOLDER}\n"
)


def _fixture(root: Path, name: str, n_transcripts: int) -> FixtureEngagement:
    """One synthetic engagement in the PRE-MIGRATION, client-named shape.

    Each traversal gets its OWN tree: the pipeline writes real outputs into the
    engagement (and the assembly step short-circuits when
    `assessment_report.md` already exists), so sharing one fixture across the
    three runs would silently skip whole steps.
    """
    documents = {"inputs/engagement_intake.md": _INTAKE}
    for i in range(1, n_transcripts + 1):
        documents[f"inputs/transcript_{i}.md"] = _transcript(10 + i)
    return build_fixture_engagement(
        root / name,
        slug=CLIENT_SLUG,
        client_name=CLIENT_NAME,
        short_name=CLIENT_SHORT,
        stakeholder=STAKEHOLDER,
        engagement=ENGAGEMENT_SLUG,
        documents=documents,
        subdirs=("outputs",),
    )


# ---------------------------------------------------------------------------
# The traversal child
# ---------------------------------------------------------------------------
#
# Written to the tempdir and executed by the resolved pipeline interpreter. It
# lives here as source rather than as a committed script because this ticket
# owns exactly two files, and because it is not something anyone should run by
# hand: it monkeypatches orchestrate module globals and is only meaningful
# inside one evaluation.
#
# WHAT IT PATCHES, AND WHY EACH ONE
#   run_agent               a thin SYNC wrapper that captures the caller's line
#                           number at coroutine-CREATION time and re-publishes it
#                           into a contextvar inside the coroutine. Capturing it
#                           from inside `run_agent` itself is impossible: every
#                           Block A call site creates its coroutine inside an
#                           `asyncio.gather`, so by the time the body runs its
#                           caller frame is asyncio's, not orchestrate's.
#   _assert_neutral_invocation
#                           the PRIMARY recorder. It sits at the choke point
#                           every invocation passes, sees the exact `cwd` and
#                           composed prompt run_agent is about to send, and —
#                           critically — still sees them when the real assertion
#                           REFUSES. The refusal is recorded and swallowed so the
#                           traversal keeps walking; the production behaviour it
#                           models (fail closed) is exercised separately and
#                           directly by the `neutral_invocation_assertion_...`
#                           probes below.
#   _resilient_query        stubbed to an async generator that yields NOTHING
#                           (so `run_agent` sets result=None and every caller's
#                           `result.total_cost_usd if result else 0` holds), and
#                           writes the output files the next step asserts on.
#                           Keyed on the invocation LABEL, which is the only
#                           thing that distinguishes narrative-assembler's plan /
#                           shard / exec-summary calls from each other.
#   builtins.input          interactive checkpoints call `input()`. Running the
#                           interactive traversal with `express=True` instead
#                           would dodge the two-phase roadmap branch entirely.
#   _load_env_file          returns {} so `step_harvest` can never pick up a real
#                           CORTEX_HARVEST_TOKEN out of the checkout's .env and
#                           push a harvest branch during an eval run.
_DRIVER_SRC = r'''
"""Traversal child for rubrics/component/pipeline_workspace.py. Not a
standalone tool: it monkeypatches scripts/orchestrate.py module globals."""
import asyncio
import builtins
import contextvars
import hashlib
import inspect
import json
import sys
import traceback
from pathlib import Path

RECORDS = []
STATE = {"run": "?", "mode": "?", "step": "?"}
TERMS = []
CALL_LINE = contextvars.ContextVar("cortex_eval_call_line", default=None)


def hits(text):
    low = str(text).lower()
    return sorted({t for t in TERMS if t and t.lower() in low})


def _body(name):
    return "# " + name + "\n\n" + ("synthetic traversal fixture content. " * 14) + "\n"


ROI_CONFIG = {
    "industry": "retail banking",
    "bank_profile": {"total_revenue": 1000000000},
    "total_investment": 5000000,
    "value_lever_groups": {"g1": {"revenue_drivers": {"d1": {
        "baseline_annual": 1000000,
        "inputs": {"backbase_impact": {"value": 0.2}}}}}},
    "scenarios": {"base": {"backbase_impacts": {"d1": 0.2}}},
    "investment": {"license": {"year_1": 1000000}},
}


def w(outputs, name, text=None):
    outputs.mkdir(parents=True, exist_ok=True)
    (outputs / name).write_text(text if text is not None else _body(name), encoding="utf-8")


def produce(label, cwd):
    """Write what the NEXT step asserts on, keyed by the invocation label."""
    o = Path(cwd) / "outputs"
    lab = label.lower()
    if lab.startswith("discovery"):
        for i in range(1, 6):
            w(o, "interim_transcript_%d.md" % i)
        for n in ("evidence_register.md", "pain_points.md", "metrics.md",
                  "stakeholder_intelligence.md"):
            w(o, n)
        w(o, "CHECKPOINT_discovery.md")
    elif lab.startswith("journey"):
        w(o, "journey_maps.json", json.dumps({"journeys": []}) + "\n" + "#" * 220)
        w(o, "journey_maps_summary.md")
        w(o, "CHECKPOINT_journey-builder.md")
    elif lab.startswith("market"):
        w(o, "market_context_validated.md")
        w(o, "CHECKPOINT_market-context.md")
    elif lab.startswith("capability"):
        w(o, "capability_assessment.md")
        w(o, "CHECKPOINT_capability.md")
    elif lab.startswith("roi hypothesis"):
        w(o, "lever_candidates.md")
        w(o, "CHECKPOINT_roi_levers.md")
    elif lab.startswith("benchmark"):
        w(o, "benchmarks_validated.md")
        w(o, "CHECKPOINT_benchmark.md")
    elif lab.startswith("roi financial") or lab.startswith("roi excel"):
        w(o, "roi_report.md")
        w(o, "roi_config.json", json.dumps(ROI_CONFIG, indent=2))
    elif lab.startswith("roadmap"):
        w(o, "roadmap.md")
        w(o, "CHECKPOINT_roadmap.md")
    elif "p2a" in lab:
        w(o, "assembly_shard_A.md")
    elif "p2b" in lab:
        w(o, "assembly_shard_B.md")
    elif "p2c" in lab:
        w(o, "assembly_shard_C.md")
    elif lab.startswith("executive summary"):
        w(o, "executive_summary.md")
    elif lab.startswith("assembly p1"):
        w(o, "CHECKPOINT_assembly_CP1.md")
    elif lab.startswith("assembly p2"):
        w(o, "assessment_report.md")
        w(o, "CHECKPOINT_assembly_CP2.md")
    elif lab.startswith("assembly p3"):
        w(o, "assessment_report.md")
        w(o, "executive_summary.md")
    elif lab.startswith("harvest"):
        (Path(cwd) / ".harvest_summary.txt").write_text("done\n", encoding="utf-8")


def install(O):
    original_assert = O._assert_neutral_invocation
    real_run_agent = O.run_agent

    def run_agent_wrapper(*args, **kwargs):
        line = inspect.currentframe().f_back.f_lineno

        async def go():
            CALL_LINE.set(line)
            return await real_run_agent(*args, **kwargs)
        return go()

    O.run_agent = run_agent_wrapper

    def recording_assert(agent_name, cwd, system_prompt):
        rec = {
            "run": STATE["run"], "mode": STATE["mode"], "step": STATE["step"],
            "agent": agent_name, "call_line": CALL_LINE.get(),
            "cwd": str(cwd), "prompt_len": len(system_prompt),
            "prompt_sha256": hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()[:16],
            "cwd_hits": hits(cwd), "prompt_hits": hits(system_prompt),
            "engagement_path_in_prompt": STATE["engagement"] in system_prompt,
            "engagement_path_in_cwd": STATE["engagement"] in str(cwd),
            "refused_on": None, "refusal": None, "label": None,
        }
        try:
            original_assert(agent_name, cwd, system_prompt)
        except O.ClientIdentifierLeak as exc:
            msg = str(exc)
            rec["refused_on"] = "cwd" if "its cwd" in msg else "composed prompt"
            rec["refusal"] = msg[:240]
        RECORDS.append(rec)

    O._assert_neutral_invocation = recording_assert

    async def stub_query(prompt, options, label):
        RECORDS[-1]["label"] = label
        produce(label, options.cwd)
        return
        yield  # noqa - unreachable; makes this an async generator

    O._resilient_query = stub_query
    O._load_env_file = lambda *a, **k: {}
    builtins.input = lambda *a, **k: ""


async def traverse(O, engagement_dir, slug, non_interactive):
    O._install_log_redactions(engagement_dir, client_slug=slug)
    express = False
    STATE["step"] = "discovery"
    _, ws = await O.step_discovery(engagement_dir, express, non_interactive, client_slug=slug)
    STATE["step"] = "parallel_a"
    await O.step_parallel_block_a(ws, express, "retail", non_interactive)
    STATE["step"] = "roadmap"
    await O.step_roadmap(ws, express, non_interactive)
    STATE["step"] = "assembly"
    await O.step_assembly(ws, express, non_interactive)
    STATE["step"] = "generate_excel"
    await O.step_generate_excel(ws)
    STATE["step"] = "generate_html"
    await O.step_generate_html(ws)
    STATE["step"] = "harvest"
    await O.step_harvest(ws, "engagement-traversal")
    return ws


def probes(O, original_assert, engagement_dir, workspace, client_name, stakeholder):
    """Exercise the PRODUCTION assertion and the log-redaction backstop directly.

    The traversal above swallows refusals so it can keep walking; these probes
    are where `_assert_neutral_invocation`'s fail-closed behaviour is actually
    asserted, including the negative control (a neutral invocation must be
    ALLOWED — an assertion hardwired to raise is not a gate).
    """
    out = {}

    def raises(cwd, prompt):
        try:
            original_assert("zzzprobe-agent", cwd, prompt)
        except O.ClientIdentifierLeak as exc:
            return str(exc)[:240]
        except Exception as exc:
            return "UNEXPECTED %s: %s" % (type(exc).__name__, exc)
        return None

    neutral_prompt = "## Runtime Parameters\n\n| engagement_dir | %s |\n" % workspace
    leaky_prompt = "## Runtime Parameters\n\n| note | prepared for %s (%s) |\n" % (
        client_name, stakeholder)
    out["client_named_cwd_refused"] = raises(engagement_dir, neutral_prompt)
    out["client_named_prompt_refused"] = raises(workspace, leaky_prompt)
    out["neutral_invocation_allowed"] = raises(workspace, neutral_prompt)

    out["redacted_engagement_path"] = O._redact(str(engagement_dir))
    out["redacted_client_sentence"] = O._redact(
        "Engagement for %s, sponsor %s" % (client_name, stakeholder))
    out["redacted_workspace_path"] = O._redact(str(workspace))
    out["workspace_path"] = str(workspace)
    return out


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    global TERMS
    TERMS = spec["terms"]
    if not TERMS:
        raise SystemExit("traversal refused: the deny-list handed to this child is EMPTY — "
                         "every hit assertion built on it would be vacuous")
    repo = Path(spec["repo"])
    sys.path.insert(0, str(repo / "scripts"))
    import orchestrate as O

    original_assert = O._assert_neutral_invocation
    install(O)

    result = {
        "ok": True,
        "records": RECORDS,
        "workspaces": {},
        "resume": {},
        "probes": {},
        "repo_root": str(O.REPO_ROOT),
        "workspace_root": str(O.WORKSPACE_ROOT),
        # Positive control on the scanner itself: a term scan that cannot find
        # the client name in a string that plainly contains it would make every
        # "no hits" assertion in this row meaningless.
        "scanner_selftest": hits("control line naming %s and %s" % (
            spec["client_name"], spec["stakeholder"])),
    }
    for t in spec["traversals"]:
        STATE["run"] = t["id"]
        STATE["mode"] = t["mode"]
        STATE["engagement"] = t["engagement"]
        eng = Path(t["engagement"])
        ws = asyncio.run(traverse(O, eng, t["slug"], t["mode"] == "non-interactive"))
        result["workspaces"][t["id"]] = str(ws.path)
        result["probes"][t["id"]] = probes(O, original_assert, eng, ws.path,
                                           spec["client_name"], spec["stakeholder"])
        # D15: `--resume-from` REATTACHES to the workspace the run used; it must
        # not re-materialise a second one. Probed before cleanup, for obvious
        # reasons.
        try:
            result["resume"][t["id"]] = str(O._restore_workspace(eng).path)
        except Exception as exc:
            result["resume"][t["id"]] = "ERROR %s: %s" % (type(exc).__name__, exc)
        try:
            ws.cleanup()
        except Exception:
            pass

    Path(spec["out"]).write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
'''


def _pipeline_interpreter() -> tuple[str, str]:
    """The interpreter that can actually RUN the pipeline, resolved not assumed.

    `scripts/orchestrate.py` imports `claude_agent_sdk` at module level and
    `step_discovery` runs the Presidio anonymiser, so bare `python3` (3.9.6 on
    most consultant machines) cannot execute the traversal at all. CLAUDE.md's
    "Commands" section names the one interpreter that can: the `.venv` created
    by `bash scripts/setup_pii.sh`. In CI there is no `.venv` — `requirements.txt`
    is installed under `actions/setup-python`'s 3.11 — so `sys.executable` is
    the fallback, probed rather than trusted.

    Returns (interpreter, note). Raises TraversalError naming the fix if
    neither candidate can import the SDK: a row that cannot prove which
    interpreter it exercised must fail loudly, never skip.
    """
    candidates = [(str(repo_root() / ".venv" / "bin" / "python"), ".venv (scripts/setup_pii.sh)"),
                  (sys.executable, "the eval runner's own sys.executable")]
    tried = []
    for interpreter, note in candidates:
        if not Path(interpreter).exists():
            tried.append(f"{interpreter} ({note}): not present")
            continue
        probe = subprocess.run(
            [interpreter, "-c", "import claude_agent_sdk, presidio_analyzer"],
            capture_output=True, timeout=180)
        if probe.returncode == 0:
            return interpreter, note
        tail = probe.stderr.decode("utf-8", errors="replace").strip().splitlines()
        tried.append(f"{interpreter} ({note}): {tail[-1] if tail else 'import failed'}")
    raise TraversalError(
        "no interpreter available that can import claude_agent_sdk + presidio_analyzer, "
        "which scripts/orchestrate.py needs at module level and in step_discovery. "
        "Tried: " + "; ".join(tried) + ". Fix: `bash scripts/setup_pii.sh` (creates the "
        ".venv CLAUDE.md's Commands section documents as the interpreter that runs the "
        "pipeline), then re-run this row."
    )


def _run_traversal(tmp: Path, fixtures: list[tuple[str, str, FixtureEngagement]],
                   terms: list) -> dict:
    """Launch the traversal child once, for all three runs, and return its JSON."""
    interpreter, note = _pipeline_interpreter()
    driver = tmp / "traversal_driver.py"
    driver.write_text(_DRIVER_SRC, encoding="utf-8")
    out = tmp / "traversal.json"
    spec = {
        "repo": str(repo_root()),
        "terms": list(terms),
        "out": str(out),
        "client_name": CLIENT_NAME,
        "stakeholder": STAKEHOLDER,
        "traversals": [
            {"id": tid, "mode": mode, "engagement": str(fx.engagement_dir),
             "slug": fx.client_dir.name}
            for tid, mode, fx in fixtures
        ],
    }
    spec_path = tmp / "traversal_spec.json"
    spec_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")

    env = dict(os.environ)
    # Never let an eval run push a harvest branch: step_harvest reads this and
    # the driver additionally stubs `_load_env_file` to {}.
    env.pop("CORTEX_HARVEST_TOKEN", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run([interpreter, str(driver), str(spec_path)],
                          capture_output=True, timeout=TRAVERSAL_TIMEOUT_S, env=env)
    if proc.returncode != 0 or not out.is_file():
        stderr = proc.stderr.decode("utf-8", errors="replace")[-1200:]
        raise TraversalError(
            f"traversal child (rc={proc.returncode}, interpreter={interpreter} [{note}]) "
            f"produced no records. stderr tail: {stderr!r}")
    data = json.loads(out.read_text(encoding="utf-8"))
    data["interpreter"] = interpreter
    data["interpreter_note"] = note
    return data


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _check_denylist_nonempty_asserted_first(fixture: FixtureEngagement) -> tuple[CheckResult, list]:
    """The vacuity guard, asserted BEFORE anything else can run.

    Three assertions, and the third one is the reason the other checks in this
    row exist at all:

      1. `_harness.assert_deny_list_non_empty` genuinely REJECTS an empty list
         and a list missing a required identity. Proving the guard bites is not
         ceremony: it is the only thing standing between this row and the
         1.000-while-certifying-nothing failure this repo has shipped twice.
      2. The deny-list PRODUCTION resolves for the fixture — through
         `pii.denylist.resolve_engagement_deny_list`, the same function
         `orchestrate.py` and `anonymize_transcript.py` call, never a literal
         list — is non-empty and carries the client's full name, short name,
         the client directory slug, and the stakeholder mined from the seeded
         documents. Obtained via `FixtureEngagement.resolved_deny_terms()`,
         which runs the guard INTERNALLY, so no caller can hold terms the
         guard never saw.
      3. Its return value is what `evaluate()` feeds the traversal. If this
         raises, the traversal is never launched and every other check on the
         row reports NOT EVALUATED — the ordering is structural, not a
         convention someone can reorder.
    """
    name = "denylist_nonempty_asserted_first"
    problems: list[str] = []

    try:
        assert_deny_list_non_empty([])
        problems.append("assert_deny_list_non_empty([]) did NOT raise — the vacuity guard is "
                        "inert, so every other assertion in this row would pass vacuously")
    except AssertionError:
        pass
    try:
        assert_deny_list_non_empty(["zzzunrelated"], must_contain=[CLIENT_NAME])
        problems.append(f"assert_deny_list_non_empty(..., must_contain=[{CLIENT_NAME!r}]) did NOT "
                        "raise on a list without it — an identity-less deny-list is as vacuous "
                        "as an empty one")
    except AssertionError:
        pass

    if problems:
        return CheckResult(name, 0.0, False, hard_fail=True, detail="; ".join(problems)), []

    try:
        terms = fixture.resolved_deny_terms(
            must_contain=[CLIENT_NAME, CLIENT_SHORT, CLIENT_SLUG, STAKEHOLDER])
    except Exception as exc:  # noqa: BLE001 - AssertionError from the guard, OSError from the reader
        return CheckResult(
            name, 0.0, False, hard_fail=True,
            detail=f"the deny-list resolved for the fixture engagement is unusable "
                   f"({type(exc).__name__}: {exc}) — nothing else in this row was evaluated, "
                   f"because every assertion built on it would pass vacuously",
        ), []

    return CheckResult(
        name, 1.0, True, hard_fail=True,
        detail=(f"the vacuity guard rejects both an empty list and an identity-less one; "
                f"production resolved {len(terms)} term(s) for the fixture, carrying the "
                f"client name, short name, directory slug and stakeholder"),
        evidence=[f"resolved deny term: {t!r}" for t in terms],
    ), terms


def _static_call_sites() -> list[int]:
    """Line numbers of every `run_agent(...)` call in `scripts/orchestrate.py`.

    Resolved through `repo_root()` so the mutation harness's shadow copy is
    what gets parsed, and by AST rather than regex so a `run_agent` mentioned
    in a comment or docstring is not counted as a call site.
    """
    source = (repo_root() / "scripts" / "orchestrate.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    return sorted({node.func.lineno for node in ast.walk(tree)
                   if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                   and node.func.id == "run_agent"})


def _check_traversal_covers_every_agent_call_site(data: dict, expected_runs: list) -> CheckResult:
    """Non-vacuity for the whole row: the traversal really walked the pipeline.

    Every "no client identifier anywhere" assertion below is only as strong as
    the set of invocations it ran over — over an empty set it is a tautology.
    So: all three traversals produced records; the total clears a floor; every
    record carries the label and call site that identify it; and the set of
    `run_agent(` call sites ACTUALLY EXECUTED equals the set the AST finds in
    `orchestrate.py`.

    That last equality is the drift alarm in both directions. A call site added
    to a step this traversal does not drive (or one that becomes unreachable,
    e.g. a branch condition pinned true) shows up as UNCOVERED. A recorded line
    that the AST does not know about means the capture is reading the wrong
    frame and the coverage claim is not trustworthy.
    """
    name = "traversal_covers_every_agent_call_site"
    records = data["records"]
    problems: list[str] = []

    by_run: dict[str, int] = {}
    for rec in records:
        by_run[rec["run"]] = by_run.get(rec["run"], 0) + 1
    for run_id in expected_runs:
        if not by_run.get(run_id):
            problems.append(f"traversal {run_id!r} produced NO agent invocations")
    if len(records) < MIN_TRAVERSAL_RECORDS:
        problems.append(f"only {len(records)} invocation(s) recorded across all traversals "
                        f"(floor {MIN_TRAVERSAL_RECORDS}) — this did not walk the pipeline")

    unlabelled = [r["agent"] for r in records if not r.get("label")]
    if unlabelled:
        problems.append(f"{len(unlabelled)} record(s) never reached the query stub "
                        f"(no label): {sorted(set(unlabelled))}")
    no_line = [r["agent"] for r in records if r.get("call_line") is None]
    if no_line:
        problems.append(f"{len(no_line)} record(s) carry no call-site line number: "
                        f"{sorted(set(no_line))}")

    static = _static_call_sites()
    executed = sorted({r["call_line"] for r in records if r.get("call_line") is not None})
    uncovered = sorted(set(static) - set(executed))
    unexpected = sorted(set(executed) - set(static))
    if uncovered:
        problems.append(f"run_agent call site(s) at orchestrate.py line(s) {uncovered} were "
                        f"NEVER executed by this traversal — they are not covered by this gate")
    if unexpected:
        problems.append(f"recorded call site line(s) {unexpected} are not run_agent calls "
                        f"according to the AST — the call-site capture is unreliable")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"{len(records)} agent invocation(s) across {len(by_run)} traversal(s) "
                f"({', '.join(f'{k}={v}' for k, v in sorted(by_run.items()))}); all "
                f"{len(static)} run_agent call site(s) in orchestrate.py executed"),
        evidence=[f"{run}: {count} invocation(s)" for run, count in sorted(by_run.items())]
                 + [f"orchestrate.py run_agent call sites executed: {executed}"],
        exercised=f"scripts/orchestrate.py pipeline steps via {data['interpreter']} "
                  f"({data['interpreter_note']}), _resilient_query stubbed",
    )


def _check_no_client_identifier_in_composed_prompt(data: dict, terms: list) -> CheckResult:
    """#167's guarantee, half one: no COMPOSED PROMPT names the client.

    `compose_prompt` renders every path param into the Runtime Parameters table
    as a value, so a step still holding the client-named engagement directory
    puts it in front of the model on every call. Three assertions:

      - the scanner's positive control found the client name in a string that
        contains it (without this, "no hits" proves nothing);
      - no deny term appears in any composed prompt;
      - the fixture's own engagement PATH appears in no composed prompt — a
        stronger, term-independent statement than the deny-term scan, and the
        one that survives a weak deny-list.
    """
    name = "no_client_identifier_in_composed_prompt"
    records = data["records"]
    problems: list[str] = []

    if not data.get("scanner_selftest"):
        problems.append("the traversal's term scanner found NOTHING in a control string that "
                        "names the client — every 'no hits' result below is vacuous")

    leaked = [r for r in records if r["prompt_hits"]]
    for rec in leaked[:8]:
        problems.append(f"{rec['run']}/{rec['step']}/{rec['agent']} (orchestrate.py:"
                        f"{rec['call_line']}): composed prompt contains {rec['prompt_hits']}")
    if len(leaked) > 8:
        problems.append(f"... and {len(leaked) - 8} more invocation(s) with a client "
                        f"identifier in the composed prompt")

    pathed = [r for r in records if r.get("engagement_path_in_prompt")]
    if pathed:
        problems.append(f"{len(pathed)} composed prompt(s) render the client-named engagement "
                        f"directory itself, e.g. {pathed[0]['run']}/{pathed[0]['agent']} at "
                        f"orchestrate.py:{pathed[0]['call_line']}")

    refused = [r for r in records if r.get("refused_on") == "composed prompt"]
    if refused:
        problems.append(f"{len(refused)} invocation(s) were REFUSED by "
                        f"_assert_neutral_invocation over their composed prompt — the pipeline "
                        f"failed closed, but a client-identifying prompt was still composed: "
                        f"{refused[0]['refusal']}")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"{len(records)} composed prompt(s) scanned against {len(terms)} deny term(s) "
                f"({', '.join(repr(t) for t in terms)}); zero hits, and none renders the "
                f"client-named engagement directory"),
        evidence=[f"scanner positive control matched: {data.get('scanner_selftest')}"],
    )


def _check_cwd_is_neutral_workspace_for_every_invocation(data: dict, terms: list) -> CheckResult:
    """#167's guarantee, half two: no `cwd` names the client — and the WORKSPACE
    ROOT is included, not just the files under it.

    Positive, not merely negative: every invocation's `cwd` must be exactly its
    traversal's neutral workspace, under `WORKSPACE_ROOT`. A deny-term scan
    alone would pass a `cwd` pointed at some third client-free-but-wrong
    directory; the identity assertion is what pins it to the workspace
    `materialise_workspace` built.
    """
    name = "cwd_is_neutral_workspace_for_every_invocation"
    records = data["records"]
    workspaces = data["workspaces"]
    workspace_root = data["workspace_root"]
    problems: list[str] = []

    leaked = [r for r in records if r["cwd_hits"]]
    for rec in leaked[:8]:
        problems.append(f"{rec['run']}/{rec['step']}/{rec['agent']} (orchestrate.py:"
                        f"{rec['call_line']}): cwd {rec['cwd']!r} contains {rec['cwd_hits']}")
    if len(leaked) > 8:
        problems.append(f"... and {len(leaked) - 8} more invocation(s) with a client "
                        f"identifier in the cwd")

    for rec in records:
        expected = workspaces.get(rec["run"])
        if expected and rec["cwd"] != expected:
            problems.append(f"{rec['run']}/{rec['agent']} (orchestrate.py:{rec['call_line']}) ran "
                            f"with cwd {rec['cwd']!r}, not the run's neutral workspace "
                            f"{expected!r}")
            break

    # The workspace root itself, segment by segment — #166's "workspace root
    # included" clause. `Meridian` hides inside a name like
    # `.anon_Meridian_notes.md`, so this is a substring test, not equality.
    for run_id, path in sorted(workspaces.items()):
        if not str(path).startswith(str(workspace_root)):
            problems.append(f"{run_id}: workspace {path!r} is not under WORKSPACE_ROOT "
                            f"{workspace_root!r}")
        for segment in Path(path).parts:
            hits = sorted(t for t in terms if t.lower() in segment.lower())
            if hits:
                problems.append(f"{run_id}: workspace path segment {segment!r} matches deny "
                                f"term(s) {hits}")

    refused = [r for r in records if r.get("refused_on") == "cwd"]
    if refused:
        problems.append(f"{len(refused)} invocation(s) were REFUSED by "
                        f"_assert_neutral_invocation over their cwd: {refused[0]['refusal']}")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"all {len(records)} invocation(s) ran with cwd == their run's neutral "
                f"workspace under {workspace_root}; no path segment of any workspace (root "
                f"included) matches any of the {len(terms)} deny term(s)"),
        evidence=[f"{run}: {path}" for run, path in sorted(workspaces.items())],
    )


def _check_neutral_invocation_assertion_refuses_client_named_cwd(data: dict) -> CheckResult:
    """The runtime enforcement itself, exercised directly rather than inferred.

    The traversal above passes because every step hands `run_agent` a neutral
    workspace — which is true whether or not `_assert_neutral_invocation` still
    works. So the probes call the REAL assertion, with the real deny-list
    installed for the fixture, in all three positions:

      client-named cwd     -> must raise ClientIdentifierLeak
      client-naming prompt -> must raise ClientIdentifierLeak
      neutral invocation   -> must NOT raise (the negative control: an
                              assertion that refuses everything is not a gate,
                              it is an outage)
    """
    name = "neutral_invocation_assertion_refuses_client_named_cwd"
    problems: list[str] = []
    seen = 0
    for run_id, probe in sorted(data["probes"].items()):
        seen += 1
        if not probe.get("client_named_cwd_refused"):
            problems.append(f"{run_id}: a client-named cwd was ALLOWED — "
                            f"_assert_neutral_invocation did not fail closed")
        elif probe["client_named_cwd_refused"].startswith("UNEXPECTED"):
            problems.append(f"{run_id}: client-named cwd raised the wrong error: "
                            f"{probe['client_named_cwd_refused']}")
        if not probe.get("client_named_prompt_refused"):
            problems.append(f"{run_id}: a composed prompt naming the client was ALLOWED")
        elif probe["client_named_prompt_refused"].startswith("UNEXPECTED"):
            problems.append(f"{run_id}: client-naming prompt raised the wrong error: "
                            f"{probe['client_named_prompt_refused']}")
        if probe.get("neutral_invocation_allowed"):
            problems.append(f"{run_id}: a NEUTRAL invocation was refused "
                            f"({probe['neutral_invocation_allowed']}) — the assertion refuses "
                            f"everything, which certifies nothing and would wedge every run")
    if not seen:
        problems.append("no probe results were reported at all")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"across {seen} traversal(s): a client-named cwd and a client-naming composed "
                f"prompt each raised ClientIdentifierLeak; the neutral invocation was allowed"),
    )


def _check_workspace_root_placement_and_resume_reattaches(data: dict, terms: list) -> CheckResult:
    """solution-design-v6 D6 + D15 — where the workspace lives, and what
    `--resume-from` does with it.

      D6/D15 placement: `WORKSPACE_ROOT` sits directly under the repo root (so
        agents can still reach the repo-relative `knowledge/` paths their
        prompts name) and NOT under `engagements/` — `denylist.py` mines the
        name of every child of `engagements/`, so a workspace parked there
        would pollute the deny-list of every session.
      D15 resume: `--resume-from` REATTACHES to the workspace the interrupted
        run used; it must not re-materialise a second one. Re-materialising
        would mean seeding from the engagement's `outputs/`, which may already
        have been through `deanonymize_dir` and therefore hold the client's
        REAL name — re-injecting exactly what this ticket keeps out, on the one
        path nobody exercises until something has already gone wrong.
    """
    name = "workspace_root_placement_and_resume_reattaches"
    problems: list[str] = []
    root = Path(data["repo_root"])
    workspace_root = Path(data["workspace_root"])

    if workspace_root.parent != root:
        problems.append(f"WORKSPACE_ROOT {workspace_root} is not directly under the repo root "
                        f"{root} — agent prompts name repo-relative knowledge paths that only "
                        f"resolve from that depth")
    if "engagements" in workspace_root.parts:
        problems.append(f"WORKSPACE_ROOT {workspace_root} sits under engagements/ — denylist.py "
                        f"mines the name of every child there, so this would pollute the "
                        f"deny-list of every session")
    root_hits = sorted(t for t in terms if t.lower() in workspace_root.name.lower())
    if root_hits:
        problems.append(f"WORKSPACE_ROOT name {workspace_root.name!r} matches deny term(s) "
                        f"{root_hits}")

    for run_id, used in sorted(data["workspaces"].items()):
        reattached = data["resume"].get(run_id)
        if reattached != used:
            problems.append(f"{run_id}: --resume-from reattached to {reattached!r}, not the "
                            f"workspace the run actually used ({used!r})")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"WORKSPACE_ROOT={workspace_root} is a direct child of the repo root, outside "
                f"engagements/, client-free; --resume-from reattached to the same workspace for "
                f"all {len(data['workspaces'])} traversal(s)"),
    )


def _check_log_redaction_backstop_scrubs_client_paths(data: dict, terms: list) -> CheckResult:
    """D15's log-redaction backstop — the pipeline's stdout is not private.

    `orchestrate.py` is normally launched with Bash from inside a Claude Code
    session, so every line it prints is read back into a model's context, and
    into the journal, the telemetry extractor and the consultant's scrollback.
    Repointing prompts and `cwd` at a neutral workspace achieves nothing if the
    next `log()` call prints the client-named engagement path.

    This is a BACKSTOP, not the control — which is why the third assertion
    matters as much as the first two: the neutral workspace path must come back
    UNCHANGED. A `_redact` that blanket-scrubbed its input would satisfy "no
    deny term survives" while destroying every log line the consultant needs.
    """
    name = "log_redaction_backstop_scrubs_client_paths"
    problems: list[str] = []
    for run_id, probe in sorted(data["probes"].items()):
        for field in ("redacted_engagement_path", "redacted_client_sentence"):
            value = probe.get(field, "")
            survivors = sorted(t for t in terms if t.lower() in value.lower())
            if survivors:
                problems.append(f"{run_id}/{field}: deny term(s) {survivors} survived redaction "
                                f"({value!r})")
            if "<REDACTED>" not in value:
                problems.append(f"{run_id}/{field}: nothing was redacted at all ({value!r})")
        workspace = probe.get("workspace_path", "")
        if probe.get("redacted_workspace_path") != workspace:
            problems.append(f"{run_id}: the NEUTRAL workspace path was redacted too "
                            f"({probe.get('redacted_workspace_path')!r} != {workspace!r}) — "
                            f"blanket redaction would make every log line useless and would "
                            f"hide a real leak behind a wall of <REDACTED>")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"the client-named engagement path and a client-naming sentence both come back "
                f"with every deny term replaced by <REDACTED>; the neutral workspace path is "
                f"returned unchanged"),
    )


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

# The checks that depend on a completed traversal, in report order. Names are
# DERIVED from the functions so the "not evaluated" path below can never drift
# out of sync with what actually runs.
_TRAVERSAL_CHECKS = (
    _check_traversal_covers_every_agent_call_site,
    _check_no_client_identifier_in_composed_prompt,
    _check_cwd_is_neutral_workspace_for_every_invocation,
    _check_neutral_invocation_assertion_refuses_client_named_cwd,
    _check_workspace_root_placement_and_resume_reattaches,
    _check_log_redaction_backstop_scrubs_client_paths,
)

CHECK_NAMES = ("denylist_nonempty_asserted_first",) + tuple(
    fn.__name__[len("_check_"):] for fn in _TRAVERSAL_CHECKS)

TRAVERSAL_PLAN = (
    ("ni_multi", "non-interactive", 3),
    ("interactive", "interactive", 3),
    ("ni_single", "non-interactive", 1),
)


def _not_evaluated(detail: str) -> list[CheckResult]:
    """Every traversal-dependent check, as a named hard failure with one shared
    reason. Reporting a single check instead would leave the rest "not
    executed", which #182 flags as a second, less informative error on top."""
    return [CheckResult(fn.__name__[len("_check_"):], 0.0, False, hard_fail=True, detail=detail)
            for fn in _TRAVERSAL_CHECKS]


def evaluate(target: str = "") -> list[CheckResult]:
    """`target` is ignored: this row has no committed golden. Every fixture is
    synthesised in a tempdir, because the subject is a code path (the pipeline's
    invocation envelope), not an artifact.
    """
    del target  # noqa: F841 - documented above; the signature is the row contract
    with tempfile.TemporaryDirectory(prefix="cortex_eval_pipeline_ws_") as td:
        tmp = Path(td)
        try:
            fixtures = [(tid, mode, _fixture(tmp, tid, n)) for tid, mode, n in TRAVERSAL_PLAN]
        except Exception as exc:  # noqa: BLE001 - a broken fixture must report, not crash
            detail = (f"could not build the synthetic engagement fixtures "
                      f"({type(exc).__name__}: {exc})")
            return ([CheckResult("denylist_nonempty_asserted_first", 0.0, False,
                                 hard_fail=True, detail=detail)] + _not_evaluated(detail))

        denylist_check, terms = _check_denylist_nonempty_asserted_first(fixtures[0][2])
        if not terms:
            # STRUCTURAL ORDERING: with no usable deny-list the traversal is
            # never launched, because every assertion it feeds would be vacuous.
            return [denylist_check] + _not_evaluated(
                f"NOT EVALUATED — `denylist_nonempty_asserted_first` failed first "
                f"({denylist_check.detail})")

        try:
            data = _run_traversal(tmp, fixtures, terms)
        except Exception as exc:  # noqa: BLE001 - report, never crash the suite
            return [denylist_check] + _not_evaluated(
                f"the pipeline traversal did not run ({type(exc).__name__}: {exc})")

        results = [denylist_check]
        expected_runs = [tid for tid, _, _ in TRAVERSAL_PLAN]
        for fn in _TRAVERSAL_CHECKS:
            try:
                if fn is _check_traversal_covers_every_agent_call_site:
                    results.append(fn(data, expected_runs))
                elif fn is _check_neutral_invocation_assertion_refuses_client_named_cwd:
                    results.append(fn(data))
                else:
                    results.append(fn(data, terms))
            except Exception as exc:  # noqa: BLE001 - a raising check still reports
                results.append(CheckResult(
                    fn.__name__[len("_check_"):], 0.0, False, hard_fail=True,
                    detail=f"check raised {type(exc).__name__}: {exc}"))
        return results
