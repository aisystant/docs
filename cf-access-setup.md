# Cloudflare Access + ORY Setup for dash.pwapps.com

WP-355 Ф17.5 — ORY auth вместо basic auth

## Prerequisites

- ORY OAuth2 client created (`scripts/create-ory-cf-client.sh`)
- `ORY_CLIENT_ID` and `ORY_CLIENT_SECRET` saved in GitHub secrets
- Access to Cloudflare Dashboard for `pwapps.com` zone
- Team name: `odd-dew-3a42` (domain: `odd-dew-3a42.cloudflareaccess.com`)

## Step 1: CF Zero Trust — Identity Provider

1. Open [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/odd-dew-3a42)
2. Go to **Settings** → **Authentication** → **Identity providers**
3. Click **Add an identity provider** → **OpenID Connect (OIDC)**
4. Fill in:
   - **Name:** `ORY-system-school`
   - **Client ID:** (from `ORY_CLIENT_ID` secret)
   - **Client secret:** (from `ORY_CLIENT_SECRET` secret)
   - **Auth URL:** `https://auth.system-school.ru/hydra/oauth2/auth`
   - **Token URL:** `https://auth.system-school.ru/hydra/oauth2/token`
   - **Certificate URL:** `https://auth.system-school.ru/hydra/.well-known/jwks.json`
   - **Scopes:** `openid`, `profile`, `email`
   - **Redirect URI:** (already set by Pasha in ORY client) `https://odd-dew-3a42.cloudflareaccess.com/cdn-cgi/access/callback`
5. Save

## Step 2: CF Access — Application

1. Go to **Access** → **Applications**
2. Click **Add an application** → **Self-hosted**
3. Fill in:
   - **Application name:** `dash-pwapps-guides`
   - **Session duration:** 24 hours
   - **Domain:** `dash.pwapps.com`
4. Add policies:
   - **Rule 1 (Allow):** Selector `Email`, Operator `matches regex`, Value `@aisystant.com|@iwe.io`
   - **Rule 2 (Allow):** Selector `Email`, Operator `matches regex`, Value `@system-school.ru`
5. Save

## Step 3: Remove Basic Auth

If `functions/_middleware.js` exists in this repo:

```bash
git rm functions/_middleware.js
git commit -m "chore(auth): remove basic auth middleware — ORY CF Access active"
```

## Step 4: Smoke Test

1. Open `https://dash.pwapps.com` in incognito window
2. Expect redirect to `auth.system-school.ru/hydra/oauth2/auth`
3. Login with ORY credentials
4. Expect redirect back to dash with access

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 after login | Email domain not in policy | Add domain to CF Access policy |
| `invalid_client` | Wrong CLIENT_ID/SECRET | Re-run `create-ory-cf-client.sh` |
| Redirect loop | Callback URL mismatch | Verify ORY client redirect_uri = `https://odd-dew-3a42.cloudflareaccess.com/cdn-cgi/access/callback` |
