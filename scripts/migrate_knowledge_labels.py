#!/usr/bin/env python3
"""
migrate_knowledge_labels.py — add the D1 discriminator to labels already
committed in `knowledge/**`.

  DRY RUN BY DEFAULT. Pass --apply to write.

WHY THIS EXISTS
  `.design/knowledge-identity-resolution.md` D1 made the knowledge label
  `[Client-{domain}-{REGION}-{year}-{disc}]`. New harvests get a discriminator;
  the ~200 labels already committed do not, so the corpus carries two shapes and
  the older ones stay ambiguous — a label with no discriminator cannot be told
  apart from another engagement that shares its domain, region and year.

WHY IT NEEDS A BINDING FILE INSTEAD OF WORKING IT OUT
  The discriminator is the first characters of an engagement's OPAQUE ID
  (`pii.identity.label_discriminator`). Deriving it requires knowing which
  engagement produced each historical label, and that binding is not recoverable
  from the repository:

    - `knowledge/**` records the label, never the engagement.
    - `EXTRACTION_REGISTRY.md` records one row per engagement, but its client
      column is now labels too — by design, since the registry is committed.
    - `.engagement_map.json` is gitignored and machine-local.

  Guessing by matching domain/region/year would be exactly wrong: those three
  fields are what collide in the first place, so a guess would silently bind two
  engagements to one ID and cement the defect this is meant to remove. So this
  script REFUSES to guess. Every label it cannot resolve from the binding file is
  reported and left alone.

PREREQUISITE, AND IT IS NOT MET IN A FRESH CLONE
  There must BE opaque engagement IDs. As of 2026-08-30 no engagement has one —
  all live directories are still client-named and `.engagement_map.json` does not
  exist (`.prd/backlog.md`, "ACTION — run the live engagement migration"). Run
  `scripts/migrate_engagement_ids.sh` first; until then this script has nothing
  to bind to and will report every label as unresolved, which is the honest
  result rather than a failure.

THE BINDING FILE
  JSON, `{"<label>": "<opaque engagement id>"}`:

      {
        "[Client-retail-NAM-2025]":      "a3f2beef",
        "[Client-wealth-APAC-2025]":     "deadbe01",
        "[Client-commercial-NAM-2026-a]": "0f1e2d3c"
      }

  It holds labels and IDs — NEVER a client name. Both sides are shape-validated
  on load, so a name cannot be passed in one by accident. The file is the
  consultant's to produce after the engagement migration, on the machine that has
  the map; it is deliberately not committed.

  Hand-assigned stopgap suffixes (`-a`, `-b`, applied during the 2026-08-30 scrub
  where two institutions genuinely collided) are replaced by the real
  discriminator when a binding is supplied for them.

Usage:
    python3 scripts/migrate_knowledge_labels.py --bindings bindings.json
    python3 scripts/migrate_knowledge_labels.py --bindings bindings.json --apply
    python3 scripts/migrate_knowledge_labels.py --bindings bindings.json --root knowledge
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pii import identity  # noqa: E402  - after sys.path setup, stdlib-only

# `[Client-domain-REGION-year]` with an optional existing suffix. The suffix
# group is what tells an already-migrated label from one still to do.
LABEL_RE = re.compile(r"\[Client-([A-Za-z0-9]+)-([A-Za-z0-9]+)-(\d{4})(?:-([A-Za-z0-9]+))?\]")

# Confidence tiers share the `[Client-...]` bracket shape but are not engagement
# labels and must never be rewritten: `[Client-Validated]`, `[Client-Synthetic]`.
# LABEL_RE already excludes them by requiring a 4-digit year, but keep the reason
# recorded — a future loosening of the regex would silently corrupt every tier.

# A real discriminator is exactly the shape `identity.label_discriminator`
# emits: a lowercase-hex prefix of an opaque engagement ID.
DISCRIMINATOR_RE = re.compile(r"[0-9a-f]{%d}" % identity.LABEL_DISCRIMINATOR_CHARS)

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".html", ".csv", ".txt"}
DEFAULT_ROOTS = ("knowledge",)


class BindingError(Exception):
    """A binding file that cannot be trusted. Never fall back to guessing."""


def load_bindings(path):
    """Read and SHAPE-VALIDATE the label -> engagement-id bindings.

    Both sides are validated, which is also what stops a client name being
    supplied in either position: a name matches neither the label pattern nor
    the opaque-ID pattern.
    """
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BindingError("could not read bindings %r: %s" % (path, exc))
    if not isinstance(raw, dict):
        raise BindingError("bindings must be a JSON object of label -> engagement id")

    bindings, bad = {}, []
    for label, eid in raw.items():
        if not LABEL_RE.fullmatch(str(label).strip()):
            bad.append("key %r is not a [Client-...] label" % label)
            continue
        disc = identity.label_discriminator(eid)
        if disc is None:
            bad.append(
                "value %r for %s is not an opaque engagement ID (%d lowercase hex "
                "chars). A discriminator is NEVER derived from a client name or "
                "slug — see identity.client_label."
                % (eid, label, identity.ID_BYTES * 2))
            continue
        bindings[str(label).strip()] = disc
    if bad:
        raise BindingError("invalid bindings:\n  - " + "\n  - ".join(bad))
    return bindings


def iter_text_files(roots):
    for root in roots:
        base = Path(root)
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES:
                yield p


def plan(roots, bindings):
    """Compute the rewrite without touching anything.

    Returns (edits, unresolved, already_done) where edits is
    {path: [(old_label, new_label), ...]}.
    """
    edits, unresolved, already = {}, {}, set()
    for path in iter_text_files(roots):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in LABEL_RE.finditer(text):
            old = m.group(0)
            domain, region, year, suffix = m.groups()
            disc = bindings.get(old)
            if disc is None:
                # No binding. Distinguish a label that is ALREADY migrated from
                # one that still needs a binding, by the SHAPE of its suffix:
                #   4 lowercase hex  -> a real discriminator, already done
                #   anything else    -> a hand-assigned stopgap (`-a`, `-b` from
                #                       the 2026-08-30 scrub) or nothing at all,
                #                       both of which still need a binding.
                # Reporting an already-migrated label as "unresolved" would make
                # a completed migration look permanently unfinished.
                if suffix and DISCRIMINATOR_RE.fullmatch(suffix):
                    already.add(old)
                else:
                    unresolved.setdefault(old, set()).add(str(path))
                continue
            new = "[Client-%s-%s-%s-%s]" % (domain, region, year, disc)
            if new == old:
                already.add(old)
                continue
            edits.setdefault(path, [])
            if (old, new) not in edits[path]:
                edits[path].append((old, new))
    return edits, unresolved, already


def apply_edits(edits):
    changed = 0
    for path, pairs in edits.items():
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
        changed += 1
    return changed


def main():
    ap = argparse.ArgumentParser(
        description="Add the D1 discriminator to labels already in knowledge/.")
    ap.add_argument("--bindings", required=True,
                    help="JSON file of {label: opaque engagement id}")
    ap.add_argument("--root", action="append", default=None,
                    help="tree to rewrite (repeatable; default: knowledge)")
    ap.add_argument("--apply", action="store_true",
                    help="actually write. Without it this is a dry run.")
    args = ap.parse_args()

    roots = args.root or list(DEFAULT_ROOTS)
    try:
        bindings = load_bindings(args.bindings)
    except BindingError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 2

    edits, unresolved, already = plan(roots, bindings)
    n_edits = sum(len(v) for v in edits.values())

    print("Knowledge label migration — %s" % ("APPLY" if args.apply else "DRY RUN"))
    print("  roots:            %s" % ", ".join(roots))
    print("  bindings loaded:  %d" % len(bindings))
    print("  files to change:  %d  (%d distinct label rewrites)" % (len(edits), n_edits))
    print("  already correct:  %d" % len(already))
    print("  UNRESOLVED:       %d" % len(unresolved))

    if edits:
        print("\nRewrites:")
        for path in sorted(edits):
            for old, new in edits[path]:
                print("  %s\n    %s  ->  %s" % (path, old, new))

    if unresolved:
        print("\nUNRESOLVED — no binding supplied, left untouched (this is not a")
        print("failure; supply bindings for these or accept them as ambiguous):")
        for label in sorted(unresolved):
            files = sorted(unresolved[label])
            print("  %s  in %d file(s), e.g. %s" % (label, len(files), files[0]))

    if not args.apply:
        print("\nDry run — nothing written. Re-run with --apply to write.")
        return 0

    if not edits:
        print("\nNothing to do.")
        return 0
    changed = apply_edits(edits)
    print("\nWrote %d file(s)." % changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
