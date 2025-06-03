variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_location" {
  description = "The GCP location for the Cloud Run service (e.g., us-central1)."
  type        = string
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
  default     = "acpf-apiserver"
}

variable "container_image" {
  description = "The full URL of the container image in Artifact Registry (e.g., us-central1-docker.pkg.dev/project/repo/image:tag)."
  type        = string
  # This will typically be supplied by CI/CD pipeline
}

variable "service_account_email" {
  description = "The email of the service account to run the Cloud Run service with."
  type        = string
}

variable "container_port" {
  description = "The port the container listens on (Nginx will listen on this port internally if used)."
  type        = number
  default     = 80 # Nginx listens on 80, Uvicorn on APP_PORT (e.g. 8000) behind it
}

variable "env_vars" {
  description = "A map of environment variables to set for the Cloud Run service."
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "A map of environment variables to be sourced from Secret Manager. Key is env var name, value is secret_name:version."
  type = map(object({
    secret_name = string
    version     = string # e.g., "latest" or specific version number
  }))
  default = {}
  # Example: {
  #   API_KEY = { secret_name = "APP_API_KEY", version = "latest" }
  # }
}


variable "min_instances" {
  description = "Minimum number of instances for the Cloud Run service."
  type        = number
  default     = 0 # Default to 0 for cost savings, scale to 1 for production if needed
}

variable "max_instances" {
  description = "Maximum number of instances for the Cloud Run service."
  type        = number
  default     = 2 # Adjust based on expected load
}

variable "cpu_limit" {
  description = "CPU limit for the Cloud Run service (e.g., 1, 2, \"1000m\")."
  type        = string
  default     = "1"
}

variable "memory_limit" {
  description = "Memory limit for the Cloud Run service (e.g., \"512Mi\", \"1Gi\")."
  type        = string
  default     = "512Mi"
}

variable "concurrency" {
  description = "The maximum number of concurrent requests that can be sent to a container instance."
  type        = number
  default     = 80 # Default value
}

variable "ingress_settings" {
  description = "Ingress settings for the Cloud Run service. Allowed values: INGRESS_TRAFFIC_ALL, INGRESS_TRAFFIC_INTERNAL_ONLY, INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER."
  type        = string
  default     = "INGRESS_TRAFFIC_ALL" # For API Gateway access and direct access if needed
  validation {
    condition     = contains(["INGRESS_TRAFFIC_ALL", "INGRESS_TRAFFIC_INTERNAL_ONLY", "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"], var.ingress_settings)
    error_message = "Invalid ingress_settings value."
  }
}

variable "labels" {
  description = "A map of labels to assign to the Cloud Run service."
  type        = map(string)
  default     = {}
}
