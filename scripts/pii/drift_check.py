#!/usr/bin/env python3
"""
Drift check — `scripts/pii/denylist.py` vs `.claude/hooks/mcp-query-guard.py`.

    python3 scripts/pii/drift_check.py

WHY THIS EXISTS
  The hook is deliberately SELF-CONTAINED and this ticket does not change it.
  Its self-containment is load-bearing: a module-level import that failed
  would raise before `main()`'s try/except, and a PreToolUse hook that exits
  that way is treated as NON-blocking — i.e. fail-open, in a hook whose whole
  purpose is failing closed. So the extraction logic now exists twice: once
  in the hook, once in `scripts/pii/denylist.py` (the seam the hook's own
  header calls out as "#159").

  Two copies that silently diverge is the failure mode to prevent. This
  script builds one fixture engagement tree and asserts BOTH produce the
  identical deny-list. Change one, and this tells you to change the other.

  It also pins the four regressions from the hook's adversarial review to the
  shared module, so a future edit to `denylist.py` cannot quietly reintroduce
  them:
    1. ordinary words ("list all onboarding capabilities") must NOT become
       client identifiers — no whole-document ALL-CAPS sweep
    2. `- **Client Name:** First Federal` must extract (markdown emphasis
       stripped from the captured value)
    3. `- **Name:** [Full legal name]` must yield nothing (unfilled template
       placeholders are not identifiers)
    4. the slug `bank_australia` must NOT add the bare word `bank`

  Standard library only, Python 3.9 compatible: the hook runs under the
  system interpreter (3.9.6 here) and so must this.

  Fixture naming follows the repo's synthetic-quarantine programme: no
  fictional bank names, only obviously-placeholder tokens.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "mcp-query-guard.py"

sys.path.insert(0, str(REPO_ROOT))

from scripts.pii import denylist  # noqa: E402


# --- fixture ---------------------------------------------------------------

def _seed_fixture(root):
    """One engagements/ tree exercising every extraction path both copies
    implement: client slug, CLIENT_PROFILE.md (with ALL-CAPS prose emphasis
    that must NOT become terms, a bold label line with a paren acronym, and a
    bare `**Name:**` field), ENGAGEMENT_CONTEXT.md, inputs/engagement_intake.md,
    an unfilled template, a generic-words-only label, and a slug whose parts
    are generic banking words."""
    eng = root / "engagements"

    # 1. Full-shape client: slug + profile + context + intake.
    c1 = eng / "zzzplaceholderclient"
    c1.mkdir(parents=True)
    (c1 / "CLIENT_PROFILE.md").write_text(
        "# CLIENT_PROFILE\n\n"
        "## EXECUTIVE SUMMARY\n\n"
        "**NEVER** share these figures outside the account team. This profile "
        "covers ALL engagement details for the SME segment at MEDIUM "
        "sensitivity — internal use only.\n\n"
        "- **Client Name:** Placeholder Holdings Group (ZPC)\n"
        "- **Primary Contact:** Jane Placeholder, SVP Digital Banking\n",
        encoding="utf-8",
    )
    e1 = c1 / "2026-01_test_engagement"
    (e1 / "inputs").mkdir(parents=True)
    (e1 / "ENGAGEMENT_CONTEXT.md").write_text(
        "# ENGAGEMENT_CONTEXT\n\n- **Client Name:** placeholdercontextonly\n",
        encoding="utf-8",
    )
    (e1 / "inputs" / "engagement_intake.md").write_text(
        "# Engagement Intake\n\n- **Client Name:** placeholderintakeonly\n",
        encoding="utf-8",
    )

    # 1b. Accented Latin identity — the 2026-08-30 widening. Both copies must
    #     extract these identically, and BOTH regexes are involved: the
    #     single-word client name goes through _WORD_RE/_single_word_ok (which
    #     used to shred "Länsförsäkringar" to "kringar" and "Bagócs" to
    #     nothing), and the stakeholder goes through _PERSON_TOKEN_RE (which
    #     used to drop "José Ramírez" entirely). A copy widened on one side
    #     only diverges here.
    c1b = eng / "zzzaccentedclient"
    c1b.mkdir(parents=True)
    (c1b / "CLIENT_PROFILE.md").write_text(
        "# CLIENT_PROFILE\n\n"
        "- **Client Name:** Zzzbagócs\n"
        "- **Client Name:** Zzzlänsförsäkringar\n"
        "- **Primary Contact:** Zzzjosé Zzzramírez, CFO\n",
        encoding="utf-8",
    )

    # 2. Regression 2 — bold label whose value is entirely generic words, so
    #    only the multi-word phrase path can catch it.
    c2 = eng / "zzzboldlabeltest"
    c2.mkdir(parents=True)
    (c2 / "CLIENT_PROFILE.md").write_text(
        "# Engagement Profile\n\n- **Client Name:** First Federal\n",
        encoding="utf-8",
    )

    # 3. Regression 3 — the literal unfilled templates/client_profile.md.
    c3 = eng / "zzzunfilledprofiletest"
    c3.mkdir(parents=True)
    (c3 / "CLIENT_PROFILE.md").write_text(
        "# Client Profile — [Client Name]\n\n"
        "## Client Identity\n\n"
        "- **Name:** [Full legal name]\n"
        "- **Short Name:** [slug used in directory names, e.g., `navy_federal`]\n",
        encoding="utf-8",
    )

    # 4. Regression 4 — a slug whose first part is a generic banking word.
    c4 = eng / "bank_australia"
    c4.mkdir(parents=True)

    # 5. Bare `**Name:**` in CLIENT_PROFILE.md (the "## Client Identity" form).
    c5 = eng / "zzznamelabeltest"
    c5.mkdir(parents=True)
    (c5 / "CLIENT_PROFILE.md").write_text(
        "# Client Profile — Zzzplaceholder\n\n"
        "## Client Identity\n\n"
        "- **Name:** Zzzplaceholder Fifth Test Holdings\n",
        encoding="utf-8",
    )

    # 6. Shared staging dirs that must be skipped, not treated as clients.
    (eng / "inputs").mkdir()
    (eng / "outputs").mkdir()


# --- the two resolvers -----------------------------------------------------

_HOOK_PROBE = (
    "import importlib.util, json, sys\n"
    "spec = importlib.util.spec_from_file_location('_hook', sys.argv[1])\n"
    "mod = importlib.util.module_from_spec(spec)\n"
    "spec.loader.exec_module(mod)\n"
    "print(json.dumps(sorted(mod._resolve_deny_list())))\n"
)


def _hook_deny_list(project_dir):
    """Run the REAL hook file's `_resolve_deny_list()` in a subprocess.

    A subprocess, not an import: the hook reads `CLAUDE_PROJECT_DIR` at
    MODULE level into `PROJECT_DIR`, so it has to be set before the module
    body runs, and running it out-of-process keeps its globals out of ours.
    """
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    proc = subprocess.run(
        [sys.executable, "-c", _HOOK_PROBE, str(HOOK_PATH)],
        capture_output=True, env=env, timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "hook probe failed (rc=%d): %s"
            % (proc.returncode, proc.stderr.decode("utf-8", "replace")[:2000])
        )
    return set(json.loads(proc.stdout.decode("utf-8")))


def _module_deny_list(project_dir):
    return set(denylist.resolve_deny_list(project_dir))


# --- checks ----------------------------------------------------------------

def check_parity(project_dir, out):
    module_terms = _module_deny_list(project_dir)
    hook_terms = _hook_deny_list(project_dir)

    out.append("pii.denylist  (%d terms): %s" % (
        len(module_terms), json.dumps(sorted(module_terms))))
    out.append("mcp-query-guard (%d terms): %s" % (
        len(hook_terms), json.dumps(sorted(hook_terms))))

    if module_terms == hook_terms:
        out.append("PASS  identical deny-lists")
        return True

    only_module = sorted(module_terms - hook_terms)
    only_hook = sorted(hook_terms - module_terms)
    out.append("FAIL  deny-lists diverged")
    out.append("      only in pii.denylist:   %s" % json.dumps(only_module))
    out.append("      only in mcp-query-guard: %s" % json.dumps(only_hook))
    return False


def check_regressions(terms, out):
    """The four cases from the hook's adversarial review, asserted against
    the shared module's extraction."""
    lower = {t.lower() for t in terms}
    ok = True

    # 1. Ordinary words from prose / ALL-CAPS emphasis must not be terms.
    generic = ["all", "not", "never", "sme", "medium", "name", "full", "legal",
               "list", "onboarding", "capabilities"]
    leaked = sorted(w for w in generic if w in lower)
    if leaked:
        ok = False
        out.append("FAIL  generic words became deny terms: %s" % json.dumps(leaked))
    else:
        out.append("PASS  no generic/emphasis word became a deny term (%s)"
                   % ", ".join(generic))

    # 2. A bold "- **Client Name:** First Federal" label must extract, with
    #    markdown emphasis stripped from the captured value.
    if "first federal" in lower:
        out.append("PASS  '- **Client Name:** First Federal' extracted as 'First Federal'")
    else:
        ok = False
        out.append("FAIL  bold 'Client Name:' label did not yield 'First Federal'")

    # 3. An unfilled "- **Name:** [Full legal name]" must yield nothing.
    #    (Checked above via 'full'/'legal'/'name'; also assert no bracket junk.)
    bracket_junk = sorted(t for t in terms if "[" in t or "]" in t)
    if bracket_junk:
        ok = False
        out.append("FAIL  bracketed template text became deny terms: %s"
                   % json.dumps(bracket_junk))
    else:
        out.append("PASS  '- **Name:** [Full legal name]' yielded no terms")

    # 4. The slug 'bank_australia' must not add the bare word 'bank'.
    if "bank" in lower:
        ok = False
        out.append("FAIL  slug 'bank_australia' added the bare word 'bank'")
    elif "bankaustralia" in lower and "australia" in lower:
        out.append("PASS  slug 'bank_australia' -> 'australia' + 'bankaustralia', not 'bank'")
    else:
        ok = False
        out.append("FAIL  slug 'bank_australia' did not extract as expected: %s"
                   % json.dumps(sorted(lower)))

    return ok


def main():
    if not HOOK_PATH.is_file():
        print("drift-check: %s not found" % HOOK_PATH, file=sys.stderr)
        return 2

    out = []
    with tempfile.TemporaryDirectory(prefix="pii_drift_") as td:
        root = Path(td)
        _seed_fixture(root)
        parity_ok = check_parity(root, out)
        out.append("")
        regressions_ok = check_regressions(_module_deny_list(root), out)

    print("\n".join(out))
    ok = parity_ok and regressions_ok
    print("\n%s" % ("DRIFT CHECK PASSED" if ok else "DRIFT CHECK FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
