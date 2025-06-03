# Outputs for the simplified AI Content Factory deployment

output "cloud_run_service_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.ai_content_factory.uri
}

output "cloud_run_service_name" {
  description = "The name of the Cloud Run service"
  value       = google_cloud_run_v2_service.ai_content_factory.name
}

output "cloud_run_service_account_email" {
  description = "The email of the Cloud Run service account"
  value       = google_service_account.cloud_run_sa.email
}

output "cloud_tasks_queue_name" {
  description = "The name of the Cloud Tasks queue"
  value       = google_cloud_tasks_queue.content_generation.name
}

output "firestore_database_name" {
  description = "The name of the Firestore database"
  value       = google_firestore_database.default.name
}

output "gcp_project_id" {
  description = "The GCP project ID"
  value       = var.gcp_project_id
}

output "gcp_region" {
  description = "The GCP region"
  value       = var.gcp_region
}
