variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_location" {
  description = "The GCP location for the Artifact Registry repository (e.g., us-central1)."
  type        = string
}

variable "repository_id" {
  description = "The ID of the Artifact Registry repository."
  type        = string
  default     = "acpf-docker-repo" # Default repo ID
} 