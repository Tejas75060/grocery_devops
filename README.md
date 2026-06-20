# 🛒 Grocery Delivery Platform — DevOps Project

**Industry:** E-Commerce  ·  **Goal:** a production-style DevOps platform for
grocery delivery that fixes order-processing delays, scaling issues, deployment
bottlenecks, and weak observability during peak demand.

Everything runs on **local / self-hosted** infrastructure — Docker, kind,
Terraform (local Docker provider), Vault. **No AWS / cloud-managed services.**

---

## Stack at a glance
| Layer | Technology |
|-------|-----------|
| Application | FastAPI (Python), SQLAlchemy |
| Database | PostgreSQL (SQLite for zero-infra dev) |
| Containerization | Docker (multi-stage), docker-compose |
| CI/CD | Jenkins (declarative pipeline) |
| IaC | Terraform + local Docker provider |
| Orchestration | Kubernetes on **kind**, HPA autoscaling |
| Monitoring | Prometheus + Grafana |
| Logging | ELK (Elasticsearch, Logstash, Kibana) + Filebeat |
| Secrets | HashiCorp Vault |

## Architecture & diagrams
- [Architecture diagram](docs/architecture.md) (component-level, Mermaid)
- [Deployment / CI-CD flow](docs/deployment-diagram.md) (GitHub→Jenkins→Docker→K8s)
- [Disaster Recovery plan](docs/disaster-recovery.md) (backup, restore, RTO/RPO)

---

## Repository layout
```
.
├── app/                  # FastAPI application (Step 1)
│   ├── main.py           # endpoints: orders, inventory, delivery, metrics
│   ├── models.py crud.py schemas.py database.py
│   ├── config.py vault_client.py   # Vault-backed config (Step 7)
│   └── static/index.html # dashboard
├── tests/                # pytest suite
├── Dockerfile            # multi-stage image (Step 2)
├── docker-compose.yml    # app + Postgres (Step 2)
├── Jenkinsfile           # CI/CD pipeline (Step 3)
├── terraform/            # local Docker provider IaC (Step 4)
├── k8s/                  # manifests + HPA + kind setup (Step 5)
├── monitoring/           # prometheus/ grafana/ elk/ (Step 6)
├── vault/                # Vault compose/k8s + setup (Step 7)
├── docs/                 # diagrams, DR plan, per-step guides, screenshots
└── Makefile              # shortcuts for every stack
```

---

## Quick start

### 1. Run the app locally (no Docker needed)
```bash
make install          # python venv + deps
make test             # pytest (6 tests)
make run              # uvicorn -> http://localhost:8000  (dashboard + /docs)
```

### 2. Run app + Postgres in containers
```bash
make compose-up       # http://localhost:8000
make compose-down
```

### 3. Provision local infra with Terraform
```bash
docker build -t grocery-app:local .
cd terraform && terraform init && terraform apply -auto-approve
```

### 4. Deploy to Kubernetes (kind) + autoscaling
```bash
make k8s-up           # build, create cluster, ingress, metrics-server, deploy
# add "127.0.0.1 grocery.localhost" to /etc/hosts -> http://grocery.localhost
bash k8s/scripts/load-test.sh   # watch HPA scale: kubectl -n grocery get hpa -w
```

### 5. Monitoring & logging
```bash
make monitoring-up    # Prometheus + Grafana (port-forward to view)
make elk-up           # Elasticsearch + Logstash + Kibana + Filebeat
```

### 6. Secrets with Vault
```bash
make vault-up         # dev Vault + seed secret/grocery
```

> **Prerequisites by stage:** Steps 2–7 require **Docker** (Docker Desktop or
> Colima) — not installed on the build machine. Steps 4–5 also need
> `terraform`, `kind`, and `kubectl` (`brew install terraform kind kubectl`).

---

## API reference
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/inventory` | Inventory check (all products) |
| GET | `/api/inventory/{sku}` | Single product stock |
| POST | `/api/orders` | Place an order (validates + decrements stock) |
| GET | `/api/orders` | List recent orders |
| GET | `/api/orders/{id}` | Track order status |
| POST | `/api/orders/{id}/assign` | Delivery assignment |
| PATCH | `/api/orders/{id}/status` | Advance order lifecycle |
| GET | `/health` `/ready` | Probes |
| GET | `/metrics` | Prometheus metrics |

Order lifecycle: `PLACED → CONFIRMED → ASSIGNED → OUT_FOR_DELIVERY → DELIVERED`
(`CANCELLED` from any pre-delivery state).

Example:
```bash
curl -X POST localhost:8000/api/orders -H 'Content-Type: application/json' \
  -d '{"customer_name":"Jane","address":"12 Market St",
       "items":[{"sku":"MILK-1L","quantity":2},{"sku":"EGGS-12","quantity":1}]}'
```

---

## Per-step documentation
| Step | Doc |
|------|-----|
| 1 — Application | this README + `app/` |
| 2 — Docker | [docs/02-docker.md](docs/02-docker.md) |
| 3 — CI/CD | [docs/03-cicd.md](docs/03-cicd.md) |
| 4 — Terraform | [docs/04-terraform.md](docs/04-terraform.md) |
| 5 — Kubernetes | [docs/05-kubernetes.md](docs/05-kubernetes.md) |
| 6 — Monitoring & Logging | [docs/06-monitoring-logging.md](docs/06-monitoring-logging.md) |
| 7 — Vault | [docs/07-vault.md](docs/07-vault.md) |
| 8 — Diagrams & DR | [architecture](docs/architecture.md) · [deployment](docs/deployment-diagram.md) · [DR](docs/disaster-recovery.md) |

Screenshots for each stack go in [`docs/screenshots/`](docs/screenshots/).

---

## How this solves the problem statement
- **Order processing delays** → FastAPI + indexed Postgres + explicit order state machine.
- **Scaling issues** → Kubernetes HPA scales 2→10 pods automatically under load.
- **Deployment bottlenecks** → Jenkins CI/CD + Terraform reproducible infra.
- **Poor monitoring** → Prometheus/Grafana metrics, ELK logs, alert rules, DR plan.
