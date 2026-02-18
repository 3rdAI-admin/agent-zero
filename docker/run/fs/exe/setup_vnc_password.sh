#!/bin/bash
# Setup VNC password file if it doesn't exist
if [ ! -f /root/.vnc/passwd ]; then
    mkdir -p /root/.vnc
    # Set password using stdin (more reliable method)
    (echo "vnc123"; echo "vnc123") | x11vnc -storepasswd /root/.vnc/passwd 2>&1
    chmod 600 /root/.vnc/passwd
    echo "VNC password file created with password: vnc123"
fi
