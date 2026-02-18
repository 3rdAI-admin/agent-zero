# Claude Pro Subscription - Quick Start Guide

## Overview

Use your Claude Pro subscription instead of API key (which charges per-use). OAuth authentication allows unlimited usage within your Pro subscription limits.

## Quick Start

### Step 1: Start OAuth Authentication

```bash
docker exec -it agent-zero claude-pro
```

### Step 2: Complete OAuth Flow

1. **Copy the OAuth URL** shown in the terminal
2. **Open it in your browser** (on your host machine, not in container)
3. **Complete Cloudflare CAPTCHA** if prompted
4. **Sign in** with your Claude Pro account
5. **Authorize** Claude Code
6. **Copy the authorization code** (shown on page or in URL)
7. **Paste it** back into the container terminal
8. **Press Enter**

### Step 3: Verify Authentication

Claude Code should now be authenticated with your Pro subscription!

## Available Commands

### Use Pro Subscription (OAuth)
```bash
docker exec -it agent-zero claude-pro
```
- Uses your Pro subscription
- No per-use API costs
- Unlimited usage within Pro limits

### Force OAuth Re-authentication
```bash
docker exec -it agent-zero claude-oauth
```
- Forces OAuth flow (useful if auth expired)

### Use API Key (Pay-per-use)
```bash
docker exec -it agent-zero claude
```
- Uses API key from `.env` file
- Charges per API call
- Useful for testing or if OAuth fails

## Authentication Persistence

✅ **Authentication is saved** in `./claude-config/` directory  
✅ **Persists across container restarts** (volume mounted)  
✅ **No need to re-authenticate** unless you clear the config

## Troubleshooting

### OAuth URL Expired
**Solution:** Run `claude-pro` again to get a fresh URL

### Cloudflare CAPTCHA Blocking
**Solution:** Complete CAPTCHA on your host browser (not in container)

### Authentication Not Persisting
**Solution:** Check that `./claude-config/` volume is mounted in docker-compose.yml

### Check Current Authentication
```bash
docker exec agent-zero ls -la /root/.config/claude-code/
```

## Cost Comparison

| Method | Cost Model | Best For |
|--------|-----------|----------|
| **Pro Subscription (OAuth)** | Fixed monthly fee | Regular/heavy usage |
| **API Key** | Pay per API call | Occasional/testing |

## Helper Scripts

**On Host Machine:**
```bash
./claude-pro-auth.sh
```
Interactive helper script for OAuth authentication.

## Configuration Files

- **docker-compose.yml**: Volume mount for `./claude-config/`
- **Helper scripts**: `/usr/local/bin/claude-pro` and `claude-oauth`
- **Config directory**: `./claude-config/` (persists authentication)

## Next Steps

1. **Authenticate now:**
   ```bash
   docker exec -it agent-zero claude-pro
   ```

2. **Start using Claude Code:**
   ```bash
   docker exec -it agent-zero claude-pro -p "your prompt"
   ```

3. **Use with Agent Zero:**
   Ask Agent Zero to use Claude Code for coding tasks!

---

**Status:** ✅ Ready for OAuth authentication  
**Browsers:** ✅ Installed (Chromium, Firefox)  
**Persistence:** ✅ Configured (survives restarts)
