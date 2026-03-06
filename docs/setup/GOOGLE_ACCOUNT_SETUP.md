# Using a Google Account (e.g. agentz@th3rdai.com) with Agent Zero

You can use a dedicated Google account (e.g. **agentz@th3rdai.com**) for:

1. **Gmail** – Agent Zero can read (and with code/smtp, send) email as that account.
2. **Google Gemini** – Use that account’s API key for the Google/Gemini model provider.

## Persistence (settings persist until you change them)

| Setting | Stored in | Persists because |
|--------|------------|-------------------|
| **Google (Gemini) API key** | Repo **`.env`** as `API_KEY_GOOGLE`, or **Settings → API Keys** (saved to `usr/.env` under your user volume) | `.env` is on the host; Docker mounts it. API keys are also written to `usr/.env` when you save in the UI. |
| **Gmail (email)** | Repo **`.env`** as `EMAIL_USER` and `EMAIL_PASSWORD`, **or** **Settings → Secrets** (saved to `usr/secrets.env`) | `.env` is mounted and loaded into the environment; the app also reads these from Secrets. If you use the **A0_volume** mount, `usr/secrets.env` is on the host and persists across rebuilds. |

- **Docker (recommended):** Put `API_KEY_GOOGLE`, `EMAIL_USER`, and `EMAIL_PASSWORD` in the repo **`.env`** file. Compose mounts `./.env` into the container and injects it as environment variables, so these values persist until you edit `.env` or change them in Settings.
- **Secrets file:** If you use **Settings → Secrets**, values are written to `usr/secrets.env`. With the `A0_volume:/a0/usr` mount, that file lives on the host at `A0_volume/secrets.env` and persists across container rebuilds.
- **API keys from UI:** Saving **Settings → API Keys** writes keys to `usr/.env` (under `A0_volume` when mounted), so they persist until you change them again.

---

## 1. Gmail (IMAP) for agentz@th3rdai.com

Agent Zero’s email helpers use **IMAP** with credentials from **Secrets**. Configure the account once, then the agent can use it when you ask (e.g. “Check my Gmail inbox”).

### 1.1 Create a Gmail App Password

1. Sign in to [Google Account](https://myaccount.google.com/) as **agentz@th3rdai.com**.
2. Turn on **2-Step Verification** (Security → How you sign in to Google).
3. Create an **App password**:
   - Security → 2-Step Verification → **App passwords**
   - Select app: **Mail**, device: **Other** (e.g. “Agent Zero”)
   - Copy the **16-character password** (no spaces).

### 1.2 Add credentials to Agent Zero

**Option A – Repo `.env` (recommended for persistence)**

In the repo root **`.env`** file add (use straight double quotes for the password if it contains spaces):

```bash
EMAIL_USER=agentz@th3rdai.com
EMAIL_PASSWORD=your_16_char_app_password_here
```

With Docker Compose, `env_file: .env` injects these into the container; the app reads them and they persist until you change `.env`.

**Option B – Settings UI (Secrets)**

1. Open Agent Zero → **Settings** → **Secrets**.
2. Add two entries (one per line, or your UI’s format):
   - `EMAIL_USER=agentz@th3rdai.com`
   - `EMAIL_PASSWORD=` + the 16-character App Password

**Option C – secrets file (Docker/volume)**

If you use the bind mount for `usr` (e.g. `A0_volume` → `/a0/usr`), edit the secrets file on the host:

- Path: **`<your_volume>/secrets.env`** (e.g. `A0_volume/secrets.env`).

Add:

```bash
EMAIL_USER=agentz@th3rdai.com
EMAIL_PASSWORD=your_16_char_app_password_here
```

Secrets are also documented under [Secrets & Variables](../guides/usage.md#secrets--variables). The email helper uses `EMAIL_USER` and `EMAIL_PASSWORD` when connecting to Gmail (e.g. `imap.gmail.com`).

### 1.3 Use in prompts

After saving, you can prompt the agent to use that account, for example:

- *“Check my Gmail inbox for the last 24 hours”*
- *“Summarize unread emails from agentz@th3rdai.com”*

The agent will use the credentials from Secrets when calling the email client.

---

## 2. Google Gemini (LLM) with agentz@th3rdai.com

To use **Gemini** with the same Google account:

1. Sign in to [Google AI Studio](https://aistudio.google.com/) as **agentz@th3rdai.com**.
2. Create or copy an **API key** (Get API key / Create API key).
3. In Agent Zero, set that key in one of these ways:
   - **Settings → API Keys** → **Google** (or “Gemini”) → paste the key, Save.
   - Or in **`.env`** (if you use env-based config):  
     `API_KEY_GOOGLE=your_api_key_here`

Then choose a Google/Gemini model (e.g. `google/gemini-2.0-flash` or the default in Settings) for chat or utility.

---

## 3. Summary

| Use case        | Where to configure | What to set |
|-----------------|--------------------|-------------|
| Gmail (read)    | **`.env`** (recommended), or Settings → Secrets / `usr/secrets.env` | `EMAIL_USER=agentz@th3rdai.com`, `EMAIL_PASSWORD=<App Password>` |
| Google Gemini   | **`.env`** or Settings → API Keys | `API_KEY_GOOGLE=<key from Google AI Studio>` |

- Use a **Gmail App Password** for email, not your normal account password.
- Keep **`.env`** and **`secrets.env`** out of version control (add them to `.gitignore` if needed).
- Settings persist until you change them; see **Persistence** above for where each value is stored.
