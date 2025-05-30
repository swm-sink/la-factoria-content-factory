variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "secret_names" {
  description = "A list of secret names (IDs) to create in Secret Manager."
  type        = list(string)
  default     = []
  # Example: ["APP_API_KEY", "ELEVENLABS_API_KEY", "VERTEX_AI_API_KEY"]
}

variable "secret_replication_policy" {
  description = "Replication policy for the secrets. Defaults to automatic."
  type = object({
    automatic = optional(bool, true)
    user_managed = optional(object({
      replicas = list(object({
        location = string
        # customer_managed_encryption = optional(string)
      }))
    }))
  })
  default = {
    automatic = true
  }
  nullable = false
}

variable "labels" {
  description = "A map of labels to assign to the secrets."
  type        = map(string)
  default     = {}
} 