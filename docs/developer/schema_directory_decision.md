# Schema Directory Structure Decision

**Date**: June 3, 2025
**Decision ID**: SCHEMA-001
**Purpose**: Clarify Pydantic model placement between `app/models/pydantic/` and `app/core/schemas/`

## Current State Analysis

### `app/models/pydantic/` ✅
- **Status**: Active, well-organized
- **Contents**: All primary Pydantic models for:
  - API requests and responses (`ContentRequest`, `ContentResponse`)
  - Core data structures (`GeneratedContent`, `ContentOutline`)
  - Content type models (`PodcastScript`, `StudyGuide`, etc.)
  - Error handling models (`APIErrorResponse`)
  - Quality and metadata models (`QualityMetrics`, `ContentMetadata`)

### `app/core/schemas/` 📁
- **Status**: Empty directory (only `__pycache__`)
- **Contents**: None
- **Purpose**: Originally intended for generic schemas

## Decision: Consolidate in `app/models/pydantic/`

**Selected Option**: **A) Keep all Pydantic models in `app/models/pydantic/`**

### Rationale

1. **Single Source of Truth**: All Pydantic models are already well-organized in one location
2. **Clear Purpose**: `app/models/pydantic/` clearly indicates "data models using Pydantic"
3. **No Generic Schemas Needed**: Analysis shows no truly generic, non-API, non-data-model schemas exist
4. **Reduced Complexity**: Eliminates confusion about where to place new Pydantic models
5. **Consistent Imports**: All services and APIs import from one predictable location

### Implementation Actions

1. **Maintain Current Structure**: Continue using `app/models/pydantic/` for all Pydantic models
2. **Remove Empty Directory**: Clean up unused `app/core/schemas/` directory
3. **Update Documentation**: Ensure README and architecture docs reflect single schema location

## Future Schema Guidelines

### When to Use `app/models/pydantic/`
- ✅ API request/response models
- ✅ Core business data structures
- ✅ Content type definitions
- ✅ Validation schemas for external data
- ✅ Error response models
- ✅ Metadata and metrics models

### What NOT to Put in Schema Directories
- ❌ Business logic (belongs in services)
- ❌ Database models (if using SQLAlchemy, would go in separate module)
- ❌ Configuration models (belong in `app/core/config/`)

## Import Pattern

**Standardized Import Pattern**:
```python
from app.models.pydantic.content import ContentRequest, GeneratedContent
```

**Benefits**:
- Clear, predictable import path
- Easy to find and maintain
- Consistent across entire codebase

## Alternative Considered and Rejected

**Option B**: Use `app/core/schemas/` for generic schemas
- **Rejected Because**: No truly "generic" schemas identified that wouldn't fit better in `app/models/pydantic/`
- **Additional Complexity**: Would require decisions on borderline cases
- **Import Confusion**: Developers would need to choose between two similar directories

## Directory Cleanup

**Action**: Remove empty `app/core/schemas/` directory
**Rationale**: Eliminates confusion and maintains clean project structure

---

**Conclusion**: All Pydantic models will continue to reside in `app/models/pydantic/`. The empty `app/core/schemas/` directory will be removed to maintain clean project structure.
