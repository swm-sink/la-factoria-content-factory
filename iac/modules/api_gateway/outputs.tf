output "gateway_url" {
  description = "The default URL of the deployed API Gateway."
  value       = google_api_gateway_gateway.default.default_hostname
}

output "gateway_id" {
  description = "The ID of the API Gateway."
  value       = google_api_gateway_gateway.default.gateway_id
}

output "api_config_id" {
  description = "The ID of the API Config used by the gateway."
  value       = google_api_gateway_gateway.default.api_config
}
