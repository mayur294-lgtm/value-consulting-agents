#!/usr/bin/env python3
"""Mutation harness — the machinery that proves a declared check can actually fail.

A check with no demonstrated failure mode certifies nothing. Until now the
"gate-bites proof" was a convention: a human broke something by hand, watched a
rubric go red, pasted the output into a PR description, and put the file back.
Conventions are exactly what let PRs #118-#123 ship on a rubber stamp. This
module turns that convention into machinery.

Two mutation kinds, one harness (solution-design-v7, D2 + D3):

  kind="source"    Does this check detect broken CODE? Mutate a copy of the
                   component's own source (a hook, a script, a runner) and
                   require the NAMED check to go red.
  kind="fixture"   Does this check detect a broken ARTIFACT? Mutate a copy of
                   the frozen golden the rubric scores and require the NAMED
                   check to go red. This is the per-check negative from D3 —
                   at threshold 0.80 a whole-artifact negative only has to
                   break a fifth of the checks to drop below the line, so an
                   individually-inert check still hides. A per-check fixture
                   mutation proves the specific claim.

`before` and `after` are BOTH required. `before` must PASS on the unmutated
tree and `after` must FAIL on the mutated one. If `before` already fails, that
is its own error state — the check was broken before the mutation touched
anything, and the result is emphatically not "proven".


Isolation contract (D2) — the hard constraint
---------------------------------------------
**The working tree is never written to.** Every mutation is applied to a copy.

This harness runs inside `bb-build` subagents and in CI, where a crash or a
SIGKILL is a normal event. In-place mutation with restore-in-`finally` (how the
v6 proofs were done by hand) would, on any hard kill, leave a developer's tree
silently carrying a deliberately-broken security hook. A throwaway git worktree
is fully isolated but needs clean git state, which mid-ticket builds rarely
have. Both were explicitly rejected in D2.

So: `SHADOW_SUBTREES` of the repo are copied into a `TemporaryDirectory` — a
"shadow root" that is a structurally faithful stand-in for the repo root. The
mutation is applied inside that copy, the rubric is imported from that copy,
and the whole thing is discarded. A SIGKILL at any point leaves a stray
tempdir the OS reaps and nothing else. `WorkingTreeGuard` re-hashes every
shadowed subtree after each run and raises `WorkingTreeMutated` if a single
byte moved.

Scoring happens in a FRESH CHILD INTERPRETER (`sys.executable -c ...`) whose
`sys.path` is prepended with the shadow's `evals/` and which calls
`importlib.invalidate_caches()` before importing the rubric. A child rather
than an in-process import for two reasons: (1) `--mutate` (#185) will run from
inside `run_experiment.py`, which has ALREADY imported `rubrics.base` — purging
and re-importing it in-process would leave the parent holding a `CheckResult`
class that is not the child's, and every `isinstance` downstream would quietly
disagree; (2) a mutated module that crashes on import, leaks state, or installs
an `atexit` hook cannot damage the run that is grading it.


What this harness CAN mutate
----------------------------
1. **Pure-Python rubrics that read an artifact.** The deliverable rubrics and
   the `specifics.py`-backed component rows. Both kinds work: `source` mutates
   the shadow's `evals/rubrics/**`, `fixture` mutates the shadow's golden.

2. **Rubrics that invoke a repo script as a subprocess, resolving it through
   `rubrics.base.repo_root()`.** This is the interesting case, and it works
   *only because* `repo_root()` walks up from `rubrics/base.py`'s own
   `__file__` — which, in the child, is the SHADOW copy. So `repo_root()`
   returns the shadow root and `mcp_query_guard`, `pii_anonymizer` and
   `run_experiment_runner` all subprocess the shadow's copy of their subject,
   not the repo's. This is why `SHADOW_SUBTREES` must include `.claude/` and
   `scripts/` and not just `evals/`: the module tree a rubric needs is the
   tree it resolves paths into, not merely the package it is imported from.

3. **Frozen goldens and fixtures** under `evals/goldens/**` (`kind="fixture"`).


What this harness CANNOT mutate — stated plainly, not papered over
------------------------------------------------------------------
* **Any file outside `SHADOW_SUBTREES`.** `knowledge/` (250 MB) and
  `engagements/` (gitignored, PII) are deliberately not copied. A mutation
  naming a file there is REFUSED with `proven: false` and a detail saying so —
  it is never applied to the real file and never silently skipped.

* **Rubrics that resolve their subject by any route other than `repo_root()`** —
  a hardcoded absolute path, `Path.cwd()` captured at import, `git rev-parse`,
  or an env var pointing at the real checkout. Such a rubric reads the REAL
  file, the shadow mutation has no effect on what runs, and the check stays
  green. The harness reports `proven: false` ("the check stayed green"), which
  is honest but **conflates a genuinely inert check with an unreached
  mutation** — on its own, `proven: false` does not say which. The two ARE
  distinguishable, via a reachability canary: delete the shadow copy of the
  mutation's `file`, rescore, and check whether the named check's state moved
  at all. A genuinely inert check is unmoved either way (REACHABLE, still
  green); a check resolving through a path outside `repo_root()` is also
  unmoved by the deletion, because it never reads the shadow copy at all
  (UNREACHABLE). Enforcing that distinction — running the canary and reporting
  UNREACHABLE as a harness error rather than a failed proof — is #186's job,
  not this module's. If a new rubric is added, resolve its paths through
  `repo_root()` or it cannot be mutation-proven.

* **Agent-prompt BEHAVIOUR.** `.claude/agents/**` is shadowed, so a mutation to
  a prompt does physically apply — but no path-2 rubric ever *executes* a
  prompt, so the mutation can only bite where a rubric greps the `.md` text
  (e.g. `knowledge_harvester.py`'s agent-file assertions). Proving that a
  changed prompt changes an agent's OUTPUT is path-1's job (`evals/path1.py`),
  not this harness's, and no `mutations:` entry should claim otherwise.

* **Anything the subject reads from outside the repo** — installed
  site-packages (Presidio, spaCy), the OS, the network, a consultant's
  `~/.claude`. Those come from the real environment in the child exactly as
  they do in a normal run.

* **Git state.** The shadow is not a checkout of this repo (`.git` is excluded;
  an empty `git init` is run in the shadow purely to stop any `git` command a
  mutated script issues from escaping upward to a real repository). A check
  that asserts on `git status`, `git check-ignore`, or branch state will behave
  differently in the shadow than in the working tree, and a mutation covering
  it is not trustworthy.


Scope
-----
This module is machinery only. The `--mutate` runner mode is #185, preflight
enforcement ("a declared check with no mutation entry fails preflight") is
#186, and the self-gating `mutation-harness` registry row is #187. The API here
is shaped for those three to consume: `mutations_from_spec()` reads a registry
row, `prove_all()` returns one `MutationResult` per `Mutation`, and
`MutationResult.message()` renders the exact failure text from ux-design-v7.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

HERE = Path(__file__).resolve().parent          # evals/
ROOT = HERE.parent                              # cortex repo root

# --- what the shadow root contains -------------------------------------------
# The repo subtrees copied into the TemporaryDirectory. This is "the target's
# module tree" generalised: it must cover not only the package the rubric is
# imported from (evals/) but every tree a rubric resolves a subject path INTO
# via repo_root() — hooks and settings.json (.claude/), pipeline and PII code
# (scripts/), generators (tools/), and output templates (templates/), and
# design-system fixtures a row gates on via `input:` (presentations/).
# knowledge/ (250 MB) and engagements/ (gitignored PII) are deliberately out;
# see the module docstring's "CANNOT mutate" section.
#
# `presentations/` was added by #201 and is NOT optional polish. The
# `frontline-builders` row gates on `presentations/frontline-2026/design-tokens.json`
# via `input:`. While that tree was absent from the shadow, `check_registry.py`
# run INSIDE a shadow hard-errored on the missing golden — which broke
# `mutation-harness`'s `every_registered_check_has_a_mutation` (it runs the real
# preflight and requires rc=0) BEFORE its own mutation was even applied, taking
# `--mutate mutation-harness` from 5/5 to 4/5. The real tree resolved fine, so
# nothing caught it until the harness tried to prove itself.
#
# THE GENERAL RULE, now enforced rather than remembered: any gating `input:` /
# golden path on a mutation-proof-enforced row MUST live under one of these
# subtrees, or the gate is silently vacuous inside every shadow. That rule is a
# preflight ERROR in `check_registry.py` (`_outside_shadow`), which reads this
# tuple directly — so extending the shadow here is what makes such a fixture
# legal, and the two can never drift.
#
# `.prd/` was added for the same reason, one rule later: `require-harness`'s
# `repo_prd_state_matches_gate` is a DEPLOYMENT check — it runs the hook over the
# repo's real `.prd/prd-v*.md` front matter, because every other check in that row
# builds a tidy synthetic root and so stayed green while the shipped repo state
# defeated the gate entirely (measured 2026-08-28). A deployment check is only
# honest if the shadow carries the same tree the real run reads; without this the
# check hard-failed inside every shadow with "no .prd/prd-v*.md in the repo".
# It is planning markdown — small, and no bigger risk in a temp dir than on disk.
SHADOW_SUBTREES: tuple[str, ...] = ("evals", ".claude", "scripts", "tools",
                                     "templates", "presentations", ".prd")

# Small root-level files copied alongside, so a shadow run reads the same
# config a real run does.
SHADOW_ROOT_FILES: tuple[str, ...] = (
    ".gitignore", ".mcp.json", "CLAUDE.md", "README.md", "STRUCTURE.md",
    "VERSION", "requirements.txt",
)

# Never copied, and never digested by WorkingTreeGuard (bytecode legitimately
# churns). `worktrees` excludes .claude/worktrees — 267 MB of unrelated trees.
SHADOW_IGNORE_NAMES: frozenset[str] = frozenset({
    "__pycache__", ".git", ".venv", "worktrees", ".DS_Store", "node_modules",
    ".pytest_cache", ".mypy_cache",
})
SHADOW_IGNORE_SUFFIXES: tuple[str, ...] = (".pyc", ".pyo")

DEFAULT_SCORE_TIMEOUT_S: float = 300.0

_SCORE_SENTINEL = "__CORTEX_MUTATION_SCORE__"

# Runs in a fresh child interpreter with the shadow's evals/ prepended to
# sys.path. Emits one sentinel-prefixed JSON line on stdout; everything the
# rubric itself prints is left alone above it.
_SCORE_CHILD_SRC = r'''
import importlib, json, sys, traceback

shadow_evals, module_name, target, sentinel = sys.argv[1:5]
sys.path.insert(0, shadow_evals)          # the shadow's rubrics package wins
importlib.invalidate_caches()             # never serve a cached real-tree module

def emit(payload):
    sys.stdout.write("\n" + sentinel + json.dumps(payload) + "\n")
    sys.stdout.flush()

try:
    mod = importlib.import_module(module_name)
    if not hasattr(mod, "evaluate"):
        emit({"ok": False, "error": "module %r has no evaluate()" % module_name})
        raise SystemExit(0)
    checks = mod.evaluate(target)
    emit({"ok": True, "checks": [
        {
            "name": c.name,
            "score": float(c.score),
            "passed": bool(c.passed),
            "skipped": bool(getattr(c, "skipped", False)),
            "unscorable": bool(getattr(c, "unscorable", False)),
            "hard_fail": bool(getattr(c, "hard_fail", False)),
            "detail": str(getattr(c, "detail", "") or ""),
        }
        for c in checks
    ]})
except SystemExit:
    raise
except BaseException as exc:
    emit({"ok": False, "error": "%s: %s" % (type(exc).__name__, exc),
          "traceback": traceback.format_exc()[-2000:]})
'''


class MutationHarnessError(RuntimeError):
    """A mutation could not be run as specified (bad path, unreadable file, ...)."""


class WorkingTreeMutated(MutationHarnessError):
    """The working tree changed while the harness ran. This is the one invariant
    the harness exists to protect, so it is raised, never downgraded to a
    result field."""


# --- the two records the design fixes ----------------------------------------

@dataclass(frozen=True)
class Mutation:
    """One named way to break one named check.

    check    the check this mutation MUST make red — a name from the row's `code:` list
    file     repo-relative path to mutate (source file, or the golden for kind="fixture")
    find     literal substring, or a regex when `regex=True`
    replace  what to put in its place; "" is a strip
    kind     "source" (does the check detect broken code?) |
             "fixture" (does the check detect a broken artifact?)
    regex    opt-in. Off by default so a `find:` that stops matching after a
             refactor reports INERT rather than being silently retried as a
             pattern that happens to match something else.
    """
    check: str
    file: str
    find: str
    replace: str = ""
    kind: str = "source"
    regex: bool = False

    def __post_init__(self) -> None:
        if not self.check:
            raise MutationHarnessError("Mutation.check is required — a mutation must name the check it proves")
        if not self.file:
            raise MutationHarnessError(f"Mutation for check `{self.check}` has no `file`")
        if not self.find:
            raise MutationHarnessError(
                f"Mutation for check `{self.check}` has an empty `find` — an empty match would "
                f"rewrite the whole file, which proves nothing about the check")
        if self.kind not in ("source", "fixture"):
            raise MutationHarnessError(
                f"Mutation for check `{self.check}` has kind={self.kind!r}; expected 'source' or 'fixture'")
        if self.regex:
            try:
                re.compile(self.find)
            except re.error as exc:
                raise MutationHarnessError(
                    f"Mutation for check `{self.check}` declares regex=True but `find` "
                    f"does not compile: {exc}") from exc

    def describe(self) -> str:
        find_disp, replace_disp, note = _clip_diff_pair(self.find, self.replace)
        return (f"{self.file}: {find_disp!r} -> {replace_disp!r}{note}"
                f"{' [regex]' if self.regex else ''} ({self.kind})")

    @classmethod
    def from_entry(cls, check: str, entry: Any, *, kind: str = "source",
                   default_file: str | None = None) -> "Mutation":
        """Build a Mutation from one registry entry.

        Two authored shapes are accepted (solution-design-v7, "Data & Contract Model"):

          executable tier, `mutations:`   {file: ..., find: ..., replace: ...}
          calibration tier, `negatives:`  {strip: "<regex>"}   -> replace "", regex, fixture

        `default_file` supplies `file` for the `strip:` shape, whose file is the
        row's golden rather than something restated per check.
        """
        if not isinstance(entry, dict):
            raise MutationHarnessError(
                f"Mutation entry for check `{check}` must be a mapping, got {type(entry).__name__}")
        if "strip" in entry:
            file = entry.get("file") or default_file
            if not file:
                raise MutationHarnessError(
                    f"`strip:` mutation for check `{check}` has no file and no golden to default to")
            return cls(check=check, file=str(file), find=str(entry["strip"]),
                       replace="", kind=entry.get("kind", "fixture"), regex=True)
        file = entry.get("file") or default_file
        if not file:
            raise MutationHarnessError(f"Mutation entry for check `{check}` has no `file`")
        if "find" not in entry:
            raise MutationHarnessError(f"Mutation entry for check `{check}` has no `find`")
        return cls(check=check, file=str(file), find=str(entry["find"]),
                   replace=str(entry.get("replace", "")),
                   kind=str(entry.get("kind", kind)),
                   regex=bool(entry.get("regex", False)))


@dataclass
class MutationResult:
    """The outcome of one mutation.

    proven is True only when the named check PASSED before and FAILED after.
    Everything else — a stale `find` that matched nothing, a check that was
    already failing, a check that vanished, a rubric that crashed — is
    `proven: False` with `detail` saying which, because every one of those
    would otherwise read as a silent pass.
    """
    check: str
    proven: bool
    before: float
    after: float
    detail: str = ""
    mutation: Mutation | None = None

    def message(self) -> str:
        """The literal operator-facing sentence (ux-design-v7, Flow 2 + Error States)."""
        if self.proven:
            return (f"✓ proven: check `{self.check}` went red under "
                    f"{self.mutation.describe() if self.mutation else 'its mutation'} "
                    f"(before {self.before:.2f} pass, after {self.after:.2f} fail)")
        desc = self.mutation.describe() if self.mutation else "its mutation"
        return (f"✗ check `{self.check}` did not detect mutation ({desc}). "
                f"Either the check is inert or the mutation is wrong. A gate that cannot "
                f"fail certifies nothing — both must be resolved before this row can gate. "
                f"[{self.detail}]")

    def as_dict(self) -> dict[str, Any]:
        return {"check": self.check, "proven": self.proven, "before": self.before,
                "after": self.after, "detail": self.detail}


# --- working-tree guard -------------------------------------------------------

class WorkingTreeGuard:
    """Proof that the harness did not write to the working tree.

    Two independent signals, because either alone has a hole:
      * a sha256 digest of every file under `SHADOW_SUBTREES` (catches
        gitignored files, which `git status` would never mention), and
      * `git status --porcelain` over the whole repo (catches anything the
        harness touched outside those subtrees).

    `diff()` never raises — callers compute it in a `finally` so an in-flight
    exception is not masked, then raise `WorkingTreeMutated` themselves.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self._digest: dict[str, str] | None = None
        self._status: str | None = None

    def snapshot(self) -> None:
        self._digest = _tree_digest(self.root)
        self._status = _git_status(self.root)

    def diff(self) -> str | None:
        if self._digest is None:
            return None
        problems: list[str] = []
        now = _tree_digest(self.root)
        before_keys, after_keys = set(self._digest), set(now)
        for rel in sorted(after_keys - before_keys)[:20]:
            problems.append(f"created: {rel}")
        for rel in sorted(before_keys - after_keys)[:20]:
            problems.append(f"deleted: {rel}")
        for rel in sorted(before_keys & after_keys):
            if self._digest[rel] != now[rel]:
                problems.append(f"modified: {rel}")
                if len(problems) > 40:
                    break
        status_now = _git_status(self.root)
        if self._status is not None and status_now is not None and status_now != self._status:
            problems.append("git status --porcelain changed while the harness ran")
        if not problems:
            return None
        return ("The mutation harness must never write to the working tree, but it changed:\n  "
                + "\n  ".join(problems[:40]))


def _tree_digest(root: Path) -> dict[str, str]:
    """sha256 per file across the shadowed subtrees + the shadowed root files."""
    out: dict[str, str] = {}
    for sub in SHADOW_SUBTREES:
        base = root / sub
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SHADOW_IGNORE_NAMES]
            for fn in filenames:
                if fn in SHADOW_IGNORE_NAMES or fn.endswith(SHADOW_IGNORE_SUFFIXES):
                    continue
                p = Path(dirpath) / fn
                try:
                    out[str(p.relative_to(root))] = _sha256(p)
                except OSError:
                    out[str(p.relative_to(root))] = "<unreadable>"
    for name in SHADOW_ROOT_FILES:
        p = root / name
        if p.is_file():
            out[name] = _sha256(p)
    return out


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def _git_status(root: Path) -> str | None:
    try:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=str(root),
                           capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace")


# --- the shadow root ----------------------------------------------------------

def _copy_ignore(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names
            if n in SHADOW_IGNORE_NAMES or n.endswith(SHADOW_IGNORE_SUFFIXES)}


@contextlib.contextmanager
def shadow_root(root: Path | None = None) -> Iterator[Path]:
    """Yield a temp copy of the repo's mutable subtrees, then discard it.

    Copies (never symlinks) — a symlinked subtree would make a write inside the
    shadow land on the real file, which is the exact failure this harness
    exists to make impossible.
    """
    src_root = Path(root or ROOT).resolve()
    with tempfile.TemporaryDirectory(prefix="cortex_mutation_") as td:
        shadow = Path(td) / "repo"
        shadow.mkdir()
        for sub in SHADOW_SUBTREES:
            src = src_root / sub
            if src.is_dir():
                shutil.copytree(src, shadow / sub, ignore=_copy_ignore, symlinks=False)
        for name in SHADOW_ROOT_FILES:
            src = src_root / name
            if src.is_file():
                shutil.copy2(src, shadow / name)
        # An empty repo of its own, so any `git` command a mutated script issues
        # inside the shadow stops here instead of walking up to a real checkout
        # (TMPDIR is not guaranteed to sit outside one).
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(["git", "init", "-q"], cwd=str(shadow),
                           capture_output=True, timeout=60)
        yield shadow


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _resolve_mutable(root: Path, rel_or_abs: str) -> tuple[Path, Path]:
    """Resolve a mutation's `file` to (real_path, path_relative_to_root).

    Refuses anything the shadow would not contain, loudly. A mutation the
    harness cannot actually apply must never look like one it applied.
    """
    p = Path(rel_or_abs)
    real = (p if p.is_absolute() else (root / p)).resolve()
    if not _is_within(real, root):
        raise MutationHarnessError(
            f"`{rel_or_abs}` resolves outside the repo ({real}) — refusing to mutate it")
    rel = real.relative_to(root)
    top = rel.parts[0] if rel.parts else ""
    if top not in SHADOW_SUBTREES and str(rel) not in SHADOW_ROOT_FILES:
        raise MutationHarnessError(
            f"`{rel}` is not inside a shadowed subtree ({', '.join(SHADOW_SUBTREES)}). "
            f"The harness copies only those trees, so mutating this file would change "
            f"nothing the scored code reads — refusing rather than reporting a pass "
            f"the mutation never earned.")
    if not real.is_file():
        raise MutationHarnessError(f"`{rel}` does not exist in the working tree")
    return real, rel


def _apply(target_file: Path, mutation: Mutation) -> tuple[bool, int]:
    """Apply a mutation to a file inside the shadow. Returns (changed, matches)."""
    resolved = target_file.resolve()
    try:
        original = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise MutationHarnessError(
            f"`{mutation.file}` is not UTF-8 text — this harness mutates text only") from exc
    if mutation.regex:
        new, matches = re.subn(mutation.find, mutation.replace, original)
    else:
        matches = original.count(mutation.find)
        new = original.replace(mutation.find, mutation.replace)
    if new == original:
        return False, matches
    resolved.write_text(new, encoding="utf-8")
    return True, matches


def shadow_target(root: Path, shadow: Path, target: str) -> str:
    """Map the evaluator's target argument into the shadow where it lives there.

    Mirrors run_experiment._run_evaluator: an empty or unresolvable target is
    handed the root itself (several rubrics ignore the argument entirely). A
    target that is not shadowed is passed through as its real path — read-only,
    and the honest thing to do for e.g. a gitignored engagement directory.
    """
    if not target:
        return str(shadow)
    p = Path(target)
    real = (p if p.is_absolute() else (root / p)).resolve()
    if _is_within(real, root):
        candidate = shadow / real.relative_to(root)
        if candidate.exists():
            return str(candidate)
    return str(real) if real.exists() else target


# --- scoring ------------------------------------------------------------------

def score(shadow: Path, evaluator: str, target: str, *, timeout: float,
          python: str, extra_pythonpath: Sequence[str]) -> dict[str, dict[str, Any]]:
    """Run `evaluator.evaluate(target)` in a fresh child rooted at the shadow.

    Returns {check_name: {score, passed, skipped, unscorable, detail}}.
    Raises MutationHarnessError if the child produced no scoreable payload.

    This module has no `__all__`; `score()` and `shadow_target()` (below) are
    the supported entry points for #186's reachability canary — delete the
    shadow copy of a mutation's `file`, call `shadow_target()` to resolve the
    (now-deleted) path in the shadow, and `score()` again to see whether the
    named check's state moved.
    """
    shadow_evals = shadow / "evals"
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"      # no stale bytecode carried anywhere
    env["CORTEX_MUTATION_SHADOW"] = str(shadow)
    # The synthetic-registry override belongs to run_experiment_runner's own
    # internal subprocess calls; it must never leak in from the ambient shell.
    env.pop("CORTEX_EVAL_REGISTRY", None)
    for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"):
        env.pop(k, None)
    pp = [str(shadow_evals), *[str(x) for x in extra_pythonpath]]
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(pp) + (os.pathsep + existing if existing else "")

    cmd = [python, "-c", _SCORE_CHILD_SRC, str(shadow_evals), evaluator, target, _SCORE_SENTINEL]
    try:
        proc = subprocess.run(cmd, cwd=str(shadow), capture_output=True,
                              timeout=timeout, env=env)
    except subprocess.TimeoutExpired as exc:
        raise MutationHarnessError(
            f"scoring `{evaluator}` timed out after {timeout:.0f}s") from exc
    out = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")
    payload = None
    for line in out.splitlines():
        if line.startswith(_SCORE_SENTINEL):
            payload = line[len(_SCORE_SENTINEL):]
    if payload is None:
        raise MutationHarnessError(
            f"scoring `{evaluator}` produced no result (rc={proc.returncode}). "
            f"stderr tail: {err[-600:]!r}")
    data = json.loads(payload)
    if not data.get("ok"):
        raise MutationHarnessError(
            f"evaluator `{evaluator}` raised while scoring: {data.get('error')}")
    return {c["name"]: c for c in data["checks"]}


def _is_red(check: dict[str, Any]) -> bool:
    """Red = would drag this row's verdict down. A skip certifies nothing and a
    parser gap (`unscorable`) is excluded from the mean, so neither counts as
    the check having DETECTED the fault."""
    return not check["passed"] and not check["skipped"] and not check["unscorable"]


# --- public API ---------------------------------------------------------------

def mutations_from_spec(spec: dict, *, default_file: str | None = None) -> list[Mutation]:
    """Read a registry row's mutation declarations into Mutation records.

    `mutations:`  mapping check -> {file, find, replace}     -> kind "source"
    `negatives:`  mapping check -> {strip: "<regex>"}        -> kind "fixture"
                  (a LIST under `negatives:` is the legacy separate-negative-file
                  form driven by `--negatives`; it is not a mutation and is ignored)
    """
    golden = default_file
    if golden is None:
        goldens = spec.get("goldens")
        if isinstance(goldens, list) and goldens:
            golden = str(goldens[0])
        elif spec.get("golden"):
            golden = str(spec["golden"])
        elif isinstance(spec.get("input"), str):
            golden = str(spec["input"])
    out: list[Mutation] = []
    for check, entry in (spec.get("mutations") or {}).items():
        out.append(Mutation.from_entry(str(check), entry, kind="source", default_file=golden))
    negatives = spec.get("negatives")
    if isinstance(negatives, dict):
        for check, entry in negatives.items():
            out.append(Mutation.from_entry(str(check), entry, kind="fixture", default_file=golden))
    return out


def prove_all(mutations: Iterable[Mutation], *, evaluator: str, target: str = "",
              root: Path | None = None, timeout: float = DEFAULT_SCORE_TIMEOUT_S,
              python: str | None = None,
              extra_pythonpath: Sequence[str] = ()) -> list[MutationResult]:
    """Prove that each mutation makes its NAMED check go red.

    One pristine shadow is scored first to establish `before` for every check at
    once (the unmutated score of check X does not depend on which mutation comes
    next). Then each mutation gets its own fresh shadow, so no mutation can
    contaminate the next.

    Raises WorkingTreeMutated if the repo changed under us — that invariant is
    not negotiable and is not reported as a mere result field.
    """
    src_root = Path(root or ROOT).resolve()
    muts = list(mutations)
    if not muts:
        return []
    py = python or sys.executable

    guard = WorkingTreeGuard(src_root)
    guard.snapshot()
    breach: str | None = None
    try:
        try:
            with shadow_root(src_root) as pristine:
                baseline = score(pristine, evaluator, shadow_target(src_root, pristine, target),
                                  timeout=timeout, python=py, extra_pythonpath=extra_pythonpath)
        except MutationHarnessError as exc:
            # Nothing can be proven if the unmutated tree does not score.
            return [MutationResult(m.check, False, 0.0, 0.0,
                                   f"baseline scoring failed, so no `before` exists: {exc}", m)
                    for m in muts]
        results = [
            _prove_one(m, src_root, evaluator, target, baseline,
                       timeout=timeout, python=py, extra_pythonpath=extra_pythonpath)
            for m in muts
        ]
    finally:
        breach = guard.diff()
        if breach and sys.exc_info()[0] is not None:
            # An exception is already unwinding; don't mask it, but never let a
            # tree breach go unsaid.
            print(f"\n[mutations] WORKING TREE BREACH during an error unwind:\n{breach}",
                  file=sys.stderr)
    if breach:
        raise WorkingTreeMutated(breach)
    return results


def prove(mutation: Mutation, **kwargs: Any) -> MutationResult:
    """Single-mutation convenience wrapper over prove_all()."""
    return prove_all([mutation], **kwargs)[0]


def _prove_one(m: Mutation, root: Path, evaluator: str, target: str,
               baseline: dict[str, dict[str, Any]], *, timeout: float, python: str,
               extra_pythonpath: Sequence[str]) -> MutationResult:
    executed = sorted(baseline)
    before_check = baseline.get(m.check)
    if before_check is None:
        return MutationResult(
            m.check, False, 0.0, 0.0,
            f"evaluator `{evaluator}` never produced a check named `{m.check}` on the "
            f"unmutated tree (it produced: {executed}). A mutation cannot prove a check "
            f"that does not run.", m)
    before = float(before_check["score"])
    if before_check["skipped"] or before_check["unscorable"] or not before_check["passed"]:
        state = ("skipped" if before_check["skipped"]
                 else "unscorable" if before_check["unscorable"] else "already failing")
        return MutationResult(
            m.check, False, before, before,
            f"check `{m.check}` was {state} BEFORE the mutation "
            f"({before_check.get('detail', '')[:200]}). `before` must pass for `after` to "
            f"mean anything — fix the check first; this is not a mutation failure.", m)

    try:
        _real, rel = _resolve_mutable(root, m.file)
    except MutationHarnessError as exc:
        return MutationResult(m.check, False, before, before, str(exc), m)

    try:
        with shadow_root(root) as shadow:
            shadow_file = shadow / rel
            if not shadow_file.is_file():
                return MutationResult(
                    m.check, False, before, before,
                    f"`{rel}` was not copied into the shadow root — it is excluded by "
                    f"SHADOW_IGNORE_NAMES, so it cannot be mutated.", m)
            # Belt and braces: a copied tree has no symlinks, but never write
            # through anything that resolves back outside the tempdir.
            if not _is_within(shadow_file.resolve(), shadow.resolve()):
                raise MutationHarnessError(
                    f"refusing to write `{rel}`: it resolves outside the shadow root")
            changed, matches = _apply(shadow_file, m)
            if not changed:
                why = (f"`find` matched {matches}x but `replace` is byte-identical to it"
                       if matches else
                       f"`find` matched nothing in `{rel}` — the string is stale "
                       f"(a refactor moved or reworded it)")
                return MutationResult(
                    m.check, False, before, before,
                    f"mutation was INERT: {why}. Nothing was changed, so the unchanged "
                    f"green is meaningless — this is reported as NOT PROVEN, never as a pass.",
                    m)
            after_map = score(shadow, evaluator,
                               shadow_target(root, shadow,
                                              target or (str(rel) if m.kind == "fixture" else "")),
                               timeout=timeout, python=python, extra_pythonpath=extra_pythonpath)
    except MutationHarnessError as exc:
        return MutationResult(
            m.check, False, before, 0.0,
            f"the mutated tree could not be scored at all ({exc}). The mutation broke the "
            f"RUBRIC rather than being detected BY it — write a more surgical mutation.", m)

    after_check = after_map.get(m.check)
    if after_check is None:
        return MutationResult(
            m.check, False, before, 0.0,
            f"check `{m.check}` disappeared from the mutated run (executed: {sorted(after_map)}). "
            f"The mutation stopped the check from running rather than making it fail; that is a "
            f"different defect and does not prove the check detects anything.", m)

    after = float(after_check["score"])
    if _is_red(after_check):
        return MutationResult(
            m.check, True, before, after,
            f"{m.describe()} applied ({matches} match{'' if matches == 1 else 'es'}); "
            f"check went red: {after_check.get('detail', '')[:200]}", m)

    state = ("skipped" if after_check["skipped"]
             else "unscorable" if after_check["unscorable"] else "still passing")
    return MutationResult(
        m.check, False, before, after,
        f"mutation applied ({matches} match{'' if matches == 1 else 'es'}) but check `{m.check}` "
        f"is {state} (score {after:.2f}). Either the check is inert, or the mutation does not "
        f"reach the code the check exercises (see this module's docstring: a rubric that "
        f"resolves its subject outside `repo_root()` reads the REAL file, not the shadow).", m)


def _common_prefix_len(a: str, b: str) -> int:
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def _common_suffix_len(a: str, b: str, prefix_len: int, limit: int) -> int:
    """Chars `a` and `b` share at the end, without re-covering the prefix."""
    i = 0
    while i < limit and a[len(a) - 1 - i] == b[len(b) - 1 - i]:
        i += 1
    return i


def _clip_window(s: str, start: int, end: int, n: int = 60) -> str:
    """Render `s[start:end]` (capped to `n` chars), with `…` where content was elided."""
    end = min(end, start + n, len(s))
    start = min(start, end)
    piece = s[start:end].replace("\n", "\\n")
    return ("…" if start > 0 else "") + piece + ("…" if end < len(s) else "")


def _clip_diff_pair(find: str, replace: str, n: int = 60, context: int = 12) -> tuple[str, str, str]:
    """Render `find`/`replace` so their divergence is visible, not just their first N chars.

    A naive clip that truncates each string independently from index 0 — when
    `replace` is `find` plus/minus a suffix, or the two only diverge past
    index `n`, both clipped strings come out byte-identical and the report
    reads as "X -> X". This elides the common PREFIX (so both windows open at
    the point they actually diverge, with a little leading context) and, when
    cheap, the common SUFFIX too (so a huge shared tail doesn't pad the window
    with non-information). Returns (find_display, replace_display, note) —
    `note` is a trailing annotation for the one degenerate case worth calling
    out explicitly.
    """
    if find == replace:
        shown = _clip_window(find, 0, len(find), n)
        return shown, shown, " (find and replace are identical — malformed mutation)"

    prefix_len = _common_prefix_len(find, replace)
    remaining = min(len(find), len(replace)) - prefix_len
    suffix_len = _common_suffix_len(find, replace, prefix_len, remaining) if remaining > 0 else 0

    start = max(0, prefix_len - context)
    find_end = min(len(find), len(find) - suffix_len + context)
    replace_end = min(len(replace), len(replace) - suffix_len + context)

    find_disp = _clip_window(find, start, find_end, n)
    replace_disp = _clip_window(replace, start, replace_end, n)
    return find_disp, replace_disp, ""
