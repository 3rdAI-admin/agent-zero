#!/usr/bin/env python3
"""Launch Agent Zero server with proper configuration"""
import os
import sys

# Fix PATH to prioritize system Python over cursor.appimage
# Remove ~/.local/bin from PATH to avoid cursor.appimage being used as python3
current_path = os.environ.get('PATH', '')
path_parts = current_path.split(':')
# Filter out ~/.local/bin and /home/kali/.local/bin
filtered_path = [p for p in path_parts if 'cursor' not in p.lower() and '.local/bin' not in p]
# Ensure system paths are first
system_paths = ['/usr/bin', '/bin', '/usr/sbin', '/sbin', '/usr/local/bin', '/usr/local/sbin']
# Combine system paths with filtered user paths
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

