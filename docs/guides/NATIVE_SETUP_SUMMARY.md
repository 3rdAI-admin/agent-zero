# Native Installation Quick Reference

This is a quick reference for native Agent Zero installations. For detailed documentation, see [docs/NATIVE_INSTALLATION.md](docs/NATIVE_INSTALLATION.md).

## Quick Setup

```bash
# 1. Install dependencies
sudo apt install python3.11 python3.11-venv

# 2. Create venv (use system Python, not cursor)
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin"
/usr/bin/python3.11 -m venv venv

# 3. Install packages
source venv/bin/activate
pip install -r requirements.txt -r requirements2.txt
python -m playwright install chromium

# 4. Launch
./startup.sh
```

## Critical Configuration

### 1. Shell Interface (Required for Code Execution)
```json
// In tmp/settings.json
{
  "shell_interface": "local"  // NOT "ssh" for native installs
}
```

### 2. Network Access
```bash
# In launch_a0_direct.py or .env
WEB_UI_HOST=0.0.0.0
WEB_UI_PORT=8000
ALLOWED_ORIGINS="*://localhost:*,*://127.0.0.1:*,*://0.0.0.0:*,*://YOUR_IP:*"
```

### 3. RFC Password (For Development Features)
```bash
# Generate and set
echo "RFC_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
```

## Key Files

- `launch_a0_direct.py` - Launch script with PATH fixes
- `startup.sh` - Automated startup (stops old, updates, starts)
- `.env` - Environment variables (RFC_PASSWORD, AUTH_LOGIN, etc.)
- `tmp/settings.json` - Agent Zero configuration

## Common Issues

| Issue | Solution |
|-------|----------|
| `/a0/usr/projects/...` not found | Fixed in code - returns actual paths for native |
| Code execution blocked | Set `shell_interface: "local"` |
| RFC password error | Set `RFC_PASSWORD` in `.env` |
| Cursor.appimage interference | Use `launch_a0_direct.py` or fix PATH |
| Origin not allowed | Add IP to `ALLOWED_ORIGINS` |

## Model Configuration (Penetration Testing)

Recommended setup:
```json
{
  "chat_model_provider": "ollama",
  "chat_model_name": "qwen3:latest",
  "util_model_provider": "ollama",
  "util_model_name": "phi3:latest",
  "browser_model_provider": "ollama",
  "browser_model_name": "qwen3:latest",
  "chat_model_api_base": "http://YOUR_OLLAMA_IP:11434",
  "util_model_api_base": "http://YOUR_OLLAMA_IP:11434",
  "browser_model_api_base": "http://YOUR_OLLAMA_IP:11434"
}
```

## Launch Commands

```bash
# Automated (recommended)
./startup.sh

# Manual
source venv/bin/activate
python launch_a0_direct.py

# Or with environment variables
source venv/bin/activate
WEB_UI_HOST=0.0.0.0 WEB_UI_PORT=8000 python run_ui.py
```

## Verification

After setup, verify:
1. ✅ Server listening: `netstat -tlnp | grep 8000`
2. ✅ Web UI accessible: `curl http://YOUR_IP:8000`
3. ✅ Code execution works: Try a simple command in Agent Zero
4. ✅ Projects work: Create/activate a project and verify paths

## Differences from Docker

| Feature | Docker | Native |
|---------|--------|--------|
| Paths | `/a0/...` | Actual filesystem paths |
| Code Execution | SSH or local | Local only (`shell_interface: "local"`) |
| Projects | `/a0/usr/projects/` | `{install-dir}/usr/projects/` |
| Configuration | Via UI or env | Via UI, env, or settings.json |

For complete documentation, see [docs/NATIVE_INSTALLATION.md](docs/NATIVE_INSTALLATION.md).

