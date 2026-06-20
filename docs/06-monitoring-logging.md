# Step 6 — Monitoring & Logging

Two parts: **metrics** (Prometheus + Grafana on the cluster) and **logs**
(ELK via docker-compose).

## A. Metrics — Prometheus + Grafana (Kubernetes)
Manifests in `monitoring/prometheus/` and `monitoring/grafana/`.

- Prometheus uses **Kubernetes service discovery** to scrape any pod annotated
  `prometheus.io/scrape: "true"` in the `grocery` namespace — the app
  Deployment already carries those annotations (Step 5).
- Grafana auto-provisions the Prometheus datasource and a
  **"Grocery Delivery Platform"** dashboard (orders, request rate, p95 latency,
  status codes).
- Alert rules: app-down and high p95 latency.

### Deploy
```bash
make monitoring-up          # or: bash monitoring/scripts/deploy-monitoring.sh
```
### Access
```bash
kubectl -n monitoring port-forward svc/prometheus 9090:9090   # http://localhost:9090
kubectl -n monitoring port-forward svc/grafana    3000:3000   # http://localhost:3000
```
Grafana login: `admin` / `admin`. Check Prometheus **Status → Targets** for
`grocery-app` UP. The app exposes metrics at `/metrics`.

## B. Logs — ELK (docker-compose)
`monitoring/elk/docker-compose.elk.yml` runs Elasticsearch + Logstash + Kibana,
with **Filebeat** shipping Docker container logs.

Flow: **container stdout (JSON) → Filebeat → Logstash → Elasticsearch → Kibana**.
The app already emits structured JSON logs (`app/logging_config.py`), so fields
land cleanly in Elasticsearch.

### Run
```bash
make elk-up
# or: docker compose -f monitoring/elk/docker-compose.elk.yml up -d
```
### Access
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601

In Kibana → **Stack Management → Data Views**, create a data view for
`grocery-logs-*`, then explore logs in **Discover**. Filter `service: grocery-app`
to see order/delivery events.

> Note: this ELK compose ships **Docker** container logs (works with the Step 2
> compose stack). For Kubernetes logs, run Filebeat as a DaemonSet — the same
> Logstash pipeline applies.

📸 Screenshot targets → `docs/screenshots/06-monitoring/`: Prometheus targets UP,
the Grafana dashboard with data, and Kibana Discover showing `grocery-logs-*`.
