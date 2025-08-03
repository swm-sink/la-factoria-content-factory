# La Factoria Prompt Template Integration Context

## Linking Existing Prompts to Langfuse and AI Providers

### Existing Prompt Template Inventory
```python
# Mapping of our 10 existing prompt templates in la-factoria/prompts/
LA_FACTORIA_PROMPT_TEMPLATES = {
    "master_content_outline": "la-factoria/prompts/master_content_outline.md",
    "podcast_script": "la-factoria/prompts/podcast_script.md", 
    "study_guide": "la-factoria/prompts/study_guide.md",
    "study_guide_enhanced": "la-factoria/prompts/study_guide_enhanced.md",
    "one_pager_summary": "la-factoria/prompts/one_pager_summary.md",
    "detailed_reading_material": "la-factoria/prompts/detailed_reading_material.md",
    "faq_collection": "la-factoria/prompts/faq_collection.md",
    "flashcards": "la-factoria/prompts/flashcards.md",
    "reading_guide_questions": "la-factoria/prompts/reading_guide_questions.md",
    "strict_json_instructions": "la-factoria/prompts/strict_json_instructions.md"
}
```

### Prompt Template Loader Service
```python
# src/services/prompt_loader.py
from pathlib import Path
from typing import Dict, Optional, Any
import re
import yaml
from langfuse import Langfuse
import logging

logger = logging.getLogger(__name__)

class PromptTemplateLoader:
    """Load and manage La Factoria prompt templates"""
    
    def __init__(self, prompts_dir: str = "la-factoria/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.templates_cache: Dict[str, str] = {}
        self.langfuse = Langfuse() if self._has_langfuse_config() else None
        
    def _has_langfuse_config(self) -> bool:
        """Check if Langfuse is configured"""
        import os
        return all([
            os.getenv("LANGFUSE_SECRET_KEY"),
            os.getenv("LANGFUSE_PUBLIC_KEY")
        ])
    
    def load_template(self, template_name: str) -> str:
        """Load prompt template from file"""
        if template_name in self.templates_cache:
            return self.templates_cache[template_name]
        
        template_path = self.prompts_dir / f"{template_name}.md"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Cache the template
        self.templates_cache[template_name] = template_content
        
        logger.info(f"Loaded prompt template: {template_name}")
        return template_content
    
    def extract_variables(self, template: str) -> list[str]:
        """Extract variable placeholders from template"""
        # Find all {variable_name} patterns
        variables = re.findall(r'\{([^}]+)\}', template)
        return list(set(variables))
    
    def compile_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Compile template with variables"""
        compiled = template
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if isinstance(var_value, (list, dict)):
                # Convert complex types to JSON
                import json
                var_value = json.dumps(var_value, indent=2)
            
            compiled = compiled.replace(placeholder, str(var_value))
        
        return compiled
    
    def sync_to_langfuse(self, template_name: str, version: str = "1.0") -> bool:
        """Sync prompt template to Langfuse"""
        if not self.langfuse:
            logger.warning("Langfuse not configured, skipping sync")
            return False
        
        try:
            template_content = self.load_template(template_name)
            variables = self.extract_variables(template_content)
            
            # Create or update prompt in Langfuse
            self.langfuse.create_prompt(
                name=f"la_factoria_{template_name}",
                prompt=template_content,
                version=version,
                labels=[
                    "la-factoria",
                    "educational-content",
                    template_name.replace("_", "-")
                ],
                config={
                    "variables": variables,
                    "content_type": template_name,
                    "educational_platform": "la-factoria"
                }
            )
            
            logger.info(f"Synced {template_name} to Langfuse as version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync {template_name} to Langfuse: {e}")
            return False
    
    def sync_all_templates(self) -> Dict[str, bool]:
        """Sync all La Factoria templates to Langfuse"""
        results = {}
        
        for template_name in LA_FACTORIA_PROMPT_TEMPLATES.keys():
            if template_name == "strict_json_instructions":
                # Skip utility template
                continue
                
            results[template_name] = self.sync_to_langfuse(template_name)
        
        return results
```

### Educational Content Generation Service with Prompt Integration
```python
# src/services/educational_content_service.py
from typing import Dict, Any, Optional
from langfuse.decorators import observe
from langfuse import Langfuse
from .prompt_loader import PromptTemplateLoader
from .ai_providers import AIProviderManager
from ..models.educational import EducationalContent, LearningObjective
import json
import time

class EducationalContentService:
    """Educational content generation service using La Factoria prompts"""
    
    def __init__(self):
        self.prompt_loader = PromptTemplateLoader()
        self.ai_provider = AIProviderManager()
        self.langfuse = Langfuse() if self._has_langfuse_config() else None
    
    def _has_langfuse_config(self) -> bool:
        import os
        return all([
            os.getenv("LANGFUSE_SECRET_KEY"),
            os.getenv("LANGFUSE_PUBLIC_KEY")
        ])
    
    @observe(name="educational_content_generation")
    async def generate_content(
        self, 
        content_type: str,
        topic: str,
        age_group: str = "general",
        learning_objectives: Optional[list[LearningObjective]] = None,
        additional_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate educational content using La Factoria prompts"""
        
        start_time = time.time()
        
        try:
            # Load the appropriate prompt template
            template = self.prompt_loader.load_template(content_type)
            
            # Prepare variables for template compilation
            variables = {
                "topic": topic,
                "age_group": age_group,
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
            
            # Handle content-type specific variables
            if content_type == "master_content_outline":
                variables["outline_json"] = "{}"  # Placeholder for JSON structure
            elif content_type == "podcast_script":
                variables["outline_json"] = json.dumps({
                    "title": f"Podcast about {topic}",
                    "sections": [{"title": "Introduction", "content": "Overview"}]
                }, indent=2)
            
            # Compile the template
            compiled_prompt = self.prompt_loader.compile_template(template, variables)
            
            # Generate content using AI provider
            generated_content = await self.ai_provider.generate_content(
                prompt=compiled_prompt,
                content_type=content_type,
                max_tokens=self._get_max_tokens_for_type(content_type)
            )
            
            # Parse the generated content
            parsed_content = self._parse_generated_content(generated_content, content_type)
            
            # Calculate metrics
            generation_time = (time.time() - start_time) * 1000  # milliseconds
            
            # Create result with metadata
            result = {
                "content_type": content_type,
                "topic": topic,
                "age_group": age_group,
                "generated_content": parsed_content,
                "metadata": {
                    "generation_duration_ms": int(generation_time),
                    "tokens_used": getattr(generated_content, 'usage', {}).get('total_tokens', 0),
                    "prompt_template": content_type,
                    "ai_provider": self.ai_provider.current_provider,
                    "template_variables": variables
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed for {content_type}: {e}")
            raise
    
    def _get_max_tokens_for_type(self, content_type: str) -> int:
        """Get appropriate token limits for each content type"""
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
    
    def _parse_generated_content(self, raw_content: str, content_type: str) -> Dict[str, Any]:
        """Parse AI-generated content based on expected structure"""
        try:
            # Try to parse as JSON first (our prompts request JSON output)
            if raw_content.strip().startswith('{'):
                return json.loads(raw_content)
            
            # Extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Fallback: return as plain text
            logger.warning(f"Could not parse JSON for {content_type}, returning as text")
            return {
                "title": f"Generated {content_type.replace('_', ' ').title()}",
                "content": raw_content,
                "raw_output": True
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for {content_type}: {e}")
            return {
                "title": f"Generated {content_type.replace('_', ' ').title()}",
                "content": raw_content,
                "parsing_error": str(e),
                "raw_output": True
            }
```

### AI Provider Manager with Multiple Provider Support
```python
# src/services/ai_providers.py
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import openai
import anthropic
import os
import logging

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        pass

class OpenAIProvider(AIProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_content(self, prompt: str, max_tokens: int = 3000, **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

class AnthropicProvider(AIProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate_content(self, prompt: str, max_tokens: int = 3000, **kwargs) -> str:
        try:
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise

class AIProviderManager:
    """Manage multiple AI providers with fallback"""
    
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.current_provider = "openai"  # Default
        
        # Initialize available providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize AI providers based on available API keys"""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.providers["openai"] = OpenAIProvider(openai_key)
        
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.providers["anthropic"] = AnthropicProvider(anthropic_key)
        
        if not self.providers:
            raise ValueError("No AI provider API keys configured")
        
        # Set default to first available provider
        self.current_provider = list(self.providers.keys())[0]
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content with fallback to other providers"""
        primary_provider = self.providers.get(self.current_provider)
        
        if not primary_provider:
            raise ValueError(f"Provider {self.current_provider} not available")
        
        try:
            return await primary_provider.generate_content(prompt, **kwargs)
        
        except Exception as e:
            logger.warning(f"Primary provider {self.current_provider} failed: {e}")
            
            # Try fallback providers
            for provider_name, provider in self.providers.items():
                if provider_name == self.current_provider:
                    continue
                
                try:
                    logger.info(f"Trying fallback provider: {provider_name}")
                    result = await provider.generate_content(prompt, **kwargs)
                    logger.info(f"Fallback provider {provider_name} succeeded")
                    return result
                
                except Exception as fallback_error:
                    logger.warning(f"Fallback provider {provider_name} failed: {fallback_error}")
                    continue
            
            # All providers failed
            raise Exception("All AI providers failed")
```

### Langfuse Integration for Prompt Management
```python
# src/integrations/langfuse_manager.py
from langfuse import Langfuse
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LangfusePromptManager:
    """Manage La Factoria prompts in Langfuse"""
    
    def __init__(self):
        self.langfuse = Langfuse()
        self.prompt_cache: Dict[str, Dict] = {}
    
    async def get_prompt(self, prompt_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get prompt from Langfuse with caching"""
        cache_key = f"{prompt_name}:{version or 'latest'}"
        
        if cache_key in self.prompt_cache:
            return self.prompt_cache[cache_key]
        
        try:
            # Get prompt from Langfuse
            langfuse_prompt_name = f"la_factoria_{prompt_name}"
            prompt = self.langfuse.get_prompt(
                name=langfuse_prompt_name,
                version=version
            )
            
            prompt_data = {
                "name": prompt_name,
                "prompt": prompt.prompt,
                "version": prompt.version,
                "config": prompt.config or {},
                "variables": prompt.config.get("variables", []) if prompt.config else []
            }
            
            # Cache the prompt
            self.prompt_cache[cache_key] = prompt_data
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Failed to get prompt {prompt_name} from Langfuse: {e}")
            # Fallback to local file
            return None
    
    def compile_langfuse_prompt(self, prompt_data: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Compile Langfuse prompt with variables"""
        prompt_template = prompt_data["prompt"]
        
        # Replace Langfuse-style variables {{variable_name}}
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            if isinstance(var_value, (list, dict)):
                import json
                var_value = json.dumps(var_value, indent=2)
            
            prompt_template = prompt_template.replace(placeholder, str(var_value))
        
        return prompt_template
    
    async def create_generation_trace(
        self, 
        prompt_name: str,
        input_variables: Dict[str, Any],
        generated_content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Create a generation trace in Langfuse"""
        try:
            trace = self.langfuse.trace(
                name=f"la_factoria_{prompt_name}_generation",
                metadata={
                    "content_type": prompt_name,
                    "platform": "la-factoria",
                    **metadata
                }
            )
            
            generation = trace.generation(
                name=f"{prompt_name}_generation",
                model=metadata.get("ai_provider", "unknown"),
                model_parameters={
                    "max_tokens": metadata.get("max_tokens", 3000),
                    "temperature": 0.7
                },
                input=input_variables,
                output=generated_content,
                usage={
                    "total_tokens": metadata.get("tokens_used", 0),
                    "prompt_tokens": metadata.get("prompt_tokens", 0),
                    "completion_tokens": metadata.get("completion_tokens", 0)
                }
            )
            
            return trace.id
            
        except Exception as e:
            logger.error(f"Failed to create Langfuse trace: {e}")
            return None
```

### Prompt Synchronization CLI Tool
```python
# scripts/sync_prompts_to_langfuse.py
"""Sync all La Factoria prompts to Langfuse"""

import asyncio
import argparse
from src.services.prompt_loader import PromptTemplateLoader
from pathlib import Path

async def sync_prompts_to_langfuse(prompts_dir: str = "la-factoria/prompts", force: bool = False):
    """Sync all La Factoria prompt templates to Langfuse"""
    
    loader = PromptTemplateLoader(prompts_dir)
    
    if not loader.langfuse:
        print("❌ Langfuse not configured. Please set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY")
        return False
    
    print("🚀 Starting La Factoria prompt sync to Langfuse...")
    
    # Get all prompt files
    prompts_path = Path(prompts_dir)
    prompt_files = list(prompts_path.glob("*.md"))
    
    if not prompt_files:
        print(f"❌ No prompt files found in {prompts_dir}")
        return False
    
    results = {}
    
    for prompt_file in prompt_files:
        template_name = prompt_file.stem
        
        # Skip utility files
        if template_name in ["README", "strict_json_instructions"]:
            continue
        
        print(f"📝 Syncing {template_name}...")
        
        try:
            success = loader.sync_to_langfuse(template_name)
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
    
    print(f"\n📊 Sync Summary: {successful}/{total} prompts synced successfully")
    
    if successful < total:
        failed_prompts = [name for name, success in results.items() if not success]
        print(f"❌ Failed prompts: {', '.join(failed_prompts)}")
    
    return successful == total

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync La Factoria prompts to Langfuse")
    parser.add_argument("--prompts-dir", default="la-factoria/prompts", help="Prompts directory")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing prompts")
    
    args = parser.parse_args()
    
    success = asyncio.run(sync_prompts_to_langfuse(args.prompts_dir, args.force))
    exit(0 if success else 1)
```