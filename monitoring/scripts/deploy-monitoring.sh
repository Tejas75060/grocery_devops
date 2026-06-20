#!/usr/bin/env bash
# Deploy Prometheus + Grafana into the 'monitoring' namespace on the local cluster.
set -euo pipefail
cd "$(dirname "$0")/../.."

kubectl apply -f monitoring/grafana/deployment.yaml      # creates namespace too
kubectl apply -f monitoring/prometheus/configmap.yaml
kubectl apply -f monitoring/prometheus/rbac.yaml
kubectl apply -f monitoring/prometheus/deployment.yaml
kubectl apply -f monitoring/grafana/dashboard-configmap.yaml

kubectl -n monitoring rollout status deployment/prometheus --timeout=120s
kubectl -n monitoring rollout status deployment/grafana --timeout=120s

cat <<'EOF'

Monitoring is up. Access via port-forward:
  kubectl -n monitoring port-forward svc/prometheus 9090:9090   # http://localhost:9090
  kubectl -n monitoring port-forward svc/grafana    3000:3000   # http://localhost:3000 (admin/admin)

In Prometheus check Status > Targets: the grocery-app pods should be UP.
In Grafana open the pre-provisioned "Grocery Delivery Platform" dashboard.
EOF
