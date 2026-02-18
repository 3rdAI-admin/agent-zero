# Installing Claude Code for Agent Zero

## Quick Install

Run this command to install Claude Code in the container:

```bash
docker exec agent-zero bash -c 'curl -fsSL https://claude.ai/install.sh | bash'
```

Then create symlinks for easy access:

```bash
docker exec agent-zero bash -c 'ln -sf ~/.local/bin/claude /usr/local/bin/claude && ln -sf ~/.local/bin/claude /usr/local/bin/claude-pro'
```

## Persistent Installation (Recommended)

To make Claude Code installation persistent across container rebuilds, add it to the Docker build:

### Option 1: Add to install_additional.sh

Edit `/docker/run/fs/ins/install_additional.sh` and add:

```bash
echo "====================INSTALLING CLAUDE CODE===================="

# Install Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# Create symlinks
ln -sf ~/.local/bin/claude /usr/local/bin/claude
ln -sf ~/.local/bin/claude /usr/local/bin/claude-pro

# Ensure PATH includes ~/.local/bin
echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.profile

echo "====================CLAUDE CODE INSTALLED===================="
```

### Option 2: Manual Installation Script

Create `/docker/run/fs/exe/install_claude_code.sh`:

```bash
#!/bin/bash
# Install Claude Code if not already installed
if [ ! -f /root/.local/bin/claude ]; then
    curl -fsSL https://claude.ai/install.sh | bash
    ln -sf ~/.local/bin/claude /usr/local/bin/claude
    ln -sf ~/.local/bin/claude /usr/local/bin/claude-pro
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.bashrc
    echo "Claude Code installed"
else
    echo "Claude Code already installed"
fi
```

Make it executable:
```bash
chmod +x /docker/run/fs/exe/install_claude_code.sh
```

## Verify Installation

After installation, verify:

```bash
docker exec agent-zero bash -c 'export PATH="$HOME/.local/bin:$PATH" && claude-pro --version'
```

## OAuth Authentication

Claude Code requires OAuth authentication. The config directory is already volume-mounted:

- Host: `./claude-config`
- Container: `/root/.config/claude-code`

To authenticate:

1. **Via VNC** (recommended):
   - Connect to VNC: `vnc://localhost:5901`
   - Open terminal
   - Run: `claude-pro`
   - Complete OAuth flow in browser

2. **Via terminal** (if you can handle CAPTCHA):
   ```bash
   docker exec -it agent-zero bash
   export PATH="$HOME/.local/bin:$PATH"
   claude-pro
   ```

## Testing Agent Zero Integration

Once installed and authenticated, test with Agent Zero:

**Via Web UI:**
1. Go to http://localhost:8888
2. Ask: "Use Claude Code (claude-pro) to generate a Python hello world script"
3. Agent Zero will invoke Claude Code and execute the code

**Via Terminal:**
```bash
# Start Agent Zero
docker exec agent-zero python3 /a0/agent.py

# Then interact with it, asking to use Claude Code
```

## Troubleshooting

### Claude Code Not Found
```bash
# Check installation
docker exec agent-zero ls -la /root/.local/bin/claude

# Check PATH
docker exec agent-zero bash -c 'echo $PATH'

# Reinstall
docker exec agent-zero bash -c 'curl -fsSL https://claude.ai/install.sh | bash'
```

### OAuth Issues
- Check config directory: `docker exec agent-zero ls -la /root/.config/claude-code/`
- Re-authenticate via VNC if needed
- See `CLAUDE_CODE_AUTH.md` for detailed steps

### PATH Issues
Agent Zero's `code_execution_tool` may need PATH explicitly set. You can:

1. **Set in tool call** (Agent Zero will do this automatically if configured)
2. **Update .bashrc** (already done if using install script above)
3. **Use full path**: `/root/.local/bin/claude-pro` instead of `claude-pro`
