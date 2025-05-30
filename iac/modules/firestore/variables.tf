variable "gcp_project_id" {
  description = "The GCP project ID where the Firestore database will be created."
  type        = string
}

variable "location_id" {
  description = "The location of the Cloud Firestore instance. For example, `us-central` or `nam5` (multi-region)."
  type        = string
  default     = "nam5" # Default to multi-region as per common practice
}

variable "database_type" {
  description = "The type of Cloud Firestore database. (NATIVE or DATASTORE_MODE). Default is NATIVE."
  type        = string
  default     = "NATIVE"
  validation {
    condition     = contains(["NATIVE", "DATASTORE_MODE"], var.database_type)
    error_message = "Allowed values for database_type are NATIVE or DATASTORE_MODE."
  }
}

variable "app_engine_integration_mode" {
  description = "The App Engine integration mode to use for this database. (ENABLED or DISABLED). Default is ENABLED for NATIVE mode."
  type        = string
  default     = "ENABLED" # Common default for NATIVE mode if App Engine integration might be used
  validation {
    condition     = contains(["ENABLED", "DISABLED"], var.app_engine_integration_mode)
    error_message = "Allowed values for app_engine_integration_mode are ENABLED or DISABLED."
  }
}

variable "point_in_time_recovery_enablement" {
  description = "Whether to enable Point In Time Recovery (PITR) for this database. (ENABLED or DISABLED). Default is DISABLED."
  type        = string
  default     = "DISABLED" # PITR has cost implications, so default to disabled
  validation {
    condition     = contains(["ENABLED", "DISABLED", "POINT_IN_TIME_RECOVERY_ENABLED", "POINT_IN_TIME_RECOVERY_DISABLED"], var.point_in_time_recovery_enablement)
    error_message = "Allowed values for point_in_time_recovery_enablement are ENABLED or DISABLED (or their longer equivalents)."
  }
}

variable "delete_protection_state" {
  description = "Whether or not to prevent deletion of the instance. (DELETE_PROTECTION_ENABLED or DELETE_PROTECTION_DISABLED). Default is DISABLED."
  type        = string
  default     = "DELETE_PROTECTION_DISABLED"
  validation {
    condition     = contains(["DELETE_PROTECTION_ENABLED", "DELETE_PROTECTION_DISABLED"], var.delete_protection_state)
    error_message = "Allowed values for delete_protection_state are DELETE_PROTECTION_ENABLED or DELETE_PROTECTION_DISABLED."
  }
} 