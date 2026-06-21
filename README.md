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
> Colima). Steps 4–5 also need `terraform`, `kind`, and `kubectl`
> (`brew install terraform kind kubectl`).

---

## Running every stack — full guide

Each stack runs independently. Start Docker Desktop first, then pick the stacks
you want. Ports used: app `8000`, Jenkins `8080`, Prometheus `9090`,
Grafana `3000`, Kibana `5601`, Elasticsearch `9200`, Vault `8200`,
K8s Ingress `80`.

### 0. One-time prerequisites
```bash
# macOS (Homebrew). Docker Desktop must be installed & running.
brew install kind kubectl terraform
```

### A. Docker — app + database (frontend is served by the backend)
```bash
docker compose up --build -d     # or: make compose-up
docker compose ps                # db + app, both "healthy"
```
`docker compose up` starts **two** containers together — `grocery-db`
(PostgreSQL) and `grocery-app` (FastAPI backend **+** the dashboard UI). The DB
starts first; the app waits for it via a healthcheck.
- Dashboard + API: **http://localhost:8000**   ·   Swagger: **http://localhost:8000/docs**
- Stop: `docker compose down`  (add `-v` to also wipe the DB volume)

### B. Kubernetes — kind cluster + HPA autoscaling
```bash
make k8s-up        # builds image, creates kind cluster, installs ingress-nginx
                   # + metrics-server, applies all manifests, waits for rollout
echo "127.0.0.1 grocery.localhost" | sudo tee -a /etc/hosts   # one-time
```
- App via Ingress: **http://grocery.localhost**
- Inspect: `kubectl -n grocery get pods,svc,ingress,hpa`
- Demo autoscaling: `bash k8s/scripts/load-test.sh` in one terminal,
  `kubectl -n grocery get hpa -w` in another (watch pods scale 2→10).
- Stop: `make k8s-down`  (`kind delete cluster --name grocery`)

### C. Prometheus + Grafana — metrics (deploy onto the K8s cluster)
> Requires the Kubernetes cluster from step B to be running.
```bash
make monitoring-up        # deploys Prometheus + Grafana into the 'monitoring' ns
# then port-forward to open them in the browser:
kubectl -n monitoring port-forward svc/prometheus 9090:9090   # http://localhost:9090
kubectl -n monitoring port-forward svc/grafana    3000:3000   # http://localhost:3000
```
- Prometheus targets: **http://localhost:9090/targets** (grocery-app pods = UP)
- Grafana: **http://localhost:3000** — login `admin` / `admin`, open the
  pre-provisioned **“Grocery Delivery Platform”** dashboard.

### D. Jenkins — CI/CD pipeline
```bash
bash jenkins/setup-jenkins.sh     # self-configuring controller (no setup wizard)
```
- Jenkins UI: **http://localhost:8080** — login `admin` / `admin`
- The `grocery-ci` job is pre-created. Trigger a build:
  ```bash
  curl -s -XPOST http://admin:admin@localhost:8080/job/grocery-ci/build
  ```
- Pipeline stages: Checkout → Build & Test → Docker Build → Push (local
  registry `:5051`) → Deploy.
- Stop: `docker rm -f jenkins grocery-registry-ci`

### E. ELK — centralized logging
```bash
make elk-up        # Elasticsearch + Logstash + Kibana + Filebeat (docker compose)
```
- Kibana: **http://localhost:5601** → Discover → data view `grocery-logs-*`
- Elasticsearch: **http://localhost:9200**
- Stop: `docker compose -f monitoring/elk/docker-compose.elk.yml down -v`

### F. Vault — secrets
```bash
make vault-up      # dev Vault + seeds secret/grocery
```
- Vault UI: **http://localhost:8200**  (token: `root`)
- Run the app against Vault:
  ```bash
  export VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN=root \
         VAULT_SECRET_PATH=secret/data/grocery
  make run     # startup log: "Loaded database_url from Vault"
  ```
- Stop: `docker rm -f vault`

### Terraform — provision the local stack instead of compose
> Alternative to **A**: provisions network + Postgres + app + a local registry
> via the Docker provider. Stop the compose stack first (same container names).
```bash
docker build -t grocery-app:local .
cd terraform && terraform init && terraform apply -auto-approve
terraform output          # app_url, registry_url, database_container
terraform destroy -auto-approve   # tear down
```

### Tear everything down
```bash
docker compose down -v
docker compose -f monitoring/elk/docker-compose.elk.yml down -v
docker rm -f jenkins grocery-registry-ci vault
cd terraform && terraform destroy -auto-approve; cd ..
make k8s-down
```

> ⚠️ Running **all** stacks at once is memory-heavy (Elasticsearch alone wants
> ~1 GB). On a laptop, give Docker Desktop 6–8 GB, or run stacks a few at a time.

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
