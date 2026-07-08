# Authentication

M365 Wrapped reads Microsoft 365 **usage reports** (org-aggregate, read-only). The only Graph
permission it ever asks for is **`Reports.Read.All`** — it cannot see message content, files, mailboxes,
or security configuration.

There are two ways to authenticate. **The tool picks automatically:**

| You set… | Mode used |
|---|---|
| nothing (no secret, no cert) | **Device-code sign-in** (default) — for people, no app registration |
| `CLIENT_SECRET` **or** `CLIENT_CERT_PATH` + `CLIENT_CERT_THUMBPRINT` | **App-only** — for headless / scheduled runs |

---

## Mode 1 — Device-code sign-in (default, zero setup)

Best for a person running it on their machine. **No app registration, no `.env`.**

```bash
docker compose run --rm wrapped run      # or: m365-wrapped run
```

The tool prints a code:

```
To sign in, use a web browser to open https://microsoft.com/devicelogin and enter the code CQFF-WYUTR
```

Open that URL, enter the code, and sign in with your Microsoft 365 account. Cards land in `./out/`.

**How it works**
- It uses a **built-in multi-tenant public-client app** (a client id ships in the tool — a client id is
  not a secret, exactly like the Azure CLI ships its own). It requests only the **delegated**
  `Reports.Read.All` scope.
- The **first** time anyone in a tenant uses it, a **Global Administrator** must approve that scope once
  — the sign-in page shows **"Consent on behalf of your organization."** After that, any user can run it.
- Nothing is stored anywhere except the output on your machine.

**About the "someone is signing in from …" screen** — this is a **normal anti-phishing check**. Microsoft
shows the **location of the machine that requested the code**. If you run the tool on your laptop it shows
your location; if you run it on a server, it shows the **server's** location (e.g. a cloud region). Only
approve a code you started yourself.

> Want to use **your own** app id instead of the built-in one? Set `CLIENT_ID` (and optionally
> `TENANT_ID`) in `.env`; the device-code flow will use yours. Your app must be **multi-tenant**, have
> **Allow public client flows = Yes**, and hold the **delegated** `Reports.Read.All` permission.

---

## Mode 2 — App-only (headless / automation)

Best for **scheduled or unattended** runs (cron, CI, a server) where no human is present to sign in.
You register your own Entra app with a secret or certificate.

### 1. Register the app
Entra admin center → **Identity → Applications → App registrations → New registration**
- **Name:** `M365 Wrapped`
- **Supported account types:** *Accounts in this organizational directory only* (single tenant)
- **Redirect URI:** leave blank
- Register, then copy the **Application (client) ID** and **Directory (tenant) ID**.

### 2. Grant the permission
**API permissions → Add a permission → Microsoft Graph → Application permissions**
- Add **`Reports.Read.All`**
- **Grant admin consent for &lt;tenant&gt;** (needs a Global Administrator) — status must show green.

### 3. Add a credential (pick one)

**Option A — Client secret** (easiest): **Certificates & secrets → Client secrets → New client secret**
→ set an expiry → **copy the Value now** (shown once). Put it in `CLIENT_SECRET`.
> Entra caps secrets at 24 months — for a long-lived setup use a certificate.

**Option B — Certificate** (no expiry pain): create a self-signed cert, upload its **public `.cer`**, keep
the **private** key locally.
```bash
openssl req -x509 -newkey rsa:2048 -sha256 -days 36500 -nodes -subj "/CN=M365 Wrapped" \
  -keyout m365-wrapped.key -out m365-wrapped.cer
openssl x509 -in m365-wrapped.cer -noout -fingerprint -sha1 | sed 's/.*=//; s/://g'   # thumbprint
```
**Certificates & secrets → Certificates → Upload certificate** → upload the **`.cer`** (public key only,
never the private key). Then set `CLIENT_CERT_PATH` (the PEM key) and `CLIENT_CERT_THUMBPRINT`.

### 4. Fill `.env`
```bash
cp .env.example .env
```
| Value | `.env` var |
|---|---|
| Directory (tenant) ID | `TENANT_ID` |
| Application (client) ID | `CLIENT_ID` |
| **Option A:** client secret value | `CLIENT_SECRET` |
| **Option B:** PEM key path + thumbprint | `CLIENT_CERT_PATH` · `CLIENT_CERT_THUMBPRINT` |

If **both** a secret and a cert are set, the **certificate wins**.

### 5. Run
```bash
docker compose run --rm wrapped run
```

---

## Troubleshooting

- **"admin consent required" / `AADSTS65001`** → a Global Administrator must approve `Reports.Read.All`
  once for the tenant (device-code: the "Consent on behalf of your organization" box; app-only: the
  **Grant admin consent** button).
- **`AADSTS7000218` / "public client flows"** (only with your own app in device-code) → set
  **Authentication → Allow public client flows = Yes** and add the *Mobile and desktop* platform.
- **`Auth failed`** (app-only) → wrong secret/thumbprint/IDs, or admin consent not granted.
- **Sign-in shows an unexpected location** → that's the machine that *requested* the code (e.g. a server),
  not an intruder — see the anti-phishing note above.
- **Empty cards** → the tenant may have very low activity, or Graph usage data is still aggregating
  (it lags ~1–2 days). Try `--period D30`.
- **Concealed names** → if your tenant conceals user names in reports, that's fine; Wrapped is
  org-aggregate and never uses names.
