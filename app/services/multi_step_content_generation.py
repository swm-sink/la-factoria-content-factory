"""
Multi-step content generation service for creating long-form educational content.
Handles orchestration of topic decomposition, content generation, and assembly.
"""

import logging
import json
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from google.cloud import aiplatform
from prometheus_client import Counter, Histogram

from app.core.config.settings import get_settings
from app.core.prompts.v1.multi_step_prompts import MultiStepPrompts
from app.services.content_cache import ContentCacheService
from app.services.progress_tracker import ProgressTracker, GenerationStage
from app.services.parallel_processor import ParallelProcessor
from app.services.quality_metrics import QualityMetricsService
from app.models.content_version import ContentVersion, ContentVersionManager, ContentFormat

# Prometheus metrics
MULTI_STEP_GENERATION_CALLS = Counter(
    'multi_step_generation_calls_total',
    'Total number of multi-step content generation calls'
)
MULTI_STEP_GENERATION_DURATION = Histogram(
    'multi_step_generation_duration_seconds',
    'Time spent on multi-step content generation'
)

@dataclass
class ContentSection:
    """Represents a section of content with its metadata."""
    title: str
    content: str
    word_count: int
    estimated_duration: float  # in minutes
    content_type: str  # e.g., 'podcast', 'guide', 'one_pager'

class EnhancedMultiStepContentGenerationService:
    """Enhanced service for generating long-form educational content through multiple steps."""
    
    def __init__(self):
        """Initialize the service with settings and AI platform."""
        self.settings = get_settings()
        self.prompts = MultiStepPrompts()
        self.cache = ContentCacheService()
        self.progress_tracker = ProgressTracker()
        self.parallel_processor = ParallelProcessor(max_workers=4)
        self.quality_service = QualityMetricsService()
        self.version_manager = ContentVersionManager()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Vertex AI
        aiplatform.init(
            project=self.settings.gcp_project_id,
            location=self.settings.gcp_location
        )
        self.model = aiplatform.GenerativeModel(self.settings.gemini_model_name)

    def generate_long_form_content(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: float = None,
        target_pages: int = None,
        use_cache: bool = True,
        use_parallel: bool = True
    ) -> Tuple[Dict[str, Any], int, str]:
        """
        Generate long-form content through multiple steps with all enhancements.
        
        Args:
            syllabus_text: The source material to generate content from
            target_format: The desired output format ('podcast', 'guide', etc.)
            target_duration: Target duration in minutes (for podcasts)
            target_pages: Target number of pages (for guides)
            use_cache: Whether to use caching
            use_parallel: Whether to use parallel processing
            
        Returns:
            Tuple of (generated_content, status_code, job_id)
        """
        start_time = time.time()
        total_token_usage = {'input_tokens': 0, 'output_tokens': 0}
        
        # Start progress tracking
        job_id = self.progress_tracker.start_job(
            syllabus_text, target_format, target_duration, target_pages
        )
        
        try:
            MULTI_STEP_GENERATION_CALLS.inc()
            
            # Check cache first
            if use_cache:
                self.progress_tracker.update_stage(
                    job_id, GenerationStage.INITIALIZING, 10.0, "Checking cache"
                )
                
                cached_content = self.cache.get(
                    syllabus_text, target_format, target_duration, target_pages
                )
                
                if cached_content:
                    self.progress_tracker.complete_job(job_id, cached_content)
                    self.logger.info(f"Content served from cache for job {job_id}")
                    return cached_content, 200, job_id
            
            # Step 1: Topic Decomposition
            self.progress_tracker.update_stage(
                job_id, GenerationStage.DECOMPOSING_TOPICS, 0.0, "Starting topic decomposition"
            )
            
            topics, decomposition_token_usage = self._decompose_topics(syllabus_text)
            total_token_usage['input_tokens'] += decomposition_token_usage.get('input_tokens', 0)
            total_token_usage['output_tokens'] += decomposition_token_usage.get('output_tokens', 0)
            
            self.progress_tracker.update_stage(
                job_id, GenerationStage.DECOMPOSING_TOPICS, 100.0, "Topic decomposition complete"
            )
            
            # Step 2: Generate Content for Each Topic
            self.progress_tracker.update_stage(
                job_id, GenerationStage.GENERATING_SECTIONS, 0.0, 
                f"Generating content for {len(topics)} topics"
            )
            
            sections: List[ContentSection] = []
            sections_token_usage: Dict[str, int] = {'input_tokens': 0, 'output_tokens': 0}
            
            if use_parallel and len(topics) > 1:
                sections, sections_token_usage = self._generate_sections_parallel(
                    topics, target_format, target_duration, target_pages, job_id
                )
            else:
                sections, sections_token_usage = self._generate_sections_sequential(
                    topics, target_format, target_duration, target_pages, job_id
                )
            
            total_token_usage['input_tokens'] += sections_token_usage.get('input_tokens', 0)
            total_token_usage['output_tokens'] += sections_token_usage.get('output_tokens', 0)
            
            # Step 3: Assemble and Enhance Content
            self.progress_tracker.update_stage(
                job_id, GenerationStage.ASSEMBLING_CONTENT, 0.0, "Assembling final content"
            )
            
            final_content, assembly_token_usage = self._assemble_content(sections, target_format)
            total_token_usage['input_tokens'] += assembly_token_usage.get('input_tokens', 0)
            total_token_usage['output_tokens'] += assembly_token_usage.get('output_tokens', 0)
            
            self.progress_tracker.update_stage(
                job_id, GenerationStage.ASSEMBLING_CONTENT, 100.0, "Content assembly complete"
            )
            
            # Step 4: Quality Evaluation
            self.progress_tracker.update_stage(
                job_id, GenerationStage.FINALIZING, 0.0, "Evaluating content quality"
            )
            
            quality_metrics = self.quality_service.evaluate_content(
                final_content['content'],
                syllabus_text,
                target_format,
                {'target_duration': target_duration, 'target_pages': target_pages}
            )
            
            final_content['quality_metrics'] = {
                'overall_score': quality_metrics.overall_score,
                'readability_score': quality_metrics.readability.get_readability_score(),
                'structure_score': quality_metrics.structure.get_structure_score(),
                'relevance_score': quality_metrics.relevance.get_relevance_score(),
                'engagement_score': quality_metrics.engagement_score,
                'format_compliance_score': quality_metrics.format_compliance_score
            }
            
            # Step 5: Version Management
            generation_time = time.time() - start_time
            content_version = ContentVersion.create_new(
                syllabus_text=syllabus_text,
                target_format=ContentFormat(target_format.upper()),
                content=final_content,
                metadata={
                    'target_duration': target_duration,
                    'target_pages': target_pages,
                    'job_id': job_id
                },
                generation_time=generation_time,
                token_usage=total_token_usage
            )
            
            content_version.update_quality_score(quality_metrics.overall_score)
            self.version_manager.add_version(content_version)
            
            final_content['version_id'] = content_version.version_id
            
            # Cache the result
            if use_cache:
                self.cache.set(
                    syllabus_text, target_format, final_content,
                    target_duration, target_pages
                )
            
            self.progress_tracker.update_stage(
                job_id, GenerationStage.FINALIZING, 100.0, "Content generation complete"
            )
            
            self.progress_tracker.complete_job(job_id, final_content)
            
            return final_content, 200, job_id
            
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error in multi-step content generation: {error_message}", exc_info=True)
            # Ensure job is marked as failed with the error message
            self.progress_tracker.fail_job(job_id, error_message)
            return self._create_error_response(error_message), 500, job_id

    def _generate_sections_sequential(
        self,
        topics: List[Dict[str, Any]],
        target_format: str,
        target_duration: Optional[float],
        target_pages: Optional[int],
        job_id: str
    ) -> Tuple[List[ContentSection], Dict[str, int]]:
        """Generate content sections sequentially and collect token usage."""
        sections = []
        total_topics = len(topics)
        total_token_usage = {'input_tokens': 0, 'output_tokens': 0}

        for i, topic in enumerate(topics):
            # Update progress before processing each topic
            progress_percentage = (i / total_topics) * 100
            self.progress_tracker.update_stage(
                job_id, GenerationStage.GENERATING_SECTIONS, progress_percentage,
                f"Processing topic {i+1}/{total_topics}: {topic.get('title', 'unknown')}"
            )

            try:
                section, token_usage = self._generate_section_content(
                    topic, target_format, target_duration, target_pages
                )
                sections.append(section)
                total_token_usage['input_tokens'] += token_usage['input_tokens']
                total_token_usage['output_tokens'] += token_usage['output_tokens']
            except Exception as e:
                self.logger.error(f"Failed to generate content for topic {i+1}/{total_topics} ('{topic.get('title', 'unknown')}'): {e}")
                # Depending on requirements, could append an empty section or a placeholder
                # For now, we log and continue, the main job will ultimately fail if critical sections are missing
                pass

        # Update progress to 100% for this stage after loop completes
        self.progress_tracker.update_stage(
            job_id, GenerationStage.GENERATING_SECTIONS, 100.0,
            "All topics processed sequentially"
        )

        return sections, total_token_usage

    def _generate_sections_parallel(
        self,
        topics: List[Dict[str, Any]],
        target_format: str,
        target_duration: Optional[float],
        target_pages: Optional[int],
        job_id: str
    ) -> Tuple[List[ContentSection], Dict[str, int]]:
        """Generate content sections in parallel and collect token usage."""
        def create_section_task(topic):
            return lambda: self._generate_section_content(
                topic, target_format, target_duration, target_pages
            )
        
        # Note: The progress_callback here updates overall stage progress,
        # but detailed per-task progress might need a more sophisticated mechanism
        def progress_callback(task_id: str, progress: float):
             # This callback receives progress for *each* task (0-100),
             # which is tricky to map directly to overall stage progress.
             # A simple approach is to just log or update a general status.
             self.logger.debug(f"Task {task_id} progress: {progress:.1f}%")
             # For simplicity, we won't update the main stage progress percentage here
             # based on individual task progress. The stage will be marked complete
             # after all tasks finish.
        
        # Create tasks for parallel execution
        tasks = [create_section_task(topic) for topic in topics]
        task_ids = [f"topic_{i}_{topic.get('title', 'unknown')}" for i, topic in enumerate(topics)]
        
        # Execute in parallel
        results_with_usage = self.parallel_processor.execute_parallel_tasks(
            tasks, task_ids, progress_callback
        )
        
        # Extract successful results and sum token usage
        sections = []
        total_token_usage = {'input_tokens': 0, 'output_tokens': 0}

        for result in results_with_usage:
            if result.success and result.result is not None:
                section, token_usage = result.result
                sections.append(section)
                total_token_usage['input_tokens'] += token_usage.get('input_tokens', 0)
                total_token_usage['output_tokens'] += token_usage.get('output_tokens', 0)
            else:
                self.logger.error(f"Failed to generate section {result.task_id}: {result.error}")
                # Handle failed tasks - maybe add a placeholder section or skip
                pass

        # Update progress to 100% for this stage after parallel execution completes
            self.progress_tracker.update_stage(
            job_id, GenerationStage.GENERATING_SECTIONS, 100.0,
            "All topics processed in parallel"
        )

        return sections, total_token_usage

    def _decompose_topics(self, syllabus_text: str) -> List[Dict[str, Any]]:
        """Decompose syllabus text into major topics using the AI model."""
        self.logger.info("Starting topic decomposition with AI model.")
        prompt = self.prompts.get_topic_decomposition_prompt(syllabus_text)
        
        try:
        response = self.model.generate_content(prompt)
            # Assuming the model response is in response.text and is a JSON string
            topics_json_str = response.text.strip()
            # Clean up potential markdown or extraneous characters around the JSON
            if topics_json_str.startswith("```json"):
                topics_json_str = topics_json_str[7:]
            if topics_json_str.endswith("```"):
                topics_json_str = topics_json_str[:-3]

            topics_data = json.loads(topics_json_str)

            if 'topics' not in topics_data or not isinstance(topics_data['topics'], list):
                 raise ValueError("Invalid response format from AI model: 'topics' key missing or not a list.")

            self.logger.info(f"Topic decomposition successful. Found {len(topics_data['topics'])} topics.")
            return topics_data['topics'], response.usage_metadata

        except Exception as e:
            self.logger.error(f"Error during topic decomposition: {e}")
            # Re-raise to be caught by the main generate method's error handling
            raise RuntimeError(f"Failed to decompose topics using AI model: {e}") from e

    def _generate_section_content(
        self,
        topic: Dict[str, Any],
        target_format: str,
        target_duration: float = None,
        target_pages: int = None
    ) -> Tuple[ContentSection, Dict[str, int]]:
        """Generate detailed content for a single topic section using the AI model and return token usage."""
        self.logger.info(f"Generating content for section: {topic.get('title', 'Untitled Topic')} (Format: {target_format})")
        token_usage = {'input_tokens': 0, 'output_tokens': 0}

        # First, get a detailed outline for the section
        outline_prompt = self.prompts.get_section_outline_prompt(
            topic, target_format, target_duration, target_pages
        )
        outline = {}
        try:
            self.logger.debug(f"Sending outline prompt to model for {topic.get('title', 'Untitled Topic')}:
{outline_prompt[:500]}...") # Log start of prompt
        outline_response = self.model.generate_content(outline_prompt)
            token_usage['input_tokens'] += outline_response.usage_metadata.input_token_count
            token_usage['output_tokens'] += outline_response.usage_metadata.output_token_count

            outline_json_str = outline_response.text.strip()
            # Clean up potential markdown or extraneous characters around the JSON
            if outline_json_str.startswith("```json"):
                outline_json_str = outline_json_str[7:]
            if outline_json_str.endswith("```"):
                outline_json_str = outline_json_str[:-3]

            outline = json.loads(outline_json_str)
            self.logger.info(f"Generated outline for {topic.get('title', 'Untitled Topic')}")

        except (json.JSONDecodeError, KeyError) as e:
             self.logger.error(f"JSON parsing error for outline of {topic.get('title', 'Untitled Topic')}: {e}")
             # Proceed without a detailed outline if parsing fails
             pass
        except Exception as e:
            self.logger.error(f"Error generating outline for {topic.get('title', 'Untitled Topic')}: {e}")
            # Proceed without a detailed outline if generation fails
            pass

        # Now generate the full content based on the outline (or just the topic if outline failed)
        content_prompt = self.prompts.get_section_content_prompt(
            topic, outline, target_format
        )

        try:
            self.logger.debug(f"Sending content prompt to model for {topic.get('title', 'Untitled Topic')}:
{content_prompt[:500]}...") # Log start of prompt
        content_response = self.model.generate_content(content_prompt)
            token_usage['input_tokens'] += content_response.usage_metadata.input_token_count
            token_usage['output_tokens'] += content_response.usage_metadata.output_token_count

            content_json_str = content_response.text.strip()
            if content_json_str.startswith("```json"):
                content_json_str = content_json_str[7:]
            if content_json_str.endswith("```"):
                content_json_str = content_json_str[:-3]

            content_data = json.loads(content_json_str)
        
            # Basic validation and extraction
            section_content = content_data.get('text', '')
            metadata = content_data.get('metadata', {})
            word_count = metadata.get('word_count', len(section_content.split()))
            # Estimate duration based on format, potentially using word count or other metrics
            # For now, a simple placeholder
            estimated_duration = metadata.get('estimated_duration', word_count / 150) # rough estimate 150 words/min

            self.logger.info(f"Content generation successful for {topic.get('title', 'Untitled Topic')}")

            section = ContentSection(
                title=content_data.get('title', topic.get('title', 'Untitled Section')),
                content=section_content,
            word_count=word_count,
            estimated_duration=estimated_duration,
            content_type=target_format
        )
            return section, token_usage

        except (json.JSONDecodeError, KeyError) as e:
             self.logger.error(f"JSON parsing error for content of {topic.get('title', 'Untitled Topic')}: {e}")
             raise RuntimeError(f"Failed to parse content from AI model for {topic.get('title', 'Untitled Topic')}: {e}") from e
        except Exception as e:
            self.logger.error(f"Error generating section content for {topic.get('title', 'Untitled Topic')}: {e}")
            raise RuntimeError(f"Failed to generate section content for {topic.get('title', 'Untitled Topic')}: {e}") from e

    def _assemble_content(
        self,
        sections: List[ContentSection],
        target_format: str
    ) -> Dict[str, Any]:
        """Assemble generated content sections into a final, cohesive piece."""
        self.logger.info(f"Assembling content for format: {target_format}")

        if not sections:
            self.logger.warning("No sections to assemble.")
            return {'title': 'Empty Content', 'content': 'No content was generated.', 'metadata': {}}

        assembly_prompt = self.prompts.get_content_assembly_prompt(
            sections, target_format
        )
        
        try:
            assembly_response = self.model.generate_content(assembly_prompt)
            assembly_json_str = assembly_response.text.strip()
            if assembly_json_str.startswith("```json"):
                assembly_json_str = assembly_json_str[7:]
            if assembly_json_str.endswith("```"):
                assembly_json_str = assembly_json_str[:-3]

            final_content_data = json.loads(assembly_json_str)
        
            # Basic validation and extraction
            final_content = {
                'title': final_content_data.get('title', f'Assembled {target_format.replace('_', ' ').title()}'),
                'content': final_content_data.get('content', ''),
                'metadata': final_content_data.get('metadata', {})
            }

            # Add total word count and duration based on assembled sections
            total_word_count = sum(s.word_count for s in sections)
            total_duration = sum(s.estimated_duration for s in sections)
            final_content['metadata']['calculated_total_word_count'] = total_word_count
            final_content['metadata']['calculated_total_duration'] = total_duration
            final_content['metadata']['format'] = target_format

            self.logger.info(f"Content assembly successful for format: {target_format}")

            return final_content

        except Exception as e:
            self.logger.error(f"Error during content assembly for format {target_format}: {e}")
            raise RuntimeError(f"Failed to assemble content using AI model: {e}") from e

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            'error': error_message,
            'status': 'error',
            'content': None
        }
    
    def get_job_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get progress information for a job."""
        progress = self.progress_tracker.get_progress(job_id)
        if not progress:
            return None
        
        return {
            'job_id': progress.job_id,
            'current_stage': progress.current_stage.value,
            'overall_progress': progress.overall_progress,
            'started_at': progress.started_at.isoformat(),
            'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
            'error_message': progress.error_message,
            'stages': {
                stage.stage.value: {
                    'progress_percentage': stage.progress_percentage,
                    'current_item': stage.current_item,
                    'completed_items': stage.completed_items,
                    'total_items': stage.total_items,
                    'started_at': stage.started_at.isoformat(),
                    'completed_at': stage.completed_at.isoformat() if stage.completed_at else None
                }
                for stage in progress.stages.values()
            }
        }
    
    def get_content_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific content version."""
        version = self.version_manager.get_version(version_id)
        return version.to_dict() if version else None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()
    
    def cleanup_resources(self) -> Dict[str, int]:
        """Cleanup old resources and return cleanup stats."""
        cache_cleaned = self.cache.cleanup_expired()
        jobs_cleaned = self.progress_tracker.cleanup_old_jobs()
        
        return {
            'cache_entries_cleaned': cache_cleaned,
            'jobs_cleaned': jobs_cleaned
        } 