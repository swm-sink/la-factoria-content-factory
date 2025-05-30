resource "google_workflows_workflow" "default" {
  provider = google-beta # Workflows often requires the beta provider

  project         = var.gcp_project_id
  region          = var.gcp_region
  name            = var.workflow_name
  description     = var.workflow_description
  service_account = var.service_account_email

  source_contents = file(var.source_contents_file)

  user_env_vars = var.user_env_vars
  call_log_level = var.call_log_level
  crypto_key_name = var.crypto_key_name # Can be null

  labels = var.labels

  lifecycle {
    create_before_destroy = true
    # ignore_changes = [source_contents] # Consider if you want to manage source_contents outside of TF apply after initial creation
  }
} 