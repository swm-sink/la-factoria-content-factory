# Deployment Guide (AI Content Factory)

**This document is deprecated.**

Deployment of the AI Content Factory is now primarily managed via Infrastructure as Code (IaC) using Terraform and automated CI/CD pipelines using GitHub Actions.

Please refer to:

-   **`README.md`**: For project overview, local setup, and general deployment concepts.
-   **`iac/` directory**: For all Terraform configurations defining the GCP infrastructure.
-   **`.github/workflows/` directory**: For CI/CD pipeline definitions that handle automated builds, testing, and deployments to Google Cloud Run.
-   **`docs/operational/deployment_checklist.md`**: For a comprehensive checklist of considerations and verification steps, many ofwhich are automated by the CI/CD and IaC setup.

Manual `gcloud` commands are generally not the primary method for deployment but may be used for specific troubleshooting or one-off tasks as documented in the `deployment_checklist.md` or other operational guides. 