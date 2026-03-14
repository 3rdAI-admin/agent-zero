#!/bin/bash
set -e

# Exit immediately if a command exits with a non-zero status.
# set -e

# branch from parameter
if [ -z "$1" ]; then
    echo "Error: Branch parameter is empty. Please provide a valid branch name."
    exit 1
fi
BRANCH="$1"

if [ "$BRANCH" = "local" ]; then
    # For local branch, use the files
    echo "Using local dev files in /git/agent-zero"
    # List all files recursively in the target directory
    # echo "All files in /git/agent-zero (recursive):"
    # find "/git/agent-zero" -type f | sort
else
    # For other branches, clone from GitHub
    echo "Cloning repository from branch $BRANCH..."
    git clone -b "$BRANCH" "https://github.com/agent0ai/agent-zero" "/git/agent-zero" || {
        echo "CRITICAL ERROR: Failed to clone repository. Branch: $BRANCH"
        exit 1
    }
fi

. "/ins/setup_venv.sh" "$@"

# moved to base image
# # Ensure the virtual environment and pip setup
# pip install --upgrade pip ipython requests
# # Install some packages in specific variants
# pip install torch --index-url https://download.pytorch.org/whl/cpu

# Ensure setuptools is available (openai-whisper needs pkg_resources at build time)
uv pip install setuptools

# Install remaining A0 python packages
# --no-build-isolation lets openai-whisper find pkg_resources from the venv
uv pip install --no-build-isolation -r /git/agent-zero/requirements.txt
# override for packages that have unnecessarily strict dependencies
uv pip install -r /git/agent-zero/requirements2.txt

# Upgrade pip to address Dependabot GHSA-4xh5-x5gv-qwph, GHSA-6vgw-5pg2-w6jp (pip 25.3+ / 26.0+)
uv pip install 'pip>=26.0'

# install playwright
bash /ins/install_playwright.sh "$@"

# Preload A0 with deterministic defaults during image build.
if [ "${A0_SKIP_PRELOAD:-0}" != "1" ]; then
    python /git/agent-zero/preload.py --dockerized=true --defaults-only
fi
