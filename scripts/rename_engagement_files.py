#!/usr/bin/env python3
"""
rename_engagement_files.py — strip client identifiers out of FILENAMES inside an
engagement.

  DRY RUN BY DEFAULT. Pass --apply to write. --revert undoes an applied run.

WHY THIS EXISTS
  Opaque engagement directories (solution-design-v6.md D6) remove the client's
  name from the DIRECTORY, but not from the files inside it.
  `<Client>_Renewal_Proposal_v8.html` still puts the name in `transcript_path`,
  in `cwd`-relative references, and in the path envelope of any interactive Read
  — which is the leak D6 exists to close, surviving the fix.

  `migrate_engagements.py` reports these and deliberately does not rename them
  ("this tool will not rename a consultant's deliverables behind their back").
  This is the separate, explicit tool that does, with the reversibility that
  makes it safe to run: `engagements/` is gitignored, so there is NO git history
  to recover from, and a rename without a recorded mapping is unrecoverable.

WHAT IT WILL NOT DO, AND WHY THOSE MATTER
  - It does not rewrite the INSIDE of an archive. A `.zip` holding a
    client-named `.html` keeps that name internally; renaming the zip hides the
    leak from a directory listing and not from whoever opens it. Reported.
  - It does not edit a build script's OUTPUT paths. A
    `build_<client>_deck.py` that writes `<Client>_Deck.pptx` will recreate the
    client-named file on its next run, so renaming the script alone is a fix
    that undoes itself. Reported.
  - It refuses any rename that would collide with an existing file, rather than
    overwriting one deliverable with another.

REFERENCES
  Renaming a file that another file links to breaks the link. Every text file in
  the engagement is scanned for the old basenames; matches are rewritten on
  --apply and listed in the dry run. Binary references (inside a .zip, a .pptx,
  a .pdf) cannot be rewritten and are reported instead.

Usage:
    python3 scripts/rename_engagement_files.py                     # plan, all engagements
    python3 scripts/rename_engagement_files.py --only hdfc         # plan, one
    python3 scripts/rename_engagement_files.py --apply
    python3 scripts/rename_engagement_files.py --revert --only hdfc
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import migrate_engagements as M                      # noqa: E402
from pii import denylist as D, identity as I         # noqa: E402

MAP_NAME = ".filename_map.json"
MAP_MODE = 0o600
TEXT_SUFFIXES = {".md", ".html", ".htm", ".txt", ".json", ".yaml", ".yml", ".csv", ".py", ".js", ".css"}
ARCHIVE_SUFFIXES = {".zip", ".gz", ".tar", ".7z", ".rar"}
OPAQUE_TO_BINARY = {".pptx", ".docx", ".xlsx", ".pdf"}


def _needles(client_dir: Path):
    """The identity tokens to strip. Same definition `migrate_engagements.
    _client_named_files` uses to REPORT them, so this tool fixes exactly what
    that one flags — a different definition here would leave a gap between the
    warning and the remedy."""
    prof = client_dir / "CLIENT_PROFILE.md"
    name = ""
    if prof.is_file():
        try:
            name = I._client_name_from_profile(prof.read_text(encoding="utf-8")) or ""
        except OSError:
            name = ""
    needles = set()
    for raw in (client_dir.name, name):
        squashed = re.sub(r"[^a-z0-9]+", "", (raw or "").lower())
        if len(squashed) >= 3:
            needles.add(squashed)
        for word in re.split(r"[^A-Za-z0-9]+", raw or ""):
            if len(word) >= 3:
                needles.add(word.lower())
    return needles


def _strip_name(filename: str, needles) -> str:
    """Remove every needle from a filename and tidy the separators it leaves.

    Operates on the STEM only; the suffix chain (`.html.zip`) is preserved
    exactly, because that is what tells a consultant and the OS what the file is.
    """
    p = Path(filename)
    suffixes = "".join(p.suffixes)
    stem = filename[:len(filename) - len(suffixes)] if suffixes else filename

    for n in sorted(needles, key=len, reverse=True):
        stem = re.sub(re.escape(n), " ", stem, flags=re.I)

    # Tidy: collapse separator runs, drop leading/trailing separators and the
    # stray connectives a removed token leaves behind ("BB &  Managed" -> "BB Managed").
    stem = re.sub(r"[ _\-]*&[ _\-]*", " ", stem)
    stem = re.sub(r"\s+", " ", stem)
    stem = re.sub(r"[ _]*_[ _]*", "_", stem)
    stem = re.sub(r"(^[\s_\-]+)|([\s_\-]+$)", "", stem)
    stem = re.sub(r"_{2,}", "_", stem)
    stem = re.sub(r"-{2,}", "-", stem)
    stem = stem.strip(" _-")
    return (stem + suffixes) if stem else ""


def plan_engagement(client_dir: Path):
    """(renames, collisions, unnameable, archives, generators)"""
    prof = client_dir / "CLIENT_PROFILE.md"
    name = ""
    if prof.is_file():
        try:
            name = I._client_name_from_profile(prof.read_text(encoding="utf-8")) or ""
        except OSError:
            name = ""
    hits = M._client_named_files(client_dir, client_dir.name, name)
    needles = _needles(client_dir)

    renames, collisions, unnameable, archives, generators = [], [], [], [], []
    proposed = {}
    for src in sorted(hits):
        new = _strip_name(src.name, needles)
        if not new or new.startswith("."):
            unnameable.append(src)
            continue
        dst = src.with_name(new)
        if dst == src:
            continue
        if dst.exists() or dst in proposed:
            collisions.append((src, dst))
            continue
        proposed[dst] = src
        renames.append((src, dst))
        if src.suffix.lower() in ARCHIVE_SUFFIXES:
            archives.append(src)
        if src.suffix.lower() == ".py" and src.name.lower().startswith("build"):
            generators.append(src)
    return renames, collisions, unnameable, archives, generators


def find_references(client_dir: Path, renames):
    """Which files mention an old basename. Text ones can be rewritten; binary
    ones cannot and are the honest limit of this tool."""
    olds = {src.name for src, _ in renames}
    text_refs, binary_refs = {}, {}
    for p in client_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in TEXT_SUFFIXES:
            try:
                body = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            found = sorted(o for o in olds if o in body)
            if found:
                text_refs[p] = found
        elif p.suffix.lower() in (ARCHIVE_SUFFIXES | OPAQUE_TO_BINARY):
            # Cannot inspect without unpacking; a same-named sibling is the
            # common case (deck.html + deck.zip) and is worth flagging.
            stem = p.name[:len(p.name) - len("".join(p.suffixes))]
            hit = sorted(o for o in olds if stem and stem in o)
            if hit:
                binary_refs[p] = hit
    return text_refs, binary_refs


def load_map(client_dir: Path):
    f = client_dir / MAP_NAME
    if not f.is_file():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_map(client_dir: Path, mapping):
    f = client_dir / MAP_NAME
    existing = load_map(client_dir)
    existing.update(mapping)
    f.write_text(json.dumps(existing, indent=2, sort_keys=True), encoding="utf-8")
    os.chmod(str(f), MAP_MODE)
    return f


def apply_engagement(client_dir: Path, renames, text_refs):
    mapping = {}
    for src, dst in renames:
        os.rename(str(src), str(dst))
        mapping[str(dst.relative_to(client_dir))] = str(src.relative_to(client_dir))
    for path, olds in text_refs.items():
        # The file may itself have just been renamed.
        target = path
        if not target.exists():
            for src, dst in renames:
                if src == path:
                    target = dst
                    break
        if not target.exists():
            continue
        body = target.read_text(encoding="utf-8", errors="replace")
        for old in olds:
            new = next((d.name for s, d in renames if s.name == old), None)
            if new:
                body = body.replace(old, new)
        target.write_text(body, encoding="utf-8")
    return mapping


def revert_engagement(client_dir: Path):
    """Undo an applied run: filenames AND the references that were rewritten
    with them.

    Restoring only the names would leave every journal entry and link citing a
    file that no longer exists — a revert that leaves the engagement more broken
    than either end state. Both halves move together, in the reverse order they
    were applied (references first, while the new names are still on disk to
    match against).
    """
    mapping = load_map(client_dir)
    if not mapping:
        return 0

    # references first: new basename -> old basename
    basenames = {Path(new_rel).name: Path(old_rel).name
                 for new_rel, old_rel in mapping.items()
                 if Path(new_rel).name != Path(old_rel).name}
    if basenames:
        for f in client_dir.rglob("*"):
            if not f.is_file() or f.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                body = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            updated = body
            for new_name, old_name in basenames.items():
                updated = updated.replace(new_name, old_name)
            if updated != body:
                f.write_text(updated, encoding="utf-8")

    done = 0
    for new_rel, old_rel in sorted(mapping.items()):
        new_p, old_p = client_dir / new_rel, client_dir / old_rel
        if new_p.is_file() and not old_p.exists():
            old_p.parent.mkdir(parents=True, exist_ok=True)
            os.rename(str(new_p), str(old_p))
            done += 1
    if done:
        (client_dir / MAP_NAME).unlink(missing_ok=True)
    return done


def main():
    ap = argparse.ArgumentParser(description="Strip client identifiers from engagement FILENAMES.")
    ap.add_argument("--only", action="append", default=None, help="client slug (repeatable)")
    ap.add_argument("--apply", action="store_true", help="actually rename. Without it, plan only.")
    ap.add_argument("--revert", action="store_true", help="undo an applied run from .filename_map.json")
    args = ap.parse_args()

    root = Path("engagements")
    if not root.is_dir():
        print("no engagements/ directory here", file=sys.stderr)
        return 1

    dirs = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name.lower() in D.SKIP_CLIENT_DIRS:
            continue
        if args.only and d.name not in args.only:
            continue
        dirs.append(d)

    if args.revert:
        total = sum(revert_engagement(d) for d in dirs)
        print("Reverted %d file(s) from %s." % (total, MAP_NAME))
        return 0

    mode = "APPLY" if args.apply else "DRY RUN"
    print("Engagement filename scrub — %s\n" % mode)
    grand = 0
    for d in dirs:
        renames, collisions, unnameable, archives, generators = plan_engagement(d)
        if not (renames or collisions or unnameable):
            continue
        text_refs, binary_refs = find_references(d, renames)
        grand += len(renames)
        print("=== %s — %d rename(s) ===" % (d.name, len(renames)))
        for src, dst in renames:
            print("    %s\n      -> %s" % (src.name, dst.name))
        if collisions:
            print("  ⛔ REFUSED (target exists — would overwrite a deliverable):")
            for src, dst in collisions:
                print("      %s -> %s" % (src.name, dst.name))
        if unnameable:
            print("  ⛔ REFUSED (nothing left after stripping — rename by hand):")
            for src in unnameable:
                print("      %s" % src.name)
        if text_refs:
            print("  ↻ references rewritten in %d text file(s):" % len(text_refs))
            for p, olds in sorted(text_refs.items()):
                print("      %s  (%d)" % (p.name, len(olds)))
        if binary_refs:
            print("  ⚠️  NOT fixed inside these — the name survives in the file's own content:")
            for p in sorted(binary_refs):
                print("      %s" % p.name)
        if archives:
            print("  ⚠️  %d archive(s) renamed on the OUTSIDE only; the client-named "
                  "file INSIDE is untouched." % len(archives))
        if generators:
            print("  ⚠️  %d build script(s) renamed — check their OUTPUT paths, or the "
                  "next run recreates client-named files." % len(generators))
        if args.apply:
            mapping = apply_engagement(d, renames, text_refs)
            f = save_map(d, mapping)
            print("  ✓ applied; reversal map: %s (chmod 600)" % f.name)
        print("")

    print("%d file(s) %s." % (grand, "renamed" if args.apply else "would be renamed"))
    if not args.apply:
        print("Dry run — nothing changed. Re-run with --apply.")
        print("engagements/ is gitignored: the ONLY undo is --revert via %s." % MAP_NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main())
