# Claude Code After Container Restart

## ✅ Current Status

**Claude Code is installed** in the running container at `/root/.local/bin/claude`

## What Happens on Restart

### Scenario 1: Simple Restart (Recommended)
```bash
docker compose restart
# OR
docker restart agent-zero
```

**Result**: ✅ **Claude Code will work**
- Container filesystem persists
- Claude Code binary remains at `/root/.local/bin/claude`
- Symlinks remain at `/usr/local/bin/claude` and `/usr/local/bin/claude-pro`
- OAuth config persists (volume-mounted)

### Scenario 2: Stop and Start
```bash
docker compose down
docker compose up -d
```

**Result**: ✅ **Claude Code will work**
- Container filesystem persists (unless you remove volumes)
- Everything remains intact

### Scenario 3: Rebuild Container
```bash
docker compose build
docker compose down
docker compose up -d
```

**Result**: ✅ **Claude Code will work** (after rebuild)
- Installation is now in `install_additional.sh`
- Claude Code will be installed during Docker build
- Takes a few minutes during build process

### Scenario 4: Complete Rebuild (No Cache)
```bash
docker compose build --no-cache
docker compose down
docker compose up -d
```

**Result**: ✅ **Claude Code will work** (after rebuild)
- Takes longer but ensures fresh installation
- Claude Code installed during build

## Important Notes

### What Persists
- ✅ **OAuth Config**: Volume-mounted (`./claude-config:/root/.config/claude-code`)
- ✅ **Container Filesystem**: Persists across restarts (not rebuilds)

### What Needs Rebuild
- ⚠️ **Claude Code Binary**: Currently in container filesystem, not image
- ✅ **After rebuild**: Will be in image (via `install_additional.sh`)

## Quick Test

After restart, verify Claude Code works:

```bash
# Check version
docker exec agent-zero claude-pro --version

# Check if it's in PATH
docker exec agent-zero which claude-pro

# Test command
docker exec agent-zero claude-pro --help
```

## Summary

**Simple restart**: ✅ Claude Code works (filesystem persists)  
**Rebuild**: ✅ Claude Code works (installed during build)  
**OAuth**: ✅ Persists (volume-mounted)

**Answer**: Yes, Claude Code will work after restart! 🎉
