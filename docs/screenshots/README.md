# Screenshots — evidence per stack

Capture a screenshot at each stage and drop it in the matching folder so the
project has visual proof every component runs. Suggested shots below.

| # | Folder | What to capture |
|---|--------|-----------------|
| 1 | `01-app/`        | Dashboard at http://localhost:8000, Swagger UI at `/docs`, `pytest` passing |
| 2 | `02-docker/`     | `docker compose ps` all healthy, dashboard served from the container |
| 3 | `03-jenkins/`    | Jenkins pipeline with all stages green |
| 4 | `04-terraform/`  | `terraform apply` output, `docker ps` showing provisioned containers |
| 5 | `05-kubernetes/` | `kubectl get pods,svc,ingress,hpa`, dashboard via Ingress |
| 6 | `06-monitoring/` | Prometheus targets UP, Grafana dashboard, Kibana logs |
| 7 | `07-vault/`      | Vault UI/CLI secret, app logs showing "Loaded database_url from Vault" |

> These folders are placeholders tracked with `.gitkeep`. Replace with real PNGs
> as you run each stage.
