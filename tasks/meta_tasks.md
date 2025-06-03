# Meta Tasks for AI Content Factory

> **Note:** All atomic tasks must be referenced here and in `tasks/task_details.md` as per the Task Management Synchronization & Hierarchy Mandate.

## [✅] META-DEPLOY-1: Deployment Readiness & Housekeeping
- Goal: Ensure the project is fully documented, tested, and ready for deployment or handoff by addressing all remaining code, task, and documentation gaps.
- Milestones:
  - [x] Resolve Frontend TypeScript Errors (FE-TS-ERRORS-RESOLVE)
  - [x] Complete Static Analysis & Linting (STATIC-ANALYSIS-ALL)
  - [x] Perform E2E Staging Tests (E2E-USER-FLOW-STAGING)
  - [x] Finalize Documentation Review (FINAL-DOCS-REVIEW)
  - [x] Create Handoff/Deployment Checklist (HANDOFF-CHECKLIST)

## Current Sprint: GCP-Native Serverless Architecture
- Goal: Migrate to a robust, scalable, Terraform-managed GCP deployment.
- Milestones:
  - [x] GCP Core Infrastructure: Firestore, Secret Manager, Cloud Run, Artifact Registry, Cloud Tasks, API Gateway, Workflows provisioned via Terraform (see atomic_tasks.yaml: GCP-1.B.*, INF-1.2)
  - [x] CI/CD Pipeline: Full build, test, deploy, and Terraform apply automation (see atomic_tasks.yaml: CI-*, CI-FE-*)
  - [x] Secure Configuration: All secrets and API keys managed via Secret Manager and securely accessed by the app (see atomic_tasks.yaml: INF-1.1, API-2.4)
  - [x] Application Deployment: FastAPI app fully containerized with Nginx, and deployed to Cloud Run (see atomic_tasks.yaml: GCP-1.A.*, CI-1.2, CI-1.4)

## Next Sprint: SaaS Quality Enhancements & Product Features
- Goal: Add reliability, observability, core product features (auth, feedback), and improve AI content quality.
- Milestones:
  - [x] Robust Job Processing: Firestore job persistence and Cloud Tasks integration for async operations (see atomic_tasks.yaml: API-2.5)
  - [x] Workflow Orchestration: Implement Cloud Workflows for complex generation pipelines (see atomic_tasks.yaml: GCP-1.B.8.* and future WF-* tasks)
  - [x] Monitoring & Cost Control: Implement AI token/cost tracking and basic observability (see atomic_tasks.yaml: AI-5.4 and future MON-* tasks)
  - [~] User Authentication: End-to-end user registration and login (see atomic_tasks.yaml: API-2.2, API-2.3, FE-3.1, FE-3.4)
  - [~] Content Interaction: User feedback system for content (see atomic_tasks.yaml: API-2.7, FE-3.5, AI-5.3)
  - [x] AI Quality: Improved prompt engineering and content post-processing (see atomic_tasks.yaml: AI-5.1, AI-5.2)
  - [x] Developer Experience: Enhanced documentation and local development setup (see atomic_tasks.yaml: DEV-6.2, DEV-6.3)

## Sprint: Core Content Generation Refactoring (Autonomous)
- Goal: Implement a robust, outline-driven, modular architecture for AI content generation.
- Milestones:
  - [x] Refactor Prompts for Modular Generation (Task ID: AI-6.1)
  - [x] Refactor Content Generation Service for New Flow (Task ID: SVC-1.1) - Core logic done, cleanup pending (SVC-1.2)
  - [x] Update Unit Tests for Refactored Service (Task ID: TEST-1.1) - Partially done, expansion pending (TEST-1.2)
  - [x] Update Project Rules (D.1) for New Architecture (Part of DOC-1.1)

## Sprint: Vibe Coding Rules & AI Guidelines Overhaul (Autonomous)
- Goal: Transform project rules and AI operational guidelines to embrace the 'Vibe Coding' philosophy.
- Milestones:
  - [x] Overhaul `.cursor/rules/project.mdc` with Vibe Coding V2 Prompt (Task ID: RULE-1.0)
  - [x] Create `memory/guidelines.md` with AI Core Operating Principles (Task ID: RULE-1.0)

## Sprint: Project Finalization & Polish (AI Execution - Cline)
- Goal: Address outstanding technical debt, complete documentation, and ensure project robustness for handoff.
- Status: In Progress - Blocked by significant testing and API integration issues. See docs/CURRENT_STATUS.md.
- Milestones:
  - [x] Finalize Service Refactoring: Cleanup Deprecated Methods (Task ID: SVC-1.2)
  - [ ] Achieve Comprehensive Unit Test Coverage (Task ID: TEST-1.2) - Status: TODO - Requires significant work. See reports/test_infrastructure_status.md
  - [x] Update README.md to Current Project State (Task ID: DOC-1.2) - Updated June 1, 2025 to reflect "In Development" status.
  - [x] Implement Non-Root User in Docker Container (Task ID: INF-2.1)
  - [ ] Address Human Review Items from `user_input_required_final.md` (Manual - User)

## [✅] META-ARCHIVE-SETTINGS: Foundational Settings & Security
- Goal: Archive of completed foundational tasks for securing and consolidating application settings.
- Milestones:
  - [x] Consolidate settings (ARCHIVE-SETTINGS-1.5)
  - [x] Remove insecure API_KEY (ARCHIVE-SETTINGS-1.6)
  - [x] Review critical settings (ARCHIVE-SETTINGS-1.7)
  - [x] Implement Secret Manager (Covered by INF-1.1, API-2.4)
  - [x] Add docstrings for settings/secrets (ARCHIVE-SETTINGS-1.9)
- Status: done

## [✅] META-ARCHIVE-COREAPI: Archived Core Service & API Alignment
- Goal: Archive of completed foundational tasks for aligning API structure and designating the primary content generation service.
- Milestones:
  - [x] Designate EnhancedMultiStepContentGenerationService as primary (ARCHIVE-COREAPI-2.1)
  - [x] Adapt API for Asynchronous Job-Based Workflow (ARCHIVE-COREAPI-2.2)
  - [x] Refactor API Routers to app/api/routes/ (ARCHIVE-COREAPI-2.3)
- Status: done

## [✅] META-ARCHIVE-DEPCLEAN: Archived Backend Dependencies & Cleanup
- Goal: Archive of completed foundational tasks for resolving backend dependency issues and cleaning up obsolete code structures.
- Milestones:
  - [x] Resolve pytest version conflict (ARCHIVE-DEPCLEAN-3.1)
  - [x] Resolve pydantic & pydantic-settings versions (ARCHIVE-DEPCLEAN-3.2)
  - [x] Clean up requirements.txt (dev dependencies) (ARCHIVE-DEPCLEAN-3.3)
  - [x] Full Review & Cleanup/Deletion of backend/ directory (ARCHIVE-DEPCLEAN-3.4)
- Status: done

## [✅] META-ARCHIVE-ASYNCTEST: Archived Sprint - Enable E2E Testing of Async Job System
- Goal: Archive of completed tasks focused on making the asynchronous content generation flow fully functional and testable, including adding missing job parameters and improving progress indication.
- Milestones:
  - [x] Add Missing Job Parameters (target_duration, target_pages) (ARCHIVE-ASYNCTEST-A)
  - [x] Improve Placeholder Progress Updates in JobManager (ARCHIVE-ASYNCTEST-B)
  - [x] Document Manual User Steps Required for Testing (ARCHIVE-ASYNCTEST-C)
- Status: done

## [✅] META-ARCHIVE-DEVEX11: Archived Task Group 11 - Developer Experience & Tooling
- Goal: Archive of completed tasks from Task Group 11 focusing on developer experience and internal tooling.
- Milestones:
  - [x] Implement Automated AI Context Dump (ARCHIVE-DEVEX11-11.1)
- Status: done

## [✅] META-INFERRED-FOUNDATION: AI-Inferred Foundational Work
- Goal: To document foundational setup and architectural work inferred by the AI assistant as completed but not explicitly tracked, ensuring a more complete project history.
- Milestones:
  - [x] Initial FastAPI Application Setup (INFERRED-FASTAPI-001)
  - [x] Basic Project Directory Structure (INFERRED-STRUCTURE-001)
  - [x] Initial Dockerfile Setup (INFERRED-DOCKER-001)
  - [x] Initial .gitignore and .dockerignore Setup (INFERRED-IGNOREFILES-001)
  - [x] Core Logging Configuration (INFERRED-LOGGING-001)
  - [x] Basic Error Handling Framework (INFERRED-ERRORHANDLING-001)
  - [x] Initial Pydantic Adoption & Basic Schemas (INFERRED-PYDANTIC-001)
- Status: done

## [ ] META-UNDOCUMENTED-WORK: Capture and Integrate Previously Undocumented Work
- Goal: To systematically document and integrate any completed development efforts that were not previously tracked in atomic_tasks.yaml or tasks_archive.md. This is a bucket for any items the user identifies beyond what the AI inferred.
- Milestones:
  - [ ] Identify and list all previously undocumented completed work items.
  - [ ] For each item, create a new atomic task with full details (objective, files, done_when, status 'done', completion_notes).
  - [ ] Link all such new atomic tasks to this meta-task.
  - [ ] Review and confirm all undocumented work is captured.
- Status: todo
