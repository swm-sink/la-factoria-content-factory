# Firestore indexes for optimal query performance
# These indexes are required for the job management queries

resource "google_firestore_index" "jobs_status_created_at" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "jobs"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_firestore_index" "jobs_status_updated_at" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "jobs"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_firestore_index" "jobs_status_only" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "jobs"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Index for content cache entries by key pattern
resource "google_firestore_index" "content_cache_key_expires" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "content_cache"

  fields {
    field_path = "cache_key"
    order      = "ASCENDING"
  }

  fields {
    field_path = "expires_at"
    order      = "ASCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Index for content cache entries by creation time for LRU eviction
resource "google_firestore_index" "content_cache_created_at" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "content_cache"

  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Index for content versions by content type and version
resource "google_firestore_index" "content_versions_type_version" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "content_versions"

  fields {
    field_path = "content_type"
    order      = "ASCENDING"
  }

  fields {
    field_path = "version"
    order      = "DESCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Index for quality metrics by job_id and metric type
resource "google_firestore_index" "quality_metrics_job_type" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "quality_metrics"

  fields {
    field_path = "job_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "metric_type"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Composite index for advanced job queries (status + metadata filters)
resource "google_firestore_index" "jobs_status_format_created" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "jobs"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "metadata.target_format"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Index for job progress tracking
resource "google_firestore_index" "jobs_processing_progress" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "jobs"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "progress.percentage"
    order      = "ASCENDING"
  }

  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# TTL policy for automatic cleanup of expired cache entries
resource "google_firestore_field" "content_cache_ttl" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "content_cache"
  field       = "expires_at"

  ttl_config {}

  lifecycle {
    prevent_destroy = true
  }
}

# TTL policy for automatic cleanup of old completed jobs (30 days)
resource "google_firestore_field" "jobs_ttl" {
  project     = var.gcp_project_id
  database    = "(default)"
  collection  = "jobs"
  field       = "ttl_expires_at"

  ttl_config {}

  lifecycle {
    prevent_destroy = true
  }
}
