resource "google_firestore_database" "default" {
  project                         = var.gcp_project_id
  name                            = "(default)" # Firestore in Native mode typically uses "(default)" database ID
  location_id                     = var.location_id
  type                            = var.database_type
  app_engine_integration_mode     = var.app_engine_integration_mode
  point_in_time_recovery_enablement = var.point_in_time_recovery_enablement
  delete_protection_state         = var.delete_protection_state

  # Deletion policy is important. For production, consider "ABANDON" if you want to retain data even if TF destroys the resource definition.
  # "DELETE" will delete the database and its data.
  # deletion_policy = "DELETE" # or "ABANDON"
}

# Note: Firestore indexes are typically managed separately, either via gcloud commands,
# manually in the console, or using google_firestore_index resources if defined explicitly.
# This module focuses on provisioning the database instance itself. 