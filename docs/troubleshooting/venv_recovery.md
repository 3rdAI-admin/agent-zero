# Corrupted Python Virtual Environment Recovery

## Symptom

- `code_execution_tool` fails with "null bytes error" when invoking venv Python
- Error: `bad magic number in <venv_path>/lib/python3.x/...`
- Python interpreter crashes or reports corrupted bytecode
- ImportError: cannot import name from partially initialized module

## Root Cause

Project venv interpreter corrupted due to:
- Disk I/O error during package installation
- Incomplete write operation
- Docker container restart mid-install
- File system issues (disk full, permissions)

## Fix

### 1. Remove Corrupted Venv

```bash
# Identify the corrupted venv path from error message
# Example: /a0/usr/workdir/google_api_env

rm -rf /a0/usr/workdir/google_api_env
```

### 2. Recreate Venv

```bash
python3 -m venv /a0/usr/workdir/google_api_env
```

### 3. Reinstall Requirements

If you have a requirements file for the project:

```bash
/a0/usr/workdir/google_api_env/bin/pip install -r requirements.txt
```

Or install packages individually:

```bash
/a0/usr/workdir/google_api_env/bin/pip install google-api-python-client google-auth
```

### 4. Test

```bash
/a0/usr/workdir/google_api_env/bin/python3 --version
/a0/usr/workdir/google_api_env/bin/python3 -c "import googleapiclient; print('OK')"
```

## Prevention

### Use Main Venv for Common Packages

Agent Zero's main venv (`/opt/venv-a0/`) now includes Google API client packages (since IMPROVE.md Task 6):

```bash
# For Google API scripts, use main venv instead of project venv:
/opt/venv-a0/bin/python3 script.py

# Or use code_execution_tool with runtime="python" (uses main venv)
```

Main venv packages:
- `google-auth>=2.35.0`
- `google-api-python-client>=2.150.0`
- All standard Agent Zero dependencies

### Check Disk Space Before Installing

```bash
df -h /a0
# Ensure at least 1GB free before installing packages
```

### Use --no-cache-dir for pip

Reduces disk usage and avoids cache corruption:

```bash
/path/to/venv/bin/pip install --no-cache-dir package_name
```

## Alternative: Use Main Venv

If you're working with Google APIs (Drive, Gmail, Sheets, Slides), use the main venv instead of creating project-specific venvs:

```bash
# Main venv (pre-configured with Google API client)
/opt/venv-a0/bin/python3 your_script.py
```

See `knowledge/main/google_apis.md` for Google API usage patterns.

## Troubleshooting

### Error: "No module named 'venv'"

Install venv package:

```bash
apt-get update && apt-get install -y python3-venv
```

### Error: "Permission denied" when removing venv

Use sudo or run from container with root user:

```bash
docker exec -it agent-zero bash
cd /a0/usr/workdir
rm -rf google_api_env
```

### Venv Recreated but Still Corrupted

Check underlying file system:

```bash
# Check disk errors
dmesg | grep -i error

# Check filesystem
df -h /a0

# Force sync
sync

# If persistent, remount the Docker volume or restart container
```

## Related Documentation

- [Google API Integration](../../knowledge/main/google_apis.md)
- [Pre-installed Tools](../../knowledge/main/preinstalled_tools.md)
- [Code Execution Tool](../guides/usage.md#code-execution)
