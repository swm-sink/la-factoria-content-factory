# Managing Secrets in ACPF

This document outlines the process for managing sensitive application secrets (API keys, database credentials, JWT secrets, etc.) for the AI Content Factory (ACPF) project, specifically for the MVP stage where a manual process is used for populating secret versions in GCP Secret Manager.

## Overview

All sensitive configuration values required by the application at runtime are stored as secrets in Google Cloud Secret Manager. The Terraform module (`iac/modules/secret_manager/`) provisions the *placeholders* (the secret shells) for these secrets. The actual secret *versions* (the sensitive values themselves) are added manually to these placeholders.

The application, when running in GCP (e.g., on Cloud Run), will have its service account granted IAM permission (`roles/secretmanager.secretAccessor`) to access these secret versions. The application code (`app/core/config/settings.py` via `app/core/security/secrets.py`) is designed to read these secrets from environment variables, which are populated by Cloud Run by referencing the secrets in Secret Manager.

## Required Secrets (MVP)

Based on `app/core/config/settings.py` (specifically `GSM_*_NAME` constants) and project requirements, the following secrets need to be created and populated in GCP Secret Manager under the project defined by `var.gcp_project_id` in Terraform:

1.  **`AI_CONTENT_FACTORY_API_KEY`**: The API key used to protect application endpoints. This is the `settings.api_key`.
2.  **`AI_CONTENT_FACTORY_ELEVENLABS_KEY`**: API key for accessing ElevenLabs TTS service. This is `settings.elevenlabs_api_key`.
3.  **`AI_CONTENT_FACTORY_JWT_SECRET_KEY`**: A strong, random string used for signing and verifying JWTs. This is `settings.jwt_secret_key`.
    *   Generate using: `openssl rand -hex 32`
4.  **`AI_CONTENT_FACTORY_SENTRY_DSN`**: (If Sentry integration is used) The DSN provided by Sentry for error reporting. This is `settings.sentry_dsn`.

**Note on Vertex AI Access:** Access to Vertex AI (Gemini) typically relies on the Cloud Run service account's IAM permissions (`roles/aiplatform.user` or similar) and Application Default Credentials (ADC). An explicit `VERTEX_AI_API_KEY` stored in Secret Manager is usually not required or used by the `google-cloud-aiplatform` library when running on GCP with a properly permissioned service account.

*(Add any other application-specific secrets as they are identified)*

## Manual Process for Populating Secret Versions (MVP)

Once the Terraform code has been applied and the secret placeholders are created in GCP Secret Manager, follow these steps to add the actual secret values:

**Prerequisites:**
*   `gcloud` CLI installed and configured with an account that has permissions to manage Secret Manager secrets (e.g., `Secret Manager Admin` role).
*   The actual secret values obtained from their respective service providers or generated securely.

**Steps:**

1.  **List available secrets (to confirm placeholders exist):**
    ```bash
    gcloud secrets list --project=YOUR_GCP_PROJECT_ID
    ```
    Replace `YOUR_GCP_PROJECT_ID` with your actual project ID.

2.  **For each secret, add its first version:**

    *   **Example for `AI_CONTENT_FACTORY_ELEVENLABS_KEY`:**
        Let's say your ElevenLabs API key is `el_yourActualApiKeyGoesHere`.

        Create a temporary file (e.g., `temp_secret.txt`) with the key as its content:
        ```text
        el_yourActualApiKeyGoesHere
        ```

        Then run the `gcloud` command:
        ```bash
        gcloud secrets versions add AI_CONTENT_FACTORY_ELEVENLABS_KEY --project=YOUR_GCP_PROJECT_ID --data-file="temp_secret.txt"
        ```
        (Ensure `AI_CONTENT_FACTORY_ELEVENLABS_KEY` matches the `secret_id` used in Terraform and referenced by `settings.py`).

        Securely delete `temp_secret.txt` after use.

    *   **Example for `AI_CONTENT_FACTORY_JWT_SECRET_KEY`:**
        Generate a strong secret:
        ```bash
        openssl rand -hex 32 > jwt_secret_value.txt
        ```
        Add it to Secret Manager:
        ```bash
        gcloud secrets versions add AI_CONTENT_FACTORY_JWT_SECRET_KEY --project=YOUR_GCP_PROJECT_ID --data-file="jwt_secret_value.txt"
        ```
        Securely delete `jwt_secret_value.txt`.

    *   Repeat for all other required secrets (`AI_CONTENT_FACTORY_API_KEY`, `AI_CONTENT_FACTORY_SENTRY_DSN`, etc.).

3.  **Verify secret version was added (optional):**
    ```bash
    gcloud secrets versions list AI_CONTENT_FACTORY_ELEVENLABS_KEY --project=YOUR_GCP_PROJECT_ID
    gcloud secrets versions access latest --secret=AI_CONTENT_FACTORY_ELEVENLABS_KEY --project=YOUR_GCP_PROJECT_ID # (This will print the secret value to console)
    ```

**Important Security Notes:**
*   Never commit actual secret values to version control.
*   Use strong, unique values for each secret.
*   Limit access to who can manage secrets in GCP IAM.
*   For production environments, consider automating secret rotation if the services support it and if a more automated CI/CD process for secrets is implemented post-MVP.

## Referencing Secrets in Cloud Run (Terraform)

The Cloud Run Terraform module (`iac/main.tf` calling `iac/modules/cloud_run_service/main.tf`) should be configured to mount these secrets as environment variables for the application container using the `secret_env_vars` argument. Example snippet from `iac/main.tf` (root module call):

```hcl
# In iac/main.tf, calling the cloud_run_service module:
module "cloud_run_service" {
  # ... other arguments ...
  secret_env_vars = [
    { 
      name           = "API_KEY", # Env var name available to the app
      secret_name    = module.secret_manager.secret_ids_map["AI_CONTENT_FACTORY_API_KEY"], # Full Secret Manager ID from module output
      secret_version = "latest"
    },
    { 
      name           = "ELEVENLABS_API_KEY", 
      secret_name    = module.secret_manager.secret_ids_map["AI_CONTENT_FACTORY_ELEVENLABS_KEY"], 
      secret_version = "latest"
    },
    # Repeat for JWT_SECRET_KEY, SENTRY_DSN etc.
  ]
}
```
This configuration ensures that when the application running in Cloud Run calls `os.getenv("API_KEY")`, it receives the value from the `AI_CONTENT_FACTORY_API_KEY` secret stored in Secret Manager. The application code (`settings.py`) is already designed to look for these exact environment variable names.

## Future Considerations (Post-MVP)
*   Automated secret rotation.
*   Using a more secure CI/CD process for managing secret versions (e.g., with tools like HashiCorp Vault or specialized CI/CD secrets management). 