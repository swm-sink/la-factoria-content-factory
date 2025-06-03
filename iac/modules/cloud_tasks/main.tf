resource "google_cloud_tasks_queue" "default" {
  project  = var.gcp_project_id
  location = var.gcp_location
  name     = var.queue_name
  # description = var.queue_description # Description is not a direct attribute of the resource, often managed via console or API directly if needed beyond name.

  rate_limits {
    max_dispatches_per_second = var.max_dispatches_per_second
    max_concurrent_dispatches = var.max_concurrent_dispatches
  }

  retry_config {
    max_attempts = var.max_attempts
    min_backoff  = var.min_backoff
    max_backoff  = var.max_backoff
    max_doublings = var.max_doublings
    # max_retry_duration - can be set if needed, e.g., "0s" for no limit besides attempts
  }

  # Stackdriver Logging Config (Optional, but useful for debugging)
  # stackdriver_logging_config {
  #   sampling_ratio = 1.0 # Log all task attempts
  # }

  # labels = var.labels # Labels are not directly supported on google_cloud_tasks_queue resource
}
