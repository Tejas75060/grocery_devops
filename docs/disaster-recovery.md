# Disaster Recovery Plan — Grocery Delivery Platform

Scope: the self-hosted stack (kind cluster, PostgreSQL, Vault, monitoring/logging).
This plan covers backup strategy, restore procedures, and RTO/RPO assumptions.

## 1. RTO / RPO objectives
| Tier | Component | RPO (max data loss) | RTO (max downtime) |
|------|-----------|---------------------|--------------------|
| 1 | PostgreSQL (orders, inventory) | **15 min** (WAL/periodic dump) | **30 min** |
| 2 | Application (stateless pods) | 0 (rebuilt from image) | **10 min** |
| 2 | Kubernetes cluster (kind) | N/A (declarative manifests) | **30 min** |
| 3 | Vault (secrets) | depends on backend; dev = re-seed | **20 min** |
| 3 | Monitoring/logging data | **24 h** (best-effort) | **1 h** |

Critical path = **PostgreSQL**, since it holds all business state. The app, k8s
objects, and config are reproducible from Git + images, so their "data loss" is
effectively zero.

## 2. What we protect
- **PostgreSQL data** — products, orders, order_items, deliveries.
- **Vault secrets** — DB creds / API keys (prod backend; dev is re-seedable).
- **Declarative config** — all manifests, Terraform, Jenkinsfile (in Git).
- **Container images** — in the registry, tagged by Git SHA (rebuildable).

## 3. Backup strategy
### 3.1 PostgreSQL (primary)
- **Logical backups:** scheduled `pg_dump` every 15 minutes / hourly to an
  off-cluster volume.
  ```bash
  # docker-compose stack
  docker exec grocery-db pg_dump -U grocery grocery | gzip > backups/grocery-$(date +%F-%H%M).sql.gz
  # kubernetes
  kubectl -n grocery exec statefulset/grocery-db -- \
    pg_dump -U grocery grocery | gzip > backups/grocery-$(date +%F-%H%M).sql.gz
  ```
- **Volume snapshots:** snapshot the PVC / `pgdata` volume daily for fast restore.
- **Retention:** 7 daily + 4 weekly copies; verify a restore weekly.
- **Automation:** run as a Kubernetes `CronJob` (manifest sketch in §6).

### 3.2 Vault
- Production: Raft/Integrated Storage **snapshot** (`vault operator raft snapshot save`).
- Dev mode: in-memory — recover by re-running `vault/scripts/setup-vault.sh`.

### 3.3 Config & images
- Git is the source of truth for all manifests/IaC — push to the remote regularly.
- Images are immutable and tagged by SHA; keep the registry backed up or
  rebuildable from Git.

## 4. Restore procedures
### 4.1 Restore PostgreSQL from a dump
```bash
# Recreate an empty DB if needed, then load the latest dump:
gunzip -c backups/grocery-<timestamp>.sql.gz | \
  kubectl -n grocery exec -i statefulset/grocery-db -- psql -U grocery -d grocery
# Verify:
kubectl -n grocery exec statefulset/grocery-db -- \
  psql -U grocery -d grocery -c "select count(*) from orders;"
```

### 4.2 Rebuild the cluster from scratch
```bash
make k8s-up                 # recreate kind cluster + app + db
make monitoring-up          # Prometheus + Grafana
# restore DB (4.1), then re-seed/restore Vault (4.3)
```

### 4.3 Restore Vault
```bash
# Production:
vault operator raft snapshot restore backups/vault-<timestamp>.snap
# Dev:
bash vault/scripts/setup-vault.sh
```

### 4.4 Roll back a bad deploy
```bash
kubectl -n grocery rollout undo deployment/grocery-app
kubectl -n grocery rollout status deployment/grocery-app
```

## 5. Failure scenarios & response
| Scenario | Detection | Response |
|----------|-----------|----------|
| App pod crash-loop | liveness probe / Prometheus `up==0` alert | k8s restarts; `rollout undo` if image-bad |
| DB pod lost, PVC intact | StatefulSet not Ready | reschedule pod; data persists on PVC |
| DB PVC corrupted/lost | failed reads, errors in logs (Kibana) | restore from latest dump (§4.1) — RPO ≤ 15 min |
| Whole cluster lost | nodes down | rebuild via `make k8s-up` (§4.2) + restore DB |
| Secret store down | app fails Vault read | app logs warning, falls back to env `DATABASE_URL` |
| Registry unavailable | deploy pull errors | rebuild image from Git, `kind load` locally |

## 6. Backup CronJob (Kubernetes) — reference
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: pg-backup
  namespace: grocery
spec:
  schedule: "*/15 * * * *"      # every 15 min -> meets 15-min RPO
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: pgdump
              image: postgres:16-alpine
              env:
                - name: PGPASSWORD
                  valueFrom: { secretKeyRef: { name: grocery-secret, key: DB_PASSWORD } }
              command: ["/bin/sh","-c"]
              args:
                - >-
                  pg_dump -h grocery-db -U grocery grocery | gzip >
                  /backups/grocery-$(date +%F-%H%M).sql.gz
              volumeMounts:
                - { name: backups, mountPath: /backups }
          volumes:
            - name: backups
              persistentVolumeClaim: { claimName: pg-backups }
```

## 7. Testing the plan
- **Weekly:** restore the latest dump into a scratch DB and run smoke queries.
- **Monthly:** full game-day — tear down the cluster and rebuild from Git +
  backups, timing against the RTO targets above.
- Track restore time vs. RTO and adjust backup frequency if RPO is missed.
