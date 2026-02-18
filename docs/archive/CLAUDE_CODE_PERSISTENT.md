# Making Claude Code Installation Persistent

## ✅ Changes Applied

Claude Code installation has been added to the Docker build process to make it persistent across container rebuilds.

## Files Updated

### 1. `/docker/run/fs/ins/install_additional.sh`
- Added Claude Code installation step
- Creates symlinks (`claude` and `claude-pro`)
- Configures PATH in `.bashrc` and `.profile`

### 2. `/docker/run/fs/per/root/.bashrc`
- Added `export PATH="$HOME/.local/bin:$PATH"` for Claude Code

### 3. `/docker/run/fs/per/root/.profile`
- Added `export PATH="$HOME/.local/bin:$PATH"` for Claude Code

## How It Works

When the Docker image is built:
1. `install_additional.sh` runs during build
2. Claude Code is installed via `curl -fsSL https://claude.ai/install.sh | bash`
3. Symlinks are created at `/usr/local/bin/claude` and `/usr/local/bin/claude-pro`
4. PATH is configured in shell config files
5. Everything is baked into the Docker image

## Applying Changes

To apply these changes:

```bash
# Rebuild the container
docker compose build

# Restart the container
docker compose down
docker compose up -d

# Verify Claude Code is installed
docker exec agent-zero claude-pro --version
```

## Verification

After rebuild, verify:

```bash
# Check installation
docker exec agent-zero which claude-pro
docker exec agent-zero claude-pro --version

# Check PATH
docker exec agent-zero bash -c 'echo $PATH' | grep local

# Check symlinks
docker exec agent-zero ls -la /usr/local/bin/claude*
```

## OAuth Authentication

**Important**: Claude Code OAuth tokens are already persistent via volume mount:
- Host: `./claude-config`
- Container: `/root/.config/claude-code`

After rebuild, if OAuth is needed:
1. Connect via VNC: `vnc://localhost:5901` (password: `vnc123`)
2. Open terminal
3. Run: `claude-pro`
4. Complete OAuth flow

## Benefits

✅ **Persistent Installation**: Claude Code survives container rebuilds
✅ **Automatic Setup**: No manual installation needed
✅ **PATH Configured**: Available in all shell sessions
✅ **Symlinks Created**: Easy access via `claude` and `claude-pro`
✅ **OAuth Persists**: Config directory is volume-mounted

## Notes

- Installation happens during Docker build (takes a few minutes)
- If installation fails during build, it will retry at runtime
- OAuth authentication is separate and persists via volume mount
- Agent Zero can use Claude Code immediately after rebuild
