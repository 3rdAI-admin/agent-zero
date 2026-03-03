#!/usr/bin/env bash
# Generate Ollama Modelfiles that set num_ctx (context length) for VRAM optimization.
# num_ctx cannot be set via LiteLLM/OpenAI kwargs; it must be set in an Ollama Modelfile.
#
# Run the generated commands ON THE OLLAMA SERVER (e.g. 192.168.50.7), not on the host.
# Example: ssh 192.168.50.7 'bash -s' < scripts/ollama_create_modelfiles.sh
# Or copy the Modelfile content below and run ollama create on the server.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "=============================================="
echo "Ollama Modelfiles for num_ctx (VRAM reduction)"
echo "=============================================="
echo ""
echo "Run these on your Ollama server (e.g. 192.168.50.7)."
echo "GLM-4.7-Flash with 32K ctx uses ~20GB VRAM instead of ~40GB (128K default)."
echo ""

# GLM-4.7-Flash 32K context
echo "--- Modelfile: glm-4.7-flash:32k (num_ctx 32768) ---"
cat << 'MODELFILE'
FROM glm-4.7-flash:latest
PARAMETER num_ctx 32768
MODELFILE
echo ""
echo "To create the model on the Ollama server:"
echo "  ollama create glm-4.7-flash:32k -f - << 'EOF'
FROM glm-4.7-flash:latest
PARAMETER num_ctx 32768
EOF"
echo ""
echo "Or save to a file and run:"
echo "  cat > /tmp/Modelfile.glm32k << 'EOF'
FROM glm-4.7-flash:latest
PARAMETER num_ctx 32768
EOF"
echo "  ollama create glm-4.7-flash:32k -f /tmp/Modelfile.glm32k"
echo ""
echo "After creating glm-4.7-flash:32k, presets ollama-glm, ollama-mixed, and ollama-glm-claude will use it (see scripts/switch_model_preset.py)."
echo "=============================================="
