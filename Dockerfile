############################################################
# Agent Zero – Production Dockerfile
#
# Builds a self-contained Agent Zero image using the same
# runtime bootstrap scripts that power the upstream images.
############################################################

# Base image already contains system deps, Python, Playwright, etc.
FROM agent0ai/agent-zero-base:latest

# Build argument controls which git branch (or local files) to install.
# Default to "local" so we reuse the build context instead of cloning.
ARG BRANCH=local
ENV BRANCH=${BRANCH}

# Copy only the runtime filesystem overlay first (better layer caching)
COPY docker/run/fs/ /

# Copy the current working tree that will be installed into /a0 during build.
# (install_A0.sh expects sources inside /git/agent-zero)
COPY . /git/agent-zero

# Install and configure Agent Zero using the bundled scripts.
RUN bash /ins/pre_install.sh "$BRANCH"
RUN bash /ins/install_A0.sh "$BRANCH"
RUN bash /ins/install_additional.sh "$BRANCH"

# Install OWASP Top 10 penetration testing tools
RUN bash /ins/install_owasp_tools.sh "$BRANCH"

# Cache-busting hook + cleanup of transient artefacts.
ARG CACHE_DATE=none
RUN echo "cache buster ${CACHE_DATE}" && bash /ins/install_A02.sh "$BRANCH"

# Sync repo into /a0 so the app (run_ui.py, models.py, etc.) uses built code including local fixes.
RUN mkdir -p /a0 && cp -rn /git/agent-zero/. /a0/

# Install ipython — required by code_execution_tool's "python" runtime.
# Without it, agent gets "ipython: command not found" and must fall back to terminal runtime.
RUN /opt/venv-a0/bin/pip install --no-cache-dir ipython 2>/dev/null || true

# Install Playwright Chromium browsers (playwright pip package is in the venv
# but browser binaries at /root/.cache/ms-playwright/ must be downloaded separately).
# --with-deps fails on Kali (different package names from Ubuntu), so install
# browser binaries only; system deps come from install_base_packages.
# The volume mount in docker-compose.yml persists browsers across container recreates.
RUN /opt/venv-a0/bin/playwright install chromium 2>/dev/null || true

# Remove apt caches to keep the image lean.
RUN bash /ins/post_install.sh "$BRANCH"

# Ensure runtime helpers are executable.
RUN chmod +x /exe/initialize.sh /exe/run_A0.sh /exe/run_searxng.sh /exe/run_tunnel_api.sh /exe/setup_vnc_password.sh /exe/generate_ssl_cert.sh /exe/start_xvfb.sh

# Default ports:
#  80  – Web UI
#  22  – Optional SSH access (disabled unless you expose it)
#  5900 – VNC server for GUI access (mapped to 5901 on host)
#  9000-9009 – ancillary services (tunnel, MCP, etc.)
EXPOSE 22 80 5900 9000-9009

# Boot the supervisor stack (run_ui, searxng, tunnel, etc.).
CMD ["/exe/initialize.sh", "local"]
