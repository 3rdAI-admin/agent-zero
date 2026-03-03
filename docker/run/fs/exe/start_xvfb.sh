#!/bin/bash
# start_xvfb.sh — Clean up stale X lock files, then exec Xvfb.
#
# Reason: When the container restarts (or supervisor restarts xvfb),
# /tmp/.X99-lock and /tmp/.X11-unix/X99 from the previous run may
# still exist.  Xvfb refuses to start if it finds these ("Server is
# already active for display 99"), exits 1, supervisor retries, and
# eventually marks the process FATAL — cascading to fluxbox, x11vnc,
# and autocutsel as well.
#
# This wrapper removes the stale artefacts before launching Xvfb so
# the server can bind display :99 cleanly on every attempt.

DISPLAY_NUM=99

# Remove stale lock file
rm -f "/tmp/.X${DISPLAY_NUM}-lock"

# Remove stale Unix socket
rm -f "/tmp/.X11-unix/X${DISPLAY_NUM}"

# Ensure the X11-unix directory exists with correct permissions
mkdir -p /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix

# Exec into Xvfb so supervisor manages the real process (not a shell wrapper)
exec /usr/bin/Xvfb ":${DISPLAY_NUM}" -screen 0 1920x1080x24 -ac +extension GLX +render -noreset
