# Service Architecture

This document outlines the key services within the AI Content Factory backend and their responsibilities.

## Primary Content Generation Service

**`EnhancedMultiStepContentGenerationService`** (located in `app/services/multi_step_content_generation.py`)

This is the **primary service** responsible for all complex, multi-step content generation tasks. It serves the main `/api/v1/generate-content` endpoint (and future job-based endpoints).

### Key Responsibilities:

*   **Orchestration**: Manages the end-to-end process of generating long-form educational content.
*   **Topic Decomposition**: Breaks down input syllabus text into manageable topics using AI.
*   **Section Content Generation**: Generates detailed content for each topic, potentially in parallel. This includes generating outlines and then expanding them into full section text using AI.
*   **Content Assembly**: Assembles the generated sections into a cohesive final piece, potentially using AI for introductions, conclusions, and transitions.
*   **Caching**: Implements caching strategies to improve performance and reduce redundant AI calls for previously generated content.
*   **Progress Tracking**: Tracks the progress of content generation jobs, allowing for status updates.
*   **Parallel Processing**: Can process multiple content sections in parallel to speed up generation.
*   **Quality Metrics**: Integrates with a quality metrics service to evaluate the generated content.
*   **Versioning**: Manages different versions of generated content.

### Interactions:

*   Receives requests from API routers (initially, the main content generation endpoint).
*   Uses `MultiStepPrompts` for AI model interactions.
*   Interacts with `ContentCacheService` for caching.
*   Uses `ProgressTracker` for job status.
*   Leverages `ParallelProcessor` for concurrent task execution.
*   Calls `QualityMetricsService` for evaluation.
*   Manages versions through `ContentVersionManager`.
*   Utilizes AI models via the Vertex AI SDK, configured through `app.core.config.settings`.

## Other Services (Supporting and/or Deprecated)

*   **`ContentGenerationService`** (located in `app/services/content_generation.py`):
    *   **Status: DEPRECATED.**
    *   This was a simpler, single-shot service for content generation. It is being replaced by `EnhancedMultiStepContentGenerationService` for all primary content generation tasks.
*   **`AudioGenerationService`**: Handles text-to-speech conversion (e.g., using ElevenLabs).
*   **`ContentCacheService`**: Provides caching functionalities.
*   **`ProgressTracker`**: Tracks asynchronous job progress.
*   **`ParallelProcessor`**: Utility for running tasks in parallel.
*   **`QualityMetricsService`**: Assesses the quality of generated content.
*   **`ContentVersionManager`**: Manages versions of content.

*(This document should be updated as the architecture evolves.)*
