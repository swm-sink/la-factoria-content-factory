from typing import Any, Dict

import pytest

from app.models.pydantic.content import (
    ContentOutline,
    GeneratedContent,
    OutlineSection,
    PodcastScript,
    StudyGuide,
)

# --- Fixtures for ContentOutline and its components ---


@pytest.fixture
def valid_outline_section_data() -> Dict:
    """Provides valid data for an OutlineSection."""
    return {
        "section_number": 1,
        "title": "Valid Section Title",
        "description": "This is a valid and sufficiently long section description for testing purposes.",
        "estimated_duration_minutes": 10.5,
        "key_points": [
            "This is valid key point number one.",
            "This is valid key point number two.",
            "This is valid key point number three.",
        ],
    }


@pytest.fixture
def valid_outline_section(valid_outline_section_data: Dict) -> OutlineSection:
    """Provides a valid OutlineSection instance."""
    return OutlineSection(**valid_outline_section_data)


@pytest.fixture
def valid_content_outline_data(valid_outline_section_data: Dict) -> Dict:
    """Provides valid data for a ContentOutline."""
    # Create a few unique section data, ensuring section numbers are unique if OutlineSection list is directly used
    sections_data = []
    for i in range(1, 4):
        section_copy = valid_outline_section_data.copy()
        section_copy["section_number"] = i
        section_copy["title"] = f"Valid Section Title {i}"
        sections_data.append(section_copy)

    return {
        "title": "Valid Content Outline Title",
        "overview": "This is a comprehensive and valid overview for the content outline, exceeding fifty characters.",
        "learning_objectives": [
            "Objective one is clearly stated and long enough.",
            "Objective two is also clearly stated and long enough.",
            "Objective three meets all length and clarity requirements.",
        ],
        "sections": sections_data,
        "estimated_total_duration": 31.5,
        "target_audience": "Test Learners",
        "difficulty_level": "intermediate",
    }


@pytest.fixture
def valid_content_outline(valid_content_outline_data: Dict) -> ContentOutline:
    """Provides a valid ContentOutline instance."""
    return ContentOutline(**valid_content_outline_data)


# --- Fixture for GeneratedContent (minimal valid instance) ---


@pytest.fixture
def valid_generated_content(valid_content_outline: ContentOutline) -> GeneratedContent:
    """Provides a minimal valid GeneratedContent instance with only the mandatory content_outline."""
    return GeneratedContent(content_outline=valid_content_outline)


# --- Placeholder fixtures for other content types (to be fleshed out) ---
# These will be needed to test GeneratedContent more thoroughly


@pytest.fixture
def valid_podcast_script_data() -> Dict:
    return {
        "title": "Valid Content Outline Title",  # To match outline for consistency validator
        "introduction": "This is a sufficiently long introduction for the podcast script, exceeding one hundred characters and providing a good overview of what will be discussed.",
        "main_content": "This is the main content of the podcast script. It needs to be quite long to pass validation, specifically between 800 and 10000 characters. This section will elaborate on all the key points mentioned in the introduction and delve deep into the subject matter, providing examples, explanations, and engaging narratives. We are aiming for at least 800 characters here. Let's add more text. We need to ensure this part is substantial. This block of text is intended to meet the minimum length requirements for the main_content field in the PodcastScript Pydantic model. It discusses various aspects of the topic, provides detailed explanations, and aims to be engaging for the listener. The length is critical for validation purposes, so padding it out is necessary for this test fixture. More content here to reach the threshold. Still more content. Almost there. One more sentence should do it.",
        "conclusion": "This is a sufficiently long conclusion for the podcast script, wrapping up the main points and providing some final thoughts for the listener. It must be at least one hundred characters long.",
        "speaker_notes": [
            "Note for speaker: emphasize this point.",
            "Another note: pause for effect here.",
        ],
        "estimated_duration_minutes": 25.0,
    }


@pytest.fixture
def valid_podcast_script(
    valid_podcast_script_data: Dict, valid_content_outline: ContentOutline
) -> PodcastScript:
    # Ensure title matches outline if that's a validation rule being tested elsewhere
    script_data = valid_podcast_script_data.copy()
    script_data["title"] = valid_content_outline.title
    return PodcastScript(**script_data)


@pytest.fixture
def valid_study_guide_data() -> Dict:
    return {
        "title": "Valid Content Outline Title",  # To match outline
        "overview": "This is a detailed overview for the study guide, exceeding 100 characters and setting the stage for the content within the guide.",
        "key_concepts": [
            "Key Concept Alpha - explained further",
            "Key Concept Bravo - detailed description",
            "Key Concept Charlie - core idea",
            "Key Concept Delta - important point",
            "Key Concept Echo - fundamental principle",
        ],
        "detailed_content": "This is the detailed content section of the study guide. It must be between 500 and 8000 characters. This section will expand on each of the key concepts, provide in-depth explanations, examples, and support learning. The purpose of this fixture is to provide enough text to pass the validation rules. This involves writing a substantial amount of placeholder text to meet the minimum length requirements. This detailed content explores various facets of the subject, offering comprehensive coverage to aid understanding and retention. More text to ensure we meet the length. Still going. Almost at the minimum length for this field. Just a bit more to be safe.",
        "summary": "This is a concise summary of the study guide, over 100 characters, highlighting the main learning points and reinforcing the key concepts discussed.",
        "recommended_reading": ["Book A by Author X", "Article B by Author Y"],
    }


@pytest.fixture
def valid_study_guide(
    valid_study_guide_data: Dict, valid_content_outline: ContentOutline
) -> StudyGuide:
    guide_data = valid_study_guide_data.copy()
    guide_data["title"] = valid_content_outline.title
    return StudyGuide(**guide_data)


# Helper functions for use in tests (not pytest fixtures)
def sample_content_outline() -> ContentOutline:
    """Create a sample ContentOutline for testing."""
    return ContentOutline(
        title="Valid Content Outline Title",
        overview="This is a comprehensive and valid overview for the content outline, exceeding fifty characters.",
        learning_objectives=[
            "Objective one is clearly stated and long enough.",
            "Objective two is also clearly stated and long enough.",
            "Objective three meets all length and clarity requirements.",
        ],
        sections=[
            OutlineSection(
                section_number=i,
                title=f"Valid Section Title {i}",
                description="This is a valid and sufficiently long section description for testing purposes.",
                estimated_duration_minutes=10.5,
                key_points=[
                    "This is valid key point number one.",
                    "This is valid key point number two.",
                    "This is valid key point number three.",
                ],
            )
            for i in range(1, 4)
        ],
        estimated_total_duration=31.5,
        target_audience="Test Learners",
        difficulty_level="intermediate",
    )


def sample_podcast_script() -> PodcastScript:
    """Create a sample PodcastScript for testing."""
    return PodcastScript(
        title="Valid Content Outline Title",
        introduction="This is a sufficiently long introduction for the podcast script, exceeding one hundred characters and providing a good overview of what will be discussed.",
        main_content="This is the main content of the podcast script. It needs to be quite long to pass validation, specifically between 800 and 10000 characters. This section will elaborate on all the key points mentioned in the introduction and delve deep into the subject matter, providing examples, explanations, and engaging narratives. We are aiming for at least 800 characters here. Let's add more text. We need to ensure this part is substantial. This block of text is intended to meet the minimum length requirements for the main_content field in the PodcastScript Pydantic model. It discusses various aspects of the topic, provides detailed explanations, and aims to be engaging for the listener. The length is critical for validation purposes, so padding it out is necessary for this test fixture. More content here to reach the threshold. Still more content. Almost there. One more sentence should do it.",
        conclusion="This is a sufficiently long conclusion for the podcast script, wrapping up the main points and providing some final thoughts for the listener. It must be at least one hundred characters long.",
        speaker_notes=[
            "Note for speaker: emphasize this point.",
            "Another note: pause for effect here.",
        ],
        estimated_duration_minutes=25.0,
    )


def sample_quality_metrics() -> Dict[str, Any]:
    """Create sample quality metrics for testing."""
    return {
        "coherence_score": 0.85,
        "completeness_score": 0.90,
        "accuracy_score": 0.88,
        "engagement_score": 0.87,
        "overall_score": 0.875,
    }


# TODO: Add similar fixtures for:
# - OnePagerSummary
# - DetailedReadingMaterial
# - FAQItem, FAQCollection
# - FlashcardItem, FlashcardCollection
# - ReadingGuideQuestions
