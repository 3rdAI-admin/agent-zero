# Playwright Chromium Browser Setup

Playwright Chromium is already installed and ready to use. This guide shows how to launch it manually.

## Quick Start

### Launch Blank Browser
```bash
./launch_chromium.sh
```

### Launch with URL
```bash
./launch_chromium_url.sh https://www.google.com
```

## Browser Location

The Chromium browser is installed at:
```
~/.cache/ms-playwright/chromium_headless_shell-1169/
```

## Usage Examples

### Basic Launch (Python)
```python
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
page = browser.new_page()
page.goto("https://www.google.com")
input("Press Enter to close...")
browser.close()
playwright.stop()
```

### Launch from Command Line
```bash
cd /home/kali/Tools/agent-zero
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=False); b.new_page().goto('https://www.google.com'); input('Press Enter...'); b.close(); p.stop()"
```

## Headless vs Headed Mode

- **Headless (default for automation)**: Browser runs without GUI
- **Headed (for manual use)**: Browser shows GUI window

The launcher scripts use `headless=False` to show the browser window.

## Integration with Agent Zero

Agent Zero automatically uses this Chromium browser for:
- Web automation tasks
- Browser-based testing
- Web scraping
- Browser interactions

The browser is configured in `python/tools/browser_agent.py` and runs in headless mode for automation.

## Troubleshooting

If the browser doesn't launch:
1. Check Playwright installation: `python3 -m playwright --version`
2. Verify browser is installed: `ls ~/.cache/ms-playwright/`
3. Reinstall browser: `python3 -m playwright install chromium`

## Notes

- This is the same Chromium browser used by Agent Zero
- It's installed via Playwright, not as a system package
- Works on ARM64 (unlike official Google Chrome)
- Fully compatible with Chrome extensions and features

