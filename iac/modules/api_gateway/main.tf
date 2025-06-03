# API Definition
resource "google_api_gateway_api" "default" {
  provider = google-beta # API Gateway often requires the beta provider
  project  = var.gcp_project_id
  api_id   = var.api_id
  display_name = var.api_display_name
  labels   = var.labels
}

# API Config Definition
# This uses the content of the OpenAPI spec file.
resource "google_api_gateway_api_config" "default" {
  provider      = google-beta
  project       = var.gcp_project_id
  api           = google_api_gateway_api.default.api_id
  api_config_id = var.api_config_id
  display_name  = var.api_config_display_name
  labels        = var.labels

  openapi_documents {
    document {
      path     = var.openapi_spec_path # e.g., "openapi.yaml"
      contents = base64encode(file(var.openapi_spec_path))
    }
  }

  gateway_config {
    backend_config {
      # This should be the fully qualified name of the Cloud Run service
      google_cloud_run_service = var.cloud_run_service_name
    }
  }
  lifecycle {
    create_before_destroy = true
  }
}

# Gateway Definition
resource "google_api_gateway_gateway" "default" {
  provider      = google-beta
  project       = var.gcp_project_id
  region        = var.gcp_region
  gateway_id    = var.gateway_id
  api_config    = google_api_gateway_api_config.default.id
  display_name  = var.gateway_display_name
  labels        = var.labels
}
