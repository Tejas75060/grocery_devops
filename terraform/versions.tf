terraform {
  required_version = ">= 1.5.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }

  # Simple local state backend (no remote/S3). State lives in this directory.
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "docker" {
  # Talks to the local Docker daemon. Override host for Colima/remote if needed.
  host = var.docker_host
}
