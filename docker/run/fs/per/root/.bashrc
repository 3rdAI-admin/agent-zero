# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# Add ~/.local/bin to PATH for Claude Code and other user-installed tools
export PATH="$HOME/.local/bin:$PATH"

# Activate the Agent Zero virtual environment (venv-a0 has all runtime packages
# including Google API libraries needed by agent-generated code)
source /opt/venv-a0/bin/activate
