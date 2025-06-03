resource "google_secret_manager_secret" "default" {
  for_each  = toset(var.secret_names)
  project   = var.gcp_project_id
  secret_id = each.key

  replication {
    auto {}
  }

  labels = var.labels
}
