#!/usr/bin/env bash
# create-ory-cf-client.sh — Create OAuth2 client in ORY Hydra for Cloudflare Access
# WP-355 Ф17.5
#
# Usage:
#   export ORY_ADMIN_URL=https://auth.system-school.ru/hydra
#   export ORY_ADMIN_TOKEN=<token from Pasha>
#   ./scripts/create-ory-cf-client.sh

set -euo pipefail

ORY_ADMIN_URL="${ORY_ADMIN_URL:-https://auth.system-school.ru/hydra}"
ORY_ADMIN_TOKEN="${ORY_ADMIN_TOKEN:-}"
# WP-355: Team name confirmed — odd-dew-3a42
# Pasha already created the ORY client with this redirect_uri.
CF_ACCESS_CALLBACK="${CF_ACCESS_CALLBACK:-https://odd-dew-3a42.cloudflareaccess.com/cdn-cgi/access/callback}"
CLIENT_NAME="cf-access-dash-pwapps"

if [[ -z "$ORY_ADMIN_TOKEN" ]]; then
  echo "::error::ORY_ADMIN_TOKEN is not set. Get it from Pasha (WP-187 ORY_ADMIN_TOKEN)."
  exit 1
fi

echo "Creating OAuth2 client in ORY Hydra for CF Access..."
echo "Admin URL: $ORY_ADMIN_URL"
echo "Client name: $CLIENT_NAME"

RESPONSE=$(curl -sf -X POST "$ORY_ADMIN_URL/admin/clients" \
  -H "Authorization: Bearer $ORY_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"client_name\": \"$CLIENT_NAME\",
    \"grant_types\": [\"authorization_code\"],
    \"response_types\": [\"code\"],
    \"redirect_uris\": [\"$CF_ACCESS_CALLBACK\"],
    \"scope\": \"openid profile email\",
    \"token_endpoint_auth_method\": \"client_secret_post\"
  }" 2>/dev/null)

if [[ $? -ne 0 ]]; then
  echo "::error::Failed to create ORY client"
  exit 1
fi

CLIENT_ID=$(echo "$RESPONSE" | grep -o '"client_id":"[^"]*"' | cut -d'"' -f4)
CLIENT_SECRET=$(echo "$RESPONSE" | grep -o '"client_secret":"[^"]*"' | cut -d'"' -f4)

echo ""
echo "=== ORY OAuth2 client created ==="
echo "Client ID:     $CLIENT_ID"
echo "Client Secret: ${CLIENT_SECRET:0:8}... (save this!)"
echo ""
echo "Next steps:"
echo "1. Save CLIENT_ID and CLIENT_SECRET as GitHub secrets in aisystant/docs:"
echo "   gh secret set ORY_CLIENT_ID -R aisystant/docs --body '$CLIENT_ID'"
echo "   gh secret set ORY_CLIENT_SECRET -R aisystant/docs --body '$CLIENT_SECRET'"
echo "2. Configure CF Access Identity Provider (see docs/cf-access-setup.md)"
echo "3. CF Access team: odd-dew-3a42 (odd-dew-3a42.cloudflareaccess.com)"
