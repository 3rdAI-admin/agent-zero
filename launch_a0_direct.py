#!/usr/bin/env python3
"""Launch Agent Zero server - uses venv Python if available, otherwise system Python"""
import os
import sys

# Get script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check if we're running in a venv
in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

# Always try to add venv site-packages first (before any imports)
venv_site_packages = os.path.join(SCRIPT_DIR, 'venv', 'lib', 'python3.11', 'site-packages')
if os.path.exists(venv_site_packages):
    # Remove from path if already there, then insert at beginning
    if venv_site_packages in sys.path:
        sys.path.remove(venv_site_packages)
    sys.path.insert(0, venv_site_packages)
    # Remove user site-packages to avoid conflicts with venv
    sys.path = [p for p in sys.path if '.local/lib/python3.11/site-packages' not in p]
    # Re-insert venv at the beginning
    if venv_site_packages not in sys.path:
        sys.path.insert(0, venv_site_packages)

# Only add user site-packages if NOT in a venv
if not in_venv:
    user_site = os.path.expanduser('~/.local/lib/python3.11/site-packages')
    if os.path.exists(user_site) and user_site not in sys.path:
        sys.path.insert(0, user_site)

# Fix PATH to prioritize system Python over cursor.appimage
current_path = os.environ.get('PATH', '')
path_parts = current_path.split(':')
filtered_path = [p for p in path_parts if 'cursor' not in p.lower() and '.local/bin' not in p]
system_paths = ['/usr/bin', '/bin', '/usr/sbin', '/sbin', '/usr/local/bin', '/usr/local/sbin']
new_path = ':'.join(system_paths + [p for p in filtered_path if p not in system_paths])
os.environ['PATH'] = new_path

# Set environment variables before any imports
os.environ['WEB_UI_HOST'] = '0.0.0.0'
os.environ['WEB_UI_PORT'] = '8000'
# Allow access from the network IP
os.environ['ALLOWED_ORIGINS'] = '*://localhost:*,*://127.0.0.1:*,*://0.0.0.0:*,*://192.168.50.70:*'

# Change to the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Now import and run
if __name__ == '__main__':
    import run_ui
    run_ui.run()

