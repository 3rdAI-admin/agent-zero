# Fixing Claude Code OAuth "Missing redirect_uri" Error

## Problem

When trying to authenticate Claude Code with OAuth, you get:
- **Error:** "Invalid OAuth Request - Missing redirect_uri parameter"
- **Cause:** The OAuth URL is being truncated or not copied completely

## Solution

### The OAuth URL is Very Long!

The OAuth URL from Claude Code is **extremely long** (often 500+ characters). When copying, make sure you:

1. **Copy the ENTIRE URL** - from `https://` to the very end
2. **Don't truncate it** - the URL must be complete
3. **Check for line breaks** - the URL might wrap in the terminal

### Step-by-Step Fix

#### Method 1: Use Terminal Copy Feature

1. **In the terminal**, look for the line:
   ```
   Browser didn't open? Use the url below to sign in (c to copy)
   ```

2. **Press 'c'** if available, or manually select the entire URL
   - Start from: `https://claude.ai/oauth/authorize?code=true&client_id=...`
   - End at: `...&state=...` (the very last parameter)

3. **Verify the URL is complete** before pasting in browser
   - It should start with `https://claude.ai/oauth/authorize?code=true`
   - It should end with `&state=...` (a long string)

#### Method 2: Extract URL to File

```bash
# Get the OAuth URL and save it
docker exec agent-zero claude-get-url > oauth-url.txt

# Then open the URL from the file
cat oauth-url.txt
```

#### Method 3: Manual URL Construction

If the URL keeps getting truncated, you can try:

1. **Copy the URL in parts** and reconstruct it
2. **Or use a URL shortener** (not recommended for security)
3. **Or access container directly** and copy from there

### Common Issues

#### Issue 1: URL Truncated in Terminal
**Solution:** 
- Use terminal's "Select All" or "Copy URL" feature
- Or pipe output to a file: `docker exec agent-zero claude-pro > url.txt`

#### Issue 2: Browser URL Bar Truncates
**Solution:**
- Paste the URL into a text editor first
- Verify it's complete
- Then copy from editor to browser

#### Issue 3: redirect_uri Parameter Missing
**Solution:**
- The redirect_uri is in the URL: `redirect_uri=https%3A%2F%2Fplatform.claude.com%2Foauth%2Fcode%2Fcallback`
- Make sure this entire parameter is included
- It's URL-encoded, so `%3A` = `:` and `%2F` = `/`

### Verification

A complete OAuth URL should contain all these parameters:
- `code=true`
- `client_id=...`
- `response_type=code`
- `redirect_uri=https%3A%2F%2Fplatform.claude.com%2Foauth%2Fcode%2Fcallback`
- `scope=...`
- `code_challenge=...`
- `code_challenge_method=S256`
- `state=...`

### Alternative: Direct Container Access

If URL copying keeps failing:

```bash
# Access container shell directly
docker exec -it agent-zero bash

# Then run claude-pro
export PATH="$HOME/.local/bin:$PATH"
unset ANTHROPIC_API_KEY
claude-pro

# Copy URL directly from container terminal
```

### Quick Test

To verify you have the complete URL:

```bash
# Check URL length (should be 500+ characters)
echo "YOUR_URL_HERE" | wc -c

# Check for redirect_uri parameter
echo "YOUR_URL_HERE" | grep -o 'redirect_uri=[^&]*'
```

If you see `redirect_uri=https%3A%2F%2Fplatform.claude.com%2Foauth%2Fcode%2Fcallback`, the URL is complete!

## Still Having Issues?

If the error persists:

1. **Try a fresh OAuth URL:**
   ```bash
   docker exec -it agent-zero claude-pro
   # Get a new URL (old ones expire)
   ```

2. **Check Claude Code version:**
   ```bash
   docker exec agent-zero claude-pro --version
   ```

3. **Clear and restart:**
   ```bash
   docker exec agent-zero rm -rf /root/.config/claude-code
   docker exec -it agent-zero claude-pro
   ```

4. **Contact Support:** If redirect_uri is in the URL but still getting error, it might be a Claude Code bug - check for updates.
