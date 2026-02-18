#!/bin/bash
# Fix virtual environment to use real Python instead of cursor.appimage

cd /home/kali/Tools/agent-zero

# Fix PATH temporarily to use system Python
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin"

echo "Removing old venv..."
rm -rf venv

echo "Creating new venv with system Python..."
/usr/bin/python3.11 -m venv venv

echo "Verifying venv uses real Python..."
if grep -q "cursor" venv/bin/python 2>/dev/null || readlink -f venv/bin/python | grep -q cursor; then
    echo "ERROR: Venv still pointing to cursor.appimage"
    exit 1
fi

echo "Upgrading pip..."
venv/bin/pip install --upgrade pip -q

echo "Installing dependencies..."
venv/bin/pip install -r requirements.txt -q
venv/bin/pip install -r requirements2.txt -q

echo "Installing Playwright browsers..."
venv/bin/python -m playwright install chromium -q

echo "✓ Virtual environment fixed and ready!"
echo ""
echo "To launch Agent Zero:"
echo "  cd /home/kali/Tools/agent-zero"
echo "  venv/bin/python launch_a0.py"

