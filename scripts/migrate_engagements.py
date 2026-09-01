#!/usr/bin/env python3
"""
Migrate client-named engagement directories to opaque engagement IDs.

    engagements/hdfc/2026-08_retail_renewal/  ->  engagements/<id>/2026-08_retail_renewal/

WHY (solution-design-v6.md D6)
  `scripts/orchestrate.py`'s `compose_prompt` renders `engagement_dir` into the
  invocation prompt as a VALUE, and `run_agent` sets `cwd` to that same path.
  So while the directory is called `hdfc`, the client's name reaches the model
  on every single agent call, no matter how well the file CONTENTS are
  scrubbed. Opaque directories close the path envelope; `.engagement_map.json`
  (repo root, chmod 600, gitignored) is the only thing that binds an ID back to
  a client, and it never leaves the machine.

THE LOAD-BEARING HAZARD — MEASURED, NOT ASSUMED
  The client's directory name is not only a leak. It is also a deny-list
  SOURCE: `denylist.extract_terms_from_slug(client_dir.name, ...)` is what puts
  `hdfc` on the list that `mcp-query-guard.py` blocks outbound queries against.

  Measured against the seven live directories before writing a line of this:

      bank_australia      slug-only  -> loses ['australia', 'bankaustralia']
      bdo-apa             slug-only  -> loses ['bdoapa']
      bdo-mh              slug-only  -> loses ['bdomh']
      hdfc                slug-only  -> loses ['hdfc']
      judo                slug-only  -> loses ['judo']
      peoples_first_bank  slug-only  -> loses ['peoples', 'peoplesfirstbank']
      wsfs                intake     -> loses only the lowercase duplicate

  Six of the seven have NO deny-list source file at all — no CLIENT_PROFILE.md,
  no ENGAGEMENT_CONTEXT.md, no inputs/engagement_intake.md. Their entire client
  deny-list IS the directory slug. A migration that only renames directories
  and writes map entries would therefore silently disarm the MCP gate for six
  of seven live engagements while reporting success — the naive fix recreating
  the bug, for the sixth time in this cycle.

  (`.prd/backlog.md` recorded the inverse of this — "wsfs is the risk, the
  other six have filled profiles". The opposite is true: only wsfs is safe.
  Corrected there.)

SO: THE SUPERSET RULE
  For every engagement, this tool resolves the deny-list BEFORE the move and
  AFTER it, and REFUSES to migrate unless the after-set covers the before-set
  (compared case-insensitively — `hdfc` is covered by `HDFC`).

  The mechanism that makes it cover: a `CLIENT_PROFILE.md` carrying a filled
  `- **Name:**` field is written into each opaque directory. That file is
  already the second entry in the design's ordered deny-list sources and is
  read by BOTH resolvers — `denylist.resolve_deny_list` (whole repo, what the
  MCP hook uses) and `denylist.resolve_engagement_deny_list` (one engagement).
  Nothing here teaches the deny-list to read the map: D14 keeps the map out of
  `denylist.py` so `drift_check.py`'s byte-parity with the copy inside
  `mcp-query-guard.py` survives.

  A slug is not a name. `bdo_apa` yields no terms as prose, while
  `BDO Unibank` yields ['BDO', 'BDO Unibank', 'Unibank']. So a client whose
  real name this tool cannot establish is REFUSED, not guessed at — supply it
  with `--name <slug>="<Client Name>"`.

DRY RUN IS THE DEFAULT. Nothing moves without `--apply`.

RESUMABLE AND IDEMPOTENT, without a state file. State is derived from the
filesystem and the map: each opaque directory carries a `.migrated_from`
breadcrumb naming the source it came from, so an interrupted run is recognised
and completed rather than restarted. A state file can itself go stale; the
filesystem cannot disagree with itself.

Standard library only, Python 3.9-clean — a consultant must not need the
Presidio venv to find or migrate their own engagements.
"""
import argparse
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pii import denylist, identity  # noqa: E402  (path set above)

BREADCRUMB = ".migrated_from"
PROFILE_NAME = denylist.CLIENT_PROFILE_NAME
# Detritus that must never keep a client directory alive after its contents
# have moved out.
DISPOSABLE = {".DS_Store", "Thumbs.db"}


class MigrationRefused(Exception):
    """A named, actionable refusal. Never a traceback for the consultant."""


# Same shape identity.py mints: secrets.token_hex(ID_BYTES).
_OPAQUE_RE = re.compile(r"^[0-9a-f]{%d}$" % (identity.ID_BYTES * 2))


# --- discovery -------------------------------------------------------------

def _is_engagement_subdir(path: Path) -> bool:
    return (
        path.is_dir()
        and not path.name.startswith(".")
        and path.name not in ("inputs", "outputs")
    )


def discover(root: Path):
    """Every (client_slug, engagement_name_or_None, source_path) still to move.

    Two live shapes, both real in this repo:
      nested — engagements/<slug>/<YYYY-MM_name>/   (5 of 7)
      flat   — engagements/<slug>/ holding inputs/outputs or loose files
               directly, with no engagement subdirectory (bdo-apa, bdo-mh)

    `engagements/inputs` and `engagements/outputs` are shared legacy staging,
    not clients — `denylist.SKIP_CLIENT_DIRS` excludes the DIRECTORIES
    THEMSELVES from client-slug mining, and they are excluded here for the same
    reason. They still carry client names in their paths; that is reported, not
    migrated.

    Their per-client SUBDIRECTORIES are no longer excluded from the deny-list:
    since 2026-08-30 the resolver descends one level and reads each
    subdirectory's documents (never its name). Before that they were skipped
    wholesale and four real clients were on no deny-list at all.
    """
    base = root / "engagements"
    plans = []
    if not base.is_dir():
        return plans

    for client_dir in sorted(base.iterdir()):
        if not client_dir.is_dir() or client_dir.name.startswith("."):
            continue
        if client_dir.name.lower() in denylist.SKIP_CLIENT_DIRS:
            continue
        if _OPAQUE_RE.match(client_dir.name):
            continue  # already migrated

        subs = [d for d in sorted(client_dir.iterdir()) if _is_engagement_subdir(d)]
        if subs:
            for sub in subs:
                plans.append((client_dir.name, sub.name, sub))
        else:
            plans.append((client_dir.name, None, client_dir))
    return plans


# --- names -----------------------------------------------------------------

def _name_from_profile(client_dir: Path):
    """The client's real name, if an existing CLIENT_PROFILE.md already fills
    it in. Reuses identity.py's own profile reader, so an unfilled
    `[Full legal name]` yields nothing here exactly as it does for the
    deny-list — which is the whole point (`engagements/wsfs` is that case)."""
    profile = client_dir / PROFILE_NAME
    if not profile.is_file():
        return None
    return identity._client_name_from_profile(
        profile.read_text(encoding="utf-8", errors="replace")
    )


def resolve_name(client_slug: str, client_dir: Path, overrides):
    """The client's real name: an explicit --name wins, then a filled profile.

    Returns None when neither supplies one. There is deliberately NO
    slug-derived fallback: `bdo_apa` title-cased is "Bdo Apa", which is not
    this client's name and would put a wrong term on the deny-list while
    looking like it had solved the problem.
    """
    override = overrides.get(client_slug) or overrides.get(client_slug.lower())
    if override:
        return override.strip()
    return _name_from_profile(client_dir)


def parse_name_args(pairs, names_file):
    overrides = {}
    if names_file:
        path = Path(names_file)
        if not path.is_file():
            raise MigrationRefused("names file not found: %s" % path)
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise MigrationRefused(
                    "%s line %d: expected `slug=Client Name`, got %r"
                    % (path, lineno, line)
                )
            slug, _, name = line.partition("=")
            overrides[slug.strip()] = name.strip()
    for pair in pairs or []:
        if "=" not in pair:
            raise MigrationRefused(
                "--name expects `slug=Client Name`, got %r" % pair
            )
        slug, _, name = pair.partition("=")
        overrides[slug.strip()] = name.strip()
    return overrides


# --- the profile that keeps the deny-list armed ----------------------------

# --- deny-list verification ------------------------------------------------

def deny_terms(engagement_dir: Path, client_slug=None):
    return denylist.resolve_engagement_deny_list(engagement_dir, client_slug=client_slug)


def predict_after(root: Path, source: Path, client_name: str, client_slug: str,
                  engagement_name, opaque_id: str):
    """Deny-list terms the engagement WILL have once migrated, computed by
    building the post-migration shape in a scratch directory rather than by
    reasoning about it. The resolver is the authority on what it will find; a
    prediction that reimplements its rules is a prediction that can be wrong
    in exactly the way that matters.
    """
    import tempfile

    with tempfile.TemporaryDirectory(prefix="cortex-migrate-check-") as tmp:
        holder = Path(tmp) / "engagements" / opaque_id
        target = holder / engagement_name if engagement_name else holder
        target.mkdir(parents=True, exist_ok=True)

        # The two deny-list source documents that travel INSIDE the engagement.
        for rel in ("inputs/engagement_intake.md", "ENGAGEMENT_CONTEXT.md"):
            src = source / rel
            if src.is_file():
                dst = target / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(str(src), str(dst))

        existing = source / PROFILE_NAME
        if not existing.is_file():
            existing = source.parent / PROFILE_NAME

        if client_name:
            (holder / PROFILE_NAME).write_text(
                identity.render_client_profile(client_name, client_slug,
                                               existing if existing.is_file() else None,
                                               project_dir=str(root)),
                encoding="utf-8",
            )
        elif existing.is_file():
            # No name to fill in, but an existing profile still travels with
            # the engagement and may carry terms of its own.
            shutil.copyfile(str(existing), str(holder / PROFILE_NAME))
        return deny_terms(target, client_slug=opaque_id)


# --- planning --------------------------------------------------------------

class Step(object):
    def __init__(self, client_slug, engagement_name, source, client_name):
        self.client_slug = client_slug
        self.engagement_name = engagement_name
        self.source = source
        self.client_name = client_name
        self.opaque_id = None
        self.before = set()
        self.after = set()
        self.lost = set()
        self.refusal = None
        self.warning = None
        self.residual = []

    def describe_dest(self):
        tail = "/%s" % self.engagement_name if self.engagement_name else ""
        return "engagements/%s%s" % (self.opaque_id or "<id>", tail)


def _client_named_files(source: Path, client_slug: str, client_name: str):
    """Files whose own NAME carries the client's identity. Renaming the
    directory does not touch these, and this tool will not rename a
    consultant's deliverables behind their back — so they are reported.
    """
    needles = set()
    for raw in (client_slug, client_name):
        squashed = re.sub(r"[^a-z0-9]+", "", (raw or "").lower())
        if len(squashed) >= 3:
            needles.add(squashed)
        for word in re.split(r"[^A-Za-z0-9]+", raw or ""):
            if len(word) >= 3:
                needles.add(word.lower())
    hits = []
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        squashed = re.sub(r"[^a-z0-9]+", "", path.name.lower())
        if any(n in squashed for n in needles):
            hits.append(path)
    return hits


def plan(root: Path, overrides, only=None):
    steps = []
    for client_slug, engagement_name, source in discover(root):
        if only and client_slug not in only:
            continue
        client_dir = source if engagement_name is None else source.parent
        client_name = resolve_name(client_slug, client_dir, overrides)
        step = Step(client_slug, engagement_name, source, client_name)

        step.before = deny_terms(source)
        step.opaque_id = identity._generate_id(
            set(_existing_ids(root)), client_name or "", client_slug
        )
        step.after = predict_after(
            root, source, client_name, client_slug,
            engagement_name, step.opaque_id,
        )
        step.lost = identity.uncovered(step.before, step.after)

        # Whether an engagement may migrate turns on MEASURED term loss, not on
        # whether a name happens to be known. `engagements/wsfs` is the case
        # that forces the distinction: its intake document supplies WSFS and
        # Wilmington independently of the slug, so it loses nothing and a
        # blanket "no name, no migration" rule would block it for no reason.
        # The six others have no source but the slug, and for them the same
        # measurement refuses.
        if step.lost:
            if client_name:
                step.refusal = (
                    "the name %r does not cover these deny-list terms, which "
                    "migrating would DROP: %s. Outbound queries naming the "
                    "client would stop being blocked. Supply a name that "
                    "covers them:  --name %s=\"<Client Name>\""
                    % (client_name, ", ".join(sorted(step.lost)), client_slug)
                )
            else:
                step.refusal = (
                    "no client name, and the directory slug %r is the only "
                    "thing putting %s on this engagement's deny-list. An "
                    "opaque directory removes it, so outbound queries naming "
                    "the client would stop being blocked. Supply the real "
                    "name:  --name %s=\"<Client Name>\""
                    % (client_slug, ", ".join(sorted(step.lost)), client_slug)
                )
        elif not client_name:
            step.warning = (
                "no client name supplied. Nothing is lost from the deny-list "
                "(the terms above come from documents inside the engagement, "
                "not from the slug), so this may migrate — but no "
                "CLIENT_PROFILE.md will be written, which means "
                "`.engagement_map.json` becomes the ONLY record of who this "
                "engagement belongs to. Supplying --name %s=\"<Client Name>\" "
                "writes a profile that rebuild_map() could recover from."
                % client_slug
            )
        step.residual = _client_named_files(source, client_slug, client_name)
        steps.append(step)
    return steps


def _existing_ids(root: Path):
    try:
        return set(identity.load_map(str(root)))
    except identity.MapNotFoundError:
        return set()


# --- reporting -------------------------------------------------------------

def report(root: Path, steps, applying: bool):
    if not steps:
        if not (root / "engagements").is_dir():
            print("No engagements/ directory here — nothing to migrate.")
        else:
            print("Nothing to migrate — every engagement directory is already "
                  "an opaque ID.")
        return 0

    header = "MIGRATION PLAN" if not applying else "MIGRATING"
    print("=" * 72)
    print("  %s — %d engagement(s)" % (header, len(steps)))
    if not applying:
        print("  DRY RUN. Nothing below has been changed.")
    print("=" * 72)

    refused = [s for s in steps if s.refusal]
    for step in steps:
        print("")
        shape = "flat" if step.engagement_name is None else "nested"
        print("  engagements/%s%s   (%s)" % (
            step.client_slug,
            "/%s" % step.engagement_name if step.engagement_name else "",
            shape,
        ))
        print("      ->  %s" % step.describe_dest())
        print("      client name  : %s" % (step.client_name or "— NOT KNOWN —"))
        print("      deny-list now: %s" % (sorted(step.before) or "(none)"))
        print("      deny-list after: %s" % (sorted(step.after) or "(none)"))
        if step.refusal:
            print("      ⛔ REFUSED: %s" % step.refusal)
            continue
        if step.warning:
            print("      ⚠️  %s" % step.warning)
        gained = identity.uncovered(step.after, step.before)
        if gained:
            print("      gained: %s" % sorted(gained))
        if step.residual:
            print("      ⚠️  %d file(s) still carry the client's name in the "
                  "FILENAME — renaming the directory does not change these:"
                  % len(step.residual))
            for path in step.residual[:5]:
                print("           %s" % path.relative_to(root))
            if len(step.residual) > 5:
                print("           ... and %d more" % (len(step.residual) - 5))

    print("")
    print("-" * 72)
    legacy = [d for d in sorted((root / "engagements").iterdir())
              if d.is_dir() and d.name.lower() in denylist.SKIP_CLIENT_DIRS] \
        if (root / "engagements").is_dir() else []
    if legacy:
        print("  OUT OF SCOPE — shared legacy staging, not client directories:")
        for d in legacy:
            children = sorted(c.name for c in d.iterdir() if c.is_dir())
            print("    engagements/%s/  (%s)" % (d.name, ", ".join(children) or "empty"))
        print("    These carry client names in their PATHS, which migrating "
              "these directories is a separate decision about.")
        print("    Their per-client subdirectories ARE covered by the deny-list "
              "(the resolver reads their CLIENT_PROFILE.md; it does not mine "
              "these directory names).")
        print("    Migrating them is a separate decision — they are shared "
              "staging, not engagements.")
        print("")

    if refused:
        print("  %d of %d engagement(s) REFUSED. Nothing will be migrated until "
              "every one resolves." % (len(refused), len(steps)))
        print("  Re-run with the missing names, e.g.:")
        for step in refused:
            print("      --name %s=\"<Client Name>\"" % step.client_slug)
        return 1

    if not applying:
        print("  All %d engagement(s) pass the deny-list superset check." % len(steps))
        print("  To perform the migration, re-run the SAME command with --apply.")
    return 0


# --- execution -------------------------------------------------------------

def _breadcrumb_index(root: Path):
    """opaque_id -> "<slug>/<engagement_name>" for everything already migrated.

    This is how an interrupted run is recognised without a state file.
    """
    index = {}
    base = root / "engagements"
    if not base.is_dir():
        return index
    for child in sorted(base.iterdir()):
        if not child.is_dir() or not _OPAQUE_RE.match(child.name):
            continue
        crumb = child / BREADCRUMB
        if crumb.is_file():
            index[child.name] = crumb.read_text(encoding="utf-8").strip()
    return index


def apply_step(root: Path, step: Step):
    """Move one engagement. Ordered so that every interruption point leaves a
    state the next run can recognise and finish:

      1. map entry      — written FIRST, so no directory can exist unfindable
      2. opaque dir     — created empty
      3. breadcrumb     — names the source, so a resumed run matches them up
      4. CLIENT_PROFILE — the deny-list source, in place BEFORE the content
      5. move           — one `os.rename` per item; a rename is atomic, and
                          moving (not copying) means the bytes are never
                          duplicated and never half-written
      6. verify         — child counts match, deny-list superset holds
      7. remove source  — only once empty, and only after 6 passes
    """
    base = root / "engagements"
    existing = {v: k for k, v in _breadcrumb_index(root).items()}
    crumb_value = "%s/%s" % (step.client_slug, step.engagement_name or "")

    if crumb_value in existing:
        step.opaque_id = existing[crumb_value]          # resuming
    else:
        # `register_engagement` requires a non-empty client. For the
        # lossless-but-unnamed case the slug is the only identifier there is,
        # and recording it beats recording nothing — the map entry is what
        # keeps the directory findable at all.
        step.opaque_id = identity.register_engagement(
            step.client_name or step.client_slug,
            slug=step.client_slug, project_dir=str(root),
        )

    holder = base / step.opaque_id
    holder.mkdir(parents=True, exist_ok=True)
    (holder / BREADCRUMB).write_text(crumb_value + "\n", encoding="utf-8")

    source_profile = step.source / PROFILE_NAME
    if not source_profile.is_file():
        source_profile = step.source.parent / PROFILE_NAME
    if step.client_name:
        (holder / PROFILE_NAME).write_text(
            identity.render_client_profile(step.client_name, step.client_slug,
                                           source_profile if source_profile.is_file() else None,
                                           project_dir=str(root)),
            encoding="utf-8",
        )
    elif source_profile.is_file() and not (holder / PROFILE_NAME).is_file():
        shutil.copyfile(str(source_profile), str(holder / PROFILE_NAME))

    if step.engagement_name:
        target = holder / step.engagement_name
        if step.source.exists():
            expected = len(list(step.source.iterdir()))
            if target.exists():
                _merge_into(step.source, target)
            else:
                os.rename(str(step.source), str(target))
            got = len(list(target.iterdir()))
            if got < expected:
                raise MigrationRefused(
                    "moved %s but it holds %d entries, expected %d — the "
                    "source is left in place; nothing was deleted"
                    % (target, got, expected)
                )
    else:
        target = holder
        if step.source.exists() and step.source != holder:
            _merge_into(step.source, target, skip={BREADCRUMB, PROFILE_NAME})

    _retire_client_dir(step.source if step.engagement_name is None
                       else step.source.parent)
    return target


def _merge_into(source: Path, target: Path, skip=frozenset()):
    target.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir()):
        if child.name in skip:
            continue
        dest = target / child.name
        if dest.exists():
            if child.is_dir():
                _merge_into(child, dest)
                _rmdir_if_empty(child)
            continue
        os.rename(str(child), str(dest))


def _rmdir_if_empty(path: Path):
    try:
        remaining = [c for c in path.iterdir() if c.name not in DISPOSABLE]
    except OSError:
        return
    if remaining:
        return
    for junk in path.iterdir():
        junk.unlink()
    path.rmdir()


def _retire_client_dir(client_dir: Path):
    """Remove the client-named directory once nothing of value is left in it.

    A leftover CLIENT_PROFILE.md is removed only AFTER its content has been
    written into every opaque directory that came from this client — if any
    engagement for this client is still unmigrated, the directory stays.
    """
    if not client_dir.is_dir():
        return
    remaining = [c for c in client_dir.iterdir()
                 if c.name not in DISPOSABLE and c.name != PROFILE_NAME]
    if remaining:
        return
    for child in list(client_dir.iterdir()):
        child.unlink()
    client_dir.rmdir()


# --- CLI -------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="migrate_engagement_ids.sh",
        description="Migrate client-named engagement directories to opaque IDs "
                    "(dry run by default).",
    )
    parser.add_argument("--apply", action="store_true",
                        help="perform the migration (default is a dry run)")
    parser.add_argument("--name", action="append", metavar="SLUG=NAME",
                        help="the client's real name for a directory slug")
    parser.add_argument("--names-file", metavar="PATH",
                        help="file of `slug=Client Name` lines")
    parser.add_argument("--only", action="append", metavar="SLUG",
                        help="migrate only these client slugs")
    parser.add_argument("--project-dir", default=None,
                        help="repo root (default: this script's repo)")
    args = parser.parse_args(argv)

    root = Path(args.project_dir).resolve() if args.project_dir \
        else Path(__file__).resolve().parents[1]

    try:
        overrides = parse_name_args(args.name, args.names_file)
        steps = plan(root, overrides, only=set(args.only or []) or None)
        rc = report(root, steps, applying=False)
        if rc != 0 or not args.apply or not steps:
            return rc

        print("")
        print("=" * 72)
        print("  APPLYING — moving %d engagement(s)" % len(steps))
        print("=" * 72)
        for step in steps:
            target = apply_step(root, step)
            actual = deny_terms(target, client_slug=step.opaque_id)
            lost = identity.uncovered(step.before, actual)
            status = "ok" if not lost else "⚠️  LOST %s" % sorted(lost)
            print("  %-28s -> engagements/%s   %s"
                  % (step.client_slug, step.opaque_id, status))
        print("")
        print("  Done. Find any engagement with:")
        print("      ./scripts/find_engagement.sh <client>")
        return 0
    except MigrationRefused as exc:
        sys.stderr.write("%s\n" % exc)
        return 1
    except identity.EngagementIdentityError as exc:
        sys.stderr.write("%s\n" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
