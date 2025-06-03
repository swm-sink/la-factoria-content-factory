provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "firestore.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudtasks.googleapis.com",
    "aiplatform.googleapis.com"
  ])

  project = var.gcp_project_id
  service = each.value

  disable_on_destroy = false
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "ai-content-factory-run"
  display_name = "AI Content Factory Cloud Run Service Account"
  description  = "Service account for AI Content Factory Cloud Run service"
}

# IAM bindings for the service account
resource "google_project_iam_member" "cloud_run_sa_firestore" {
  project = var.gcp_project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_secret_manager" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_vertex_ai" {
  project = var.gcp_project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_cloud_tasks" {
  project = var.gcp_project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Firestore Database
resource "google_firestore_database" "default" {
  project     = var.gcp_project_id
  name        = "(default)"
  location_id = var.gcp_region
  type        = "FIRESTORE_NATIVE"
}

# Cloud Tasks Queue
resource "google_cloud_tasks_queue" "content_generation" {
  name     = "ai-content-factory-queue"
  location = var.gcp_region
  project  = var.gcp_project_id

  rate_limits {
    max_dispatches_per_second = 10
  }

  retry_config {
    max_attempts       = 3
    max_retry_duration = "300s"
    max_backoff        = "60s"
    min_backoff        = "5s"
    max_doublings      = 5
  }
}

# Build and deploy the Cloud Run service
resource "google_cloud_run_v2_service" "ai_content_factory" {
  name     = "ai-content-factory"
  location = var.gcp_region
  project  = var.gcp_project_id

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = "gcr.io/${var.gcp_project_id}/ai-content-factory:${var.image_tag}"

      ports {
        container_port = 8080
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.gcp_project_id
      }

      env {
        name  = "GCP_LOCATION"
        value = var.gcp_region
      }

      env {
        name  = "GCP_JOB_QUEUE_NAME"
        value = google_cloud_tasks_queue.content_generation.name
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      # Secret environment variables
      env {
        name = "API_KEY"
        value_source {
          secret_key_ref {
            secret  = "AI_CONTENT_FACTORY_API_KEY"
            version = "latest"
          }
        }
      }

      env {
        name = "ELEVENLABS_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "AI_CONTENT_FACTORY_ELEVENLABS_KEY"
            version = "latest"
          }
        }
      }

      env {
        name = "JWT_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = "AI_CONTENT_FACTORY_JWT_SECRET_KEY"
            version = "latest"
          }
        }
      }

      env {
        name = "SENTRY_DSN"
        value_source {
          secret_key_ref {
            secret  = "AI_CONTENT_FACTORY_SENTRY_DSN"
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "2Gi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [
    google_project_service.required_apis,
    google_firestore_database.default,
    google_cloud_tasks_queue.content_generation
  ]
}

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.ai_content_factory.location
  project  = google_cloud_run_v2_service.ai_content_factory.project
  service  = google_cloud_run_v2_service.ai_content_factory.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
