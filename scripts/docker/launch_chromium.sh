#!/bin/bash
# Launch Playwright Chromium Browser
# This script launches the Chromium browser installed by Playwright

cd /home/kali/Tools/agent-zero

# Check if venv exists, if not use system Python
if [ -f venv/bin/python ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="/usr/bin/python3.11"
fi

echo "🌐 Launching Playwright Chromium Browser..."
echo ""

# Launch Chromium in headed mode (visible browser window)
$PYTHON_CMD << 'EOF'
from playwright.sync_api import sync_playwright
import sys

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
    
    # Create a new page
    page = browser.new_page()
    
    # Navigate to a page (or about:blank)
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "about:blank"
    
    page.goto(url)
    
    print(f"✅ Chromium browser launched!")
    print(f"   URL: {url}")
    print(f"   Browser will stay open until you close it.")
    print("")
    print("Press Ctrl+C to close the browser...")
    
    # Keep browser open
    try:
        input("Press Enter to close the browser...")
    except KeyboardInterrupt:
        pass
    finally:
        browser.close()
        playwright.stop()
        print("Browser closed.")
        
except Exception as e:
    print(f"❌ Error launching browser: {e}")
    sys.exit(1)
EOF

