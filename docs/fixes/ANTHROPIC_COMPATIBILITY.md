# Anthropic Claude API Compatibility Fix

## Overview

This document describes the fixes implemented for Anthropic Claude API compatibility issues in Agent Zero.

**Status**: ✅ Fixed and Deployed (2026-03-14)

## Issues Resolved

### 1. Unsupported Parameter: `frequency_penalty`

**Error**:
```
litellm.UnsupportedParamsError: anthropic does not support parameters: ['frequency_penalty']
```

**Root Cause**:
- Anthropic's Claude API does not support the `frequency_penalty` parameter
- Agent Zero's LIVE preset included this parameter in model kwargs
- LiteLLM was passing it directly to Anthropic, causing API rejection

**Fix Location**: `models.py:516-517`
```python
# Remove unsupported parameters
if "frequency_penalty" in call_kwargs:
    call_kwargs.pop("frequency_penalty")
```

### 2. Parameter Conflict: `temperature` and `top_p`

**Issue**:
- Anthropic Claude API does not allow both `temperature` and `top_p` in the same request
- Agent Zero's LIVE preset included both parameters

**Fix Location**: `models.py:513-514`
```python
# Anthropic doesn't allow both temperature and top_p - prefer temperature
if "temperature" in call_kwargs and "top_p" in call_kwargs:
    call_kwargs.pop("top_p")
```

### 3. API Key Credit Balance Error

**Error**:
```
{"type":"error","error":{"type":"invalid_request_error",
"message":"Your credit balance is too low to access the Anthropic API."}}
```

**Root Cause**:
- Wrong API key was active in `.env` file
- The active key (`API_KEY_ANTHROPIC`) had insufficient credits
- A working key with credits was commented out

**Fix**: Swapped to the working API key in both `.env` files:
- `/Users/james/Docker/AgentZ/.env`
- `/Users/james/Docker/A0_volume/.env`

## Implementation Details

### Parameter Filtering Logic

The fix filters incompatible parameters before making Anthropic API calls:

```python
# models.py:512-517
# Anthropic doesn't allow both temperature and top_p - prefer temperature
# Also, Anthropic doesn't support frequency_penalty at all
if "anthropic" in self.model_name.lower():
    if "temperature" in call_kwargs and "top_p" in call_kwargs:
        call_kwargs.pop("top_p")
    # Remove unsupported parameters
    if "frequency_penalty" in call_kwargs:
        call_kwargs.pop("frequency_penalty")
```

### How It Works

1. **Detection**: Checks if model name contains "anthropic" (case-insensitive)
2. **Conflict Resolution**: If both `temperature` and `top_p` exist, removes `top_p`
3. **Unsupported Parameter Removal**: Removes `frequency_penalty` entirely
4. **Transparent**: Settings still stored in `settings.json` for reference, but filtered before API calls

### LIVE Preset Behavior

The LIVE preset (`MODELS.sh live`) includes these parameters in `settings.json`:
```json
{
  "chat_model_kwargs": {
    "temperature": 0.4,
    "frequency_penalty": 1.45,  // Stored but filtered before API call
    "max_tokens": 4096,
    "top_p": 0.9                 // Stored but filtered before API call
  }
}
```

**Why Keep Them?**
- Documentation of intended behavior
- Compatibility with other providers (Ollama, OpenAI, etc.)
- Easy to reference when switching models

## Persistence

### Container Image
- Fix is **baked into the Docker image**
- Persists across container restarts
- Only lost if rebuilding from old Dockerfile without the fix

### API Key
- Stored in `.env` files on **host filesystem**
- `/Users/james/Docker/AgentZ/.env` (read by docker-compose)
- `/Users/james/Docker/A0_volume/.env` (volume-mounted to container)
- Persists across all restarts/rebuilds

## Testing

### Verify the Fix

1. **Check parameter filtering**:
```bash
docker exec agent-zero grep -A5 "frequency_penalty" /a0/models.py
```

2. **Check API key**:
```bash
grep "API_KEY_ANTHROPIC=" /Users/james/Docker/A0_volume/.env
```

3. **Test API directly**:
```bash
docker exec agent-zero bash -c 'curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $API_KEY_ANTHROPIC" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '"'"'{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'"'"''
```

4. **Check logs for errors**:
```bash
docker compose logs agent-zero 2>&1 | grep -E "(frequency_penalty|UnsupportedParams|credit balance)"
```

### Expected Results

✅ No `frequency_penalty` errors
✅ No `UnsupportedParamsError`
✅ No credit balance errors
✅ Claude responses working normally

## Related Documentation

- `docs/LIVE_PRESET.md` - LIVE preset configuration details
- `MODELS.sh` - Model preset switcher script
- `models.py:512-517` - Parameter filtering implementation

## Troubleshooting

### If errors return after rebuild:

1. **Check if models.py has the fix**:
```bash
grep -A5 "frequency_penalty" models.py | grep "pop"
```

2. **Verify container image includes fix**:
```bash
docker exec agent-zero grep -A5 "frequency_penalty" /a0/models.py
```

3. **Rebuild if needed**:
```bash
docker compose build agent-zero
./restart.sh
```

### If API key issues persist:

1. **Verify correct key is active**:
```bash
grep "API_KEY_ANTHROPIC=" .env
```

2. **Test key directly** (see Testing section above)

3. **Check Anthropic console**: https://console.anthropic.com/settings/keys

## Version History

- **2026-03-14**: Initial fix implemented
  - Parameter filtering added to models.py
  - API key swapped to working key
  - Documentation created
  - Tested and verified working

## Contact

**Organization**: Th3rdAI
**Email**: agentz@th3rdai.com
**Repository**: https://github.com/Th3rdai/AgentZero

---

**Created**: 2026-03-14
**Author**: Claude Code (Anthropic)
**Status**: Active
