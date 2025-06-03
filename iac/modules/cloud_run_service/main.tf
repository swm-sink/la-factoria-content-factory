resource "google_cloud_run_v2_service" "default" {
  project  = var.gcp_project_id
  location = var.gcp_location
  name     = var.service_name

  ingress = var.ingress_settings

  template {
    service_account = var.service_account_email
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2" # Use Gen2 for latest features
    max_instance_request_concurrency = var.concurrency
    timeout = "300s" # Default, can be made a variable

    containers {
      image = var.container_image
      ports {
        container_port = var.container_port # Port Nginx listens on (e.g. 80)
      }

      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = var.secret_env_vars
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value.secret_name # This should be the short secret ID/name
              version = env.value.version
            }
          }
        }
      }

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
        # startup_cpu_boost = true # Consider for faster cold starts
      }

      startup_probe {
        initial_delay_seconds = 60 # Give time for app to start
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
        http_get {
          path = "/healthz" # Updated to unauthenticated health check endpoint
          port = google_cloud_run_v2_service.default.template[0].containers[0].ports[0].container_port
        }
      }

      liveness_probe {
        initial_delay_seconds = 120 # After startup probe passes
        timeout_seconds       = 5
        period_seconds        = 20
        failure_threshold     = 3
        http_get {
          path = "/healthz" # Updated to unauthenticated health check endpoint
          port = google_cloud_run_v2_service.default.template[0].containers[0].ports[0].container_port
        }
      }
    }

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # vpc_access { # Configure if VPC connector is needed
    #   connector = "projects/YOUR_PROJECT/locations/YOUR_REGION/connectors/YOUR_CONNECTOR"
    #   egress    = "ALL_TRAFFIC"
    # }
  }

  labels = var.labels

  # Optional: IAM policy to allow unauthenticated invocations if it's a public service
  # (though API Gateway will handle auth for the main API path)
  # If ingress is ALL and you want it truly public (e.g. for a health check not via Gateway)
  # resource "google_cloud_run_v2_service_iam_member" "allow_public" {
  #   project  = google_cloud_run_v2_service.default.project
  #   location = google_cloud_run_v2_service.default.location
  #   name     = google_cloud_run_v2_service.default.name
  #   role     = "roles/run.invoker"
  #   member   = "allUsers"
  # }
}
