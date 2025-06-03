# API Gateway Rate Limiting Configuration
# Production-grade rate limiting for AI Content Factory

resource "google_api_gateway_api_config" "ai_content_factory_config" {
  provider      = google-beta
  api           = google_api_gateway_api.ai_content_factory.api_id
  api_config_id = "acf-config-v1"

  openapi_documents {
    document {
      path     = "openapi.yaml"
      contents = base64encode(templatefile("${path.module}/../../files/openapi_with_rate_limits.yaml", {
        backend_url = var.backend_url
      }))
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "google_api_gateway_gateway" "ai_content_factory_gateway" {
  provider   = google-beta
  api_config = google_api_gateway_api_config.ai_content_factory_config.id
  gateway_id = "acf-gateway-v1"
  region     = var.region

  labels = {
    environment = var.environment
    project     = "ai-content-factory"
    purpose     = "production-api-gateway"
  }
}

# Quota configuration for rate limiting
resource "google_service_usage_consumer_quota_override" "api_quota_per_minute" {
  provider       = google-beta
  project        = var.project_id
  service        = "aiplatform.googleapis.com"
  metric         = "aiplatform.googleapis.com%2Fquota%2Frequests"
  limit          = "%2Fmin%2Fproject"
  override_value = "600"  # 10 requests per minute * 60 users

  force = true
}

resource "google_service_usage_consumer_quota_override" "api_quota_per_day" {
  provider       = google-beta
  project        = var.project_id
  service        = "aiplatform.googleapis.com"
  metric         = "aiplatform.googleapis.com%2Fquota%2Frequests"
  limit          = "%2Fday%2Fproject"
  override_value = "14400"  # 100 requests per hour * 24 hours * 6 for safety

  force = true
}

# Output the gateway URL - handled in outputs.tf
