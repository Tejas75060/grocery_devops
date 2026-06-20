.PHONY: help install test run docker-build compose-up compose-down \
        tf-init tf-apply tf-destroy k8s-up k8s-down monitoring-up elk-up vault-up

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  %-16s %s\n", $$1, $$2}'

install:  ## Create venv and install Python deps
	python3 -m venv .venv && . .venv/bin/activate && \
	  pip install -U pip && pip install -r app/requirements.txt

test:  ## Run the pytest suite
	. .venv/bin/activate && pytest -q

run:  ## Run the app locally with reload (SQLite)
	. .venv/bin/activate && uvicorn app.main:app --reload

docker-build:  ## Build the backend image
	docker build -t grocery-app:local .

compose-up:  ## Run app + Postgres locally
	docker compose up --build -d

compose-down:  ## Stop the local stack
	docker compose down -v

tf-init:  ## Initialise Terraform (local Docker provider)
	cd terraform && terraform init

tf-apply:  ## Provision local infra with Terraform
	cd terraform && terraform apply -auto-approve

tf-destroy:  ## Tear down Terraform-provisioned infra
	cd terraform && terraform destroy -auto-approve

k8s-up:  ## Create kind cluster + deploy app
	bash k8s/scripts/up.sh

k8s-down:  ## Delete the kind cluster
	kind delete cluster --name grocery

monitoring-up:  ## Deploy Prometheus + Grafana to the cluster
	bash monitoring/scripts/deploy-monitoring.sh

elk-up:  ## Start the ELK logging stack via docker compose
	docker compose -f monitoring/elk/docker-compose.elk.yml up -d

vault-up:  ## Start dev Vault and seed secrets
	bash vault/scripts/setup-vault.sh
