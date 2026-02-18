# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# Add ~/.local/bin to PATH for Claude Code and other user-installed tools
export PATH="$HOME/.local/bin:$PATH"

# Activate the virtual environment
source /opt/venv/bin/activate
