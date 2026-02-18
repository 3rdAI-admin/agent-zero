# ⚠️ IMPORTANT: Virtual Environment Issue Fixed

## Problem
The virtual environment was incorrectly symlinked to `cursor.appimage` instead of the real Python interpreter. This caused:
- Every Python command to launch a new Cursor window
- Server startup failures
- Command-line arguments being intercepted by Cursor's Electron wrapper

## Solution Applied
The virtual environment has been recreated using the system Python (`/usr/bin/python3.11`) directly, bypassing any symlinks or aliases.

## Verification
The venv now uses the real Python interpreter. You can verify with:
```bash
cd /home/kali/Tools/agent-zero
venv/bin/python --version
```

## Next Steps
You can now safely launch the server without opening Cursor windows:
```bash
cd /home/kali/Tools/agent-zero
source venv/bin/activate
python launch_a0.py
```

The dependencies may need to be reinstalled since we recreated the venv. If you get import errors, run:
```bash
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements2.txt
python -m playwright install chromium
```

