# Agent Zero – Ollama setup

Config and settings to run Agent Zero with **Ollama** (local LLMs). No API key required.

---

## Quick start

1. **Install and run Ollama** – [ollama.com](https://ollama.com) → install → start the Ollama service (default port **11434**).
2. **Pull a model** – e.g. `ollama pull qwen2.5:latest` (or another from the [Ollama library](https://ollama.com/library)).
3. **Apply preset** – Run `./MODELS.sh ollama` (or inside container: `docker exec agent-zero /a0/MODELS.sh ollama`), then restart the app/container.
4. **Verify** – Optional: `./MODELS.sh ollama --test-llm` to run a short LLM call.

---

## Ollama setup

### Install

| OS | Command / link |
|----|-----------------|
| **macOS** | `brew install ollama` or [Download](https://ollama.com/download) |
| **Linux** | `curl -fsSL https://ollama.com/install.sh \| sh` |
| **Windows** | [OllamaSetup.exe](https://ollama.com/download/OllamaSetup.exe) |

After install, the Ollama service usually runs in the background. Default API: **http://localhost:11434**.

### Pull models

```bash
# List installed models
ollama list

# Pull a model (use the exact name in Settings / preset)
ollama pull qwen2.5:latest
```

Use names from the [Ollama library](https://ollama.com/library) (e.g. `llama3.2`, `qwen2.5:latest`, `mistral`, `phi3`).

### No API key

Ollama is local; Agent Zero does **not** require an API key for the Ollama provider. Leave the Ollama API key field empty in Settings.

---

## Model config

### Ollama preset (this repo)

The **ollama** preset sets Chat, Utility, and Browser to Ollama with these values:

| Setting | Value |
|--------|--------|
| **Provider** | `ollama` |
| **API base** | `http://localhost:11434` |
| **Chat model** | `qwen2.5:latest` |
| **Utility model** | `qwen2.5:latest` |
| **Browser model** | `qwen2.5:latest` |

Ensure `qwen2.5:latest` (or the model you choose) is pulled: `ollama pull qwen2.5:latest`.

### Apply the preset

```bash
# From repo root (writes repo usr/settings.json)
./MODELS.sh ollama

# Optional: verify with a short LLM call
./MODELS.sh ollama --test-llm
```

If the app runs in Docker and `usr` is a **separate volume**:

- Run inside the container: `docker exec agent-zero /a0/MODELS.sh ollama`
- Or from host: `A0_USR_PATH=/path/to/A0_volume ./MODELS.sh ollama`

Then **restart** the app or container.

### Custom host or port

The preset uses `http://localhost:11434`. If Ollama runs on another host or port:

- **Settings UI:** Settings → Chat / Utility / Browser model → set **API base URL** to e.g. `http://YOUR_IP:11434` or `http://host.docker.internal:11434` (Docker, Ollama on host).
- **Or** edit `usr/settings.json` and set `chat_model_api_base`, `util_model_api_base`, `browser_model_api_base` to your Ollama URL.

---

## Docker: Agent Zero + Ollama

If **Agent Zero runs in Docker** and **Ollama runs on the host**:

- Use API base: **`http://host.docker.internal:11434`** (Mac/Windows) or the host’s IP on Linux.
- Ensure port **11434** is reachable from the container (no firewall blocking).

If **both run in Docker** (same network):

- Use API base: **`http://<ollama_container_name>:11434`**.

After changing the API base, save settings and restart the app/container.

---

## Config files reference

| File | Purpose |
|------|--------|
| **`conf/model_providers.yaml`** | Provider definitions. Ollama = `ollama` with `litellm_provider: ollama` (no default api_base in YAML; preset sets it). |
| **`usr/settings.json`** | Runtime model/provider and API base (written by `MODELS.sh` or Settings UI). |
| **`MODELS.sh`** | Script to switch presets; `./MODELS.sh ollama` applies the Ollama preset. |
| **`scripts/switch_model_preset.py`** | Applies preset to `usr/settings.json`; used by `MODELS.sh`. |

### Ollama in `model_providers.yaml`

```yaml
chat:
  ollama:
    name: Ollama
    litellm_provider: ollama
```

The preset fills in the API base in `usr/settings.json`; the YAML does not define a default base URL.

---

## Troubleshooting

- **Connection refused / no response**  
  Ensure Ollama is running: `ollama list` or open http://localhost:11434 in a browser. If Agent Zero is in Docker and Ollama is on the host, use `http://host.docker.internal:11434` (or host IP on Linux) as the API base.

- **Model not found**  
  Pull the model: `ollama pull qwen2.5:latest` (or the exact name shown in Settings). Use names from [ollama.com/library](https://ollama.com/library).

- **Preset not applied in container**  
  If `usr` is a Docker volume, run the preset inside the container: `docker exec agent-zero /a0/MODELS.sh ollama`, then restart.

- **Different model per role**  
  Apply the preset, then in Settings change Chat / Utility / Browser model names (e.g. Chat: `qwen2.5:latest`, Utility: `phi3`, Browser: `llama3.2`) and save.
