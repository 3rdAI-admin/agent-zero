# Agent Zero Startup Script

## Overview
The `startup.sh` script automates the process of starting Agent Zero with proper checks and updates.

## What it does:
1. **Checks for running instances** - Finds and stops any existing Agent Zero processes
2. **Verifies port availability** - Ensures port 8000 is free
3. **Updates files** - Pulls latest changes from git (if repository)
4. **Checks dependencies** - Verifies Python is available
5. **Starts Agent Zero** - Launches the server with proper configuration

## Usage

### Basic usage:
```bash
cd /home/kali/Tools/agent-zero
./startup.sh
```

### What happens:
- Stops any running Agent Zero instances
- Updates from git (if repository and no uncommitted changes)
- Starts Agent Zero in the background
- Displays status and endpoints

## Features

### Automatic Process Management
- Gracefully stops existing instances (SIGTERM)
- Force kills if needed (SIGKILL)
- Waits for port to be released

### Git Integration
- Automatically detects if it's a git repository
- Pulls latest changes (if no uncommitted changes)
- Skips update if you have local changes (to prevent conflicts)

### Logging
- Creates timestamped log files in `/tmp/`
- Log file format: `a0_startup_YYYYMMDD_HHMMSS.log`
- Shows log file location after startup

### Status Display
- Shows process ID
- Displays network endpoints (Web UI and A2A)
- Provides commands to stop or view logs

## Stopping Agent Zero

### Using the process ID:
```bash
kill <PID>
```

### Using pkill:
```bash
pkill -f launch_a0_direct
```

### View logs:
```bash
tail -f /tmp/a0_startup_*.log
```

## Configuration

The script uses:
- **Python**: `/usr/bin/python3.11` (or auto-detected)
- **Launch script**: `launch_a0_direct.py`
- **Port**: `8000`
- **Log directory**: `/tmp/`

## Troubleshooting

### Port already in use:
- The script will try to stop existing processes
- If port is still in use, check manually: `netstat -tlnp | grep 8000`

### Process dies immediately:
- Check the log file for errors
- Verify Python dependencies are installed
- Check that `launch_a0_direct.py` exists

### Git update fails:
- This is OK if you're offline or not using git
- The script will continue and start Agent Zero anyway

