# Architecture Map

This document provides a high-level, simplified overview of the project's main components and how they interact.

## Core Backend Services (FastAPI - `app/` directory)

-   **API Routes (`app/api/routes/`)**:
    -   `auth.py`: Handles user registration, login (JWT generation), and `/users/me`.
    -   `jobs.py`: Manages asynchronous content generation jobs (creation, status polling). Interacts with `JobManager`.
    -   `feedback.py`: Handles user feedback submission for content.
    -   `worker.py`: Internal endpoint (`/internal/v1/process-generation-task`) for Cloud Tasks to trigger synchronous content generation.
-   **Services (`app/services/`)**:
    -   `multi_step_content_generation.py` (`EnhancedMultiStepContentGenerationService`): Orchestrates the main outline-driven content generation.
        -   Uses `PromptService` for loading AI prompts.
        -   Interacts with Vertex AI Gemini for text generation.
        -   Uses `text_cleanup.py` for grammar/style correction.
        -   Tracks token usage and costs.
    -   `prompts.py` (`PromptService`): Loads AI prompt templates from `.md` files located in `app/core/prompts/v1/`.
        -   *Note (Cleanup)*: Old Python-based prompt files (`app/core/prompts/v1/content_generation.py`, `app/core/prompts/v1/multi_step_prompts.py`) and the deprecated service `app/services/content_generation.py` have been removed.
    -   `audio_generation.py` (`AudioGenerationService`): Handles text-to-speech conversion (e.g., using ElevenLabs).
    -   `job_manager.py` (`JobManager`): Manages the lifecycle of content generation jobs, interacting with Firestore and Cloud Tasks.
    -   Other services for caching, progress tracking, quality metrics, etc.
-   **Core Components (`app/core/`)**:
    -   `config/settings.py`: Application configuration.
    -   `security/`: Handles password hashing, JWT token creation/validation.
    -   `prompts/v1/`: Directory containing `.md` prompt templates.
-   **Models (`app/models/pydantic/`)**: Pydantic models for API request/response validation and data structuring (e.g., `content.py`, `user.py`, `job.py`, `feedback.py`).
-   **Core Schemas (`app/core/schemas/`)**: Pydantic schemas primarily for job management (e.g., `job.py`).
-   **Models (`app/models/pydantic/`)**: Pydantic models for API request/response validation and content structures (e.g., `content.py`, `user.py`, `feedback.py`).

## Frontend (React - `frontend/` directory)

-   **API Client (`frontend/src/api.ts`):** Axios instance configured for backend communication. Includes interceptors for API key and JWT.
-   **Contexts (`frontend/src/contexts/`)**:
    -   `AuthContext.tsx`: Manages user authentication state, login/registration logic, token handling.
    -   `ErrorContext.tsx`: Provides global error message state.
-   **Components (`frontend/src/components/`)**: Reusable UI elements.
    -   `Auth/`: Login and Registration forms.
    -   `Content/ContentGeneratorForm.tsx`: Form for submitting content generation requests.
    -   `Job/JobStatusDisplay.tsx`: Displays status and results of generation jobs.
    -   `Content/ContentDisplay.tsx`: Displays generated content and includes feedback UI.
-   **Pages (`frontend/src/pages/`)**: Top-level views for different routes.
-   **Types (`frontend/src/types/content.ts`):** TypeScript interfaces for API data structures.

## Data Flow (Simplified for Content Generation)

1.  **User (Frontend)** submits syllabus via `ContentGeneratorForm.tsx`.
2.  **Frontend** sends request to `POST /api/v1/jobs` (FastAPI backend).
3.  **`jobs.py` (API Route)** uses `JobManager` to:
    a.  Create a job record in Firestore (status: PENDING).
    b.  Enqueue a task to Google Cloud Tasks, pointing to the internal worker endpoint (`POST /internal/v1/process-generation-task`).
    c.  Returns job ID and initial status to Frontend.
4.  **Frontend** (e.g., `JobStatusPage.tsx`) **polls** `GET /api/v1/jobs/{job_id}` for updates (not using Server-Sent Events (SSE) in current MVP).
5.  **Google Cloud Task** triggers `POST /internal/v1/process-generation-task` (FastAPI `worker.py`).
6.  **`worker.py`** fetches job details from Firestore, then calls `EnhancedMultiStepContentGenerationService`.
7.  **`EnhancedMultiStepContentGenerationService`**:
    a.  Generates master `ContentOutline` using `PromptService` and Vertex AI.
    b.  Generates derivative content types (podcast script, study guide, etc.) in parallel, using the master outline and specific prompts via `PromptService` and Vertex AI.
    c.  Applies grammar/style correction.
    d.  Aggregates results into `GeneratedContent` model.
8.  **`worker.py`** validates the `GeneratedContent` and updates the job record in Firestore with results and status (COMPLETED/FAILED).
9.  **Frontend** polling eventually shows completed status and displays results.
10. **User (Frontend)** can submit feedback via `ContentDisplay.tsx` to `POST /api/v1/feedback/content/{content_id}/feedback`.
11. **`feedback.py` (API Route)** stores feedback in Firestore.

---
