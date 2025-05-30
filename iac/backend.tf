# Terraform Backend Configuration
# ------------------------------------------------------------------------------
# This file configures the GCS backend for storing Terraform state.
# The bucket name is expected to be provided during 'terraform init' via
# backend configuration, typically by a CI/CD pipeline.
# ------------------------------------------------------------------------------

terraform {
  backend "gcs" {
    # The bucket name will be provided via backend configuration in the CI/CD pipeline.
    # Example: terraform init -backend-config="bucket=your-tf-state-bucket"
    # prefix = "env/prod" # Optional: use prefixes for different environments
  }
}
