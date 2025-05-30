resource "google_artifact_registry_repository" "default" {
  project       = var.gcp_project_id
  location      = var.gcp_location
  repository_id = var.repository_id
  description   = "Docker repository for AI Content Factory application images"
  format        = "DOCKER"

  docker_config {
    # Immutable tags are recommended for better security and versioning.
    # Vulnerability scanning is typically enabled at the project/organization level
    # or can be configured more specifically if needed (e.g. through gcloud commands or separate resources if available).
    # Setting immutable_tags = true is a good practice that aids scanning policies.
    immutable_tags = true
  }

  # KMS key for encryption (optional, but good practice for production)
  # kms_key_name = "projects/YOUR_PROJECT/locations/YOUR_REGION/keyRings/YOUR_KEYRING/cryptoKeys/YOUR_KEY"

  labels = {
    environment = "shared" # Or tie to a specific environment variable
    app         = "acpf"
  }
} 