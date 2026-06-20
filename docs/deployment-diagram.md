# Deployment / CI-CD Flow — Grocery Delivery Platform

End-to-end pipeline from source control to the running cluster.
GitHub → Jenkins → Docker → Kubernetes (all self-hosted; no cloud-managed steps).

```mermaid
flowchart LR
  dev([Developer]) -->|git push| gh[(GitHub repo)]
  gh -->|webhook / SCM poll| jenkins["Jenkins\nPipeline"]

  subgraph pipeline["Jenkins stages"]
    direction TB
    s1[Checkout] --> s2[Build venv\n+ deps]
    s2 --> s3[Test\npytest + JUnit]
    s3 --> s4[Docker Build\nimage:sha]
    s4 --> s5[Push to Registry]
    s5 --> s6[Deploy\nkubectl set image]
  end

  jenkins --> pipeline
  s5 -->|docker push| reg[(Container Registry\nlocal registry:2)]
  s6 -->|kubectl rollout| k8s["kind cluster\nns: grocery"]
  reg -->|image pull / kind load| k8s

  k8s --> mon["Prometheus + Grafana"]
  k8s --> logs["ELK (Filebeat→Logstash→ES→Kibana)"]
```

## Flow summary
1. **Developer** pushes code to **GitHub**.
2. **Jenkins** triggers on the change and runs the pipeline.
3. **Checkout → Build → Test** validate the change (`pytest`, JUnit report).
4. **Docker Build** produces an image tagged with the short Git SHA.
5. **Push to Registry** publishes `:sha` and `:latest` to the registry.
6. **Deploy** rolls the image onto the kind cluster via `kubectl set image` and
   waits for `rollout status`.
7. The running app is observed by **Prometheus/Grafana** (metrics) and **ELK** (logs).

## Provisioning path (Terraform)
Infrastructure (network, Postgres, app, local registry) is provisioned with
**Terraform + the local Docker provider** — see `terraform/` and
`docs/04-terraform.md`. Kubernetes objects are applied from `k8s/` (Step 5).
