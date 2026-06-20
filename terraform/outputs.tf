output "app_url" {
  description = "URL of the running grocery app."
  value       = "http://localhost:${var.app_port}"
}

output "registry_url" {
  description = "Local image registry endpoint (Jenkins push target)."
  value       = "localhost:${var.registry_port}"
}

output "database_container" {
  description = "Name of the Postgres container."
  value       = docker_container.db.name
}
