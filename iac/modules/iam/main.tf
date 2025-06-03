resource "google_service_account" "cloud_run" {
  project      = var.gcp_project_id
  account_id   = var.cloud_run_sa_name
  display_name = "Service Account for ACPF Cloud Run service"
  description  = "Used by the main Cloud Run application service."
  # labels       = var.labels # Labels are not directly supported on google_service_account resource
}

resource "google_service_account" "cloud_tasks_invoker" {
  project      = var.gcp_project_id
  account_id   = var.cloud_tasks_invoker_sa_name
  display_name = "Service Account for Cloud Tasks to invoke Cloud Run"
  description  = "Allows Cloud Tasks to securely invoke the Cloud Run worker endpoint."
  # labels       = var.labels # Labels are not directly supported on google_service_account resource
}

resource "google_service_account" "workflows_executor" {
  project      = var.gcp_project_id
  account_id   = var.workflows_executor_sa_name
  display_name = "Service Account for Cloud Workflows execution"
  description  = "Used by Cloud Workflows to orchestrate tasks and access other GCP services."
  # labels       = var.labels # Labels are not directly supported on google_service_account resource
}

# ====================================
# IAM Bindings for Cloud Run Service Account
# ====================================

# Secret Manager access (read-only for app secrets)
resource "google_project_iam_member" "cloud_run_sa_secret_accessor" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Firestore database access
resource "google_project_iam_member" "cloud_run_sa_firestore_user" {
  project = var.gcp_project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Vertex AI access for content generation (resource-constrained for security)
resource "google_project_iam_member" "cloud_run_sa_vertexai_user" {
  project = var.gcp_project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"

  condition {
    title       = "limit_to_gemini_models"
    description = "Restrict access to Gemini models only for enhanced security"
    expression  = "resource.name.startsWith('projects/${var.gcp_project_id}/locations/${var.gcp_region}/publishers/google/models/gemini')"
  }
}

# Cloud Tasks enqueue permissions (required for API-2.5 job processing)
resource "google_project_iam_member" "cloud_run_sa_tasks_enqueuer" {
  project = var.gcp_project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Logging for application logs
resource "google_project_iam_member" "cloud_run_sa_logging_writer" {
  project = var.gcp_project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Monitoring for metrics (read-only for cost tracking)
resource "google_project_iam_member" "cloud_run_sa_monitoring_metricwriter" {
  project = var.gcp_project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# ====================================
# IAM Bindings for Cloud Tasks Invoker Service Account
# ====================================

# Invoke Cloud Run services (for internal worker endpoints)
resource "google_project_iam_member" "tasks_invoker_sa_run_invoker" {
  project = var.gcp_project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.cloud_tasks_invoker.email}"
}

# ====================================
# IAM Bindings for Workflows Executor Service Account
# ====================================

# Execute workflows
resource "google_project_iam_member" "workflows_executor_sa_workflows_invoker" {
  project = var.gcp_project_id
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${google_service_account.workflows_executor.email}"
}

# Invoke Cloud Run services (for workflow steps)
resource "google_project_iam_member" "workflows_executor_sa_run_invoker" {
  project = var.gcp_project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.workflows_executor.email}"
}

# Secret Manager access (for workflow configurations)
resource "google_project_iam_member" "workflows_executor_sa_secret_accessor" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.workflows_executor.email}"
}

# Enqueue Cloud Tasks (for workflows that create jobs)
resource "google_project_iam_member" "workflows_executor_sa_tasks_enqueuer" {
  project = var.gcp_project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.workflows_executor.email}"
}

# ====================================
# Security Optimizations & Constraints
# ====================================

# Note: For production, consider adding conditional IAM bindings with:
# - Time-based conditions
# - Resource-specific constraints
# - IP address restrictions where appropriate
# These would be implemented using the condition block in google_project_iam_member resources

# Example conditional binding (commented out for MVP):
# resource "google_project_iam_member" "cloud_run_sa_vertexai_user_conditional" {
#   project = var.gcp_project_id
#   role    = "roles/aiplatform.user"
#   member  = "serviceAccount:${google_service_account.cloud_run.email}"
#   condition {
#     title       = "limit_to_business_hours"
#     description = "Only allow AI API calls during business hours"
#     expression  = "request.time.getHours() >= 8 && request.time.getHours() <= 18"
#   }
# }

# Add more IAM bindings as needed for other services (e.g., Cloud Tasks, Pub/Sub, Monitoring)
# Custom roles can be created and assigned here if needed, using var.custom_roles
