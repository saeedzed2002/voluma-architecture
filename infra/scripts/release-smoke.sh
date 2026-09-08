#!/usr/bin/env sh
set -eu

: "${VOLUMA_PUBLIC_ORIGIN:?VOLUMA_PUBLIC_ORIGIN is required}"
: "${VOLUMA_SMOKE_ADMIN_EMAIL:?VOLUMA_SMOKE_ADMIN_EMAIL is required}"
: "${VOLUMA_SMOKE_ADMIN_PASSWORD:?VOLUMA_SMOKE_ADMIN_PASSWORD is required}"

base_url=${VOLUMA_PUBLIC_ORIGIN%/}
cookie_file=$(mktemp)
curl_insecure=""
if [ "${VOLUMA_SMOKE_ALLOW_INSECURE_TLS:-}" = "1" ]; then
  curl_insecure="--insecure"
fi
trap 'rm -f "$cookie_file"' EXIT HUP INT TERM

curl $curl_insecure --fail --silent --show-error --location "$base_url/en" > /dev/null
curl $curl_insecure --fail --silent --show-error --location "$base_url/fa" > /dev/null
curl $curl_insecure --fail --silent --show-error "$base_url/api/readyz" > /dev/null

headers=$(curl $curl_insecure --fail --silent --show-error --head "$base_url/en")
printf '%s\n' "$headers" | grep -qi "content-security-policy:.*frame-ancestors 'none'"
printf '%s\n' "$headers" | grep -qi "referrer-policy: strict-origin-when-cross-origin"
printf '%s\n' "$headers" | grep -qi "x-content-type-options: nosniff"

login_payload=$(docker compose exec -T \
  -e VOLUMA_SMOKE_ADMIN_EMAIL \
  -e VOLUMA_SMOKE_ADMIN_PASSWORD \
  api python -c 'import json, os; print(json.dumps({"email": os.environ["VOLUMA_SMOKE_ADMIN_EMAIL"], "password": os.environ["VOLUMA_SMOKE_ADMIN_PASSWORD"]}))')

curl $curl_insecure --fail --silent --show-error \
  --cookie-jar "$cookie_file" \
  --header "Origin: $base_url" \
  --header "Content-Type: application/json" \
  --data "$login_payload" \
  "$base_url/api/v1/admin/auth/login" > /dev/null

echo "Nginx release smoke checks passed. Verify a published project and public media derivative when production content exists."
