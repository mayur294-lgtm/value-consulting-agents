#!/usr/bin/env bash
# Developer onboarding for the bb-* harness eval keys.
#
# WHO RUNS THIS: developers who change agents/skills/components (the people the
# bb-* lifecycle + eval gate apply to). People who only RUN agents to generate
# outputs do NOT need this and are never prompted.
#
# WHAT IT SETS (into evals/.env, gitignored):
#   ANTHROPIC_API_KEY  -> the developer's OWN key (for the LLM-judges). Prompted.
#   LANGFUSE_*         -> the SHARED eval-project keys. Seeded from (in order):
#                         existing env vars, then evals/.env.shared (team-distributed,
#                         gitignored), else prompted.
#
# Idempotent: re-running only fills what's missing. Never commits secrets.
set -euo pipefail
cd "$(dirname "$0")/.."          # repo root
ENV="evals/.env"
SHARED="evals/.env.shared"       # optional, gitignored, team-distributed
touch "$ENV"; chmod 600 "$ENV"

# set KEY=VALUE in $ENV (replace if present, append if missing); skip empty values
put() { local k="$1" v="$2"; [ -z "$v" ] && return 0
  if grep -q "^${k}=" "$ENV"; then
    tmp=$(mktemp); grep -v "^${k}=" "$ENV" > "$tmp"; mv "$tmp" "$ENV"; fi
  printf '%s=%s\n' "$k" "$v" >> "$ENV"; }
have() { grep -q "^${1}=." "$ENV"; }
from_shared() { [ -f "$SHARED" ] && grep "^${1}=" "$SHARED" | head -1 | cut -d= -f2- || true; }

echo "== bb-* developer eval setup =="

# --- Langfuse (shared eval project) ----------------------------------------
put LANGFUSE_HOST "${LANGFUSE_HOST:-$(from_shared LANGFUSE_HOST)}"
have LANGFUSE_HOST || put LANGFUSE_HOST "https://cloud.langfuse.com"   # EU default
for k in LANGFUSE_PUBLIC_KEY LANGFUSE_SECRET_KEY; do
  if ! have "$k"; then
    v="${!k:-$(from_shared "$k")}"
    if [ -z "$v" ]; then
      read -r -p "Shared $k (from the team — leave blank to skip Langfuse logging): " v
    fi
    put "$k" "$v"
  fi
done

# --- Anthropic (the developer's OWN key, for the judges) -------------------
if ! have ANTHROPIC_API_KEY; then
  echo
  echo "The LLM-judges (arc threading, conservative bias, ...) need YOUR OWN Anthropic API key."
  echo "Get one at https://console.anthropic.com/settings/keys"
  read -r -s -p "ANTHROPIC_API_KEY (input hidden, blank to skip judges): " ak; echo
  put ANTHROPIC_API_KEY "$ak"
fi

echo
echo "Wrote $ENV. Configured: $(grep -oE '^[A-Z_]+' "$ENV" | tr '\n' ' ')"
echo "Install eval deps:  python3 -m pip install -r evals/requirements.txt langfuse anthropic"
echo "Smoke test:         python3 evals/run_experiment.py --deck evals/goldens/deck_valid_min.html"
have ANTHROPIC_API_KEY || echo "NOTE: no ANTHROPIC_API_KEY — judges will be skipped until you add one (re-run this script)."
