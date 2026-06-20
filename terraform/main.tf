# Provisions a self-contained local environment with the Docker provider:
#   - a private network
#   - a PostgreSQL container (with a persistent volume)
#   - the grocery app container wired to Postgres
#   - a local OCI registry (push target for the Jenkins pipeline)
# No AWS, no managed services — everything runs on the local Docker daemon.

resource "docker_network" "grocery" {
  name = "grocery-net"
}

resource "docker_volume" "pgdata" {
  name = "grocery-pgdata"
}

# ------------------------------- PostgreSQL ---------------------------------
resource "docker_image" "postgres" {
  name         = "postgres:16-alpine"
  keep_locally = true
}

resource "docker_container" "db" {
  name    = "grocery-db"
  image   = docker_image.postgres.image_id
  restart = "unless-stopped"

  env = [
    "POSTGRES_USER=grocery",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=grocery",
  ]

  networks_advanced {
    name    = docker_network.grocery.name
    aliases = ["db"]
  }

  volumes {
    volume_name    = docker_volume.pgdata.name
    container_path = "/var/lib/postgresql/data"
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U grocery -d grocery"]
    interval = "5s"
    timeout  = "3s"
    retries  = 10
  }
}

# --------------------------------- App --------------------------------------
# Uses a locally-built image (grocery-app:local). Build it before apply.
resource "docker_image" "app" {
  name         = var.app_image
  keep_locally = true
}

resource "docker_container" "app" {
  name    = "grocery-app"
  image   = docker_image.app.image_id
  restart = "unless-stopped"

  env = [
    "ENVIRONMENT=production",
    "DATABASE_URL=postgresql://grocery:${var.postgres_password}@db:5432/grocery",
  ]

  networks_advanced {
    name = docker_network.grocery.name
  }

  ports {
    internal = 8000
    external = var.app_port
  }

  depends_on = [docker_container.db]
}

# ----------------------------- Local registry -------------------------------
resource "docker_image" "registry" {
  name         = "registry:2"
  keep_locally = true
}

resource "docker_container" "registry" {
  name    = "grocery-registry"
  image   = docker_image.registry.image_id
  restart = "unless-stopped"

  ports {
    internal = 5000
    external = var.registry_port
  }

  networks_advanced {
    name = docker_network.grocery.name
  }
}
