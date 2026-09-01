#!/usr/bin/env bash
#
# find_engagement.sh — Resolve a client name to its engagement director(ies).
#
# Usage:
#   ./scripts/find_engagement.sh <client>          # human-readable listing
#   ./scripts/find_engagement.sh --path <client>   # bare paths, one per line
#
# Examples:
#   ./scripts/find_engagement.sh hdfc
#   ./scripts/find_engagement.sh "peoples first"
#   cd "$(./scripts/find_engagement.sh --path hdfc)"
#
# WHY THIS SCRIPT EXISTS
#   Engagement directories are opaque IDs (`engagements/e7f3a2c1/...`), because
#   the directory name would otherwise put the client's name into every agent
#   prompt (solution-design-v6.md D6). Consultants must never have to know or
#   hand-type an ID — this is the lookup that means they don't.
#
#   Matching is PARTIAL and case-insensitive: "peoples", "Peoples First Bank"
#   and "peoples_first_bank" all resolve.
#
# The ID -> client binding lives ONLY in `.engagement_map.json` (repo root,
# chmod 600, gitignored). It never leaves this machine.
#
# Runs on the SYSTEM python3 — `scripts/pii/identity.py` is stdlib-only and
# 3.9-clean by contract, so looking up an engagement never requires the
# Presidio venv.

set -euo pipefail

CORTEX_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

PATH_ONLY="no"
if [ "${1:-}" = "--path" ]; then
    PATH_ONLY="yes"
    shift
fi

if [ $# -lt 1 ]; then
    echo "Usage: $0 [--path] <client>" >&2
    echo "" >&2
    echo "  client    Client name or slug — partial and case-insensitive." >&2
    echo "  --path    Print bare engagement paths only (for cd/scripting)." >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 hdfc" >&2
    echo "  cd \"\$($0 --path hdfc)\"" >&2
    exit 2
fi

QUERY="$*"

# identity.py raises a NAMED error for every failure (no map, unreadable map,
# no match). Each is caught and reported as one plain line — a consultant must
# never be shown a traceback for typing a client name wrong.
CORTEX_ROOT="$CORTEX_ROOT" QUERY="$QUERY" PATH_ONLY="$PATH_ONLY" python3 - <<'PY'
import os
import sys

root = os.environ["CORTEX_ROOT"]
query = os.environ["QUERY"]
path_only = os.environ["PATH_ONLY"] == "yes"

sys.path.insert(0, os.path.join(root, "scripts"))
from pii import identity  # noqa: E402  (path set above)

try:
    matches = identity.search_engagements(query, project_dir=root)
except identity.MapNotFoundError:
    # NOT the "you lost your map" case identity.py's own message describes.
    # Before migration there simply is no map yet, and the engagement
    # directories are still client-named — so say that, and name the two
    # commands that create entries, rather than telling a consultant with a
    # perfectly healthy repo to restore a backup.
    sys.stderr.write(
        "No engagements are registered yet, so there is nothing to look up.\n"
        "  - to register the engagement directories you already have:  "
        "./scripts/migrate_engagement_ids.sh\n"
        "  - to start a new engagement:                                "
        "./scripts/init_engagement.sh <client> <engagement_name>\n"
    )
    sys.exit(1)
except identity.EngagementIdentityError as exc:
    sys.stderr.write("%s\n" % exc)
    sys.exit(1)

if path_only:
    for m in matches:
        print(m["path"])
    sys.exit(0)

label = "engagement" if len(matches) == 1 else "engagements"
print("%d %s for %r:" % (len(matches), label, query))
for m in matches:
    print("")
    print("  %s  (created %s)" % (m["client"], m["created"] or "unknown"))
    print("    %s" % m["path"])
    # Everything below the opaque directory keeps its ordinary names, so the
    # engagement subdirectory and CLIENT_PROFILE.md are found by looking, not
    # by another map lookup.
    engagement_root = m["path"]
    if not os.path.isdir(engagement_root):
        print("    ⚠️  directory missing — the map has an entry but the "
              "directory is gone")
        continue
    profile = os.path.join(engagement_root, "CLIENT_PROFILE.md")
    if os.path.isfile(profile):
        print("    profile: %s" % profile)
    subs = sorted(
        d for d in os.listdir(engagement_root)
        if os.path.isdir(os.path.join(engagement_root, d))
        and not d.startswith(".")
        and d not in ("inputs", "outputs")
    )
    for sub in subs:
        print("    work:    %s" % os.path.join(engagement_root, sub))
PY
