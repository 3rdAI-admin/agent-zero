# Container Hardening

Agent Zero now applies the following baseline hardening in `docker-compose.yml` for the main `agent-zero` container:

- `cap_drop: [ALL]`
- `cap_add: [CHOWN, NET_RAW, NET_BIND_SERVICE, SETUID, SETGID]`
- `security_opt: [no-new-privileges:true]`
- `tmpfs` mounts for `/tmp`, `/run`, `/var/run`, and `/var/log`

## Why These Settings

- `cap_drop: [ALL]` removes the broad default Linux capability set.
- `CHOWN` preserves the runtime ownership fixups used for Claude-related persisted files.
- `NET_RAW` keeps raw-socket support for tools such as `nmap` host discovery without leaving `NET_ADMIN` or `SYS_ADMIN` enabled by default.
- `NET_BIND_SERVICE` keeps the current low-port listeners working while the stack still binds `22` and `80` inside the container.
- `SETUID` and `SETGID` preserve the current supervisor/SSH behavior that starts as root and drops selected services to non-root users.
- `no-new-privileges:true` blocks setuid/setcap privilege escalation inside the container.
- `tmpfs` keeps ephemeral runtime state out of the image filesystem and ensures lock files, sockets, and transient logs are recreated on each start.

## Runtime Directories Recreated At Startup

`docker/run/fs/exe/initialize.sh` recreates the writable directories that supervisor-managed services need after the tmpfs mounts are applied:

- `/var/log/nginx`
- `/var/log/supervisor`
- `/var/run/sshd`
- `/run`
- `/var/run`
- `/tmp/.X11-unix`

This keeps the current supervisor, SSH, nginx, and X11/VNC stack working without requiring image rebuild-time log directories to stay writable.

## Why The Container Is Not Fully `read_only` Yet

Full `read_only: true` is intentionally deferred. The current startup flow still mutates additional system paths at runtime:

- `initialize.sh` copies persisted overlay content from `/per` into `/`
- `generate_ssl_cert.sh` can regenerate certificates during boot
- `supervisord` runs as root and launches a mix of root-owned and service-owned processes

Before enabling a fully read-only root filesystem, those writes need to be redirected into explicitly writable mounts and the certificate/init flow needs to be tightened.

## Why The Main App Still Runs Under Root-Supervised Startup

The current container startup model uses root-owned supervisor orchestration for:

- `sshd`
- `cron`
- nginx/bootstrap wiring
- Xvfb / Fluxbox / x11vnc support

That makes an immediate "run the whole container as non-root" switch too risky for this phase. A safer future step would be:

1. Keep `supervisord` as PID 1 under root.
2. Drop only the Agent Zero app process and tunnel process to a dedicated non-root runtime user.
3. Revalidate file ownership under `/a0/usr`, `/a0/logs`, `/a0/tmp`, and the mounted repo.

For this phase, capability reduction and `no-new-privileges` provide the best security gain with the lowest startup risk.
