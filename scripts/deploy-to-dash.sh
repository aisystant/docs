#!/usr/bin/env bash
# deploy-to-dash.sh — Deploy guides v4 to dash.pwapps.com
# WP-355 Ф18.2
#
# Usage:
#   ./scripts/deploy-to-dash.sh --dry-run
#   ./scripts/deploy-to-dash.sh --mode content_url
#   ./scripts/deploy-to-dash.sh --mode push --dist ./docs/.vitepress/dist

set -euo pipefail

# Defaults
DEPLOY_MODE="${DASH_DEPLOY_MODE:-content_url}"
DASH_ENDPOINT="${DASH_ENDPOINT:-https://dash.pwapps.com/api/v1/guides/deploy}"
DASH_API_TOKEN="${DASH_API_TOKEN:-}"
STAGING_URL="${STAGING_URL:-https://iwe-staging-docs.pages.dev}"
DIST_PATH="${DIST_PATH:-./docs/.vitepress/dist}"
VERSION="${VERSION:-$(git describe --tags --always --dirty 2>/dev/null || echo 'unknown')}"

DRY_RUN=false

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --mode) DEPLOY_MODE="$2"; shift 2 ;;
    --dist) DIST_PATH="$2"; shift 2 ;;
    --endpoint) DASH_ENDPOINT="$2"; shift 2 ;;
    --token) DASH_API_TOKEN="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Validation
if [[ -z "$DASH_API_TOKEN" ]]; then
  echo "::error::DASH_API_TOKEN is not set. Export it or pass --token."
  exit 1
fi

echo "=== Deploy to dash.pwapps.com ==="
echo "Mode:       $DEPLOY_MODE"
echo "Endpoint:   $DASH_ENDPOINT"
echo "Version:    $VERSION"
echo "Dry-run:    $DRY_RUN"

# Build payload based on mode
if [[ "$DEPLOY_MODE" == "content_url" ]]; then
  PAYLOAD=$(cat <<EOF
{
  "guide_id": "personal-design",
  "content_url": "$STAGING_URL",
  "version": "$VERSION",
  "metadata": {
    "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "source": "cf-pages-staging"
  }
}
EOF
)
  CURL_ARGS=(
    -sf -X POST "$DASH_ENDPOINT"
    -H "Authorization: Bearer $DASH_API_TOKEN"
    -H "Content-Type: application/json"
    -d "$PAYLOAD"
  )
elif [[ "$DEPLOY_MODE" == "push" ]]; then
  if [[ ! -d "$DIST_PATH" ]]; then
    echo "::error::DIST_PATH not found: $DIST_PATH"
    exit 1
  fi
  # Create a tarball of the dist
  TAR_FILE=$(mktemp)
  tar -czf "$TAR_FILE" -C "$DIST_PATH" .
  CURL_ARGS=(
    -sf -X POST "$DASH_ENDPOINT"
    -H "Authorization: Bearer $DASH_API_TOKEN"
    -F "content=@$TAR_FILE"
    -F "version=$VERSION"
    -F "guide_id=personal-design"
  )
else
  echo "::error::Unknown deploy mode: $DEPLOY_MODE. Use 'content_url' or 'push'."
  exit 1
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[DRY-RUN] Would execute:"
  echo "curl ${CURL_ARGS[*]}"
  if [[ "$DEPLOY_MODE" == "content_url" ]]; then
    echo "[DRY-RUN] Payload:"
    echo "$PAYLOAD"
  fi
  echo "[DRY-RUN] Done."
  exit 0
fi

# Execute deploy
echo "Sending deploy request..."
RESPONSE=$(curl "${CURL_ARGS[@]}" 2>/dev/null)
HTTP_CODE=${?}

if [[ $HTTP_CODE -ne 0 ]]; then
  echo "::error::Deploy request failed (curl exit $HTTP_CODE)"
  exit 1
fi

echo "Deploy successful. Response:"
echo "$RESPONSE"

# Smoke test: verify dash serves the content
echo "Running smoke test..."
SMOKE_URL="${DASH_ENDPOINT%/deploy}/personal-design/guide-1"
SMOKE_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "$SMOKE_URL" -H "Authorization: Bearer $DASH_API_TOKEN" 2>/dev/null || echo "000")

if [[ "$SMOKE_STATUS" == "200" ]]; then
  echo "Smoke test passed: $SMOKE_URL -> HTTP 200"
else
  echo "::warning::Smoke test failed: $SMOKE_URL -> HTTP $SMOKE_STATUS"
  exit 1
fi
