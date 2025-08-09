"""
Integration tests for Quality Assessment System
Tests integration with Educational Content Service and API endpoints
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

# Mock the configuration before importing
import sys
from types import ModuleType

mock_config = ModuleType('config')
mock_settings = Mock()
mock_settings.QUALITY_THRESHOLD_OVERALL = 0.70
mock_settings.QUALITY_THRESHOLD_EDUCATIONAL = 0.75
mock_settings.QUALITY_THRESHOLD_FACTUAL = 0.85
mock_config.settings = mock_settings
sys.modules['src.core.config'] = mock_config

# Now import our modules
from src.services.quality_assessor import EducationalQualityAssessor
from src.models.educational import LearningObjective, CognitiveLevel

class TestQualityAssessmentIntegration:
    """Integration tests for quality assessment with content generation"""

    @pytest.fixture
    def quality_assessor(self):
        """Create quality assessor instance"""
        return EducationalQualityAssessor()

    @pytest.fixture
    def high_quality_study_guide(self):
        """High-quality study guide content for testing"""
        return {
            "title": "Photosynthesis in Plants",
            "overview": "Understanding how plants convert sunlight into energy",
            "learning_objectives": [
                "Students will understand the process of photosynthesis",
                "Students will identify the components needed for photosynthesis",
                "Students will analyze the importance of photosynthesis in ecosystems"
            ],
            "sections": [
                {
                    "title": "What is Photosynthesis?",
                    "content": """
                    Photosynthesis is the process by which plants convert sunlight into energy.
                    According to scientific research, this process is essential for all life on Earth.

                    The basic equation for photosynthesis is:
                    6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂

                    Let's break this down step by step:
                    1. Plants absorb carbon dioxide from the air
                    2. Plants take in water through their roots
                    3. Chlorophyll captures light energy from the sun
                    4. These combine to create glucose (sugar) and oxygen
                    """
                },
                {
                    "title": "Why is Photosynthesis Important?",
                    "content": """
                    Photosynthesis is crucial for several reasons:
                    - Produces oxygen that we breathe
                    - Creates food for plants and animals
                    - Removes carbon dioxide from the atmosphere
                    - Forms the base of most food chains

                    Try this activity: Go outside and observe different plants.
                    Can you identify which ones are actively photosynthesizing?
                    """
                }
            ],
            "key_terms": [
                {"term": "Chlorophyll", "definition": "Green pigment that captures light energy"},
                {"term": "Glucose", "definition": "Sugar produced during photosynthesis"},
                {"term": "Carbon dioxide", "definition": "Gas absorbed by plants from the air"}
            ],
            "practice_questions": [
                {
                    "question": "What are the main inputs needed for photosynthesis?",
                    "answer": "Carbon dioxide, water, and light energy"
                },
                {
                    "question": "What does photosynthesis produce?",
                    "answer": "Glucose (sugar) and oxygen"
                }
            ],
            "summary": """
            Photosynthesis is the fundamental process that allows plants to convert
            sunlight into energy, producing the oxygen we breathe and forming the
            foundation of Earth's food webs.
            """
        }

    @pytest.fixture
    def poor_quality_content(self):
        """Poor quality content with errors for testing"""
        return {
            "title": "Bad Science Content",
            "content": """
            The Earth is flat and vaccines cause autism. Plants don't really
            need sunlight because they can survive in complete darkness.
            Photosynthesis is fake science made up by scientists.
            Water boils at 50 degrees Celsius and 2 + 2 = 5.
            This content has no structure or educational value.
            """
        }

    @pytest.fixture
    def sample_learning_objectives(self):
        """Sample learning objectives for testing"""
        return [
            LearningObjective(
                cognitive_level=CognitiveLevel.UNDERSTANDING,
                subject_area="biology",
                specific_skill="photosynthesis process",
                measurable_outcome="explain how plants convert sunlight to energy",
                difficulty_level=6
            ),
            LearningObjective(
                cognitive_level=CognitiveLevel.ANALYZING,
                subject_area="biology",
                specific_skill="ecosystem relationships",
                measurable_outcome="analyze the role of photosynthesis in food webs",
                difficulty_level=7
            )
        ]

    @pytest.mark.asyncio
    async def test_high_quality_content_assessment(
        self, quality_assessor, high_quality_study_guide, sample_learning_objectives
    ):
        """Test that high-quality content meets all quality thresholds"""

        result = await quality_assessor.assess_content_quality(
            content=high_quality_study_guide,
            content_type="study_guide",
            age_group="high_school",
            learning_objectives=sample_learning_objectives
        )

        # Validate comprehensive quality metrics
        assert "overall_quality_score" in result
        assert "educational_effectiveness" in result
        assert "factual_accuracy" in result
        assert "readability_score" in result
        assert "learning_objective_alignment" in result
        assert "engagement_score" in result
        assert "structural_quality" in result
        assert "blooms_taxonomy_alignment" in result
        assert "quality_improvement_suggestions" in result

        # Validate quality thresholds
        assert result["overall_quality_score"] >= 0.70, f"Overall quality {result['overall_quality_score']} below threshold"
        assert result["educational_effectiveness"] >= 0.75, f"Educational effectiveness {result['educational_effectiveness']} below threshold"
        assert result["factual_accuracy"] >= 0.85, f"Factual accuracy {result['factual_accuracy']} below threshold"

        # Validate threshold compliance flags
        assert result["meets_quality_threshold"] == True
        assert result["meets_educational_threshold"] == True
        assert result["meets_factual_threshold"] == True

        # Validate learning objective alignment is working
        assert result["learning_objective_alignment"] > 0.5, "Learning objective alignment should be reasonable"

        # Validate Bloom's taxonomy assessment
        assert result["blooms_taxonomy_alignment"] > 0.0, "Bloom's taxonomy alignment should be calculated"

        print(f"✅ High-quality content assessment: {result['overall_quality_score']:.3f}")

    @pytest.mark.asyncio
    async def test_poor_quality_content_rejection(
        self, quality_assessor, poor_quality_content
    ):
        """Test that poor-quality content is properly rejected"""

        result = await quality_assessor.assess_content_quality(
            content=poor_quality_content,
            content_type="study_guide",
            age_group="high_school"
        )

        # Poor content should fail quality thresholds
        assert result["overall_quality_score"] < 0.70, "Poor content should not meet quality threshold"
        assert result["educational_effectiveness"] < 0.75, "Poor content should not meet educational threshold"
        assert result["factual_accuracy"] < 0.85, "Poor content should not meet factual accuracy threshold"

        # Validate threshold compliance flags
        assert result["meets_quality_threshold"] == False
        assert result["meets_educational_threshold"] == False
        assert result["meets_factual_threshold"] == False

        # Should provide improvement suggestions
        assert len(result["quality_improvement_suggestions"]) > 0, "Should provide improvement suggestions"

        print(f"✅ Poor-quality content rejection: {result['overall_quality_score']:.3f}")

    @pytest.mark.asyncio
    async def test_content_type_specific_assessment(self, quality_assessor):
        """Test content type specific quality assessment"""

        # Test flashcards content
        flashcards_content = {
            "cards": [
                {
                    "question": "What is photosynthesis?",
                    "answer": "The process by which plants convert sunlight into energy"
                },
                {
                    "question": "What gas do plants absorb during photosynthesis?",
                    "answer": "Carbon dioxide"
                },
                {
                    "question": "What do plants produce during photosynthesis?",
                    "answer": "Glucose and oxygen"
                }
            ],
            "topic": "Photosynthesis Basics",
            "difficulty": "beginner"
        }

        result = await quality_assessor.assess_content_quality(
            content=flashcards_content,
            content_type="flashcards",
            age_group="middle_school"
        )

        # Flashcards should have decent educational effectiveness
        assert result["educational_effectiveness"] >= 0.6, "Flashcards should have educational value"
        assert "overall_quality_score" in result

        print(f"✅ Flashcards quality assessment: {result['overall_quality_score']:.3f}")

    @pytest.mark.asyncio
    async def test_age_group_adaptability(self, quality_assessor):
        """Test that quality assessment adapts to different age groups"""

        # Simple content that should be appropriate for elementary
        simple_content = {
            "title": "Plants Need Light",
            "content": """
            Plants need light to grow. When plants get light from the sun,
            they make their own food. This is called photosynthesis.
            Plants also need water and air to live and grow big and strong.
            """
        }

        # Test with different age groups
        age_groups = ["elementary", "middle_school", "high_school", "college"]
        results = {}

        for age_group in age_groups:
            result = await quality_assessor.assess_content_quality(
                content=simple_content,
                content_type="one_pager_summary",
                age_group=age_group
            )
            results[age_group] = result

        # Simple content should be most appropriate for elementary
        elementary_readability = results["elementary"]["readability_score"]["age_appropriateness_score"]
        college_readability = results["college"]["readability_score"]["age_appropriateness_score"]

        assert elementary_readability >= college_readability, "Simple content should be more appropriate for elementary"

        print(f"✅ Age adaptability - Elementary: {elementary_readability:.3f}, College: {college_readability:.3f}")

    @pytest.mark.asyncio
    async def test_factual_accuracy_detection(self, quality_assessor):
        """Test factual accuracy detection capabilities"""

        test_cases = [
            {
                "content": {"content": "According to peer-reviewed research, photosynthesis converts CO₂ and water into glucose using light energy."},
                "expected_accuracy": "high",
                "description": "Scientific content with citations"
            },
            {
                "content": {"content": "The Earth is flat and vaccines cause autism. Plants don't need sunlight."},
                "expected_accuracy": "low",
                "description": "Content with major factual errors"
            },
            {
                "content": {"content": "Plants generally absorb carbon dioxide, though the exact mechanisms may vary by species."},
                "expected_accuracy": "medium",
                "description": "Content with appropriate uncertainty"
            }
        ]

        accuracy_scores = []
        for case in test_cases:
            result = await quality_assessor.assess_content_quality(
                content=case["content"],
                content_type="study_guide",
                age_group="high_school"
            )

            accuracy = result["factual_accuracy"]
            accuracy_scores.append((case["description"], accuracy, case["expected_accuracy"]))

            print(f"   {case['description']}: {accuracy:.3f}")

        # Validate that detection is working correctly
        scientific_accuracy = accuracy_scores[0][1]  # Should be high
        error_accuracy = accuracy_scores[1][1]       # Should be low
        uncertainty_accuracy = accuracy_scores[2][1] # Should be medium

        assert scientific_accuracy > error_accuracy, "Scientific content should score higher than error content"
        assert scientific_accuracy >= 0.8, "Good scientific content should score well"
        assert error_accuracy <= 0.5, "Content with errors should score poorly"

        print(f"✅ Factual accuracy detection working correctly")

    @pytest.mark.asyncio
    async def test_educational_effectiveness_scoring(self, quality_assessor):
        """Test educational effectiveness scoring across different content qualities"""

        content_examples = [
            {
                "content": {
                    "learning_objectives": ["Understand photosynthesis", "Apply knowledge to real scenarios"],
                    "examples": ["Plant experiment", "Real-world application"],
                    "exercises": ["Practice problems", "Hands-on activities"],
                    "content": "This content teaches students to understand and apply photosynthesis concepts through examples and practice."
                },
                "expected": "high",
                "description": "Comprehensive educational content"
            },
            {
                "content": {
                    "content": "Some basic information about plants and how they work in nature."
                },
                "expected": "low",
                "description": "Minimal educational structure"
            }
        ]

        for example in content_examples:
            result = await quality_assessor.assess_content_quality(
                content=example["content"],
                content_type="study_guide",
                age_group="high_school"
            )

            effectiveness = result["educational_effectiveness"]
            print(f"   {example['description']}: {effectiveness:.3f}")

            if example["expected"] == "high":
                assert effectiveness >= 0.75, f"High-quality educational content should meet threshold: {effectiveness}"
            elif example["expected"] == "low":
                assert effectiveness < 0.75, f"Low-quality educational content should not meet threshold: {effectiveness}"

        print(f"✅ Educational effectiveness scoring validated")

    @pytest.mark.asyncio
    async def test_quality_improvement_suggestions(self, quality_assessor):
        """Test that quality improvement suggestions are relevant and actionable"""

        # Content with various quality issues
        problematic_content = {
            "content": """
            Some information about a topic. No clear structure.
            No examples or exercises. No learning objectives stated.
            Information presented without sources or verification.
            """
        }

        result = await quality_assessor.assess_content_quality(
            content=problematic_content,
            content_type="study_guide",
            age_group="high_school"
        )

        suggestions = result["quality_improvement_suggestions"]
        assert len(suggestions) > 0, "Should provide improvement suggestions for poor content"

        # Check for common suggestion types
        suggestion_text = " ".join(suggestions).lower()

        expected_suggestion_themes = [
            "learning objectives",  # Educational effectiveness
            "sources",             # Factual accuracy
            "structure",           # Structural quality
            "examples"             # Engagement
        ]

        themes_found = sum(1 for theme in expected_suggestion_themes if theme in suggestion_text)
        assert themes_found >= 2, f"Should suggest improvements for multiple quality dimensions: {suggestions}"

        print(f"✅ Quality improvement suggestions generated: {len(suggestions)} suggestions")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"   {i}. {suggestion}")

    @pytest.mark.asyncio
    async def test_blooms_taxonomy_alignment(self, quality_assessor):
        """Test Bloom's taxonomy alignment assessment"""

        blooms_content = {
            "content": """
            Students will remember the basic facts about photosynthesis.
            They will understand how plants convert sunlight to energy.
            Students will apply this knowledge to analyze plant growth.
            Finally, they will evaluate different environmental factors
            and create their own experiment design.
            """
        }

        result = await quality_assessor.assess_content_quality(
            content=blooms_content,
            content_type="study_guide",
            age_group="high_school"
        )

        blooms_score = result["blooms_taxonomy_alignment"]
        assert blooms_score > 0.0, "Should calculate Bloom's taxonomy alignment"
        assert blooms_score <= 1.0, "Bloom's score should be within valid range"

        print(f"✅ Bloom's taxonomy alignment: {blooms_score:.3f}")

    @pytest.mark.asyncio
    async def test_quality_assessment_metadata(self, quality_assessor):
        """Test that quality assessment metadata is comprehensive"""

        content = {"content": "Sample educational content for metadata testing."}

        result = await quality_assessor.assess_content_quality(
            content=content,
            content_type="study_guide",
            age_group="high_school"
        )

        metadata = result["assessment_metadata"]

        # Check required metadata fields
        required_fields = [
            "content_type", "age_group", "text_length",
            "has_learning_objectives", "assessment_version", "assessed_at"
        ]

        for field in required_fields:
            assert field in metadata, f"Missing required metadata field: {field}"

        assert metadata["assessment_version"] == "2.0", "Should use correct assessment version"
        assert metadata["content_type"] == "study_guide", "Should record correct content type"
        assert metadata["age_group"] == "high_school", "Should record correct age group"
        assert isinstance(metadata["text_length"], int), "Text length should be integer"

        print(f"✅ Quality assessment metadata complete: version {metadata['assessment_version']}")

class TestQualityAssessmentPerformance:
    """Performance tests for quality assessment system"""

    @pytest.fixture
    def quality_assessor(self):
        return EducationalQualityAssessor()

    @pytest.mark.asyncio
    async def test_assessment_performance(self, quality_assessor):
        """Test that quality assessment completes within performance requirements"""
        import time

        content = {
            "title": "Performance Test Content",
            "content": "Sample content for performance testing. " * 100,  # Moderate size content
            "examples": ["Example 1", "Example 2"],
            "exercises": ["Exercise 1", "Exercise 2"]
        }

        start_time = time.time()

        result = await quality_assessor.assess_content_quality(
            content=content,
            content_type="study_guide",
            age_group="high_school"
        )

        end_time = time.time()
        assessment_time = end_time - start_time

        # Should complete within 5 seconds as per requirements
        assert assessment_time < 5.0, f"Quality assessment took {assessment_time:.2f}s, should be <5s"
        assert "overall_quality_score" in result, "Should return complete results"

        print(f"✅ Performance test passed: {assessment_time:.3f}s assessment time")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
