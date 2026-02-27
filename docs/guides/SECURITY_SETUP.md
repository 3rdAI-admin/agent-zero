# Agent Zero Security & Penetration Testing Setup

This guide explains how to configure Agent Zero for LAN access and security testing operations.

## Network Configuration

The `docker-compose.yml` has been configured with two options for network access:

### Option 1: Host Network Mode (Recommended for Pen Testing)
This gives the container full access to the host's network stack, allowing it to scan the entire LAN.

**To enable:**
1. Uncomment the `network_mode: host` line in `docker-compose.yml`
2. Comment out or remove the `cap_add` section (not needed with host mode)
3. Remove the `ports` section (not needed with host mode)

**Pros:**
- Full network access
- Can scan entire LAN
- No port mapping needed
- Best for comprehensive security testing

**Cons:**
- Less isolation
- Container shares host network namespace

### Option 2: Bridge Mode with Capabilities (Current Default)
This provides network scanning capabilities while maintaining some isolation.

**Current configuration:**
- `cap_add` includes `NET_RAW`, `NET_ADMIN`, and `SYS_ADMIN`
- Allows raw sockets for nmap and other tools
- Maintains Docker network isolation

**Pros:**
- Better isolation
- Still allows network scanning
- More secure default

**Cons:**
- May have limitations with some advanced network operations
- Requires port mapping for services

### Resolving LAN hostnames (so Agent Zero can “see” other machines by name)

To let the container resolve friendly names (e.g. `nas`, `my-server`) to LAN IPs—so tools like `ping`, `nmap`, and `ssh` work by hostname—use **`extra_hosts`** in `docker-compose.yml`. That injects entries into the container’s `/etc/hosts`.

**Correct syntax** (one entry per host, or multiple hostnames for one IP):

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"   # host machine (already present)
  - "nas:192.168.50.5"                    # hostname:ip
  - "my-server:192.168.50.10"
  - "router:192.168.50.1"
  # Multiple names for same IP: "name1 name2:192.168.50.20"
  - "printer print-server:192.168.50.20"
```

- Use **hostname** (no spaces) then a single colon then **IP**. No spaces around the colon.
- After changing `extra_hosts`, run `docker compose up -d` (recreate the container so the new entries are applied).

**Do not use the Settings Secret Store or Variables Store for this.** Those are for credentials and env vars the agent uses; they do not change the container’s `/etc/hosts`. Name resolution for commands like `ping nas` or `nmap my-server` must come from `extra_hosts` (or a custom `/etc/hosts` mount, which is more involved).

**Optional:** If you only need the *agent* to know “nas = 192.168.50.5” for planning or prompts (and don’t need the OS to resolve the name), you can add a line in **Settings → Secrets → Variables Store**, e.g. `LAN_HOSTS=nas=192.168.50.5,server=192.168.50.10`. The agent can read that; the shell still won’t resolve `nas` unless you also add it via `extra_hosts`.

## Installing Security Tools

### Method 1: Run Installation Script Inside Container

```bash
# Copy script into container
docker cp docker/install_security_tools.sh agent-zero:/tmp/

# Execute inside container
docker exec -it agent-zero bash /tmp/install_security_tools.sh
```

### Method 2: Add to Dockerfile (Permanent)

Add this to your Dockerfile before the final CMD:

```dockerfile
# Install security tools
COPY docker/install_security_tools.sh /tmp/
RUN bash /tmp/install_security_tools.sh && rm /tmp/install_security_tools.sh
```

Then rebuild:
```bash
docker compose build agent-zero
docker compose up -d
```

### Method 3: Install Tools On-Demand via Agent Zero

You can ask Agent Zero to install tools as needed using the code execution tool:

```
Please install nmap and nikto using apt-get
```

## Using Security Tools with Agent Zero

### Via Code Execution Tool

Agent Zero can execute terminal commands directly. Examples:

**Network Scanning:**
```
Scan the local network 192.168.1.0/24 for open ports using nmap
```

**Web Application Testing:**
```
Run nikto against http://192.168.1.100 to check for vulnerabilities
```

**Vulnerability Assessment:**
```
Perform a comprehensive nmap scan of 192.168.1.0/24 with service detection and OS detection
```

### Example Commands Agent Zero Can Execute

**Network Discovery:**
```bash
# Discover hosts on network
nmap -sn 192.168.1.0/24

# Port scan with service detection
nmap -sV -sC 192.168.1.100

# Full TCP scan
nmap -p- 192.168.1.100
```

**Web Application Scanning:**
```bash
# Nikto web scan
nikto -h http://192.168.1.100

# Directory brute force
gobuster dir -u http://192.168.1.100 -w /usr/share/wordlists/dirb/common.txt

# SQL injection testing
sqlmap -u "http://192.168.1.100/page?id=1" --batch
```

**Vulnerability Scanning:**
```bash
# Comprehensive nmap scan
nmap -sS -sV -sC -A -O 192.168.1.100

# SSL/TLS testing
sslscan 192.168.1.100:443
testssl.sh 192.168.1.100
```

## Important Security Considerations

### ⚠️ Legal and Ethical Warnings

1. **Only scan networks you own or have explicit permission to test**
2. **Unauthorized scanning is illegal in most jurisdictions**
3. **Use Agent Zero responsibly and ethically**
4. **Document all testing activities and obtain proper authorization**

### Network Access Verification

Test network access from inside the container:

```bash
# Check if container can reach LAN
docker exec -it agent-zero ping -c 3 192.168.1.1

# Test nmap capabilities
docker exec -it agent-zero nmap --version

# Verify network interfaces
docker exec -it agent-zero ip addr show
```

### Firewall Configuration

Ensure your host firewall allows:
- Outbound connections from Docker containers
- Inbound connections to the Agent Zero web UI (port 8888)

On Linux:
```bash
# Allow Docker containers to access LAN
sudo iptables -I DOCKER-USER -i docker0 -j ACCEPT
sudo iptables -I DOCKER-USER -o docker0 -j ACCEPT
```

## Using the Hacker Agent Profile

Agent Zero includes a "hacker" agent profile optimized for security testing:

1. Go to Settings in the Web UI
2. Under "Agent Configuration", set "Prompts Subdirectory" to `hacker`
3. This profile includes prompts optimized for penetration testing tasks

## Troubleshooting

### Network Access Issues

**Problem:** Container cannot reach LAN hosts
- **Solution:** Switch to `network_mode: host` or check firewall rules

**Problem:** nmap fails with "Operation not permitted"
- **Solution:** Ensure `cap_add: NET_RAW` is set in docker-compose.yml

**Problem:** Tools not found
- **Solution:** Run the installation script or install tools manually

### Performance Issues

- Large network scans can be resource-intensive
- Consider scanning smaller subnets or using faster scan options
- Monitor container resources: `docker stats agent-zero`

## Example Agent Zero Prompts for Security Testing

**Vulnerability Scan:**
```
Perform a comprehensive vulnerability scan of the 192.168.1.0/24 network. 
Identify all hosts, open ports, services, and potential vulnerabilities. 
Generate a detailed report.
```

**Penetration Test:**
```
Conduct a penetration test of 192.168.1.100. Start with reconnaissance, 
then perform port scanning, service enumeration, vulnerability assessment, 
and attempt to identify potential attack vectors.
```

**Web Application Security:**
```
Test the web application at http://192.168.1.100 for common vulnerabilities 
including SQL injection, XSS, directory traversal, and misconfigurations.
```

## Additional Resources

- [Kali Linux Tools Documentation](https://www.kali.org/tools/)
- [Nmap Documentation](https://nmap.org/book/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Agent Zero Documentation](./docs/)
