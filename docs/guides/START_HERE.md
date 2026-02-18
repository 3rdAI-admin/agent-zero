# 🚨 IMPORTANT: How to Fix the Cursor Windows Issue

## The Problem
Your `~/.local/bin/cursor.appimage` is in your PATH and is being used as `python3`. This causes:
- Every Python command to open a Cursor window
- Virtual environments to symlink to cursor.appimage instead of real Python

## The Fix (Run in a Regular Terminal)

### Option 1: Use System Python Directly (Recommended)
```bash
cd /home/kali/Tools/agent-zero
rm -rf venv
/usr/bin/python3.11 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
venv/bin/pip install -r requirements2.txt
venv/bin/python -m playwright install chromium
```

Then launch using the venv Python directly:
```bash
cd /home/kali/Tools/agent-zero
venv/bin/python launch_a0.py
```

### Option 2: Fix Your PATH Temporarily
```bash
cd /home/kali/Tools/agent-zero
export PATH=/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements2.txt
python -m playwright install chromium
python launch_a0.py
```

### Option 3: Use System Python Without Venv (Quick Test)
```bash
cd /home/kali/Tools/agent-zero
/usr/bin/python3.11 -m pip install --user -r requirements.txt
/usr/bin/python3.11 -m pip install --user -r requirements2.txt
WEB_UI_HOST=0.0.0.0 WEB_UI_PORT=8000 /usr/bin/python3.11 run_ui.py
```

## Verify It's Fixed
```bash
venv/bin/python -c "import sys; print(sys.executable)"
# Should show: /usr/bin/python3.11 (NOT cursor.appimage)
```

## A2A Endpoint
Once running: **http://192.168.50.70:8000/a2a**

