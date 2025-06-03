output "secret_ids" {
  description = "A map of secret names to their full Secret Manager resource IDs."
  value       = { for secret in google_secret_manager_secret.default : secret.secret_id => secret.id }
}

output "secret_names_list" {
  description = "A list of the created secret names (short IDs)."
  value       = keys(google_secret_manager_secret.default)
}
