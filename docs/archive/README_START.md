# Starting Agent Zero Server (Native Installation)

## Quick Start (Recommended):
```bash
cd /home/kali/Tools/agent-zero
./startup.sh
```

This automated script:
- Stops any running instances
- Updates from git (if safe)
- Starts Agent Zero with proper configuration

## Manual Launch:
```bash
cd /home/kali/Tools/agent-zero
source venv/bin/activate
python launch_a0_direct.py
```

## A2A Endpoint:
Once running, the endpoint will be:
**http://192.168.50.70:8000/a2a**

## Documentation:
- **Complete Guide**: [docs/NATIVE_INSTALLATION.md](docs/NATIVE_INSTALLATION.md)
- **Quick Reference**: [NATIVE_SETUP_SUMMARY.md](NATIVE_SETUP_SUMMARY.md)

## Key Configuration:
- **Shell Interface**: Set to `"local"` in settings (required for code execution)
- **Network Access**: Configured via `launch_a0_direct.py` or environment variables
- **Models**: Configured for Ollama at http://192.168.50.7:11434

## Check Status:
```bash
ps aux | grep launch_a0_direct
netstat -tlnp | grep 8000
curl http://192.168.50.70:8000/a2a
```
