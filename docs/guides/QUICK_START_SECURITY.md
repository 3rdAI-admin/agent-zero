# Quick Start: Agent Zero Security Testing

## ✅ Configuration Complete

Your `docker-compose.yml` has been configured with network capabilities for security scanning.

## 🚀 Quick Start Steps

### 1. Restart Container (Apply New Configuration)

```bash
cd /Users/james/Docker/AgentZ
docker compose down
docker compose up -d
```

### 2. Install Security Tools

**Option A: Quick Install (Recommended)**
```bash
docker exec -it agent-zero bash -c "apt-get update && apt-get install -y nmap nikto gobuster sqlmap masscan"
```

**Option B: Full Install (All Tools)**
```bash
docker cp docker/install_security_tools.sh agent-zero:/tmp/
docker exec -it agent-zero bash /tmp/install_security_tools.sh
```

### 3. Verify Network Access

```bash
# Test ping to your router/gateway
docker exec -it agent-zero ping -c 3 192.168.1.1

# Test nmap
docker exec -it agent-zero nmap --version
```

### 4. Start Using Agent Zero

Access the Web UI: http://localhost:8888

## 📝 Example Prompts for Agent Zero

**Network Discovery:**
```
Scan the network 192.168.1.0/24 to discover all active hosts and identify their open ports and services
```

**Vulnerability Scan:**
```
Perform a comprehensive vulnerability scan of 192.168.1.100 including port scanning, service detection, and vulnerability assessment
```

**Web Application Testing:**
```
Test the web application at http://192.168.1.100 for common vulnerabilities using nikto and gobuster
```

## 🔧 Advanced: Full LAN Access (Host Network Mode)

For maximum network access (recommended for comprehensive pen testing):

1. Edit `docker-compose.yml`
2. Uncomment: `network_mode: host`
3. Comment out: `cap_add` section
4. Comment out: `ports` section
5. Restart: `docker compose down && docker compose up -d`

**Note:** With host network mode, the Web UI will be on port 80 (not 8888).

## ⚠️ Important Reminders

- **Only scan networks you own or have permission to test**
- **Unauthorized scanning is illegal**
- **Use responsibly and ethically**

## 📚 Full Documentation

See [SECURITY_SETUP.md](./SECURITY_SETUP.md) for complete details.
