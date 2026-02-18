# Fixing Kali Linux Repository Issues

If you're seeing 404 errors and GPG key errors when updating Kali Linux, follow these steps:

## Quick Fix (Recommended)

Run the complete automated fix script (handles everything):
```bash
sudo bash fix_kali_complete.sh
```

This will:
1. Fix repository URLs
2. Add GPG key (tries multiple methods)
3. Update package lists

Or use the individual scripts:
```bash
# Just fix repository URLs
sudo bash fix_kali_sources.sh

# Original script (GPG key only)
sudo bash fix_kali_repo.sh
```

## Manual Fix

## Problem
- 404 errors for Node.js packages
- GPG key error: `NO_PUBKEY ED65462EC8D5E4C5`
- Repository signature verification failures

## Solution

### Step 1: Fix GPG Key
```bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5
```

### Step 2: Update Repository Sources
```bash
# Check current sources
cat /etc/apt/sources.list.d/kali.sources

# Update to use kali.download instead of http.kali.org
sudo sed -i 's|http://http.kali.org/kali|http://kali.download/kali|g' /etc/apt/sources.list.d/kali.sources
```

### Step 3: Update Package Lists
```bash
sudo apt-get update
```

### Alternative: Use HTTPS Mirror
If issues persist, try using HTTPS:
```bash
sudo sed -i 's|http://kali.download/kali|https://kali.download/kali|g' /etc/apt/sources.list.d/kali.sources
sudo apt-get update
```

## Important Note

**Agent Zero does NOT require Node.js or npm** - these packages are not dependencies for Agent Zero. The errors you're seeing are from a system-wide package update, not from Agent Zero installation.

Agent Zero only requires:
- Python 3.11+
- Python packages (installed via pip in venv)
- Playwright browsers (installed via Python)

If you don't need Node.js for other purposes, you can skip installing it.

## Verify Agent Zero Dependencies

Agent Zero dependencies are installed via pip:
```bash
cd /home/kali/Tools/agent-zero
source venv/bin/activate
pip list | grep -E "flask|playwright|litellm"
```

All required packages should be in the virtual environment, not system packages.

