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
- Milestones:
  - [x] Finalize Service Refactoring: Cleanup Deprecated Methods (Task ID: SVC-1.2)
  - [x] Achieve Comprehensive Unit Test Coverage (Task ID: TEST-1.2)
  - [x] Update README.md to Current Project State (Task ID: DOC-1.2)
  - [x] Implement Non-Root User in Docker Container (Task ID: INF-2.1)
  - [ ] Address Human Review Items from `user_input_required_final.md` (Manual - User)
