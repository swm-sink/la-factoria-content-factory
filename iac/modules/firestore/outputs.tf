output "database_name" {
  description = "The full name of the Firestore database."
  value       = google_firestore_database.default.name
}

output "location_id" {
  description = "The location of the Firestore database."
  value       = google_firestore_database.default.location_id
}

output "database_type" {
  description = "The type of the Firestore database (NATIVE or DATASTORE_MODE)."
  value       = google_firestore_database.default.type
}
