#!/usr/bin/env bash
#
# setup_pii.sh — One-command installer for Cortex's PII protection tooling
# (Presidio detection/anonymisation, document text extraction, OCR).
#
# This is the single command scripts/../.claude/hooks/pii-preflight.sh prints
# when it detects the PII stack isn't set up. See .design/solution-design-v6.md
# D8 and .design/ux-design-v6.md Flow A.
#
# What it does:
#   1. Finds a Python interpreter in the 3.10-3.13 range Presidio supports
#      (the system `python3` here is 3.9.6 and cannot run it)
#   2. Creates (or reuses) a virtualenv at .venv
#   3. Installs requirements.txt into it
#   4. Downloads the spaCy NER model Presidio uses (en_core_web_lg, ~380 MB)
#   5. Checks for the `tesseract` OCR binary — reports if missing, does NOT
#      install it (it's a large system-level package, and only needed for
#      screenshot ingest — see PRD v6 §3 Out of Scope)
#   6. Self-checks: imports Presidio, loads the spaCy model
#
# Safe to re-run — a second run reuses .venv and skips work already done.
#
# IMPORTANT: Run this from the cortex repo root.

set -uo pipefail

CORTEX_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$CORTEX_ROOT"

VENV_DIR="$CORTEX_ROOT/.venv"
VENV_PY="$VENV_DIR/bin/python"
SPACY_MODEL="en_core_web_lg"

echo "=== Cortex PII protection setup ==="
echo ""

# --- 1. Find a Python interpreter Presidio can run on (3.10-3.13) ---

echo "Looking for a compatible Python interpreter (3.10-3.13)..."

find_compatible_python() {
    local candidates=(python3.13 python3.12 python3.11 python3.10 python3 python)
    local best=""
    local best_minor=-1
    for cand in "${candidates[@]}"; do
        if ! command -v "$cand" >/dev/null 2>&1; then
            continue
        fi
        local ver
        ver="$(command "$cand" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null)" || continue
        local major="${ver%%.*}"
        local minor="${ver##*.}"
        if [ "$major" != "3" ]; then
            continue
        fi
        if [ "$minor" -ge 10 ] 2>/dev/null && [ "$minor" -le 13 ] 2>/dev/null; then
            if [ "$minor" -gt "$best_minor" ]; then
                best="$(command -v "$cand")"
                best_minor="$minor"
            fi
        fi
    done
    echo "$best"
}

PYTHON_BIN="$(find_compatible_python)"

if [ -z "$PYTHON_BIN" ]; then
    cat <<'EOF'

[X] No compatible Python found.

    Cortex's PII protection tooling (Presidio) needs Python 3.10, 3.11,
    3.12, or 3.13. This machine only has other versions on its PATH.

    Install one, then run this script again. The easiest way on a Mac:

        brew install python@3.11

    On Linux, use your package manager (e.g. `apt install python3.11`).
    This script does NOT install a Python interpreter for you — everything
    else it does (creating the environment, installing packages, downloading
    the language model) happens after that one step.

EOF
    exit 1
fi

echo "  Using $PYTHON_BIN ($("$PYTHON_BIN" -c 'import sys; print(sys.version.split()[0])'))"
echo ""

# --- 2. Create or reuse the virtualenv ---

if [ -x "$VENV_PY" ]; then
    echo "Reusing existing environment at .venv"
else
    echo "Creating environment at .venv ..."
    if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
        echo ""
        echo "[X] Could not create .venv. See the error above."
        exit 1
    fi
fi
echo ""

# --- 3. Install requirements.txt ---

echo "Installing dependencies (this can take a few minutes)..."
if ! "$VENV_PY" -m pip install --upgrade pip --quiet; then
    echo "[!] Could not upgrade pip inside .venv — continuing with the version it shipped with."
fi

if ! "$VENV_PY" -m pip install -r "$CORTEX_ROOT/requirements.txt"; then
    echo ""
    echo "[X] Dependency install failed. See the error above and re-run this script"
    echo "    once it's resolved — it's safe to re-run."
    exit 1
fi
echo "  [OK] Dependencies installed"
echo ""

# --- 4. Download the spaCy model Presidio uses for name/entity detection ---

echo "Checking language model ($SPACY_MODEL, ~380 MB)..."
if "$VENV_PY" -c "import spacy; spacy.load('$SPACY_MODEL')" >/dev/null 2>&1; then
    echo "  [OK] Model already present"
else
    echo "  Downloading — this is the slow step, give it a few minutes..."
    if ! "$VENV_PY" -m spacy download "$SPACY_MODEL"; then
        echo ""
        echo "[X] Model download failed. Check your network connection and re-run"
        echo "    this script — it will skip everything already done."
        exit 1
    fi
    echo "  [OK] Model downloaded"
fi
echo ""

# --- 5. Check for tesseract (OCR binary) — report only, never auto-install ---

echo "Checking for the OCR tool (needed for screenshots)..."
if command -v tesseract >/dev/null 2>&1; then
    echo "  [OK] tesseract found ($(command -v tesseract))"
else
    echo "  [!] tesseract not found. Text and document PII protection will still"
    echo "      work fully — screenshots and other images just won't be usable"
    echo "      until this is installed."
    echo ""
    echo "      One command to install it:"
    if [[ "$(uname -s)" == "Darwin" ]]; then
        echo "          brew install tesseract"
    else
        echo "          sudo apt install tesseract-ocr   # or your distro's package manager"
    fi
fi
echo ""

# --- 6. Self-check ---

echo "Running self-check..."
SELF_CHECK_ERR="$("$VENV_PY" -c "
import presidio_analyzer
import presidio_anonymizer
import spacy
spacy.load('$SPACY_MODEL')
print('ok')
" 2>&1)"

if [ "$SELF_CHECK_ERR" = "ok" ]; then
    echo "  [OK] Presidio imports and the language model loads"
    echo ""
    echo "=== Setup complete ==="
    echo ""
    echo "PII protection is ready. Client documents in engagements/*/inputs/"
    echo "will now be scrubbed automatically before Claude reads them."
    if ! command -v tesseract >/dev/null 2>&1; then
        echo ""
        echo "(Screenshots still need tesseract — see above.)"
    fi
    exit 0
else
    echo "  [X] Self-check failed:"
    echo ""
    echo "$SELF_CHECK_ERR" | sed 's/^/      /'
    echo ""
    echo "Re-run this script once resolved — it will skip steps already done."
    exit 1
fi
