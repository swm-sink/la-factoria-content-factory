# AI Content Factory - Project Overview
**Generated**: 2025-06-02 20:55:15

## 🎯 Project Mission

Transform textual input into comprehensive educational content:
- Podcast scripts with natural flow and timing
- Study guides with key concepts and examples
- One-page summaries for quick reference
- Interactive study aids (FAQs, flashcards, reading questions)
- High-quality audio generation via ElevenLabs

**Target**: MVP deployment on Google Cloud Run with Vertex AI integration

## 🏗 Architecture Overview

- **Backend**: FastAPI + Python 3.11
- **AI**: Vertex AI Gemini for content generation
- **Audio**: ElevenLabs text-to-speech
- **Storage**: Firestore for job persistence
- **Deployment**: Docker → Cloud Run
- **Queue**: Cloud Tasks for async processing

## 📊 Current State

- **Data Models**: 195 Pydantic models defined
- **API Endpoints**: 72 routes implemented
- **Known Issues**: 1 active blockers

### Key Models
- `BaseSettings` - Base class for settings, allowing values to be overridden by environment variables.
- `RootModel` - Usage docs: https://docs.pydantic.dev/2.8/concepts/models/#rootmodel-and-custom-root-types
- `GenericModel` - Data model
- `ModelDeleted` - Data model
- `Completion` - Data model

### API Endpoints
- `GET /healthz`
- `GET /users/`
- `GET /items/`
- `GET /items/`
- `GET /items/`
- `PUT /items/{item_id}`
- `POST /items/`
- `DELETE /items/{item_id}`

## 🚨 Current Blockers

1. **Firestore Database Issue (Encountered: 2025-06-02)**: **Task(s) Blocked:** T-102 (Verify Endpoints in Swagger UI - partially), T-104 (Manual Endpoint Smoke Test), and any subsequent tasks relying on job creation or database interaction.

**Issue:** The a...

## 📋 Task Status

**Next Steps:**
- Tasks pending (see atomic_tasks.yaml)
- See meta_tasks.md for current sprint

## 🎯 Immediate Goals

1. **Resolve Database Connection** - Fix Firestore connectivity issues
2. **Complete API Implementation** - Finish job creation/status endpoints
3. **Test Content Generation** - Verify AI pipeline works end-to-end
4. **Deployment Readiness** - Ensure Docker build and Cloud Run deployment

## 📁 Key Files for Debugging

- `project_blockers.md` - Current issues preventing progress
- `app/main.py` - FastAPI application entry point
- `app/api/routes/jobs.py` - Job management endpoints
- `app/services/` - Core business logic
- `Dockerfile` - Container configuration

---
*For complete technical details, see `complete_codebase.md`*
