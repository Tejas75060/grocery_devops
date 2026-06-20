variable "docker_host" {
  description = "Docker daemon socket. Use the Colima socket if not on Docker Desktop."
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "app_image" {
  description = "Backend image to run (build it first: docker build -t grocery-app:local .)"
  type        = string
  default     = "grocery-app:local"
}

variable "app_port" {
  description = "Host port to expose the app on."
  type        = number
  default     = 8000
}

variable "postgres_password" {
  description = "Password for the Postgres role."
  type        = string
  default     = "grocery"
  sensitive   = true
}

variable "registry_port" {
  description = "Host port for the local image registry."
  type        = number
  default     = 5000
}
