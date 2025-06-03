output "workflow_name" {
  description = "The name of the Cloud Workflow."
  value       = google_workflows_workflow.default.name
}

output "workflow_id" {
  description = "The fully qualified ID of the Cloud Workflow."
  value       = google_workflows_workflow.default.id
}

output "workflow_revision_id" {
  description = "The revision ID of the deployed Cloud Workflow."
  value       = google_workflows_workflow.default.revision_id
}

output "region" {
  description = "The region of the Cloud Workflow."
  value       = google_workflows_workflow.default.region
}
