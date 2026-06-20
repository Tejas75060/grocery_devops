#!/usr/bin/env bash
# Start dev Vault (if not running) and seed the grocery DB credentials.
# The app reads these at startup when VAULT_ADDR + VAULT_TOKEN are set
# (see app/config.py + app/vault_client.py).
set -euo pipefail
cd "$(dirname "$0")/.."

export VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
export VAULT_TOKEN="${VAULT_TOKEN:-root}"

if ! docker ps --format '{{.Names}}' | grep -q '^vault$'; then
  echo "==> Starting dev Vault"
  docker compose -f docker-compose.vault.yml up -d
  sleep 4
fi

# Run vault CLI inside the container so a local install isn't required.
v() { docker exec -e VAULT_ADDR="http://127.0.0.1:8200" -e VAULT_TOKEN="$VAULT_TOKEN" vault vault "$@"; }

echo "==> Enabling KV v2 at secret/ (ignore if already enabled)"
v secrets enable -path=secret kv-v2 2>/dev/null || true

echo "==> Writing grocery secrets"
v kv put secret/grocery \
  database_url="postgresql://grocery:grocery@db:5432/grocery" \
  db_user="grocery" \
  db_password="grocery" \
  api_key="demo-api-key-123"

echo "==> Verifying"
v kv get secret/grocery

cat <<EOF

Vault seeded. Point the app at it:
  export VAULT_ADDR=http://127.0.0.1:8200
  export VAULT_TOKEN=root
  export VAULT_SECRET_PATH=secret/data/grocery
  uvicorn app.main:app   # logs: "Loaded database_url from Vault"
EOF
