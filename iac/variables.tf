# Terraform Root Variables
# ------------------------------------------------------------------------------
# These variables are used by the root Terraform configuration (main.tf)
# and are passed down to the various modules.
# ------------------------------------------------------------------------------

variable "gcp_project_id" {
  description = "The GCP project ID to deploy resources into."
  type        = string
  # No default, should be provided at runtime (e.g., via CI/CD secrets or tfvars)
}

variable "gcp_region" {
  description = "The GCP region to deploy resources into (e.g., us-central1)."
  type        = string
  default     = "us-central1"
}

variable "app_name" {
  description = "Base name for application resources."
  type        = string
  default     = "acpf-mvp" # AI Content Podcast Factory - MVP
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "image_tag" {
  description = "Docker image tag to deploy (e.g., git SHA or 'latest')."
  type        = string
  default     = "latest" # Default to latest, but CI should pass specific tag (e.g., GITHUB_SHA)
}

variable "storage_bucket_name" {
  description = "Name of the GCS bucket for storing application files (e.g., audio outputs)."
  type        = string
  # No default, must be provided as it's environment/project specific.
}
