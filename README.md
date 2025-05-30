# AI Content Factory

## Overview

The AI Content Factory is a web application designed to generate various types of educational content using AI. It leverages Google's Vertex AI for content generation and ElevenLabs for text-to-speech conversion. The application is built with a React frontend and a FastAPI backend.

This project aims to provide a modular, scalable, and easy-to-use platform for creating:
- Content Outlines
- Podcast Scripts
- Study Guides
- One-Pager Summaries
- Detailed Reading Materials
- FAQs
- Flashcards
- Reading Guide Questions

## Features

- **Versatile Content Generation**: Create a wide range of educational materials from a single topic.
- **AI-Powered**: Utilizes state-of-the-art AI models for high-quality content.
- **Text-to-Speech**: Convert generated text content into natural-sounding audio.
- **Secure API**: Endpoints protected by API key authentication.
- **Modular Architecture**: Separated frontend and backend services for better maintainability and scalability.
- **Containerized**: Dockerized for easy setup and deployment.
- **CI/CD**: GitHub Actions for automated linting, testing, building, and deployment.
- **Asynchronous Job Processing**: Utilizes Firestore and Cloud Tasks for scalable, asynchronous content generation jobs.

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Zustand, React Router, Axios
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic
- **AI Services**: Google Vertex AI (Gemini), ElevenLabs (or Google Cloud TTS)
- **Cloud Platform**: Google Cloud Platform (Cloud Run, Firestore, Cloud Tasks, Secret Manager, Artifact Registry, API Gateway, Workflows)
- **Containerization**: Docker, Docker Compose
- **Infrastructure as Code (IaC)**: Terraform
- **CI/CD**: GitHub Actions
- **Linting/Formatting**: Flake8, Black, MyPy (Python); ESLint, Prettier (Frontend)
- **Retry Logic**: Tenacity (for resilient API calls to AI services)
- **Task Management**: YAML-based atomic tasks, Markdown for meta-tasks and details.

## Project Structure

```
.                           # Project Root
├── .cursor/                # Cursor AI assistant rules and configuration
│   └── rules/
│       └── project.mdc     # Core project rules for AI interaction
├── .github/                # GitHub specific files
│   └── workflows/          # CI/CD pipeline definitions
├── app/                    # FastAPI backend application
│   ├── __init__.py
│   ├── api/                # API layer: routes and dependencies
│   │   ├── routes/         # Modular route definitions (jobs, worker, auth, etc.)
│   │   └── routes.py       # (If used as an aggregator)
│   ├── core/               # Core components (config, security, prompts, exceptions)
│   │   ├── config/
│   │   ├── prompts/
│   │   ├── schemas/        # Pydantic schemas (e.g., app/core/schemas/job.py)
│   │   └── security/
│   ├── models/             # Data models
│   │   └── pydantic/       # Pydantic models for API requests, responses, content structures (e.g., content.py, user.py, feedback.py)
│   ├── services/           # Business logic (content generation, job management)
│   │   └── job/
│   ├── utils/              # Utility functions
│   └── main.py             # FastAPI application entrypoint
├── docker/                 # Docker-related files (e.g., nginx config)
│   └── nginx/
├── docs/                   # Project documentation (architecture, deployment, operational guides)
├── frontend/               # React frontend application (if applicable)
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
├── iac/                    # Infrastructure as Code (Terraform)
│   ├── modules/            # Reusable Terraform modules
│   └── main.tf             # Root Terraform configuration
├── memory/                 # AI operational guidelines
│   └── guidelines.md
├── scripts/                # Utility scripts (e.g., local run scripts)
├── tasks/                  # Authoritative task management system
│   ├── atomic_tasks.yaml   # AI-executable tasks
│   ├── meta_tasks.md       # High-level goals and sprints
│   └── task_details.md     # Detailed context for atomic tasks
├── tests/                  # Automated tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example            # Example environment variables
├── .gitignore
├── Dockerfile              # Root Dockerfile (multi-stage)
├── docker-compose.yml      # Docker Compose for local development
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── start.sh                # Container startup script
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ and npm (for frontend development if not using Docker for frontend)
- Access to Google Cloud Platform with Vertex AI API enabled.
- An ElevenLabs API key.

### Setup Environment Variables

1.  Copy `.env.example` (from the project root) to a new file named `.env` in the **project root**:
    ```bash
    cp .env.example .env
    ```
2.  Update `.env` with your actual API keys and GCP project ID. Key variables include:
    - `API_KEY`: A secure, unique key you define for clients to access *this application's* API.
    - `GCP_PROJECT_ID`: Your Google Cloud Project ID.
    - `ELEVENLABS_API_KEY`: Your API key from ElevenLabs (if using ElevenLabs for TTS).
    - `JWT_SECRET_KEY`: A long, random string for signing JWTs (if auth is enabled).
    - `SENTRY_DSN` (Optional): For error tracking with Sentry.
    - `APP_PORT`: Port for the backend API server (default 8080).
    Refer to `app/core/config/settings.py` for a complete list and descriptions. These can also be loaded from Google Secret Manager in a GCP environment.

### Local Development (using Docker Compose)

This is the recommended way to run the application locally.

1.  **Ensure Docker Desktop is running.**
2.  **Build and run the services:**
    From the project root directory:
   ```bash
    docker-compose up --build
    ```
    - The application (served by Nginx, proxying to FastAPI) will be available based on your `docker-compose.yml` port mapping. Typically, if `docker-compose.yml` maps `"8080:8080"`, it will be `http://localhost:8080`.
    - Nginx inside the container listens on the port specified by the `NGINX_PORT` environment variable (default 8080, which is also the default `APP_PORT` for backend settings).

3.  **Accessing the application:**
    - Application UI: Open `http://localhost:YOUR_MAPPED_PORT` (e.g., `http://localhost:8080`) in your browser.
    - Backend API Docs (Swagger UI): `http://localhost:YOUR_MAPPED_PORT/docs` (e.g., `http://localhost:8080/docs`).

### Local Development (Manual - Backend)

If you prefer to run the backend directly without Docker:

1.  **Navigate to the project root directory.** (The application `app/` is at the root).
2.  **Create and activate a virtual environment:**
   ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3.  **Install dependencies:**
   ```bash
   pip install -r requirements.txt
    ```
4.  **Ensure your root `.env` file is configured.**
5.  **Run the FastAPI development server:**
    From the project root directory:
   ```bash
    uvicorn app.main:app --reload --port ${APP_PORT:-8080} 
    ```
    (Ensure `APP_PORT` is set in your environment or `.env` file, or it defaults to the value in `app/core/config/settings.py`, typically 8080)

### Local Development (Manual - Frontend)

(Instructions remain similar if frontend exists and is developed separately)

1.  **Navigate to the `frontend` directory.**
2.  **Install dependencies:**
   ```bash
    npm install
   ```
3.  **Run the Vite development server:**
```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173` (or another port). Ensure its proxy settings in `vite.config.ts` point to your running backend API (e.g., `http://localhost:8080`).

## API Usage

Most API endpoints under `/api/v1/` require an `X-API-Key` header for authentication, as defined in `app.core.config.settings.API_KEY`.
Endpoints under `/api/v1/auth/` (for registration and login) do not require this API key.
The root `/healthz` endpoint (for GCP health checks) also does not require an API key.

### Core Endpoints

-   **`POST /api/v1/jobs`**: Creates a new asynchronous content generation job.
    -   **Request Body** (conforms to `ContentRequest` model from `app/models/pydantic/content.py`):
        ```json
        {
          "syllabus_text": "Detailed topic on the principles of quantum mechanics for beginners.",
          "target_format": "podcast_script",
          "target_duration": 10,
          "target_pages": null,
          "use_parallel": true,
          "use_cache": true
        }
        ```
    -   **Response Body** (conforms to `Job` model from `app/core/schemas/job.py`, status `pending`):
        ```json
        {
          "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
          "status": "pending",
          "created_at": "2024-07-27T10:00:00Z",
          "updated_at": "2024-07-27T10:00:00Z",
          "completed_at": null,
          "error": null,
          "progress": null,
          "result": null,
          "metadata": {
            "syllabus_text": "Detailed topic on the principles of quantum mechanics for beginners.",
            "target_format": "podcast_script",
            "target_duration": 10,
            "target_pages": null,
            "use_parallel": true,
            "use_cache": true
          }
        }
        ```

-   **`GET /api/v1/jobs/{job_id}`**: Retrieves the status and results of a specific job.
    -   **Response Body** (conforms to `Job` model, example if completed. The `result` field will contain the `GeneratedContent` structure from `app/models/pydantic/content.py`):
        ```json
        {
          "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
          "status": "completed",
          "created_at": "2024-07-27T10:00:00Z",
          "updated_at": "2024-07-27T10:05:00Z",
          "completed_at": "2024-07-27T10:05:00Z",
          "error": null,
          "progress": {
            "current_step": "Content generation complete",
            "total_steps": 5,
            "completed_steps": 5,
            "percentage": 100.0,
            "estimated_time_remaining": 0.0
          },
          "result": {
            "content_outline": { /* ... outline data ... */ },
            "podcast_script": { /* ... podcast script data ... */ },
            "study_guide": { /* ... study guide data ... */ },
            "faqs": { /* ... faqs data ... */ }
            // ... other generated content types as per app/models/pydantic/content.py ...
          },
          "metadata": { /* ... original request metadata ... */ }
        }
        ```

-   **`GET /api/v1/health`**: Health check endpoint for the backend API. Returns `{"status": "healthy"}`. (Note: This endpoint might be in `app/api/routes/content.py` or a dedicated health route).

(Other endpoints like user authentication (`/api/v1/auth/`) and feedback (`/api/v1/feedback/`) exist. Refer to API documentation or source code for full details.)

## Running Tests

### Backend Tests

1.  **Navigate to the project root directory.**
2.  Ensure you have a virtual environment activated with test dependencies installed (`pip install -r requirements-dev.txt` if a separate dev requirements file exists, or from `requirements.txt`).
3.  Run pytest:
```bash
pytest
```
    Or to target specific tests:
    ```bash
    pytest tests/unit/
    pytest tests/integration/
    ```

### Frontend Tests (Vitest)

(If frontend is part of the current scope)
1.  Navigate to the `frontend` directory.
2.  Run Vitest:
```bash
    npm test
    ```

## Linting and Type Checking

### Backend (Flake8, Black, MyPy)

From the project root directory:

```bash
ruff check app/
black --check app/
mypy app/
```
(Consider using `pre-commit` for automated checks - see `DEV-6.3` task)

### Frontend (ESLint & Prettier)

(If frontend is part of the current scope)
From the `frontend` directory:
```bash
npm run lint
npm run format # To check formatting with Prettier, or format:check if you have a specific check script
```

### Pre-commit Hooks

This project uses pre-commit hooks to automatically lint and format code before committing.

**Backend (Python):**
- Uses `pre-commit` with configurations in `.pre-commit-config.yaml`.
- Runs tools like Black (formatter), Ruff (linter), and Mypy (type checker) on staged Python files.
- **Setup:**
  ```bash
  pip install pre-commit
  pre-commit install
  ```
  This installs the hooks into your local `.git/hooks` directory.

**Frontend (TypeScript/React):**
- Uses `husky` and `lint-staged`.
- Runs ESLint (linter/fixer) and Prettier (formatter) on staged `.ts` and `.tsx` files.
- **Setup:**
  The hooks are automatically set up when you install dependencies in the `frontend` directory due to the `prepare` script in `frontend/package.json`:
  ```bash
  cd frontend
  npm install
  ```
  This configures Husky to run `lint-staged` on pre-commit.

## Deployment

Deployment is managed via GitHub Actions workflows that build Docker images, push them to Google Artifact Registry, apply Terraform configurations, and deploy to Google Cloud Run. Refer to `.github/workflows/` and `iac/` directories for details.

Key deployment files:
- `Dockerfile`: Defines the multi-stage Docker build.
- `iac/`: Contains Terraform configurations for all GCP resources.
- `.github/workflows/build-push-docker.yml`: Builds and pushes Docker image.
- `.github/workflows/terraform-apply.yml`: Applies Terraform changes.
- `.github/workflows/deploy-cloud-run.yml`: Deploys to Cloud Run.

## Contributing

Contributions are welcome! Please follow standard fork-and-pull-request workflow. Ensure your code adheres to linting and testing standards. Update relevant documentation and task files (`tasks/atomic_tasks.yaml`) with your changes.

## License

(To be determined - e.g., MIT License. A `LICENSE` file should be added.)

## Environment Variables

The application uses Pydantic Settings management, loading variables from environment variables, a `.env` file, and potentially Google Secret Manager. Create a `.env` file in the project root by copying `.env.example`.

**Key Environment Variables (refer to `app/core/config/settings.py` for the full list and descriptions):**

```bash
# Application API Key (for clients accessing this API)
API_KEY="your_strong_unique_api_key_for_clients"

# Google Cloud Platform (GCP) Settings
GCP_PROJECT_ID="your-gcp-project-id"  # Required for GCP services including Secret Manager
GCP_LOCATION="us-central1"      # Default GCP region

# AI Service API Keys (Loaded from GSM if GCP_PROJECT_ID is set, otherwise from Env)
ELEVENLABS_API_KEY="your_elevenlabs_api_key" # Required if using ElevenLabs TTS

# JWT Authentication (Loaded from GSM if GCP_PROJECT_ID is set, otherwise from Env)
JWT_SECRET_KEY="your_very_long_and_random_jwt_secret_key_at_least_32_chars" # For signing access tokens

# Optional: Sentry for error tracking (Loaded from GSM if GCP_PROJECT_ID is set, otherwise from Env)
SENTRY_DSN="your_sentry_dsn_if_using_sentry"

# Development & Operational Settings
APP_PORT=8080 # Port for Uvicorn locally (Note: Nginx listens on NGINX_PORT, Uvicorn on APP_PORT_UVICORN internally in Docker)
LOG_LEVEL="INFO" # DEBUG, INFO, WARNING, ERROR
# ... other settings like database URLs, Redis URLs, model names can be found in settings.py
```
**Note on Secrets:** In a deployed GCP environment, sensitive values like `API_KEY`, `ELEVENLABS_API_KEY`, and `JWT_SECRET_KEY` should be stored in Google Secret Manager and will be loaded automatically by the application if `GCP_PROJECT_ID` is configured. For local development, they can be set in the `.env` file.

### Manual Testing Steps & Local Setup Notes

1. **Create `.env` File:** Copy `.env.example` to `.env` in the project root and populate with your values.
2. **Python Version:** Ensure Python 3.11+ is used.
3. **Pre-commit Hooks:** It's recommended to install and use pre-commit hooks:
   ```bash
   # For backend hooks (run from project root)
   pip install pre-commit
   pre-commit install
   # For frontend hooks (run from frontend directory, if not already done by npm install)
   # cd frontend
   # npx husky install # Generally handled by "npm install" via "prepare" script
   ```
4. **Docker for Local Dev:**
   ```bash
   docker-compose up --build -d
   ```
   The application UI will typically be available at `http://localhost:8080` (if your `docker-compose.yml` maps host port 8080 to the container's `NGINX_PORT` which defaults to 8080).
   Swagger Docs: `http://localhost:8080/docs` (assuming the same port mapping).