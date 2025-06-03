# AI Content Factory - Architecture Overview

**⚠️ CURRENT STATUS: In Development - Significant Issues Remain ⚠️**

This document provides a high-level overview of the AI Content Factory's architecture. For a more detailed, dynamically updated map of components and data flows, please refer to [`docs/architecture-map.md`](./architecture-map.md). The comprehensive architectural principles, patterns, and technology stack are defined in the project's single source of truth for rules: `/.cursor/rules/project.mdc`.

**For the latest project status and known issues, please see [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md).**

## Core Philosophy

The application is built with a modular, scalable, and maintainable design, emphasizing a clear separation of concerns. It leverages a modern tech stack centered around Python (FastAPI) for the backend, React/TypeScript for the frontend, and Google Cloud Platform (GCP) for serverless deployment and services.

## Key Architectural Aspects

1.  **Outline-Driven Content Generation:**
    *   The core AI functionality revolves around first generating a master content outline from user input.
    *   This outline then serves as the foundation for generating various derivative content types (podcast scripts, study guides, etc.) in parallel.
    *   This approach ensures consistency and modularity in content creation.

2.  **Asynchronous Job Processing:**
    *   Content generation tasks are handled as asynchronous jobs.
    *   The system uses Google Cloud Firestore for job persistence and Google Cloud Tasks for queuing and triggering job execution.
    *   This allows the API to respond quickly to user requests while long-running generation tasks are processed in the background.

3.  **Service-Oriented Backend (`app/`):**
    *   **API Layer (`app/api/routes/`):** Exposes RESTful endpoints for frontend interaction (e.g., job creation, status polling, user authentication, feedback).
    *   **Service Layer (`app/services/`):** Encapsulates business logic, including:
        *   `EnhancedMultiStepContentGenerationService`: Orchestrates the AI content generation pipeline.
        *   `JobManager`: Manages the lifecycle of asynchronous jobs.
        *   `PromptService`: Loads and manages AI prompt templates from external files.
        *   Services for audio generation, text cleanup, etc.
    *   **Core Components (`app/core/`):** Provides shared utilities for configuration (`settings.py`), security (JWTs, hashing), and externalized AI prompts (`app/core/prompts/v1/`).
    *   **Data Models (`app/models/pydantic/`):** Pydantic models define the structure for API requests/responses and internal data, ensuring validation and type safety.

4.  **React Frontend (`frontend/`):**
    *   Provides the user interface for submitting content generation requests, managing jobs, viewing results, and providing feedback.
    *   Uses TypeScript for type safety and modern React features (Context API, hooks) for state management.

5.  **GCP Native Deployment:**
    *   **Cloud Run:** Hosts the containerized FastAPI application.
    *   **Firestore:** Provides a NoSQL database for job persistence and other application data.
    *   **Cloud Tasks:** Manages the asynchronous execution of content generation tasks.
    *   **Secret Manager:** Securely stores API keys and other sensitive configurations.
    *   **Artifact Registry:** Stores Docker container images.
    *   **API Gateway:** (Optional, for managing API access, rate limiting, etc.)
    *   **Cloud Workflows:** (For orchestrating more complex multi-step processes, if needed).

6.  **Infrastructure as Code (IaC):**
    *   Terraform (`iac/`) is used to define and manage all GCP resources, ensuring reproducible and version-controlled infrastructure.

7.  **CI/CD:**
    *   GitHub Actions (`.github/workflows/`) automate testing, linting, Docker image building, and deployment to GCP.

## Further Details

For specific details on:
-   **Technology Stack:** See Section B in `/.cursor/rules/project.mdc`.
-   **Coding Standards & Style:** See Section C in `/.cursor/rules/project.mdc`.
-   **Detailed Architectural Principles & Patterns:** See Section D in `/.cursor/rules/project.mdc`.
-   **Security Mandates:** See Section E in `/.cursor/rules/project.mdc`.
-   **Project File Structure:** See Section F in `/.cursor/rules/project.mdc` and `README.md`.
-   **Testing Philosophy:** See Section G in `/.cursor/rules/project.mdc`.
-   **Error Handling & Resilience:** See Section H in `/.cursor/rules/project.mdc`.
-   **Deployment Process:** See `docs/DEPLOYMENT.md` and relevant CI/CD workflow files.

This document aims to provide a starting point for understanding the system's architecture. Always refer to `/.cursor/rules/project.mdc` and `docs/architecture-map.md` for the most current and detailed information.
