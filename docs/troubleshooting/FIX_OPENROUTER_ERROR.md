# Fix: OpenRouter "Insufficient Credits" Error

## Problem
Agent Zero is configured to use OpenRouter by default, but your API key doesn't have credits. This causes errors when trying to use features like "Recall memories".

## Solutions

### Option 1: Use Ollama (Free, Local Models) - Recommended for Kali Runner

**Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Start Ollama service:**
```bash
ollama serve &
```

**Download a model (choose one):**
```bash
# Small, fast model
ollama pull llama3.2

# Or larger, more capable model
ollama pull qwen2.5:7b
```

**Configure Agent Zero:**
1. Open Settings in Agent Zero Web UI
2. **Chat Model:**
   - Provider: `Ollama`
   - Model Name: `llama3.2` (or your chosen model)
   - API URL: `http://localhost:11434`
3. **Utility Model:**
   - Provider: `Ollama`
   - Model Name: `llama3.2` (or your chosen model)
   - API URL: `http://localhost:11434`
4. **Browser Model:**
   - Provider: `Ollama`
   - Model Name: `llama3.2` (or your chosen model)
   - API URL: `http://localhost:11434`
5. Click "Save"

### Option 2: Add OpenRouter Credits
1. Go to https://openrouter.ai/settings/credits
2. Purchase credits or add a valid API key with credits
3. Add your API key in Agent Zero Settings → API Keys → OpenRouter

### Option 3: Use Another Provider
Configure any other provider (OpenAI, Anthropic, Groq, etc.) in Settings with a valid API key.

## Quick Fix Script
If you want to quickly switch to Ollama, you can modify the settings file directly, but it's easier to use the Web UI Settings page.

