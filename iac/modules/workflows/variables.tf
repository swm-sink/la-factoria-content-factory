variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region where the Cloud Workflow will be deployed (e.g., us-central1)."
  type        = string
}

variable "workflow_name" {
  description = "The name of the Cloud Workflow."
  type        = string
  default     = "acpf-content-orchestration"
}

variable "workflow_description" {
  description = "A description for the Cloud Workflow."
  type        = string
  default     = "Orchestrates multi-step AI content generation processes."
}

variable "service_account_email" {
  description = "The email of the service account to be used by the Cloud Workflow for its execution and accessing other GCP services."
  type        = string
  # This will be provided by the IAM module or root configuration
}

variable "source_contents_file" {
  description = "Path to the YAML file containing the workflow definition (e.g., iac/files/workflow_definition.yaml)."
  type        = string
  # Example: "../../files/workflow_placeholder.yaml" if file is in root iac/files relative to module path
}

variable "crypto_key_name" {
  description = "Optional. The KMS key used to encrypt workflow and execution data."
  type        = string
  default     = null
}

variable "user_env_vars" {
  description = "User-defined environment variables to be key-value pairs available to the workflow ENV an arg without a value, you must pass \"=\" ex. MYVAR=."
  type        = map(string)
  default     = {}
}

variable "call_log_level" {
  description = "The call log level for the execution. (CALL_LOG_LEVEL_UNSPECIFIED, LOG_ALL_CALLS, LOG_ERRORS_ONLY, LOG_NONE)."
  type        = string
  default     = "LOG_ERRORS_ONLY"
  validation {
    condition     = contains(["CALL_LOG_LEVEL_UNSPECIFIED", "LOG_ALL_CALLS", "LOG_ERRORS_ONLY", "LOG_NONE"], var.call_log_level)
    error_message = "Invalid call_log_level value."
  }
}

variable "labels" {
  description = "A map of labels to assign to the Cloud Workflow."
  type        = map(string)
  default     = {}
}
