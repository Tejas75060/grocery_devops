# Step 5 — Kubernetes (local kind cluster)

Manifests in `k8s/` deploy the full app to a **local kind cluster** — no EKS.

| File | Resource |
|------|----------|
| `00-namespace.yaml` | `grocery` namespace |
| `01-configmap.yaml` | non-secret config (app name, DB host/port/name) |
| `02-secret.yaml` | DB creds + `DATABASE_URL` (Vault replaces this in Step 7) |
| `03-postgres.yaml` | Postgres StatefulSet + headless Service + 1Gi PVC |
| `04-app-deployment.yaml` | app Deployment (2 replicas, probes, Prometheus annotations) |
| `05-app-service.yaml` | ClusterIP Service (:80 → :8000) |
| `06-ingress.yaml` | Ingress via ingress-nginx (`grocery.localhost`) |
| `07-hpa.yaml` | HPA 2→10 replicas on CPU 60% / memory 75% |

## Prerequisites
```bash
brew install kind kubectl    # plus Docker running
```

## One-command bring-up
```bash
make k8s-up          # or: bash k8s/scripts/up.sh
```
The script: builds the image, creates the cluster, loads the image, installs
**ingress-nginx** and **metrics-server**, applies all manifests, and waits for
rollout.

Add to `/etc/hosts`:
```
127.0.0.1 grocery.localhost
```
Open **http://grocery.localhost**.

## Inspect
```bash
kubectl -n grocery get pods,svc,ingress,hpa
kubectl -n grocery logs deploy/grocery-app
kubectl -n grocery describe hpa grocery-app-hpa
```

## Demonstrate autoscaling (HPA)
```bash
# Terminal 1 — watch replicas grow:
kubectl -n grocery get hpa -w
# Terminal 2 — generate load:
bash k8s/scripts/load-test.sh
```
Under load, CPU passes 60% and the HPA scales `grocery-app` up toward 10 pods;
it scales back down after the stabilization window when load stops.

## Tear down
```bash
make k8s-down        # kind delete cluster --name grocery
```

📸 Screenshot targets → `docs/screenshots/05-kubernetes/`:
`kubectl get pods,svc,ingress,hpa`, the dashboard via Ingress, and the HPA
scaling up during the load test.
