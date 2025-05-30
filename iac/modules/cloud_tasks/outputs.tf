output "queue_name" {
  description = "The name of the Cloud Tasks queue."
  value       = google_cloud_tasks_queue.default.name
}

output "queue_id" {
  description = "The fully qualified ID of the Cloud Tasks queue (projects/PROJECT_ID/locations/LOCATION_ID/queues/QUEUE_NAME)."
  # The resource 'id' attribute usually provides the fully qualified path.
  value       = google_cloud_tasks_queue.default.id 
}

output "location" {
  description = "The location of the Cloud Tasks queue."
  value       = google_cloud_tasks_queue.default.location
} 