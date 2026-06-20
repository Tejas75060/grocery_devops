#!/usr/bin/env bash
# Spin up a local kind cluster, load the app image, install ingress-nginx +
# metrics-server, and deploy all grocery manifests.
set -euo pipefail
cd "$(dirname "$0")/../.."

CLUSTER=grocery
IMAGE=grocery-app:local

command -v kind >/dev/null    || { echo "kind not installed: brew install kind"; exit 1; }
command -v kubectl >/dev/null || { echo "kubectl not installed: brew install kubectl"; exit 1; }

echo "==> Building app image"
docker build -t "$IMAGE" .

echo "==> Creating kind cluster '$CLUSTER'"
if ! kind get clusters | grep -q "^${CLUSTER}$"; then
  kind create cluster --name "$CLUSTER" --config k8s/kind-config.yaml
fi

echo "==> Loading image into the cluster"
kind load docker-image "$IMAGE" --name "$CLUSTER"

echo "==> Installing ingress-nginx"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx wait --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller --timeout=180s

echo "==> Installing metrics-server (HPA needs it)"
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
# kind uses self-signed kubelet certs — allow insecure TLS for metrics-server.
kubectl -n kube-system patch deployment metrics-server --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

echo "==> Deploying grocery manifests"
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secret.yaml
kubectl apply -f k8s/03-postgres.yaml
kubectl -n grocery rollout status statefulset/grocery-db --timeout=120s
kubectl apply -f k8s/04-app-deployment.yaml
kubectl apply -f k8s/05-app-service.yaml
kubectl apply -f k8s/06-ingress.yaml
kubectl apply -f k8s/07-hpa.yaml
kubectl -n grocery rollout status deployment/grocery-app --timeout=120s

echo
echo "Done. Add this to /etc/hosts if not present:"
echo "  127.0.0.1 grocery.localhost"
echo "Then open: http://grocery.localhost"
kubectl -n grocery get pods,svc,ingress,hpa
