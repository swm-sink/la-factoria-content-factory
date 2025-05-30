provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# ------------------------------------------------------------------------------
# Core Infrastructure Modules
# ------------------------------------------------------------------------------

module "artifact_registry" {
  source = "./modules/artifact_registry"

  gcp_project_id = var.gcp_project_id
  gcp_location   = var.gcp_region
  repository_id  = "${var.app_name}-images" # Example naming
  description    = "Docker container registry for ${var.app_name} application."
  labels         = {
    environment = var.environment
    app         = var.app_name
  }
}

module "secret_manager" {
  source = "./modules/secret_manager"

  gcp_project_id = var.gcp_project_id
  gcp_region     = var.gcp_region # Used for replication policy if not auto
  secret_names   = [ # These should align with GSM_*_NAME constants in settings.py
    "AI_CONTENT_FACTORY_API_KEY",
    "AI_CONTENT_FACTORY_ELEVENLABS_KEY",
    "AI_CONTENT_FACTORY_JWT_SECRET_KEY",
    "AI_CONTENT_FACTORY_SENTRY_DSN"
    # Add other secrets as needed
  ]
  labels         = {
    environment = var.environment
    app         = var.app_name
  }
}

module "firestore" {
  source = "./modules/firestore"

  gcp_project_id = var.gcp_project_id
  location_id    = var.gcp_region # Or a specific Firestore region like "nam5"
  database_type  = "NATIVE"       # Or "DATASTORE_MODE"
  labels         = {
    environment = var.environment
    app         = var.app_name
  }
}

module "cloud_tasks" {
  source = "./modules/cloud_tasks"

  gcp_project_id = var.gcp_project_id
  location       = var.gcp_region
  queue_name     = "${var.app_name}-content-generation-${var.environment}"
  description    = "Cloud Tasks queue for ${var.app_name} content generation jobs."
  labels         = {
    environment = var.environment
    app         = var.app_name
  }
  # Default retry and rate limits are in the module, override here if needed
}

module "cloud_run_service" {
  source = "./modules/cloud_run_service"

  gcp_project_id      = var.gcp_project_id
  gcp_location        = var.gcp_region
  service_name        = "${var.app_name}-api-${var.environment}"
  container_image     = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${module.artifact_registry.repository_id}/${var.app_name}:${var.image_tag}" # Using var.image_tag
  container_port      = 8080 # Nginx listens on this port (NGINX_PORT in start.sh defaults to PORT or 8080)
  service_account_email = module.iam.cloud_run_sa_email
  
  env_vars = [
    { name = "APP_PORT_UVICORN", value = "8000" }, # Uvicorn's internal port, Nginx proxies to this
    { name = "GCP_PROJECT_ID", value = var.gcp_project_id },
    { name = "GCP_LOCATION", value = var.gcp_region }, # Added GCP_LOCATION for consistency if needed by app
    { name = "GCP_QUEUE_LOCATION", value = var.gcp_region },
    { name = "GCP_JOB_QUEUE_NAME", value = module.cloud_tasks.queue_name },
    { name = "GCP_JOB_WORKER_ENDPOINT", value = "${module.cloud_run_service.service_url}/internal/v1/process-generation-task" }, # Dynamically set worker endpoint
    { name = "GCP_JOB_WORKER_SA_EMAIL", value = module.iam.cloud_tasks_invoker_sa_email },
    { name = "STORAGE_BUCKET", value = var.storage_bucket_name } # Added STORAGE_BUCKET
  ]

  secret_env_vars = [
    { name = "API_KEY", secret_name = module.secret_manager.secret_ids_map["AI_CONTENT_FACTORY_API_KEY"], secret_version = "latest" },
    { name = "ELEVENLABS_API_KEY", secret_name = module.secret_manager.secret_ids_map["AI_CONTENT_FACTORY_ELEVENLABS_KEY"], secret_version = "latest" },
    { name = "JWT_SECRET_KEY", secret_name = module.secret_manager.secret_ids_map["AI_CONTENT_FACTORY_JWT_SECRET_KEY"], secret_version = "latest" },
    { name = "SENTRY_DSN", secret_name = module.secret_manager.secret_ids_map["AI_CONTENT_FACTORY_SENTRY_DSN"], secret_version = "latest" }
  ]

  min_instances = (var.environment == "prod" ? 1 : 0)
  max_instances = (var.environment == "prod" ? 10 : 2)
  
  labels = {
    environment = var.environment
    app         = var.app_name
  }
  # Depends on Artifact Registry for image and IAM for service account
  depends_on = [module.artifact_registry, module.iam]
}

module "api_gateway" {
  source = "./modules/api_gateway"

  gcp_project_id   = var.gcp_project_id
  api_id           = "${var.app_name}-api-${var.environment}"
  api_config_id    = "${var.app_name}-api-config-${var.environment}"
  gateway_id       = "${var.app_name}-gw-${var.environment}"
  gateway_region   = var.gcp_region
  openapi_spec_path = "${path.module}/files/openapi.yaml" # Path to your OpenAPI spec
  
  # Pass backend service URL (Cloud Run service URL)
  backend_service_url = module.cloud_run_service.service_url # Pass the Cloud Run service URL
  
  labels = {
    environment = var.environment
    app         = var.app_name
  }
  depends_on = [module.cloud_run_service]
}

module "workflows" {
  source = "./modules/workflows"

  gcp_project_id          = var.gcp_project_id
  region                  = var.gcp_region
  workflow_name           = "${var.app_name}-main-orchestration-${var.environment}"
  description             = "Main orchestration workflow for ${var.app_name}."
  service_account_email = module.iam.workflows_executor_sa_email # Assuming IAM module outputs this
  source_contents_path  = "${path.module}/files/workflow_placeholder.yaml" # Path to your workflow definition
  
  labels = {
    environment = var.environment
    app         = var.app_name
  }
  depends_on = [module.iam]
}

# ------------------------------------------------------------------------------
# IAM Module (Service Accounts and Bindings)
# ------------------------------------------------------------------------------
# Called after other resources that might need SAs or be granted permissions.
module "iam" {
  source = "./modules/iam"

  gcp_project_id = var.gcp_project_id
  gcp_region     = var.gcp_region # Though IAM is mostly global, region might be used for some resource context or naming
  app_name       = var.app_name
  environment    = var.environment
  
  # Pass resource names/IDs that SAs need access to
  # Example:
  # secret_manager_secret_ids = module.secret_manager.secret_ids_map # Assuming module outputs a map
  # cloud_run_service_id    = module.cloud_run_service.service_id
  # firestore_database_name = module.firestore.database_name
  # cloud_tasks_queue_name  = module.cloud_tasks.queue_name
  # workflow_id             = module.workflows.workflow_id

  labels         = {
    environment = var.environment
    app         = var.app_name
  }
}

# Additional global configurations or resources can be defined here if necessary.
# Example: Global network resources, DNS configurations, etc.
