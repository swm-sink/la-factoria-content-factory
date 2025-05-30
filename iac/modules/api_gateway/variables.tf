variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region where the API Gateway and related resources will be deployed (e.g., us-central1)."
  type        = string
}

variable "api_id" {
  description = "The ID of the API (e.g., acpf-api)."
  type        = string
  default     = "acpf-api"
}

variable "api_display_name" {
  description = "A human-readable name for the API."
  type        = string
  default     = "AI Content Factory API"
}

variable "api_config_id" {
  description = "The ID of the API Config (e.g., acpf-api-config-v1)."
  type        = string
  default     = "acpf-api-config-v1"
}

variable "api_config_display_name" {
  description = "A human-readable name for the API Config."
  type        = string
  default     = "ACPF API Config v1"
}

variable "gateway_id" {
  description = "The ID of the API Gateway (e.g., acpf-gateway)."
  type        = string
  default     = "acpf-gateway"
}

variable "gateway_display_name" {
  description = "A human-readable name for the API Gateway."
  type        = string
  default     = "ACPF API Gateway"
}

variable "openapi_spec_path" {
  description = "Path to the OpenAPI specification file (e.g., iac/files/openapi.yaml)."
  type        = string
  # Default path within the module or relative to root, to be confirmed by usage
}

variable "cloud_run_service_name" {
  description = "The name of the Cloud Run service to target (e.g., projects/PROJECT_ID/locations/REGION/services/SERVICE_NAME)."
  type        = string
  # This should be the fully qualified name or the short name if region/project are implicitly known by the backend config.
}

variable "labels" {
  description = "A map of labels to assign to API Gateway resources."
  type        = map(string)
  default     = {}
} 