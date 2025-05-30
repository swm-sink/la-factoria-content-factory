# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `python-json-logger` for structured JSON logging.
- Updated `app/main.py` to use `JsonFormatter`.
- Deprecation notice to `docs/DEPLOYMENT.md`.
- Notes about CI/CD automation to `docs/operational/deployment_checklist.md`.

### Changed
- Logging setup in `app/main.py` to use `python-json-logger`.

## [1.0.0-MVP-RC1] - 2025-05-30 
### Added
- PII avoidance instructions to all AI content generation prompts.
- Retry logic using `tenacity` for core AI model calls to improve resilience.
- Logging for token usage exceeding 80% or 100% of `max_total_tokens`.
- `google-cloud-storage`, `google-cloud-secretmanager`, `google-cloud-tasks`, `tenacity` to `requirements.txt`.
- Pip dependency caching to `backend-ci.yml`.
- `permissions: read-all` to CI workflow jobs (`backend-ci.yml`, `frontend-ci.yml`).
- Global API Key authentication to all `/api/v1/*` routes via `app/api/routes.py`.
- `/healthz` unauthenticated endpoint in `app/main.py` for GCP health checks.
- Health probes (startup and liveness) to Cloud Run service definition in `iac/modules/cloud_run_service/main.tf`, pointing to `/healthz`.
- `VITE_API_BASE_URL` environment variable usage in `frontend/src/api.ts`.
- Type definitions for `import.meta.env` in `frontend/src/vite-env.d.ts`.
- UI fields and payload parameters for `target_pages`, `use_parallel`, `use_cache` in `frontend/src/components/ContentGeneratorForm.tsx`.

### Changed
- Dockerfile and Nginx configuration to correctly run as non-root user, with Nginx listening on a configurable port (default 8080 via `${PORT}` env var from Cloud Run) and proxying to Uvicorn on an internal port (default 8000).
- `start.sh` to use `envsubst` for Nginx configuration and manage distinct Nginx/Uvicorn ports.
- Updated `README.md` with corrected Docker Compose access info, `tenacity` dependency, accurate API request examples for `/jobs`, and restored truncated content.
- Updated `docs/operational/deployment_checklist.md` with correct Secret Manager secret names.
- Updated `app/services/audio_generation.py` to upload generated audio to GCS and return a public URL.
- Updated `iac/main.tf` to correctly mount secrets as environment variables in Cloud Run, dynamically set `GCP_JOB_WORKER_ENDPOINT`, and use `var.image_tag`.
- Aligned Docker image name in `.github/workflows/build-push-docker.yml` to `acpf-mvp`.
- API integration tests in `tests/integration/test_api.py` rewritten to target `POST /api/v1/jobs` and mock `JobManager`.
- Enabled `gzip on;` in `docker/nginx/nginx.conf`.
- Extended title consistency Pydantic validation in `app/models/pydantic/content.py`.
- `app/core/config/settings.py` to load `CORS_ORIGINS` from environment and include `correlation_id` in `log_format`.

### Fixed
- Erroneous Python code injection in `faq_collection.md` and `flashcards.md` prompts.
- Hardcoded API key in `.env.example` (User action was required).
- Placeholder `openapi.yaml` updated with a basic structure including security schemes (User action required to replace with actual spec).

### Created
- Initial versions of `docs/learn-as-you-go.md`, `test/auto-validation.txt`, `reports/user-flow.summary`, `reports/error-analysis.md`.
- `.dockerignore` file.

### Security
- Applied API key authentication globally to `/api/v1` routes.
- Addressed hardcoded secret in `.env.example` (manual user fix was required).
- Updated Nginx to run as non-root user.
- Added `permissions: read-all` or more specific WIF permissions to GitHub Actions workflows.

## [0.1.0] - 2025-05-29
### Added
- Initial project structure.
- Core FastAPI backend with Pydantic models.
- Basic AI content generation service.
- Frontend setup with Vite and React.
- Dockerfile and Docker Compose for local development.
- Basic CI/CD workflows for linting and testing.
- Terraform IaC for GCP resources (Cloud Run, Firestore, etc.).
- Comprehensive project rules in `.cursor/rules/project.mdc`.

[Unreleased]: https://github.com/your-repo/ai-content-factory/compare/v1.0.0-MVP-RC1...HEAD
[1.0.0-MVP-RC1]: https://github.com/your-repo/ai-content-factory/compare/v0.1.0...v1.0.0-MVP-RC1
[0.1.0]: https://github.com/your-repo/ai-content-factory/tree/v0.1.0
