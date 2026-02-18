#!/bin/bash
# Launch Playwright Chromium Browser with a URL
# Usage: ./launch_chromium_url.sh [URL]

cd /home/kali/Tools/agent-zero

# Check if venv exists, if not use system Python
if [ -f venv/bin/python ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="/usr/bin/python3.11"
fi

URL=${1:-"about:blank"}

echo "🌐 Launching Playwright Chromium Browser..."
echo "   URL: $URL"
echo ""

# Launch Chromium in headed mode
$PYTHON_CMD << EOF
from playwright.sync_api import sync_playwright
import sys
import time

try:
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
        ]
    )
    
    page = browser.new_page()
    page.goto("$URL")
    
    print("✅ Browser launched!")
    print("   Close the browser window to exit.")
    print("")
    
    # Keep browser open until closed
    try:
        while browser.is_connected():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        browser.close()
        playwright.stop()
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

