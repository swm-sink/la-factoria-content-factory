# Changelog

All notable changes to the AI Content & Podcast Factory MVP will be documented in this file.

## [0.3.0] - 2025-05-28 (Foundational Refactoring & Enhancements)

### Added
- **Settings Management & Security**:
  - Consolidated all application settings into a single source of truth (`app/core/config/settings.py`) using Pydantic V2.
  - Implemented loading of sensitive settings (API keys) from Google Secret Manager, with a fallback to environment variables.
  - Removed insecure default API keys and enforced mandatory API key validation.
  - Added robust validation for critical settings (Gemini model name, API prefix, ElevenLabs Voice ID, GCP Project ID).
- **API & Routing**:
  - Refactored API routing to be modular, with endpoint logic moved from `app/main.py` to `app/api/routes/content.py`.
  - Centralized API router aggregation in `app/api/routes.py`.
  - Ensured consistent usage of the API version prefix (`/api/v1`) from settings.
  - Cleaned up `app/main.py` to focus on application setup and top-level router inclusion.
- **Service Strategy**:
  - Formally designated `EnhancedMultiStepContentGenerationService` as the primary service for the main content generation endpoint (`/api/v1/generate-content`).
  - Deprecated the older, simpler `ContentGenerationService`.
  - Created `app/core/docs/service_architecture.md` to document service roles.
- **Dependency Management**:
  - Resolved version conflicts for `pytest` and `pydantic-settings`.
  - Standardized `pytest` usage, ensuring it's only in development dependencies (`requirements-dev.txt`).
  - Cleaned `requirements.txt` to primarily contain production runtime dependencies, moving relevant development tools to `requirements-dev.txt`.
- **Developer Experience**:
  - Created `generate_ai_context_dump.py` script to automate the generation of `ai_context_dump.md` for providing context to LLMs.
- **Asynchronous Job System**:
  - Implemented a robust asynchronous job system for long-running content generation tasks.
  - Added job management endpoints for creating, monitoring, and managing content generation jobs.
  - Created Pydantic models for job status tracking, progress monitoring, and error handling.
  - Integrated job system with the existing content generation service.
  - Added background job processing with real-time progress updates.

### Changed
- **Error Handling**: Defined a `JobErrorCode` Enum in `app/core/schemas/job.py` for more granular job error reporting. The `JobError` model now uses this enum for its `code` field. `JobManager` has been updated to use initial set of these codes.
- **Job Creation**: The `/jobs` endpoint for creating new asynchronous jobs now accepts a `ContentRequest` payload directly, mirroring the synchronous content generation endpoint, instead of a generic metadata dictionary. The `JobManager` service has been updated to process this `ContentRequest` to perform content generation.
- **Settings Loading**: Application now attempts to load secrets from Google Secret Manager before falling back to environment variables.
- **API Structure**: Endpoints are now served via a more organized router structure within `app/api/`.
- **Logging**: Improved logging in settings loading and `app/main.py`.
- **Backend Structure & Docker Configuration (Major Refactor)**:
    - Consolidated all backend Python code from the legacy `backend/app/` directory into the unified `app/` directory at the project root.
    - Updated the root `Dockerfile` to build the application from the `app/` directory, including multi-stage builds for frontend and backend.
    - Modified `docker-compose.yml` to reflect the new application structure, removing references to the old `backend/` service and adjusting volume mounts and build context to use the root `Dockerfile` and the `app/` directory.

### Fixed
- Corrected inconsistent `pytest` versions between production and development requirements.
- Aligned `pydantic-settings` versions.

### Removed
- Redundant settings files (`backend/app/core/config.py`, `backend/app/core/settings.py`, `app/core/config/config.py`).
- `pytest` and other development-specific dependencies from the production `requirements.txt`.
- The entire `backend/` directory structure and its contents, following a backup to `backend_backup/`.
- All `__pycache__` directories and `.pyc` files from the `app/` directory structure to ensure a clean state after refactoring.

## [0.2.0] - 2024-06-09

### Added
- Expanded content generation capabilities:
  - Content outline generation as the primary structure
  - One-pager summaries for quick reference
  - Detailed reading materials for in-depth study
  - FAQs for common questions and misconceptions
  - Flashcards for key terms and concepts
  - Reading guide questions for critical thinking
- Enhanced Gemini prompt engineering for structured JSON output
- Improved error handling with detailed error messages
- Token usage and cost tracking for Gemini API calls
- Modular code structure with helper functions
- Comprehensive test coverage for new content types

### Changed
- Refactored `/generate-content` endpoint to return all content types
- Updated API response structure to include all generated content
- Enhanced error responses to include partial content when available
- Improved logging with token usage metrics

## [0.1.0] - 2024-02-19

### Added
- Initial MVP release with core functionality
- Flask application with `/generate-content` endpoint
- Integration with Vertex AI Gemini for content generation
- Integration with ElevenLabs for text-to-speech conversion
- Docker containerization with optimized Dockerfile
- Basic unit tests with pytest
- Comprehensive error handling and logging
- Input validation for API endpoints
- Environment variable configuration for API keys

### Known Issues
- Audio files are stored temporarily (to be moved to Cloud Storage) - *Partially addressed by planning for GCS in settings, but implementation pending.*
- No authentication/authorization implemented
- Limited error recovery for external API failures - *Improved by retry planning, but full implementation pending.*
- No rate limiting or request throttling - *Planned in SaaS enhancements.*
- No monitoring or alerting setup - *Basic Prometheus metrics exist, advanced setup pending.*

### Security Notes
- Sensitive configuration now managed via Google Secret Manager or environment variables.
- No authentication required for MVP endpoints. 