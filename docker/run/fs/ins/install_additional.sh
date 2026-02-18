#!/bin/bash
set -e

# install playwright - moved to install A0
# bash /ins/install_playwright.sh "$@"

# searxng - moved to base image
# bash /ins/install_searxng.sh "$@"

echo "====================INSTALLING PYTHON AND DEVELOPMENT TOOLS===================="

# Update package list
apt-get update

# Install Python and development tools
apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    python3-venv

# Create python symlink if it doesn't exist
if [ ! -f /usr/bin/python ]; then
    ln -sf /usr/bin/python3 /usr/bin/python
fi

# Create pip symlink if it doesn't exist
if [ ! -f /usr/bin/pip ]; then
    ln -sf /usr/bin/pip3 /usr/bin/pip
fi

echo "====================PYTHON INSTALLED===================="

echo "====================INSTALLING VNC AND GUI COMPONENTS===================="

# Update package list
apt-get update

# Install VNC server components
apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    fluxbox \
    autocutsel

# Install GUI applications
apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    lxterminal \
    xterm \
    mousepad \
    gedit

# Install clipboard and automation tools
apt-get install -y --no-install-recommends \
    xdotool \
    xclip \
    xsel

# Ensure setup scripts are executable
chmod +x /exe/setup_vnc_password.sh
chmod +x /usr/local/bin/setup-clipboard-shortcuts

echo "====================VNC AND GUI COMPONENTS INSTALLED===================="

echo "====================INSTALLING CLAUDE CODE===================="

# Install Claude Code
if [ ! -f /root/.local/bin/claude ]; then
    curl -fsSL https://claude.ai/install.sh | bash || echo "Claude Code installation failed, will retry at runtime"
    
    # Create symlinks for easy access
    if [ -f /root/.local/bin/claude ]; then
        ln -sf /root/.local/bin/claude /usr/local/bin/claude
        ln -sf /root/.local/bin/claude /usr/local/bin/claude-pro
        echo "Claude Code symlinks created"
    fi
else
    echo "Claude Code already installed"
    # Ensure symlinks exist
    ln -sf /root/.local/bin/claude /usr/local/bin/claude 2>/dev/null || true
    ln -sf /root/.local/bin/claude /usr/local/bin/claude-pro 2>/dev/null || true
fi

# Ensure PATH includes ~/.local/bin in shell configs
if ! grep -q '\.local/bin' /root/.bashrc 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.bashrc
fi

if ! grep -q '\.local/bin' /root/.profile 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.profile
fi

echo "====================CLAUDE CODE INSTALLED===================="

echo "====================INSTALLING BURP SUITE (ARM64)===================="

# Install Burp Suite for DAST testing
apt-get install -y --no-install-recommends burpsuite || echo "Burp Suite installation failed, may need manual installation"

# Verify installation
if command -v burpsuite >/dev/null 2>&1; then
    echo "Burp Suite installed successfully"
    burpsuite --version 2>&1 | head -1 || true
else
    echo "Burp Suite not found in PATH, checking alternatives..."
    # Burp Suite may be installed but not in PATH
    if [ -f /usr/bin/burpsuite ]; then
        echo "Burp Suite found at /usr/bin/burpsuite"
    fi
fi

echo "====================BURP SUITE INSTALLED===================="

echo "====================SETTING UP YOLO MODE FOR CLAUDE CODE===================="

# Create claude user for YOLO mode (non-root execution)
if ! id claude >/dev/null 2>&1; then
    useradd -m -s /bin/bash claude
    echo "Created claude user for YOLO mode"
fi

# Install Claude Code for claude user if not already installed
if [ ! -f /home/claude/.local/bin/claude ]; then
    echo "Installing Claude Code for claude user..."
    su - claude -c 'curl -fsSL https://claude.ai/install.sh | bash' || echo "Claude Code installation for claude user failed, will retry at runtime"
fi

# Create claude-pro symlink for claude user
if [ -f /home/claude/.local/bin/claude ] && [ ! -f /home/claude/.local/bin/claude-pro ]; then
    su - claude -c 'ln -sf ~/.local/bin/claude ~/.local/bin/claude-pro' 2>/dev/null || true
fi

# Ensure PATH includes ~/.local/bin for claude user
if ! grep -q '\.local/bin' /home/claude/.bashrc 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/claude/.bashrc
fi

if ! grep -q '\.local/bin' /home/claude/.profile 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/claude/.profile
fi

# Share OAuth config between root and claude user
mkdir -p /home/claude/.config
if [ ! -L /home/claude/.config/claude-code ] && [ -d /root/.config/claude-code ]; then
    ln -sf /root/.config/claude-code /home/claude/.config/claude-code
fi

# Ensure wrapper script is executable
chmod +x /usr/local/bin/claude-pro-yolo 2>/dev/null || true

echo "====================YOLO MODE SETUP COMPLETE===================="

echo "====================INSTALLING SECURITY ASSESSMENT TOOLS===================="

# Install essential network scanning tools
apt-get install -y --no-install-recommends \
    nmap \
    masscan \
    netcat-openbsd \
    dnsutils \
    whois

# Install web scanning tools
apt-get install -y --no-install-recommends \
    nikto \
    dirb \
    whatweb || echo "Some web tools failed to install, will use on-demand installation"

# Install Go runtime for nuclei, subfinder, etc.
apt-get install -y --no-install-recommends golang-go || echo "Go installation failed, on-demand tools may not work"

# Set up Go environment
export GOPATH=/root/go
export PATH=$PATH:/root/go/bin
mkdir -p /root/go/bin

# Add Go to shell configs if not present
if ! grep -q 'GOPATH' /root/.bashrc 2>/dev/null; then
    echo 'export GOPATH=$HOME/go' >> /root/.bashrc
    echo 'export PATH=$PATH:$GOPATH/bin' >> /root/.bashrc
fi

if ! grep -q 'GOPATH' /root/.profile 2>/dev/null; then
    echo 'export GOPATH=$HOME/go' >> /root/.profile
    echo 'export PATH=$PATH:$GOPATH/bin' >> /root/.profile
fi

# Install SAST tools via pip
pip install --no-cache-dir semgrep bandit || echo "SAST tools pip install failed, will use on-demand installation"

# Verify installations
echo "Verifying security tool installations..."
nmap --version 2>&1 | head -1 || echo "nmap not installed"
nikto -Version 2>&1 | head -1 || echo "nikto not installed"
semgrep --version 2>&1 | head -1 || echo "semgrep not installed"
bandit --version 2>&1 | head -1 || echo "bandit not installed"
go version 2>&1 | head -1 || echo "go not installed"

echo "====================SECURITY ASSESSMENT TOOLS INSTALLED===================="

echo "====================INSTALLING WALLPAPER TOOLS===================="

# Install feh and imagemagick for wallpaper (packages only)
# Wallpaper configuration is handled by install_security_tools.sh at container start
apt-get install -y --no-install-recommends feh imagemagick || echo "Wallpaper tools install failed"

# Create wallpapers directory (will be populated by install_security_tools.sh)
mkdir -p /usr/share/wallpapers

echo "====================WALLPAPER TOOLS INSTALLED===================="