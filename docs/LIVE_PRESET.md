# Th3rdAI Production Settings - LIVE Preset

## Overview

The `--LIVE` preset preserves Th3rdAI's production Agent Zero configuration with optimized Claude Sonnet 4.6 parameters.

## Quick Usage

```bash
# From host (recommended)
cd /Users/james/Docker/AgentZ
A0_USR_PATH=/Users/james/Docker/A0_volume ./MODELS.sh live

# Or use the wrapper from A0_volume
cd /Users/james/Docker/A0_volume
./MODELS.sh live

# From inside container
docker exec agent-zero /a0/MODELS.sh live
```

## Configuration Details

### Chat Model (Claude Sonnet 4.6)
- **Temperature**: 0.4 (balanced creativity/consistency)
- **Frequency Penalty**: 1.45 (strong repetition prevention)
- **Max Tokens**: 4096 (full responses)
- **Top-P**: 0.9 (diverse output sampling)
- **Context Length**: 32,000 tokens

### Utility Model (Claude Sonnet 4.6)
- **Temperature**: 0.2 (deterministic for utilities)
- **Frequency Penalty**: 1.1 (moderate repetition prevention)
- **Max Tokens**: 2048 (concise utility responses)
- **Context Length**: 32,000 tokens

### Browser Model (Claude Sonnet 4.6)
- **Temperature**: 0.2 (structured for web extraction)
- **Frequency Penalty**: 1.45 (strong repetition prevention)
- **Max Tokens**: 4096 (full browser responses)

## When to Use

Use the `live` preset to:
1. **Restore Production Settings**: After testing other presets
2. **New Environment Setup**: Configure a fresh Agent Zero instance
3. **Consistency**: Ensure identical settings across deployments
4. **Backup/Recovery**: Quickly restore known-good configuration

## Parameter Rationale

### Chat Model Parameters
- **Temperature 0.4**: Sweet spot for conversational AI
  - Not too creative (0.7+) to hallucinate
  - Not too deterministic (0.1) to be robotic
  - Produces reliable, contextual responses

- **Frequency Penalty 1.45**: Prevents Claude from:
  - Repeating the same phrases
  - Getting stuck in loops
  - Overusing certain sentence structures
  - Note: Anthropic uses this differently than OpenAI

- **Top-P 0.9**: Nucleus sampling for diversity
  - Considers top 90% probability mass
  - Balances coherence with creativity
  - Works well with temperature 0.4

### Utility Model Parameters
- **Lower Temperature (0.2)**: Deterministic for:
  - Code generation
  - File operations
  - System commands
  - Structured data parsing

- **Lower Frequency Penalty (1.1)**: Utilities need:
  - Consistent command syntax
  - Predictable output formats
  - Reliable structured responses

### Browser Model Parameters
- **Temperature 0.2**: Structured extraction from web pages
- **High Frequency Penalty (1.45)**: Prevents repetitive scraping patterns
- **Max Tokens 4096**: Handles complex page structures

## Anthropic-Specific Notes

The `live` preset includes Anthropic parameter compatibility fixes:
- **No `frequency_penalty`** passed to API (filtered out in models.py:516)
- **Never both `temperature` and `top_p`** (conflict resolution in models.py:512-514)
- Parameters stored for future reference but filtered before API calls

## Version History

- **2026-03-14**: Initial creation
  - Based on current production settings
  - Includes Anthropic parameter compatibility fixes
  - Tested and verified with Claude Sonnet 4.6

## Updating the LIVE Preset

If you change production settings and want to update the `live` preset:

1. Edit `scripts/switch_model_preset.py`
2. Find the `"live"` preset dictionary (around line 93)
3. Update the parameters
4. Test with: `./MODELS.sh live`
5. Commit changes to git

## Related Files

- `/Users/james/Docker/AgentZ/MODELS.sh` - Main preset switcher
- `/Users/james/Docker/AgentZ/scripts/switch_model_preset.py` - Preset definitions
- `/Users/james/Docker/AgentZ/models.py:512-517` - Anthropic parameter filtering
- `/a0/usr/settings.json` - Active configuration file

## Contact

**Organization**: Th3rdAI
**Email**: agentz@th3rdai.com
**GitHub**: https://github.com/Th3rdai/AgentZero

---

**Last Updated**: 2026-03-14
**Created by**: Agent Zero (Claude Code)
