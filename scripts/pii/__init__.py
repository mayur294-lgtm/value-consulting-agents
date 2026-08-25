"""
scripts.pii — Cortex's PII detection and reversible-pseudonymisation package.

    from scripts.pii import denylist          # stdlib only, safe anywhere
    from scripts.pii import anonymize_text    # pulls in Presidio + spaCy

IMPORT CONTRACT (verified, not aspirational)
  `import scripts.pii` MUST NOT load spaCy or Presidio.

  Why it matters: `scripts/artifact_boundary.py` and the `.claude/hooks/`
  scripts run under the SYSTEM interpreter, which is Python 3.9.6 here.
  Presidio needs 3.10-3.13 and lives in `.venv` (see `scripts/setup_pii.sh`
  and solution-design-v6.md D8/D12). If merely importing this package pulled
  in Presidio, every one of those callers would blow up at import time —
  and for a PreToolUse hook that means exiting in the way Claude Code treats
  as NON-blocking, i.e. failing open in a control whose job is failing
  closed.

  So: `denylist` is imported eagerly (standard library only, 3.9-clean), and
  everything from `engine` is resolved lazily through module `__getattr__`
  (PEP 562) on first attribute access. Nothing heavyweight is touched until
  a caller actually asks for it.

  There is a regression check for this — see `scripts/pii/drift_check.py`
  and the ticket's verification steps: after `import scripts.pii`, neither
  `spacy` nor `presidio_analyzer` may appear in `sys.modules`.
"""
import importlib

from . import denylist  # noqa: F401  — stdlib only; see IMPORT CONTRACT above

__all__ = [
    "denylist",
    # --- lazily resolved from .engine (Presidio + spaCy) ---
    "engine",
    "PIISession",
    "anonymize_text",
    "deanonymize_text",
    "build_mapping_file",
    "flatten_mapping",
    "PLACEHOLDER_RE",
]

# Attribute name -> the submodule it lives in. Kept explicit rather than
# "try every submodule" so a typo raises AttributeError instead of silently
# importing the world.
_LAZY = {
    "engine": None,  # the module itself
    "PIISession": "engine",
    "anonymize_text": "engine",
    "deanonymize_text": "engine",
    "build_mapping_file": "engine",
    "flatten_mapping": "engine",
    "PLACEHOLDER_RE": "engine",
}


def __getattr__(name):
    """PEP 562 lazy attribute resolution — the mechanism that keeps Presidio
    and spaCy out of `import scripts.pii`."""
    if name not in _LAZY:
        raise AttributeError("module %r has no attribute %r" % (__name__, name))
    submodule = _LAZY[name]
    if submodule is None:
        module = importlib.import_module("." + name, __name__)
        globals()[name] = module
        return module
    module = importlib.import_module("." + submodule, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(list(globals().keys()) + __all__))
