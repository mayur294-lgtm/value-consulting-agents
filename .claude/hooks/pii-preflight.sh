#!/bin/bash
# PII protection preflight — SessionStart
#
# Checks whether Cortex's PII-scrubbing tooling (Presidio + the spaCy model
# + the OCR binary) is installed, and if not, tells the consultant in plain
# language what's missing and the one command that fixes it. See
# .design/ux-design-v6.md Flow A for the copy this implements, and the Copy
# Rules at the bottom of that doc (no tool names, consequence before
# instruction, one command, never blocks).
#
# Modeled on auto-branch.sh: defensive, silent on success, ALWAYS exit 0 —
# this hook must never fail or block a session, only inform.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_DIR" 2>/dev/null || exit 0

VENV_PY="$PROJECT_DIR/.venv/bin/python"
SPACY_MODEL="en_core_web_lg"

# --- Checks (each one best-effort; any failure just counts as "missing") ---

python_available() {
    if [ -x "$VENV_PY" ]; then
        return 0
    fi
    local cand ver major minor
    for cand in python3.13 python3.12 python3.11 python3.10 python3; do
        command -v "$cand" >/dev/null 2>&1 || continue
        ver="$(command "$cand" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null)" || continue
        major="${ver%%.*}"
        minor="${ver##*.}"
        if [ "$major" = "3" ] && [ "$minor" -ge 10 ] 2>/dev/null && [ "$minor" -le 13 ] 2>/dev/null; then
            return 0
        fi
    done
    return 1
}

venv_present() {
    [ -x "$VENV_PY" ]
}

presidio_importable() {
    [ -x "$VENV_PY" ] || return 1
    "$VENV_PY" -c "import presidio_analyzer, presidio_anonymizer" >/dev/null 2>&1
}

model_present() {
    [ -x "$VENV_PY" ] || return 1
    "$VENV_PY" -c "import spacy; spacy.load('$SPACY_MODEL')" >/dev/null 2>&1
}

tesseract_present() {
    command -v tesseract >/dev/null 2>&1
}

# --- Evaluate state ---

CORE_OK=1
python_available   || CORE_OK=0
if [ "$CORE_OK" = "1" ]; then venv_present        || CORE_OK=0; fi
if [ "$CORE_OK" = "1" ]; then presidio_importable || CORE_OK=0; fi
if [ "$CORE_OK" = "1" ]; then model_present       || CORE_OK=0; fi

TESS_OK=1
tesseract_present || TESS_OK=0

# Everything set up — say nothing.
if [ "$CORE_OK" = "1" ] && [ "$TESS_OK" = "1" ]; then
    exit 0
fi

# Core protection (text/document scrubbing) is missing — the full notice.
if [ "$CORE_OK" = "0" ]; then
    if [ "$TESS_OK" = "1" ]; then
        EVERYTHING_ELSE_LINE="   • Everything else works normally."
    else
        EVERYTHING_ELSE_LINE="   • Everything else works normally — except screenshots and other images
     in inputs/, which won't be usable until this is fixed too."
    fi
    cat <<EOF
⚠️  Cortex can't protect client information right now

What's wrong
   The tool that strips client names, emails and account numbers out of
   documents before they go to Claude isn't set up on this computer.

What this means for you
   • You can keep working. Nothing is locked.
   • Files in your engagement's inputs/ folder won't open until this is
     fixed. That's on purpose — opening one right now would send the
     client's real details to Claude with nothing removed.
$EVERYTHING_ELSE_LINE

How to fix it — about 5 minutes, once
   Paste this into your terminal:

       bash scripts/setup_pii.sh

   It downloads a language pack (~380 MB), so give it a few minutes.

   Stuck? Just ask Claude: "help me set up PII protection"
EOF
    exit 0
fi

# Core protection is fine — only the OCR piece (screenshots) is missing.
# Print the actual fix directly (not setup_pii.sh, which by design never
# installs this — it only reports it's missing). Platform detection mirrors
# setup_pii.sh's own tesseract-missing branch so the two never drift.
if [[ "$(uname -s)" == "Darwin" ]]; then
    TESS_CMD="brew install tesseract"
else
    TESS_CMD="sudo apt install tesseract-ocr   # or your distro's package manager"
fi

cat <<EOF
⚠️  Cortex can't process screenshots yet

What's wrong
   The tool that reads text out of screenshots and images before they go
   to Claude isn't set up on this computer.

What this means for you
   • You can keep working normally. Nothing is locked.
   • Documents — PDFs, Word, Excel, PowerPoint — still get cleaned and
     read fine.
   • Screenshots and other images in your engagement's inputs/ folder
     won't be usable until this is fixed.

How to fix it — about a minute, once
   Paste this into your terminal:

       $TESS_CMD

   Stuck? Just ask Claude: "help me set up PII protection"
EOF

exit 0
