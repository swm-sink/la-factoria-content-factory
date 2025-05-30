# Project Task Tracker

## Current Sprint Focus (Next ~2 Weeks) - Foundational Stability & Cleanup - COMPLETED

### Execution Path 1: Settings & Security (Priority) - COMPLETED
**Goal**: Secure and consolidate all application settings with proper environment variable 
handling and security measures. Ensure `app/main.py` (and all components) use these 
settings.

- [x] Task 1.5: Consolidate settings into single source of truth 
[AI-EXECUTION-SESSION-20250527]
- [x] Task 1.6: Remove default insecure `API_KEY` from `app/core/config/settings.py` 
[AI-EXECUTION-SESSION-20250527]
- [x] Task 1.7: Review and ensure all critical settings in `app/core/config/settings.py` 
are correctly defined [AI-EXECUTION-SESSION-20250528]
- [x] Task 1.8: Implement Google Secret Manager integration for sensitive settings 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 1.9: Add comprehensive Google-style docstrings to `app/core/config/settings.py` 
and `app/core/security/secrets.py` [AI-EXECUTION-SESSION-20250528]

### Execution Path 2: Core Service Strategy & API Alignment - COMPLETED
**Goal**: Align the API (`app/main.py` and `app/api/routes/`) to use the 
`EnhancedMultiStepContentGenerationService` from `app/services/
multi_step_content_generation.py` as the primary service for content generation.

- [x] Task 2.1: Designate `EnhancedMultiStepContentGenerationService` as primary & 
Refactor API to use it [AI-EXECUTION-SESSION-20250528]
    *   [x] Verified `app/main.py` API endpoint uses 
    `EnhancedMultiStepContentGenerationService` and compatible Pydantic models.
    *   [x] Created/Updated `app/core/docs/service_architecture.md` to reflect 
    `EnhancedMultiStepContentGenerationService` as primary.
    *   [x] Deprecated the simple `app/services/content_generation.py` with warnings and 
    docstring updates.

- [x] Task 2.2: Adapt API for Asynchronous Job-Based Workflow 
[AI-EXECUTION-SESSION-PREVIOUS]
    *   Dependencies: Task 2.1
    *   Files: Created and implemented:
        *   `app/core/schemas/job.py`: Pydantic models for job management.
        *   `app/api/routes/jobs.py`: API endpoints for job operations.
        *   `app/services/job_manager.py`: Job lifecycle management service.
    *   Steps:
        *   Created job schema with status tracking, progress monitoring, and error 
        handling.
        *   Implemented RESTful job management endpoints (create, list, get, update, 
        delete).
        *   The `create_job` endpoint now accepts `ContentRequest` directly.
        *   `JobManager` now uses `ContentRequest` from `job.metadata` to call 
        `EnhancedMultiStepContentGenerationService` for actual content generation 
        (executed in a separate thread).
        *   Basic result and error state from content generation service are stored in the 
        Job object.
        *   Updated main API router to include job endpoints.
    *   Success Criteria: Asynchronous job system framework implemented with API support 
    and core content generation processing.
    *   **Pending Enhancements / Skipped Items (deferred until after E2E async testing):**
        *   **Detailed Real-time Progress Tracking:** Current progress updates in 
        `JobManager._process_job` are placeholders. True real-time progress requires 
        deeper integration with `EnhancedMultiStepContentGenerationService`'s internal 
        `ProgressTracker` (e.g., via callbacks or a shared observable state).
        *   **Job Persistence:** The `JobManager` currently stores jobs in-memory. For 
        production, job state needs to be persisted to a database (e.g., SQLite, 
        PostgreSQL). This is a significant next step (see Execution Path 4).
        *   **Advanced Error Handling & Retries:** While basic error state is captured, 
        more granular error codes from the content generation process and retry mechanisms 
        for transient issues could be implemented.
        *   **Scalability & Resource Management:** For a high number of concurrent jobs, a 
        more robust worker system (e.g., Celery, or careful management of `asyncio.
        to_thread` with resource limits) and strategies for managing external API rate 
        limits are needed (see Execution Path 5).

- [x] Task 2.3: Refactor API Routers to be fully within `app/api/routes/` 
[AI-EXECUTION-SESSION-20250528]
    *   [x] Created `app/api/routes/content.py`.
    *   [x] Moved `/api/generate-content` and `/api/health` endpoint logic to `app/api/
    routes/content.py`.
    *   [x] Created `app/api/routes.py` to aggregate routers.
    *   [x] Updated `app/main.py` to use the main `api_router` with prefix.

### Execution Path 3: Backend Dependencies & Cleanup - COMPLETED
**Goal**: Resolve dependency conflicts, ensure proper version management, and remove 
obsolete code.

- [x] Task 3.1: Resolve `pytest` version conflict & standardize usage 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 3.2: Resolve `pydantic` & `pydantic-settings` versions (ensure Pydantic V2) 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 3.3: Clean up `requirements.txt` (move all dev dependencies) 
[AI-EXECUTION-SESSION-20250528]

- [x] Task 3.4: Full Review & Cleanup/Deletion of `backend/` directory 
[AI-EXECUTION-SESSION-PREVIOUS]
    *   Dependencies: Execution Paths 1 & 2 fully completed and stable (or Task 2.2 
    deferred).
    *   Files: Entire `backend/` directory.
    *   Steps:
        1.  **Final Confirmation**: Verified all functionality from `backend/app/` is 
        covered by `app/`.
        2.  Checked `Dockerfile` and `docker-compose.yml` point to `app.main:app` and 
        updated them.
        3.  Created a final backup of `backend/` to `backend_backup/`.
        4.  Deleted the `backend/` directory.
        5.  Removed `__pycache__` directories from `app/`.
    *   Success Criteria: `backend/` removed; app structure consolidated into `app/`. 
    Docker configurations updated.
    *   **Pending Items (to be addressed later / User Action Required):**
        *   **Python 3.13 `pydantic-core` Build Issue (User Action for Local Dev):** Local 
        `pytest` execution with Python 3.13 encounters build failures for `pydantic-core`. 
        Workaround `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` helps but a permanent fix is 
        needed if local Python 3.13 testing is a priority.
        *   **`.env` File Creation (User Action for Testing):** A `.env` file at the 
        project root is required for `docker-compose` to run successfully and for local 
        testing if Secret Manager is not configured locally. It should contain essential 
        variables like `API_KEY`, `ELEVENLABS_API_KEY`, `GCP_PROJECT_ID`.

---
## NEW SPRINT FOCUS: Enable End-to-End Testing of Asynchronous Job System - COMPLETED
**Goal**: Make the asynchronous content generation flow fully functional and testable, 
from job creation to retrieving generated content, with basic but meaningful progress 
indication.

- [x] **Task A: Add Missing Job Parameters (`target_duration`, `target_pages`)**
    - [x] **Sub-task A.1:** Update `app/api/routes/content.py`'s `ContentRequest` model to 
    include `target_duration: Optional[float] = None` and `target_pages: Optional[int] = 
    None`.
    - [x] **Sub-task A.2:** Ensure `JobManager._process_job` correctly extracts these from 
    `job.metadata` (derived from `ContentRequest`) and passes them to `self.
    _content_service.generate_long_form_content`.
    - [x] **Sub-task A.3:** Verify OpenAPI schema (auto-generated docs) for the `/jobs` 
    endpoint reflects these new optional parameters in the request body.

- [x] **Task B: Improve Placeholder Progress Updates in `JobManager`**
    - [x] **Sub-task B.1:** Analyze the main stages in 
    `EnhancedMultiStepContentGenerationService.generate_long_form_content` (e.g., Cache 
    Check, Topic Decomposition, Section Generation, Assembly, Quality Eval, Versioning).
    - [x] **Sub-task B.2:** Modify `JobManager._process_job` to update `Job.progress` with 
    more meaningful `current_step` messages and `percentage` estimates that roughly 
    correspond to these actual service stages.

- [x] **Task C: Document Manual User Steps Required for Testing (User Action Required)**
    - [x] **Sub-task C.1:** (User Action) Create `.env` file at project root with `API_KEY`, 
    `ELEVENLABS_API_KEY`, `GCP_PROJECT_ID` for Dockerized testing and local testing if 
    Secret Manager is not used locally. (Documentation updated in README.md)
    - [x] **Sub-task C.2:** (User Action) For local testing on Python 3.13 outside Docker, the 
    `pydantic-core` build issue may require setting 
    `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` or other resolution. (Documentation updated in README.md)

---
## CURRENT SPRINT FOCUS: Transition to GCP-Native Serverless Architecture

**Goal**: Migrate the application to a fully managed, scalable, and robust serverless architecture on Google Cloud Platform. This involves setting up core GCP infrastructure, refactoring job management to use Firestore and Cloud Tasks, implementing Cloud Workflows for orchestration, and leveraging API Gateway and other GCP services for a production-grade deployment.

### Phase 1: Core GCP Infrastructure Setup, Containerization, CI/CD & Initial Wiring
**Overall Goal for Phase 1**: Establish foundational GCP services via Terraform, create a runnable and production-like Docker container, implement CI/CD for testing and deployment, and perform initial code wiring for Firestore and Cloud Tasks to unblock Phase 2.

- [ ] **Task GCP-1.1: GCP Project Setup & API Enablement (Prerequisite)**
    - [ ] Verify GCP project is created and configured.
    - [ ] Enable necessary APIs: Cloud Run, Vertex AI, Firestore, Cloud Tasks, Cloud Workflows, API Gateway, Secret Manager, Cloud Logging, Cloud Monitoring, Artifact Registry.

---
#### **Sub-Phase 1.A: Containerization Enhancements & Test Alignment**
**Goal:** Create a production-ready Docker image with Nginx for serving static content (future) and proxying to Uvicorn, and ensure basic test suite is functional.

*(Note: Flask purge and test alignment from original plan now in Execution Path 11, to be completed first)*

- [ ] **Task GCP-1.A.1: Implement `start.sh` for Docker Container**
    - [ ] Create `start.sh` in the project root:
      ```bash
      #!/bin/sh
      set -e
      # Start Nginx in the background
      nginx -g 'daemon off;' &
      # Start Uvicorn, listening on port 8000 (or $APP_PORT)
      exec uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8000} --workers ${UVICORN_WORKERS:-1}
      ```
    - [ ] In `Dockerfile`, add `COPY start.sh /start.sh`, `RUN chmod +x /start.sh`.
    - [ ] Change Dockerfile `CMD` to `["/start.sh"]`.
- [ ] **Task GCP-1.A.2: Configure Nginx in Docker Image**
    - [ ] Create `nginx.conf` (e.g., in a new `docker/nginx/nginx.conf` directory):
      ```nginx
      worker_processes auto;
      events {
          worker_connections 1024;
      }
      http {
          include /etc/nginx/mime.types;
          default_type application/octet-stream;

          sendfile on;
          keepalive_timeout 65;

          # Basic static file serving (if/when frontend assets are added)
          server {
              listen 80; # Nginx listens on port 80 inside the container
              server_name localhost;

              location / {
                  root /usr/share/nginx/html; # Standard Nginx static content location
                  index index.html index.htm;
                  try_files $uri $uri/ /index.html; # For SPAs if used later
              }

              location /api {
                  proxy_pass http://localhost:${APP_PORT:-8000}; # Proxy to Uvicorn on its internal port
                  proxy_set_header Host $host;
                  proxy_set_header X-Real-IP $remote_addr;
                  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                  proxy_set_header X-Forwarded-Proto $scheme;
              }

              # Optional: Health check endpoint directly handled by Nginx
              location = /nginx_health {
                  access_log off;
                  return 200 "Nginx is healthy";
                  add_header Content-Type text/plain;
              }
          }
      }
      ```
    - [ ] In `Dockerfile`, add `COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf`.
    - [ ] Ensure Nginx is installed in the Docker base image (e.g., `apt-get update && apt-get install -y nginx`).
    - [ ] Create a placeholder `index.html` in `docker/static_content/index.html` (e.g., "Welcome to ACPF") and copy it to `/usr/share/nginx/html` in the Dockerfile.

---
#### **Sub-Phase 1.B: Terraform Modular Scaffolding**
**Goal:** Define all core GCP services as modular Terraform configurations.

- [ ] **Task GCP-1.B.1: Terraform Root Setup & Backend Configuration** (Adapts GCP-1.2)
    - [ ] Initialize Terraform in `iac/` directory.
    - [ ] Create `iac/main.tf` to call modules.
    - [ ] Create `iac/variables.tf` for project_id, region, etc.
    - [ ] Create `iac/versions.tf` to pin GCP provider.
    - [ ] Create `iac/backend.tf` to configure GCS backend for Terraform state (bucket name to be provided via CI).
    - [ ] Define a common `iac/modules/outputs.tf` if needed or rely on root outputs.
- [ ] **Task GCP-1.B.2: Terraform Module - Artifact Registry** (Adapts GCP-1.3)
    - [ ] Create `iac/modules/artifact_registry/` with `main.tf`, `variables.tf`, `outputs.tf`.
    - [ ] Define `google_artifact_registry_repository` resource.
    - [ ] Configuration: repository_id (e.g., "acpf"), location (from var), format "DOCKER".
    - [ ] Enable vulnerability scanning (`docker_config { immutable_tags = true }` and ensure scanning is enabled at project/org level or specific settings).
    - [ ] Outputs: repository name, location.
- [ ] **Task GCP-1.B.3: Terraform Module - Secret Manager** (Adapts GCP-1.3)
    - [ ] Create `iac/modules/secret_manager/` with `main.tf`, `variables.tf`, `outputs.tf`.
    - [ ] Define `google_secret_manager_secret` resources for required secrets (e.g., `APP_API_KEY`, `ELEVENLABS_API_KEY`, `VERTEX_AI_API_KEY`). Names provided as variables.
    - [ ] Note: Secret *versions* (actual values) are not managed by Terraform here; values injected manually or by CI.
    - [ ] Add placeholder `replication { auto {} }` or specific regional replication.
    - [ ] Mark `rotation {}` block as a placeholder for future implementation if needed.
    - [ ] Outputs: List of secret IDs (full names).
- [ ] **Task GCP-1.B.4: Terraform Module - Cloud Run Service** (Adapts GCP-1.3)
    - [ ] Create `iac/modules/cloud_run_service/` with `main.tf`, `variables.tf`, `outputs.tf`.
    - [ ] Define `google_cloud_run_v2_service` resource.
    - [ ] Configuration:
        - `location` (from var).
        - `ingress = "INGRESS_TRAFFIC_ALL"` (for API Gateway access).
        - `template`:
            - `containers`: image (from Artifact Registry module output + tag from CI var), ports (containerPort 80 for Nginx).
            - `service_account` (name of SA to be created in IAM module or root).
            - `environment_variables`: (e.g., `APP_PORT=8000`, `GCP_PROJECT_ID`, links to Secret Manager secrets for API keys).
            - Scaling, CPU, memory settings as variables.
    - [ ] Outputs: service URL, service account email (if created here, else taken as input).
- [ ] **Task GCP-1.B.5: Terraform Module - Firestore** (Adapts GCP-1.4)
    - [ ] Create `iac/modules/firestore/` with `main.tf`, `variables.tf`, `outputs.tf`.
    - [ ] Define `google_firestore_database` resource.
    - [ ] Configuration: type "NATIVE", location_id (e.g., "nam5" or project default from var).
    - [ ] Outputs: (None explicitly needed from DB resource itself, but confirm).
    - [ ] (Indexes `google_firestore_index` will be defined later as needed by queries, likely in a separate module or by application logic if simple).
- [ ] **Task GCP-1.B.6: Terraform Module - Cloud Tasks** (Adapts GCP-1.4)
    - [ ] Create `iac/modules/cloud_tasks/` with `main.tf`, `variables.tf`, `outputs.tf`.
    - [ ] Define `google_cloud_tasks_queue` resource.
    - [ ] Configuration: name (e.g., "acpf-content-generation-queue"), location (from var).
    - [ ] Configure retry policies, rate limits (as variables).
    - [ ] (OIDC service account for task invocation will be referenced from IAM module or root).
    - [ ] Outputs: queue ID (full name).
- [ ] **Task GCP-1.B.7: Terraform Module - API Gateway** (Adapts GCP-1.4)
    - [ ] Create `iac/modules/api_gateway/` with `main.tf`, `variables.tf`, `outputs.tf`.
        - [ ] Define `google_api_gateway_api`, `google_api_gateway_api_config`, `google_api_gateway_gateway`.
    - [ ] Manage `openapi.yaml` in `iac/files/openapi.yaml`. Initially include paths for `/api/v1/health` and `/api/v1/jobs/...` pointing to the Cloud Run service backend.
        - The `openapi.yaml` should reference the Cloud Run service URL (output from cloud_run_service module).
    - [ ] Outputs: gateway URL.
- [ ] **Task GCP-1.B.8: Terraform Module - Cloud Workflows** (Adapts GCP-1.5)
    - [ ] Create `iac/modules/workflows/` with `main.tf`, `variables.tf`, `outputs.tf`.
    - [ ] Define `google_workflows_workflow` resource.
    - [ ] Configuration: name, region, service_account (from IAM module or root).
    - [ ] `source_contents`: Use a placeholder YAML workflow definition initially; real logic to be developed in Phase 2.
    - [ ] Outputs: workflow ID (full name).
- [ ] **Task GCP-1.B.9: Terraform Module/Root - IAM & Service Accounts** (Adapts GCP-1.6)
    - [ ] Create `iac/modules/iam/` or manage in root `main.tf`.
    - [ ] Define `google_service_account` for the Cloud Run application.
    - [ ] Grant this SA minimal necessary permissions:
        - Secret Manager Secret Accessor (for specified secrets).
        - Vertex AI User.
        - Firestore User.
        - Cloud Tasks Enqueuer (if app creates tasks directly) / Cloud Tasks Task Runner (if invoked via HTTP by tasks - requires OIDC setup).
        - Cloud Workflows Invoker (if app triggers workflows).
        - Cloud Logging Log Writer, Cloud Monitoring Metric Writer.
    - [ ] Define OIDC service account for Cloud Tasks to invoke Cloud Run securely.
    - [ ] Grant `roles/run.invoker` to the Cloud Tasks OIDC SA on the Cloud Run service.
    - [ ] Outputs: Cloud Run service account email.

---
#### **Sub-Phase 1.C: CI/CD (GitHub Actions)**
**Goal:** Implement a GitHub Actions workflow for automated testing, building, and deployment.

- [ ] **Task GCP-1.C.1: CI Job - "test"**
    - [ ] Trigger: on push to `main` and `develop` branches, and on pull requests.
    - [ ] Steps:
        - Checkout code.
        - Setup Python.
        - Install dependencies (`pip install -r requirements.txt -r requirements-dev.txt`).
        - Run `pytest`.
        - (Optional) Run pre-commit checks (`pre-commit run --all-files`).
- [ ] **Task GCP-1.C.2: CI Job - "build-and-push-image"**
    - [ ] Trigger: on push to `main` (after "test" job succeeds).
    - [ ] Depends on: "test" job.
    - [ ] Steps:
        - Checkout code.
        - Authenticate to GCP Artifact Registry (e.g., using Workload Identity Federation).
        - Docker build (`docker build -t us-central1-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/acpf/ai-content-factory:$GITHUB_SHA .`).
        - Docker push (`docker push us-central1-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/acpf/ai-content-factory:$GITHUB_SHA`).
- [ ] **Task GCP-1.C.3: CI Job - "terraform-apply"**
    - [ ] Trigger: on push to `main` (after "test" job succeeds). Consider manual approval for production applies.
    - [ ] Depends on: "test" job.
    - [ ] Environment: `staging` or `production` (use GitHub environments for secrets).
    - [ ] Steps:
        - Checkout code.
        - Setup Terraform.
        - Authenticate to GCP (Workload Identity Federation).
        - `cd iac/`
        - `terraform init -backend-config="bucket=${{ secrets.GCP_TERRAFORM_STATE_BUCKET }}" -backend-config="prefix=env/${{ github.ref_name }}"` (or similar for env isolation).
        - `terraform validate`.
        - `terraform plan -var="project_id=${{ secrets.GCP_PROJECT_ID }}" -var="region=${{ secrets.GCP_REGION }}" ... (other vars as needed)`
        - `terraform apply -auto-approve -var="project_id=${{ secrets.GCP_PROJECT_ID }}" ...`
- [ ] **Task GCP-1.C.4: CI Job - "deploy-cloud-run"**
    - [ ] Trigger: on push to `main` (after "build-and-push-image" and "terraform-apply" succeed).
    - [ ] Depends on: "build-and-push-image", "terraform-apply".
    - [ ] Steps:
        - Authenticate to GCP (Workload Identity Federation).
        - `gcloud run deploy acpf-mvp-cr-apiserver --image us-central1-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/acpf/ai-content-factory:$GITHUB_SHA --region ${{ secrets.GCP_REGION }} --project ${{ secrets.GCP_PROJECT_ID }} --service-account <cloud_run_sa_email_from_terraform_output_or_known>`
        - (Ensure Cloud Run service name matches what's in Terraform or use data source).

---
#### **Sub-Phase 1.D: Code Wiring for Firestore & Cloud Tasks (Unblocks Phase 2 Reliability)**
**Goal:** Implement the Python code to interact with Firestore for job persistence and Cloud Tasks for enqueuing generation tasks.

- [ ] **Task GCP-1.D.1: Implement Firestore Job Persistence Logic**
    - [ ] Create `app/services/job/firestore_client.py` (or similar):
      ```python
      # app/services/job/firestore_client.py
      from google.cloud import firestore_async # Ensure this is google-cloud-firestore >= 2.0 for async
      from app.core.config.settings import settings
      from app.models.pydantic.job import Job, JobStatus # Assuming Job is Pydantic
      from typing import Optional, Dict, Any
      import logging

      logger = logging.getLogger(__name__)
      db = None

      def get_firestore_client():
          global db
          if db is None:
              # Initialize client. For Cloud Run, project should be inferred.
              # For local dev with emulator, set FIRESTORE_EMULATOR_HOST env var.
              db = firestore_async.AsyncClient(project=settings.GCP_PROJECT_ID if settings.GCP_PROJECT_ID else None)
              logger.info(f"Firestore AsyncClient initialized for project: {db.project}")
          return db

      async def create_job_in_firestore(job: Job) -> None:
          client = get_firestore_client()
          job_dict = job.model_dump(exclude_none=True) # Use model_dump for Pydantic V2
          # Ensure complex objects like error/progress are also dicts if nested Pydantic
          if job_dict.get("error"):
              job_dict["error"] = job.error.model_dump(exclude_none=True) if job.error else None
          if job_dict.get("progress"):
              job_dict["progress"] = job.progress.model_dump(exclude_none=True) if job.progress else None

          logger.info(f"Creating job {job.id} in Firestore with data: {job_dict}")
          await client.collection("jobs").document(job.id).set(job_dict)
          logger.info(f"Job {job.id} created in Firestore.")


      async def update_job_status_in_firestore(job_id: str, status: JobStatus, **kwargs: Any) -> None:
          client = get_firestore_client()
          update_data: Dict[str, Any] = {"status": status.value, **kwargs} # Use .value for Enums
          # Convert Pydantic sub-models in kwargs to dicts
          for key, value in update_data.items():
              if hasattr(value, 'model_dump'): # Check if it's a Pydantic model
                  update_data[key] = value.model_dump(exclude_none=True)
          
          logger.info(f"Updating job {job_id} in Firestore with status: {status.value} and data: {update_data}")
          await client.collection("jobs").document(job_id).update(update_data)
          logger.info(f"Job {job_id} status updated in Firestore.")

      async def get_job_from_firestore(job_id: str) -> Optional[Job]:
          client = get_firestore_client()
          logger.info(f"Fetching job {job_id} from Firestore.")
          doc_ref = client.collection("jobs").document(job_id)
          doc = await doc_ref.get()
          if doc.exists:
              logger.info(f"Job {job_id} found in Firestore.")
              # Reconstruct Pydantic model from dict
              return Job(**doc.to_dict())
          logger.warning(f"Job {job_id} not found in Firestore.")
          return None
      ```
    - [ ] Ensure `google-cloud-firestore` (version supporting async) is in `requirements.txt`.
- [ ] **Task GCP-1.D.2: Implement Cloud Tasks Enqueue Logic**
    - [ ] Create `app/services/job/tasks_client.py` (or similar):
      ```python
      # app/services/job/tasks_client.py
      from google.cloud import tasks_v2
      from google.protobuf import timestamp_pb2, duration_pb2
      from app.core.config.settings import settings
      from app.models.pydantic.job import Job # Assuming Job is Pydantic
      import json
      import datetime
      import logging

      logger = logging.getLogger(__name__)
      tasks_client = None

      def get_tasks_client():
          global tasks_client
          if tasks_client is None:
              tasks_client = tasks_v2.CloudTasksAsyncClient()
              logger.info("CloudTasksAsyncClient initialized.")
          return tasks_client

      async def enqueue_content_generation_task(job: Job) -> str:
          client = get_tasks_client()
          
          if not all([settings.GCP_PROJECT_ID, settings.GCP_QUEUE_LOCATION, settings.GCP_JOB_QUEUE_NAME, settings.GCP_JOB_WORKER_ENDPOINT, settings.GCP_JOB_WORKER_SA_EMAIL]):
              logger.error("Missing Cloud Tasks configuration in settings. Cannot enqueue task.")
              raise ValueError("Cloud Tasks configuration is incomplete.")

          queue_path = client.queue_path(settings.GCP_PROJECT_ID, settings.GCP_QUEUE_LOCATION, settings.GCP_JOB_QUEUE_NAME)
          
          payload = {"job_id": job.id}
          task_body = json.dumps(payload).encode()

          task = tasks_v2.types.Task(
              http_request=tasks_v2.types.HttpRequest(
                  http_method=tasks_v2.types.HttpMethod.POST,
                  url=settings.GCP_JOB_WORKER_ENDPOINT, # e.g., https://your-cloud-run-worker-url/process-job
                  oidc_token=tasks_v2.types.OidcToken(
                      service_account_email=settings.GCP_JOB_WORKER_SA_EMAIL
                  ),
                  headers={"Content-Type": "application/json"},
                  body=task_body,
              ),
              # Optional: schedule_time, dispatch_deadline
              # schedule_time=timestamp_pb2.Timestamp(seconds=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) + 10), # 10s delay
          )
          
          logger.info(f"Creating Cloud Task for job {job.id} in queue {queue_path} to target {settings.GCP_JOB_WORKER_ENDPOINT}")
          created_task = await client.create_task(request={"parent": queue_path, "task": task})
          logger.info(f"Cloud Task {created_task.name} created for job {job.id}.")
          return created_task.name
      ```
    - [ ] Ensure `google-cloud-tasks` is in `requirements.txt`.
    - [ ] Add new settings to `app/core/config/settings.py`: `GCP_QUEUE_LOCATION`, `GCP_JOB_QUEUE_NAME`, `GCP_JOB_WORKER_ENDPOINT`, `GCP_JOB_WORKER_SA_EMAIL`.
- [ ] **Task GCP-1.D.3: Update `JobManager` to Use Firestore and Cloud Tasks**
    - [ ] Modify `app/services/job_manager.py`:
        - Remove in-memory `self._jobs` dictionary.
        - In `create_job`:
            - Call `create_job_in_firestore(job_instance)`.
            - Call `enqueue_content_generation_task(job_instance)`.
            - Update job status to `JobStatus.QUEUED` in Firestore.
        - In `get_job`:
            - Call `get_job_from_firestore(job_id)`.
        - (The actual job processing logic that was in `_process_job` will eventually move to a new HTTP endpoint on Cloud Run, triggered by the Cloud Task. This new endpoint will fetch job details from Firestore, call `EnhancedMultiStepContentGenerationService`, and update job status/results in Firestore. This worker endpoint is part of Phase 2, but the enqueueing happens here).
- [ ] **Task GCP-1.D.4: Implement HTTP Worker Endpoint for Cloud Tasks**
    - [ ] Create a new API router (e.g., in `app/api/routes/worker.py`) with an endpoint like `/process-job`.
    - [ ] This endpoint will:
        - Receive `{"job_id": "..."}` in the request body.
        - Be secured to only allow invocation from Cloud Tasks (using OIDC token validation, FastAPI dependency).
        - Fetch the job details from Firestore using `get_job_from_firestore(job_id)`.
        - Update job status to `PROCESSING` in Firestore.
        - Execute the core content generation logic by calling `EnhancedMultiStepContentGenerationService.generate_long_form_content(...)` (similar to how `_process_job` did).
        - On success, update job status to `COMPLETED` and store results in Firestore.
        - On failure, update job status to `FAILED` and store error details in Firestore.
    - [ ] Ensure this endpoint is NOT exposed via API Gateway if it's internal. Cloud Run allows direct invocation.

---
#### **Sub-Phase 1.E: Documentation & Final Review**
- [ ] **Task GCP-1.E.1: Update `README.md` and Developer Documentation**
    - [ ] Document new environment variables needed for local dev (if any related to GCP services).
    - [ ] Document Terraform setup and usage (`iac/README.md`).
    - [ ] Document CI/CD pipeline.
    - [ ] Document how to use GCP emulators locally (Task GCP-1.7).
- [ ] **Task GCP-1.E.2: Phase 1 Review and "gcp-smoke-test" Branch**
    - [ ] After Sub-Phases 1.A to 1.D (excluding the worker endpoint implementation in 1.D.4 which can be parallel) are merged and CI passes for "test", "build-push", "terraform-apply".
    - [ ] Create a `gcp-smoke-test` branch.
    - [ ] Manually run/verify `terraform apply` for a staging environment.
    - [ ] Deploy the image using `gcloud run deploy ... --image ...`.
    - [ ] Test the `/api/v1/health` endpoint (via API Gateway if configured, or directly to Cloud Run if not).
    - [ ] Check logs for secure secret access.
    - [ ] If successful, this clears the path for deeper Phase 2 work (like full Cloud Workflows orchestration).

---
**(Existing Phase 1 tasks like GCP-1.5, GCP-1.6, GCP-1.7 will be re-evaluated and either integrated into the modules above, handled at the root Terraform level, or remain as distinct tasks if they are cross-cutting concerns or documentation efforts.)**

**Next Steps for this Phase:**
1. Begin with **Execution Path 11** tasks to clean up the repository and align tests.
2. Proceed to **Sub-Phase 1.A: Containerization Enhancements**.
3. Continue with **Sub-Phase 1.B: Terraform Modular Scaffolding**.
4. Implement **Sub-Phase 1.C: CI/CD (GitHub Actions)**.
5. Implement **Sub-Phase 1.D: Code Wiring for Firestore & Cloud Tasks**.
6. Conclude with **Sub-Phase 1.E: Documentation & Final Review**.

---
## Previous Sprint Focus (Foundational Stability & Cleanup) - COMPLETED 
**(Duplicated Section for historical reference only - tasks are identical to the first section with this title)**

### Execution Path 1: Settings & Security (Priority) - COMPLETED
### Execution Path 2: Core Service Strategy & API Alignment - COMPLETED
### Execution Path 3: Backend Dependencies & Cleanup - COMPLETED

---
## Phase 2: SaaS Quality Enhancements (Post-GCP Transition Phase 1)
**Note:** These tasks are adapted to leverage the new GCP-Native Serverless Architecture.

### Execution Path 4: Reliability & Resilience (GCP Focused)
**Goal**: Enhance the application's ability to handle failures gracefully, ensure data 
integrity, and recover from errors, using GCP services.

- **Task 4.1: Implement Job Persistence for Asynchronous System using Firestore**
    - **Sub-task 4.1.1: Database Technology Chosen: Firestore (Native Mode).** (Decision made as part of GCP architecture)
    - **Sub-task 4.1.2: Define Firestore Document Model for Jobs.**
        - Goal: Translate `Job` Pydantic model to a Firestore document structure.
        - Proposed Schema (conceptual for Firestore):
          ```json
          {
            "id": "string (UUID)",
            "status": "string (pending, processing, completed, failed, cancelled)",
            "created_at": "timestamp",
            "updated_at": "timestamp",
            "completed_at": "timestamp (optional)",
            "error": { // JobError model
              "code": "string (JobErrorCode)",
              "message": "string",
              "details": "string (optional)"
            },
            "progress": { // JobProgress model
              "current_step": "string",
              "total_steps": "integer",
              "percentage": "float",
              "completed_steps": ["string"]
            },
            "result": "map (JSON structure of the job result)",
            "metadata": "map (JSON structure of ContentRequest)"
          }
          ```
        - Considerations: Use Firestore server timestamps for `created_at`, `updated_at`.
        - Plan for indexing critical fields for querying (e.g., `status`, `user_id` if applicable, `created_at`).
    - **Sub-task 4.1.3: Implement Firestore Interaction Logic in `JobManager`.**
        - Replace in-memory `self._jobs` with Firestore client operations (async `google-cloud-firestore`).
        - Implement CRUD operations for jobs in Firestore.
    - **Sub-task 4.1.4: Database Migrations (Not typically required for Firestore schema changes like SQL).**
        - Data migration/transformation scripts might be needed if structure changes significantly later.
    - **Sub-task 4.1.5: Test Job Persistence thoroughly with Firestore.**
        - Ensure jobs are saved, retrieved, updated, and listed correctly.
        - Test application restarts.

- **Task 4.2: Implement Detailed Real-time Progress Tracking for Jobs (Firestore Based)**
    - (Sub-tasks remain largely the same, but `Job.progress` updates will write to Firestore)
    - **Sub-task 4.2.1: Design Progress Update Mechanism.**
    - **Sub-task 4.2.2: Update `EnhancedMultiStepContentGenerationService` Progress Reporting.**
    - **Sub-task 4.2.3: Update `JobManager._process_job` to use Detailed Progress (writing to Firestore).**

- **Task 4.3: Advanced Error Handling & Retry Mechanisms (Leveraging Cloud Tasks/Workflows)**
    - (Sub-tasks remain relevant, potentially enhanced by GCP capabilities)
    - **Sub-task 4.3.1: Define Granular Error Codes.** (Partially complete, refine for GCP services)
    - **Sub-task 4.3.2: Implement Retries for Transient Errors.**
        - Leverage Cloud Tasks queue retry policies.
        - Consider Cloud Workflows for more complex retry/error handling logic across multiple steps.
    - **Sub-task 4.3.3: Ensure Idempotency for Retried Operations.**

- **Task 4.4: Implement Multi-Step Orchestration with Cloud Workflows**
    - **Sub-task 4.4.1: Design Content Generation Workflow in Cloud Workflows YAML.**
        - Break down `EnhancedMultiStepContentGenerationService` into callable steps/microservices if necessary, or orchestrate calls to different parts of the API (which could be Cloud Run services invoked by Workflow).
        - Define states, transitions, error handling, and retries within the workflow definition.
    - **Sub-task 4.4.2: Integrate `JobManager` with Cloud Workflows.**
        - `JobManager` (or a Cloud Task handler triggered after initial job creation) triggers a Cloud Workflow execution.
        - Workflow updates job status in Firestore at key stages (e.g., by calling a small Cloud Run endpoint or using Firestore connector if available/suitable).
    - **Sub-task 4.4.3: Implement Callbacks or Polling for Workflow Completion.**
        - Cloud Workflows can call back to an HTTP endpoint on completion/failure, or `JobManager` can poll workflow status (less ideal for serverless).

### Execution Path 5: Scalability & Performance (GCP Focused)
**Goal**: Ensure the application can handle increasing load and perform efficiently using GCP's scalable services.

- **Task 5.1: Implement Robust Background Worker System with Cloud Tasks**
    - **Sub-task 5.1.1: Worker Technology Chosen: Cloud Tasks.** (Decision made as part of GCP architecture)
    - **Sub-task 5.1.2: Integrate Cloud Tasks for Job Processing.**
        - `JobManager`'s `create_job` method creates a job document in Firestore and then enqueues a task in Cloud Tasks.
        - The Cloud Task payload will contain the job ID.
        - Create an HTTP endpoint (e.g., on Cloud Run, potentially a separate service or specific endpoint) that Cloud Tasks will call to process the job. This endpoint will fetch job details from Firestore and execute the content generation logic (e.g., by calling `EnhancedMultiStepContentGenerationService`).
    - **Sub-task 5.1.3: Configure Cloud Tasks Queue.**
        - Set dispatch rates, max concurrent dispatches, retry policies via Terraform.
    - **Sub-task 5.1.4: Secure Cloud Tasks Invocation.**
        - Ensure only Cloud Tasks can invoke the worker HTTP endpoint (e.g., using OIDC authentication with the invoker service account for Cloud Tasks).

- **Task 5.2: Add Missing Job Parameters to `ContentRequest` (and through the system) - VERIFIED COMPLETE**
    - This task was completed in the "Enable End-to-End Testing" sprint.

- **Task 5.3: API Rate Limiting & Throttling using API Gateway**
    - **Sub-task 5.3.1: Configure Rate Limiting in API Gateway.**
        - Define rate limits (requests per minute/key) in the API Gateway configuration (OpenAPI spec or service definition).
        - Apply to job creation and potentially status polling endpoints.
        - Requires API Key management strategy (API Gateway can manage API keys).
    - **Sub-task 5.3.2: Test Rate Limiting.**

### Execution Path 6: Advanced Security (GCP Focused)
**Goal**: Harden the application using GCP security best practices and services.
- **Task 6.1: Secure Service-to-Service Communication.**
    - Use IAM and service accounts with least privilege for all GCP service interactions (Cloud Run to Firestore, Cloud Tasks to Cloud Run, etc.).
    - Leverage VPC Service Controls if appropriate for project complexity.
- **Task 6.2: API Security with API Gateway.**
    - Implement API key validation via API Gateway.
    - Consider JWT validation or other authentication mechanisms if needed.
    - Ensure HTTPS is enforced.
- **Task 6.3: Secret Management with Google Secret Manager.**
    - Ensure ALL secrets (API keys, database credentials, etc.) are stored in Secret Manager and accessed by Cloud Run via its service account.
- **Task 6.4: Vulnerability Scanning.**
    - Enable Artifact Registry vulnerability scanning for container images.
    - Consider Web Security Scanner for deployed Cloud Run services.
- **Task 6.5: Review IAM Permissions Regularly.**
    - Periodically audit service account permissions.

### Execution Path 7: Maintainability & Advanced Code Quality
**Goal**: Ensure the codebase is easy to understand, modify, and extend.
- **Task 7.1: Comprehensive Unit and Integration Tests.**
    - Increase test coverage, especially for interactions with GCP services (using emulators or mocks).
    - Test Cloud Workflow logic.
- **Task 7.2: Consistent Code Style and Linting.** (Already in place, maintain)
- **Task 7.3: Documentation Updates.**
    - Update `README.md` with new GCP setup, deployment, and local development instructions.
    - Document Terraform IaC.
    - Document Cloud Workflow definitions.
    - Update service architecture diagrams.
- **Task 7.4: CI/CD Pipeline Enhancements.**
    - Automate Terraform apply in CI/CD (e.g., GitHub Actions).
    - Automate container builds and pushes to Artifact Registry.
    - Automate Cloud Run deployments.
    - Include automated testing in the pipeline.

### Execution Path 8: Advanced Observability (GCP Focused)
**Goal**: Gain deep insights into application performance, errors, and usage patterns using GCP observability tools.
- **Task 8.1: Structured Logging.**
    - Implement structured logging (JSON) in the FastAPI application for better parsing in Cloud Logging.
    - Include trace IDs for request tracing across services.
- **Task 8.2: Custom Metrics & Dashboards in Cloud Monitoring.**
    - Define custom metrics for key application performance indicators (e.g., job processing time, error rates by type, queue lengths).
    - Create Cloud Monitoring dashboards to visualize these metrics.
- **Task 8.3: Alerting in Cloud Monitoring.**
    - Set up alerts for critical errors, high latency, resource exhaustion, and other important conditions.
- **Task 8.4: Distributed Tracing with Cloud Trace.**
    - Instrument the application to send traces to Cloud Trace, especially for requests involving multiple GCP services (API Gateway -> Cloud Run -> Cloud Tasks -> Cloud Run -> Firestore).

### Execution Path 9: Frontend Development
**Goal**: Develop a user interface for interacting with the content generation service.
- (Tasks remain as previously defined or to be detailed later, assuming this is primarily backend-focused for now)
- **Task 9.1: Basic UI for Job Submission and Status Tracking.**
- **Task 9.2: UI for Viewing Generated Content.**

### Execution Path 10: Cost-Effectiveness & Optimization (GCP Focused)
**Goal**: Ensure the application runs cost-effectively on GCP.
- **Task 10.1: Right-Sizing GCP Resources.**
    - Monitor Cloud Run instance performance and adjust CPU/memory settings.
    - Optimize Firestore usage (e.g., efficient queries, minimize document size).
- **Task 10.2: GCP Budgets and Cost Alerts.**
    - Set up GCP budgets and alerts to monitor spending.
- **Task 10.3: Review Service Tiers and Pricing Models.**
    - Choose appropriate service tiers (e.g., for Vertex AI models, API Gateway).
- **Task 10.4: Optimize Cloud Workflow Executions.**
    - Minimize unnecessary steps or expensive operations within workflows.

---
## Execution Path 11: Repository Cleanup & Test Alignment (Pre-GCP Focus)
**Goal:** Address immediate blockers related to leftover Flask artifacts, test suite failures, and code polish to ensure a stable base before deeper GCP integration and CI/CD setup.

- [ ] **Task EP11.1: Purge Flask Artifacts & Align Tests**
    - [ ] Remove Flask and Gunicorn from `requirements.txt` and `requirements-dev.txt`.
    - [ ] Update `tests/unit/test_app.py`:
        - [ ] Replace `from flask import Flask` with `from fastapi.testclient import TestClient`.
        - [ ] Point tests at `app.main.app` instead of the old `create_app()` factory.
        - [ ] Adapt existing tests or write new basic tests for FastAPI structure (e.g., health check, basic job submission).
    - [ ] Remove any other lingering Flask-specific import paths or code from the project.
- [ ] **Task EP11.2: Implement Pre-commit Hooks**
    - [ ] Create a basic `.pre-commit-config.yaml` including `black`, `ruff`, and `mypy`.
    - [ ] Install pre-commit and run `pre-commit install`.
    - [ ] Run `pre-commit run --all-files` to format and lint the existing codebase. Address any reported issues.
    - [ ] Prepare for CI integration of pre-commit checks.
- [ ] **Task EP11.3: Resolve Application Port & Potential Prometheus Collision**
    - [ ] Review current Uvicorn port configuration (default 8000).
    - [ ] If Prometheus metrics are exposed (or planned soon), ensure they use a different port (e.g., 9000).
    - [ ] Make the main application (Uvicorn) port configurable via an environment variable (e.g., `APP_PORT`) for flexibility.
- [ ] **Task EP11.4: Fix `settings.api_key` Slicing Bug**
    - [ ] Locate any instances of `settings.api_key[:10]` (likely in logging or debug output).
    - [ ] Wrap the slicing operation with a conditional check, e.g., `settings.api_key[:10] if settings.api_key else None`.
- [ ] **Task EP11.5: Add Flashcards Length Validation**
    - [ ] In `app/services/multi_step_content_generation.py` (or relevant Pydantic model for flashcard generation), add validation to ensure the number of flashcards is between 10 and 20 (inclusive) as per project rules.

---
## Task Group 11: Developer Experience & Tooling - COMPLETED

- [x] **Task 11.1: Implement Automated AI Context Dump** (2025-05-28)
  - [x] Create `generate_ai_context_dump.py` script... [AI-EXECUTION-SESSION-20250528]
  - [x] Internally validated script... [AI-EXECUTION-SESSION-20250528]
  - **Outcome/Notes:** Script `generate_ai_context_dump.py` created in project root.

---
## Path Interactions
(Remains as previously defined or to be reviewed)
- **Path 4 (Reliability) & Path 5 (Scalability)** are tightly coupled with the choice of GCP services (Firestore, Cloud Tasks, Workflows).
- **Path 6 (Security)** depends on IAM, Secret Manager, and API Gateway features.
- **Path 8 (Observability)** relies on Cloud Monitoring and Cloud Logging.

---
## Project Sessions

### Session 1: Initial Setup & Environment (2025-05-26) - COMPLETED
#### Completed Tasks
- [x] Task 1: Local Development Environment Setup [AI-EXECUTION-SESSION-20250526]
- [x] Task 2: GCP Project & Project Orchestration Setup [AI-EXECUTION-SESSION-20250526]
- [x] Task 3: Initial Project Structure [AI-EXECUTION-SESSION-20250527]

### Session 2: Core AI Integration (2025-05-27) - COMPLETED
#### Completed Tasks
- [x] Task 4: Initial AI Core Integration [AI-EXECUTION-SESSION-20250527]

### Session 3: MVP Enhancement (2024-06-09) - COMPLETED
#### Completed Tasks
- [x] Task 5: MVP Finalization & Testing [AI-EXECUTION-SESSION-20240609]
- [x] Task 5.1: Project Scope Update [AI-EXECUTION-SESSION-20240609]
- [x] Task 6: Content Generation Enhancement [AI-EXECUTION-SESSION-20240609]

### Session 4: Code Quality & Architecture (2024-06-09 - 2024-06-10) - COMPLETED
#### Completed Tasks
- [x] Task 7: Code Quality Improvements [AI-EXECUTION-SESSION-20240609]
- [x] Task 14: Codebase Modularization [AI-EXECUTION-SESSION-20240610]

### Session 5: Foundational Stability & Async Enablement (2025-05-27 - Recent) - COMPLETED
**Focus**: Settings consolidation, service strategy, dependency cleanup, enabling E2E async testing.
#### Completed Tasks (within this extended session period)
- [x] Task 1.5: Consolidate settings into single source of truth 
[AI-EXECUTION-SESSION-20250527]
- [x] Task 1.6: Remove default insecure `API_KEY` from settings 
[AI-EXECUTION-SESSION-20250527]
- [x] Task 1.7: Review and ensure all critical settings in `app/core/config/settings.py` 
are correctly defined [AI-EXECUTION-SESSION-20250528]
- [x] Task 1.8: Implement Google Secret Manager integration for sensitive settings 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 1.9: Add comprehensive Google-style docstrings (as part of 1.8) 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 2.1: Designate `EnhancedMultiStepContentGenerationService` as primary & 
Refactor API to use it [AI-EXECUTION-SESSION-20250528]
- [x] Task 2.2: Adapt API for Asynchronous Job-Based Workflow 
[AI-EXECUTION-SESSION-PREVIOUS]
- [x] Task 2.3: Refactor API Routers to be fully within `app/api/routes/` 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 3.1: Resolve `pytest` version conflict & standardize usage 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 3.2: Resolve `pydantic` & `pydantic-settings` versions (ensure Pydantic V2) 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 3.3: Clean up `requirements.txt` (move all dev dependencies) 
[AI-EXECUTION-SESSION-20250528]
- [x] Task 3.4: Full Review & Cleanup/Deletion of `backend/` directory 
[AI-EXECUTION-SESSION-PREVIOUS]
- [x] Task 11.1: Implement Automated AI Context Dump [AI-EXECUTION-SESSION-20250528]
- [x] All tasks under "NEW SPRINT FOCUS: Enable End-to-End Testing of Asynchronous Job System" (Tasks A, B, C)

#### In Progress Tasks (Current Sprint)
- Tasks under "CURRENT SPRINT FOCUS: Transition to GCP-Native Serverless Architecture" - Phase 1 are now active.

---
## Task Breakdown Instructions
(Remains as previously defined)

---
## Summary of Progress
(To be updated after GCP transition begins)

---
## Issues
(This section can be removed or repurposed as most items are now integrated into the 
Execution Paths above or SaaS Quality Enhancements Phase)

---
## Go Live Checklist
(Remains as previously defined or to be reviewed in context of GCP)
