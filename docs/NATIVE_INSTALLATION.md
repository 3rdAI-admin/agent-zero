# Native Installation Guide for Agent Zero

This guide covers installing and configuring Agent Zero on a native Linux system (without Docker), specifically for Kali Linux.

## Overview

Agent Zero can run natively on Linux systems without Docker. This is useful for:
- Direct system access without container overhead
- Integration with system tools (penetration testing tools, etc.)
- Full access to host resources
- Development and customization

## Prerequisites

- Python 3.11 or higher
- Kali Linux (or similar Debian-based distribution)
- Network access to Ollama instance (or API keys for cloud models)
- At least 4GB RAM (8GB+ recommended)

## Installation Steps

### 1. Install System Dependencies

```bash
# Install Python and venv support
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install other dependencies (if needed)
sudo apt install -y build-essential curl git
```

### 2. Clone or Download Agent Zero

```bash
cd ~/Tools
git clone https://github.com/agent0ai/agent-zero.git
cd agent-zero
```

### 3. Create Virtual Environment

**Important:** Ensure system Python is used, not Cursor or other wrappers.

```bash
# Fix PATH to use system Python
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin"

# Create venv with system Python
/usr/bin/python3.11 -m venv venv

# Verify venv uses real Python (not cursor.appimage)
readlink -f venv/bin/python
# Should show: /usr/bin/python3.11 or similar, NOT cursor.appimage
```

### 4. Install Python Dependencies

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements2.txt
```

### 5. Install Playwright Browsers

```bash
python -m playwright install chromium
```

## Configuration

### 1. Network Access Configuration

Agent Zero needs to be configured to accept connections from your network.

**Option A: Using launch script (Recommended)**

Use the provided `launch_a0_direct.py` which sets environment variables:

```bash
python launch_a0_direct.py
```

**Option B: Manual environment variables**

```bash
export WEB_UI_HOST=0.0.0.0
export WEB_UI_PORT=8000
export ALLOWED_ORIGINS="*://localhost:*,*://127.0.0.1:*,*://0.0.0.0:*,*://YOUR_IP:*"
python run_ui.py
```

### 2. Model Configuration

For native installs, configure models via Settings in the Web UI or by editing `tmp/settings.json`.

**Recommended for Penetration Testing:**
```json
{
  "chat_model_provider": "ollama",
  "chat_model_name": "qwen3:latest",
  "chat_model_api_base": "http://YOUR_OLLAMA_IP:11434",
  "util_model_provider": "ollama",
  "util_model_name": "phi3:latest",
  "util_model_api_base": "http://YOUR_OLLAMA_IP:11434",
  "browser_model_provider": "ollama",
  "browser_model_name": "qwen3:latest",
  "browser_model_api_base": "http://YOUR_OLLAMA_IP:11434"
}
```

### 3. Code Execution Configuration

**Critical:** For native installs, set `shell_interface` to `"local"`:

```json
{
  "shell_interface": "local"
}
```

This allows code execution to work locally without SSH or root password.

### 4. RFC Password Configuration

Set an RFC password for development features:

```bash
# Generate secure password
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env file
echo "RFC_PASSWORD=your_generated_password" >> .env
```

Or configure via Web UI: Settings → Development → RFC Password

## Launching Agent Zero

### Quick Start (Recommended)

Use the startup script:

```bash
./startup.sh
```

This script:
- Stops any running instances
- Checks port availability
- Updates from git (if repository)
- Starts Agent Zero with proper configuration

### Manual Launch

```bash
source venv/bin/activate
python launch_a0_direct.py
```

Or:

```bash
source venv/bin/activate
export WEB_UI_HOST=0.0.0.0
export WEB_UI_PORT=8000
python run_ui.py
```

## Key Differences from Docker Installation

### 1. Path Handling

- **Docker:** Uses `/a0/...` paths
- **Native:** Uses actual filesystem paths (e.g., `/home/kali/Tools/agent-zero/...`)

The code execution tool automatically handles this difference.

### 2. Code Execution

- **Docker:** Can use SSH to container or local execution
- **Native:** Uses local execution only (set `shell_interface: "local"`)

### 3. Project Directories

- **Docker:** Projects in `/a0/usr/projects/`
- **Native:** Projects in `{agent-zero-dir}/usr/projects/`

### 4. Environment Variables

Native installs require explicit environment variable configuration:
- `WEB_UI_HOST` (default: `localhost`, set to `0.0.0.0` for network access)
- `WEB_UI_PORT` (default: `5000`)
- `ALLOWED_ORIGINS` (for CORS/CSRF protection)

## Troubleshooting

### Issue: "No such file or directory: '/a0/usr/projects/...'"

**Solution:** This is fixed in the code. Ensure you're using the latest version where `get_cwd()` returns actual paths for native installs.

### Issue: "No RFC password, cannot handle RFC calls"

**Solution:** Set RFC password in `.env` or via Settings UI:
```bash
echo "RFC_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
```

### Issue: Code execution tool blocked / requires root password

**Solution:** Set `shell_interface` to `"local"` in settings:
```json
{
  "shell_interface": "local"
}
```

### Issue: Cursor.appimage interfering with Python

**Solution:** Use `launch_a0_direct.py` which fixes PATH, or manually:
```bash
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin:$(echo $PATH | tr ':' '\n' | grep -v cursor | tr '\n' ':' | sed 's/:$//')"
```

### Issue: Virtual environment links to cursor.appimage

**Solution:** Recreate venv with system Python:
```bash
rm -rf venv
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin"
/usr/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements2.txt
```

### Issue: "Origin not allowed" error

**Solution:** Add your IP to `ALLOWED_ORIGINS`:
```bash
export ALLOWED_ORIGINS="*://localhost:*,*://127.0.0.1:*,*://0.0.0.0:*,*://YOUR_IP:*"
```

Or update `launch_a0_direct.py` to include your IP.

## File Structure

```
agent-zero/
├── launch_a0_direct.py      # Launch script with PATH fix
├── startup.sh               # Automated startup script
├── run_ui.py                # Main server entry point
├── venv/                    # Python virtual environment
├── .env                     # Environment variables (RFC_PASSWORD, etc.)
├── tmp/
│   └── settings.json        # Agent Zero settings
├── usr/
│   └── projects/            # Project directories
└── python/                  # Framework code
```

## Security Considerations

1. **Network Access:** When binding to `0.0.0.0`, ensure firewall rules are configured
2. **Authentication:** Set up UI login/password if exposing to network:
   ```bash
   echo "AUTH_LOGIN=your_username" >> .env
   echo "AUTH_PASSWORD=your_password" >> .env
   ```
3. **RFC Password:** Use strong, randomly generated passwords
4. **File Permissions:** Ensure project directories have appropriate permissions

## Best Practices

1. **Use startup.sh:** Automates common tasks and ensures proper configuration
2. **Monitor Logs:** Check `/tmp/a0_*.log` for errors
3. **Backup Settings:** Regularly backup `tmp/settings.json` and `.env`
4. **Update Regularly:** Pull latest changes from git repository
5. **Resource Monitoring:** Monitor CPU/RAM usage, especially with large models

## Advanced Configuration

### Custom Model Providers

Configure custom Ollama instances or other providers in `tmp/settings.json`:

```json
{
  "chat_model_provider": "ollama",
  "chat_model_api_base": "http://custom-ollama-server:11434"
}
```

### Development Mode

For development with RFC features:
1. Set RFC password
2. Configure RFC URL and ports in Settings
3. Ensure both instances use same RFC password

## Support

For issues specific to native installation:
- Check logs in `/tmp/a0_*.log`
- Verify Python version: `python3 --version` (should be 3.11+)
- Verify venv: `which python` (should point to venv, not system)
- Check network: `netstat -tlnp | grep 8000` or `ss -tlnp | grep 8000`

## Summary

Native installation provides:
- ✅ Direct system access
- ✅ No Docker overhead
- ✅ Full integration with host tools
- ✅ Easier debugging and development

Key configuration points:
- Set `shell_interface: "local"` for code execution
- Configure `ALLOWED_ORIGINS` for network access
- Use `launch_a0_direct.py` or `startup.sh` for proper PATH handling
- Set RFC password for development features

