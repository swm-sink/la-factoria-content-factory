output "repository_name" {
  description = "The full name of the Artifact Registry repository."
  value       = google_artifact_registry_repository.default.name
}

output "repository_id" {
  description = "The ID of the Artifact Registry repository."
  value       = google_artifact_registry_repository.default.repository_id
}

output "location" {
  description = "The location of the Artifact Registry repository."
  value       = google_artifact_registry_repository.default.location
}

output "repository_url" {
  description = "The URL of the Artifact Registry repository (format: location-docker.pkg.dev/project/repository)."
  # Constructing the URL as per GCP format: https://cloud.google.com/artifact-registry/docs/docker/names
  # Example: us-central1-docker.pkg.dev/my-project/my-repo
  value       = "${google_artifact_registry_repository.default.location}-docker.pkg.dev/${google_artifact_registry_repository.default.project}/${google_artifact_registry_repository.default.repository_id}"
}
