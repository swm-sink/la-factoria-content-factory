# Terraform Version and Provider Constraints
# ------------------------------------------------------------------------------
# This file defines the required versions for Terraform itself and for any
# providers used in the configuration. This helps ensure compatibility and
# predictable behavior across different environments and Terraform runs.
# ------------------------------------------------------------------------------

terraform {
  required_version = ">= 1.0" # Specify a minimum Terraform version

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0" # Pin to a specific major version, allow minor/patch updates
    }
  }
}
