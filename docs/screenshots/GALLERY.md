# Evidence Gallery — Grocery Delivery Platform

Screenshots captured from the **live running** stacks on a local Docker Desktop +
kind environment. 24 shots across all 7 stacks.

## 1. Application
| Evidence | Shot |
|----------|------|
| pytest — 6 tests passing | ![](01-app/01-pytest.png) |

## 2. Docker
| Evidence | Shot |
|----------|------|
| Dashboard (served from container, live orders) | ![](02-docker/01-dashboard.png) |
| Swagger / OpenAPI docs | ![](02-docker/02-swagger.png) |
| `docker compose ps` (app + db healthy) | ![](02-docker/03-compose-ps.png) |
| `docker images` | ![](02-docker/04-docker-images.png) |

## 3. Jenkins CI/CD
| Evidence | Shot |
|----------|------|
| Pipeline builds #2/#3 green, 6 tests passing trend | ![](03-jenkins/01-pipeline-stages.png) |
| Console — all stages SUCCESS | ![](03-jenkins/02-console-success.png) |
| Build detail (git revision, tests) | ![](03-jenkins/03-build-graph.png) |
| Jenkins dashboard | ![](03-jenkins/04-dashboard.png) |

## 4. Terraform (local Docker provider)
| Evidence | Shot |
|----------|------|
| `terraform apply` — 8 resources | ![](04-terraform/01-tf-apply.png) |
| `terraform output` | ![](04-terraform/02-tf-output.png) |
| `docker ps` — provisioned containers | ![](04-terraform/03-docker-ps.png) |

## 5. Kubernetes (kind)
| Evidence | Shot |
|----------|------|
| `get pods,svc,ingress,hpa` | ![](05-kubernetes/01-get-all.png) |
| Dashboard via Ingress (grocery.localhost) | ![](05-kubernetes/02-dashboard-ingress.png) |
| HPA autoscaling 2→8 under load (CPU 457%) | ![](05-kubernetes/03-hpa-scaling.png) |
| HPA + pods scaled | ![](05-kubernetes/04-hpa-pods.png) |

## 6. Monitoring & Logging
| Evidence | Shot |
|----------|------|
| Prometheus targets UP | ![](06-monitoring/01-prometheus-targets.png) |
| Prometheus request-rate graph | ![](06-monitoring/02-prometheus-graph.png) |
| Grafana dashboard (live data) | ![](06-monitoring/03-grafana-dashboard.png) |
| Kibana Discover — grocery-logs | ![](06-monitoring/04-kibana-logs.png) |
| Elasticsearch index | ![](06-monitoring/05-es-index.png) |

## 7. Vault
| Evidence | Shot |
|----------|------|
| `vault kv get secret/grocery` | ![](07-vault/01-vault-kv-get.png) |
| App loads DB creds from Vault | ![](07-vault/02-app-vault-override.png) |
| Vault UI | ![](07-vault/03-vault-ui.png) |
