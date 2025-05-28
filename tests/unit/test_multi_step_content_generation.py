import pytest
from unittest.mock import MagicMock, patch

# Mock the google.cloud.aiplatform import at the module level before importing the service
# This prevents the actual aiplatform.init() call during service initialization

# We still need a mock GenerativeModel instance to be returned
mock_model_instance = MagicMock(
    text='{}', # Default empty JSON response
    usage_metadata=MagicMock(input_token_count=0, output_token_count=0)
)

with patch('google.cloud.aiplatform.init'):
    with patch('google.cloud.aiplatform.GenerativeModel', return_value=mock_model_instance):
        from app.services.multi_step_content_generation import EnhancedMultiStepContentGenerationService, ContentSection
        from app.core.prompts.v1.multi_step_prompts import MultiStepPrompts
        from app.services.content_cache import ContentCacheService
        from app.services.progress_tracker import ProgressTracker
        from app.services.parallel_processor import ParallelProcessor
        from app.services.quality_metrics import QualityMetricsService
        from app.models.content_version import ContentVersionManager
        from app.core.config.settings import get_settings

# Helper functions for creating mock responses
def create_mock_ai_response(text: str, input_tokens: int = 0, output_tokens: int = 0) -> MagicMock:
    """Create a mock AI response with the given text and token counts."""
    return MagicMock(
        text=text,
        usage_metadata=MagicMock(
            input_token_count=input_tokens,
            output_token_count=output_tokens
        )
    )

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
def sample_topic():
    """Fixture providing a sample topic for testing."""
    return {
        "title": "Test Topic",
        "subtopics": [{
            "title": "Subtopic",
            "key_concepts": ["Concept"],
            "learning_objectives": ["Objective"]
        }]
    }

@pytest.fixture
def sample_sections():
    """Fixture providing sample content sections for testing."""
    return [
        ContentSection(
            title="Intro",
            content="Intro content.",
            word_count=2,
            estimated_duration=0.1,
            content_type="guide"
        ),
        ContentSection(
            title="Body",
            content="Body content.",
            word_count=3,
            estimated_duration=0.2,
            content_type="guide"
        )
    ]

@pytest.fixture
def mock_parallel_executor():
    """Fixture providing a mock parallel executor function."""
    def executor(tasks, task_ids, progress_callback):
        results = []
        for i, task in enumerate(tasks):
            try:
                result = task()
                results.append(MagicMock(success=True, result=result, task_id=task_ids[i]))
                if progress_callback:
                    progress_callback(task_ids[i], 100.0)
            except Exception as e:
                results.append(MagicMock(success=False, error=str(e), task_id=task_ids[i]))
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
def multi_step_service():
    """Fixture for the EnhancedMultiStepContentGenerationService with mocked dependencies."""
    with (
        # Patching the imported classes/functions within the service module
        patch('app.services.multi_step_content_generation.MultiStepPrompts') as MockPrompts,
        patch('app.services.multi_step_content_generation.ContentCacheService') as MockCacheService,
        patch('app.services.multi_step_content_generation.ProgressTracker') as MockProgressTracker,
        patch('app.services.multi_step_content_generation.ParallelProcessor') as MockParallelProcessor,
        patch('app.services.multi_step_content_generation.QualityMetricsService') as MockQualityService,
        patch('app.services.multi_step_content_generation.ContentVersionManager') as MockVersionManager,
        patch('app.services.multi_step_content_generation.aiplatform.GenerativeModel') as MockGenerativeModel # Re-patch GenerativeModel here too for safety
    ):

        # Configure the mocks to return mock instances when instantiated
        mock_prompts_instance = MockPrompts.return_value
        mock_cache_instance = MockCacheService.return_value
        mock_progress_tracker_instance = MockProgressTracker.return_value
        mock_parallel_processor_instance = MockParallelProcessor.return_value
        mock_quality_service_instance = MockQualityService.return_value
        mock_version_manager_instance = MockVersionManager.return_value

        # Instantiate the service - its __init__ will use the mocked dependencies
        service = EnhancedMultiStepContentGenerationService()

        # Attach the mock instances to the service fixture for easy access in tests
        service.mock_prompts = mock_prompts_instance
        service.mock_cache = mock_cache_instance
        service.mock_progress_tracker = mock_progress_tracker_instance
        service.mock_parallel_processor = mock_parallel_processor_instance
        service.mock_quality_service = mock_quality_service_instance
        service.mock_version_manager = mock_version_manager_instance
        service.mock_model = mock_model_instance

        yield service

def test_service_initialization(multi_step_service):
    """Verify that the service was initialized with mocked dependencies."""
    assert isinstance(multi_step_service.prompts, MagicMock)
    assert isinstance(multi_step_service.cache, MagicMock)
    assert isinstance(multi_step_service.progress_tracker, MagicMock)
    assert isinstance(multi_step_service.parallel_processor, MagicMock)
    assert isinstance(multi_step_service.quality_service, MagicMock)
    assert isinstance(multi_step_service.version_manager, MagicMock)
    assert isinstance(multi_step_service.model, MagicMock)

def test__decompose_topics_success(multi_step_service):
    """Tests successful topic decomposition."""
    syllabus_text = "This is a sample syllabus text about AI and ML."
    mock_prompt_response = """
    ```json
    {
        "topics": [
            {
                "title": "Topic 1: Introduction to AI",
                "subtopics": [],
                "key_concepts": ["AI", "Machine Learning"],
                "learning_objectives": ["Understand AI basics"],
                "suggested_formats": ["guide"]
            }
        ],
        "total_topics": 1,
        "estimated_total_duration": 30
    }
    ```
    """
    # Configure the mock AI model to return a specific response
    multi_step_service.mock_model.generate_content.return_value = MagicMock(
        text=mock_prompt_response,
        usage_metadata=MagicMock(input_token_count=10, output_token_count=20)
    )

    # Call the method
    topics, token_usage = multi_step_service._decompose_topics(syllabus_text)

    # Assertions
    multi_step_service.mock_prompts.get_topic_decomposition_prompt.assert_called_once_with(syllabus_text)
    multi_step_service.mock_model.generate_content.assert_called_once()
    
    assert isinstance(topics, list)
    assert len(topics) == 1
    assert topics[0]['title'] == "Topic 1: Introduction to AI"
    assert token_usage['input_token_count'] == 10
    assert token_usage['output_token_count'] == 20

def test__generate_section_content_success(multi_step_service, sample_topic):
    """Tests successful section content generation."""
    target_format = "guide"

    mock_outline_response = create_mock_ai_response(
        text='```json{"title": "Test Outline", "sections": [], "introduction": {}, "conclusion": {}}```',
        input_tokens=5,
        output_tokens=10
    )
    mock_content_response = create_mock_ai_response(
        text='```json{"title": "Test Content", "text": "This is the generated content.", "metadata": {"word_count": 5, "estimated_duration": 0.5}}```',
        input_tokens=15,
        output_tokens=25
    )

    # Configure mock AI model for two sequential calls
    multi_step_service.mock_model.generate_content.side_effect = [
        mock_outline_response,
        mock_content_response
    ]

    # Call the method
    section, token_usage = multi_step_service._generate_section_content(
        sample_topic, target_format
    )

    # Assertions
    multi_step_service.mock_prompts.get_section_outline_prompt.assert_called_once_with(
        sample_topic, target_format, None, None # Check default None values
    )
    multi_step_service.mock_prompts.get_section_content_prompt.assert_called_once()
    assert multi_step_service.mock_model.generate_content.call_count == 2 # Two calls made

    assert isinstance(section, ContentSection)
    assert section.title == "Test Content"
    assert section.content == "This is the generated content."
    assert section.word_count == 5
    assert section.estimated_duration == 0.5
    assert section.content_type == target_format

    assert token_usage['input_tokens'] == 5 + 15
    assert token_usage['output_tokens'] == 10 + 25

def test__assemble_content_success(multi_step_service, sample_sections):
    """Tests successful content assembly."""
    target_format = "guide"

    mock_assembly_response = create_mock_ai_response(
        text='```json{"title": "Assembled Guide", "content": "Intro content.\nBody content.", "metadata": {"format": "guide", "enhancements": []}}```',
        input_tokens=50,
        output_tokens=100
    )

    # Configure mock AI model response for assembly
    multi_step_service.mock_model.generate_content.return_value = mock_assembly_response

    # Call the method
    final_content, token_usage = multi_step_service._assemble_content(sample_sections, target_format)

    # Assertions
    multi_step_service.mock_prompts.get_content_assembly_prompt.assert_called_once_with(
        sample_sections, target_format
    )
    multi_step_service.mock_model.generate_content.assert_called_once()

    assert isinstance(final_content, dict)
    assert final_content['title'] == "Assembled Guide"
    assert final_content['content'] == "Intro content.\nBody content."
    assert 'metadata' in final_content
    assert final_content['metadata']['format'] == target_format
    assert final_content['metadata']['calculated_total_word_count'] == 5 # 2 + 3
    assert final_content['metadata']['calculated_total_duration'] == pytest.approx(0.3) # 0.1 + 0.2

    # Verify token usage
    assert token_usage['input_tokens'] == 50
    assert token_usage['output_tokens'] == 100

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

def test_generate_long_form_content_version_management(multi_step_service):
    """Tests version management during content generation."""
    syllabus_text = "Sample syllabus for version test."
    target_format = "guide"
    job_id = "test-job-version"

    # Configure mock responses
    mock_decompose_response = create_mock_ai_response(
        text='```json{"topics": [{"title": "Topic 1"}]}```',
        input_tokens=10,
        output_tokens=20
    )
    mock_section_outline_response = create_mock_ai_response(
        text='```json{"title": "Outline", "sections": []}```',
        input_tokens=5,
        output_tokens=10
    )
    mock_section_content_response = create_mock_ai_response(
        text='```json{"title": "Content", "text": "Section content.", "metadata": {"word_count": 3, "estimated_duration": 0.15}}```',
        input_tokens=15,
        output_tokens=25
    )
    mock_assemble_response = create_mock_ai_response(
        text='```json{"title": "Final Guide", "content": "Assembled content.", "metadata": {}}```',
        input_tokens=50,
        output_tokens=100
    )

    # Set up responses
    multi_step_service.mock_model.generate_content.side_effect = [
        mock_decompose_response,
        mock_section_outline_response,
        mock_section_content_response,
        mock_assemble_response
    ]

    # Mock quality metrics
    mock_quality_result = create_mock_quality_result()
    multi_step_service.mock_quality_service.evaluate_content.return_value = mock_quality_result
    multi_step_service.mock_progress_tracker.start_job.return_value = job_id

    # Call the method
    content, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text, target_format
    )

    # Assertions
    assert status_code == 200
    assert returned_job_id == job_id
    assert 'version_id' in content

    # Verify version was created with correct data
    version_call_args = multi_step_service.mock_version_manager.add_version.call_args[0][0]
    assert version_call_args.syllabus_text == syllabus_text
    assert version_call_args.target_format == target_format.upper()
    assert version_call_args.content == content
    assert version_call_args.metadata['job_id'] == job_id
    assert version_call_args.quality_score == 0.9

    # Verify token usage in version
    expected_input_tokens = 10 + 5 + 15 + 50  # decompose + outline + content + assemble
    expected_output_tokens = 20 + 10 + 25 + 100
    assert version_call_args.token_usage['input_tokens'] == expected_input_tokens
    assert version_call_args.token_usage['output_tokens'] == expected_output_tokens

def test_generate_long_form_content_progress_tracking(multi_step_service):
    """Tests progress tracking during content generation."""
    syllabus_text = "Sample syllabus for progress test."
    target_format = "guide"
    job_id = "test-job-progress"

    # Configure mock responses
    mock_decompose_response = create_mock_ai_response(
        text='```json{"topics": [{"title": "Topic 1"}]}```',
        input_tokens=10,
        output_tokens=20
    )
    mock_section_outline_response = create_mock_ai_response(
        text='```json{"title": "Outline", "sections": []}```',
        input_tokens=5,
        output_tokens=10
    )
    mock_section_content_response = create_mock_ai_response(
        text='```json{"title": "Content", "text": "Section content.", "metadata": {"word_count": 3, "estimated_duration": 0.15}}```',
        input_tokens=15,
        output_tokens=25
    )
    mock_assemble_response = create_mock_ai_response(
        text='```json{"title": "Final Guide", "content": "Assembled content.", "metadata": {}}```',
        input_tokens=50,
        output_tokens=100
    )

    # Set up responses
    multi_step_service.mock_model.generate_content.side_effect = [
        mock_decompose_response,
        mock_section_outline_response,
        mock_section_content_response,
        mock_assemble_response
    ]

    # Mock quality metrics
    mock_quality_result = create_mock_quality_result()
    multi_step_service.mock_quality_service.evaluate_content.return_value = mock_quality_result
    multi_step_service.mock_progress_tracker.start_job.return_value = job_id

    # Call the method
    content, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text, target_format
    )

    # Assertions
    assert status_code == 200
    assert returned_job_id == job_id

    # Verify progress tracking calls
    multi_step_service.mock_progress_tracker.start_job.assert_called_once_with(
        syllabus_text, target_format, None, None
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "INITIALIZING", 10.0, "Checking cache"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "DECOMPOSING_TOPICS", 0.0, "Starting topic decomposition"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "DECOMPOSING_TOPICS", 100.0, "Topic decomposition complete"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "GENERATING_SECTIONS", 0.0, "Generating content for 1 topics"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "GENERATING_SECTIONS", 100.0, "All topics processed sequentially"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "ASSEMBLING_CONTENT", 0.0, "Assembling final content"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "ASSEMBLING_CONTENT", 100.0, "Content assembly complete"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "FINALIZING", 0.0, "Evaluating content quality"
    )
    multi_step_service.mock_progress_tracker.update_stage.assert_any_call(
        job_id, "FINALIZING", 100.0, "Content generation complete"
    )
    multi_step_service.mock_progress_tracker.complete_job.assert_called_once_with(job_id, content)

def test__decompose_topics_invalid_json(multi_step_service):
    """Tests handling of invalid JSON response during topic decomposition."""
    syllabus_text = "This is a sample syllabus text about AI and ML."
    invalid_json_response = "This is not a valid JSON response"
    
    multi_step_service.mock_model.generate_content.return_value = MagicMock(
        text=invalid_json_response,
        usage_metadata=MagicMock(input_token_count=10, output_token_count=20)
    )

    with pytest.raises(RuntimeError) as exc_info:
        multi_step_service._decompose_topics(syllabus_text)
    
    assert "Failed to decompose topics" in str(exc_info.value)
    assert "JSON" in str(exc_info.value).lower()

def test__generate_section_content_api_error(multi_step_service):
    """Tests handling of API errors during section content generation."""
    topic = {
        "title": "Test Topic",
        "subtopics": []
    }
    target_format = "guide"

    # Simulate API error
    multi_step_service.mock_model.generate_content.side_effect = Exception("API Error")

    with pytest.raises(Exception) as exc_info:
        multi_step_service._generate_section_content(topic, target_format)
    
    assert "API Error" in str(exc_info.value)

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

def test_generate_long_form_content_parallel(multi_step_service, mock_parallel_executor):
    """Tests parallel content generation with multiple topics."""
    syllabus_text = "Sample syllabus for parallel processing test."
    target_format = "guide"
    job_id = "test-job-parallel"

    # Configure mock responses for parallel processing
    mock_decompose_response = create_mock_ai_response(
        text='```json{"topics": [{"title": "Topic 1"}, {"title": "Topic 2"}, {"title": "Topic 3"}]}```',
        input_tokens=10,
        output_tokens=20
    )

    # Create mock responses for each topic
    mock_section_responses = []
    for i in range(3):
        mock_section_responses.extend([
            create_mock_ai_response(
                text=f'```json{{"title": "Outline {i+1}", "sections": []}}```',
                input_tokens=5,
                output_tokens=10
            ),
            create_mock_ai_response(
                text=f'```json{{"title": "Content {i+1}", "text": "Section {i+1} content.", "metadata": {{"word_count": 3, "estimated_duration": 0.15}}}}```',
                input_tokens=15,
                output_tokens=25
            )
        ])

    mock_assemble_response = create_mock_ai_response(
        text='```json{"title": "Final Guide", "content": "Assembled parallel content.", "metadata": {}}```',
        input_tokens=50,
        output_tokens=100
    )

    # Set up all responses in sequence
    multi_step_service.mock_model.generate_content.side_effect = [
        mock_decompose_response,
        *mock_section_responses,
        mock_assemble_response
    ]

    # Mock parallel processor
    multi_step_service.mock_parallel_processor.execute_parallel_tasks.side_effect = mock_parallel_executor
    multi_step_service.mock_progress_tracker.start_job.return_value = job_id

    # Mock quality metrics
    mock_quality_result = create_mock_quality_result()
    multi_step_service.mock_quality_service.evaluate_content.return_value = mock_quality_result

    # Call the main generation method with parallel processing enabled
    content, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text, target_format, use_parallel=True
    )

    # Assertions
    assert status_code == 200
    assert returned_job_id == job_id
    assert content['title'] == "Final Guide"
    assert content['content'] == "Assembled parallel content."
    assert 'quality_metrics' in content
    assert content['quality_metrics']['overall_score'] == 0.9

    # Verify parallel processing was used
    multi_step_service.mock_parallel_processor.execute_parallel_tasks.assert_called_once()
    call_args = multi_step_service.mock_parallel_processor.execute_parallel_tasks.call_args[0]
    assert len(call_args[0]) == 3  # Number of tasks
    assert len(call_args[1]) == 3  # Number of task IDs

    # Verify token usage
    version_call_args = multi_step_service.mock_version_manager.add_version.call_args[0][0]
    expected_input_tokens = 10 + (3 * (5 + 15)) + 50  # decompose + (3 topics * (outline + content)) + assemble
    expected_output_tokens = 20 + (3 * (10 + 25)) + 100
    assert version_call_args.token_usage['input_tokens'] == expected_input_tokens
    assert version_call_args.token_usage['output_tokens'] == expected_output_tokens

def test_generate_long_form_content_parallel_failure(multi_step_service):
    """Tests handling of failures during parallel content generation."""
    syllabus_text = "Sample syllabus for parallel failure test."
    target_format = "guide"
    job_id = "test-job-parallel-fail"

    # Configure mock responses
    mock_decompose_response = MagicMock(
        text='```json{"topics": [{"title": "Topic 1"}, {"title": "Topic 2"}]}```',
        usage_metadata=MagicMock(input_token_count=10, output_token_count=20)
    )

    # Mock parallel processor to simulate one task failure
    def mock_parallel_execute(tasks, task_ids, progress_callback):
        results = []
        for i, task in enumerate(tasks):
            if i == 0:  # First task fails
                results.append(MagicMock(
                    success=False,
                    error="Task failed",
                    task_id=task_ids[i]
                ))
            else:
                try:
                    result = task()
                    results.append(MagicMock(
                        success=True,
                        result=result,
                        task_id=task_ids[i]
                    ))
                except Exception as e:
                    results.append(MagicMock(
                        success=False,
                        error=str(e),
                        task_id=task_ids[i]
                    ))
            if progress_callback:
                progress_callback(task_ids[i], 100.0)
        return results

    multi_step_service.mock_model.generate_content.return_value = mock_decompose_response
    multi_step_service.mock_parallel_processor.execute_parallel_tasks.side_effect = mock_parallel_execute
    multi_step_service.mock_progress_tracker.start_job.return_value = job_id

    # Call the main generation method
    content, status_code, returned_job_id = multi_step_service.generate_long_form_content(
        syllabus_text, target_format, use_parallel=True
    )

    # Assertions
    assert status_code == 500
    assert "error" in content
    assert returned_job_id == job_id
    multi_step_service.mock_progress_tracker.fail_job.assert_called_once_with(job_id, content['error']) 