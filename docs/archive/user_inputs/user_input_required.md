# User Input Required

This file lists items identified during the autonomous sprint that require your input, decision, or action.

## Items from Previous Sprint (Addressed or In Progress)

**1. Architectural Deviation in Content Generation Flow & Mismatch Between Content Assembly Service Logic and Prompt Definition**
   - **Status:** ADDRESSED.
   - **Resolution:** The content generation service (`EnhancedMultiStepContentGenerationService`) and prompts (`MultiStepPrompts`) have been refactored to an outline-driven, modular flow.
     - A master `ContentOutline` is generated first.
     - Derivative content types are then generated in parallel, each from the master outline using dedicated prompts and validated against their Pydantic models.
     - The old monolithic assembly logic has been replaced.
   - **Follow-up:** The old, now unused methods in `EnhancedMultiStepContentGenerationService` (`_decompose_topics`, `_generate_sections_sequential`, `_generate_sections_parallel`, `_generate_section_content`, `_assemble_content`) were intended to be fully commented out/removed, but tool issues prevented reliable application of these cleanup edits. **Manual review and cleanup of these deprecated methods in `app/services/multi_step_content_generation.py` is required.**

**2. Unit Test Gap for Comprehensive Content Generation**
   - **Status:** PARTIALLY ADDRESSED.
   - **Resolution:** Unit tests in `tests/unit/test_multi_step_content_generation.py` have been updated to include foundational tests for the new outline-driven flow (master outline success, outline failure). Old tests for deprecated methods have been commented out.
   - **Follow-up:** More comprehensive unit test coverage is still needed for:
        - Successful generation and validation of *all* derivative content types.
        - Partial success scenarios (e.g., outline succeeds, some derivatives fail).
        - Adapting remaining skipped tests (e.g., `test_generate_long_form_content_cache_hit`, `test_generate_long_form_content_timeout`) to the new service logic and return structures.

## Ongoing Items / New Items from This Sprint

**3. AI Prompt Logging and Potential Sensitive Data Exposure (DEBUG Level)**
   - **File:** `app/services/multi_step_content_generation.py` (Method: `_call_generative_model` - formerly `_generate_section_content`)
   - **Issue:** The service logs the first 500 characters of AI prompts at the DEBUG level. These prompts can contain portions of the user-provided `syllabus_text`.
   - **Concern:** Logging a direct slice of the prompt (`[:500]`) is not a robust form of sanitization. Rule C.1 requires "sanitized input summary".
   - **Recommendation:** User to review and decide:
        1.  Accept As Is: If DEBUG logs are strictly controlled.
        2.  Reduce Detail: Log only metadata like prompt length or a generic message.
        3.  Implement Sanitization: Add placeholder/TODO for robust sanitization.

**4. README.md Update Required**
   - **File:** `README.md`
   - **Issue:** Contains outdated information regarding project structure, API examples (`/api/generate-content` request body), and environment variables.
   - **Recommendation:** User to manually review and update `README.md` to align with current implementation (Pydantic models for requests, `app/` structure, full list of env vars from `settings.py`).

**5. Task Management File Conflict: `user_input_required.md`**
   - **Issue:** This file exists at project root (used by this sprint) and in `tasks/`.
   - **Recommendation:** User to consolidate and clarify canonical location (details previously logged).

**6. Dockerfile: Application Runs as Root User**
   - **Files:** `Dockerfile`, `start.sh`
   - **Issue:** Python application (Uvicorn) runs as root, violating Rule C.2.
   - **Recommendation:** User to modify Dockerfile/start.sh to use a non-root user (details previously logged).

## End of Current Autonomous Sprint (Refactoring Focus)

This sprint focused on refactoring the core content generation pipeline to an outline-driven, modular architecture.

**Key Accomplishments:**
- Prompts (`app/core/prompts/v1/multi_step_prompts.py`) refactored for the new flow.
- Core logic of `EnhancedMultiStepContentGenerationService` in `app/services/multi_step_content_generation.py` refactored.
- Foundational unit tests for the new flow added to `tests/unit/test_multi_step_content_generation.py`.
- Task management files (`meta_tasks.md`, `atomic_tasks.yaml`, `task_details.md`) updated with new tasks for this refactoring.
- Project rule D.1 in `.cursor/rules/project.mdc` updated to describe the new architecture.

**Immediate Follow-up Items for User:**
- Manually comment out/remove deprecated methods in `app/services/multi_step_content_generation.py`.
- Review and expand unit test coverage for the refactored service.
- Address the remaining items: AI prompt logging, README updates, task file conflict, and Docker root user execution.

Further autonomous work can now build upon this more robust and modular foundation.
