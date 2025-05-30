# Task Details and Rich Context

> **Note:** All atomic tasks must have a detailed entry here and be referenced in `tasks/meta_tasks.md` as per the Task Management Synchronization & Hierarchy Mandate.

This document provides detailed context, rationale, edge cases, and implementation notes for atomic tasks listed in `atomic_tasks.yaml`. Consult this before starting any task.

---
## META-DEPLOY-1: Deployment Readiness & Housekeeping

### FE-TS-ERRORS-RESOLVE (META-DEPLOY-1)
**Objective:** Resolve persistent TypeScript errors in frontend files (Axios/Zustand types, etc.) to enable clean builds and documentation.
**Rationale:** Current TypeScript errors, especially around Axios and Zustand types, are hindering frontend development, commenting, and potentially causing subtle runtime issues.
**Context:** Errors manifest when trying to add module-level comments or during specific type interactions. Reverting changes has been necessary.
**Key Actions:**
  - Investigate `tsconfig.json` for module resolution, type root issues.
  - Verify versions of `typescript`, `@types/axios`, `@types/react`, etc., for compatibility.
  - Test with explicit type imports or different type assertion methods.
  - Ensure `node_modules` and `package-lock.json` are consistent.
**Done When:**
  - `npm run build` (or equivalent for frontend) completes without TypeScript errors.
  - Module-level JSDoc/TSDoc comments can be added to `.ts` and `.tsx` files without errors.
  - Findings and solutions are documented here.
**Cross-References:**
  - `tasks/meta_tasks.md` (META-DEPLOY-1)
  - `tasks/atomic_tasks.yaml` (FE-TS-ERRORS-RESOLVE)

### STATIC-ANALYSIS-ALL (META-DEPLOY-1)
**Objective:** Run and document all static analysis and linting tools for both backend and frontend to ensure code quality and adherence to standards.
**Rationale:** Consistent code quality and style are crucial for maintainability and collaboration.
**Context:** Tools include `flake8`, `black`, `mypy` for backend; `eslint`, `prettier` for frontend; `pip-audit` for backend dependencies.
**Key Actions:**
  - Ensure all linters and formatters are correctly configured (`.flake8`, `pyproject.toml`, `.eslintrc.js`, `.prettierrc.js`).
  - Execute all tools across the relevant parts of the codebase.
  - Document findings, fixes, and any newly created tasks for outstanding issues in `reports/static_analysis_summary.md` (or similar).
  - Update pre-commit hooks if new tools/configurations are added.
**Done When:**
  - All configured static analysis tools run successfully.
  - A summary report of findings and actions is created and linked here.
  - Any necessary fixes are applied or tracked as new atomic tasks.
**Cross-References:**
  - `tasks/meta_tasks.md` (META-DEPLOY-1)
  - `tasks/atomic_tasks.yaml` (STATIC-ANALYSIS-ALL)

### E2E-USER-FLOW-STAGING (META-DEPLOY-1)
**Objective:** Perform a full end-to-end user flow test in the staging environment to validate functionality and user experience before potential production deployment.
**Rationale:** Validates the integration of all components in a production-like environment.
**Context:** Test should cover registration, login, content generation request, job status polling, viewing results, submitting feedback (if UI exists), and logout.
**Key Actions:**
  - Define a clear test plan in `tests/e2e/staging_test_plan.md` covering all critical user paths.
  - Execute the test plan on the staging environment.
  - Document results, including screenshots/videos for any issues, in `reports/staging_e2e_results.md`.
  - Log any bugs or significant UX issues as new atomic tasks.
**Done When:**
  - The E2E test plan is fully executed on staging.
  - Results are documented, and any new issues are tracked.
**Cross-References:**
  - `tasks/meta_tasks.md` (META-DEPLOY-1)
  - `tasks/atomic_tasks.yaml` (E2E-USER-FLOW-STAGING)

### FINAL-DOCS-REVIEW (META-DEPLOY-1)
**Objective:** Conduct a final, comprehensive review of all project documentation to ensure accuracy, clarity, completeness, and consistency.
**Rationale:** Accurate documentation is essential for maintainability, onboarding, and project understanding.
**Context:** Includes `README.md`, all files in `docs/`, `tasks/`, `.cursor/rules/project.mdc`, and significant code comments/docstrings.
**Key Actions:**
  - Review all documents for outdated information, typos, and clarity.
  - Verify all internal links (e.g., between task files, to code sections) and external links.
  - Ensure consistency in terminology and style across documents.
  - Confirm that setup instructions in `README.md` are still accurate.
**Done When:**
  - All key project documents have been reviewed and updated.
  - A summary of changes/verifications is noted here.
**Cross-References:**
  - `tasks/meta_tasks.md` (META-DEPLOY-1)
  - `tasks/atomic_tasks.yaml` (FINAL-DOCS-REVIEW)

### HANDOFF-CHECKLIST (META-DEPLOY-1)
**Objective:** Prepare a comprehensive handoff/production deployment checklist.
**Rationale:** Facilitates smooth transitions for new developers or for deploying the application to production.
**Context:** Checklist should cover environment setup (local and cloud), secrets management procedures, build and deployment steps, key troubleshooting tips, and rollback procedures.
**Key Actions:**
  - Draft the checklist in `docs/operational/deployment_checklist.md`.
  - Include sections for:
    - Prerequisites (tools, access)
    - Backend Setup/Deployment
    - Frontend Setup/Deployment (if applicable)
    - Database/Firestore Setup
    - Secret Management
    - CI/CD Pipeline Overview
    - Monitoring & Logging Access
    - Common Issues & Troubleshooting
    - Rollback Steps
**Done When:**
  - A comprehensive checklist is created and stored in `docs/operational/deployment_checklist.md`.
**Cross-References:**
  - `tasks/meta_tasks.md` (META-DEPLOY-1)
  - `tasks/atomic_tasks.yaml` (HANDOFF-CHECKLIST)

---
## GCP-1.B Series: Terraform Modular Scaffolding
*(Details for these tasks would be here if they weren't already completed)*

---
## INF Series: Infrastructure Hardening & Security
*(Details for INF-1.1, INF-1.2)*

---
## CI Series: Continuous Integration & Deployment
*(Details for CI-1.1 to CI-1.4)*

---
## API Series: Backend API Development
*(Details for API-2.1 to API-2.7)*

---
## VAL Series: Content Validation
*(Details for VAL-1.1, API-VAL-2.8)*

---
## AI-6 Series & SVC-1 Series & TEST-1 Series: Core Content Generation Refactoring
*(Details for AI-6.1, SVC-1.1, SVC-1.2, TEST-1.1, TEST-1.2)*

---
## DOC Series & RULE Series: Documentation and AI Rules
*(Details for DOC-1.1, DOC-1.2, RULE-1.0)*

---
## DEV Series: Developer Experience
*(Details for DEV-6.1, DEV-6.2, DEV-6.4)*

---
## EP11 Series: Legacy Task Integration
*(Details for EP11.1 to EP11.5-FIX)*

---
## MVP Finalization Sprint - 10 Hour Execution Block (New Plan - 2025-05-29)

**Overarching Goal for this 10-hour block:** Achieve significant progress towards a functional MVP, focusing on completing critical backend enhancements (already done prior to this specific plan), establishing frontend CI/CD and DevEx, and building out the core frontend user flow from authentication to content generation and basic feedback.

**Context:** The backend AI enhancements (AI-5.1: Prompt Externalization, AI-5.2: Grammar/Style Post-Processing, AI-5.4: Token/Cost Tracking) were completed in a previous session. This 10-hour plan picks up from there.

**Detailed Phased Plan (Target: ~10 Hours Autonomous Execution):**

**Phase 1: Frontend CI/CD & Developer Experience Polish (Est. 1.5 - 2 hours)**
*   **Task `CI-FE-1.1`: Configure GitHub Actions for frontend CI** (`done`)
    *   **Objective:** Automate frontend testing, linting, building.
    *   **Action:**
        1.  Confirm frontend build scripts from `frontend/package.json` (scripts: `lint`, `test -- --run`, `build`).
        2.  Create/update `.github/workflows/frontend-ci.yml`:
            *   Trigger on push/PR to `main`/`develop` for paths `frontend/**` and the workflow file.
            *   Setup Node.js (e.g., v18 LTS).
            *   Use `npm ci` (caching `frontend/package-lock.json`).
            *   Run `npm run lint`.
            *   Run `npm run test -- --run`.
            *   Run `npm run build`.
*   **Task `DEV-6.3`: DevEx: Pre-commit Hooks Setup (Frontend)** (`done`)
    *   **Objective:** Automate local code quality checks for frontend.
    *   **Action:**
        1.  **Frontend Setup (Husky & lint-staged):**
            *   Install dev dependencies: `npm install --save-dev husky lint-staged` (in `frontend/`).
            *   Initialize Husky: `npx husky init` (in `frontend/`).
            *   Configure `lint-staged` in `frontend/package.json` to run `eslint --fix` and `prettier --write` on staged `*.{ts,tsx}` files.
            *   Create `frontend/.husky/pre-commit` hook to run `npx lint-staged`.
        2.  Document frontend pre-commit setup in `README.md`.

**Phase 2: Core Frontend - Authentication & API Foundation (Est. 2 - 2.5 hours)**
*   **Task `FE-3.1`: User Registration & Login (API/Context & Forms)**
    *   **Action (API & Auth Context):**
        1.  Enhance `frontend/src/api.ts`: Axios instance (`baseURL: /api/v1`), JWT request interceptor, basic response error interceptor.
        2.  Create `frontend/src/contexts/AuthContext.tsx` (or Zustand store): Manage `user`, `token`, `isAuthenticated`; provide `login()`, `logout()`; handle `localStorage` persistence.
        3.  Wrap `frontend/src/App.tsx` with `AuthProvider`.
    *   **Action (Auth Forms & Routing):**
        1.  Create `RegisterPage.tsx`, `LoginPage.tsx`.
        2.  Create `RegistrationForm.tsx`, `LoginForm.tsx` (functional, Tailwind CSS styling).
        3.  Implement form submissions to `/auth/register` & `/auth/login`, use `AuthContext`, handle success/error messages, implement redirection.
        4.  Add routes in `frontend/src/App.tsx`. Create basic `HomePage.tsx` (placeholder for after login) and `ProtectedRoutes.tsx` HOC.

**Phase 3: Core Frontend - Content Generation & Job Management (Est. 3.5 - 4 hours)**
*   **Task `FE-3.2`: Content Generation Form**
    *   **Action:**
        1.  Create `GeneratePage.tsx` (protected route).
        2.  Create `ContentGeneratorForm.tsx`: `syllabus_text` (textarea), `target_format` (select: Podcast, Study Guide, etc.), optional `target_duration`, `target_pages`.
        3.  Implement submission to `/jobs` POST endpoint. Handle loading/errors. On success, navigate to job status page.
*   **Task `FE-3.3`: Job Status Display & Basic Results**
    *   **Action:**
        1.  Create `JobStatusPage.tsx` (protected, parameterized by `job_id`).
        2.  Create `JobStatusDisplay.tsx`: Poll `/jobs/{job_id}`; display status text; if `COMPLETED`, display `content_outline.title`, `content_outline.overview`.
        3.  Create `ContentDisplay.tsx` (basic): Render key fields of `ContentOutline` and the primary `content` string from the job result in a readable format.
*   **Task `FE-3.4`: Logout Functionality**
    *   **Action:** Add Logout button (e.g., in a shared `Navbar.tsx`) using `AuthContext`.

**Phase 4: Basic Feedback UI, UX Polish & E2E Smoke Test (Est. 2 - 2.5 hours)**
*   **Task `FE-3.5`: Content Feedback UI (Basic)**
    *   **Action:** On content display, add "Like" / "Dislike" buttons; implement API call to `/content/{job_id}/feedback`.
*   **Task `UX-4.2` (Simplified): Basic Loading States & Error Modals**
    *   **Action:** Implement text-based loading indicators. Create a simple global error modal/toast system (e.g., using a new `ErrorContext.tsx`) for API errors.
*   **(Stretch Goal if time permits) Task `UX-4.1` (Simplified Onboarding):**
    *   Create a very simple modal shown on first login (use `localStorage`) briefly explaining the app's purpose.
*   **E2E Smoke Test:** Manually test Register -> Login -> Generate -> View Status/Result -> Basic Feedback -> Logout.

**Deferred Tasks (Beyond this 10-hour block, from full checklist):**
*   Full implementation of `UX-4.1` (multi-step Onboarding Wizard).
*   Full implementation of `UX-4.2` (detailed Skeleton Screens).
*   Comprehensive E2E Test Suite development.
*   `AI-5.3` (Full verification of feedback system, including analytics/usage).
*   Remaining Documentation updates (`architecture-map.md`, `feature-tracker.md`, `CHANGELOG.md` finalization).
*   Monitoring Setup verification.
*   Full Deployment & Production Verification steps.
*   Performance Validation against specific targets.
*   Handover phase.

This revised 10-hour plan is more aggressive on the frontend side, aiming for a more complete user flow.
---
*(Existing task details for other IDs would follow)*
