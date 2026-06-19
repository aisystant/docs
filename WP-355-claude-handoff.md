# WP-355 Handoff → Claude (CF Access + ORY setup)

## Context
- WP-355: Production Deploy руководств v4, Ф17.5 ORY auth setup
- Паша создал ORY OAuth2 client для CF Access
- Team name найден: `odd-dew-3a42`
- У Клода есть Cloudflare API token с правами на Access

## Current Status

### ✅ Done
- [x] ORY client credentials получены от Паши
  - `client_id`: `043d1532-71d5-41ea-be6e-efd9e9d83944`
  - `client_secret`: `UCNiFzbKR74GBNnBT_Q7Pp9H5k`
- [x] GitHub secrets (`aisystant/docs`): `ORY_CLIENT_ID`, `ORY_CLIENT_SECRET`
- [x] Team name: `odd-dew-3a42` (domain: `odd-dew-3a42.cloudflareaccess.com`)
- [x] Redirect URI (для Паши): `https://odd-dew-3a42.cloudflareaccess.com/cdn-cgi/access/callback`

### ⚠️ Blocker Found
**dash.pwapps.com НЕ проксируется через Cloudflare.**
- DNS resolves to `185.236.10.253` (direct IP, не Cloudflare)
- HTTP response: `307` redirect to `/account`, **no CF headers** (`cf-ray`, `cloudflare` missing)
- CF Access **will not work** without orange-cloud proxying

### 🔲 Remaining Tasks

#### 1. Fix DNS proxying for dash.pwapps.com
- Cloudflare Account ID: `b6ea9a991319d14c2e78590526c5fb4f`
- Zone: `pwapps.com`
- Check DNS record for `dash.pwapps.com` — must be **Proxied** (orange cloud), not DNS-only (grey)
- If missing — create A/CNAME record pointing to origin, enable proxying

#### 2. Verify CF Access Identity Provider
- Zero Trust team: `odd-dew-3a42`
- Should exist: OIDC provider → ORY Hydra
  - Name: `ORY-system-school`
  - Client ID: `043d1532-71d5-41ea-be6e-efd9e9d83944`
  - Client Secret: `UCNiFzbKR74GBNnBT_Q7Pp9H5k`
  - Auth URL: `https://auth.system-school.ru/hydra/oauth2/auth`
  - Token URL: `https://auth.system-school.ru/hydra/oauth2/token`
  - JWKS URL: `https://auth.system-school.ru/hydra/.well-known/jwks.json`
  - Scopes: `openid`, `profile`, `email`
- Verify via API: `GET /accounts/{account_id}/access/identity_providers`

#### 3. Verify CF Access Application
- Should exist: Self-hosted app for `dash.pwapps.com`
- Verify via API: `GET /accounts/{account_id}/access/apps`

#### 4. Verify Access Policy
- Allow policy: email-based
- Suggested domains: `@aisystant.com`, `@system-school.ru`
- Adjust based on actual pilot emails

#### 5. Remove basic auth middleware (if exists)
- File: `docs/functions/_middleware.js`
- If exists: `git rm functions/_middleware.js` + commit

#### 6. Smoke test
- `curl -I https://dash.pwapps.com` → expect CF Access redirect (not 307 to /account)
- Open in browser → expect ORY login page
- Login → expect access to dash

## Files Updated
- `docs/scripts/create-ory-cf-client.sh` — team name fixed
- `docs/cf-access-setup.md` — team name + redirect URI documented

## Contact
- Паша: ORY admin, client credentials, redirect URI verification
- Андрей: DNS zone management (if CF DNS issues)
