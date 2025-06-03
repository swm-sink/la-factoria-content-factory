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

variable "repository_description" {
  description = "The description of the Artifact Registry repository."
  type        = string
  default     = "Docker repository for ACPF application"
}

variable "labels" {
  description = "A map of labels to assign to the Artifact Registry repository."
  type        = map(string)
  default     = {}
}
