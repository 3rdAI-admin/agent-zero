# Migration Guide - File Reorganization

This guide helps you adapt to the new file organization structure.

## What Changed

### Scripts
All scripts have been moved from root to `scripts/` directory:
- Setup scripts → `scripts/setup/`
- Test scripts → `scripts/testing/`
- Maintenance scripts → `scripts/maintenance/`
- Docker scripts → `scripts/docker/`

### Documentation
Documentation has been organized into `docs/` subdirectories:
- Setup guides → `docs/guides/`
- Integration docs → `docs/integration/`
- Troubleshooting → `docs/troubleshooting/`
- Historical → `docs/archive/`

## Backward Compatibility

### Convenience Symlinks
Common scripts are available via symlinks in root:
- `./startup.sh` → `scripts/setup/startup.sh`
- `./validate.sh` → `scripts/testing/validate.sh`

### Updated Commands

**Before:**
```bash
./setup_claude_oauth.sh
./test_claude_integration.sh
./validate.sh
```

**After (recommended):**
```bash
./scripts/setup/setup_claude_oauth.sh
./scripts/testing/test_claude_integration.sh
./scripts/testing/validate.sh
```

**After (via symlinks):**
```bash
./startup.sh  # Still works
./validate.sh  # Still works
```

## Updating Your Workflows

### CI/CD Pipelines
If your CI/CD references scripts, update paths:
```yaml
# Before
script: ./validate.sh

# After
script: ./scripts/testing/validate.sh
```

### Documentation References
Update any documentation that references old paths:
- `./setup_claude_oauth.sh` → `./scripts/setup/setup_claude_oauth.sh`
- `./test_*.sh` → `./scripts/testing/test_*.sh`

### Docker Compose
No changes needed - volume mounts remain the same.

### Python Imports
No changes needed - Python imports unchanged.

## Benefits

1. **Cleaner Root**: Only core files in root directory
2. **Better Organization**: Files grouped by purpose
3. **Easier Navigation**: Clear directory structure
4. **Professional Standards**: Follows industry best practices
5. **Maintainability**: Easier to find and maintain files

## Need Help?

- See `docs/README.md` for documentation structure
- See `scripts/README.md` for scripts structure
- See `.directory-structure.md` for full directory layout
