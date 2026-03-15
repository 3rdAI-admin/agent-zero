# Agent Zero Fixes

This directory documents production fixes and patches applied to Agent Zero.

## Overview

Each fix is documented in its own markdown file with:
- **Problem description** - What was broken
- **Root cause analysis** - Why it was broken
- **Implementation details** - How we fixed it
- **Testing procedures** - How to verify it works
- **Persistence notes** - How to ensure it stays fixed

## Active Fixes

### Anthropic Claude API Compatibility
**File**: `ANTHROPIC_COMPATIBILITY.md`
**Date**: 2026-03-14
**Status**: ✅ Active

Fixes three issues with Anthropic Claude API integration:
1. Unsupported `frequency_penalty` parameter
2. Conflict between `temperature` and `top_p` parameters
3. API key credit balance error

**Impact**:
- Enables LIVE preset with Claude Sonnet 4-6
- Prevents LiteLLM parameter errors
- Ensures API calls succeed

**Files Modified**:
- `models.py:512-517` - Parameter filtering logic
- `.env` - API key configuration
- `Dockerfile:36` - Documentation reference

### Voice Function - Whisper Model Size
**File**: `VOICE_WHISPER_MODEL_SIZE.md`
**Date**: 2026-03-15
**Status**: ✅ Active

Fixes Whisper STT model crash that prevented voice function from working:
1. run_ui process crash (SIGKILL)
2. "Failed to load modal content" error in browser
3. Voice/speech-to-text not loading

**Impact**:
- Voice function now works reliably
- No more process crashes
- Faster model loading with "base" vs "medium"

**Files Modified**:
- `/Users/james/Docker/A0_volume/settings.json:72` - Changed `stt_model_size` from "medium" to "base"

## Adding New Fixes

When documenting a new fix:

1. **Create a markdown file** in this directory
2. **Use this template**:
```markdown
# [Fix Name]

## Overview
Brief description of what was fixed

## Issues Resolved
List of specific errors or problems

## Implementation Details
Code changes made, with file locations

## Testing
How to verify the fix works

## Persistence
How the fix survives restarts/rebuilds

## Version History
- Date: What was done
```

3. **Update this README** with a summary in the "Active Fixes" section

4. **Reference in related files**:
   - Add comments to modified code files
   - Update Dockerfile if changes affect build
   - Update relevant documentation

## Fix Status Codes

- ✅ **Active** - Currently deployed and working
- 🔄 **In Progress** - Being implemented or tested
- 📝 **Documented** - Issue documented, fix planned
- ⏸️ **Deferred** - Fix postponed for later
- ❌ **Obsolete** - No longer needed (e.g., upstream fixed)

## Related Documentation

- `docs/LIVE_PRESET.md` - Production model configuration
- `docs/DOCUMENTATION_INDEX.md` - All Agent Zero documentation
- `MODELS.sh` - Model preset switcher
- `Dockerfile` - Container build configuration

## Contact

**Organization**: Th3rdAI
**Email**: agentz@th3rdai.com
**Repository**: https://github.com/Th3rdai/AgentZero

---

**Last Updated**: 2026-03-15
**Total Fixes**: 2 active
