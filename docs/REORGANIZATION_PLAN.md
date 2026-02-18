# File Reorganization Plan - Industry Standards

## Current Issues
- Too many markdown files in root directory
- Scripts scattered across root
- Documentation not well-organized
- Test files mixed with source
- Configuration files scattered

## Target Structure

```
AgentZ/
├── .github/                    # GitHub workflows (keep)
├── .vscode/                    # VS Code config (keep)
├── docker/                     # Docker files (keep, already organized)
├── docs/                       # Main documentation (enhance)
│   ├── guides/                 # User guides
│   ├── integration/            # Integration docs
│   ├── troubleshooting/        # Troubleshooting docs
│   └── res/                    # Images/assets (keep)
├── scripts/                    # NEW: All scripts organized
│   ├── setup/                  # Setup/installation scripts
│   ├── testing/                # Test scripts
│   ├── maintenance/            # Maintenance scripts
│   └── docker/                 # Docker-related scripts
├── tests/                      # Test files (keep, enhance)
├── config/                     # NEW: Configuration files
│   └── examples/               # Example configs
├── docs/archive/               # NEW: Historical/obsolete docs
├── python/                     # Python code (keep)
├── webui/                      # Web UI (keep)
├── prompts/                    # Prompts (keep)
├── knowledge/                  # Knowledge base (keep)
├── agents/                     # Agents (keep)
├── instruments/                # Instruments (keep)
├── [data dirs]/               # memory, logs, tmp, etc. (keep)
├── README.md                   # Main README (keep)
├── docker-compose.yml          # Docker compose (keep)
├── Dockerfile                  # Dockerfile (keep)
└── [core files]               # agent.py, run_ui.py, etc. (keep)
```

## Reorganization Steps

### Phase 1: Create New Directories
- Create `scripts/` with subdirectories
- Create `config/` directory
- Create `docs/archive/` for obsolete docs
- Create `docs/guides/`, `docs/integration/`, `docs/troubleshooting/`

### Phase 2: Move Scripts
- Setup scripts → `scripts/setup/`
- Test scripts → `scripts/testing/`
- Maintenance scripts → `scripts/maintenance/`
- Docker scripts → `scripts/docker/` (if not in docker/)

### Phase 3: Organize Documentation
- Integration docs → `docs/integration/`
- Setup guides → `docs/guides/`
- Troubleshooting → `docs/troubleshooting/`
- Obsolete → `docs/archive/`

### Phase 4: Organize Config Files
- Example configs → `config/examples/`
- Keep active configs in root or appropriate location

### Phase 5: Update References
- Update all imports/paths
- Update documentation links
- Update docker-compose volume paths if needed

## Files to Move

### Scripts → scripts/
- `setup_claude_oauth.sh` → `scripts/setup/`
- `configure_mcp_token.sh` → `scripts/setup/`
- `configure_claude_mcp.sh` → `scripts/setup/`
- `validate.sh` → `scripts/testing/`
- `test_*.sh` → `scripts/testing/`
- `test_*.py` → `scripts/testing/` (or keep in tests/)
- `startup.sh` → `scripts/setup/`
- `fix_*.sh` → `scripts/maintenance/`
- `get-*.sh` → `scripts/setup/`
- `extract-*.sh` → `scripts/setup/`
- `launch_*.sh` → `scripts/docker/`
- `start_*.sh` → `scripts/docker/`

### Documentation → docs/
- Integration docs → `docs/integration/`
- Setup guides → `docs/guides/`
- Troubleshooting → `docs/troubleshooting/`
- Historical → `docs/archive/`

### Config → config/
- Example configs → `config/examples/`

## Files to Keep in Root
- `README.md`
- `docker-compose.yml`
- `Dockerfile`, `DockerfileLocal`
- `agent.py`, `run_ui.py`, `run_tunnel.py`
- `initialize.py`, `prepare.py`, `preload.py`
- `models.py`
- `.env` (user config, keep in root)
- Core Python entry points

## Verification
- All imports still work
- All scripts still executable
- All paths updated
- Documentation links updated
- Docker volumes still work
