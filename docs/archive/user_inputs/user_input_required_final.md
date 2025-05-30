# User Input Required (Final - For Human Review)

This file lists items that require human judgment, decision, or manual intervention for project finalization.
AI-executable tasks are defined in `tasks/atomic_tasks.yaml`.

## 1. AI Prompt Logging Strategy (Security/Privacy)
   - **Context:** The service logs the first 500 characters of AI prompts at DEBUG level (`app/services/multi_step_content_generation.py`, method `_call_generative_model`). These prompts can contain user-provided `syllabus_text`.
   - **Issue:** Logging direct slices of prompts is not robust sanitization and could expose sensitive data if `syllabus_text` is sensitive. Project Rule C.1 (Logging) requires "sanitized input summary".
   - **Decision Needed:** Choose one of the following approaches:
        1.  **Accept As Is:** If DEBUG logs are strictly controlled in production and the risk is deemed acceptable.
        2.  **Reduce Detail in Logs:** Instruct AI (Cline) to modify the logging to only include metadata (e.g., prompt length, a generic message like "Sending prompt for X..." but not the content slice).
        3.  **Implement/Placeholder for Sanitization:** If full prompt logging at DEBUG is desired but needs sanitization, this becomes a more complex task, potentially requiring a dedicated sanitization utility. For now, a TODO comment might suffice if this is lower priority.
   - **Relevant Project Rule:** C.1 (Logging).

## 2. Canonical Location for `user_input_required.md` (Admin/Process)
   - **Context:** During previous autonomous sprints, `user_input_required.md` was created at the project root, while a `tasks/user_input_required.md` also existed (and might still).
   - **Issue:** Potential for confusion regarding the authoritative file for issues logged by AI that need human attention.
   - **Decision Needed:** 
        1.  **Choose One Location:** Decide if future AI-logged human-review items should go to the root `user_input_required_final.md` (this file) or if the `tasks/` directory should house such a file.
        2.  **Consolidate/Archive:** Review `user_input_required.md` (root) and `tasks/user_input_required.md` (if it exists and contains different info) and merge any unique, still relevant human-only items into this `user_input_required_final.md`. Archive or delete the others to avoid confusion.
        3.  **Update Rules (Optional):** If desired, clarify the chosen location in `.cursor/rules/project.mdc` (Section I or K).

## 3. Review and Approve Major Refactoring & Rules Overhaul (Quality Gate)
   - **Context:** Significant refactoring of the core content generation service and a comprehensive overhaul of `.cursor/rules/project.mdc` (Vibe Coding) have been performed.
   - **Action Needed (Human Review):**
        *   Review the refactored code in `app/services/multi_step_content_generation.py` (once `SVC-1.2` for cleanup is done by AI/Cline).
        *   Review the updated prompts in `app/core/prompts/v1/multi_step_prompts.py`.
        *   Review the partially updated unit tests in `tests/unit/test_multi_step_content_generation.py` (and ensure `TEST-1.2` for full coverage is completed by AI/Cline).
        *   Thoroughly review the new `.cursor/rules/project.mdc` and `memory/guidelines.md` for alignment with project vision and operational needs.
   - **Reason:** To ensure the quality, correctness, and alignment of these critical changes before considering the project fully finalized.

This `user_input_required_final.md` should now only contain items that genuinely require human intervention or decision-making. All other actionable items for AI/Cline are in `tasks/atomic_tasks.yaml`.
