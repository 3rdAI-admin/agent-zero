# Voice Function - Whisper Model Size Fix

## Overview

This document describes the fix for the voice/speech-to-text function crash in Agent Zero.

**Status**: ✅ Fixed and Deployed (2026-03-15)

## Issues Resolved

### Whisper Model Crash (SIGKILL)

**Symptoms**:
- Voice function not working in Web UI
- Browser error: "Failed to load modal content: Failed to fetch"
- Process crash in container logs

**Error in Logs**:
```
Loading Whisper model: medium
2026-03-15 07:07:10,801 WARN exited: run_ui (terminated by SIGKILL; not expected)
```

**Root Cause**:
- Whisper "medium" model was too heavy for the container resources
- The run_ui process was being killed by SIGKILL when attempting to load the model
- Memory usage was not the issue (only 18.53% utilization)
- Likely caused by CPU constraints or model loading timeout

## Implementation Details

### Model Size Reduction

**File**: `/Users/james/Docker/A0_volume/settings.json:72`

**Change**:
```json
// Before:
"stt_model_size": "medium",

// After:
"stt_model_size": "base",
```

### Why "base" Model?

The Whisper model has several sizes available:
- **tiny**: Fastest, least accurate (~39M parameters)
- **base**: Good balance of speed and accuracy (~74M parameters) ✅ **CHOSEN**
- **small**: Better accuracy, slower (~244M parameters)
- **medium**: High accuracy, resource-intensive (~769M parameters) ❌ **CAUSED CRASH**
- **large**: Best accuracy, very resource-intensive (~1550M parameters)

We chose "base" because:
1. Significantly lighter than "medium" (74M vs 769M parameters)
2. Still provides good transcription accuracy for English
3. Fast enough for real-time speech recognition
4. Proven stable in containerized environments

## Persistence

### ✅ Survives Container Restarts
- Setting stored in volume-mounted `settings.json`
- Location: `/Users/james/Docker/A0_volume/settings.json`
- Mapped to container at `/a0/usr/settings.json`

### ✅ Survives Container Rebuilds
- Settings file is on host filesystem, not in container
- Persists independently of container image

### ✅ Survives Git Pulls/Merges
- Settings file is in `.gitignore` (user-specific configuration)
- Will not be overwritten by repository updates

## Testing

### Verify the Fix

1. **Check setting in volume**:
```bash
grep "stt_model_size" /Users/james/Docker/A0_volume/settings.json
```
**Expected output**: `"stt_model_size": "base",`

2. **Check setting inside container**:
```bash
docker exec agent-zero grep "stt_model_size" /a0/usr/settings.json
```
**Expected output**: `"stt_model_size": "base",`

3. **Check for process crashes**:
```bash
docker compose logs agent-zero 2>&1 | grep -E "(SIGKILL|terminated by)" | tail -10
```
**Expected output**: No SIGKILL errors (only SIGHUP from normal restarts)

4. **Check container health**:
```bash
docker compose ps agent-zero
```
**Expected output**: `Up X minutes (healthy)`

### Expected Results

✅ No SIGKILL errors
✅ run_ui process stays running
✅ Container status shows "healthy"
✅ Voice function loads in Web UI
✅ Speech-to-text transcription works

## Related Documentation

- `settings.json` - User configuration file
- `/Users/james/Docker/A0_volume/` - Persistent volume mount

## Troubleshooting

### If voice function still doesn't work:

1. **Verify setting is correct**:
```bash
docker exec agent-zero grep "stt_model_size" /a0/usr/settings.json
```

2. **Check for WebSocket errors**:
```bash
docker compose logs agent-zero 2>&1 | grep -i websocket | tail -20
```

3. **Restart container**:
```bash
./restart.sh
```

4. **Try even smaller model** (if base is still too heavy):
Edit `/Users/james/Docker/A0_volume/settings.json` line 72:
```json
"stt_model_size": "tiny",
```
Then restart: `./restart.sh`

### Alternative Solutions

If local Whisper continues to have issues:

1. **Disable voice function**: Set in settings.json
2. **Use external STT API**: Configure OpenAI Whisper API or Google Speech-to-Text
3. **Increase container resources**: Modify docker-compose.yml to allocate more CPU/memory

## Version History

- **2026-03-15**: Initial fix implemented
  - Changed model size from "medium" to "base"
  - Tested and verified working
  - No more SIGKILL crashes
  - Container healthy and stable

## Contact

**Organization**: Th3rdAI
**Email**: agentz@th3rdai.com
**Repository**: https://github.com/Th3rdai/AgentZero

---

**Created**: 2026-03-15
**Author**: Claude Code (Anthropic)
**Status**: Active
