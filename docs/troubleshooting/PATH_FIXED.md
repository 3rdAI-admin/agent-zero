# ✅ PATH Adjusted in Launch Scripts

## Changes Made

### 1. **launch_a0.py** - Updated
- Now adjusts PATH before any imports
- Removes `~/.local/bin` (where cursor.appimage lives) from PATH
- Prioritizes system Python paths (`/usr/bin`, `/bin`, etc.)
- This prevents cursor.appimage from being used as python3

### 2. **start_server.sh** - Updated  
- Same PATH fix applied
- Ensures system Python is used when activating venv

### 3. **fix_venv.sh** - New Script
- Helper script to recreate the venv properly
- Uses system Python directly to avoid PATH issues

## How to Use

### Option 1: Fix the Virtual Environment First (Recommended)
```bash
cd /home/kali/Tools/agent-zero
bash fix_venv.sh
```

Then launch:
```bash
venv/bin/python launch_a0.py
```

### Option 2: Use the Updated Launch Script
The `launch_a0.py` script now fixes PATH automatically, but you still need a proper venv:
```bash
cd /home/kali/Tools/agent-zero
# First fix venv (one time)
bash fix_venv.sh

# Then launch (PATH is fixed automatically)
python launch_a0.py
```

## What the PATH Fix Does

1. Filters out any PATH entries containing "cursor" or ".local/bin"
2. Prioritizes system directories: `/usr/bin`, `/bin`, `/usr/sbin`, `/sbin`
3. Keeps other valid paths but ensures system Python is found first

This prevents cursor.appimage from being used as python3, eliminating the Cursor window issue.

## A2A Endpoint
Once running: **http://192.168.50.70:8000/a2a**

