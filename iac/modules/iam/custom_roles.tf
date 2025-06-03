# Custom IAM Roles for Enhanced Security & Granular Permissions
# Following principle of least privilege with specific permissions for each service

# ====================================
# Custom Role: ACPF Content Generator
# ====================================
resource "google_project_iam_custom_role" "acpf_content_generator" {
  project     = var.gcp_project_id
  role_id     = "acpfContentGenerator"
  title       = "ACPF Content Generation Service"
  description = "Minimal permissions for AI content generation with strict resource access"

  permissions = [
    # Vertex AI - Specific model prediction permissions only
    "aiplatform.endpoints.predict",
    "aiplatform.models.predict",

    # Secret Manager - Read-only access to specific secrets
    "secretmanager.versions.access",

    # Firestore - Minimal document operations
    "datastore.entities.create",
    "datastore.entities.get",
    "datastore.entities.update",
    "datastore.entities.list",

    # Cloud Tasks - Job enqueuing only
    "cloudtasks.tasks.create",

    # Logging - Write application logs
    "logging.logEntries.create",

    # Monitoring - Write custom metrics
    "monitoring.timeSeries.create"
  ]

  stage = "GA"
}

# ====================================
# Custom Role: ACPF Task Processor
# ====================================
resource "google_project_iam_custom_role" "acpf_task_processor" {
  project     = var.gcp_project_id
  role_id     = "acpfTaskProcessor"
  title       = "ACPF Background Task Processor"
  description = "Minimal permissions for processing background content generation tasks"

  permissions = [
    # Cloud Run - Invoke internal services only
    "run.services.invoke",

    # Firestore - Task status updates
    "datastore.entities.get",
    "datastore.entities.update",

    # Secret Manager - Configuration access
    "secretmanager.versions.access",

    # Logging - Task execution logs
    "logging.logEntries.create"
  ]

  stage = "GA"
}

# ====================================
# Custom Role: ACPF Workflow Orchestrator
# ====================================
resource "google_project_iam_custom_role" "acpf_workflow_orchestrator" {
  project     = var.gcp_project_id
  role_id     = "acpfWorkflowOrchestrator"
  title       = "ACPF Workflow Orchestration Service"
  description = "Permissions for orchestrating multi-step content generation workflows"

  permissions = [
    # Workflows - Execute and manage workflows
    "workflows.executions.create",
    "workflows.executions.get",
    "workflows.executions.list",

    # Cloud Run - Invoke workflow steps
    "run.services.invoke",

    # Cloud Tasks - Create job queues
    "cloudtasks.tasks.create",
    "cloudtasks.queues.get",

    # Firestore - Workflow state management
    "datastore.entities.create",
    "datastore.entities.get",
    "datastore.entities.update",
    "datastore.entities.delete",

    # Secret Manager - Workflow configuration
    "secretmanager.versions.access",

    # Logging - Workflow execution logs
    "logging.logEntries.create",

    # Monitoring - Workflow metrics
    "monitoring.timeSeries.create"
  ]

  stage = "GA"
}

# ====================================
# Custom Role: ACPF Security Auditor
# ====================================
resource "google_project_iam_custom_role" "acpf_security_auditor" {
  project     = var.gcp_project_id
  role_id     = "acpfSecurityAuditor"
  title       = "ACPF Security Audit Service"
  description = "Read-only permissions for security monitoring and compliance auditing"

  permissions = [
    # IAM - Read permissions and policy analysis
    "iam.serviceAccounts.get",
    "iam.serviceAccounts.list",
    "iam.roles.get",
    "iam.roles.list",

    # Resource Manager - Project resource access
    "resourcemanager.projects.get",
    "resourcemanager.projects.getIamPolicy",

    # Logging - Read audit logs
    "logging.logEntries.list",
    "logging.logs.list",

    # Monitoring - Read security metrics
    "monitoring.timeSeries.list",
    "monitoring.metricDescriptors.list",

    # Asset Inventory - Resource discovery
    "cloudasset.assets.searchAllResources",
    "cloudasset.assets.searchAllIamPolicies"
  ]

  stage = "GA"
}

# ====================================
# Custom Role Assignments (Future Use)
# ====================================

# Note: These custom roles can be assigned to service accounts in place of
# broader predefined roles for enhanced security. For example:
#
# resource "google_project_iam_member" "cloud_run_content_generator" {
#   project = var.gcp_project_id
#   role    = google_project_iam_custom_role.acpf_content_generator.name
#   member  = "serviceAccount:${google_service_account.cloud_run.email}"
# }

# This provides more granular control than predefined roles like
# roles/aiplatform.user or roles/datastore.user

# ====================================
# Security Validation
# ====================================

# Output custom role names for reference in other modules
output "custom_role_content_generator" {
  description = "Custom role for content generation service"
  value       = google_project_iam_custom_role.acpf_content_generator.name
}

output "custom_role_task_processor" {
  description = "Custom role for task processing service"
  value       = google_project_iam_custom_role.acpf_task_processor.name
}

output "custom_role_workflow_orchestrator" {
  description = "Custom role for workflow orchestration"
  value       = google_project_iam_custom_role.acpf_workflow_orchestrator.name
}

output "custom_role_security_auditor" {
  description = "Custom role for security auditing"
  value       = google_project_iam_custom_role.acpf_security_auditor.name
}
