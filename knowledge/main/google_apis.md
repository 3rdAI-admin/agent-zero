# Google API Integration — Already Configured

DO NOT recreate, reinstall, or re-authenticate Google API access. Everything below is already set up and working.

## Authentication

- **OAuth Credentials**: `/a0/usr/projects/a0_sip/credentials.json`
- **OAuth Token**: `/a0/usr/projects/a0_sip/token.json` (auto-refreshes)
- **Account**: bill@th3rdai.com
- **Token includes all required scopes** — no need to re-authorize

### Authorized OAuth Scopes

- `gmail.send` — Send emails
- `gmail.readonly` — Read emails
- `drive` — Google Drive (upload, create folders, share)
- `spreadsheets` — Google Sheets (read/write)
- `presentations` — Google Slides (create/edit)
- `cloud-platform` — Google Cloud Platform APIs

## How to Connect to Any Google API

Use the token file directly. Do NOT re-run OAuth flows or ask the user to re-authenticate.

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/a0/usr/projects/a0_sip/token.json"
creds = Credentials.from_authorized_user_file(TOKEN)

# Gmail
gmail = build("gmail", "v1", credentials=creds)

# Google Drive
drive = build("drive", "v3", credentials=creds)

# Google Sheets
sheets = build("sheets", "v4", credentials=creds)

# Google Slides
slides = build("slides", "v1", credentials=creds)
```

### Token Refresh (if expired)

If the token has expired, refresh it before use:

```python
import json, requests
from datetime import datetime, timezone, timedelta

with open("/a0/usr/projects/a0_sip/credentials.json") as f:
    client_data = json.load(f).get("installed", {})
with open("/a0/usr/projects/a0_sip/token.json") as f:
    t = json.load(f)

resp = requests.post("https://oauth2.googleapis.com/token", data={
    "refresh_token": t["refresh_token"],
    "client_id": client_data["client_id"],
    "client_secret": client_data["client_secret"],
    "grant_type": "refresh_token"
})
td = resp.json()
t["token"] = td["access_token"]
t["expiry"] = (datetime.now(timezone.utc) + timedelta(seconds=3600)).strftime("%Y-%m-%dT%H:%M:%SZ")
with open("/a0/usr/projects/a0_sip/token.json", "w") as f:
    json.dump(t, f)
```

## Existing Scripts (already created — reuse these, do not recreate)

| Script | Path | Purpose |
|--------|------|---------|
| Gmail OAuth test | `/a0/usr/projects/a0_sip/gmail_oauth.py` | Test Gmail API connection |
| Send email | `/a0/usr/workdir/send_email.py` | Send emails via Gmail API |
| Send email (auto) | `/a0/usr/workdir/send_email_auto.py` | Automated email sending |
| Upload to Drive | `/a0/usr/workdir/upload_to_drive.py` | Upload files to Google Drive, create folders |
| Sheets model | `/a0/usr/workdir/sheets_model.py` | Read/write Google Sheets data |
| Create presentation | `/a0/usr/workdir/create_pres.py` | Create Google Slides presentations |
| Update slides | `/a0/usr/workdir/update_slides_v2.py` | Update existing Slides presentations |
| Preseed deck | `/a0/usr/workdir/preseed_deck.py` | Generate preseed investor deck |
| Branded presentation | `/a0/usr/workdir/branded_pres.py` | Create branded presentations |
| Update financials | `/a0/usr/workdir/update_financials.py` | Update financial data in Sheets/Slides |
| Financial model | `/a0/usr/workdir/fin_model.py` | Financial modeling via Sheets |

## Virtual Environment

A dedicated Python virtual environment with all Google API packages is available:

- **Path**: `/a0/usr/workdir/google_api_env/`
- **Python**: `/a0/usr/workdir/google_api_env/bin/python3` (Python 3.13)
- **Installed packages**: `google-api-python-client`, `google-auth`, `google-auth-httplib2`, `google-auth-oauthlib`, `googleapis-common-protos`

To use it in terminal:
```bash
source /a0/usr/workdir/google_api_env/bin/activate
python3 script.py
```

Or call directly:
```bash
/a0/usr/workdir/google_api_env/bin/python3 script.py
```

## Important Reminders

- NEVER ask the user to re-authenticate or create new OAuth credentials
- NEVER recreate scripts that already exist (check the table above first)
- ALWAYS use the token at `/a0/usr/projects/a0_sip/token.json`
- If a script needs modification, edit the existing file rather than creating a new one
- The `code_execution_tool` with `runtime: "python"` may fail with "ipython: command not found" — use `runtime: "terminal"` with explicit python path instead
