# Playwright Browser Version Mismatch After Upgrade

## Symptom

- `crawl4ai_rag.crawl_website` fails with error:
  ```
  Executable doesn't exist at /root/.cache/ms-playwright/chromium-XXXX/chrome-linux/chrome
  ```
- Error occurs after upgrading Playwright pip package inside container
- Browser automation tools fail to launch

## Root Cause

Playwright pip package upgrades (e.g. 1.52.0 → 1.58.0) may require different browser binary versions.

The volume-mounted browser directory (`./playwright-browsers` → `/root/.cache/ms-playwright`) contains old chromium version (e.g. chromium-1169) but new Playwright expects different version (e.g. chromium-1208).

Playwright pip package and browser binaries must match versions.

## Fix

### Inside Container

```bash
# Re-download browser binaries to match Playwright version
playwright install chromium

# Verify installation
ls -la /root/.cache/ms-playwright/

# Test
playwright open http://example.com
```

### From Host

```bash
# Execute playwright install inside running container
docker exec -it agent-zero playwright install chromium

# Or restart container (if Dockerfile has playwright install)
docker compose restart agent-zero
```

### After Docker Rebuild

Browser binaries are downloaded during image build (see `Dockerfile` line ~47).
If you rebuild the image, browsers are re-downloaded automatically:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Prevention

### Check Before Upgrade

Before upgrading Playwright pip package, check if browser version will change:

```bash
# Current Playwright version
/opt/venv-a0/bin/playwright --version

# Check installed browser
ls /root/.cache/ms-playwright/

# After pip upgrade, always run:
/opt/venv-a0/bin/playwright install chromium
```

### Automate Browser Install

Add to your upgrade script:

```bash
#!/bin/bash
# upgrade_playwright.sh

# Upgrade pip package
/opt/venv-a0/bin/pip install --upgrade playwright

# Re-download browsers
/opt/venv-a0/bin/playwright install chromium

echo "Playwright upgraded and browsers synced"
```

### Volume Mount Persistence

The `docker-compose.yml` includes a volume mount to persist browsers across container recreates:

```yaml
volumes:
  - ./playwright-browsers:/root/.cache/ms-playwright
```

This avoids re-downloading 900MB+ of browser binaries on every container restart.

## Troubleshooting

### Error: "playwright: command not found"

Playwright is installed in the main venv. Use full path:

```bash
/opt/venv-a0/bin/playwright install chromium
```

### Error: "Permission denied" when writing to cache

Check volume mount permissions:

```bash
# From host
ls -la playwright-browsers/

# Fix ownership if needed
sudo chown -R $(id -u):$(id -g) playwright-browsers/
```

### Browsers Not Persisting

Check `docker-compose.yml` volume mount:

```yaml
services:
  agent-zero:
    volumes:
      - ./playwright-browsers:/root/.cache/ms-playwright
```

Verify the directory exists on host:

```bash
ls -la ./playwright-browsers/
```

### Install Fails: "Failed to install browsers"

Install with `--force` to bypass version checks:

```bash
/opt/venv-a0/bin/playwright install --force chromium
```

Or install with system dependencies (on Debian/Ubuntu-based images):

```bash
/opt/venv-a0/bin/playwright install --with-deps chromium
```

**Note**: `--with-deps` may fail on Kali Linux due to different package names. On Kali, install system deps manually:

```bash
apt-get install -y libasound2t64 libgbm1 libnss3 libxshmfence1 \
  libxkbcommon0 libxdamage1 libxfixes3 libxcomposite1 libxrandr2
```

### Check Current Versions

```bash
# Playwright pip package version
/opt/venv-a0/bin/pip show playwright

# Installed browser versions
/opt/venv-a0/bin/playwright list

# Or check directory
ls -1 /root/.cache/ms-playwright/
```

## Version History

| Playwright Version | Chromium Version | Release Date |
|--------------------|------------------|--------------|
| 1.52.0 | 1169 | 2025-01-15 |
| 1.58.0 | 1208 | 2025-02-20 |

Check [Playwright releases](https://github.com/microsoft/playwright/releases) for latest versions.

## Related Documentation

- [Playwright Official Docs](https://playwright.dev/python/docs/intro)
- [Agent Zero Pre-installed Tools](../../knowledge/main/preinstalled_tools.md)
- [MCP Crawl4AI Integration](../../knowledge/main/mcp_servers.md#crawl4ai-rag-tools)
