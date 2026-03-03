# Use the pre-built base image for A0
# FROM agent-zero-base:local
# FROM agent0ai/agent-zero-base:testing
FROM agent0ai/agent-zero-base:latest

# Check if the argument is provided, else throw an error
ARG BRANCH
RUN if [ -z "$BRANCH" ]; then echo "ERROR: BRANCH is not set!" >&2; exit 1; fi
ENV BRANCH=$BRANCH

# Copy filesystem files to root
COPY ./fs/ /

# pre installation steps
RUN bash /ins/pre_install.sh $BRANCH

# install A0
RUN bash /ins/install_A0.sh $BRANCH

# install additional software
RUN bash /ins/install_additional.sh $BRANCH

# install OWASP Top 10 penetration testing tools
RUN bash /ins/install_owasp_tools.sh $BRANCH

# cleanup repo and install A0 without caching, this speeds up builds
ARG CACHE_DATE=none
RUN echo "cache buster $CACHE_DATE" && bash /ins/install_A02.sh $BRANCH

# post installation steps
RUN bash /ins/post_install.sh $BRANCH

# Expose ports
#  22  – Optional SSH access
#  80  – Web UI
#  5900 – VNC server for GUI access (mapped to 5901 on host)
#  9000-9009 – ancillary services (tunnel, MCP, etc.)
EXPOSE 22 80 5900 9000-9009

RUN chmod +x /exe/initialize.sh /exe/run_A0.sh /exe/run_searxng.sh /exe/run_tunnel_api.sh /exe/setup_vnc_password.sh /exe/start_xvfb.sh

# initialize runtime and switch to supervisord
CMD ["/exe/initialize.sh", "$BRANCH"]
