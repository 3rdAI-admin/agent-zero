# Agent Zero – API and model setup

Config and settings to set up the **Agent Zero API** (A0T staking credits) and **model presets** in this repo.

---

## Quick start

1. **Get an API key** – [Agent Zero API Dashboard](https://agent-zero.ai) → stake A0T → generate LLM API key (`sk-a0-...`).
2. **Set the key** – In this app: **Settings → External Services → API Keys → Agent Zero Venice.ai**, or in `.env`: `API_KEY_A0_VENICE=sk-a0-your-key`.
3. **Apply preset** – Run `./MODELS.sh agent-zero` (or inside container: `docker exec agent-zero /a0/MODELS.sh agent-zero`), then restart the app/container.
4. **Verify** – Optional: `./MODELS.sh agent-zero --test-llm` to run a short LLM call.

---

## API setup

### Dashboard

- **URL:** [Agent Zero API Dashboard (beta)](https://agent-zero.ai)
- **Wallet:** Connect wallet; fund with ETH on Base if needed.
- **Staking:** Stake A0T to unlock free daily API credits (see “Stake calculation” / “My stakes”).
- **API key:** In the “LLM API key” card, generate or show your key. Format: `sk-a0-...`. Use this only in this app or `.env`; do not commit it.

### Where to set the key in this app

| Method | Where | Notes |
|--------|--------|--------|
| **Settings UI** | Settings → External Services → API Keys → **Agent Zero Venice.ai** | Stored in `usr/.env`; works with Docker volume. |
| **.env file** | Repo root `.env` or `usr/.env` | Use variable `API_KEY_A0_VENICE=sk-a0-...`. Restart app/container after editing. |

The app loads **root `.env`** first, then **`usr/.env`** (override). In Docker, root is often `/a0`; if the repo `.env` is not mounted there, save the key via the Settings UI so it goes to `usr/.env`.

---

## Model config

### Agent Zero API preset (recommended)

The **agent-zero** preset sets Chat, Utility, and Browser to the Agent Zero API with these values:

| Setting | Value |
|--------|--------|
| **Provider** | `a0_venice` (Agent Zero API) |
| **API base** | `https://llm.agent-zero.ai/v1` |
| **Chat model** | `mistral-31-24b` |
| **Utility model** | `qwen3-4b` (temperature 0.2) |
| **Browser model** | `mistral-31-24b` |

### Apply the preset

```bash
# From repo root (writes repo usr/settings.json)
./MODELS.sh agent-zero

# Optional: verify with a short LLM call
./MODELS.sh agent-zero --test-llm
```

If the app runs in Docker and `usr` is a **separate volume**, either:

- Run the script **inside** the container so it writes the volume’s `usr/settings.json`:
  ```bash
  docker exec agent-zero /a0/MODELS.sh agent-zero
  ```
- Or from the host, point at the volume:
  ```bash
  A0_USR_PATH=/path/to/A0_volume ./MODELS.sh agent-zero
  ```

Then **restart** the app or container.

### Other presets

| Preset | Command | Use case |
|--------|---------|----------|
| **anthropic** | `./MODELS.sh anthropic` | Claude (set `API_KEY_ANTHROPIC`) |
| **venice** | `./MODELS.sh venice` | Direct Venice.ai (set `API_KEY_VENICE`) |
| **agent-zero** | `./MODELS.sh agent-zero` | Agent Zero API / staking credits (set `API_KEY_A0_VENICE`) |
| **ollama** | `./MODELS.sh ollama` | Local Ollama (default `localhost:11434`) |

---

## Config files reference

| File | Purpose |
|------|--------|
| **`conf/model_providers.yaml`** | Provider definitions. Agent Zero API = `a0_venice` with `api_base: https://llm.agent-zero.ai/v1`. |
| **`usr/settings.json`** | Runtime model/provider choices (written by `MODELS.sh` or Settings UI). |
| **`.env`** or **`usr/.env`** | API keys and auth (e.g. `API_KEY_A0_VENICE`). |
| **`MODELS.sh`** | Script to switch presets (anthropic, venice, agent-zero, ollama). |
| **`scripts/switch_model_preset.py`** | Applies preset to `usr/settings.json`; used by `MODELS.sh`. |

### Agent Zero API in `model_providers.yaml`

```yaml
chat:
  a0_venice:
    name: Agent Zero API
    litellm_provider: openai
    kwargs:
      api_base: https://llm.agent-zero.ai/v1
      venice_parameters:
        include_venice_system_prompt: false
```

---

## Troubleshooting

- **“Settings not working” / no response**  
  Apply preset and restart: `./MODELS.sh agent-zero` then restart. Ensure the key is set (Settings → API Keys or `API_KEY_A0_VENICE` in `.env`). In Docker, if repo `.env` is not mounted, save the key in the Settings UI.

- **Wrong provider**  
  Use **Agent Zero API** (not “Venice.ai”) when using the dashboard key (`sk-a0-...`). Venice.ai uses a different key and `https://api.venice.ai/api/v1`.

- **401 / invalid key**  
  Regenerate the key on the dashboard and update Settings or `.env`. Restart after changing `.env`.

More detail: see **A0_VENICEAI.md** (Venice vs Agent Zero API, dashboard sections, troubleshooting).
