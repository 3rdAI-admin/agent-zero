# Agent Zero – Venice.ai (Agent Zero API) configuration

**Source:** Agent Zero API Dashboard (beta) — [agent-zero.ai](https://agent-zero.ai)  
**Saved:** 2026-02-26

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
