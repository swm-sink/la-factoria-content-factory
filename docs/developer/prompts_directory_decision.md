# Prompts Directory Naming Decision

**Date**: June 3, 2025
**Decision ID**: PROMPTS-001
**Purpose**: Document decision on prompts directory naming per Phase 3 Checklist

## Current State Analysis

### `app/core/prompts/` ✅
- **Status**: Active, well-organized
- **Structure**:
  - `app/core/prompts/v1/` - Contains versioned prompt templates
  - Used by `PromptService` in `app/services/prompts.py`
  - Clear versioning strategy (v1, future v2, etc.)

### Usage Analysis
```python
# From app/services/prompts.py
_base_prompt_path: str = "app/core/prompts/v1"
```

**Current References**:
- PromptService class references this path
- All prompt template loading uses this structure
- Clear separation from other core components

## Decision: Keep Current Name `app/core/prompts/`

**Selected Option**: **Keep the current name**

### Rationale

1. **Clear and Descriptive**: "prompts" clearly indicates the contents
2. **Established Usage**: Already integrated throughout the codebase
3. **Appropriate Location**: Belongs in `app/core/` as shared resource
4. **Versioning Support**: Current structure supports versioning (v1, v2, etc.)
5. **No Confusion**: No similar directory names that would cause ambiguity

### Alternative Considered and Rejected

**Option**: Rename to `app/core/ai_prompts/`
- **Rejected Because**:
  - Current name is already clear and unambiguous
  - No other "prompts" in the system that would cause confusion
  - Unnecessary change would require updates across codebase
  - "AI" prefix adds no meaningful disambiguation

## Current Structure Benefits

### Well-Organized ✅
```
app/core/prompts/
├── __init__.py
└── v1/
    ├── master_content_outline.md
    ├── podcast_script.md
    ├── study_guide.md
    ├── one_pager_summary.md
    ├── detailed_reading_material.md
    ├── faqs.md
    ├── flashcards.md
    └── reading_guide_questions.md
```

### Clear Integration ✅
- PromptService automatically loads from versioned directories
- Easy to add new versions (v2, v3) without breaking existing functionality
- Separation of prompt content from business logic

## Future Considerations

### Versioning Strategy
- **Current**: `v1/` subdirectory
- **Future**: Add `v2/`, `v3/` as needed
- **Migration**: PromptService can be configured to use different versions

### Content Organization
- **Current**: One file per content type
- **Scalable**: Can add subdirectories within versions if needed
- **Maintainable**: Clear naming convention

## Testing Impact

**No Changes Required**:
- All tests that reference prompt loading continue to work
- PromptService tests use the existing path structure
- No import statement updates needed

---

**Conclusion**: The current `app/core/prompts/` directory name is clear, well-organized, and appropriately placed. No renaming is necessary or beneficial.
