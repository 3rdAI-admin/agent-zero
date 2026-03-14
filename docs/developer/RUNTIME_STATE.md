# Runtime State Model

This document defines the effective runtime state model for Agent Zero.

## Source of truth

- Runtime settings file: `usr/settings.json`
- Sensitive settings: root `.env` plus `usr/.env`
- Runtime-derived values: generated at runtime and not authoritative in JSON

In Docker, the effective settings path is `/a0/usr/settings.json`.

## Load order

1. `runtime.initialize()` establishes runtime mode and derived paths.
2. `initialize.initialize_migration()` migrates legacy data such as `tmp/settings.json` to `usr/settings.json`.
3. `python.helpers.dotenv.load_dotenv()` loads:
   - root `.env` first with `override=False`
   - `usr/.env` second with `override=True`
4. `python.helpers.settings.get_settings()` reads `usr/settings.json`, normalizes it, and overlays sensitive values from env.

## Important precedence rules

- Saved values in `usr/settings.json` win over defaults.
- `A0_SET_*` values only seed defaults through `get_default_settings()`.
- `usr/.env` overrides root `.env` for duplicate keys.
- Sensitive values are not persisted in `usr/settings.json`.

## Runtime-derived values

These values should not be scraped from settings files:

- `mcp_server_token`
  - Derived at runtime from persistent runtime id plus `AUTH_LOGIN` and `AUTH_PASSWORD`
  - Removed before writing settings back to disk
- runtime/session ids
  - Derived in `python.helpers.runtime`
  - Not stable file-backed configuration

## Preload behavior

- Build-time preload may run before user settings exist.
- Build-time preload should therefore run in deterministic defaults-only mode.
- Runtime preload must use effective runtime settings, not only defaults.
- `preload.py` supports two modes:
  - build-time: `--defaults-only`
  - runtime: effective settings via `get_settings()`
- `install_A0.sh` uses `--defaults-only` during image build.
- `install_A02.sh` skips the duplicate second preload pass.

## Startup readiness

- `GET /health` is liveness only and should stay cheap and unconditional.
- `GET /ready` reports startup readiness and phase details separately from liveness.
- Required readiness phases currently focus on core local startup, especially migration and chat restore.
- MCP initialization is tracked in readiness output, but it is informational by default because optional integrations may not be started with the main container.
- Set `A0_READY_REQUIRE_MCP=1` to make MCP initialization block readiness.

## Legacy compatibility

`tmp/settings.json` is migration input only, not an active source of truth.

Scripts and tests should not:

- read `/a0/tmp/settings.json` for `mcp_server_token`
- assume `/a0/usr/runtime_id` is the token source
- treat repo `usr/settings.json` as authoritative when a mounted user volume is active

## Operational guidance

- For live status, prefer runtime APIs/helpers or container reads of `/a0/usr/settings.json`.
- `scripts/show_status.sh` now reports runtime truth and drift warnings from the live container, including:
  - live settings path versus repo seed path
  - model assignment drift
  - MCP config drift
  - runtime-derived fields that should not be treated as file-backed truth
- For MCP token checks, use runtime-derived helpers instead of JSON scraping.
- When debugging drift, compare:
  - effective `usr/settings.json`
  - root `.env`
  - `usr/.env`
  - runtime-derived values
