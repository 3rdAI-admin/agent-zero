#!/usr/bin/env bash
# Switch Agent Zero model settings between Anthropic, Venice.ai, Agent Zero API, or Ollama.
# Usage: ./MODELS.sh <anthropic|venice|agent-zero|ollama> [--test-llm]
#   --test-llm  Optional: run a minimal LLM call to confirm the model responds.
#
# Agent Zero API (agent-zero) preset – confirmed working:
#   Provider: a0_venice (Agent Zero API)
#   API base: https://llm.agent-zero.ai/v1
#   Chat/Browser: mistral-31-24b | Utility: qwen3-4b (temperature 0.2)
#   Key: set in Settings → API Keys (Agent Zero Venice.ai) or .env as API_KEY_A0_VENICE=sk-a0-...
#
# Where settings are written (so the container sees the change):
#   - From host, writing to the volume (recommended so container sees the change):
#     cd /Users/james/Docker/AgentZ
#     A0_USR_PATH=/Users/james/Docker/A0_volume ./MODELS.sh ollama
#   - Or from the volume (A0_volume has a wrapper that calls this script with A0_USR_PATH set):
#     cd /Users/james/Docker/A0_volume && ./MODELS.sh ollama
#   - From host (./MODELS.sh only): writes to repo usr/settings.json; container won't see it if usr is a volume.
#   - From inside container: writes to /a0/usr/settings.json (the volume the app uses):
#     docker exec agent-zero /a0/MODELS.sh ollama

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR" && pwd)"
cd "$REPO_ROOT"

# MODELS.sh and scripts/ must live in the same repo; writing to a volume uses A0_USR_PATH
if [[ ! -f "$REPO_ROOT/scripts/switch_model_preset.py" ]]; then
  echo "Error: scripts/switch_model_preset.py not found (run from AgentZ repo, not from A0_Volume)."
  echo "To write settings to the volume, run from the repo:"
  echo "  cd /Users/james/Docker/AgentZ"
  echo "  A0_USR_PATH=/Users/james/Docker/A0_volume ./MODELS.sh ollama"
  exit 2
fi

PRESET="${1:-}"
if [[ -z "$PRESET" ]]; then
  echo "Usage: $0 <anthropic|venice|agent-zero|ollama> [--test-llm]"
  echo ""
  echo "Presets:"
  echo "  anthropic   Chat/Utility/Browser -> Anthropic (Claude)"
  echo "  venice      Chat/Utility/Browser -> Venice.ai direct (mistral-31-24b, qwen3-4b)"
  echo "  agent-zero  Chat/Utility/Browser -> Agent Zero API (llm.agent-zero.ai/v1, mistral-31-24b, qwen3-4b, temp 0.2)"
  echo "  ollama      Chat/Utility/Browser -> Ollama (qwen2.5:latest, 192.168.50.7:11434)"
  echo ""
  echo "Optional: --test-llm  Run a short LLM call to verify the model responds."
  exit 2
fi

PRESET_LOWER="$(echo "$PRESET" | tr '[:upper:]' '[:lower:]')"
# Normalize agent-zero for Python script (preset key is agent_zero)
[[ "$PRESET_LOWER" == "agent-zero" ]] && PRESET_LOWER="agent_zero"
case "$PRESET_LOWER" in
  anthropic|venice|agent_zero|ollama) ;;
  *)
    echo "Error: preset must be anthropic, venice, agent-zero, or ollama (got: $PRESET)"
    exit 2
    ;;
esac

# Prefer repo venv, then system python
PYTHON=""
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON="$REPO_ROOT/.venv/bin/python"
elif command -v python3 &>/dev/null; then
  PYTHON="python3"
else
  PYTHON="python"
fi

echo "=============================================="
echo "Agent Zero – switch model preset to: $PRESET_LOWER"
echo "=============================================="

export A0_USR_PATH="${A0_USR_PATH:-}"
EXTRA_ARGS=()
for a in "$@"; do [[ "$a" == --test-llm ]] && EXTRA_ARGS+=(--test-llm); done
OUTPUT="$("$PYTHON" "$SCRIPT_DIR/scripts/switch_model_preset.py" "$PRESET_LOWER" "${EXTRA_ARGS[@]}" 2>&1)" || true
EXIT=$?

echo "$OUTPUT"
echo "----------------------------------------------"

if [[ $EXIT -eq 0 ]]; then
  echo "Status: Preset '$PRESET_LOWER' applied and verified."
else
  echo "Status: Preset '$PRESET_LOWER' applied; verification reported issues (see above)."
fi
echo "Venice.ai     -> set Venice.ai key in Settings → API Keys or API_KEY_VENICE in .env."
echo "Agent Zero    -> set Agent Zero API key (sk-a0-...) in Settings → API Keys or API_KEY_A0_VENICE."
echo "Anthropic     -> set API_KEY_ANTHROPIC."
echo "Ollama        -> ensure Ollama is running at api_base (192.168.50.7:11434)."
echo "----------------------------------------------"
if [[ -x "$REPO_ROOT/restart.sh" ]]; then
  echo "Restarting Agent Zero..."
  "$REPO_ROOT/restart.sh" || echo "Restart failed (e.g. run from host: ./restart.sh)."
else
  echo "Restart Agent Zero to use the new models (e.g. ./restart.sh)."
fi
echo "=============================================="
exit $EXIT
