# Claude Code Authentication in Headless Docker Container

## Problem
Claude Code requires OAuth authentication, but Docker containers are headless (no browser). You need to authenticate externally and paste the code back.

## Solution: Manual OAuth Flow

### Step 1: Get the Authorization URL

When you run `claude` in the container, it will display:
```
Browser didn't open? Use the url below to sign in (c to copy)
https://claude.ai/oauth/authorize?code=true&client_id=...
```

**Copy this entire URL** from the terminal output.

### Step 2: Open URL in Host Browser

1. **Copy the OAuth URL** from the container terminal
2. **Open it in a web browser** on your host machine (outside Docker)
3. **Sign in** with your Anthropic/Claude account
4. **Authorize** Claude Code to access your account

### Step 3: Get the Authorization Code

After authorizing, you'll be redirected to a page that shows:
- An authorization code (usually 6-8 characters)
- OR you'll be redirected and the code will be in the URL

**Copy this authorization code.**

### Step 4: Paste Code Back into Container

1. **Return to the container terminal** where Claude Code is waiting
2. **Paste the authorization code** at the prompt:
   ```
   Paste code here if prompted >
   ```
3. **Press Enter**

### Step 5: Verify Authentication

After pasting the code, Claude Code should authenticate successfully. You'll see a success message and can start using it.

## Alternative: Using Environment Variables

If you have an Anthropic API key, you can set it as an environment variable:

```bash
# In docker-compose.yml, add to environment:
ANTHROPIC_API_KEY=your_api_key_here

# Or set it in the container:
docker exec -it agent-zero bash -c "export ANTHROPIC_API_KEY=your_key && claude"
```

## Quick Reference

**Container Terminal:**
```bash
docker exec -it agent-zero bash
claude
# Copy the OAuth URL shown
```

**Host Machine:**
1. Open browser
2. Paste OAuth URL
3. Sign in and authorize
4. Copy authorization code

**Back to Container:**
1. Paste code at prompt
2. Press Enter
3. Start using Claude Code!

## Troubleshooting

**If the code doesn't work:**
- Make sure you copied the entire code
- Check that you're signed into the correct Anthropic account
- Try generating a new OAuth URL by running `claude` again

**If you lose the prompt:**
- Run `claude` again to get a new OAuth URL
- OAuth URLs expire after a few minutes, so generate a fresh one

**To check if already authenticated:**
```bash
claude --version
# If authenticated, you can use it directly
claude "your prompt here"
```

## Persistence

Once authenticated, Claude Code stores your credentials in:
- `~/.config/claude-code/` inside the container

These credentials persist across container restarts as long as the container's filesystem persists.
