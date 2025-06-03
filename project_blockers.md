# Project Blockers

This file lists critical issues that are currently preventing further progress on certain tasks.

## Firestore Database Issue (Encountered: 2025-06-02)

**Task(s) Blocked:** T-102 (Verify Endpoints in Swagger UI - partially), T-104 (Manual Endpoint Smoke Test), and any subsequent tasks relying on job creation or database interaction.

**Issue:** The application is unable to connect to the Firestore database. API calls requiring database access (e.g., POST `/api/v1/jobs`) are failing with a 500 Internal Server Error.

**Error Message:**
`"Failed to create job: 404 The database (default) does not exist for project ai-content-factory-460918 Please visit https://console.cloud.google.com/datastore/setup?project=ai-content-factory-460918 to add a Cloud Datastore or Cloud Firestore database."`

**Troubleshooting Steps/Verification Needed by User:**
1.  **Firestore Database Existence and Mode:** Confirm that a Firestore database exists in the `ai-content-factory-460918` project and is in the correct mode (Native or Datastore mode, ensuring consistency with application expectations).
2.  **IAM Permissions:** Double-check that the service account used by the application (locally or on Cloud Run) has the "Cloud Datastore User" role (or equivalent permissions for Firestore) for the `ai-content-factory-460918` project.
3.  **Project ID Configuration:** Verify that the application is correctly configured to use the `ai-content-factory-460918` project ID when initializing the Firestore client. This might be through an environment variable (e.g., `GOOGLE_CLOUD_PROJECT`) or explicitly in the code.
4.  **API Enablement:** Ensure the Cloud Firestore API is enabled for the `ai-content-factory-460918` project in the Google Cloud Console.
5.  **Authentication Context:** If running locally, ensure Application Default Credentials (ADC) are correctly configured and pointing to an identity with permissions for the `ai-content-factory-460918` project. `gcloud auth application-default login` might need to be re-run.
