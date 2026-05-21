# Bluesky LIVE setup (Step 4)

## What is an “app password”?

It is **not** your normal Bluesky login password.

| | Main password | App password |
|---|----------------|----------------|
| **Used for** | Logging in on the website/app | Scripts & apps (like PulseCup) |
| **You type it** | On bsky.app login screen | Only in your `.env` file |
| **Format** | Your chosen password | Bluesky generates one, e.g. `abcd-efgh-ijkl-mnop` |
| **Revoke** | Change account password | Delete that app password in settings anytime |

Bluesky created app passwords so you never put your real password in code. If `.env` leaks, you only revoke the app password — your account stays safe.

---

## Setup (5 minutes)

### 1. Create an app password on Bluesky

1. Log in at [https://bsky.app](https://bsky.app)
2. Go to **Settings** → **Privacy and security** → **App passwords**
   - Direct link: [https://bsky.app/settings/app-passwords](https://bsky.app/settings/app-passwords)
3. Click **Add App Password**
4. Name it e.g. `PulseCup Dashboard`
5. Bluesky shows a password **once** — copy it immediately (looks like `xxxx-xxxx-xxxx-xxxx`)

### 2. Add to your `.env` file (project root)

Open `FIFA-Project/.env` and add or update:

```env
BLUESKY_HANDLE=yourname.bsky.social
BLUESKY_APP_PASSWORD=paste-the-app-password-here
BLUESKY_DEMO_FALLBACK=false
```

**Handle tips:**
- Use your full handle, e.g. `manan123.bsky.social` (include `.bsky.social`)
- Or the email you use to log in — Bluesky accepts both

**Important:** Set `BLUESKY_DEMO_FALLBACK=false` so the collector uses **real posts only** (no synthetic demo data).

### 3. Test the connection

```powershell
cd backend
python test_bluesky_auth.py
```

You want to see:
- `Login: OK`
- `Search test: OK (N posts found)`

### 4. Run one live collection

```powershell
python -c "from collectors.bluesky import collect_bluesky; collect_bluesky()"
```

You want: `[Bluesky] Done (LIVE) — 32 teams...`

### 5. Confirm on the dashboard

- API: http://localhost:8000/api/status → `"bluesky": "live"` (after fresh collect)
- UI badges on Sentiment / Overview should show **LIVE** (not DEMO)

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Auth failed: 401` | Wrong handle or app password; create a new app password |
| `Search still 403` | Rare; retry in a few minutes or check Bluesky status |
| Still shows DEMO | Restart API after changing `.env`; run collector again |
| `No posts for Team X` | Normal — not every team has posts every hour |

---

## Security (team project)

- **Never** commit `.env` to Git (already in `.gitignore`)
- Share app password with teammates via a **password manager**, not Slack/email if possible
- Each teammate can use their **own** Bluesky app password on the same shared account, or one shared “bot” account
