"""Comprehensive unit tests for quality services including validation, semantic analysis, refinement, and prompt optimization."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.pydantic.content import (
    ContentOutline,
    DetailedReadingMaterial,
    FAQCollection,
    FAQItem,
    FlashcardCollection,
    GeneratedContent,
    MainTopic,
    OnePagerSummary,
    OutlineSection,
    PodcastScript,
    ReadingGuideQuestions,
    StudyGuide,
    Subtopic,
)
from app.models.pydantic.feedback import FeedbackBase
from app.services.comprehensive_content_validator import (
    ComprehensiveContentValidator,
    ComprehensiveValidationReport,
)
from app.services.enhanced_content_validator import (
    EnhancedContentValidator,
    FactualValidation,
    InputValidation,
    RedundancyReport,
    StructureValidation,
    ValidationIssue,
    ValidationResult,
)
from app.services.prompt_optimizer import (
    OptimizationResult,
    PromptMetrics,
    PromptOptimizer,
)
from app.services.quality_refinement import (
    QualityRefinementEngine,
    RefinementResult,
    RefinementSuggestion,
)
from app.services.semantic_validator import (
    ConsistencyItem,
    ConsistencyReport,
    SemanticConsistencyValidator,
)

# --- Fixtures ---


@pytest.fixture
def mock_generated_content():
    """Create a mock GeneratedContent object for testing."""
    outline = ContentOutline(
        title="Test Outline",
        description="Test description",
        main_topics=[
            MainTopic(
                title="Topic 1",
                description="Description 1",
                subtopics=[
                    Subtopic(title="Subtopic 1.1", description="Description 1.1"),
                    Subtopic(title="Subtopic 1.2", description="Description 1.2"),
                ],
            ),
            MainTopic(
                title="Topic 2",
                description="Description 2",
                subtopics=[
                    Subtopic(title="Subtopic 2.1", description="Description 2.1"),
                ],
            ),
        ],
    )

    return GeneratedContent(
        content_outline=outline,
        podcast_script=PodcastScript(
            title="Test Podcast",
            script="Test podcast script content",
            duration_minutes=10,
        ),
        study_guide=StudyGuide(
            title="Test Study Guide",
            content="Test study guide content",
            key_points=["Point 1", "Point 2"],
        ),
        one_pager_summary=OnePagerSummary(
            title="Test Summary", summary="Test summary content"
        ),
        detailed_reading_material=DetailedReadingMaterial(
            title="Test Reading", content="Test reading content"
        ),
        faqs=FAQCollection(
            title="Test FAQs",
            questions=[
                {"question": "Q1", "answer": "A1"},
                {"question": "Q2", "answer": "A2"},
            ],
        ),
        flashcards=FlashcardCollection(
            title="Test Flashcards",
            cards=[
                {"front": "Front 1", "back": "Back 1"},
                {"front": "Front 2", "back": "Back 2"},
            ],
        ),
        reading_guide_questions=ReadingGuideQuestions(
            title="Test Questions",
            questions=[{"question": "Question 1"}, {"question": "Question 2"}],
        ),
    )


@pytest.fixture
def enhanced_validator():
    """Create an EnhancedContentValidator instance for testing."""
    return EnhancedContentValidator()


@pytest.fixture
def comprehensive_validator():
    """Create a ComprehensiveContentValidator instance for testing."""
    return ComprehensiveContentValidator()


# --- Test EnhancedContentValidator ---


def test_pre_validate_input_good_quality(enhanced_validator: EnhancedContentValidator):
    """Test pre-validation of high quality input."""
    syllabus_text = "This is a well-structured syllabus about advanced machine learning. It covers topics like deep neural networks, reinforcement learning, and generative models. Learning objectives include understanding complex algorithms and applying them to real-world problems. The target audience is graduate students with a strong mathematical background."
    result = enhanced_validator.pre_validate_input(syllabus_text)

    assert isinstance(result, InputValidation)
    assert result.quality_score > 0.7  # Expect good score
    assert result.word_count == len(syllabus_text.split())
    assert not result.clarity_issues
    assert result.estimated_complexity == "high"  # Based on keywords


def test_pre_validate_input_poor_quality(enhanced_validator: EnhancedContentValidator):
    """Test pre-validation of poor quality input."""
    syllabus_text = "ai stuff. make it good. for all."
    result = enhanced_validator.pre_validate_input(syllabus_text)

    assert result.quality_score < 0.5  # Expect poor score
    assert "Vague language detected" in " ".join(result.clarity_issues)
    assert "Add more detail" in " ".join(result.enhancement_suggestions)
    assert result.estimated_complexity == "low"


def test_validate_structure_pass(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test structure validation with valid content."""
    # Assuming 'comprehensive' requires outline, podcast, study_guide
    result = enhanced_validator.validate_structure(
        mock_generated_content, "comprehensive"
    )
    assert isinstance(result, StructureValidation)
    assert result.has_required_sections is True
    assert not result.missing_sections
    assert result.section_balance_score > 0.5  # Should be reasonably balanced
    assert result.logical_flow_score > 0.5  # Heuristic, check if positive


def test_validate_structure_missing_sections(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test structure validation with missing sections."""
    mock_generated_content.podcast_script = (
        None  # Remove a required component for 'comprehensive'
    )
    result = enhanced_validator.validate_structure(
        mock_generated_content, "comprehensive"
    )
    assert result.has_required_sections is False
    assert "podcast_script" in result.missing_sections


def test_validate_complete_pipeline_happy_path(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test complete validation pipeline with good content."""
    # Mock internal validation methods to return passing results
    enhanced_validator.pre_validate_input = MagicMock(
        return_value=InputValidation(
            quality_score=0.9,
            readability_score=0.9,
            completeness_score=0.9,
            clarity_issues=[],
            enhancement_suggestions=[],
            word_count=100,
            estimated_complexity="medium",
        )
    )
    enhanced_validator.validate_structure = MagicMock(
        return_value=StructureValidation(
            has_required_sections=True,
            missing_sections=[],
            section_balance_score=0.8,
            logical_flow_score=0.8,
            hierarchy_issues=[],
            format_compliance={},
        )
    )
    enhanced_validator.validate_factual_consistency = MagicMock(
        return_value=FactualValidation(
            consistency_score=0.9,
            contradictions_found=[],
            unsupported_claims=[],
            fact_density_score=0.8,
            citation_coverage=0.7,
        )
    )
    enhanced_validator.detect_redundancy = MagicMock(
        return_value=RedundancyReport(
            redundancy_score=0.1,
            repeated_sections=[],
            verbose_passages=[],
            consolidation_opportunities=[],
        )
    )
    enhanced_validator.validate_semantic_consistency = MagicMock(
        return_value=FactualValidation(
            consistency_score=0.9,
            contradictions_found=[],
            unsupported_claims=[],
            fact_density_score=0.8,
            citation_coverage=0.7,
        )
    )

    validation_result = enhanced_validator.validate_complete_pipeline(
        content=mock_generated_content,
        syllabus_text="Valid syllabus text for testing.",
        target_format="comprehensive",
    )

    assert isinstance(validation_result, ValidationResult)
    assert validation_result.is_valid is True
    assert validation_result.overall_score > 0.75  # Expect good overall score
    assert not validation_result.issues


def test_validate_complete_pipeline_semantic_failure(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test validation pipeline with semantic validation failure."""
    # Mock semantic validation to return a poor score
    enhanced_validator.validate_semantic_consistency = MagicMock(
        return_value=FactualValidation(
            consistency_score=0.5,  # Below threshold
            contradictions_found=[],
            unsupported_claims=[],
            fact_density_score=0.8,
            citation_coverage=0.7,
        )
    )

    # Mock other stages to pass
    enhanced_validator.pre_validate_input = MagicMock(
        return_value=InputValidation(
            quality_score=0.9,
            readability_score=0.9,
            completeness_score=0.9,
            clarity_issues=[],
            enhancement_suggestions=[],
            word_count=100,
            estimated_complexity="medium",
        )
    )
    enhanced_validator.validate_structure = MagicMock(
        return_value=StructureValidation(
            has_required_sections=True,
            missing_sections=[],
            section_balance_score=0.8,
            logical_flow_score=0.8,
            hierarchy_issues=[],
            format_compliance={},
        )
    )
    enhanced_validator.validate_factual_consistency = MagicMock(
        return_value=FactualValidation(
            consistency_score=0.9,
            contradictions_found=[],
            unsupported_claims=[],
            fact_density_score=0.8,
            citation_coverage=0.7,
        )
    )
    enhanced_validator.detect_redundancy = MagicMock(
        return_value=RedundancyReport(
            redundancy_score=0.1,
            repeated_sections=[],
            verbose_passages=[],
            consolidation_opportunities=[],
        )
    )

    validation_result = enhanced_validator.validate_complete_pipeline(
        content=mock_generated_content,
        syllabus_text="Valid syllabus text for testing.",
        target_format="comprehensive",
    )

    assert validation_result.is_valid is False  # Should fail due to low semantic score
    assert any(
        issue.issue_type == "low_semantic_alignment"
        for issue in validation_result.issues
    )
    assert (
        "Improve content alignment with outline topics"
        in validation_result.recommendations
    )


def test_validate_complete_pipeline_strict_mode(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test validation in strict mode where any issue causes failure."""
    # Mock a minor issue that would normally pass
    enhanced_validator.pre_validate_input = MagicMock(
        return_value=InputValidation(
            quality_score=0.75,  # Just above normal threshold
            readability_score=0.8,
            completeness_score=0.8,
            clarity_issues=["Minor clarity issue"],
            enhancement_suggestions=[],
            word_count=100,
            estimated_complexity="medium",
        )
    )
    enhanced_validator.validate_structure = MagicMock(
        return_value=StructureValidation(
            has_required_sections=True,
            missing_sections=[],
            section_balance_score=0.8,
            logical_flow_score=0.8,
            hierarchy_issues=[],
            format_compliance={},
        )
    )
    enhanced_validator.validate_factual_consistency = MagicMock(
        return_value=FactualValidation(
            consistency_score=0.9,
            contradictions_found=[],
            unsupported_claims=[],
            fact_density_score=0.8,
            citation_coverage=0.7,
        )
    )
    enhanced_validator.detect_redundancy = MagicMock(
        return_value=RedundancyReport(
            redundancy_score=0.1,
            repeated_sections=[],
            verbose_passages=[],
            consolidation_opportunities=[],
        )
    )
    enhanced_validator.validate_semantic_consistency = MagicMock(
        return_value=FactualValidation(
            consistency_score=0.9,
            contradictions_found=[],
            unsupported_claims=[],
            fact_density_score=0.8,
            citation_coverage=0.7,
        )
    )

    # In strict mode, even minor issues should cause failure
    validation_result = enhanced_validator.validate_complete_pipeline(
        content=mock_generated_content,
        syllabus_text="Valid syllabus text for testing.",
        target_format="comprehensive",
        strict=True,
    )

    assert validation_result.is_valid is False  # Should fail in strict mode
    assert any(
        "clarity" in issue.description.lower() for issue in validation_result.issues
    )


def test_enhanced_validator_calculate_readability_score(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _calculate_readability_score helper."""
    assert (
        enhanced_validator._calculate_readability_score("Short simple sentence.", 4)
        > 0.8
    )
    assert enhanced_validator._calculate_readability_score(
        "This is a very long and convoluted sentence that goes on and on and on and on.",
        20,
    ) < enhanced_validator._calculate_readability_score(
        "This is a very long and convoluted sentence that goes on and on.", 10
    )  # Longer avg length = lower score
    assert (
        enhanced_validator._calculate_readability_score("No punctuation here", 4) < 0.8
    )  # Penalize no punctuation
    assert enhanced_validator._calculate_readability_score(
        "Sentence one. Sentence two.\nParagraph break.", 3
    ) > enhanced_validator._calculate_readability_score(
        "Sentence one. Sentence two.", 3
    )  # Bonus for paragraph


def test_enhanced_validator_assess_input_completeness(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _assess_input_completeness helper."""
    text_with_indicators = "This course will help you learn to analyze data. We will cover topics like statistics. Objective: understand models. Focus on Python."
    text_without_indicators = "Some random text about a subject."
    assert enhanced_validator._assess_input_completeness(
        text_with_indicators
    ) > enhanced_validator._assess_input_completeness(text_without_indicators)
    assert enhanced_validator._assess_input_completeness(
        "Short text"
    ) < enhanced_validator._assess_input_completeness(
        "This is a much longer text that provides more details about the subject matter, potentially indicating a more complete input for generation purposes, at least fifty words long."
    )


def test_enhanced_validator_identify_clarity_issues(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _identify_clarity_issues helper."""
    assert "Vague language detected" in " ".join(
        enhanced_validator._identify_clarity_issues(
            "This thing is about various stuff etc."
        )
    )
    assert "Possible incomplete sentences" in " ".join(
        enhanced_validator._identify_clarity_issues("This is one. And this")
    )
    assert "Many abbreviations used" in " ".join(
        enhanced_validator._identify_clarity_issues(
            "Use NASA, FBI, CIA, NSA, DOD, DOE for this task."
        )
    )
    assert "No clear educational context" in " ".join(
        enhanced_validator._identify_clarity_issues("A story about a cat.")
    )


def test_enhanced_validator_generate_input_suggestions(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _generate_input_suggestions helper."""
    suggestions_low_completeness = enhanced_validator._generate_input_suggestions(
        "short text", [], 0.3
    )
    assert any("Add more detail" in s for s in suggestions_low_completeness)

    suggestions_vague = enhanced_validator._generate_input_suggestions(
        "long text about various stuff",
        ["Vague language detected: various, stuff"],
        0.8,
    )
    assert any("Replace vague terms" in s for s in suggestions_vague)

    suggestions_no_level = enhanced_validator._generate_input_suggestions(
        "A course on Python programming.", [], 0.8
    )
    assert any("Specify the difficulty level" in s for s in suggestions_no_level)


def test_enhanced_validator_estimate_complexity(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _estimate_complexity helper."""
    assert (
        enhanced_validator._estimate_complexity("Introduction to basics of Python.", 6)
        == "low"
    )
    assert (
        enhanced_validator._estimate_complexity(
            "Advanced theoretical physics research methodology and evaluation.", 7
        )
        == "high"
    )
    assert (
        enhanced_validator._estimate_complexity(
            "A general course on project management.", 6
        )
        == "medium"
    )


def test_enhanced_validator_get_section_lengths(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test _get_section_lengths helper."""
    lengths = enhanced_validator._get_section_lengths(mock_generated_content)
    assert "outline" in lengths and lengths["outline"] > 0
    assert "podcast" in lengths and lengths["podcast"] > 0
    assert "guide" in lengths and lengths["guide"] > 0


def test_enhanced_validator_calculate_balance_score(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _calculate_balance_score helper."""
    assert (
        enhanced_validator._calculate_balance_score({"s1": 100, "s2": 110, "s3": 90})
        > 0.8
    )  # Well balanced
    assert (
        enhanced_validator._calculate_balance_score({"s1": 100, "s2": 10, "s3": 200})
        < 0.5
    )  # Poorly balanced
    assert (
        enhanced_validator._calculate_balance_score({"s1": 100}) == 1.0
    )  # Single section is perfectly balanced


def test_enhanced_validator_assess_logical_flow(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test _assess_logical_flow helper."""
    # Make guide content reference outline sections for higher score
    mock_generated_content.study_guide.detailed_content += (
        " Section One is important. Then Section Two follows."
    )
    score_good_flow = enhanced_validator._assess_logical_flow(mock_generated_content)

    mock_generated_content_no_flow = mock_generated_content.model_copy(deep=True)
    mock_generated_content_no_flow.study_guide.detailed_content = "Random text."
    mock_generated_content_no_flow.podcast_script.main_content = "More random text."
    score_bad_flow = enhanced_validator._assess_logical_flow(
        mock_generated_content_no_flow
    )

    assert score_good_flow > score_bad_flow


def test_enhanced_validator_check_hierarchy_issues(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test _check_hierarchy_issues helper."""
    assert not enhanced_validator._check_hierarchy_issues(
        mock_generated_content
    )  # Fixture is fine

    mock_generated_content.content_outline.sections[
        1
    ].section_number = 5  # Break sequence
    issues = enhanced_validator._check_hierarchy_issues(mock_generated_content)
    assert any("Section numbering is not sequential" in issue for issue in issues)

    mock_generated_content.content_outline.sections[
        0
    ].key_points = []  # Empty key points
    issues_empty_kp = enhanced_validator._check_hierarchy_issues(mock_generated_content)
    assert any("has no key points" in issue for issue in issues_empty_kp)


def test_enhanced_validator_check_format_compliance(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test _check_format_compliance helper."""
    compliance_podcast = enhanced_validator._check_format_compliance(
        mock_generated_content, "podcast"
    )
    assert compliance_podcast["has_introduction"] is True
    assert compliance_podcast["appropriate_length"] is True  # Based on fixture length

    mock_generated_content.podcast_script.main_content = "Too short."
    compliance_podcast_short = enhanced_validator._check_format_compliance(
        mock_generated_content, "podcast"
    )
    assert compliance_podcast_short["appropriate_length"] is False

    compliance_guide = enhanced_validator._check_format_compliance(
        mock_generated_content, "guide"
    )
    assert compliance_guide["has_key_concepts"] is True  # Fixture has 5


def test_enhanced_validator_collect_text_segments(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test _collect_text_segments helper."""
    segments = enhanced_validator._collect_text_segments(mock_generated_content)
    assert len(segments) > 0
    assert any(seg[0].startswith("outline_section_") for seg in segments)
    assert any(seg[0].startswith("podcast_") for seg in segments)
    assert any(seg[0].startswith("guide_") for seg in segments)


def test_enhanced_validator_calculate_text_similarity(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _calculate_text_similarity helper."""
    text1 = "This is a test sentence."
    text2 = "This is a test sentence."
    text3 = "This is a completely different sentence."
    text4 = "this is a test sentence."  # Case difference
    assert enhanced_validator._calculate_text_similarity(text1, text2) == 1.0
    assert enhanced_validator._calculate_text_similarity(text1, text3) < 0.5
    assert (
        enhanced_validator._calculate_text_similarity(text1, text4) == 1.0
    )  # Should be case-insensitive


def test_enhanced_validator_calculate_verbosity(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _calculate_verbosity helper."""
    verbose_text = (
        "It is very, very important to actually understand that this thing, you know, is basically a sort of complex stuff. In fact, we really need to consider it."
        * 3
    )
    concise_text = (
        "Understanding this complex topic is crucial. We must consider it." * 3
    )
    assert enhanced_validator._calculate_verbosity(
        verbose_text
    ) > enhanced_validator._calculate_verbosity(concise_text)
    assert (
        enhanced_validator._calculate_verbosity("Short text.") == 0.0
    )  # Too short to be verbose


def test_enhanced_validator_cluster_by_topic(
    enhanced_validator: EnhancedContentValidator,
):
    """Test _cluster_by_topic helper."""
    segments = [
        ("loc1", "This segment is about machine learning and AI."),
        ("loc2", "Another segment discussing artificial intelligence (AI)."),
        ("loc3", "This part covers Python programming."),
        ("loc4", "More on machine learning algorithms."),
    ]
    clusters = enhanced_validator._cluster_by_topic(segments)
    assert (
        "machine" in clusters
        or "learning" in clusters
        or "intelligence" in clusters
        or "ai" in clusters
    )
    if "machine" in clusters:
        assert "loc1" in clusters["machine"] and "loc4" in clusters["machine"]
    if "python" in clusters:
        assert "loc3" in clusters["python"]


def test_enhanced_validator_are_contradictory(
    enhanced_validator: EnhancedContentValidator,
):
    """Test the _are_contradictory helper method."""
    # Clear contradiction (negation)
    assert (
        enhanced_validator._are_contradictory(
            "The sky is blue.", "The sky is not blue."
        )
        is True
    )
    assert (
        enhanced_validator._are_contradictory("Cats can fly.", "Cats cannot fly.")
        is True
    )

    # Conflicting numbers
    assert (
        enhanced_validator._are_contradictory(
            "The project cost is $100.", "The project cost is $200."
        )
        is True
    )
    assert (
        enhanced_validator._are_contradictory(
            "There are 5 apples.", "There are 10 apples."
        )
        is True
    )

    # No contradiction
    assert (
        enhanced_validator._are_contradictory("The sky is blue.", "The grass is green.")
        is False
    )
    assert (
        enhanced_validator._are_contradictory(
            "The project cost is $100.", "The project duration is 2 weeks."
        )
        is False
    )

    # Similar but not contradictory
    assert (
        enhanced_validator._are_contradictory("The cat is black.", "The dog is black.")
        is False
    )
    assert (
        enhanced_validator._are_contradictory(
            "The system is fast.", "The system is very fast."
        )
        is False
    )  # Might need refinement if "very" implies a contradiction

    # Edge cases
    assert enhanced_validator._are_contradictory("", "The sky is not blue.") is False
    assert enhanced_validator._are_contradictory("The sky is blue.", "") is False
    assert enhanced_validator._are_contradictory("", "") is False

    # More subtle negation
    assert (
        enhanced_validator._are_contradictory(
            "The feature will be implemented.", "The feature will not be implemented."
        )
        is True
    )


def test_enhanced_validator_facts_match(enhanced_validator: EnhancedContentValidator):
    """Test the _facts_match helper method."""
    # Nearly identical
    assert (
        enhanced_validator._facts_match(
            "The capital of France is Paris.", "The capital of France is Paris."
        )
        is True
    )
    assert (
        enhanced_validator._facts_match(
            "The capital of France is Paris.", "paris is the capital of france."
        )
        is True
    )  # Case-insensitive

    # Similar wording, same meaning
    assert (
        enhanced_validator._facts_match(
            "Water boils at 100 degrees Celsius.", "At 100°C, water starts to boil."
        )
        is True
    )

    # Different facts
    assert (
        enhanced_validator._facts_match("The sky is blue.", "The grass is green.")
        is False
    )

    # Similar topic, different details
    assert (
        enhanced_validator._facts_match(
            "The project deadline is Monday.", "The project deadline is Friday."
        )
        is False
    )

    # Partial overlap but different meaning
    assert (
        enhanced_validator._facts_match("The car is red and fast.", "The car is red.")
        is False
    )  # One is a subset, but not a "match" for full fact

    # Edge cases
    assert (
        enhanced_validator._facts_match("", "Paris is the capital of France.") is False
    )
    assert (
        enhanced_validator._facts_match("Paris is the capital of France.", "") is False
    )
    assert enhanced_validator._facts_match("", "") is True  # Empty strings are similar


def test_detect_redundancy_with_repetition(
    enhanced_validator: EnhancedContentValidator,
):
    """Test redundancy detection with actual repetitive content."""
    # Create content with obvious repetition
    repetitive_content = GeneratedContent(
        content_outline=ContentOutline(
            title="Test Title",
            overview="This is about machine learning. Machine learning is important. We will learn about machine learning.",
            learning_objectives=[
                "Learn about ML concepts and principles",
                "Understand ML algorithms and techniques",
                "Apply ML methods to solve problems",
            ],
            sections=[
                OutlineSection(
                    section_number=1,
                    title="Introduction to ML",
                    description="ML is machine learning. Machine learning is ML.",
                    key_points=[
                        "ML basics explained",
                        "Machine learning basics covered",
                        "Basics of ML introduced",
                    ],
                ),
                OutlineSection(
                    section_number=2,
                    title="ML Applications",
                    description="Applications of machine learning. ML has many applications.",
                    key_points=[
                        "ML in healthcare sector",
                        "Machine learning in healthcare",
                    ],
                ),
            ],
        )
    )

    result = enhanced_validator.detect_redundancy(repetitive_content)

    assert result.redundancy_score > 0.3  # Should detect significant redundancy
    assert len(result.repeated_sections) > 0
    assert "machine learning" in str(result.verbose_passages).lower()


def test_enhanced_validator_validate_factual_consistency_logic(
    enhanced_validator: EnhancedContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test the core logic of validate_factual_consistency by mocking its helpers."""

    # Mock helper methods
    enhanced_validator._extract_factual_statements = MagicMock(
        return_value={
            "outline": ["Fact A from outline", "Fact B from outline"],
            "guide": [
                "Fact A from guide (matches A)",
                "Fact C from guide (unsupported)",
            ],
            "faqs": ["Fact D from faqs (unsupported)", "Contradictory fact to B"],
        }
    )

    # Simulate _find_contradictions finding one contradiction
    enhanced_validator._find_contradictions = MagicMock(
        return_value=[
            {
                "source1": "outline",
                "fact1": "Fact B from outline",
                "source2": "faqs",
                "fact2": "Contradictory fact to B",
            }
        ]
    )

    # Simulate _facts_match behavior
    def mock_facts_match(fact1, fact2):
        if "Fact A from outline" in fact1 and "Fact A from guide" in fact2:
            return True
        if (
            "Fact B from outline" in fact1 and "Contradictory fact to B" in fact2
        ):  # Should not be considered a match for support
            return False
        return False

    enhanced_validator._facts_match = MagicMock(side_effect=mock_facts_match)

    enhanced_validator._count_total_words = MagicMock(return_value=1000)
    enhanced_validator._calculate_citation_coverage = MagicMock(return_value=0.75)

    # Act
    result = enhanced_validator.validate_factual_consistency(mock_generated_content)

    # Assert
    assert isinstance(result, FactualValidation)

    # Check contradictions (1 expected)
    assert len(result.contradictions_found) == 1
    assert result.contradictions_found[0]["fact1"] == "Fact B from outline"

    # Check unsupported claims (Fact C and Fact D expected)
    # Note: The logic for unsupported claims checks non-outline facts against outline facts.
    # "Contradictory fact to B" is also unsupported by the outline.
    assert len(result.unsupported_claims) == 3
    assert any("Fact C from guide" in claim for claim in result.unsupported_claims)
    assert any("Fact D from faqs" in claim for claim in result.unsupported_claims)
    assert any(
        "Contradictory fact to B" in claim for claim in result.unsupported_claims
    )

    # Check consistency score calculation (1 contradiction * 0.1 penalty, 3 unsupported * 0.05 penalty)
    # Expected score = 1.0 - 0.1 - (3 * 0.05) = 1.0 - 0.1 - 0.15 = 0.75
    assert result.consistency_score == pytest.approx(0.75)

    # Check fact density (mocked total_words and _count_total_words)
    # Extracted facts: 2 (outline) + 2 (guide) + 2 (faqs) = 6 facts
    # Estimated words per fact = 5. Total fact words = 6 * 5 = 30
    # Total content words = 1000
    # fact_density_score = min(1.0, 30 / 1000 * 10) = min(1.0, 0.3) = 0.3
    assert result.fact_density_score == pytest.approx(0.3)

    assert result.citation_coverage == 0.75  # From mock

    # Verify mocks were called
    enhanced_validator._extract_factual_statements.assert_called_once_with(
        mock_generated_content
    )
    # _find_contradictions is called for each pair of sources.
    # Sources: outline, guide, faqs. Pairs: (outline, guide), (outline, faqs), (guide, faqs) -> 3 calls
    assert enhanced_validator._find_contradictions.call_count == 3
    enhanced_validator._count_total_words.assert_called_once_with(
        mock_generated_content
    )
    enhanced_validator._calculate_citation_coverage.assert_called_once_with(
        mock_generated_content
    )


# --- Test SemanticConsistencyValidator ---


@pytest.fixture
def semantic_validator():
    """Create a SemanticConsistencyValidator instance."""
    return SemanticConsistencyValidator()


def test_semantic_validator_validate_title_consistency(
    semantic_validator: SemanticConsistencyValidator,
    mock_generated_content: GeneratedContent,
):
    """Test title consistency validation across content types."""
    # All titles match - should have high consistency
    report = semantic_validator.validate_title_consistency(mock_generated_content)

    assert isinstance(report, ConsistencyItem)
    assert report.item_type == "title_consistency"
    assert report.consistency_score > 0.9
    assert not report.issues

    # Test with mismatched titles
    mock_generated_content.podcast_script.title = "Different Title"
    report = semantic_validator.validate_title_consistency(mock_generated_content)

    assert report.consistency_score < 0.7
    assert len(report.issues) > 0
    assert "title mismatch" in report.issues[0].lower()


def test_semantic_validator_validate_content_alignment(
    semantic_validator: SemanticConsistencyValidator,
    mock_generated_content: GeneratedContent,
):
    """Test content alignment validation between outline and derived content."""
    report = semantic_validator.validate_content_alignment(
        mock_generated_content.content_outline,
        mock_generated_content.podcast_script,
        "podcast_script",
    )

    assert isinstance(report, ConsistencyItem)
    assert report.item_type == "content_alignment_podcast_script"
    assert report.consistency_score > 0.5  # Should have some alignment


def test_semantic_validator_validate_complete_content(
    semantic_validator: SemanticConsistencyValidator,
    mock_generated_content: GeneratedContent,
):
    """Test complete content validation pipeline."""
    report = semantic_validator.validate_complete_content(mock_generated_content)

    assert isinstance(report, ConsistencyReport)
    assert report.overall_consistency_score > 0
    assert len(report.item_reports) > 0
    assert any(item.item_type == "title_consistency" for item in report.item_reports)
    assert any("alignment" in item.item_type for item in report.item_reports)


def test_semantic_validator_cross_reference_validation(
    semantic_validator: SemanticConsistencyValidator,
):
    """Test cross-reference validation between content types."""
    # Create content with FAQ that references outline sections
    content = GeneratedContent(
        content_outline=ContentOutline(
            title="Test Title",
            overview="This is a comprehensive overview for testing cross-references in the content.",
            learning_objectives=[
                "Learning objective one with details",
                "Learning objective two with details",
                "Learning objective three with details",
            ],
            sections=[
                OutlineSection(
                    section_number=1,
                    title="Introduction",
                    description="Introduction description with adequate length",
                    key_points=["Key point one for introduction"],
                )
            ],
        ),
        faq_collection=FAQCollection(
            title="Frequently Asked Questions",
            description="FAQ Description",
            items=[
                FAQItem(
                    question="What is covered in the Introduction section?",
                    answer="The Introduction covers Point 1 and basic concepts that are explained in detail.",
                    category="General",
                ),
                FAQItem(
                    question="How long does this course take to complete?",
                    answer="The course duration depends on your pace but typically takes 4-6 weeks to complete.",
                    category="General",
                ),
                FAQItem(
                    question="What are the prerequisites for this course?",
                    answer="Basic understanding of programming and mathematics is recommended for best results.",
                    category="Prerequisites",
                ),
                FAQItem(
                    question="Can I access the materials after completion?",
                    answer="Yes, all materials remain accessible indefinitely after course completion.",
                    category="Access",
                ),
                FAQItem(
                    question="Is there a certificate upon completion?",
                    answer="Yes, a certificate is provided upon successful completion of all modules.",
                    category="Certification",
                ),
            ],
        ),
    )

    report = semantic_validator.validate_cross_references(content)

    assert isinstance(report, ConsistencyItem)
    assert report.item_type == "cross_references"
    assert report.consistency_score > 0.7  # Should detect the reference


# --- Test QualityRefinementEngine ---


@pytest.fixture
def refinement_engine():
    """Create a QualityRefinementEngine with mocked dependencies."""
    engine = QualityRefinementEngine()
    engine.prompt_optimizer = MagicMock(spec=PromptOptimizer)
    return engine


def test_refinement_engine_generate_refinements_low_quality(
    refinement_engine: QualityRefinementEngine, mock_generated_content: GeneratedContent
):
    """Test refinement generation for low quality content."""
    # Create a validation result indicating low quality
    validation_result = ValidationResult(
        is_valid=False,
        overall_score=0.5,
        input_validation=InputValidation(
            quality_score=0.5,
            readability_score=0.6,
            completeness_score=0.5,
            clarity_issues=["Vague language", "Incomplete sections"],
            enhancement_suggestions=["Add more detail"],
            word_count=50,
            estimated_complexity="low",
        ),
        structure_validation=StructureValidation(
            has_required_sections=False,
            missing_sections=["study_guide"],
            section_balance_score=0.4,
            logical_flow_score=0.5,
            hierarchy_issues=["Inconsistent section depth"],
            format_compliance={"comprehensive": False},
        ),
        semantic_validation=ConsistencyReport(
            overall_consistency_score=0.6,
            item_reports=[],
            recommendations=["Improve content alignment"],
        ),
        issues=[],
        recommendations=["Improve clarity", "Add missing sections"],
    )

    result = refinement_engine.generate_refinements(
        content=mock_generated_content,
        validation_result=validation_result,
        feedback_history=[],
    )

    assert isinstance(result, RefinementResult)
    assert len(result.suggestions) > 0
    assert result.priority_score > 0.5  # Low quality should have high priority
    assert any(s.refinement_type == "clarity" for s in result.suggestions)
    assert any(s.refinement_type == "structure" for s in result.suggestions)


@pytest.mark.asyncio
async def test_refinement_engine_apply_refinements(
    refinement_engine: QualityRefinementEngine, mock_generated_content: GeneratedContent
):
    """Test applying refinements to content."""
    # Mock the LLM service

    suggestions = [
        RefinementSuggestion(
            refinement_type="clarity",
            target_section="introduction",
            current_issue="Vague language",
            suggested_improvement="Add specific examples",
            priority=0.8,
        ),
        RefinementSuggestion(
            refinement_type="structure",
            target_section="outline",
            current_issue="Missing learning objectives",
            suggested_improvement="Add 3-5 clear learning objectives",
            priority=0.9,
        ),
    ]

    with patch(
        "app.services.quality_refinement.generate_refined_content",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = (
            mock_generated_content  # Return same content for simplicity
        )

        refined_content = await refinement_engine.apply_refinements(
            content=mock_generated_content, suggestions=suggestions, max_iterations=1
        )

        assert refined_content is not None
        mock_generate.assert_called_once()


def test_refinement_engine_incorporate_feedback(
    refinement_engine: QualityRefinementEngine,
):
    """Test incorporating user feedback into refinements."""
    feedback_history = [
        FeedbackBase(rating=False, comment="The content is too technical"),
        FeedbackBase(rating=False, comment="Need more examples"),
        FeedbackBase(rating=True, comment="Good structure"),
    ]

    validation_result = ValidationResult(
        is_valid=True,
        overall_score=0.8,
        input_validation=MagicMock(),
        structure_validation=MagicMock(),
        semantic_validation=MagicMock(),
        issues=[],
        recommendations=[],
    )

    result = refinement_engine.generate_refinements(
        content=MagicMock(),
        validation_result=validation_result,
        feedback_history=feedback_history,
    )

    # Should generate refinements based on negative feedback
    assert len(result.suggestions) > 0
    assert any("technical" in s.current_issue.lower() for s in result.suggestions)
    assert any(
        "examples" in s.suggested_improvement.lower() for s in result.suggestions
    )


def test_refinement_engine_no_issues(
    refinement_engine: QualityRefinementEngine, mock_generated_content: GeneratedContent
):
    """Test refinement engine when content has no issues."""
    perfect_validation = ValidationResult(
        is_valid=True,
        overall_score=0.95,
        input_validation=MagicMock(quality_score=0.95),
        structure_validation=MagicMock(has_required_sections=True),
        semantic_validation=ConsistencyReport(
            overall_consistency_score=0.95, item_reports=[], recommendations=[]
        ),
        issues=[],
        recommendations=[],
    )

    result = refinement_engine.generate_refinements(
        content=mock_generated_content,
        validation_result=perfect_validation,
        feedback_history=[],
    )

    assert len(result.suggestions) == 0  # No refinements needed
    assert result.priority_score < 0.2  # Low priority


# --- Test PromptOptimizer ---


@pytest.fixture
def prompt_optimizer():
    """Create a PromptOptimizer instance."""
    return PromptOptimizer()


def test_prompt_optimizer_analyze_prompt_basic(prompt_optimizer: PromptOptimizer):
    """Test basic prompt analysis."""
    prompt = "Generate a comprehensive study guide about machine learning. Include key concepts, examples, and practice questions."

    metrics = prompt_optimizer.analyze_prompt(prompt)

    assert isinstance(metrics, PromptMetrics)
    assert metrics.clarity_score > 0.7  # Should be reasonably clear
    assert metrics.specificity_score > 0.6  # Has some specific requirements
    assert metrics.token_count > 0
    assert len(metrics.improvement_suggestions) >= 0


def test_prompt_optimizer_analyze_prompt_vague(prompt_optimizer: PromptOptimizer):
    """Test analysis of vague prompt."""
    prompt = "Make it good."

    metrics = prompt_optimizer.analyze_prompt(prompt)

    assert metrics.clarity_score < 0.5
    assert metrics.specificity_score < 0.5
    assert len(metrics.improvement_suggestions) > 0
    assert any("specific" in s.lower() for s in metrics.improvement_suggestions)


def test_prompt_optimizer_optimize_for_model(prompt_optimizer: PromptOptimizer):
    """Test prompt optimization for specific model."""
    original_prompt = "Create content about AI."

    result = prompt_optimizer.optimize_for_model(
        prompt=original_prompt,
        model_name="gemini-pro",
        optimization_goals=["clarity", "specificity"],
    )

    assert isinstance(result, OptimizationResult)
    assert result.optimized_prompt != original_prompt  # Should be modified
    assert len(result.optimized_prompt) > len(
        original_prompt
    )  # Should be more detailed
    assert result.confidence_score > 0
    assert "changes_made" in result.metadata


def test_prompt_optimizer_optimize_with_examples(prompt_optimizer: PromptOptimizer):
    """Test prompt optimization with example incorporation."""
    prompt = "Generate a podcast script."
    examples = [
        "Example 1: A podcast about space exploration...",
        "Example 2: A podcast about climate change...",
    ]

    result = prompt_optimizer.optimize_with_examples(
        prompt=prompt, examples=examples, model_name="gemini-pro"
    )

    assert (
        "example" in result.optimized_prompt.lower()
        or "similar to" in result.optimized_prompt.lower()
    )
    assert result.confidence_score > 0.7  # Examples should increase confidence


@pytest.mark.asyncio
async def test_prompt_optimizer_iterative_optimization(
    prompt_optimizer: PromptOptimizer,
):
    """Test iterative prompt optimization based on output quality."""
    initial_prompt = "Write about technology."

    # Mock quality scores for iterations
    quality_scores = [0.5, 0.7, 0.85]  # Improving scores

    with patch.object(
        prompt_optimizer, "evaluate_output_quality", side_effect=quality_scores
    ):
        final_result = await prompt_optimizer.iterative_optimization(
            initial_prompt=initial_prompt,
            quality_threshold=0.8,
            max_iterations=3,
            model_name="gemini-pro",
        )

        assert final_result.confidence_score >= 0.8
        assert final_result.metadata["iterations"] == 3
        assert final_result.metadata["final_quality_score"] == 0.85


def test_prompt_optimizer_template_selection(prompt_optimizer: PromptOptimizer):
    """Test automatic template selection based on content type."""
    # Test podcast script template selection
    result = prompt_optimizer.select_template(
        content_type="podcast_script",
        requirements={"duration": 20, "style": "conversational"},
    )

    assert "podcast" in result.optimized_prompt.lower()
    assert "conversational" in result.optimized_prompt.lower()
    assert result.metadata["template_used"] == "podcast_script"

    # Test study guide template selection
    result = prompt_optimizer.select_template(
        content_type="study_guide",
        requirements={"level": "beginner", "include_exercises": True},
    )

    assert "study guide" in result.optimized_prompt.lower()
    assert "beginner" in result.optimized_prompt.lower()
    assert "exercise" in result.optimized_prompt.lower()


def test_prompt_optimizer_extreme_length(prompt_optimizer: PromptOptimizer):
    """Test prompt optimizer with extremely long prompt."""
    # Create a very long prompt
    long_prompt = "Generate content about " + " and ".join(
        [f"topic{i}" for i in range(100)]
    )

    metrics = prompt_optimizer.analyze_prompt(long_prompt)

    assert metrics.token_count > 200  # Should be many tokens
    assert any("length" in s.lower() for s in metrics.improvement_suggestions)

    # Optimization should try to reduce length
    result = prompt_optimizer.optimize_for_model(
        prompt=long_prompt, model_name="gemini-pro", optimization_goals=["conciseness"]
    )

    assert len(result.optimized_prompt) < len(long_prompt)


# --- Integration Tests for Quality Services ---


@pytest.mark.asyncio
async def test_quality_pipeline_integration(
    enhanced_validator: EnhancedContentValidator,
    semantic_validator: SemanticConsistencyValidator,
    refinement_engine: QualityRefinementEngine,
    prompt_optimizer: PromptOptimizer,
    mock_generated_content: GeneratedContent,
):
    """Test integration of all quality services in a pipeline."""
    # Step 1: Validate content
    validation_result = enhanced_validator.validate_complete_pipeline(
        content=mock_generated_content,
        syllabus_text="Test syllabus for ML course",
        target_format="comprehensive",
    )

    # Step 2: If validation fails, generate refinements
    if not validation_result.is_valid:
        refinement_result = refinement_engine.generate_refinements(
            content=mock_generated_content,
            validation_result=validation_result,
            feedback_history=[],
        )

        # Step 3: Optimize prompts for refinement
        for suggestion in refinement_result.suggestions[:2]:  # Test first 2 suggestions
            optimized = prompt_optimizer.optimize_for_model(
                prompt=f"Improve {suggestion.target_section}: {suggestion.suggested_improvement}",
                model_name="gemini-pro",
                optimization_goals=["clarity", "actionability"],
            )
            assert optimized.confidence_score > 0.5

    assert validation_result is not None


# --- Edge Cases and Error Handling ---


def test_enhanced_validator_empty_content(enhanced_validator: EnhancedContentValidator):
    """Test validation with empty content."""
    empty_content = GeneratedContent(content_outline=None)

    result = enhanced_validator.validate_complete_pipeline(
        content=empty_content,
        syllabus_text="Test syllabus",
        target_format="comprehensive",
    )

    assert result.is_valid is False
    assert result.overall_score == 0
    assert any("missing" in issue.description.lower() for issue in result.issues)


def test_semantic_validator_partial_content(
    semantic_validator: SemanticConsistencyValidator,
):
    """Test semantic validation with partial content."""
    partial_content = GeneratedContent(
        content_outline=ContentOutline(
            title="Test",
            overview="Overview with sufficient length for validation requirements.",
            learning_objectives=[
                "LO1 with enough detail",
                "LO2 with enough detail",
                "LO3 with enough detail",
            ],
            sections=[],
        ),
        podcast_script=None,  # Missing other content
        study_guide=None,
    )

    report = semantic_validator.validate_complete_content(partial_content)

    assert report.overall_consistency_score < 1.0
    assert len(report.recommendations) > 0


def test_comprehensive_validation_pipeline(
    comprehensive_validator: ComprehensiveContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test the comprehensive validation pipeline."""
    # Mock the structural validator
    comprehensive_validator.structural_validator = MagicMock()
    comprehensive_validator.structural_validator.validate_complete_pipeline.return_value = ValidationResult(
        is_valid=True, overall_score=0.9, issues=[], recommendations=[], metadata={}
    )

    # Run the validation pipeline
    report = comprehensive_validator.validate_content_pipeline(
        generated_content=mock_generated_content,
        original_syllabus_text="Test syllabus",
        target_format="comprehensive",
    )

    assert isinstance(report, ComprehensiveValidationReport)
    assert report.overall_passed is True
    assert report.overall_score > 0.7
    assert not report.actionable_feedback  # No issues found


def test_comprehensive_validation_with_issues(
    comprehensive_validator: ComprehensiveContentValidator,
    mock_generated_content: GeneratedContent,
):
    """Test comprehensive validation with validation issues."""
    # Mock the structural validator to return issues
    comprehensive_validator.structural_validator = MagicMock()
    comprehensive_validator.structural_validator.validate_complete_pipeline.return_value = ValidationResult(
        is_valid=False,
        overall_score=0.6,
        issues=[
            ValidationIssue(
                severity="major",
                issue_type="structure_issue",
                description="Missing required sections",
                location="structure",
                suggested_fix="Add missing sections",
            )
        ],
        recommendations=["Add missing sections"],
        metadata={},
    )

    # Run the validation pipeline
    report = comprehensive_validator.validate_content_pipeline(
        generated_content=mock_generated_content,
        original_syllabus_text="Test syllabus",
        target_format="comprehensive",
    )

    assert isinstance(report, ComprehensiveValidationReport)
    assert report.overall_passed is False
    assert report.overall_score < 0.7
    assert len(report.actionable_feedback) > 0
    assert any(
        "missing sections" in feedback.lower()
        for feedback in report.actionable_feedback
    )
