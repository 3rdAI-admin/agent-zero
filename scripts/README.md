# Scripts Directory

This directory contains all executable scripts organized by purpose.

## Structure

- **setup/**: Installation and configuration scripts
- **testing/**: Test and validation scripts  
- **maintenance/**: Maintenance and fix scripts
- **docker/**: Docker-related scripts

## Usage

### Setup Scripts
```bash
# Configure MCP token
./scripts/setup/configure_mcp_token.sh

# Setup Claude OAuth
./scripts/setup/setup_claude_oauth.sh

# Start Agent Zero
./scripts/setup/startup.sh
```

### Testing Scripts
```bash
# Run validation
./scripts/testing/validate.sh

# Test Claude integration
./scripts/testing/test_claude_integration.sh
```

### Maintenance Scripts
```bash
# Fix Kali repository issues
./scripts/maintenance/fix_kali_repo.sh
```

### Docker Scripts
```bash
# Launch Chromium in VNC
./scripts/docker/launch_chromium.sh
```
