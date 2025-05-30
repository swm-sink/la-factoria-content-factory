# User Input Required (v2 - Post-Refactoring Sprint)

This file lists items requiring user input, decision, or action following the core content generation refactoring sprint.

## I. Critical Manual Follow-up from Refactoring Sprint:

1.  **Service Code Cleanup (`app/services/multi_step_content_generation.py`)**
    *   **Action:** Manually comment out or remove the old, deprecated methods:
        *   `_decompose_topics`
        *   `_generate_sections_sequential`
        *   `_generate_sections_parallel`
        *   `_generate_section_content`
        *   The old `_assemble_content` (LLM-based assembly)
    *   **Reason:** Automated attempts to perform this cleanup failed due to tool limitations with large file edits. These methods are no longer used by the new outline-driven flow and their presence could cause confusion or errors if accidentally called.

2.  **Unit Test Expansion (`tests/unit/test_multi_step_content_generation.py`)**
    *   **Action:** Enhance unit test coverage for the refactored `EnhancedMultiStepContentGenerationService`.
    *   **Specifics:**
        *   Add tests for successful generation and Pydantic validation of *all* derivative content types (FAQs, Flashcards, One-Pager, Detailed Reading, Reading Questions).
        *   Implement tests for partial success scenarios (e.g., master outline succeeds, but one or more derivative types fail to generate).
        *   Adapt previously skipped tests (e.g., `test_generate_long_form_content_cache_hit`, `test_generate_long_form_content_timeout`) to the new service logic, cache key strategy, and return structures.
        *   Verify token aggregation from multiple LLM calls.
    *   **Reason:** Current tests cover the basic new flow and outline failure but lack comprehensive coverage for all derivative types and edge cases.

## II. Previously Logged Items Still Requiring Attention:

3.  **AI Prompt Logging and Potential Sensitive Data Exposure (DEBUG Level)**
    *   **File:** `app/services/multi_step_content_generation.py` (Method: `_call_generative_model`)
    *   **Issue:** DEBUG level logging of the first 500 characters of AI prompts (`prompt_str[:500]...`) might expose sensitive data if `syllabus_text` is sensitive. Rule C.1 requires "sanitized input summary".
    *   **Recommendation:** User to review and decide:
        1.  Accept As Is (if DEBUG logs are strictly controlled).
        2.  Reduce Detail (log only metadata like prompt length).
        3.  Implement/Placeholder for Sanitization.

4.  **README.md Updates**
    *   **File:** `README.md`
    *   **Issue:** Contains outdated information on project structure, API examples (`/api/generate-content` request body), and environment variables.
    *   **Recommendation:** Manually review and update `README.md` to align with current implementation (Pydantic models for requests, `app/` structure, full list of env vars from `settings.py`).

5.  **Task Management File Conflict: `user_input_required.md`**
    *   **Issue:** `user_input_required.md` was created at project root during the initial autonomous sprint. A `tasks/user_input_required.md` also exists.
    *   **Recommendation:** Consolidate into one canonical file. (This `user_input_required_v2.md` is an attempt to sidestep tool issues with the original). Decide on the final location.

6.  **Dockerfile: Application Runs as Root User**
    *   **Files:** `Dockerfile` (final stage), `start.sh`
    *   **Issue:** Python application (Uvicorn) runs as root, violating Rule C.2 ("Run as non-root user").
    *   **Recommendation:** Modify Dockerfile and potentially `start.sh` to create and use a non-root user for the application, ensuring correct file permissions.

## III. Documentation Tasks (Partially Addressed, Vibe Coding Overhaul Pending)

7.  **Project Rules Overhaul (`.cursor/rules/project.mdc`)**
    *   **Status:** Rule D.1 (Content Generation Flow) updated to reflect the new architecture. The major "Vibe Coding" revision as per the detailed user prompt is the next large task.
    *   **Action:** Proceed with the full "Vibe Coding" transformation of `.cursor/rules/project.mdc` as outlined in the user's V2 prompt.

This consolidated list should guide the next steps. The "Vibe Coding" update to `project.mdc` is a significant distinct task.
