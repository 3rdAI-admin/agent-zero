#!/usr/bin/env python3
"""Launch Agent Zero server - uses venv Python directly to avoid Cursor interference"""
import os
import sys

# Use the venv Python directly (bypasses PATH issues)
venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
if os.path.exists(venv_python):
    # Check if it's actually Python or cursor
    import subprocess
    result = subprocess.run([venv_python, '--version'], capture_output=True, text=True)
    if 'cursor' in result.stdout.lower() or 'cursor' in result.stderr.lower():
        print("ERROR: Virtual environment is still pointing to cursor.appimage")
        print("Please run this in a regular terminal and use the system Python:")
        print("  /usr/bin/python3.11 -m venv --clear venv")
        sys.exit(1)

# Set environment variables before any imports
os.environ['WEB_UI_HOST'] = '0.0.0.0'
os.environ['WEB_UI_PORT'] = '8000'

# Change to the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Now import and run
if __name__ == '__main__':
    import run_ui
    run_ui.run()

