from unittest.mock import MagicMock, patch

import pytest

from app.core.config.settings import Settings  # Added import
from app.models.pydantic.content import (
    ContentOutline,
    GeneratedContent,
    PodcastScript,
    StudyGuide,
)
from app.services.comprehensive_content_validator import (  # Added import
    ComprehensiveValidationReport,
    ValidationStageResult,
)
from app.services.multi_step_content_generation_final import (
    EnhancedMultiStepContentGenerationService,
)

# This is the continuation of the tests - to be appended to the main file
# Fixtures like mock_settings, mock_content_outline
# are assumed to be defined in the main test file or a conftest.py

SAMPLE_JOB_ID = "test-job-part2"
SAMPLE_SYLLABUS = "Syllabus for part2 tests"


# Minimal mock_settings if not available from main test file via pytest
@pytest.fixture(
    scope="module"
)  # Use module scope if settings are constant for this part
def mock_settings_part2():
    return Settings(
        gcp_project_id="test-project-p2",
        gcp_location="us-central1",
        gemini_model_name="models/gemini-2.5-flash-preview-05-20",
        max_refinement_iterations=1,
        # Add other fields as necessary if EnhancedMultiStepContentGenerationService requires them
        # For example, if cache settings are used directly in tested methods:
        cache_max_size=100,
        cache_ttl_seconds=3600,
        cache_min_quality_retrieval=0.6,
        cache_min_quality_storage=0.7,
    )


@pytest.fixture(scope="module")
def mock_content_outline_part2():
    return ContentOutline(
        title="Mock Outline Part2",
        overview="Overview Part2",
        learning_objectives=["LO1p2", "LO2p2", "LO3p2"],
        sections=[
            {
                "section_number": 1,
                "title": "Sec1P2",
                "description": "DescP2",
                "key_points": ["KP1P2"],
            }
        ],
    )


@patch("app.services.multi_step_content_generation_final.vertexai.init")
@patch("app.services.multi_step_content_generation_final.GenerativeModel")
def test_derivative_generation_partial_failure(
    MockGenerativeModel,
    mock_vertex_init,
    mock_settings_part2,
    mock_content_outline_part2,
    mocker,  # Use part2 fixtures
):
    """Test handling of partial failures during derivative content generation."""
    # --- Arrange ---
    mocker.patch(
        "app.services.multi_step_content_generation_final.get_settings",
        return_value=mock_settings_part2,
    )
    service = EnhancedMultiStepContentGenerationService()

    # Common setup
    mocker.patch.object(service, "_analyze_input_complexity", return_value=MagicMock())
    mocker.patch.object(
        service,
        "_generate_master_content_outline",
        return_value=(
            mock_content_outline_part2,
            {"input_tokens": 10, "output_tokens": 20},
        ),
    )
    mocker.patch.object(
        service.content_validator,
        "pre_validate_input",
        return_value=MagicMock(quality_score=0.9),
    )
    mocker.patch.object(service.cache, "get", return_value=None)
    mocker.patch.object(service.cache, "set")

    # Mock individual derivative generation to simulate partial failure
    mocker.patch.object(
        service,
        "_generate_podcast_script",
        return_value=(
            PodcastScript(
                title="Test Podcast Title Valid Length",
                introduction="Intro " * 20,  # Approx 100 chars
                main_content="Main content " * 160,  # Approx 800 chars
                conclusion="Conclusion " * 20,  # Approx 100 chars
            ),
            {"input_tokens": 20, "output_tokens": 40},
        ),
    )

    # Study guide generation fails
    mocker.patch.object(
        service,
        "_generate_study_guide",
        side_effect=Exception("Failed to generate study guide"),
    )

    # Other derivatives succeed (returning None for content, but some token usage)
    mocker.patch.object(
        service,
        "_generate_one_pager_summary",
        return_value=(None, {"input_tokens": 5, "output_tokens": 5}),
    )
    mocker.patch.object(
        service,
        "_generate_detailed_reading_material",
        return_value=(None, {"input_tokens": 5, "output_tokens": 5}),
    )
    mocker.patch.object(
        service,
        "_generate_faq_collection",
        return_value=(None, {"input_tokens": 5, "output_tokens": 5}),
    )
    mocker.patch.object(
        service,
        "_generate_flashcard_collection",
        return_value=(None, {"input_tokens": 5, "output_tokens": 5}),
    )
    mocker.patch.object(
        service,
        "_generate_reading_guide_questions",
        return_value=(None, {"input_tokens": 5, "output_tokens": 5}),
    )

    # Validation should detect the missing study guide for comprehensive format
    mock_report = MagicMock(spec=ComprehensiveValidationReport)
    mock_report.overall_passed = False
    mock_report.overall_score = 0.6
    mock_report.stage_results = [
        MagicMock(
            spec=ValidationStageResult,
            stage_name="Completeness Validation",
            passed=False,
            issues_found=["Missing study_guide for comprehensive format"],
        )
    ]
    mocker.patch.object(
        service.comprehensive_validator,
        "validate_content_pipeline",
        return_value=mock_report,
    )

    # --- Act ---
    gc, meta, qm, tokens, error = service.generate_long_form_content(
        job_id=SAMPLE_JOB_ID,
        syllabus_text=SAMPLE_SYLLABUS,
        target_format="comprehensive",
        use_parallel=False,  # Sequential to control order
    )

    # --- Assert ---
    assert error is not None
    assert error["code"] == "QUALITY_THRESHOLD_NOT_MET"
    assert gc is None

    service._generate_study_guide.assert_called_once()
    service._generate_podcast_script.assert_called_once()


@patch("app.services.multi_step_content_generation_final.vertexai.init")
@patch("app.services.multi_step_content_generation_final.GenerativeModel")
def test_metadata_and_metrics_calculation(
    MockGenerativeModel,
    mock_vertex_init,
    mock_settings_part2,
    mock_content_outline_part2,
    mocker,  # Use part2 fixtures
):
    """Test correct calculation of metadata and quality metrics."""
    # --- Arrange ---
    mocker.patch(
        "app.services.multi_step_content_generation_final.get_settings",
        return_value=mock_settings_part2,
    )
    service = EnhancedMultiStepContentGenerationService()

    mocker.patch.object(service, "_analyze_input_complexity", return_value=MagicMock())
    mocker.patch.object(
        service,
        "_generate_master_content_outline",
        return_value=(
            mock_content_outline_part2,
            {"input_tokens": 100, "output_tokens": 200},
        ),
    )

    comprehensive_content = GeneratedContent(
        content_outline=mock_content_outline_part2,
        podcast_script=PodcastScript(
            title="Test Podcast Title Valid Length",
            introduction="Intro " * 20,
            main_content="Main " * 160,
            conclusion="Conclusion " * 20,
            estimated_duration_minutes=20.5,
        ),
        study_guide=StudyGuide(
            title="Test Study Guide Valid Length",
            overview="Overview " * 20,
            key_concepts=[f"Concept {i} valid length" for i in range(5)],
            detailed_content="Detailed content " * 100,  # Approx 500 chars
            summary="Summary " * 20,
        )
        # Add other content types if comprehensive_validator checks for them explicitly
    )

    mocker.patch.object(
        service,
        "_orchestrate_derivative_content_generation",
        return_value=(
            comprehensive_content,
            {"input_tokens": 500, "output_tokens": 1000},
        ),
    )

    mock_report = MagicMock(spec=ComprehensiveValidationReport)
    mock_report.overall_passed = True
    mock_report.overall_score = 0.92
    mock_report.stage_results = [
        MagicMock(
            spec=ValidationStageResult,
            stage_name="Structural Validation",
            score=0.95,
            passed=True,
        ),
        MagicMock(
            spec=ValidationStageResult,
            stage_name="Completeness Validation",
            score=0.90,
            passed=True,
        ),
        MagicMock(
            spec=ValidationStageResult,
            stage_name="Coherence Validation",
            score=0.88,
            passed=True,
        ),
        MagicMock(
            spec=ValidationStageResult,
            stage_name="Educational Value",
            score=0.94,
            passed=True,
        ),
    ]
    mocker.patch.object(
        service.comprehensive_validator,
        "validate_content_pipeline",
        return_value=mock_report,
    )

    mocker.patch.object(service.cache, "get", return_value=None)
    mocker.patch.object(service.cache, "set")
    mocker.patch.object(
        service.content_validator,
        "pre_validate_input",
        return_value=MagicMock(quality_score=0.9),
    )

    # --- Act ---
    gc, meta, qm, tokens, error = service.generate_long_form_content(
        job_id=SAMPLE_JOB_ID,
        syllabus_text=SAMPLE_SYLLABUS,
        target_format="comprehensive",
    )

    # --- Assert ---
    assert error is None
    assert gc is not None

    assert meta.source_syllabus_length == len(SAMPLE_SYLLABUS)
    assert meta.source_format == "comprehensive"
    assert meta.target_duration_minutes == 20.5
    assert meta.ai_model_used == mock_settings_part2.gemini_model_name
    assert meta.tokens_consumed == 1800

    assert qm.overall_score == 0.92
    assert qm.structure_score == 0.95
    assert qm.format_compliance_score is not None  # Should be calculated, not just > 0
    assert qm.content_length_compliance is True

    assert tokens["input_tokens"] == 600
    assert tokens["output_tokens"] == 1200
