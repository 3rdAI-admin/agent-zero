# Access Container Directly for OAuth (Solution 3)

## Step-by-Step Instructions

### Step 1: Access Container Shell

Run this command in your terminal:

```bash
docker exec -it agent-zero bash
```

### Step 2: Set Up Environment

Once inside the container, run:

```bash
export PATH="$HOME/.local/bin:$PATH"
unset ANTHROPIC_API_KEY
unset API_KEY_ANTHROPIC
```

### Step 3: Start Claude Code OAuth

Run:

```bash
claude-pro
```

Or use the helper:

```bash
claude-start-oauth
```

### Step 4: Copy the OAuth URL

Claude Code will display:
- Welcome message
- ASCII art
- A line saying "Browser didn't open? Use the url below to sign in"
- **A VERY LONG URL** starting with `https://claude.ai/oauth/authorize?code=true&client_id=...`

**CRITICAL:** Copy the **ENTIRE URL** - it's 500+ characters long!

**How to copy:**
1. Click and drag from the start (`https://`) to the very end
2. Or triple-click the URL line if your terminal supports it
3. Verify it includes `redirect_uri=https%3A%2F%2Fplatform.claude.com%2Foauth%2Fcode%2Fcallback`

### Step 5: Verify URL Completeness

Before pasting in browser, check:
- URL starts with: `https://claude.ai/oauth/authorize?code=true`
- URL includes: `redirect_uri=https%3A%2F%2Fplatform.claude.com%2Foauth%2Fcode%2Fcallback`
- URL ends with: `&state=...` (long string)
- Total length: 500+ characters

### Step 6: Open URL in Browser

1. **Open a web browser** on your host machine
2. **Paste the complete URL** into the address bar
3. **Press Enter**

### Step 7: Complete Authentication

1. **Complete Cloudflare CAPTCHA** if shown
2. **Sign in** with your Claude Pro account
3. **Authorize** Claude Code
4. **Copy the authorization code** (shown on page or in URL)

### Step 8: Paste Code Back

1. **Return to the container terminal**
2. **Paste the authorization code** at the prompt:
   ```
   Paste code here if prompted >
   ```
3. **Press Enter**

### Step 9: Verify Authentication

Claude Code should now be authenticated! You can test with:

```bash
claude-pro -p "test"
```

## Quick Reference Commands

**Access container:**
```bash
docker exec -it agent-zero bash
```

**Inside container:**
```bash
export PATH="$HOME/.local/bin:$PATH"
unset ANTHROPIC_API_KEY
claude-pro
```

**Or use helper:**
```bash
claude-start-oauth
```

## Troubleshooting

### URL Still Truncated

If the URL keeps getting truncated in the terminal:

1. **Use terminal's "Select All"** feature
2. **Or pipe output to file:**
   ```bash
   claude-pro > /tmp/oauth-output.txt 2>&1
   cat /tmp/oauth-output.txt | grep oauth/authorize
   ```

### Can't Copy from Terminal

**Solution:** Use the extraction script:
```bash
# On host machine
cd /Users/james/Docker/AgentZ
./get-claude-oauth.sh
```

### redirect_uri Still Missing

**Check:**
- Did you copy from `https://` to the very end?
- Is the URL 500+ characters?
- Does it include all parameters?

If yes to all but still missing, it might be a Claude Code bug - try getting a fresh URL.

## Success Indicators

✅ URL is 500+ characters long  
✅ Includes `redirect_uri=` parameter  
✅ Browser accepts the URL (no "Missing redirect_uri" error)  
✅ You can complete authentication  
✅ Authorization code is received  
✅ Code works when pasted back

---

**Ready to start?** Run: `docker exec -it agent-zero bash`
