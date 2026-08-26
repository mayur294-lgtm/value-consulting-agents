#!/usr/bin/env python3
"""
Engagement identity — opaque IDs, the local ID<->client map, and the neutral
pipeline workspace.

WHY THIS MODULE EXISTS
  The engagement directory IS the client's identity. `engagements/hdfc/...`,
  `judo`, `wsfs`, `bdo-apa`, `bank_australia`, `peoples_first_bank`. And
  `scripts/orchestrate.py`'s `compose_prompt` renders `engagement_dir`,
  `outputs_dir` and `transcript_path` into the invocation prompt as VALUES
  (its own docstring says so), while `run_agent` sets `cwd` to that same
  client-named directory.

  So perfect content anonymisation is defeated by the path envelope on every
  single agent invocation: the model is told the client's name in the
  Runtime Parameters table before it reads a single scrubbed byte. This is
  solution-design-v6.md D6, and PRD v6 §"Path anonymisation (both surfaces)".

  Two surfaces, two mechanisms, both in this module:

    1. OPAQUE DIRECTORIES  — `engagements/e7f3a2c1/...` instead of
       `engagements/hdfc/...`. The binding from ID to client lives ONLY in
       `.engagement_map.json` (repo root, chmod 600, gitignored), which never
       leaves the machine.
    2. NEUTRAL WORKSPACE   — even with opaque directories, an INPUT FILENAME
       is client-controlled (`HDFC_Annual_Report.pdf` -> the scrubbed sibling
       `.anon_HDFC_Annual_Report.pdf.md`), and that filename is exactly what
       travels as `transcript_path`. `materialise_workspace()` builds a
       throwaway directory in which EVERY path segment is generated here and
       nothing is inherited from a client-controlled name.

SCOPE OF THIS TICKET (#166)
  Primitives only. Wiring them into `scripts/orchestrate.py` is #167;
  migrating the seven live engagement directories and adding
  `find_engagement.sh` is #168. Nothing in this module imports, reads or
  writes anything under `engagements/` on import.

WHAT AN ID IS, AND IS NOT
  IDs are generated with `secrets.token_hex` — RANDOM, never derived from the
  client's name by any transform. A hash of "hdfc" would be an opaque-looking
  string that a dictionary attack reverses in milliseconds; there are only so
  many banks. The association is STORED, not computed.

  `_resembles_client()` is a belt-and-braces filter, not the security
  property: it regenerates on the vanishingly rare coincidence that a random
  hex ID happens to contain a >=3-character run from the client's own name
  (only a-f/0-9 runs can collide at all — "fed", "cab", "ace", ...).

WHAT NEVER GETS LOGGED
  The map's contents — the client's real name — must never reach a log, a
  journal entry, a telemetry block, or any file under `outputs/`. Two
  structural measures rather than a convention:
    - `Workspace` never holds a client name. It holds paths only, so there is
      nothing for a caller to accidentally serialise.
    - `Workspace.__repr__` prints the NEUTRAL workspace path and nothing else,
      so an ordinary `log(f"... {ws}")` cannot leak the engagement path.

CONSTRAINTS (load-bearing)
  - Standard library only. No Presidio, no spaCy, no third-party imports.
    `scripts/pii/__init__.py`'s IMPORT CONTRACT says `import scripts.pii` must
    not load spaCy or Presidio; this module is imported eagerly there, exactly
    like `denylist`, so it has to stay stdlib-clean.
  - Python 3.9 compatible. The system interpreter here is 3.9.6 and the hooks
    run under it.
  - No silent fallbacks. A missing or unreadable map raises an error NAMING
    the file. Falling back to a client-named path because a lookup failed
    would reintroduce the exact leak this module exists to close.
"""
import json
import os
import re
import secrets
import shutil
import stat
import tempfile
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from . import denylist

__all__ = [
    "MAP_FILENAME",
    "MAP_MODE",
    "ID_BYTES",
    "ANON_PREFIX",
    "WORKSPACE_PREFIX",
    "EngagementIdentityError",
    "MapNotFoundError",
    "MapUnreadableError",
    "UnknownEngagementIdError",
    "UnknownClientError",
    "CopyBackInterrupted",
    "Workspace",
    "repo_root",
    "map_path",
    "load_map",
    "register_engagement",
    "client_for_id",
    "ids_for_client",
    "engagement_root",
    "rebuild_map",
    "materialise_workspace",
]

MAP_FILENAME = ".engagement_map.json"
MAP_MODE = 0o600          # owner read/write only — this file binds ID -> client
ID_BYTES = 4              # -> 8 hex characters
ANON_PREFIX = ".anon_"    # scripts/pii/ingest.py + scripts/anonymize_transcript.py
WORKSPACE_PREFIX = "cortex-ws-"

_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_BRACKET_SEGMENT_RE = re.compile(r"\[[^\]]*\]")
_MAX_ID_ATTEMPTS = 64
_MIN_RESEMBLANCE = 2      # see _resembles_client for why 2 and not 1 or 3


# --- errors ----------------------------------------------------------------

class EngagementIdentityError(Exception):
    """Base for every failure in this module.

    Every subclass message NAMES the file or directory involved. A consultant
    who has lost their map has to be told which file to restore, and a caller
    must never be able to mistake a lookup failure for "no mapping needed" and
    quietly carry on with a client-named path.
    """


class MapNotFoundError(EngagementIdentityError):
    """`.engagement_map.json` does not exist."""


class MapUnreadableError(EngagementIdentityError):
    """`.engagement_map.json` exists but cannot be read or parsed."""


class UnknownEngagementIdError(EngagementIdentityError):
    """The map exists but holds no entry for this ID."""


class UnknownClientError(EngagementIdentityError):
    """The map exists but holds no entry for this client."""


class CopyBackInterrupted(EngagementIdentityError):
    """Copy-back failed DURING the publish phase — see `Workspace.copy_back`.

    Carries `staging_dir` (where every produced file still is, intact),
    `published` and `pending` so the caller can tell the consultant exactly
    what to do. The staging directory is deliberately NOT deleted when this is
    raised: deliverables must never be stranded somewhere only this process
    knew about.
    """

    def __init__(self, message, staging_dir, published, pending):
        EngagementIdentityError.__init__(self, message)
        self.staging_dir = Path(staging_dir)
        self.published = list(published)
        self.pending = list(pending)


# --- the map ---------------------------------------------------------------

def repo_root() -> Path:
    """The cortex repo root — `scripts/pii/identity.py` -> up two levels."""
    return Path(__file__).resolve().parents[2]


def map_path(project_dir=None) -> Path:
    """Absolute path to `.engagement_map.json`.

    `project_dir` exists so tests and the eval rubric can point at a tempdir;
    production callers pass nothing and get the repo root.
    """
    base = Path(project_dir) if project_dir is not None else repo_root()
    return base / MAP_FILENAME


def load_map(project_dir=None) -> Dict[str, dict]:
    """Read `.engagement_map.json` and return `{id: {client, slug, created}}`.

    Raises `MapNotFoundError` when the file is absent and `MapUnreadableError`
    when it exists but cannot be read or parsed — NEVER an empty dict for
    either case. An empty-dict fallback is indistinguishable from "no
    engagements registered", and a caller that cannot tell those apart will
    happily fall back to a client-named path, which is the leak.
    """
    path = map_path(project_dir)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise MapNotFoundError(
            "engagement map not found: %s — every engagement directory is an "
            "opaque ID and this file is the only thing that says which client "
            "each one belongs to. Restore it from a local backup, or rebuild "
            "what can be recovered with pii.identity.rebuild_map()." % path
        )
    except OSError as exc:
        raise MapUnreadableError(
            "engagement map could not be read: %s (%s: %s)"
            % (path, type(exc).__name__, exc)
        )

    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise MapUnreadableError(
            "engagement map is not valid JSON: %s (%s). Fix or restore the "
            "file — it is not regenerated automatically." % (path, exc)
        )

    if not isinstance(data, dict):
        raise MapUnreadableError(
            "engagement map has the wrong shape: %s holds %s, expected an "
            'object of {"<id>": {"client": ..., "slug": ..., "created": ...}}'
            % (path, type(data).__name__)
        )

    for key, record in data.items():
        if not isinstance(record, dict) or "client" not in record:
            raise MapUnreadableError(
                "engagement map entry %r is malformed in %s — every entry must "
                'be an object carrying at least a "client" field' % (key, path)
            )
    return data


def _write_map(data, project_dir=None) -> Path:
    """Persist the map, chmod 600, replacing atomically.

    Written to a sibling temp file and `os.replace`d so an interrupted write
    can never leave a truncated map — which `load_map` would (correctly)
    refuse to parse, locking the consultant out of every engagement at once.
    """
    path = map_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=MAP_FILENAME + ".", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_name, MAP_MODE)
        os.replace(tmp_name, str(path))
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    # Re-assert the mode: an existing file replaced in place keeps the NEW
    # inode's bits (set above), but be explicit rather than rely on that.
    os.chmod(str(path), MAP_MODE)
    return path


def _slugify(value: str) -> str:
    return _ALNUM_RE.sub("_", (value or "").strip().lower()).strip("_")


def _resembles_client(candidate: str, *needles) -> bool:
    """True when `candidate` contains any run of `_MIN_RESEMBLANCE` or more
    characters taken from a client identifier.

    NOT the security property — that is `secrets.token_hex`, which never looks
    at the client's name at all. This only removes the coincidence where a
    random hex ID happens to spell part of the name it is meant to hide
    ("fed", "cab", "ace", "dade", ... are all reachable from [0-9a-f]).

    The floor is 2, not 3, so the ID satisfies the plain reading of "contains
    no substring of the client name" rather than a hedged version of it — a
    two-character run carries no real information, but arguing that is worse
    than just not producing one. It is not 1: a single character would make
    generation impossible for any client name containing three or more hex
    letters, which is most of them.

    Cost of the tighter floor, for an 8-hex-character ID (7 adjacent pairs
    out of 256 possible): a long name might ban ~25 pairs, giving roughly a
    50% regeneration rate and ~2 attempts on average — comfortably inside
    `_MAX_ID_ATTEMPTS`, which raises a NAMED error rather than reusing an ID
    if it is ever exhausted.
    """
    cand = _ALNUM_RE.sub("", candidate.lower())
    for needle in needles:
        text = _ALNUM_RE.sub("", (needle or "").lower())
        if len(text) < _MIN_RESEMBLANCE:
            continue
        for size in range(_MIN_RESEMBLANCE, len(text) + 1):
            for start in range(0, len(text) - size + 1):
                if text[start:start + size] in cand:
                    return True
    return False


def _generate_id(taken, *needles) -> str:
    for _ in range(_MAX_ID_ATTEMPTS):
        candidate = secrets.token_hex(ID_BYTES)
        if candidate in taken:
            continue
        if _resembles_client(candidate, *needles):
            continue
        return candidate
    raise EngagementIdentityError(
        "could not generate an opaque engagement ID after %d attempts — this "
        "means the map is implausibly full or the client name collides with "
        "almost every hex string; widen ID_BYTES rather than reusing an ID"
        % _MAX_ID_ATTEMPTS
    )


def register_engagement(client, slug=None, project_dir=None, created=None) -> str:
    """Mint a NEW opaque ID for one engagement and record it in the map.

    Returns the ID. The map is created (chmod 600) if it does not exist yet —
    this is the one path that may create it, and it is explicit.

    ONE ID PER ENGAGEMENT, NOT PER CLIENT. A second engagement for the same
    client gets its own, distinct ID, and both resolve back to that client via
    `client_for_id` / `ids_for_client`. Reusing one ID across engagements would
    make the ID a stable client pseudonym — the same identifier appearing in
    prompts across months of unrelated work, which is precisely the correlatable
    handle opaque directories exist to avoid.
    """
    client = (client or "").strip()
    if not client:
        raise EngagementIdentityError(
            "register_engagement: a client name is required (it is what the "
            "opaque ID stands for)"
        )
    resolved_slug = _slugify(slug) if slug else _slugify(client)

    try:
        data = load_map(project_dir)
    except MapNotFoundError:
        data = {}
    # MapUnreadableError deliberately propagates: a map we cannot parse must
    # not be silently overwritten with a fresh one holding a single entry.

    engagement_id = _generate_id(set(data), client, resolved_slug)
    data[engagement_id] = {
        "client": client,
        "slug": resolved_slug,
        "created": (created or date.today().isoformat()),
    }
    _write_map(data, project_dir)
    return engagement_id


def client_for_id(engagement_id, project_dir=None) -> Dict[str, str]:
    """ID -> `{"client", "slug", "created"}`. The direction the deny-list and
    final deliverable naming need.

    Raises `UnknownEngagementIdError` (naming the map file) for an ID the map
    does not hold. There is deliberately no `default=` parameter: a caller that
    could not resolve an ID has no business guessing.
    """
    data = load_map(project_dir)
    record = data.get(str(engagement_id))
    if record is None:
        raise UnknownEngagementIdError(
            "no entry for engagement ID %r in %s — the directory exists but "
            "nothing binds it to a client. Restore the map from a local "
            "backup, or run pii.identity.rebuild_map() to recover what the "
            "engagement's own CLIENT_PROFILE.md still knows."
            % (engagement_id, map_path(project_dir))
        )
    return dict(record)


def ids_for_client(client, project_dir=None) -> List[str]:
    """Client name OR slug -> every engagement ID registered for it, oldest
    first. The direction `find_engagement.sh` needs (#168).

    Matching is case-insensitive and slug-normalised, so "HDFC", "hdfc" and
    "  HDFC " all resolve. Raises `UnknownClientError` when nothing matches —
    an empty list would be indistinguishable from "this client has no
    engagements", and the caller would have no way to tell a typo from a
    genuinely new client.
    """
    data = load_map(project_dir)
    wanted = _slugify(client)
    matches = [
        (record.get("created") or "", eid)
        for eid, record in data.items()
        if _slugify(record.get("client", "")) == wanted
        or _slugify(record.get("slug", "")) == wanted
    ]
    if not matches:
        raise UnknownClientError(
            "no engagement registered for client %r in %s"
            % (client, map_path(project_dir))
        )
    return [eid for _created, eid in sorted(matches)]


def engagement_root(engagement_id, project_dir=None) -> Path:
    """`<project_dir>/engagements/<id>` — the opaque directory an ID names.

    Resolves through the map first, so an unregistered ID raises rather than
    handing back a path that looks plausible. The directory's INTERNAL shape
    (`inputs/`, `outputs/`, `ENGAGEMENT_JOURNAL.md`, `.engagement_session_id`)
    is unchanged by this ticket and unchanged by #168.
    """
    client_for_id(engagement_id, project_dir)  # raises if unknown
    base = Path(project_dir) if project_dir is not None else repo_root()
    return base / "engagements" / str(engagement_id)


# --- recovery --------------------------------------------------------------

def _client_name_from_profile(text: str) -> Optional[str]:
    """Pull a client's real name out of a CLIENT_PROFILE.md body.

    Reuses `denylist`'s two PUBLIC label regexes rather than inventing a third
    parser — the profile-only bare `**Name:**` form plus the general
    `Client Name:` / `Institution:` / `Organisation:` forms. Unfilled template
    placeholders (`[Full legal name]`) yield nothing, exactly as they do for
    the deny-list.
    """
    for label_re in (denylist.CLIENT_PROFILE_LABEL_LINE_RE, denylist.LABEL_LINE_RE):
        for match in label_re.finditer(text):
            value = match.group(1).strip(" \t*_")
            value = _BRACKET_SEGMENT_RE.sub(" ", value).strip().strip(".,;:*_")
            if value:
                return value
    return None


def rebuild_map(project_dir=None, apply=False) -> Dict[str, object]:
    """Best-effort recovery of a lost `.engagement_map.json`.

    THE DECISION (recorded here because the ticket asked for it explicitly):
    a rebuild path IS worth providing, but only a conservative, reporting one.

    The map is a genuine single point of failure — lose it and every
    engagement is an opaque directory whose owner is unknown. But the
    engagement directory still contains `CLIENT_PROFILE.md`, and that file's
    "## Client Identity" section holds the client's legal name. So recovery
    is possible, and leaving a consultant to open seven directories by hand
    would be a poor answer.

    What it will NOT do:
      - overwrite an existing entry (recovery never contradicts a surviving
        record; the map on disk is always more authoritative than a re-read)
      - invent a name. An unfilled or missing profile is REPORTED as
        unrecovered, never guessed from the directory name or the file tree.
      - write anything unless `apply=True`. The default is a dry run.

    Returns `{"recovered": {id: {...}}, "unrecovered": [id, ...],
    "existing": [id, ...], "applied": bool, "map": <path>}`.
    """
    base = Path(project_dir) if project_dir is not None else repo_root()
    root = base / "engagements"
    try:
        existing = load_map(project_dir)
    except MapNotFoundError:
        existing = {}

    recovered = {}
    unrecovered = []
    if root.is_dir():
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            if child.name.lower() in denylist.SKIP_CLIENT_DIRS:
                continue
            if child.name in existing:
                continue
            name = None
            for profile in sorted(child.rglob(denylist.CLIENT_PROFILE_NAME)):
                name = _client_name_from_profile(
                    profile.read_text(encoding="utf-8", errors="replace")
                )
                if name:
                    break
            if not name:
                unrecovered.append(child.name)
                continue
            recovered[child.name] = {
                "client": name,
                "slug": _slugify(name),
                "created": date.fromtimestamp(child.stat().st_mtime).isoformat(),
            }

    if apply and recovered:
        merged = dict(existing)
        merged.update(recovered)
        _write_map(merged, project_dir)

    return {
        "recovered": recovered,
        "unrecovered": unrecovered,
        "existing": sorted(existing),
        "applied": bool(apply and recovered),
        "map": str(map_path(project_dir)),
    }


# --- the neutral workspace -------------------------------------------------

def _artifact_key_and_suffix(name):
    """Split an `.anon_` artifact filename into (source key, artifact suffix).

    The naming rule is `scripts/pii/ingest.py`'s OUTPUT NAMING:
        transcript_1.md -> .anon_transcript_1.md      (plain text facade)
        report.pdf      -> .anon_report.pdf.md        (document sidecar)
        shot.png        -> .anon_shot.png.md          (OCR sidecar)
                        +  .anon_shot.png.png         (redacted copy)

    Stripping only the FINAL suffix gives "shot.png" for both image artifacts,
    so the sidecar and its redacted copy share one key and therefore get one
    workspace index — they must stay a pair.
    """
    rest = name[len(ANON_PREFIX):]
    suffix = Path(rest).suffix
    key = rest[: len(rest) - len(suffix)] if suffix else rest
    return key, suffix


class Workspace(object):
    """A throwaway directory in which no path segment came from the client.

    Layout::

        <workspace>/
            inputs/
                .anon_input_01.md      <- renamed from .anon_<client name>.pdf.md
                .anon_input_02.md      <- OCR sidecar   ) same source image,
                .anon_input_02.png     <- redacted copy ) one index
            outputs/                   <- empty; agents write here

    Deliberately holds NO client name in any attribute. `engagement_dir` is a
    path (needed by `copy_back`); nothing here is read from the map, so there
    is nothing for a caller to serialise into a journal or telemetry block.
    """

    __slots__ = ("path", "inputs", "outputs", "engagement_dir", "input_names")

    def __init__(self, path, engagement_dir, input_names):
        self.path = Path(path)
        self.inputs = self.path / "inputs"
        self.outputs = self.path / "outputs"
        self.engagement_dir = Path(engagement_dir)
        # {neutral workspace filename: original artifact Path}. IN MEMORY ONLY —
        # the original filenames are client-controlled, so this is never written
        # into the workspace (an agent could read it) and never logged.
        self.input_names = dict(input_names)

    def __repr__(self):
        # The neutral path ONLY. `engagement_dir` is client-named and this
        # object lands in ordinary f-string logging, so it must not appear.
        return "<Workspace %s>" % self.path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # Cleaned up only on a clean exit. An exception mid-run means agent
        # output may still be sitting in outputs/ un-copied-back; deleting it
        # here would destroy work the consultant could otherwise recover.
        if exc_type is None:
            self.cleanup()
        return False

    # -- copy-back ---------------------------------------------------------

    def copy_back(self):
        """Return everything produced under `<workspace>/outputs/` to the real
        engagement's `outputs/`, preserving relative structure.

        THE ATOMICITY GUARANTEE (stated precisely, because "atomic" alone is
        not a guarantee):

          Phase 1 — every file is copied into a staging directory created
          INSIDE the engagement directory, i.e. on the same filesystem as
          `outputs/`. All the expensive, failure-prone I/O lives here: reads
          from the workspace, writes to disk, running out of space. If ANY of
          it fails — including a KeyboardInterrupt — the staging directory is
          removed and `outputs/` is byte-for-byte untouched. Nothing is
          stranded: the workspace still holds every file.

          Phase 2 — each staged file is moved into place with `os.replace`,
          which on POSIX is an atomic rename within one filesystem. Individual
          files therefore never appear truncated or half-written; a reader sees
          either the old file or the new one.

        So: `outputs/` is never left half-WRITTEN. It CAN be left half-
        PUBLISHED if phase 2 is interrupted — a rename-only phase with no data
        transfer, so the window is small, but it is not zero and pretending
        otherwise would be dishonest. When that happens `CopyBackInterrupted`
        is raised, the staging directory is deliberately KEPT (it still holds
        every not-yet-published file), and the exception names it along with
        what was published and what is pending. Re-running `copy_back()` is
        also safe — it is idempotent, since the source of truth is the
        workspace, not the staging copy.

        Merge, not replace: files already in `outputs/` that the workspace did
        not produce are left alone. A directory swap would delete the
        checkpoint files the orchestrator writes host-side.
        """
        dest = self.engagement_dir / "outputs"
        files = sorted(p for p in self.outputs.rglob("*") if p.is_file())
        if not files:
            return {"published": [], "count": 0}

        dest.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".copyback_", dir=str(self.engagement_dir)))

        # Phase 1 — all the real I/O, none of it touching outputs/.
        try:
            for src in files:
                rel = src.relative_to(self.outputs)
                target = staging / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(target))
        except BaseException:
            # BaseException, not Exception: a Ctrl-C here must also leave
            # outputs/ untouched rather than abandoning a half-filled staging
            # directory next to the consultant's deliverables.
            shutil.rmtree(str(staging), ignore_errors=True)
            raise

        # Phase 2 — metadata-only atomic renames, same filesystem.
        published = []
        pending = [str(p.relative_to(self.outputs)) for p in files]
        try:
            for src in files:
                rel = src.relative_to(self.outputs)
                (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                os.replace(str(staging / rel), str(dest / rel))
                published.append(str(rel))
                pending.remove(str(rel))
        except BaseException as exc:
            raise CopyBackInterrupted(
                "copy-back was interrupted while publishing to %s (%s: %s). "
                "%d file(s) published, %d still staged. NOTHING IS LOST — the "
                "remaining files are intact in %s, and re-running copy_back() "
                "republishes from the workspace."
                % (dest, type(exc).__name__, exc, len(published), len(pending), staging),
                staging, published, pending,
            )

        shutil.rmtree(str(staging), ignore_errors=True)
        return {"published": published, "count": len(published)}

    def cleanup(self):
        """Remove the workspace. Safe to call twice."""
        shutil.rmtree(str(self.path), ignore_errors=True)


def materialise_workspace(engagement_dir, workspace_root=None) -> Workspace:
    """Build a neutrally-named working directory for one engagement run.

    ONLY `.anon_` artifacts are copied in, and every one of them is RENAMED.
    Both halves are load-bearing:

      - only `.anon_`: a raw `inputs/` file is unscrubbed client material by
        definition, and `engagement_intake.md` / `CLIENT_PROFILE.md` /
        `ENGAGEMENT_JOURNAL.md` are deny-list SOURCES — they exist to hold the
        client's name. None of them may enter a directory an agent runs in.
        (If a step needs intake context, #167 must scrub it into an `.anon_`
        artifact first; there is no exemption here for it.)

      - renamed: an `.anon_` artifact's filename embeds the RAW filename
        (`.anon_HDFC_Annual_Report.pdf.md`), and that filename is precisely
        what `compose_prompt` renders as `transcript_path`. Copying the
        artifacts under their own names would leave the client's name in the
        prompt after all this work. Names become `.anon_input_NN<suffix>`,
        assigned here, derived from nothing the client controls. A sidecar and
        its redacted image copy share one index so they stay a pair.

    The workspace lives in the system temp directory by default (`mkdtemp`,
    mode 0700, random name). Pass `workspace_root` to place it elsewhere — that
    root must itself be neutral, since this function can only guarantee the
    segments it creates.

    One workspace per RUN, not per step: agents accumulate their output in
    `<workspace>/outputs/`, which starts empty, and `copy_back()` returns it at
    the end. Seeding it with the engagement's existing outputs is deliberately
    not offered — those filenames are not generated here either.
    """
    engagement_dir = Path(engagement_dir).resolve()
    if not engagement_dir.is_dir():
        raise EngagementIdentityError(
            "cannot materialise a workspace: %s is not a directory" % engagement_dir
        )

    src_inputs = engagement_dir / "inputs"
    artifacts = []
    if src_inputs.is_dir():
        # Recursive: a consultant may have foldered their inputs. The directory
        # NAMES are dropped entirely (they are client-controlled too) — the
        # workspace's inputs/ is flat, and the index makes names unique.
        artifacts = sorted(
            p for p in src_inputs.rglob("*")
            if p.is_file() and p.name.startswith(ANON_PREFIX)
        )

    # Group by source key so an image's sidecar and its redacted copy get one
    # index. Sorted for determinism.
    index_for = {}
    for artifact in artifacts:
        key, _suffix = _artifact_key_and_suffix(artifact.name)
        if key not in index_for:
            index_for[key] = len(index_for) + 1

    root = Path(tempfile.mkdtemp(prefix=WORKSPACE_PREFIX,
                                 dir=str(workspace_root) if workspace_root else None))
    ws_inputs = root / "inputs"
    ws_outputs = root / "outputs"
    ws_inputs.mkdir()
    ws_outputs.mkdir()

    input_names = {}
    try:
        for artifact in artifacts:
            key, suffix = _artifact_key_and_suffix(artifact.name)
            neutral = "%sinput_%02d%s" % (ANON_PREFIX, index_for[key], suffix)
            shutil.copy2(str(artifact), str(ws_inputs / neutral))
            input_names[neutral] = artifact
    except BaseException:
        shutil.rmtree(str(root), ignore_errors=True)
        raise

    # mkdtemp already gives 0700; assert it rather than assume, since the
    # workspace holds scrubbed-but-still-sensitive client material.
    os.chmod(str(root), stat.S_IRWXU)
    return Workspace(root, engagement_dir, input_names)
