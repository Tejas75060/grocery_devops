# Step 3 — CI/CD with Jenkins

`Jenkinsfile` is a declarative pipeline with stages:
**Checkout → Build → Test → Docker Build → Push to Registry → Deploy**.

It is intentionally **generic / self-hosted** — no AWS or cloud-managed steps.
Any OCI registry works (Docker Hub, Harbor, GitLab Container Registry, or a
local `registry:2`).

## Pipeline stages
| Stage | What it does |
|-------|--------------|
| Checkout | `checkout scm`, records short SHA used as the image tag |
| Build | Creates a venv and installs `app/requirements.txt` |
| Test | Runs `pytest`, publishes JUnit results to Jenkins |
| Docker Build | Builds `${REGISTRY}/${IMAGE_NAME}:<sha>` and `:latest` |
| Push to Registry | `docker login` with credentials, pushes both tags |
| Deploy | `kubectl set image` + `rollout status` on the local cluster |

## Required Jenkins setup
1. **Plugins:** Pipeline, Git, Docker Pipeline, Credentials Binding, JUnit.
2. **Agent:** must have `python3`, `docker`, and `kubectl` available.
3. **Credentials:**
   - `registry-credentials` — *Username with password* for your registry.
   - `kubeconfig` — *Secret file* containing the kubeconfig for the kind/minikube cluster.
4. **Job:** create a *Multibranch Pipeline* or *Pipeline from SCM* pointing at
   this repo; Jenkins auto-discovers the `Jenkinsfile`.

## Configurable env (set as job/global env or pipeline parameters)
| Variable | Default | Purpose |
|----------|---------|---------|
| `REGISTRY` | `localhost:5000` | Registry host[:port] |
| `IMAGE_NAME` | `grocery-app` | Image repository name |

## Run a local registry for testing the push stage
```bash
docker run -d -p 5000:5000 --name registry registry:2
```

## Quick local Jenkins (optional)
```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
# unlock with: docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## Self-configuring demo (used for the screenshots)
`jenkins/setup-jenkins.sh` runs a controller that needs **no setup wizard** — it
applies `jenkins/casc.yaml` (Configuration-as-Code), installs the required
plugins + build tools, starts a local registry on `:5051`, and pre-creates the
`grocery-ci` pipeline (`jenkins/pipeline.groovy`).

```bash
bash jenkins/setup-jenkins.sh          # http://localhost:8080  (admin/admin)
# trigger a build:
curl -s -XPOST http://admin:admin@localhost:8080/job/grocery-ci/build
```

The demo pipeline runs **Build & Test inside a `python:3.11` container** (sharing
the workspace via `--volumes-from jenkins`) so dependency wheels resolve cleanly
regardless of the controller's Python version. Stages: **Checkout → Build & Test
→ Docker Build → Push to Registry (:5051) → Deploy**. Verified green: 6 tests
pass and the image is pushed to the local registry (tags `<build#>` + `latest`).
The Deploy stage is an echo in the demo; the production `Jenkinsfile` does a real
`kubectl set image` rollout given a kubeconfig credential.

📸 Evidence in `docs/screenshots/03-jenkins/`: pipeline #2/#3 green, console with
all stages SUCCESS, build detail (git revision + tests), dashboard.

📸 Screenshot targets → `docs/screenshots/03-jenkins/`: the pipeline stage view
with all stages green, and the JUnit test trend.
