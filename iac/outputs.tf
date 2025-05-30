# Terraform Root Outputs
# ------------------------------------------------------------------------------
# This file defines the outputs from the root Terraform configuration.
# These outputs provide important information about the deployed infrastructure.
# ------------------------------------------------------------------------------

output "gcp_project_id" {
  description = "The GCP project ID where resources are deployed."
  value       = var.gcp_project_id
}

output "gcp_region" {
  description = "The GCP region where resources are deployed."
  value       = var.gcp_region
}

output "app_name" {
  description = "The base name used for application resources."
  value       = var.app_name
}

output "environment" {
  description = "The deployment environment."
  value       = var.environment
}

output "artifact_registry_repository_url" {
  description = "The URL of the Artifact Registry repository."
  value       = module.artifact_registry.repository_url
  sensitive   = false # URLs are generally not sensitive
}

output "cloud_run_service_url" {
  description = "The URL of the deployed Cloud Run service."
  value       = module.cloud_run_service.service_url
  sensitive   = false
}

output "cloud_run_service_name" {
  description = "The name of the deployed Cloud Run service."
  value       = module.cloud_run_service.service_name
}

output "cloud_run_service_account_email" {
  description = "The email of the service account used by the Cloud Run service."
  value       = module.iam.cloud_run_sa_email # Assuming this output from iam module
}

output "api_gateway_url" {
  description = "The URL of the deployed API Gateway."
  value       = module.api_gateway.gateway_url # Assuming this output from api_gateway module
  sensitive   = false
}

output "cloud_tasks_queue_name" {
  description = "The name of the Cloud Tasks queue."
  value       = module.cloud_tasks.queue_name
}

output "firestore_database_name" {
  description = "The name of the Firestore database."
  value       = module.firestore.database_name # Assuming this output from firestore module
}

output "workflow_id" {
  description = "The ID of the main Cloud Workflow."
  value       = module.workflows.workflow_id # Assuming this output from workflows module
}

# Example for outputting a map of secret names (keys might differ based on module.secret_manager output structure)
# output "secret_manager_secret_ids" {
#   description = "Map of Secret Manager secret names to their full IDs."
#   value       = module.secret_manager.secret_ids_map 
#   sensitive   = true # Secret IDs can be sensitive
# }
