variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region for resources (e.g., us-central1)."
  type        = string
}

variable "cloud_run_sa_name" {
  description = "The name of the service account for Cloud Run."
  type        = string
  default     = "acpf-cloud-run-sa"
}

variable "cloud_tasks_invoker_sa_name" {
  description = "The name of the service account for Cloud Tasks to invoke Cloud Run."
  type        = string
  default     = "acpf-tasks-invoker-sa"
}

variable "workflows_executor_sa_name" {
  description = "The name of the service account for Cloud Workflows execution."
  type        = string
  default     = "acpf-workflows-executor-sa"
}

variable "custom_roles" {
  description = "A map of custom roles to be created or used."
  type        = map(string)
  default     = {}
}

variable "labels" {
  description = "A map of labels to assign to all service accounts."
  type        = map(string)
  default     = {}
}
