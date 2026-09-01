#!/usr/bin/env python3
"""
The identity half of `init_engagement.sh`: mint an opaque engagement ID,
record it in the map, and write the CLIENT_PROFILE.md that keeps the client's
name on the deny-list.

Kept as a file rather than inlined in the shell script because it is the part
that must not go wrong quietly, and a heredoc is a poor place for logic with
three failure modes. `init_engagement.sh` reads two lines from stdout:

    line 1: the opaque engagement ID
    line 2: "Yes" | "No"  — whether this is a new client

Inputs arrive as environment variables (CORTEX_ROOT, CLIENT_SLUG,
ENGAGEMENT_NAME) so nothing client-named is ever passed on a command line,
where it would show up in `ps` output.

Exit codes:  0 ok · 3 the engagement already exists · 1 anything else.

Standard library only, Python 3.9-clean — starting an engagement must never
require the Presidio venv.
"""
import os
import sys
from pathlib import Path

root = Path(os.environ["CORTEX_ROOT"])
slug = os.environ["CLIENT_SLUG"]
name = os.environ["ENGAGEMENT_NAME"]

sys.path.insert(0, str(root / "scripts"))

from pii import identity  # noqa: E402  (path set above)


def main():
    # Does this client already have an engagement by this name? A fresh ID is
    # minted per engagement, so the destination can never collide on disk —
    # the duplicate has to be caught through the map instead. Without this,
    # `init_engagement.sh hdfc 2026-08_retail_renewal` run twice would produce
    # two opaque directories holding two halves of one engagement.
    try:
        prior = identity.search_engagements(slug, project_dir=str(root))
    except identity.MapNotFoundError:
        prior = []          # first engagement on this machine
    except identity.UnknownClientError:
        prior = []          # first engagement for this client

    for record in prior:
        if (Path(record["path"]) / name).is_dir():
            sys.stderr.write(
                "Error: engagement %r already exists for %s.\n"
                "  %s\n"
                "If you want to resume it, cd there. Find it any time with:\n"
                "    ./scripts/find_engagement.sh %s\n"
                % (name, record["client"], Path(record["path"]) / name, slug)
            )
            return 3

    is_new_client = "No" if prior else "Yes"

    # Carry the most recent existing profile forward. CLIENT_PROFILE.md is
    # long-term memory that survives across engagements (its own header says
    # so), and one opaque directory per engagement must not fragment it.
    existing = None
    for record in reversed(prior):
        candidate = Path(record["path"]) / identity.denylist.CLIENT_PROFILE_NAME
        if candidate.is_file():
            existing = candidate
            break

    # Prefer the real client name the carried-forward profile already holds
    # over the directory slug the consultant typed — a filled profile is the
    # better identifier, and it is what keeps the deny-list strong.
    client_name = None
    if existing is not None:
        client_name = identity._client_name_from_profile(
            existing.read_text(encoding="utf-8", errors="replace")
        )

    engagement_id = identity.register_engagement(
        client_name or slug, slug=slug, project_dir=str(root)
    )
    holder = root / "engagements" / engagement_id
    holder.mkdir(parents=True, exist_ok=True)
    (holder / identity.denylist.CLIENT_PROFILE_NAME).write_text(
        identity.render_client_profile(
            client_name or slug, slug, existing, project_dir=str(root)
        ),
        encoding="utf-8",
    )

    print(engagement_id)
    print(is_new_client)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except identity.EngagementIdentityError as exc:
        sys.stderr.write("Error: %s\n" % exc)
        sys.exit(1)
