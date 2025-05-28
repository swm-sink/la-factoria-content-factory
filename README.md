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
- **CI/CD**: GitHub Actions for automated linting, testing, and type checking.

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, React Query, Axios
- **Backend**: Python, FastAPI, Uvicorn, Pydantic
- **AI Services**: Google Vertex AI (Gemini/PaLM), ElevenLabs
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Linting/Formatting**: Flake8, MyPy, ESLint, Prettier (to be configured for frontend)

## Project Structure

```
.                           # Project Root
├── .github/workflows/      # GitHub Actions CI workflows
│   └── ci.yml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core/             # Core components (config, security)
│   │   ├── models/           # Pydantic models
│   │   ├── routers/          # API routers (endpoints)
│   │   ├── services/         # Business logic (content/audio generation)
│   │   ├── tests/            # Backend tests
│   │   └── main.py           # FastAPI application entrypoint
│   ├── .env.example        # Example environment variables for backend
│   ├── Dockerfile          # Dockerfile for the backend service
│   └── pytest.ini          # Pytest configuration
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .env.example        # Example environment variables for frontend (if any)
│   ├── Dockerfile          # Dockerfile for frontend (if built separately)
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── storage/                  # Local storage for generated files (e.g., audio, history JSON)
│   ├── audio/
│   └── history.json
├── .env.example              # Root example environment variables (can be consolidated)
├── .gitignore
├── Dockerfile                # Root Dockerfile (multi-stage for building frontend & backend)
├── docker-compose.yml        # Docker Compose for local development
├── README.md                 # This file
├── requirements.txt          # Python dependencies for backend
└── tasks.md                  # Project task tracking
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ and npm (for frontend development if not using Docker for frontend)
- Access to Google Cloud Platform with Vertex AI API enabled.
- An ElevenLabs API key.

### Setup Environment Variables

1.  **Backend**: Navigate to the `backend` directory.
    Copy `.env.example` to a new file named `.env`:
    ```bash
    cp backend/.env.example backend/.env
    ```
    Update `backend/.env` with your actual API keys and GCP project ID:
    - `API_KEY`: A secure, unique key you create for accessing your API.
    - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID.
    - `ELEVENLABS_API_KEY`: Your API key from ElevenLabs.

    *Note: The root `.env.example` can also be used, ensure your `docker-compose.yml` or run configurations point to the correct `.env` file.*

### Local Development (using Docker Compose)

This is the recommended way to run the application locally.

1.  **Ensure Docker Desktop is running.**
2.  **Build and run the services:**
    From the project root directory:
   ```bash
    docker-compose up --build
    ```
    - The backend API will be available at `http://localhost:8000`.
    - The frontend (served by Nginx via the backend service) will be available at `http://localhost:80` (or a port you map in `docker-compose.yml` if 80 is taken).

3.  **Accessing the application:**
    - Frontend: Open `http://localhost` (or your mapped port) in your browser.
    - Backend API Docs (Swagger UI): `http://localhost:8000/docs`

### Local Development (Manual - Backend)

If you prefer to run the backend directly without Docker:

1.  **Navigate to the `backend` directory.**
2.  **Create and activate a virtual environment:**
   ```bash
    python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3.  **Install dependencies:**
   ```bash
   pip install -r requirements.txt
    ```
4.  **Ensure your `backend/.env` file is configured.**
5.  **Run the FastAPI development server:**
    From the `backend` directory:
   ```bash
    uvicorn app.main:app --reload --port 8000
    ```

### Local Development (Manual - Frontend)

If you prefer to run the frontend directly using Vite's dev server:

1.  **Navigate to the `frontend` directory.**
2.  **Install dependencies:**
   ```bash
    npm install
   ```
3.  **Run the Vite development server:**
```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173` (or another port if 5173 is busy). The Vite server is pre-configured to proxy API requests to `http://localhost:8000/api` (assuming your backend is running there).

## API Usage

All API endpoints require an `X-API-Key` header for authentication.

### Endpoints

-   **`POST /api/generate-content`**: Generates content based on the request body.
    -   **Request Body** (example):
        ```json
        {
          "topic": "Photosynthesis",
          "content_type": "study_guide", // e.g., study_guide, podcast, summary
          "target_audience": "high school students",
          "length": "medium", // e.g., short, medium, long
          "generate_audio": true // Optional, defaults to false
        }
        ```
    -   **Response Body** (example):
        ```json
        {
          "content": {
            "outline": "...",
            "podcast_script": "...",
            "study_guide": "...",
            // ... other content types
          },
          "audio_url": "/storage/audio/your_audio_file.mp3" // If audio was generated
        }
        ```

-   **`GET /api/content-history`**: Retrieves a paginated list of previously generated content.
    -   Query Parameters: `skip` (int, default 0), `limit` (int, default 10)

-   **`GET /api/content/{content_id}`**: Retrieves specific content by its ID.

-   **`DELETE /api/content-history/{content_id}`**: Deletes a specific content entry.

-   **`GET /health`**: Health check endpoint for the backend API.

## Running Tests

### Backend Tests

1.  Navigate to the `backend` directory.
2.  Ensure you have a virtual environment activated with test dependencies installed (pytest, httpx).
3.  Run pytest:
```bash
pytest
```
    Or from the root directory:
    ```bash
    pytest backend/app/tests
    ```

### Frontend Tests (Vitest)

1.  Navigate to the `frontend` directory.
2.  Run Vitest:
```bash
    npm test
    ```

## Linting and Type Checking

### Backend (Flake8 & MyPy)

From the project root or `backend` directory:

```bash
flake8 backend/app
mypy backend/app
```

### Frontend (ESLint)

From the `frontend` directory:

```bash
npm run lint
```

## Deployment

Detailed deployment instructions (e.g., to Google Cloud Run) will be added here.

### Basic Docker Deployment Steps

1.  **Build the Docker image:**
```bash
docker build -t ai-content-factory .
```
2.  **Run the Docker container:**
    (Ensure you provide necessary environment variables, e.g., by adapting the `docker-compose.yml` env_file or using `docker run -e ...`)
```bash
    docker run -p 80:80 -p 8000:8000 --env-file backend/.env ai-content-factory
```
    This assumes the root `Dockerfile` is configured to serve both frontend and backend (e.g., with Nginx and Uvicorn).

## Contributing

Contributions are welcome! Please follow standard fork-and-pull-request workflow.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details (though a LICENSE file hasn't been created yet).

## Environment Variables

The following environment variables are required for the application to function properly. Create a `.env` file in the project root with these variables:

```bash
# API Authentication
API_KEY=your-api-key-here  # Required: API key for authenticating requests

# Google Cloud Platform (GCP) Settings
GCP_PROJECT_ID=your-project-id  # Required: Your Google Cloud project ID
GCP_LOCATION=us-central1  # Optional: Default GCP region for AI services

# AI Service Settings
GEMINI_MODEL_NAME=gemini-pro  # Optional: Default AI model to use
ELEVENLABS_API_KEY=your-elevenlabs-key  # Required if using audio generation

# Content Generation Settings
MAX_TOKENS_PER_CONTENT_TYPE={"guide": 4000, "article": 2000}  # Optional: Token limits per content type
MAX_TOTAL_TOKENS=10000  # Optional: Maximum total tokens per generation
MAX_GENERATION_TIME=90  # Optional: Maximum time in seconds for generation
MAX_RETRIES=3  # Optional: Maximum number of retries for failed operations
RETRY_DELAY=2  # Optional: Delay in seconds between retries

# Development Settings
DEBUG=false  # Optional: Enable debug mode
LOG_LEVEL=INFO  # Optional: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

### Manual Testing Steps

1. **Create `.env` File**
   - Copy the environment variables above into a `.env` file in the project root
   - Fill in your actual values for `API_KEY`, `GCP_PROJECT_ID`, and `ELEVENLABS_API_KEY`

2. **Python 3.13 Local Development Note**
   - If testing locally with Python 3.13, you may encounter a `pydantic-core` build issue
   - Workaround: Set `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` before running tests:
     ```bash
     export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
     pytest
     ```

3. **Docker Testing**
   - The application can be tested using Docker Compose:
     ```bash
     docker-compose up --build -d
     ```
   - The API will be available at `http://localhost:8000`
   - API documentation is available at `http://localhost:8000/docs`