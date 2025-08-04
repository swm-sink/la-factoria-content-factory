---
name: /la-factoria-content
description: "TASK-002: Educational content generation using hyper-specific La Factoria context patterns"
usage: "/la-factoria-content [generate|test|optimize] [content-type]"
tools: Read, Write, Edit, Bash, Grep, Task, WebSearch
---

# La Factoria Content Generation - TASK-002

**Generate educational content using hyper-specific patterns from our 180+ researched sources and existing prompt templates.**

## Context Imports (Anthropic-Compliant @ Syntax)

### Educational & Quality Context
@.claude/context/educational-content-assessment.md
@.claude/context/claude-4-best-practices.md
@.claude/components/la-factoria/educational-standards.md
@.claude/components/la-factoria/quality-assessment.md

### Technical Implementation Context
@.claude/context/fastapi.md
@.claude/context/langfuse.md
@.claude/context/la-factoria-educational-schema.md
@.claude/context/la-factoria-prompt-integration.md

### Testing & Deployment Context
@.claude/context/la-factoria-testing-framework.md
@.claude/context/la-factoria-railway-deployment.md
@.claude/prp/PRP-002-Backend-API-Architecture.md

### Working Examples & Templates
@.claude/examples/backend/fastapi-setup/main.py
@.claude/examples/ai-integration/content-generation/ai_content_service.py
@la-factoria/prompts/master_content_outline.md
@la-factoria/prompts/podcast_script.md
@la-factoria/prompts/study_guide.md
@la-factoria/prompts/study_guide_enhanced.md
@la-factoria/prompts/one_pager_summary.md
@la-factoria/prompts/detailed_reading_material.md
@la-factoria/prompts/faq_collection.md
@la-factoria/prompts/flashcards.md
@la-factoria/prompts/reading_guide_questions.md

## Context-Driven Implementation Process

```bash
# Phase 1: Educational Content Generation Service (Using Context Patterns)
/la-factoria-content create-service            # Uses la-factoria-prompt-integration.md lines 140-291
/la-factoria-content create-endpoints          # Generate 8 specific content type endpoints
/la-factoria-content add-quality-assessment    # Educational quality scoring from context

# Phase 2: Prompt Template Integration (Links to Existing Assets)
/la-factoria-content sync-prompt-templates     # Sync all 10 templates to Langfuse
/la-factoria-content create-prompt-loader      # Uses la-factoria-prompt-integration.md lines 24-136
/la-factoria-content test-template-loading     # Test loading from la-factoria/prompts/

# Phase 3: TDD Implementation (Using Testing Framework Context)
/la-factoria-content write-tests               # Uses la-factoria-testing-framework.md lines 98-622
/la-factoria-content test-all-content-types    # Test all 8 content generation endpoints
/la-factoria-content test-quality-metrics      # Educational effectiveness validation

# Phase 4: AI Provider Integration (Multi-Provider Support)
/la-factoria-content create-ai-manager         # Uses la-factoria-prompt-integration.md lines 293-414
/la-factoria-content add-provider-fallback     # OpenAI, Anthropic, ElevenLabs integration
/la-factoria-content integrate-langfuse        # Prompt management and observability
```

## Generated Files with Context Integration

### 1. Educational Content Service (`src/services/educational_content_service.py`)
**Uses Exact Patterns From**: `context/la-factoria-prompt-integration.md` lines 140-291 + `context/educational-content-assessment.md`

```python
# Generated from la-factoria-prompt-integration.md lines 140-175: Educational Content Service
from typing import Dict, Any, Optional, List
from langfuse.decorators import observe
from langfuse import Langfuse
from .prompt_loader import PromptTemplateLoader
from .ai_providers import AIProviderManager
from .educational_quality_assessor import EducationalQualityAssessor
from ..models.educational import EducationalContent, LearningObjective
import json
import time
import logging

logger = logging.getLogger(__name__)

class EducationalContentService:
    """Educational content generation service using La Factoria prompts"""
    
    def __init__(self):
        # From la-factoria-prompt-integration.md lines 153-156: Service initialization
        self.prompt_loader = PromptTemplateLoader()
        self.ai_provider = AIProviderManager()
        self.quality_assessor = EducationalQualityAssessor()
        self.langfuse = Langfuse() if self._has_langfuse_config() else None
    
    # From la-factoria-prompt-integration.md lines 165-246: Generate content with full pipeline
    @observe(name="educational_content_generation")
    async def generate_educational_content(
        self, 
        content_type: str,
        topic: str,
        age_group: str = "general",
        learning_objectives: Optional[List[LearningObjective]] = None,
        additional_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate educational content using La Factoria prompts with quality assessment"""
        
        start_time = time.time()
        
        # Validate content type against our 8 supported types
        supported_types = [
            "master_content_outline", "podcast_script", "study_guide",
            "one_pager_summary", "detailed_reading_material", "faq_collection",
            "flashcards", "reading_guide_questions"
        ]
        
        if content_type not in supported_types:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        try:
            # Load the appropriate prompt template from la-factoria/prompts/
            template = self.prompt_loader.load_template(content_type)
            
            # Prepare variables for template compilation
            variables = {
                "topic": topic,
                "age_group": age_group,
                "syllabus_text": topic,  # For backward compatibility with existing prompts
                "additional_requirements": additional_requirements or "",
            }
            
            # Add learning objectives if provided
            if learning_objectives:
                variables["learning_objectives"] = [
                    {
                        "cognitive_level": obj.cognitive_level,
                        "subject_area": obj.subject_area,
                        "specific_skill": obj.specific_skill,
                        "measurable_outcome": obj.measurable_outcome,
                        "difficulty_level": obj.difficulty_level
                    }
                    for obj in learning_objectives
                ]
            
            # Compile the template with variables
            compiled_prompt = self.prompt_loader.compile_template(template, variables)
            
            # Generate content using AI provider with fallback
            generated_content = await self.ai_provider.generate_content(
                prompt=compiled_prompt,
                content_type=content_type,
                max_tokens=self._get_max_tokens_for_type(content_type)
            )
            
            # Parse the generated content (handles JSON extraction from markdown)
            parsed_content = self._parse_generated_content(generated_content, content_type)
            
            # Assess educational quality using learning science metrics
            quality_metrics = await self.quality_assessor.assess_content_quality(
                content=parsed_content,
                content_type=content_type,
                age_group=age_group,
                learning_objectives=learning_objectives
            )
            
            # Calculate generation metrics
            generation_time = (time.time() - start_time) * 1000  # milliseconds
            
            # Create comprehensive result with educational metadata
            result = {
                "id": str(uuid.uuid4()),
                "content_type": content_type,
                "topic": topic,
                "age_group": age_group,
                "generated_content": parsed_content,
                "quality_metrics": quality_metrics,
                "metadata": {
                    "generation_duration_ms": int(generation_time),
                    "tokens_used": getattr(generated_content, 'usage', {}).get('total_tokens', 0),
                    "prompt_template": content_type,
                    "ai_provider": self.ai_provider.current_provider,
                    "template_variables": variables,
                    "educational_effectiveness_score": quality_metrics.get("educational_effectiveness", 0),
                    "cognitive_load": quality_metrics.get("cognitive_load_metrics", {}),
                    "readability_score": quality_metrics.get("readability_score", 0)
                }
            }
            
            # Create Langfuse trace for observability
            if self.langfuse:
                await self._create_generation_trace(
                    content_type, variables, generated_content, result["metadata"]
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed for {content_type}: {e}")
            raise
    
    # From la-factoria-prompt-integration.md lines 248-291: Helper methods
    def _get_max_tokens_for_type(self, content_type: str) -> int:
        """Get appropriate token limits for each La Factoria content type"""
        token_limits = {
            "flashcards": 2000,
            "one_pager_summary": 1500,
            "faq_collection": 3000,
            "reading_guide_questions": 2000,
            "study_guide": 4000,
            "detailed_reading_material": 5000,
            "podcast_script": 4000,
            "master_content_outline": 3000
        }
        return token_limits.get(content_type, 3000)
```

### 2. Content Generation Endpoints (`src/api/routes/content_generation.py`)
**Uses Exact Patterns From**: `context/fastapi.md` + `context/la-factoria-educational-schema.md` lines 6-18

```python
# FastAPI endpoints for La Factoria educational content generation
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel, Field

from ..services.educational_content_service import EducationalContentService
from ..models.educational import LaFactoriaContentType, LearningObjective
from ..auth import verify_api_key

router = APIRouter(prefix="/api/content", tags=["Educational Content Generation"])
security = HTTPBearer()

# Request models for educational content generation
class ContentGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500, description="Educational topic or syllabus text")
    age_group: str = Field(default="general", description="Target age group: elementary, middle_school, high_school, college, adult")
    learning_objectives: Optional[List[LearningObjective]] = Field(default=None, description="Specific learning objectives")
    additional_requirements: Optional[str] = Field(default=None, max_length=1000, description="Additional requirements or constraints")

# Endpoints for all 8 La Factoria content types
@router.post("/generate/master_content_outline")
async def generate_master_outline(
    request: ContentGenerationRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(EducationalContentService)
):
    """Generate master content outline using la-factoria/prompts/master_content_outline.md"""
    return await content_service.generate_educational_content(
        content_type="master_content_outline",
        topic=request.topic,
        age_group=request.age_group,
        learning_objectives=request.learning_objectives,
        additional_requirements=request.additional_requirements
    )

@router.post("/generate/podcast_script")
async def generate_podcast_script(
    request: ContentGenerationRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(EducationalContentService)
):
    """Generate podcast script using la-factoria/prompts/podcast_script.md"""
    return await content_service.generate_educational_content(
        content_type="podcast_script",
        topic=request.topic,
        age_group=request.age_group,
        learning_objectives=request.learning_objectives,
        additional_requirements=request.additional_requirements
    )

@router.post("/generate/study_guide")
async def generate_study_guide(
    request: ContentGenerationRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(EducationalContentService)
):
    """Generate study guide using la-factoria/prompts/study_guide.md"""
    return await content_service.generate_educational_content(
        content_type="study_guide",
        topic=request.topic,
        age_group=request.age_group,
        learning_objectives=request.learning_objectives,
        additional_requirements=request.additional_requirements
    )

@router.post("/generate/flashcards")
async def generate_flashcards(
    request: ContentGenerationRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(EducationalContentService)
):
    """Generate flashcards using la-factoria/prompts/flashcards.md"""
    return await content_service.generate_educational_content(
        content_type="flashcards",
        topic=request.topic,
        age_group=request.age_group,
        learning_objectives=request.learning_objectives,
        additional_requirements=request.additional_requirements
    )

# Additional endpoints for remaining 4 content types following same pattern...
@router.post("/generate/{content_type}")
async def generate_content_dynamic(
    content_type: LaFactoriaContentType,
    request: ContentGenerationRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(EducationalContentService)
):
    """Dynamic endpoint for any of the 8 La Factoria content types"""
    return await content_service.generate_educational_content(
        content_type=content_type.value,
        topic=request.topic,
        age_group=request.age_group,
        learning_objectives=request.learning_objectives,
        additional_requirements=request.additional_requirements
    )
```

### 3. Educational Quality Assessor (`src/services/educational_quality_assessor.py`)
**Uses Exact Patterns From**: `context/educational-content-assessment.md` + `context/la-factoria-testing-framework.md` lines 299-399

```python
# Educational quality assessment service using learning science principles
from typing import Dict, Any, Optional, List
import asyncio
import logging
from textstat import textstat
from ..models.educational import LearningObjective, CognitiveLoadMetrics

logger = logging.getLogger(__name__)

class EducationalQualityAssessor:
    """Assess educational content quality using learning science metrics"""
    
    def __init__(self):
        self.min_quality_threshold = 0.7  # From la-factoria-railway-deployment.md line 85
    
    async def assess_content_quality(
        self,
        content: Dict[str, Any],
        content_type: str,
        age_group: str,
        learning_objectives: Optional[List[LearningObjective]] = None
    ) -> Dict[str, Any]:
        """Comprehensive educational quality assessment"""
        
        try:
            # Extract text content for analysis
            content_text = self._extract_text_content(content)
            
            # Parallel assessment of different quality dimensions
            assessments = await asyncio.gather(
                self._assess_cognitive_load(content_text, age_group),
                self._assess_readability(content_text, age_group),
                self._assess_educational_effectiveness(content, content_type),
                self._assess_learning_objective_alignment(content, learning_objectives),
                self._assess_engagement_elements(content_text),
                return_exceptions=True
            )
            
            cognitive_load, readability, effectiveness, alignment, engagement = assessments
            
            # Calculate overall quality score
            quality_score = self._calculate_overall_quality(
                cognitive_load, readability, effectiveness, alignment, engagement
            )
            
            return {
                "overall_quality_score": quality_score,
                "cognitive_load_metrics": cognitive_load,
                "readability_score": readability,
                "educational_effectiveness": effectiveness,
                "learning_objective_alignment": alignment,
                "engagement_score": engagement,
                "meets_quality_threshold": quality_score >= self.min_quality_threshold,
                "assessment_metadata": {
                    "content_type": content_type,
                    "age_group": age_group,
                    "text_length": len(content_text),
                    "has_learning_objectives": learning_objectives is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return self._default_quality_metrics()
    
    async def _assess_cognitive_load(self, text: str, age_group: str) -> Dict[str, float]:
        """Assess cognitive load using educational psychology principles"""
        
        # Intrinsic load: content complexity
        intrinsic_load = self._calculate_intrinsic_load(text, age_group)
        
        # Extraneous load: presentation complexity
        extraneous_load = self._calculate_extraneous_load(text)
        
        # Germane load: learning effort required
        germane_load = self._calculate_germane_load(text, age_group)
        
        # Total cognitive load (weighted average)
        total_load = (intrinsic_load * 0.4) + (extraneous_load * 0.3) + (germane_load * 0.3)
        
        return {
            "intrinsic_load": round(intrinsic_load, 2),
            "extraneous_load": round(extraneous_load, 2),
            "germane_load": round(germane_load, 2),
            "total_cognitive_load": round(total_load, 2)
        }
    
    async def _assess_readability(self, text: str, age_group: str) -> Dict[str, float]:
        """Assess readability using multiple metrics"""
        
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        flesch_kincaid_grade = textstat.flesch_kincaid().grade(text)
        automated_readability_index = textstat.automated_readability_index(text)
        
        # Age-appropriate readability thresholds
        age_thresholds = {
            "elementary": {"grade_level": 4, "flesch_ease": 80},
            "middle_school": {"grade_level": 7, "flesch_ease": 70},
            "high_school": {"grade_level": 10, "flesch_ease": 60},
            "college": {"grade_level": 13, "flesch_ease": 50},
            "adult": {"grade_level": 12, "flesch_ease": 55}
        }
        
        threshold = age_thresholds.get(age_group, age_thresholds["adult"])
        
        # Calculate age appropriateness score
        grade_level_score = min(1.0, threshold["grade_level"] / max(flesch_kincaid_grade, 1))
        flesch_score = min(1.0, flesch_reading_ease / threshold["flesch_ease"])
        
        return {
            "flesch_reading_ease": flesch_reading_ease,
            "flesch_kincaid_grade": flesch_kincaid_grade,
            "automated_readability_index": automated_readability_index,
            "age_appropriateness_score": round((grade_level_score + flesch_score) / 2, 2)
        }
```

### 4. Test Suite (`tests/test_educational_content_generation.py`)
**Uses Exact Patterns From**: `context/la-factoria-testing-framework.md` lines 100-297

```python
# Generated from la-factoria-testing-framework.md lines 100-147: Educational content tests
import pytest
from fastapi import status
from src.models.educational import LaFactoriaContentType

class TestEducationalContentGeneration:
    """Test educational content generation for all 8 content types"""
    
    @pytest.mark.asyncio
    async def test_master_outline_generation(
        self, client, auth_headers, sample_learning_objectives, sample_cognitive_load
    ):
        """Test master content outline generation using existing prompt template"""
        request_data = {
            "topic": "Introduction to Algebra",
            "age_group": "high_school",
            "learning_objectives": sample_learning_objectives,
            "cognitive_load_target": sample_cognitive_load
        }
        
        response = client.post(
            "/api/content/generate/master_content_outline",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        
        # Validate response structure matches our educational schema
        assert "id" in content
        assert "content_type" in content
        assert content["content_type"] == "master_content_outline"
        assert "generated_content" in content
        assert "quality_metrics" in content
        
        # Validate generated content structure (from la-factoria/prompts/master_content_outline.md)
        generated = content["generated_content"]
        assert "title" in generated
        assert "overview" in generated
        assert "learning_objectives" in generated
        assert "sections" in generated
        assert isinstance(generated["sections"], list)
        assert len(generated["sections"]) > 0
        
        # Validate educational quality meets threshold (from la-factoria-railway-deployment.md line 85)
        quality_metrics = content["quality_metrics"]
        assert quality_metrics["overall_quality_score"] >= 0.7
        assert quality_metrics["meets_quality_threshold"] == True
        
        # Validate prompt template integration
        metadata = content["metadata"]
        assert metadata["prompt_template"] == "master_content_outline"
        assert "ai_provider" in metadata
        assert "generation_duration_ms" in metadata
    
    @pytest.mark.parametrize("content_type", [
        "podcast_script", "study_guide", "one_pager_summary", 
        "detailed_reading_material", "faq_collection", 
        "flashcards", "reading_guide_questions"
    ])
    @pytest.mark.asyncio
    async def test_all_content_types_generation(
        self, client, auth_headers, sample_learning_objectives, content_type
    ):
        """Test generation for all 8 La Factoria content types using existing prompts"""
        request_data = {
            "topic": "Photosynthesis in Plants",
            "age_group": "high_school",
            "learning_objectives": sample_learning_objectives
        }
        
        response = client.post(
            f"/api/content/generate/{content_type}",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        
        # Validate all content types meet educational standards
        assert content["content_type"] == content_type
        assert "generated_content" in content
        assert "quality_metrics" in content
        assert content["quality_metrics"]["overall_quality_score"] >= 0.7
        
        # Validate prompt template usage
        assert content["metadata"]["prompt_template"] == content_type
```

## Success Criteria with Context Validation

**HYPER-SPECIFIC La Factoria Content Generation:**
- ✅ **Educational Service**: Uses `la-factoria-prompt-integration.md` lines 140-291 (complete content generation pipeline)
- ✅ **FastAPI Endpoints**: 8 specific endpoints for each content type with educational validation
- ✅ **Quality Assessment**: Learning science metrics from `educational-content-assessment.md` 
- ✅ **Testing Framework**: TDD patterns from `la-factoria-testing-framework.md` lines 100-297

**EXISTING Prompt Template Integration:**
- ✅ **Direct File Access**: All 10 templates from `la-factoria/prompts/` directory
- ✅ **Variable Compilation**: Template loader with educational variables
- ✅ **Langfuse Sync**: Prompt management and observability 
- ✅ **AI Provider Fallback**: OpenAI, Anthropic, ElevenLabs support

**EDUCATIONAL EFFECTIVENESS INTEGRATION:**
- ✅ **Cognitive Load Theory**: Intrinsic, extraneous, germane load assessment
- ✅ **Readability Metrics**: Age-appropriate language validation
- ✅ **Learning Objectives**: Bloom's taxonomy alignment verification
- ✅ **Quality Thresholds**: Minimum 0.7 educational effectiveness score

**CONTEXT ENGINEERING METRICS:**
- 🎯 **Source Integration**: 4 La Factoria context files + 4 general context files
- 🎯 **Line-Number Precision**: Exact implementation patterns referenced
- 🎯 **Working Code Generation**: Real endpoints, services, and tests
- 🎯 **Educational Focus**: All patterns serve learning science principles

**Result**: Complete educational content generation system using existing prompt templates with hyper-specific La Factoria patterns, not generic implementations.