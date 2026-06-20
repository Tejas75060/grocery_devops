# Architecture — Grocery Delivery Platform

Component-level view of the platform: application, database, Kubernetes,
monitoring/logging, and secrets. Everything runs on **local/self-hosted**
infrastructure (Docker + kind) — no AWS managed services.

```mermaid
flowchart TB
  user([User / Browser])

  subgraph cluster["Local Kubernetes cluster (kind)"]
    direction TB
    ingress["Ingress (nginx)\ngrocery.localhost"]

    subgraph ns_grocery["namespace: grocery"]
      svc["Service: grocery-app (ClusterIP :80)"]
      subgraph deploy["Deployment: grocery-app (2..10 pods)"]
        app1["FastAPI pod\n/metrics /health /ready"]
        app2["FastAPI pod"]
      end
      hpa["HPA\nCPU 60% / mem 75%\n2 → 10"]
      cm["ConfigMap\ngrocery-config"]
      sec["Secret\ngrocery-secret"]
      db[("PostgreSQL\nStatefulSet + PVC")]
    end

    subgraph ns_monitoring["namespace: monitoring"]
      prom["Prometheus\n(k8s SD scrape)"]
      graf["Grafana\ndashboards"]
    end

    subgraph ns_vault["namespace: vault"]
      vault["Vault (KV v2)\nDB creds / API keys"]
    end
  end

  subgraph elk["ELK stack (docker-compose)"]
    fb["Filebeat"] --> ls["Logstash"] --> es[("Elasticsearch")] --> kib["Kibana"]
  end

  user --> ingress --> svc --> app1 & app2
  app1 -- SQL --> db
  app2 -- SQL --> db
  hpa -. scales .-> deploy
  cm -. env .-> deploy
  sec -. env .-> deploy
  vault -. secret injection .-> deploy
  prom -- scrape /metrics --> app1 & app2
  graf -- query --> prom
  app1 -- JSON logs (stdout) --> fb
  app2 -- JSON logs (stdout) --> fb
```

## Component responsibilities
| Component | Role |
|-----------|------|
| **FastAPI app** | Orders, inventory, delivery assignment; exposes `/metrics`, `/health`, `/ready` |
| **PostgreSQL** | Durable store for products, orders, deliveries (StatefulSet + PVC) |
| **Ingress (nginx)** | External entrypoint at `grocery.localhost` |
| **HPA** | Horizontal autoscaling 2→10 on CPU/memory for peak demand |
| **ConfigMap / Secret** | Non-secret config / credentials (Vault-backed in prod) |
| **Prometheus** | Scrapes app metrics via Kubernetes service discovery + alert rules |
| **Grafana** | Dashboards for orders, request rate, p95 latency, status codes |
| **ELK** | Centralized structured logs: Filebeat → Logstash → Elasticsearch → Kibana |
| **Vault** | Central secret store for DB creds / API keys, injected at app startup |

## How it addresses the problem statement
- **Order processing delays** → async-capable FastAPI + indexed Postgres + clear
  order state machine.
- **Scaling issues** → Kubernetes HPA scales pods automatically under load.
- **Deployment bottlenecks** → Jenkins CI/CD with automated build/test/deploy and
  Terraform-provisioned, reproducible infra.
- **Poor monitoring** → Prometheus/Grafana metrics + ELK logs + alert rules.
