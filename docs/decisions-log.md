# Decisions Log

This document records key architectural and design decisions made during development.

---

-   **Decision:** Consolidated all AI prompt management to `PromptService` loading from `.md` files, removing old Python-based prompt modules for maintainability.
    -   **Rationale:** Improves separation of concerns, makes prompts easier to iterate on by non-Python developers, and centralizes prompt loading logic.
    -   **Date:** 2025-05-30

-   **Decision:** Resolved critical frontend TypeScript errors by updating type definitions in `types/content.ts` to match backend Pydantic models and by removing conflicting `@types/axios` package.
    -   **Rationale:** Enhances type safety, reduces runtime errors, and ensures frontend data structures align with backend API contracts. Removing `@types/axios` resolves conflicts with Axios 1.x.x's bundled types.
    -   **Date:** 2025-05-30

-   **Decision:** Implemented a `/users/me` endpoint for fetching authenticated user details and integrated it into the frontend `AuthContext` for login and session validation.
    -   **Rationale:** Provides a secure way to retrieve current user information after login and to validate existing sessions, separating token issuance from user detail retrieval.
    -   **Date:** 2025-05-30

---
