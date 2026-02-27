# Agent Zero – Venice.ai (Agent Zero API) configuration

**Source:** Agent Zero API Dashboard (beta) — [agent-zero.ai](https://agent-zero.ai)  
**Saved:** 2026-02-26

---

## Default configuration (this repo)

Agent Zero is configured to use **Venice.ai** by default for Chat, Utility, and Browser:

| Role    | Provider  | Default model     |
|---------|-----------|-------------------|
| Chat    | Venice.ai | `mistral-31-24b`  |
| Utility | Venice.ai | `qwen3-4b`       |
| Browser | Venice.ai | `mistral-31-24b`  |

You only need to add your **API key** (see below). To restore these defaults via env, use `conf/venice-defaults.env.example`.

---

## Overview

A0T token holders can use **free Venice.ai API credits** to run Agent Zero. Credits are tied to staking; the dashboard shows wallet info, remaining quota, and an LLM API key to use with the **Agent Zero Venice.ai** model provider in Agent Zero.

**Do not commit API keys.** Store the key in Agent Zero’s **External Services → API keys** (or in `.env` as below). This file documents only the setup steps and provider details.

---

## How to use (from the dashboard)

1. **Stake A0T tokens**  
   Stake A0T tokens to unlock free daily API credits. See the dashboard **“Stakes”** / **“Stake calculation”** links.

2. **Generate API key**  
   On the API Dashboard, open the **“LLM API key”** card and generate your API key.  
   Format: `sk-a0-...` (paste only into Agent Zero or `.env`, never into this file).

3. **Select Agent Zero Venice.ai in Agent Zero**  
   For **Chat**, **Utility**, or **Browser** model, in Agent Zero Settings choose the **Agent Zero Venice.ai** (or **Agent Zero API**) model provider.

4. **Paste the API key in Agent Zero**  
   Go to **External Services** (or **Settings → API keys**), open **API keys**, and paste your key into the **Agent Zero Venice.ai** field.

5. **Pick a Venice text model**  
   In the model dropdown for Chat/Utility/Browser, select one of the Venice text models:  
   [Venice text models](https://docs.venice.ai/models/text).

6. **Use your daily quota**  
   Requests use your free daily quota shown on the dashboard.

---

## Recommended Venice models (by role)

Use the **exact model IDs** shown in Agent Zero’s model dropdown when **Agent Zero Venice.ai** is selected, or check the current list: [Venice text models](https://docs.venice.ai/models/text). Names below are guidance; Venice may add or rename models.

| Role | Use for | Recommendation |
|------|--------|----------------|
| **Chat** | Main conversation and reasoning | A **capable mid- or top-tier** text model (e.g. a strong Qwen, Mistral, or Llama variant). Use the same tier you would for primary chat. |
| **Utility** | Summarization, memory extraction, internal tasks | A **smaller / faster** model to save quota and keep latency low. Prefer a small Qwen, Mistral, or Llama (e.g. 7B or smaller). Good balance of quality and cost for summarization. |
| **Browser** | Web automation (browser-use: click, type, navigate) | A model that supports **Vision** and **Function calling**. Use a **mid-tier or same as Chat**—not the smallest. Needed for screenshots and tool use; avoid the tiniest models for reliability. |

**Summary**

- **Chat:** Strong model (top or mid tier).
- **Utility:** Smaller model (e.g. 7B or small variant) to save credits.
- **Browser:** Vision + function-calling model, mid-tier or same as Chat.

If the dropdown lists multiple sizes (e.g. 7B vs 70B), use **7B/small for Utility** and **larger for Chat/Browser** as above.

---

## Agent Zero provider details

| Item | Value |
|------|--------|
| **Provider ID (config)** | `a0_venice` |
| **UI name** | Agent Zero API / Agent Zero Venice.ai |
| **API base** | `https://llm.agent-zero.ai/v1` |
| **Env var for API key** | `API_KEY_A0_VENICE` or `A0_VENICE_API_KEY` (in `.env`) |
| **Config file** | `conf/model_providers.yaml` (chat provider `a0_venice`) |

You can set the key either in the **API keys** section of the Settings UI (under the Agent Zero Venice.ai / a0_venice field) or in `.env`:

```bash
# Optional: set in .env instead of UI (do not commit)
API_KEY_A0_VENICE=sk-a0-your-key-here
```

**Where the app reads the key:** The app loads two `.env` files (in order): the repo/root `.env` (e.g. project root or `/a0/.env` in Docker), then `usr/.env` (Settings-page saves; in Docker this is the `A0_volume` mount). Use **exactly** `API_KEY_VENICE` for Venice.ai or `API_KEY_A0_VENICE` for Agent Zero API. Restart the container after editing `.env` so the process picks up the change.

---

## Dashboard sections (reference)

- **Wallet info:** Address, A0T balance, Staked A0T, Stake Score (links: Stake calculation, My stakes).
- **Free daily API credits:** Remaining quota, base quota, dynamic quota, used quota, LLM requests, LLM tokens (In/Out). Links: How does it work?, Stake calculation.
- **Global API data:** Quota multiplier, global quota, daily reset (0:00 UTC), LLM requests/tokens, total stake score. Link: How does it work?.
- **LLM API key:** Generate / Show / Clear key; terms and conditions apply.

---

## Venice.ai vs Agent Zero Venice.ai

- **Agent Zero Venice.ai** (`a0_venice`): Uses `https://llm.agent-zero.ai/v1` and the API key from the Agent Zero API Dashboard. For A0T stakers’ free credits.
- **Venice.ai** (`venice`): Uses `https://api.venice.ai/api/v1` and your own Venice.ai API key. Different provider in the dropdown.

Use **Agent Zero Venice.ai** when following the dashboard “How to use” steps and when using the key from the LLM API key card.

---

## Troubleshooting: “Venice not working”

If you switched from Claude to Venice and chat/utility/browser don’t respond or show errors, check the following.

### 1. **Provider and API key must match**

| If you selected this in Settings | You must set the API key here | Env var (if using `.env`) |
|----------------------------------|------------------------------|---------------------------|
| **Venice.ai** (your own Venice account) | Settings → API Keys → **Venice.ai** | `API_KEY_VENICE=` (get key from [venice.ai](https://venice.ai)) |
| **Agent Zero API** (staking credits) | Settings → API Keys → **Agent Zero API** | `API_KEY_A0_VENICE=` (key from [agent-zero.ai](https://agent-zero.ai) dashboard, `sk-a0-...`) |

- You cannot use an Agent Zero dashboard key (`sk-a0-...`) with the **Venice.ai** provider, or a Venice.ai key with **Agent Zero API**.
- If you see a banner **“Missing LLM API Key for current settings”**, the key for your *selected* provider is missing. Add it under that provider’s name in Settings → External Services → API Keys (or in `.env` as above).

### 2. **Where the key is read from**

- **Settings UI:** Keys you save in Settings → API Keys are stored in the app’s env file (e.g. `usr/.env` in the container). No need to edit `.env` if you set it in the UI.
- **Docker with repo `.env`:** If you use `env_file: .env` in docker-compose, variables from the repo’s `.env` are injected into the container. Use `API_KEY_VENICE=...` for **Venice.ai** or `API_KEY_A0_VENICE=...` for **Agent Zero API**. Restart the container after changing `.env`.

### 3. **Set all three roles (Chat, Utility, Browser)**

In Settings, set **provider and model** for:

- **Chat model** → e.g. Venice.ai (or Agent Zero API) + a model (e.g. `mistral-31-24b` or `qwen3-4b`).
- **Utility model** → Same provider, smaller model (e.g. `qwen3-4b`) to save quota.
- **Browser model** → Same provider, a model that supports **vision + function calling** (e.g. `mistral-31-24b`).

If any role still points at Anthropic/Claude, that role will use Claude and can fail or cost money. Switch each role to Venice (or Agent Zero API) and a valid model.

### 4. **Model ID**

Use a **model ID that appears in the dropdown** for your provider. If you type a custom ID, it must be a valid Venice model (see [Venice text models](https://docs.venice.ai/models/text)). Wrong or deprecated IDs can cause 404 or “model not found” errors.

### 5. **Quick checklist**

- [ ] Settings → Chat/Utility/Browser **provider** is **Venice.ai** or **Agent Zero API** (not Anthropic).
- [ ] Settings → API Keys has a key for **that same provider** (Venice.ai **or** Agent Zero API).
- [ ] No “Missing LLM API Key” banner (or it’s gone after adding the key).
- [ ] After changing provider or key, try a simple chat again; restart the app/container if you edited `.env` on the host.

### 6. **"Settings not working" (Agent Zero API)**

If you've set the provider and key but chat/utility/browser still fail:

- **Apply preset and restart:** Run `./MODELS.sh agent-zero` (or inside the container: `docker exec agent-zero /a0/MODELS.sh agent-zero`), then restart the app/container. That sets Chat/Utility/Browser to Agent Zero API and `https://llm.agent-zero.ai/v1`.
- **Docker and `.env`:** The app loads root `.env` then `usr/.env`. In Docker, root is often `/a0`; if your repo `.env` isn't mounted there, the container won't see it. Either mount the repo (or a file) so `/a0/.env` exists, or save the key in **Settings → API Keys** so it's stored in `usr/.env` (the volume the app uses).
- **Restart after editing `.env`:** Env vars are read at process start and when settings are loaded. Restart the container after changing `.env` so the new key is picked up.
