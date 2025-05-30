import pytest
from unittest.mock import MagicMock, patch, call
import json

# Mock the google.cloud.aiplatform import at the module level before importing the service
# This prevents the actual aiplatform.init() call during service initialization

# We still need a mock GenerativeModel instance to be returned
mock_model_instance = MagicMock(
    usage_metadata=MagicMock(prompt_token_count=0, candidates_token_count=0)
)

with patch('google.cloud.aiplatform.init'):
    with patch('google.cloud.aiplatform.GenerativeModel', return_value=mock_model_instance):
        from app.services.multi_step_content_generation import EnhancedMultiStepContentGenerationService
        # from app.core.prompts.v1.multi_step_prompts import MultiStepPrompts # No longer used directly by service
        from app.services.prompts import PromptService # Import new PromptService
        from app.services.content_cache import ContentCacheService
        from app.services.progress_tracker import ProgressTracker, GenerationStage
        from app.services.parallel_processor import ParallelProcessor
        from app.services.quality_metrics import QualityMetricsService
        from app.models.content_version import ContentVersionManager, ContentVersion, ContentFormat
        from app.core.config.settings import get_settings
        from app.models.pydantic.content import (
            ContentOutline, PodcastScript, StudyGuide, GeneratedContent,
            FAQCollection, FlashcardCollection, OnePagerSummary, DetailedReadingMaterial, ReadingGuideQuestions
        )
        from pydantic import BaseModel

# Helper functions for creating mock responses
def create_mock_ai_response(json_data: dict, input_tokens: int = 10, output_tokens: int = 20) -> MagicMock:
    mock_response = MagicMock()
    mock_response.text = json.dumps(json_data)
    mock_response.usage_metadata = MagicMock(prompt_token_count=input_tokens, candidates_token_count=output_tokens)
    return mock_response

def create_mock_quality_result(
    overall_score: float = 0.9,
    readability_score: float = 0.8,
    structure_score: float = 0.9,
    relevance_score: float = 0.95,
    engagement_score: float = 0.85,
    format_compliance_score: float = 0.9
) -> MagicMock:
    """Create a mock quality metrics result with the given scores."""
    mock_result = MagicMock()
    mock_result.overall_score = overall_score
    mock_result.readability = MagicMock()
    mock_result.readability.get_readability_score.return_value = readability_score
    mock_result.structure = MagicMock()
    mock_result.structure.get_structure_score.return_value = structure_score
    mock_result.relevance = MagicMock()
    mock_result.relevance.get_relevance_score.return_value = relevance_score
    mock_result.engagement_score = engagement_score
    mock_result.format_compliance_score = format_compliance_score
    return mock_result

# Fixtures for common test data
@pytest.fixture
def mock_content_outline() -> ContentOutline:
    return ContentOutline(
        title="Master Outline Title",
        overview="This is a great master overview.",
        learning_objectives=["Objective 1", "Objective 2", "Objective 3"],
        sections=[
            {"section_number": 1, "title": "Section 1", "description": "Desc 1", "key_points": ["KP1"]},
            {"section_number": 2, "title": "Section 2", "description": "Desc 2", "key_points": ["KP2"]},
            {"section_number": 3, "title": "Section 3", "description": "Desc 3", "key_points": ["KP3"]}
        ]
    )

@pytest.fixture
def mock_podcast_script() -> PodcastScript:
    return PodcastScript(
        title="Master Outline Title",
        introduction="Podcast intro.",
        main_content="Podcast main content based on outline.",
        conclusion="Podcast conclusion."
    )

@pytest.fixture
def mock_study_guide() -> StudyGuide:
    return StudyGuide(
        title="Master Outline Title",
        overview="Study guide overview.",
        key_concepts=["KC1", "KC2", "KC3", "KC4", "KC5"],
        detailed_content="Detailed study guide content based on outline.",
        summary="Study guide summary."
    )

@pytest.fixture
def mock_faq_collection() -> FAQCollection:
    return FAQCollection(
        title="Master Outline Title - FAQs",
        faqs=[
            {"question": "FAQ Q1?", "answer": "FAQ A1"},
            {"question": "FAQ Q2?", "answer": "FAQ A2"}
        ]
    )

@pytest.fixture
def mock_flashcard_collection() -> FlashcardCollection:
    return FlashcardCollection(
        title="Master Outline Title - Flashcards",
        flashcards=[
            {"front": "Flashcard Front 1", "back": "Flashcard Back 1"},
            {"front": "Flashcard Front 2", "back": "Flashcard Back 2"}
        ]
    )

@pytest.fixture
def mock_one_pager_summary() -> OnePagerSummary:
    return OnePagerSummary(
        title="Master Outline Title - One Pager",
        summary_points=["Point 1", "Point 2", "Point 3"],
        main_content="This is the main content of the one-pager summary."
    )

@pytest.fixture
def mock_detailed_reading_material() -> DetailedReadingMaterial:
    return DetailedReadingMaterial(
        title="Master Outline Title - Detailed Reading",
        introduction="Intro to detailed reading.",
        sections=[
            {"title": "Reading Section 1", "content": "Content for reading section 1."},
            {"title": "Reading Section 2", "content": "Content for reading section 2."}
        ],
        conclusion="Conclusion of detailed reading."
    )

@pytest.fixture
def mock_reading_guide_questions() -> ReadingGuideQuestions:
    return ReadingGuideQuestions(
        title="Master Outline Title - Reading Questions",
        questions=[
            {"question_text": "What is concept X?", "expected_answer_summary": "Concept X is..."},
            {"question_text": "Explain Y.", "expected_answer_summary": "Y can be explained as..."}
        ]
    )

@pytest.fixture
def mock_parallel_executor():
    """Fixture providing a mock parallel executor function."""
    def executor(tasks, task_ids, progress_callback):
        results = []
        for i, task in enumerate(tasks):
            try:
                result, tokens = task() # Assuming task returns (PydanticObject|None, token_dict)
                results.append(MagicMock(success=True, result=(result, tokens), task_id=task_ids[i]))
                if progress_callback:
                    progress_callback(task_ids[i], 100.0)
            except Exception as e:
                results.append(MagicMock(success=False, error=str(e), task_id=task_ids[i], result=(None, {})))
        return results
    return executor

# Ensure settings are mocked to avoid requiring real env vars during test setup
@pytest.fixture(autouse=True)
def mock_settings():
    with patch('app.services.multi_step_content_generation.get_settings') as mock_get_settings:
        with patch('app.core.config.settings.get_settings') as mock_core_get_settings:
            mock_settings = MagicMock()
            mock_settings.gcp_project_id = "test-project"
            mock_settings.gcp_location = "test-location"
            mock_settings.gemini_model_name = "test-model"
            mock_settings.elevenlabs_api_key = "test-key"
            # Add other necessary settings attributes if they are accessed
            mock_settings.max_tokens_per_content_type = {}
            mock_settings.max_total_tokens = 10000
            mock_settings.max_generation_time = 90
            mock_settings.max_retries = 3
            mock_settings.retry_delay = 2

            mock_get_settings.return_value = mock_settings
            mock_core_get_settings.return_value = mock_settings
            yield mock_settings

@pytest.fixture
def multi_step_service(mock_settings):
    """Fixture for the EnhancedMultiStepContentGenerationService with mocked dependencies."""
    with patch('app.services.multi_step_content_generation.aiplatform.GenerativeModel', return_value=mock_model_instance) as MockGM,\
         patch('app.services.multi_step_content_generation.PromptService') as MockPromptService, \
         patch('app.services.multi_step_content_generation.ContentCacheService') as MockCacheService,\
         patch('app.services.multi_step_content_generation.ProgressTracker') as MockProgressTracker,\
         patch('app.services.multi_step_content_generation.ParallelProcessor') as MockParallelProcessor,\
         patch('app.services.multi_step_content_generation.QualityMetricsService') as MockQualityService,\
         patch('app.services.multi_step_content_generation.ContentVersionManager') as MockVersionManager:
        
        # Mock the __init__ of PromptService if it's instantiated inside EnhancedMultiStepContentGenerationService's __init__
        # This is already done by patching 'app.services.multi_step_content_generation.PromptService'
        
        service = EnhancedMultiStepContentGenerationService()
        service.model = mock_model_instance # Ensure model is mocked

        # The service now has an instance of PromptService at self.prompt_service
        # We can mock its get_prompt method directly on the instance or ensure the patched class returns a mock instance
        # The patch for PromptService already makes its instance a MagicMock.
        # So, service.prompt_service will be a MagicMock.
        
        # service.mock_prompts = MockPrompts.return_value # Old way
        # No need to assign service.mock_prompts, service.prompt_service is already a mock.
        
        service.mock_cache = MockCacheService.return_value # Keep if cache is used as before
        service.mock_progress_tracker = MockProgressTracker.return_value # Keep
        service.mock_parallel_processor = MockParallelProcessor.return_value # Keep
        service.mock_quality_service = MockQualityService.return_value
        service.mock_version_manager = MockVersionManager.return_value

        yield service

def test_service_initialization(multi_step_service):
    """Verify that the service was initialized with mocked dependencies."""
    assert isinstance(multi_step_service.prompt_service, MagicMock) # Changed attribute name
    assert isinstance(multi_step_service.cache, MagicMock)
    assert isinstance(multi_step_service.progress_tracker, MagicMock)
    assert isinstance(multi_step_service.parallel_processor, MagicMock)
    assert isinstance(multi_step_service.quality_service, MagicMock)
    assert isinstance(multi_step_service.version_manager, MagicMock)
    assert isinstance(multi_step_service.model, MagicMock)

def test_generate_long_form_content_cache_hit(multi_step_service):
    """Tests content generation with cache hit."""
    syllabus_text = "Sample syllabus for cache test."
    target_format = "guide"
    job_id = "test-job-cache"

    # Mock cached content
    cached_content = {
        'title': 'Cached Guide',
        'content': 'Cached content.',
        'metadata': {'format': 'guide'},
        'quality_metrics': {'overall_score': 0.9}
    }
    multi_step_service.mock_cache.get.return_value = cached_content
    multi_step_service.mock_progress_tracker.start_job.return_value = job_id

    # Call the method
    content, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text, target_format, use_cache=True
    )

    # Assertions
    assert status_code == 200
    assert returned_job_id == job_id
    assert content == cached_content
    multi_step_service.mock_cache.get.assert_called_once_with(
        syllabus_text, target_format, None, None
    )
    multi_step_service.mock_model.generate_content.assert_not_called()
    multi_step_service.mock_progress_tracker.complete_job.assert_called_once_with(job_id, content)

def test_generate_long_form_content_timeout(multi_step_service):
    """Tests handling of timeout during long-form content generation."""
    syllabus_text = "Sample syllabus for timeout test."
    target_format = "guide"
    job_id = "test-job-timeout"

    # Configure mock to simulate timeout
    multi_step_service.mock_model.generate_content.side_effect = TimeoutError("Request timed out")
    multi_step_service.mock_progress_tracker.start_job.return_value = job_id

    content, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text, target_format
    )

    assert status_code == 500
    assert "timeout" in content['error'].lower()
    assert returned_job_id == job_id
    multi_step_service.mock_progress_tracker.fail_job.assert_called_once_with(job_id, content['error'])

def test_generate_long_form_content_new_flow_success(
    multi_step_service,
    mock_content_outline,
    mock_podcast_script,
    mock_study_guide,
    mock_faq_collection,
    mock_flashcard_collection,
    mock_one_pager_summary,
    mock_detailed_reading_material,
    mock_reading_guide_questions,
    mock_parallel_executor
):
    """Tests the new outline-driven content generation flow for success, including all derivative types."""
    syllabus_text = "A great syllabus about LLMs and Python programming."
    target_format = "comprehensive"
    job_id = "test-job-new-flow"

    multi_step_service.mock_progress_tracker.start_job.return_value = job_id
    multi_step_service.mock_cache.get.return_value = None

    mock_outline_ai_response = create_mock_ai_response(mock_content_outline.model_dump(), 10, 200)
    mock_podcast_ai_response = create_mock_ai_response(mock_podcast_script.model_dump(), 10, 150)
    mock_study_guide_ai_response = create_mock_ai_response(mock_study_guide.model_dump(), 10, 120)
    mock_faq_ai_response = create_mock_ai_response(mock_faq_collection.model_dump(), 5, 50)
    mock_flashcard_ai_response = create_mock_ai_response(mock_flashcard_collection.model_dump(), 5, 60)
    mock_one_pager_ai_response = create_mock_ai_response(mock_one_pager_summary.model_dump(), 5, 80)
    mock_detailed_reading_ai_response = create_mock_ai_response(mock_detailed_reading_material.model_dump(), 10, 250)
    mock_reading_questions_ai_response = create_mock_ai_response(mock_reading_guide_questions.model_dump(), 5, 70)

    # Store call_args for prompts to check later, as side_effect doesn't allow easy inspection of specific calls
    prompt_calls = {}

    def mock_generate_content_side_effect(prompt_str):
        # This side_effect needs to be more robust if prompts are very similar.
        # For now, relying on unique elements in prompt strings.
        if "Master Content Outline" in prompt_str: # Assuming this is unique enough
            prompt_calls['outline'] = prompt_str
            return mock_outline_ai_response
        elif "Podcast Script" in prompt_str:
            prompt_calls['podcast'] = prompt_str
            return mock_podcast_ai_response
        elif "Study Guide" in prompt_str:
            prompt_calls['study_guide'] = prompt_str
            return mock_study_guide_ai_response
        elif "FAQs" in prompt_str:
            prompt_calls['faqs'] = prompt_str
            return mock_faq_ai_response
        elif "Flashcards" in prompt_str:
            prompt_calls['flashcards'] = prompt_str
            return mock_flashcard_ai_response
        elif "One-Pager Summary" in prompt_str:
            prompt_calls['one_pager'] = prompt_str
            return mock_one_pager_ai_response
        elif "Detailed Reading Material" in prompt_str:
            prompt_calls['detailed_reading'] = prompt_str
            return mock_detailed_reading_ai_response
        elif "Reading Guide Questions" in prompt_str:
            prompt_calls['reading_questions'] = prompt_str
            return mock_reading_questions_ai_response
        else:
            # Fallback for any unexpected prompt
            return create_mock_ai_response({}, input_tokens=1, output_tokens=1)

    multi_step_service.model.generate_content.side_effect = mock_generate_content_side_effect
    
    # Mocking the prompt generation calls via the new PromptService
    # The service.prompt_service is already a MagicMock due to the patch.
    # We need to configure its get_prompt method.
    def mock_get_prompt_side_effect(prompt_name_key, **kwargs):
        # Return simple strings, actual formatting isn't tested here, just that it's called.
        if prompt_name_key == "master_content_outline":
            return f"Prompt for Master Content Outline with {kwargs.get('syllabus_text', '')}"
        return f"Prompt for {prompt_name_key} with {kwargs.get('outline_json', '')}"

    multi_step_service.prompt_service.get_prompt.side_effect = mock_get_prompt_side_effect


    def updated_mock_parallel_executor(tasks, task_ids, progress_callback):
        results = []
        mock_objects = {
            "podcast_script": (mock_podcast_script, {'input_tokens':10, 'output_tokens':150}),
            "study_guide": (mock_study_guide, {'input_tokens':10, 'output_tokens':120}),
            "faqs": (mock_faq_collection, {'input_tokens':5, 'output_tokens':50}),
            "flashcards": (mock_flashcard_collection, {'input_tokens':5, 'output_tokens':60}),
            "one_pager_summary": (mock_one_pager_summary, {'input_tokens':5, 'output_tokens':80}),
            "detailed_reading_material": (mock_detailed_reading_material, {'input_tokens':10, 'output_tokens':250}),
            "reading_guide_questions": (mock_reading_guide_questions, {'input_tokens':5, 'output_tokens':70}),
        }
        for i, task_lambda in enumerate(tasks):
            task_id = task_ids[i]
            if task_id in mock_objects:
                obj, tokens = mock_objects[task_id]
                results.append(MagicMock(success=True, result=(obj, tokens), task_id=task_id))
            else: # Should not happen if all tasks are defined
                results.append(MagicMock(success=True, result=(None, {'input_tokens':1, 'output_tokens':1}), task_id=task_id))
            if progress_callback: progress_callback(task_id, 100.0)
        return results

    multi_step_service.mock_parallel_processor.execute_parallel_tasks.side_effect = updated_mock_parallel_executor

    mock_quality_eval_result = create_mock_quality_result(overall_score=0.88)
    multi_step_service.mock_quality_service.evaluate_content.return_value = mock_quality_eval_result

    service_return_dict, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text=syllabus_text, 
        target_format=target_format, 
        use_cache=False, 
        use_parallel=True
    )

    assert status_code == 200 # All types are mocked to succeed
    assert returned_job_id == job_id
    assert service_return_dict is not None

    # Verify master outline generation
    multi_step_service.prompt_service.get_prompt.assert_any_call("master_content_outline", syllabus_text=syllabus_text)
    assert service_return_dict['content_outline'] == mock_content_outline.model_dump()
    assert service_return_dict['title'] == mock_content_outline.title
    
    # Verify all derivative content types were attempted and populated
    master_outline_json_arg = mock_content_outline.model_dump_json()
    
    # Check that get_prompt was called for each derivative type
    expected_prompt_calls = [
        call("podcast_script", outline_json=master_outline_json_arg),
        call("study_guide", outline_json=master_outline_json_arg),
        call("faq_collection", outline_json=master_outline_json_arg),
        call("flashcards", outline_json=master_outline_json_arg),
        call("one_pager_summary", outline_json=master_outline_json_arg),
        call("detailed_reading_material", outline_json=master_outline_json_arg),
        call("reading_guide_questions", outline_json=master_outline_json_arg),
    ]
    for expected_call in expected_prompt_calls:
        multi_step_service.prompt_service.get_prompt.assert_any_call(*expected_call.args, **expected_call.kwargs)

    assert service_return_dict['podcast_script'] == mock_podcast_script.model_dump()
    assert service_return_dict['study_guide'] == mock_study_guide.model_dump()
    assert service_return_dict['faqs'] == mock_faq_collection.model_dump()
    assert service_return_dict['flashcards'] == mock_flashcard_collection.model_dump()
    assert service_return_dict['one_pager_summary'] == mock_one_pager_summary.model_dump()
    assert service_return_dict['detailed_reading_material'] == mock_detailed_reading_material.model_dump()
    assert service_return_dict['reading_guide_questions'] == mock_reading_guide_questions.model_dump()

    multi_step_service.mock_parallel_processor.execute_parallel_tasks.assert_called_once()
    
    # Verify token aggregation
    expected_input_tokens = 10 + 10 + 10 + 5 + 5 + 5 + 10 + 5 # Outline + 7 derivatives
    expected_output_tokens = 200 + 150 + 120 + 50 + 60 + 80 + 250 + 70 # Outline + 7 derivatives
    
    added_version = multi_step_service.mock_version_manager.add_version.call_args[0][0]
    assert isinstance(added_version, ContentVersion)
    assert added_version.token_usage['input_tokens'] == expected_input_tokens
    assert added_version.token_usage['output_tokens'] == expected_output_tokens
    assert added_version.content['content_outline']['title'] == "Master Outline Title"
    assert added_version.quality_score == 0.88

    multi_step_service.mock_cache.set.assert_called_once()

    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, GenerationStage.GENERATING_OUTLINE, 100.0, "Master content outline generated"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, GenerationStage.GENERATING_DERIVATIVES, 100.0, "All derivative content generation attempted"
    )
    multi_step_service.mock_progress_tracker.complete_job.assert_called_once()

def test_generate_long_form_content_outline_failure(multi_step_service):
    """Tests the new flow when master content outline generation fails."""
    syllabus_text = "Syllabus that will cause outline failure."
    target_format = "guide"
    job_id = "test-job-outline-fail"

    multi_step_service.mock_progress_tracker.start_job.return_value = job_id
    multi_step_service.mock_cache.get.return_value = None

    # Simulate _call_generative_model returning None for the outline due to, e.g., Pydantic error
    # This requires mocking _call_generative_model itself or ensuring model.generate_content leads to it.
    # For simplicity, let's make model.generate_content return a response that _call_generative_model will fail to parse for ContentOutline
    multi_step_service.model.generate_content.return_value = create_mock_ai_response({"bad_field": "no_title"}, input_tokens=5, output_tokens=0)

    service_return_dict, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text=syllabus_text, target_format=target_format, use_cache=False
    )
    
    assert status_code == 500
    assert returned_job_id == job_id
    assert "error" in service_return_dict
    # The error message comes from _call_generative_model or _generate_master_content_outline
    assert "Pydantic validation error for Master Content Outline" in service_return_dict['error'] or \
           "Master content outline generation failed" in service_return_dict['error'] # If _generate_master_content_outline returns None
    
    multi_step_service.prompt_service.get_prompt.assert_any_call("master_content_outline", syllabus_text=syllabus_text)
    multi_step_service.mock_parallel_processor.execute_parallel_tasks.assert_not_called()
    multi_step_service.mock_progress_tracker.fail_job.assert_called_once()

def test_generate_long_form_content_partial_success(
    multi_step_service,
    mock_content_outline,
    mock_podcast_script, # Will succeed
    # mock_study_guide, # This one will fail
    mock_faq_collection # Will succeed
):
    """Tests partial success: outline and some derivatives succeed, one fails."""
    syllabus_text = "Syllabus for partial success test."
    target_format = "comprehensive"
    job_id = "test-job-partial-success"

    multi_step_service.mock_progress_tracker.start_job.return_value = job_id
    multi_step_service.mock_cache.get.return_value = None

    # Mock AI responses
    mock_outline_ai_response = create_mock_ai_response(mock_content_outline.model_dump(), 10, 200)
    mock_podcast_ai_response = create_mock_ai_response(mock_podcast_script.model_dump(), 10, 150)
    # Study guide will fail, so its AI response mock isn't strictly needed if _call_generative_model handles it
    # but let's assume _call_generative_model returns None for it.
    mock_faq_ai_response = create_mock_ai_response(mock_faq_collection.model_dump(), 5, 50)

    # Mock prompt generation using the new service
    def mock_get_prompt_partial_side_effect(prompt_name_key, **kwargs):
        if prompt_name_key == "master_content_outline":
            return "Prompt for Master Content Outline"
        elif prompt_name_key == "podcast_script":
            return "Prompt for Podcast Script"
        elif prompt_name_key == "study_guide":
            return "Prompt for Study Guide" # This one will lead to a simulated failure
        elif prompt_name_key == "faq_collection": # Renamed from faqs for consistency with PromptService
            return "Prompt for FAQs"
        # Add other prompt keys if they are part of content_types_to_generate
        return f"Generic prompt for {prompt_name_key}"
    multi_step_service.prompt_service.get_prompt.side_effect = mock_get_prompt_partial_side_effect


    # Side effect for the main model call
    def mock_model_generate_content_side_effect(prompt_str):
        if "Master Content Outline" in prompt_str:
            return mock_outline_ai_response
        # For derivatives, _call_generative_model is called internally by _generate_specific_content_type
        # We will mock _generate_specific_content_type directly for finer control in parallel execution mock
        # Or, more simply, mock the behavior of _call_generative_model for the failing type
        elif "Podcast Script" in prompt_str:
             return mock_podcast_ai_response
        elif "Study Guide" in prompt_str: # This one will cause a failure in _call_generative_model
             raise Exception("Simulated LLM error for Study Guide")
        elif "FAQs" in prompt_str:
             return mock_faq_ai_response
        # For other types, return a generic empty valid Pydantic model or make them fail too
        return create_mock_ai_response({})


    multi_step_service.model.generate_content.side_effect = mock_model_generate_content_side_effect
    
    # Mock parallel executor to simulate one failure
    def updated_mock_parallel_executor(tasks, task_ids, progress_callback):
        results = []
        mock_objects_success = {
            "podcast_script": (mock_podcast_script, {'input_tokens':10, 'output_tokens':150}),
            "faqs": (mock_faq_collection, {'input_tokens':5, 'output_tokens':50}),
        }
        # Simulate other types also succeeding with minimal data to keep test focused
        other_successful_types = ["flashcards", "one_pager_summary", "detailed_reading_material", "reading_guide_questions"]
        
        for i, task_lambda in enumerate(tasks):
            task_id = task_ids[i]
            if task_id in mock_objects_success:
                obj, tokens = mock_objects_success[task_id]
                results.append(MagicMock(success=True, result=(obj, tokens), task_id=task_id))
            elif task_id == "study_guide": # Explicit failure for study_guide
                results.append(MagicMock(success=False, error="Simulated failure for study_guide", task_id=task_id, result=(None, {})))
            elif task_id in other_successful_types: # Other types succeed with placeholder
                 # Create minimal valid Pydantic objects for these if needed by GeneratedContent
                 # For simplicity, assume None is acceptable if the Pydantic model allows Optional
                 results.append(MagicMock(success=True, result=(None, {'input_tokens':1, 'output_tokens':1}), task_id=task_id))
            else: # Should not happen
                results.append(MagicMock(success=False, error="Unknown task", task_id=task_id, result=(None, {})))

            if progress_callback: progress_callback(task_id, 100.0)
        return results

    multi_step_service.mock_parallel_processor.execute_parallel_tasks.side_effect = updated_mock_parallel_executor
    
    multi_step_service.mock_quality_service.evaluate_content.return_value = create_mock_quality_result()

    service_return_dict, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text=syllabus_text, target_format=target_format, use_cache=False, use_parallel=True
    )

    assert status_code == 202 # Partial success
    assert returned_job_id == job_id
    assert service_return_dict is not None
    
    assert service_return_dict['content_outline'] == mock_content_outline.model_dump()
    assert service_return_dict['podcast_script'] == mock_podcast_script.model_dump()
    assert service_return_dict['study_guide'] is None # Failed
    assert service_return_dict['faqs'] == mock_faq_collection.model_dump()
    # Other types might be None or empty based on the mock_parallel_executor
    assert service_return_dict.get("flashcards") is None 

    multi_step_service.mock_version_manager.add_version.assert_called_once()
    multi_step_service.mock_cache.set.assert_called_once()
    multi_step_service.mock_progress_tracker.complete_job.assert_called_once()


# --- DEPRECATED TESTS ---
# The following tests were for the old, section-based generation flow and are now deprecated.

# def test__decompose_topics_success(multi_step_service):
#     """[DEPRECATED] Tests successful topic decomposition."""
#     pass

# def test__generate_section_content_success(multi_step_service, sample_topic):
#     """[DEPRECATED] Tests successful section content generation."""
#     pass

# def test__assemble_content_success(multi_step_service, sample_sections):
#     """[DEPRECATED] Tests successful content assembly."""
#     pass

# def test_generate_long_form_content_version_management(multi_step_service):
#     """[DEPRECATED] Tests version management during content generation - OLD FLOW."""
#     pass

# def test_generate_long_form_content_progress_tracking(multi_step_service):
#     """[DEPRECATED] Tests progress tracking during content generation - OLD FLOW."""
#     pass

# def test__decompose_topics_invalid_json(multi_step_service):
#     """[DEPRECATED] Tests handling of invalid JSON response during topic decomposition."""
#     pass

# def test__generate_section_content_api_error(multi_step_service):
#     """[DEPRECATED] Tests handling of API errors during section content generation."""
#     pass

# def test_generate_long_form_content_parallel(multi_step_service, mock_parallel_executor):
#     """[DEPRECATED] Tests parallel content generation with multiple topics - OLD FLOW."""
#     pass

# def test_generate_long_form_content_parallel_failure(multi_step_service):
#     """[DEPRECATED] Tests handling of failures during parallel content generation - OLD FLOW."""
#     pass

# --- END OF DEPRECATED TESTS --- 

def test_generate_long_form_content_cache_hit_new_flow(multi_step_service, mock_content_outline):
    """Tests content generation with cache hit for the new outline-driven flow."""
    syllabus_text = "Syllabus for cache hit new flow."
    target_format = "comprehensive" # Or any other format
    job_id = "test-job-cache-new-flow"
    
    # Expected cache key parameters based on current implementation
    cache_key_params = (syllabus_text, "all_types_from_outline", None, None)


    # Mock cached content - this should be the dictionary returned by the service
    # which is then used to populate ContentResponse by the API route.
    # It should contain all fields that generate_long_form_content would normally return.
    cached_service_return_dict = {
        "job_id": job_id,
        "version_id": "cached-version-id",
        "quality_metrics": {"overall_score": 0.95},
        "content_outline": mock_content_outline.model_dump(), # Example, real cache would have all fields
        "podcast_script": None, # etc. for all derivative types
        "study_guide": None,
        "one_pager_summary": None,
        "detailed_reading_material": None,
        "faqs": None,
        "flashcards": None,
        "reading_guide_questions": None,
        "metadata": {
            'source_syllabus_length': len(syllabus_text),
            'source_format': target_format,
            'target_duration_minutes': None,
            'target_pages_count': None,
            'calculated_total_word_count': 500, 
            'ai_model_used': multi_step_service.settings.gemini_model_name,
            'tokens_consumed': 550
        },
        "title": mock_content_outline.title,
        "content": mock_content_outline.overview 
    }
    multi_step_service.mock_cache.get.return_value = cached_service_return_dict
    multi_step_service.mock_progress_tracker.start_job.return_value = job_id

    # Call the method
    content_dict, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text, target_format, use_cache=True
    )

    # Assertions
    assert status_code == 200 # Assuming cache hit means full success
    assert returned_job_id == job_id
    assert content_dict == cached_service_return_dict
    multi_step_service.mock_cache.get.assert_called_once_with(*cache_key_params)
    # Ensure _generate_master_content_outline and _generate_specific_content_type are not called
    multi_step_service.model.generate_content.assert_not_called() # More direct check
    multi_step_service.mock_parallel_processor.execute_parallel_tasks.assert_not_called()
    multi_step_service.mock_progress_tracker.complete_job.assert_called_once_with(job_id, cached_service_return_dict)


def test_generate_long_form_content_timeout_in_llm_call(multi_step_service):
    """Tests handling of timeout during an LLM call within _call_generative_model."""
    syllabus_text = "Syllabus for LLM timeout test."
    target_format = "guide"
    job_id = "test-job-llm-timeout"

    multi_step_service.mock_progress_tracker.start_job.return_value = job_id
    multi_step_service.mock_cache.get.return_value = None # Cache miss

    # Simulate timeout during the first LLM call (e.g., for master outline)
    # The _call_generative_model method is where the actual LLM call happens.
    # We need to make the `self.model.generate_content` call within it raise a TimeoutError.
    
    # Mock the prompt first using the new service
    multi_step_service.prompt_service.get_prompt.return_value = "Prompt for Master Content Outline" # Simplified for this test
    
    # Now mock the model's generate_content to raise TimeoutError
    multi_step_service.model.generate_content.side_effect = TimeoutError("LLM request timed out")

    service_return_dict, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text=syllabus_text, target_format=target_format, use_cache=False
    )
    
    assert status_code == 500 # Expecting internal server error
    assert returned_job_id == job_id
    assert "error" in service_return_dict
    # The error message might be wrapped, check for key phrases
    assert "Error generating Master Content Outline with LLM" in service_return_dict['error'] or "timeout" in service_return_dict['error'].lower()
    
    multi_step_service.prompt_service.get_prompt.assert_any_call("master_content_outline", syllabus_text=syllabus_text)
    multi_step_service.model.generate_content.assert_called_once() # It was called once before timeout
    multi_step_service.mock_parallel_processor.execute_parallel_tasks.assert_not_called() # Should not reach parallel processing
    multi_step_service.mock_progress_tracker.fail_job.assert_called_once()
    # Check that the fail_job message contains timeout information
    fail_message = multi_step_service.mock_progress_tracker.fail_job.call_args[0][1]
    assert "timeout" in fail_message.lower() or "error generating master content outline" in fail_message.lower()
