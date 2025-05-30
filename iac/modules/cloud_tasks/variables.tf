variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_location" {
  description = "The GCP location for the Cloud Tasks queue (e.g., us-central1)."
  type        = string
}

variable "queue_name" {
  description = "The name of the Cloud Tasks queue."
  type        = string
  default     = "acpf-job-queue" # Default queue name
}

variable "queue_description" {
  description = "A description for the Cloud Tasks queue."
  type        = string
  default     = "Queue for AI Content Factory background jobs"
}

# Rate limits configuration
variable "max_dispatches_per_second" {
  description = "The maximum rate at which tasks are dispatched from this queue. Must be > 0."
  type        = number
  default     = 500 # Default, adjust as needed
}

variable "max_concurrent_dispatches" {
  description = "The maximum number of concurrent tasks that Cloud Tasks allows to be dispatched for this queue. Must be > 0."
  type        = number
  default     = 1000 # Default, adjust as needed
}

# Retry configuration
variable "max_attempts" {
  description = "The maximum number of attempts for a task. Set to -1 for unlimited retries (not recommended for all cases)."
  type        = number
  default     = 3 # Default to 3 attempts
}

variable "min_backoff" {
  description = "The minimum amount of time to wait before retrying a task after it fails (e.g., \"5s\")."
  type        = string
  default     = "5s"
}

variable "max_backoff" {
  description = "The maximum amount of time to wait before retrying a task after it fails (e.g., \"3600s\")."
  type        = string
  default     = "3600s"
}

variable "max_doublings" {
  description = "The max number of times that the interval between failed task retries will be doubled before the increase becomes linear."
  type        = number
  default     = 16
}

variable "labels" {
  description = "A map of labels to assign to the Cloud Tasks queue."
  type        = map(string)
  default     = {}
} 