#!/bin/bash
# Security tools and wallpaper setup - runs on container start

echo "Checking security tools..."

# Install only if missing
if ! command -v nmap &>/dev/null; then
    echo "Installing security tools..."
    apt-get update -qq
    apt-get install -y -qq nmap masscan netcat-openbsd dnsutils whois 2>/dev/null
    echo "Security tools installed"
else
    echo "Security tools already installed"
fi

# Verify
nmap --version 2>&1 | head -1 || true

echo "Setting up wallpaper..."

# Install feh if missing
if ! command -v feh &>/dev/null; then
    apt-get install -y -qq feh imagemagick 2>/dev/null
fi

# Create wallpaper if missing
mkdir -p /usr/share/wallpapers
if [ ! -f /usr/share/wallpapers/agent-zero.jpg ]; then
    if command -v convert &>/dev/null; then
        convert -size 1920x1080 gradient:"#1a1a2e"-"#16213e" /usr/share/wallpapers/agent-zero.jpg 2>/dev/null
    fi
fi

# Configure fluxbox
mkdir -p /root/.fluxbox
echo "background: none" > /root/.fluxbox/overlay

# Fix fluxbox lastwallpaper to use our wallpaper
echo '$full $full|/usr/share/wallpapers/agent-zero.jpg|style|:99.0' > /root/.fluxbox/lastwallpaper

# Create fehbg script
cat > /root/.fehbg << 'FEHBG'
#!/bin/sh
feh --no-fehbg --bg-fill /usr/share/wallpapers/agent-zero.jpg
FEHBG
chmod +x /root/.fehbg

# Create fluxbox startup with delayed wallpaper
# This ensures wallpaper is set after fluxbox fully starts
cat > /root/.fluxbox/startup << 'STARTUP'
#!/bin/sh
# Set wallpaper after fluxbox starts (handled by supervisor wallpaper program)
# Start fluxbox
exec fluxbox
STARTUP
chmod +x /root/.fluxbox/startup

# Also set wallpaper immediately if display is available
if [ -n "$DISPLAY" ] || [ -e /tmp/.X99-lock ]; then
    export DISPLAY=:99
    (sleep 5 && feh --no-fehbg --bg-fill /usr/share/wallpapers/agent-zero.jpg) &
fi

echo "Wallpaper setup complete"

echo "Setting up keyring for Claude Code..."

# Install keyring with file backend
pip install keyring keyrings.alt --break-system-packages -q 2>/dev/null || true

# Configure keyring to use plaintext file backend
mkdir -p /home/claude/.config /home/claude/.local/share/python_keyring
cat > /home/claude/.config/keyringrc.cfg << 'KEYRINGCFG'
[backend]
default-keyring=keyrings.alt.file.PlaintextKeyring
KEYRINGCFG

chown -R claude:claude /home/claude/.config /home/claude/.local/share/python_keyring 2>/dev/null || true

echo "Keyring setup complete"

echo "Setting up gnome-keyring for Claude Code credentials..."

# Install gnome-keyring if not present
if ! command -v gnome-keyring-daemon &>/dev/null; then
    apt-get install -y -qq gnome-keyring libsecret-1-0 libsecret-tools dbus-x11 2>/dev/null || true
fi

# Create a startup script for gnome-keyring
cat > /usr/local/bin/start-keyring.sh << 'KEYRING_START'
#!/bin/bash
export DISPLAY=:99
eval $(dbus-launch --sh-syntax)
export DBUS_SESSION_BUS_ADDRESS
gnome-keyring-daemon --start --components=secrets
KEYRING_START
chmod +x /usr/local/bin/start-keyring.sh

echo "Gnome-keyring setup complete"

echo "Installing X11 fonts and terminal emulators..."

# Install X11 fonts for Eterm and other terminals
if ! dpkg -l | grep -q xfonts-base 2>/dev/null; then
    apt-get install -y -qq xfonts-base xfonts-100dpi xfonts-75dpi fonts-dejavu-core eterm 2>/dev/null || true
    # Refresh font cache
    mkfontdir /usr/share/fonts/X11/misc 2>/dev/null || true
fi

echo "X11 fonts and terminal setup complete"

echo "Setting up Claude Code onboarding bypass..."

# Create .claude.json in the persisted volume and symlink it
# This ensures onboarding state persists across container restarts
if [ ! -f /home/claude/.claude/.claude.json ]; then
    cat > /home/claude/.claude/.claude.json << 'CLAUDEJSON'
{
  "numImpressions": 10,
  "lastShownAt": 0,
  "lastMcpAcknowledgedAt": 0,
  "lastShownMcpDialogAt": 0
}
CLAUDEJSON
    chown claude:claude /home/claude/.claude/.claude.json 2>/dev/null || true
fi

# Create symlink from home directory to persisted volume
if [ ! -L /home/claude/.claude.json ]; then
    rm -f /home/claude/.claude.json 2>/dev/null || true
    ln -sf /home/claude/.claude/.claude.json /home/claude/.claude.json
    chown -h claude:claude /home/claude/.claude.json 2>/dev/null || true
fi

# Ensure settings.json has onboarding completed
if [ ! -f /home/claude/.claude/settings.json ]; then
    cat > /home/claude/.claude/settings.json << 'SETTINGSJSON'
{
  "hasCompletedOnboarding": true,
  "theme": "dark",
  "preferredNotifChannel": "status_bar"
}
SETTINGSJSON
    chown claude:claude /home/claude/.claude/settings.json 2>/dev/null || true
fi

# Create skills directory to prevent errors
mkdir -p /home/claude/.claude/skills /etc/claude-code/.claude/skills 2>/dev/null || true

echo "Claude Code onboarding bypass complete"
