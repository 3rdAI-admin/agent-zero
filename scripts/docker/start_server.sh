#!/bin/bash
cd /home/kali/Tools/agent-zero

# Fix PATH to prioritize system Python over cursor.appimage
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin:$(echo $PATH | tr ':' '\n' | grep -v cursor | grep -v '\.local/bin' | tr '\n' ':' | sed 's/:$//')"

source venv/bin/activate
export WEB_UI_HOST=0.0.0.0
export WEB_UI_PORT=8000
exec python run_ui.py

