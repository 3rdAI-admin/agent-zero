# Container Recreation Safety Guide

## ✅ Settings That WILL Persist (Safe)

All important settings and data are persisted via volume mounts in `docker-compose.yml`:

### 1. **Agent Zero Settings** ✅
- **Location**: `./tmp/settings.json` → `/a0/tmp/settings.json`
- **Contains**:
  - Chat model configuration (provider, model name, API URL, context length)
  - Utility model settings
  - Embedding model settings
  - MCP server configurations
  - API keys (stored in settings)
  - Agent configuration (prompts subdirectory, memory subdirectory, knowledge subdirectory)
  - Speech-to-text settings
  - Authentication credentials (UI login/password)
- **Status**: ✅ **SAFE** - Persisted via `./tmp:/a0/tmp` volume mount

### 2. **Memory & Learned Information** ✅
- **Location**: `./memory` → `/a0/memory`
- **Contains**: Agent's memory and learned information
- **Status**: ✅ **SAFE** - Persisted via volume mount

### 3. **Knowledge Base** ✅
- **Location**: `./knowledge` → `/a0/knowledge`
- **Contains**: Custom knowledge files
- **Status**: ✅ **SAFE** - Persisted via volume mount

### 4. **Logs** ✅
- **Location**: `./logs` → `/a0/logs`
- **Contains**: All session logs and HTML outputs
- **Status**: ✅ **SAFE** - Persisted via volume mount

### 5. **Claude Code OAuth Authentication** ✅
- **Location**: `./claude-config` → `/root/.config/claude-code` and `/home/claude/.config/claude-code`
- **Contains**: OAuth tokens and authentication for Claude Code
- **Status**: ✅ **SAFE** - Persisted via volume mount

### 6. **Environment Variables** ✅
- **Location**: `.env` file on host (loaded via `env_file: - .env`)
- **Contains**: API keys, credentials, configuration
- **Status**: ✅ **SAFE** - Loaded from host file, not stored in container

### 7. **Chat History** ✅
- **Location**: Stored in memory/logs directories
- **Status**: ✅ **SAFE** - Persisted via volume mounts

## ⚠️ Things That MAY Be Lost

### 1. **Installed Packages** ⚠️
- **If installed**: Packages installed via `apt-get`, `pip`, etc. after container creation
- **Status**: ⚠️ **LOST** - Unless installed in Dockerfile or via volume-mounted scripts
- **Solution**: Add package installations to `Dockerfile` or `install_additional.sh`

### 2. **Files Created Outside Volumes** ⚠️
- **If created**: Files created in `/a0` subdirectories not covered by volume mounts
- **Status**: ⚠️ **LOST** - Only files in mounted volumes persist
- **Solution**: Ensure important files are in `./memory`, `./knowledge`, `./logs`, or `./tmp`

### 3. **Runtime State** ⚠️
- **If exists**: In-memory state, active sessions, temporary files
- **Status**: ⚠️ **LOST** - Container restart clears runtime state
- **Solution**: This is expected behavior - Agent Zero will reinitialize on startup

### 4. **Custom Installed Tools** ⚠️
- **If installed**: Security tools, custom scripts installed after container creation
- **Status**: ⚠️ **LOST** - Unless added to Dockerfile or installation scripts
- **Solution**: Add to `docker/install_additional.sh` or `Dockerfile`

## 🔍 How to Verify What Will Persist

### Check Volume Mounts
```bash
# List all mounted volumes
docker inspect agent-zero | grep -A 10 "Mounts"

# Or check docker-compose.yml volumes section
cat docker-compose.yml | grep -A 10 "volumes:"
```

### Check Settings File
```bash
# Verify settings.json exists and is persisted
ls -lh ./tmp/settings.json

# View current settings
cat ./tmp/settings.json | python3 -m json.tool
```

### Check Important Data
```bash
# Check memory directory
ls -la ./memory/

# Check knowledge directory
ls -la ./knowledge/

# Check logs
ls -la ./logs/ | tail -10

# Check Claude config
ls -la ./claude-config/
```

## 📋 Pre-Recreation Checklist

Before recreating the container, verify:

- [ ] `./tmp/settings.json` exists (contains your settings)
- [ ] `./memory/` has important data (if any)
- [ ] `./knowledge/` has custom knowledge files (if any)
- [ ] `./logs/` has logs you want to keep
- [ ] `./claude-config/` has OAuth tokens (if Claude Code is authenticated)
- [ ] `.env` file exists on host with API keys

## 🛡️ Safe Recreation Process

### Option 1: Force Recreate (Recommended)
```bash
# This keeps volumes intact, only recreates container
docker compose up -d --force-recreate agent-zero
```

### Option 2: Stop and Start
```bash
# Stop container
docker compose down

# Start with new configuration
docker compose up -d
```

### Option 3: Full Rebuild (Only if Dockerfile changed)
```bash
# Rebuild image and recreate container
docker compose build
docker compose up -d --force-recreate agent-zero
```

## ✅ After Recreation Verification

After recreating, verify everything is intact:

```bash
# 1. Check container is running
docker ps | grep agent-zero

# 2. Check settings loaded
docker exec agent-zero cat /a0/tmp/settings.json | python3 -m json.tool

# 3. Check memory/knowledge accessible
docker exec agent-zero ls -la /a0/memory/
docker exec agent-zero ls -la /a0/knowledge/

# 4. Check Claude Code config
docker exec agent-zero ls -la /root/.config/claude-code/

# 5. Access Web UI
# Open http://localhost:8888 and verify settings are still there
```

## 🎯 Summary

**Good News**: All important settings and data are persisted via volume mounts. Recreating the container will:
- ✅ Keep all Agent Zero settings (`tmp/settings.json`)
- ✅ Keep all memory and knowledge
- ✅ Keep all logs
- ✅ Keep Claude Code OAuth authentication
- ✅ Keep environment variables (from `.env` file)

**Only Lost**: 
- ⚠️ Packages/tools installed after container creation (unless in Dockerfile)
- ⚠️ Files created outside mounted volumes
- ⚠️ Runtime state (expected - will reinitialize)

## 💡 Best Practice

To ensure nothing is lost:
1. Always install packages via Dockerfile or installation scripts
2. Store important files in mounted volumes (`./memory`, `./knowledge`, `./logs`, `./tmp`)
3. Use the Web UI Settings page to configure Agent Zero (saves to `tmp/settings.json`)
4. Keep `.env` file on host (not in container)

**Conclusion**: Recreating the container is **SAFE** - all your settings and data will persist! 🎉
