# Step 2 — Containerization

## Files
- `Dockerfile` — multi-stage build (wheels builder → slim runtime), non-root
  user, healthcheck, runs uvicorn on port 8000.
- `.dockerignore` — keeps the build context small (no venv, infra, docs).
- `docker-compose.yml` — runs the **app + PostgreSQL** together locally.

## Prerequisites
Docker is **not installed** on this machine. Install one of:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS/Windows), or
- [Colima](https://github.com/abiosoft/colima) (`brew install colima docker docker-compose && colima start`)

Verify: `docker version` and `docker compose version`.

## Build & run the image alone
```bash
docker build -t grocery-app:local .
docker run --rm -p 8000:8000 grocery-app:local
# SQLite inside the container; open http://localhost:8000
```

## Run app + Postgres together
```bash
docker compose up --build -d     # or: make compose-up
docker compose ps                # all services healthy
curl localhost:8000/health
open http://localhost:8000       # dashboard
docker compose logs -f app
docker compose down -v           # stop + remove volumes
```

The app connects to Postgres via
`DATABASE_URL=postgresql://grocery:grocery@db:5432/grocery`, set in compose.
`depends_on` + Postgres healthcheck ensure the DB is ready before the app starts.

## Verify
```bash
curl -s localhost:8000/api/inventory | head
curl -s -X POST localhost:8000/api/orders \
  -H 'Content-Type: application/json' \
  -d '{"customer_name":"Docker","address":"1 Wharf","items":[{"sku":"MILK-1L","quantity":2}]}'
```

📸 Screenshot targets → `docs/screenshots/02-docker/`: `docker compose ps`,
dashboard served from the container, `docker images` showing `grocery-app`.
