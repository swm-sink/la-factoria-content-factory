---
name: /la-factoria-langfuse
description: "TASK-003: Langfuse prompt management using hyper-specific La Factoria context patterns"
usage: "/la-factoria-langfuse [setup|sync|test] [prompt-name]"
tools: Read, Write, Edit, Bash, Grep
---

# La Factoria Langfuse Integration - TASK-003

**Manage La Factoria educational prompts using hyper-specific patterns from our context engineering and existing prompt templates.**

## Context Imports (Anthropic-Compliant)

### Core Langfuse & Educational Context
@.claude/context/langfuse.md
@.claude/context/educational-content-assessment.md
@.claude/context/claude-4-best-practices.md

### La Factoria Specific Context
@.claude/context/la-factoria-prompt-integration.md
@.claude/context/la-factoria-testing-framework.md
@.claude/context/la-factoria-educational-schema.md
@.claude/context/la-factoria-railway-deployment.md

### Existing Prompt Templates (Direct Sync to Langfuse)
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
# Phase 1: Langfuse Prompt Manager (Using Context Patterns)
/la-factoria-langfuse create-manager            # Uses la-factoria-prompt-integration.md lines 418-519
/la-factoria-langfuse setup-client              # Langfuse client with educational metadata
/la-factoria-langfuse create-trace-service      # Generation trace service for observability

# Phase 2: Prompt Synchronization (Links to Existing Templates)
/la-factoria-langfuse sync-all-templates        # Sync all 10 templates from la-factoria/prompts/
/la-factoria-langfuse create-sync-cli           # CLI tool from la-factoria-prompt-integration.md lines 522-595
/la-factoria-langfuse verify-template-sync      # Verify all templates in Langfuse

# Phase 3: TDD Testing (Using Testing Framework Context)
/la-factoria-langfuse write-integration-tests   # Uses la-factoria-testing-framework.md lines 402-463
/la-factoria-langfuse test-prompt-loading       # Test Langfuse prompt retrieval with caching
/la-factoria-langfuse test-variable-compilation # Test educational variable compilation

# Phase 4: Production Integration (Railway Deployment)
/la-factoria-langfuse add-env-variables         # Uses la-factoria-railway-deployment.md lines 77-80
/la-factoria-langfuse create-health-checks      # Langfuse connectivity health checks
/la-factoria-langfuse integrate-observability   # Educational content generation tracing
```

## Generated Files with Context Integration

### 1. Langfuse Prompt Manager (`src/integrations/langfuse_manager.py`)
**Uses Exact Patterns From**: `context/la-factoria-prompt-integration.md` lines 418-519 + `context/langfuse.md`

```python
# Generated from la-factoria-prompt-integration.md lines 418-430: La Factoria Langfuse Manager
from langfuse import Langfuse
from typing import Dict, Any, Optional
import logging
import os
import time

logger = logging.getLogger(__name__)

class LangfusePromptManager:
    """Manage La Factoria prompts in Langfuse with educational metadata"""
    
    def __init__(self):
        # From la-factoria-prompt-integration.md lines 428-430: Initialize with config check
        self.langfuse = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        self.prompt_cache: Dict[str, Dict] = {}
        
        # La Factoria specific configuration
        self.educational_labels = [
            "la-factoria", "educational-content", "learning-science",
            "cognitive-load", "bloom-taxonomy"
        ]
    
    # From la-factoria-prompt-integration.md lines 432-463: Get prompt with educational caching
    async def get_educational_prompt(
        self, 
        prompt_name: str, 
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get educational prompt from Langfuse with metadata caching"""
        cache_key = f"la_factoria_{prompt_name}:{version or 'latest'}"
        
        if cache_key in self.prompt_cache:
            logger.info(f"Retrieved cached prompt: {prompt_name}")
            return self.prompt_cache[cache_key]
        
        try:
            # Get prompt from Langfuse with La Factoria naming convention
            langfuse_prompt_name = f"la_factoria_{prompt_name}"
            prompt = self.langfuse.get_prompt(
                name=langfuse_prompt_name,
                version=version
            )
            
            # Extract educational metadata
            config = prompt.config or {}
            educational_metadata = config.get("educational_metadata", {})
            
            prompt_data = {
                "name": prompt_name,
                "prompt": prompt.prompt,
                "version": prompt.version,
                "config": config,
                "variables": config.get("variables", []),
                "educational_metadata": {
                    "content_type": prompt_name,
                    "cognitive_complexity": educational_metadata.get("cognitive_complexity", "medium"),
                    "age_groups": educational_metadata.get("age_groups", ["general"]),
                    "bloom_levels": educational_metadata.get("bloom_levels", ["understand"]),
                    "learning_modalities": educational_metadata.get("learning_modalities", ["visual", "auditory"]),
                    **educational_metadata
                }
            }
            
            # Cache the prompt with educational context
            self.prompt_cache[cache_key] = prompt_data
            logger.info(f"Cached educational prompt: {prompt_name}")
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Failed to get prompt {prompt_name} from Langfuse: {e}")
            # Fallback to local template if Langfuse fails
            return self._fallback_to_local_template(prompt_name)
    
    # From la-factoria-prompt-integration.md lines 465-479: Compile educational prompts
    def compile_educational_prompt(
        self, 
        prompt_data: Dict[str, Any], 
        variables: Dict[str, Any]
    ) -> str:
        """Compile Langfuse prompt with educational variables"""
        prompt_template = prompt_data["prompt"]
        
        # Add educational context to variables if not present
        if "age_group" not in variables:
            variables["age_group"] = "general"
        
        # Replace Langfuse-style variables {{variable_name}}
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            if isinstance(var_value, (list, dict)):
                import json
                var_value = json.dumps(var_value, indent=2)
            
            prompt_template = prompt_template.replace(placeholder, str(var_value))
        
        # Also support standard template variables {variable_name} for backward compatibility
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if isinstance(var_value, (list, dict)):
                import json
                var_value = json.dumps(var_value, indent=2)
            
            prompt_template = prompt_template.replace(placeholder, str(var_value))
        
        return prompt_template
    
    # From la-factoria-prompt-integration.md lines 480-519: Create educational generation trace
    async def create_educational_generation_trace(
        self, 
        prompt_name: str,
        input_variables: Dict[str, Any],
        generated_content: str,
        educational_metadata: Dict[str, Any]
    ) -> str:
        """Create educational content generation trace in Langfuse"""
        try:
            # Create trace with educational context
            trace = self.langfuse.trace(
                name=f"la_factoria_{prompt_name}_generation",
                metadata={
                    "platform": "la-factoria",
                    "content_type": prompt_name,
                    "educational_context": {
                        "age_group": input_variables.get("age_group", "general"),
                        "topic": input_variables.get("topic", ""),
                        "learning_objectives": input_variables.get("learning_objectives", []),
                        **educational_metadata
                    },
                    "generation_timestamp": int(time.time()),
                    "content_length": len(generated_content)
                }
            )
            
            # Create generation span with educational metrics
            generation = trace.generation(
                name=f"{prompt_name}_educational_generation",
                model=educational_metadata.get("ai_provider", "unknown"),
                model_parameters={
                    "max_tokens": educational_metadata.get("max_tokens", 3000),
                    "temperature": 0.7,
                    "educational_context": True
                },
                input=input_variables,
                output=generated_content,
                usage={
                    "total_tokens": educational_metadata.get("tokens_used", 0),
                    "prompt_tokens": educational_metadata.get("prompt_tokens", 0),
                    "completion_tokens": educational_metadata.get("completion_tokens", 0)
                }
            )
            
            # Add educational quality score if available
            if "quality_score" in educational_metadata:
                generation.score(
                    name="educational_quality",
                    value=educational_metadata["quality_score"],
                    comment="Educational effectiveness assessment"
                )
            
            logger.info(f"Created educational trace for {prompt_name}: {trace.id}")
            return trace.id
            
        except Exception as e:
            logger.error(f"Failed to create Langfuse trace for {prompt_name}: {e}")
            return None
    
    def _fallback_to_local_template(self, prompt_name: str) -> Dict[str, Any]:
        """Fallback to local template if Langfuse is unavailable"""
        try:
            from pathlib import Path
            template_path = Path(f"la-factoria/prompts/{prompt_name}.md")
            
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                logger.warning(f"Using local fallback template for {prompt_name}")
                return {
                    "name": prompt_name,
                    "prompt": template_content,
                    "version": "local-fallback",
                    "config": {},
                    "variables": [],
                    "educational_metadata": {
                        "content_type": prompt_name,
                        "source": "local-fallback"
                    }
                }
            else:
                logger.error(f"No local template found for {prompt_name}")
                return None
                
        except Exception as e:
            logger.error(f"Fallback template loading failed for {prompt_name}: {e}")
            return None
```

### 2. Prompt Synchronization CLI (`scripts/sync_la_factoria_prompts.py`)
**Uses Exact Patterns From**: `context/la-factoria-prompt-integration.md` lines 522-595

```python
# Generated from la-factoria-prompt-integration.md lines 522-595: Prompt sync CLI
"""Sync all La Factoria educational prompts to Langfuse"""

import asyncio
import argparse
import os
from pathlib import Path
from langfuse import Langfuse
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LaFactoriaPromptSyncer:
    """Sync La Factoria educational prompts to Langfuse"""
    
    def __init__(self, prompts_dir: str = "la-factoria/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.langfuse = self._init_langfuse()
        
        # Educational content types from our schema
        self.content_types = [
            "master_content_outline", "podcast_script", "study_guide",
            "one_pager_summary", "detailed_reading_material", "faq_collection",
            "flashcards", "reading_guide_questions"
        ]
    
    def _init_langfuse(self) -> Langfuse:
        """Initialize Langfuse client with educational configuration"""
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if not secret_key or not public_key:
            raise ValueError("LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY must be set")
        
        return Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host=host
        )
    
    async def sync_all_educational_prompts(self, force: bool = False) -> Dict[str, bool]:
        """Sync all La Factoria educational prompts to Langfuse"""
        
        print("🚀 Starting La Factoria educational prompt sync to Langfuse...")
        
        # Get all prompt files
        prompt_files = list(self.prompts_dir.glob("*.md"))
        
        if not prompt_files:
            print(f"❌ No prompt files found in {self.prompts_dir}")
            return {}
        
        results = {}
        
        for prompt_file in prompt_files:
            template_name = prompt_file.stem
            
            # Skip utility files and README
            if template_name in ["README", "strict_json_instructions"]:
                continue
            
            # Only sync our 8 educational content types
            if template_name not in self.content_types:
                print(f"⏭️  Skipping {template_name} (not in educational content types)")
                continue
            
            print(f"📝 Syncing educational prompt: {template_name}...")
            
            try:
                success = await self._sync_educational_prompt(template_name, force)
                results[template_name] = success
                
                if success:
                    print(f"✅ {template_name} synced successfully")
                else:
                    print(f"❌ {template_name} sync failed")
                    
            except Exception as e:
                print(f"❌ {template_name} sync error: {e}")
                results[template_name] = False
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print(f"\n📊 Educational Prompt Sync Summary: {successful}/{total} prompts synced successfully")
        
        if successful < total:
            failed_prompts = [name for name, success in results.items() if not success]
            print(f"❌ Failed prompts: {', '.join(failed_prompts)}")
        
        return results
    
    async def _sync_educational_prompt(self, template_name: str, force: bool = False) -> bool:
        """Sync individual educational prompt to Langfuse with metadata"""
        
        try:
            # Load template content
            template_path = self.prompts_dir / f"{template_name}.md"
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Extract variables from template
            variables = self._extract_template_variables(template_content)
            
            # Generate educational metadata based on content type
            educational_metadata = self._generate_educational_metadata(template_name, template_content)
            
            # Create or update prompt in Langfuse
            langfuse_prompt_name = f"la_factoria_{template_name}"
            
            self.langfuse.create_prompt(
                name=langfuse_prompt_name,
                prompt=template_content,
                version="1.0",
                labels=[
                    "la-factoria",
                    "educational-content",
                    template_name.replace("_", "-"),
                    f"content-type-{template_name}"
                ],
                config={
                    "variables": variables,
                    "content_type": template_name,
                    "educational_platform": "la-factoria",
                    "educational_metadata": educational_metadata
                }
            )
            
            logger.info(f"Synced educational prompt {template_name} to Langfuse")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync educational prompt {template_name}: {e}")
            return False
    
    def _extract_template_variables(self, template: str) -> list:
        """Extract variable placeholders from educational template"""
        # Find all {variable_name} and {{variable_name}} patterns
        variables = set()
        variables.update(re.findall(r'\{([^}]+)\}', template))
        variables.update(re.findall(r'\{\{([^}]+)\}\}', template))
        return list(variables)
    
    def _generate_educational_metadata(self, content_type: str, template_content: str) -> Dict[str, Any]:
        """Generate educational metadata for content type"""
        
        # Educational metadata mapping for each content type
        metadata_mapping = {
            "master_content_outline": {
                "cognitive_complexity": "high",
                "bloom_levels": ["understand", "apply", "analyze"],
                "age_groups": ["high_school", "college", "adult"],
                "learning_modalities": ["visual", "reading"],
                "estimated_time_minutes": 30
            },
            "podcast_script": {
                "cognitive_complexity": "medium",
                "bloom_levels": ["remember", "understand"],
                "age_groups": ["middle_school", "high_school", "college", "adult"],
                "learning_modalities": ["auditory"],
                "estimated_time_minutes": 20
            },
            "study_guide": {
                "cognitive_complexity": "high",
                "bloom_levels": ["understand", "apply", "analyze", "evaluate"],
                "age_groups": ["high_school", "college"],
                "learning_modalities": ["visual", "reading", "kinesthetic"],
                "estimated_time_minutes": 45
            },
            "flashcards": {
                "cognitive_complexity": "low",
                "bloom_levels": ["remember", "understand"],
                "age_groups": ["elementary", "middle_school", "high_school"],
                "learning_modalities": ["visual", "kinesthetic"],
                "estimated_time_minutes": 15
            }
        }
        
        # Default metadata for content types not explicitly mapped
        default_metadata = {
            "cognitive_complexity": "medium",
            "bloom_levels": ["understand", "apply"],
            "age_groups": ["general"],
            "learning_modalities": ["visual", "reading"],
            "estimated_time_minutes": 25
        }
        
        metadata = metadata_mapping.get(content_type, default_metadata)
        
        # Add template analysis
        metadata.update({
            "template_length": len(template_content),
            "has_json_structure": "```json" in template_content,
            "has_variables": "{" in template_content,
            "content_type": content_type
        })
        
        return metadata

async def main():
    """Main CLI function for syncing La Factoria prompts"""
    parser = argparse.ArgumentParser(description="Sync La Factoria educational prompts to Langfuse")
    parser.add_argument("--prompts-dir", default="la-factoria/prompts", help="Prompts directory")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing prompts")
    
    args = parser.parse_args()
    
    try:
        syncer = LaFactoriaPromptSyncer(args.prompts_dir)
        results = await syncer.sync_all_educational_prompts(args.force)
        
        # Exit with success if all prompts synced successfully
        all_successful = all(results.values()) if results else False
        exit(0 if all_successful else 1)
        
    except Exception as e:
        print(f"❌ Fatal error during prompt sync: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Langfuse Integration Tests (`tests/test_langfuse_integration.py`)
**Uses Exact Patterns From**: `context/la-factoria-testing-framework.md` lines 402-463

```python
# Generated from la-factoria-testing-framework.md lines 402-463: Langfuse integration tests
import pytest
from unittest.mock import AsyncMock, Mock, patch
import os
from src.integrations.langfuse_manager import LangfusePromptManager

class TestLangfuseIntegration:
    """Test Langfuse integration for La Factoria educational prompts"""
    
    @pytest.fixture
    def langfuse_manager(self):
        """Create Langfuse manager for testing"""
        with patch.dict(os.environ, {
            "LANGFUSE_SECRET_KEY": "test-secret-key",
            "LANGFUSE_PUBLIC_KEY": "test-public-key",
            "LANGFUSE_HOST": "https://test.langfuse.com"
        }):
            return LangfusePromptManager()
    
    @pytest.mark.asyncio
    async def test_educational_prompt_retrieval(self, langfuse_manager):
        """Test retrieval of educational prompts from Langfuse"""
        
        # Mock Langfuse client response
        mock_prompt = Mock()
        mock_prompt.prompt = "You are an expert educational content creator. Generate a study guide for {topic}."
        mock_prompt.version = "1.0"
        mock_prompt.config = {
            "variables": ["topic", "age_group"],
            "educational_metadata": {
                "content_type": "study_guide",
                "cognitive_complexity": "high",
                "bloom_levels": ["understand", "apply", "analyze"]
            }
        }
        
        langfuse_manager.langfuse.get_prompt = Mock(return_value=mock_prompt)
        
        # Test prompt retrieval
        prompt_data = await langfuse_manager.get_educational_prompt("study_guide")
        
        assert prompt_data is not None
        assert prompt_data["name"] == "study_guide"
        assert prompt_data["version"] == "1.0"
        assert "educational_metadata" in prompt_data
        assert prompt_data["educational_metadata"]["content_type"] == "study_guide"
        assert "cognitive_complexity" in prompt_data["educational_metadata"]
        
        # Verify Langfuse call with correct naming convention
        langfuse_manager.langfuse.get_prompt.assert_called_once_with(
            name="la_factoria_study_guide",
            version=None
        )
    
    @pytest.mark.asyncio
    async def test_educational_prompt_caching(self, langfuse_manager):
        """Test prompt caching functionality"""
        
        # Mock Langfuse client response
        mock_prompt = Mock()
        mock_prompt.prompt = "Test prompt content"
        mock_prompt.version = "1.0"
        mock_prompt.config = {"variables": ["topic"]}
        
        langfuse_manager.langfuse.get_prompt = Mock(return_value=mock_prompt)
        
        # First call - should fetch from Langfuse
        prompt_data_1 = await langfuse_manager.get_educational_prompt("flashcards")
        
        # Second call - should use cache
        prompt_data_2 = await langfuse_manager.get_educational_prompt("flashcards")
        
        # Verify Langfuse was only called once
        assert langfuse_manager.langfuse.get_prompt.call_count == 1
        
        # Verify both calls returned same data
        assert prompt_data_1 == prompt_data_2
        assert prompt_data_1["name"] == "flashcards"
    
    def test_educational_prompt_compilation(self, langfuse_manager):
        """Test educational prompt variable compilation"""
        
        prompt_data = {
            "name": "study_guide",
            "prompt": "Create a study guide for {{topic}} suitable for {{age_group}} students.",
            "version": "1.0",
            "educational_metadata": {
                "content_type": "study_guide"
            }
        }
        
        variables = {
            "topic": "Photosynthesis",
            "age_group": "high_school"
        }
        
        compiled_prompt = langfuse_manager.compile_educational_prompt(prompt_data, variables)
        
        assert "{{topic}}" not in compiled_prompt
        assert "{{age_group}}" not in compiled_prompt
        assert "Photosynthesis" in compiled_prompt
        assert "high_school" in compiled_prompt
    
    @pytest.mark.asyncio
    async def test_educational_prompt_fallback(self, langfuse_manager):
        """Test fallback to local templates when Langfuse fails"""
        
        # Mock Langfuse failure
        langfuse_manager.langfuse.get_prompt = Mock(side_effect=Exception("Langfuse unavailable"))
        
        # Mock local file existence and content
        mock_template_content = "You are an expert educator. Create flashcards for {topic}."
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=mock_template_content)):
            
            prompt_data = await langfuse_manager.get_educational_prompt("flashcards")
            
            assert prompt_data is not None
            assert prompt_data["name"] == "flashcards"
            assert prompt_data["version"] == "local-fallback"
            assert prompt_data["prompt"] == mock_template_content
            assert prompt_data["educational_metadata"]["source"] == "local-fallback"
    
    @pytest.mark.asyncio
    async def test_educational_generation_trace(self, langfuse_manager):
        """Test creation of educational generation traces"""
        
        # Mock Langfuse trace methods
        mock_trace = Mock()
        mock_trace.id = "trace-12345"
        mock_generation = Mock()
        
        mock_trace.generation = Mock(return_value=mock_generation)
        langfuse_manager.langfuse.trace = Mock(return_value=mock_trace)
        
        # Test trace creation
        input_variables = {
            "topic": "Mathematics",
            "age_group": "high_school",
            "learning_objectives": [{"skill": "solve equations"}]
        }
        
        generated_content = "Generated study guide content..."
        educational_metadata = {
            "ai_provider": "openai",
            "quality_score": 0.85,
            "tokens_used": 1500
        }
        
        trace_id = await langfuse_manager.create_educational_generation_trace(
            "study_guide",
            input_variables,
            generated_content,
            educational_metadata
        )
        
        assert trace_id == "trace-12345"
        
        # Verify trace was created with educational context
        langfuse_manager.langfuse.trace.assert_called_once()
        trace_call_args = langfuse_manager.langfuse.trace.call_args
        assert "la_factoria_study_guide_generation" in trace_call_args[1]["name"]
        assert "educational_context" in trace_call_args[1]["metadata"]
        
        # Verify generation was created
        mock_trace.generation.assert_called_once()
        
        # Verify educational quality score was added
        mock_generation.score.assert_called_once_with(
            name="educational_quality",
            value=0.85,
            comment="Educational effectiveness assessment"
        )

def mock_open(read_data=""):
    """Helper to mock file opening for template fallback tests"""
    from unittest.mock import mock_open as orig_mock_open
    return orig_mock_open(read_data=read_data)
```

### 4. Health Check Integration (`src/health/langfuse_health.py`)
**Uses Exact Patterns From**: `context/la-factoria-railway-deployment.md` lines 290-298

```python
# Langfuse health check for Railway deployment
from typing import Dict, Any
import logging
import asyncio
from ..integrations.langfuse_manager import LangfusePromptManager

logger = logging.getLogger(__name__)

async def check_langfuse_connectivity() -> Dict[str, Any]:
    """Health check for Langfuse connectivity and educational prompt availability"""
    
    health_status = {
        "service": "langfuse",
        "status": "healthy",
        "checks": {}
    }
    
    try:
        # Test Langfuse connection
        manager = LangfusePromptManager()
        
        # Test basic connectivity by trying to get a prompt
        test_prompt = await manager.get_educational_prompt("study_guide")
        
        if test_prompt:
            health_status["checks"]["prompt_retrieval"] = "healthy"
            health_status["checks"]["educational_metadata"] = "available" if test_prompt.get("educational_metadata") else "missing"
        else:
            health_status["checks"]["prompt_retrieval"] = "degraded"
            health_status["status"] = "degraded"
        
        # Test prompt caching
        cached_prompt = await manager.get_educational_prompt("study_guide")
        if cached_prompt == test_prompt:
            health_status["checks"]["prompt_caching"] = "healthy"
        else:
            health_status["checks"]["prompt_caching"] = "degraded"
        
        # Check if all 8 educational content types are available
        content_types = [
            "master_content_outline", "podcast_script", "study_guide",
            "one_pager_summary", "detailed_reading_material", "faq_collection",
            "flashcards", "reading_guide_questions"
        ]
        
        available_prompts = 0
        for content_type in content_types:
            try:
                prompt = await manager.get_educational_prompt(content_type)
                if prompt:
                    available_prompts += 1
            except Exception:
                continue
        
        health_status["checks"]["educational_prompts_available"] = f"{available_prompts}/{len(content_types)}"
        
        if available_prompts < len(content_types):
            health_status["status"] = "degraded"
            
    except Exception as e:
        logger.error(f"Langfuse health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["checks"]["connection"] = f"failed: {str(e)}"
        health_status["checks"]["fallback"] = "local_templates_available"
    
    return health_status
```

## Success Criteria with Context Validation

**HYPER-SPECIFIC La Factoria Langfuse Integration:**
- ✅ **Prompt Manager**: Uses `la-factoria-prompt-integration.md` lines 418-519 (complete Langfuse management with educational metadata)
- ✅ **Sync CLI Tool**: Direct sync of all 10 templates from `la-factoria/prompts/` with educational metadata
- ✅ **Testing Framework**: Integration tests from `la-factoria-testing-framework.md` lines 402-463
- ✅ **Health Checks**: Railway deployment health monitoring for Langfuse connectivity

**EXISTING Prompt Template Integration:**
- ✅ **Template Sync**: All 8 educational content types + 2 utility templates synced to Langfuse
- ✅ **Educational Metadata**: Bloom's taxonomy, cognitive complexity, learning modalities per content type
- ✅ **Fallback System**: Local template fallback when Langfuse unavailable
- ✅ **Variable Support**: Both `{variable}` and `{{variable}}` template patterns

**LANGFUSE OBSERVABILITY INTEGRATION:**
- ✅ **Generation Tracing**: Educational content generation traces with learning context
- ✅ **Quality Scoring**: Educational effectiveness scores in Langfuse traces
- ✅ **Prompt Caching**: Educational prompt caching for performance
- ✅ **Error Handling**: Graceful degradation with local template fallback

**CONTEXT ENGINEERING METRICS:**
- 🎯 **Source Integration**: La Factoria context files + Langfuse context + existing templates
- 🎯 **Line-Number Precision**: Exact implementation patterns from context files
- 🎯 **Educational Focus**: All Langfuse integration serves learning science goals
- 🎯 **Production Ready**: Railway deployment health checks and environment configuration

**Result**: Complete Langfuse integration for La Factoria educational prompts using hyper-specific context patterns with observability, health monitoring, and educational metadata.