# Pre-Installed Tools in Agent Zero Container

DO NOT install these tools manually. They are already available in the container.

## Security & Penetration Testing

| Tool | Path | Purpose | Usage Example |
|------|------|---------|---------------|
| nmap | /usr/bin/nmap | Network scanner | `nmap -sV -p- target.com` |
| nikto | /usr/bin/nikto | Web server vulnerability scanner | `nikto -h http://target.com` |
| nuclei | /usr/local/bin/nuclei | Vulnerability scanner with templates | `nuclei -u http://target.com` |
| sqlmap | /usr/bin/sqlmap | SQL injection testing | `sqlmap -u "http://target.com?id=1"` |
| gobuster | /usr/bin/gobuster | Directory/file brute-forcing | `gobuster dir -u http://target.com -w wordlist.txt` |
| wpscan | /usr/bin/wpscan | WordPress vulnerability scanner | `wpscan --url http://target.com` |

## Development & Utilities

| Tool | Path | Purpose | Usage Example |
|------|------|---------|---------------|
| git | /usr/bin/git | Version control | `git clone https://github.com/user/repo` |
| docker | /usr/bin/docker | Container management (Docker-in-Docker) | `docker ps` |
| curl | /usr/bin/curl | HTTP client | `curl -X GET https://api.example.com` |
| wget | /usr/bin/wget | File downloader | `wget https://example.com/file.zip` |
| jq | /usr/bin/jq | JSON processor | `echo '{"key":"value"}' \| jq .key` |
| python3 | /opt/venv-a0/bin/python3 | Python interpreter (main venv) | `/opt/venv-a0/bin/python3 script.py` |
| pip | /opt/venv-a0/bin/pip | Python package installer | `/opt/venv-a0/bin/pip install package` |
| node | /usr/bin/node | Node.js runtime | `node script.js` |
| npm | /usr/bin/npm | Node package manager | `npm install package` |

## Browser & Automation

| Tool | Path | Purpose | Usage Example |
|------|------|---------|---------------|
| chromium | /root/.cache/ms-playwright/chromium-*/chrome-linux/chrome | Playwright browser | Via `crawl4ai_rag` MCP tools |
| playwright | /opt/venv-a0/bin/playwright | Browser automation | `playwright install chromium` |

## Text & Data Processing

| Tool | Path | Purpose | Usage Example |
|------|------|---------|---------------|
| sed | /usr/bin/sed | Stream editor | `sed 's/old/new/g' file.txt` |
| awk | /usr/bin/awk | Pattern scanning | `awk '{print $1}' file.txt` |
| grep | /usr/bin/grep | Pattern matching | `grep "pattern" file.txt` |
| tr | /usr/bin/tr | Character translation | `echo "HELLO" \| tr '[:upper:]' '[:lower:]'` |
| cut | /usr/bin/cut | Column extraction | `cut -d',' -f1 file.csv` |
| sort | /usr/bin/sort | Sort lines | `sort file.txt` |
| uniq | /usr/bin/uniq | Remove duplicates | `sort file.txt \| uniq` |
| wc | /usr/bin/wc | Word count | `wc -l file.txt` |

## File Operations

| Tool | Path | Purpose | Usage Example |
|------|------|---------|---------------|
| tar | /usr/bin/tar | Archive files | `tar -czf archive.tar.gz dir/` |
| unzip | /usr/bin/unzip | Extract ZIP archives | `unzip file.zip` |
| rsync | /usr/bin/rsync | File synchronization | `rsync -av src/ dest/` |
| find | /usr/bin/find | Search for files | `find /path -name "*.py"` |
| tree | /usr/bin/tree | Directory structure | `tree -L 2 /path` |

## Network Tools

| Tool | Path | Purpose | Usage Example |
|------|------|---------|---------------|
| netstat | /usr/bin/netstat | Network statistics | `netstat -tulpn` |
| ss | /usr/bin/ss | Socket statistics | `ss -tulpn` |
| ping | /usr/bin/ping | Network connectivity | `ping -c 4 google.com` |
| traceroute | /usr/bin/traceroute | Network path tracing | `traceroute google.com` |
| dig | /usr/bin/dig | DNS lookup | `dig example.com` |
| nc | /usr/bin/nc | Netcat (networking utility) | `nc -zv target.com 80` |

## Important Notes

- **All tools are in PATH**: Use direct commands (e.g. `nmap -sV target.com`)
- **Python venv**: Main venv is at `/opt/venv-a0/`. For Python scripts, use:
  - `/opt/venv-a0/bin/python3 script.py` (direct)
  - Or activate: `source /opt/venv-a0/bin/activate` then `python3 script.py`
- **Playwright**: Use `crawl4ai_rag` MCP tools for web scraping instead of raw Playwright
- **Google APIs**: Use main venv (`/opt/venv-a0/bin/python3`) for Drive/Gmail scripts (see `knowledge/main/google_apis.md`)
- **Docker-in-Docker**: Agent Zero container can control other Docker containers on the host
- **Security tools**: Always get explicit authorization before running scans; document Rules of Engagement (ROE)

## Usage Patterns

### Running Security Scans

Always verify authorization and scope before scanning:

```bash
# 1. Verify ROE (Rules of Engagement)
cat /a0/usr/projects/PROJECT_NAME/ROE.md

# 2. Run reconnaissance
nmap -sV -p- target.com

# 3. Web server scan
nikto -h http://target.com

# 4. Vulnerability scan
nuclei -u http://target.com -t cves/
```

### Python Scripts with Main Venv

```bash
# For Google API scripts (now supported in main venv)
/opt/venv-a0/bin/python3 << 'EOF'
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file("/a0/usr/projects/a0_sip/token.json")
drive = build("drive", "v3", credentials=creds)
results = drive.files().list(pageSize=10).execute()
print(results)
EOF
```

### Web Scraping with MCP Tools

```bash
# Use crawl4ai_rag MCP tools instead of raw Playwright
# Example: Ask agent to "Crawl https://example.com and extract the title"
# Agent will use crawl4ai_rag.crawl_website automatically
```

## Don't Reinstall

If agent tries to install these tools:
- **Stop**: All tools are pre-installed
- **Use directly**: `nmap target.com` (not `apt install nmap`)
- **Check version**: `nmap --version` to verify it's installed
