output "cloud_run_service_account_email" {
  description = "The email address of the Cloud Run service account."
  value       = google_service_account.cloud_run.email
}

output "cloud_tasks_invoker_service_account_email" {
  description = "The email address of the Cloud Tasks invoker service account."
  value       = google_service_account.cloud_tasks_invoker.email
}

output "workflows_executor_service_account_email" {
  description = "The email address of the Workflows executor service account."
  value       = google_service_account.workflows_executor.email
} 