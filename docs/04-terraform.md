# Step 4 — Infrastructure as Code (Terraform, local Docker provider)

Provisions the whole local environment with the **`kreuzwerker/docker`**
provider — **no AWS, no managed services**. State uses the **local backend**
(`terraform.tfstate` in this folder).

## What it creates
- `grocery-net` — a private Docker network
- `grocery-db` — PostgreSQL 16 with a persistent volume + healthcheck
- `grocery-app` — the backend, wired to Postgres, exposed on `:8000`
- `grocery-registry` — a local OCI registry on `:5000` (Jenkins push target)

## Prerequisites
- Docker running (Docker Desktop or Colima)
- Terraform ≥ 1.5 (`brew install terraform`)
- App image built locally first:
  ```bash
  docker build -t grocery-app:local .
  ```

## Usage
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # adjust if using Colima
terraform init
terraform plan
terraform apply -auto-approve
terraform output            # app_url, registry_url, database_container
```
Then open the printed `app_url` (http://localhost:8000).

## Tear down
```bash
terraform destroy -auto-approve
```

## Notes
- For **Colima**, set `docker_host` in `terraform.tfvars` to the Colima socket
  (see the example file).
- State is local and git-ignored. For team use you could later switch the
  `backend "local"` block to a remote backend — kept simple here on purpose.

📸 Screenshot targets → `docs/screenshots/04-terraform/`: `terraform apply`
summary, `terraform output`, and `docker ps` showing the three containers.
