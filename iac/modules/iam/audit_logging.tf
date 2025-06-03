# Enhanced Audit Logging Configuration for Security Monitoring
# Enables comprehensive logging for sensitive GCP operations

# ====================================
# Project-Wide Audit Configuration
# ====================================

# All Services Audit Configuration (Basic)
resource "google_project_iam_audit_config" "all_services" {
  project = var.gcp_project_id
  service = "allServices"

  audit_log_config {
    log_type = "ADMIN_READ"
  }

  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# ====================================
# AI Platform Enhanced Audit Logging
# ====================================

resource "google_project_iam_audit_config" "aiplatform_audit" {
  project = var.gcp_project_id
  service = "aiplatform.googleapis.com"

  # Admin operations (IAM changes, configuration)
  audit_log_config {
    log_type = "ADMIN_READ"
  }

  # Data access operations (model predictions, endpoint calls)
  audit_log_config {
    log_type = "DATA_READ"
  }

  # Data modification operations (model training, endpoint updates)
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# ====================================
# Secret Manager Audit Logging
# ====================================

resource "google_project_iam_audit_config" "secretmanager_audit" {
  project = var.gcp_project_id
  service = "secretmanager.googleapis.com"

  # Admin operations (secret creation, deletion, IAM changes)
  audit_log_config {
    log_type = "ADMIN_READ"
  }

  # Secret access operations (critical for security)
  audit_log_config {
    log_type = "DATA_READ"
  }

  # Secret modification operations
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# ====================================
# Firestore Audit Logging
# ====================================

resource "google_project_iam_audit_config" "firestore_audit" {
  project = var.gcp_project_id
  service = "datastore.googleapis.com"

  # Admin operations (database configuration, IAM)
  audit_log_config {
    log_type = "ADMIN_READ"
  }

  # Data write operations (document creation, updates)
  audit_log_config {
    log_type = "DATA_WRITE"
  }

  # Note: DATA_READ disabled for Firestore to avoid excessive log volume
  # Enable only if specific compliance requirements mandate it
}

# ====================================
# IAM Audit Logging (Enhanced)
# ====================================

resource "google_project_iam_audit_config" "iam_audit" {
  project = var.gcp_project_id
  service = "iam.googleapis.com"

  # All IAM operations are critical for security
  audit_log_config {
    log_type = "ADMIN_READ"
  }

  audit_log_config {
    log_type = "DATA_READ"
  }

  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# ====================================
# Cloud Run Audit Logging
# ====================================

resource "google_project_iam_audit_config" "cloudrun_audit" {
  project = var.gcp_project_id
  service = "run.googleapis.com"

  # Service configuration and deployment changes
  audit_log_config {
    log_type = "ADMIN_READ"
  }

  audit_log_config {
    log_type = "DATA_WRITE"
  }

  # Service invocation logs (for monitoring access patterns)
  audit_log_config {
    log_type = "DATA_READ"
    exempted_members = [
      # Exempt health checks and internal monitoring to reduce log volume
      "serviceAccount:service-${data.google_project.current.number}@gcp-sa-monitoring-notification.iam.gserviceaccount.com"
    ]
  }
}

# ====================================
# Cloud Tasks Audit Logging
# ====================================

resource "google_project_iam_audit_config" "cloudtasks_audit" {
  project = var.gcp_project_id
  service = "cloudtasks.googleapis.com"

  # Queue configuration changes
  audit_log_config {
    log_type = "ADMIN_READ"
  }

  # Task creation and execution (for job tracking)
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# ====================================
# Resource Manager Audit Logging
# ====================================

resource "google_project_iam_audit_config" "resourcemanager_audit" {
  project = var.gcp_project_id
  service = "cloudresourcemanager.googleapis.com"

  # Project-level changes (critical for security)
  audit_log_config {
    log_type = "ADMIN_READ"
  }

  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# ====================================
# Data Source for Project Information
# ====================================

data "google_project" "current" {
  project_id = var.gcp_project_id
}

# ====================================
# Security Monitoring Log Sink
# ====================================

# Create a dedicated log sink for security events
resource "google_logging_project_sink" "security_audit_sink" {
  name        = "acpf-security-audit-sink"
  description = "Dedicated sink for ACPF security audit logs"

  # Filter for security-relevant events
  filter = <<-EOT
    (
      protoPayload.serviceName="iam.googleapis.com" OR
      protoPayload.serviceName="secretmanager.googleapis.com" OR
      protoPayload.serviceName="aiplatform.googleapis.com" OR
      protoPayload.serviceName="cloudresourcemanager.googleapis.com"
    ) AND (
      protoPayload.methodName=~".*Create.*" OR
      protoPayload.methodName=~".*Delete.*" OR
      protoPayload.methodName=~".*Update.*" OR
      protoPayload.methodName=~".*SetIamPolicy.*" OR
      protoPayload.methodName=~".*GetSecret.*" OR
      protoPayload.methodName=~".*AccessSecretVersion.*"
    )
  EOT

  # Destination can be configured based on requirements
  destination = "logging.googleapis.com/projects/${var.gcp_project_id}/logs/acpf-security-audit"

  # Ensure sink has necessary permissions
  unique_writer_identity = true
}

# ====================================
# Audit Log Retention Policy
# ====================================

# Note: Audit logs are retained according to Cloud Logging retention policies
# For compliance requirements, consider:
# 1. Exporting logs to Cloud Storage for long-term retention
# 2. Setting up log-based metrics for security monitoring
# 3. Creating alerting policies for suspicious activities

# Example log-based metric for failed authentication attempts
resource "google_logging_metric" "failed_auth_attempts" {
  name   = "acpf_failed_auth_attempts"
  filter = <<-EOT
    protoPayload.serviceName="iam.googleapis.com" AND
    protoPayload.authenticationInfo.principalEmail!="" AND
    protoPayload.response.error.code!=0
  EOT

  metric_descriptor {
    metric_kind = "CUMULATIVE"
    value_type  = "INT64"
    display_name = "ACPF Failed Authentication Attempts"
  }

  label_extractors = {
    "principal" = "EXTRACT(protoPayload.authenticationInfo.principalEmail)"
    "error_code" = "EXTRACT(protoPayload.response.error.code)"
  }
}

# Example log-based metric for secret access
resource "google_logging_metric" "secret_access" {
  name   = "acpf_secret_access"
  filter = <<-EOT
    protoPayload.serviceName="secretmanager.googleapis.com" AND
    protoPayload.methodName="google.cloud.secretmanager.v1.SecretManagerService.AccessSecretVersion"
  EOT

  metric_descriptor {
    metric_kind = "CUMULATIVE"
    value_type  = "INT64"
    display_name = "ACPF Secret Access Events"
  }

  label_extractors = {
    "principal" = "EXTRACT(protoPayload.authenticationInfo.principalEmail)"
    "secret_name" = "EXTRACT(protoPayload.resourceName)"
  }
}
