# Step 7 — Secrets with HashiCorp Vault

DB credentials and API keys are managed in **Vault** instead of being baked into
images or committed YAML. The app integrates natively: when `VAULT_ADDR` and
`VAULT_TOKEN` are set, `app/config.py` calls `app/vault_client.py` to read
`secret/data/grocery` and overrides `DATABASE_URL` at startup.

```
Vault (KV v2)  ──read──►  app/config.py  ──►  DATABASE_URL used by SQLAlchemy
secret/grocery: { database_url, db_user, db_password, api_key }
```

## A. Local (docker-compose)
```bash
make vault-up        # or: bash vault/scripts/setup-vault.sh
```
This starts dev Vault (root token `root`) and seeds `secret/grocery`. Then run
the app against it:
```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root
export VAULT_SECRET_PATH=secret/data/grocery
source .venv/bin/activate && uvicorn app.main:app
# startup log shows: "Loaded database_url from Vault"
```
Vault UI: http://localhost:8200 (token `root`).

## B. Kubernetes
```bash
# 1) Deploy dev Vault in-cluster
kubectl apply -f vault/k8s/vault-dev.yaml
kubectl -n vault rollout status deploy/vault

# 2) Seed the secret
kubectl -n vault exec deploy/vault -- sh -c '
  export VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN=root
  vault kv put secret/grocery \
    database_url="postgresql://grocery:grocery@grocery-db.grocery.svc.cluster.local:5432/grocery" \
    api_key="demo-api-key-123"'

# 3) Give the app a Vault token, then enable Vault injection
kubectl -n grocery create secret generic vault-token --from-literal=token=root
kubectl apply -f vault/k8s/app-with-vault.yaml
kubectl -n grocery rollout status deploy/grocery-app
kubectl -n grocery logs deploy/grocery-app | grep -i vault
```

## Security notes (dev vs prod)
- **Dev mode** is in-memory, auto-unsealed, single root token — for learning only.
- **Production** hardening (out of scope, documented for completeness):
  - Run Vault with an HA storage backend (Raft/Integrated Storage) and TLS.
  - Replace the static token with **Kubernetes auth** + short-lived tokens, or
    the **Vault Agent Injector** (sidecar) to render secrets to a file/env.
  - Use **dynamic database secrets** so Vault issues per-pod Postgres creds with
    a TTL instead of a static password.

📸 Screenshot targets → `docs/screenshots/07-vault/`: `vault kv get secret/grocery`,
the Vault UI, and app logs showing "Loaded database_url from Vault".
