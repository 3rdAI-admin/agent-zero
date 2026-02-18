# Burp Suite Quick Start with Agent Zero (ARM64)

## ✅ Installation Status

**Burp Suite**: ✅ Installed (Version 2025.12.3, ARM64)  
**Java**: ✅ OpenJDK 21 (ARM64)  
**Architecture**: ✅ ARM64 (aarch64) compatible

## Quick Access

### Via VNC GUI (Interactive)
```bash
# 1. Connect to VNC: vnc://localhost:5901 (password: vnc123)
# 2. Open terminal in VNC
# 3. Run:
export DISPLAY=:99
burpsuite &
```

### Via Command Line (Headless)
```bash
# Start Burp Suite headless
docker exec agent-zero burpsuite --project-file=/tmp/burp_project.burp
```

### Via Agent Zero
```
Ask Agent Zero: "Use Burp Suite to scan http://target.com for web vulnerabilities"
```

## Common Commands

### Check Installation
```bash
docker exec agent-zero burpsuite --version
```

### Start Burp Suite
```bash
# GUI mode (requires VNC)
docker exec agent-zero bash -c "export DISPLAY=:99 && burpsuite &"

# Headless mode
docker exec agent-zero burpsuite --project-file=/tmp/burp_project.burp
```

### Proxy Configuration
- **Default Proxy**: `127.0.0.1:8080`
- **Port**: `8080`
- **No authentication** (default)

## Integration Examples

### Example 1: Basic DAST Scan
**Ask Agent Zero:**
```
Use Burp Suite to perform a DAST scan of http://192.168.1.100. 
Start Burp Suite, configure the scan, execute it, and report findings.
```

### Example 2: Comprehensive Web App Testing
**Ask Agent Zero:**
```
Perform a complete security assessment of http://target.com:
1. Use Burp Suite for DAST scanning
2. Use nikto for web server vulnerabilities  
3. Combine results into a security report
```

### Example 3: OWASP Top Ten Testing
**Ask Agent Zero:**
```
Use Burp Suite to test http://target.com for OWASP Top Ten vulnerabilities.
Focus on injection flaws, broken authentication, and security misconfigurations.
```

## Architecture Notes

✅ **ARM64 Compatible**: Burp Suite runs natively on ARM64  
✅ **Java ARM64**: OpenJDK 21 optimized for ARM  
✅ **Performance**: Excellent performance on ARM architecture  
✅ **GUI Support**: Full GUI access via VNC

## Documentation

- **Full Guide**: [BURP_SUITE_INTEGRATION.md](./BURP_SUITE_INTEGRATION.md)
- **Security Tools**: [SECURITY_SETUP.md](./SECURITY_SETUP.md)
- **OWASP Tools**: [OWASP_TOP_TEN_TOOLS.md](./OWASP_TOP_TEN_TOOLS.md)

## Summary

Burp Suite is **installed, verified, and ready** for DAST testing with Agent Zero on ARM64 architecture! 🎉
