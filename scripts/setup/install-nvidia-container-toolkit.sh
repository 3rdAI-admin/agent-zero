#!/usr/bin/env bash
# Install and configure NVIDIA Container Toolkit on the host so Docker containers
# (e.g. Ollama) can use the GPU. Run this on the Linux machine where Docker runs
# and the NVIDIA GPU is attached (e.g. 192.168.50.7).
#
# Usage (on the GPU host):
#   sudo bash scripts/setup/install-nvidia-container-toolkit.sh
# Or from another machine:
#   ssh YOUR_GPU_HOST 'bash -s' < scripts/setup/install-nvidia-container-toolkit.sh
#
# Requires: NVIDIA drivers already installed (nvidia-smi works), root/sudo.

set -e

echo "=== NVIDIA Container Toolkit setup ==="

# Require nvidia-smi so we know the driver is present
if ! command -v nvidia-smi &>/dev/null; then
  echo "Error: nvidia-smi not found. Install NVIDIA drivers first (nvidia-smi should work)."
  exit 1
fi
echo "NVIDIA driver OK:"
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || nvidia-smi -L

# Detect package manager and install nvidia-container-toolkit
if command -v apt-get &>/dev/null; then
  echo "Installing nvidia-container-toolkit (Debian/Ubuntu)..."
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  apt-get update
  apt-get install -y nvidia-container-toolkit
elif command -v yum &>/dev/null || command -v dnf &>/dev/null; then
  echo "Installing nvidia-container-toolkit (RHEL/CentOS/Fedora)..."
  if command -v dnf &>/dev/null; then
    dnf config-manager --add-repo https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo
    dnf install -y nvidia-container-toolkit
  else
    yum config-manager --add-repo https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo
    yum install -y nvidia-container-toolkit
  fi
else
  echo "Error: Unsupported package manager (apt-get or yum/dnf required)."
  echo "See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
  exit 1
fi

echo "Configuring Docker to use NVIDIA runtime..."
nvidia-ctk runtime configure --runtime=docker

echo "Restarting Docker..."
if command -v systemctl &>/dev/null; then
  systemctl restart docker
  echo "Docker restarted (systemctl)."
else
  echo "Please restart Docker manually (e.g. service docker restart)."
fi

echo ""
echo "Done. Verify with: docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi"
echo "Then start the Ollama stack: docker compose up -d ollama"
