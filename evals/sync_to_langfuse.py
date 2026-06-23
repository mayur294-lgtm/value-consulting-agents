#!/usr/bin/env python3
"""Mirror the git-authored evals INTO Langfuse (git stays the source of truth).

Pushes:
  • judge prompts  evals/rubrics/judge/prompts/*.md  ->  Langfuse managed prompts
                   (name "cortex-eval/<judge>", label "production", versioned)
  • golden cases   PII-safe files under evals/goldens/ ->  Langfuse datasets
                   (one dataset per deliverable type, golden + negative items)

So Langfuse hosts the same evals (for the dashboard + auto-scoring live production
traces), while the rulebook + CI gate stay in git. Run in CI on merge to main so
Langfuse always mirrors main.

PII boundary: only files UNDER evals/goldens/ are synced. Engagement goldens
(engagements/** — gitignored, client PII) are intentionally NOT pushed to Cloud.

Needs LANGFUSE_* in env (or evals/.env). No-op with a clear message if absent.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from run_experiment import _load_dotenv  # noqa: E402

PROMPTS = HERE / "rubrics" / "judge" / "prompts"


def _client():
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        print("No LANGFUSE_* keys in env — skipping sync (set evals/.env).")
        return None
    try:
        from langfuse import Langfuse
    except ImportError:
        print("langfuse SDK not installed — `pip install langfuse`. Skipping.")
        return None
    return Langfuse()


def _sync_prompts(lf) -> int:
    n = 0
    for f in sorted(PROMPTS.glob("*.md")):
        name = f"cortex-eval/{f.stem}"
        body = f.read_text()
        # Skip if the production version is already identical (avoid version spam).
        try:
            existing = lf.get_prompt(name, label="production", cache_ttl_seconds=0)
            if getattr(existing, "prompt", None) == body:
                print(f"  = {name} (unchanged)")
                continue
        except Exception:
            pass
        lf.create_prompt(name=name, prompt=body, labels=["production"], type="text",
                         tags=["cortex-eval", "judge"],
                         commit_message="sync from git evals/rubrics/judge/prompts")
        print(f"  + {name} (new version)")
        n += 1
    return n


def _sync_datasets(lf) -> int:
    """Sync PII-safe golden + negative cases under evals/goldens/ as datasets."""
    import yaml
    reg = yaml.safe_load((HERE / "registry.yaml").read_text())
    count = 0
    for dname, spec in reg.get("deliverables", {}).items():
        items = []
        for kind in ("goldens", "negatives"):
            for rel in spec.get(kind, []):
                p = (ROOT / rel)
                # PII boundary: only sync files inside evals/goldens/
                if "evals/goldens" not in rel or not p.exists():
                    continue
                items.append((rel, p.read_text(errors="replace"),
                              "pass" if kind == "goldens" else "fail"))
        if not items:
            continue
        ds = f"cortex-{dname}"
        lf.create_dataset(name=ds, description=f"Golden + negative cases for {dname} eval",
                          metadata={"source": "git evals/goldens", "threshold": spec.get("threshold")})
        for rel, content, expect in items:
            lf.create_dataset_item(dataset_name=ds, input={"path": rel, "content": content[:50000]},
                                   expected_output={"verdict": expect},
                                   metadata={"expect": expect}, id=rel)
            print(f"  + {ds} <- {rel} (expect {expect})")
            count += 1
    return count


def main() -> int:
    _load_dotenv()
    lf = _client()
    if lf is None:
        return 0
    print("Syncing judge prompts -> Langfuse:")
    p = _sync_prompts(lf)
    print("Syncing golden datasets -> Langfuse:")
    d = _sync_datasets(lf)
    lf.flush()
    print(f"\nDone. {p} prompt version(s), {d} dataset item(s) synced. git remains source of truth.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
