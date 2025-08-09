"""
Real AI Content Validation Tests for La Factoria
===============================================

Comprehensive validation of all 8 educational content types with REAL AI providers.
Tests quality thresholds, educational standards, and content structure for production readiness.

IMPORTANT: This test uses REAL AI providers and will consume tokens/credits.
Only run when you have proper API keys configured and want to validate production readiness.
"""

import pytest
import asyncio
import os
import json
from typing import Dict, Any, List
from datetime import datetime

# Skip entire module if no AI API keys configured
pytest_plugins = []

# Check for AI API keys - skip module if not configured for real AI testing
skip_real_ai = not any([
    os.getenv("OPENAI_API_KEY"),
    os.getenv("ANTHROPIC_API_KEY"), 
    os.getenv("GOOGLE_CLOUD_PROJECT")
])

if skip_real_ai:
    pytestmark = pytest.mark.skip("Real AI testing requires API keys - use --real-ai flag to enable")

# Fix Python path for src imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.educational_content_service import EducationalContentService
from src.models.educational import LaFactoriaContentType, LearningLevel, CognitiveLevel, LearningObjective

class TestRealAIContentValidation:
    """Validate all 8 content types with real AI providers for production readiness"""

    @pytest.fixture(scope="class")
    async def content_service(self):
        """Initialize real content service with AI providers"""
        service = EducationalContentService()
        await service.initialize()
        return service

    @pytest.fixture(scope="class")
    def sample_topics(self):
        """High-quality educational topics for comprehensive testing"""
        return {
            "elementary": "Life Cycle of a Butterfly",
            "middle_school": "Introduction to Algebra",
            "high_school": "Photosynthesis and Cellular Respiration",
            "college": "Machine Learning Fundamentals",
            "general": "Climate Change and Environmental Science"
        }

    @pytest.fixture(scope="class") 
    def quality_thresholds(self):
        """Production quality thresholds from La Factoria standards"""
        return {
            "overall_minimum": 0.70,       # Overall quality score
            "educational_minimum": 0.75,   # Educational value
            "factual_minimum": 0.85,       # Factual accuracy
            "engagement_minimum": 0.65,    # Student engagement
            "structural_minimum": 0.70     # Content organization
        }

    @pytest.fixture(scope="class")
    def educational_learning_objectives(self):
        """Sample learning objectives for different cognitive levels"""
        return [
            LearningObjective(
                cognitive_level=CognitiveLevel.UNDERSTANDING,
                subject_area="Science",
                specific_skill="photosynthesis process",
                measurable_outcome="explain the steps of photosynthesis with 80% accuracy",
                difficulty_level=6
            ),
            LearningObjective(
                cognitive_level=CognitiveLevel.APPLYING,
                subject_area="Science", 
                specific_skill="energy conversion",
                measurable_outcome="solve energy conversion problems correctly",
                difficulty_level=7
            )
        ]

    # ========================================
    # COMPREHENSIVE CONTENT TYPE VALIDATION
    # ========================================

    @pytest.mark.asyncio
    @pytest.mark.real_ai
    async def test_master_content_outline_real_ai(
        self, content_service, sample_topics, quality_thresholds, educational_learning_objectives
    ):
        """Test master content outline generation with real AI"""
        
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.MASTER_CONTENT_OUTLINE.value,
            topic=sample_topics["high_school"],
            age_group="high_school",
            learning_objectives=educational_learning_objectives,
            additional_requirements="Include assessment strategies and timeline"
        )

        # Validate response structure
        assert "id" in result
        assert "content_type" in result
        assert result["content_type"] == "master_content_outline"
        assert "generated_content" in result
        assert "quality_metrics" in result
        assert "metadata" in result

        # Validate generated content structure - master outline specific
        content = result["generated_content"]
        assert "title" in content
        assert "overview" in content
        assert "learning_objectives" in content
        assert "sections" in content
        assert isinstance(content["sections"], list)
        assert len(content["sections"]) >= 3, "Master outline should have at least 3 main sections"

        # Validate section structure
        for section in content["sections"][:3]:  # Check first 3 sections
            assert "title" in section, f"Section missing title: {section}"
            assert any(key in section for key in ["duration", "content", "description", "objectives"]), f"Section missing content: {section}"

        # Validate quality thresholds
        quality = result["quality_metrics"]
        await self._validate_quality_thresholds(quality, quality_thresholds, "master_content_outline")

        # Educational standards validation
        await self._validate_educational_standards(content, "high_school", "master_content_outline")
        
        print(f"✅ Master Content Outline: Quality={quality.get('overall_quality_score', 0):.2f}")

    @pytest.mark.asyncio
    @pytest.mark.real_ai
    async def test_study_guide_real_ai(
        self, content_service, sample_topics, quality_thresholds, educational_learning_objectives
    ):
        """Test study guide generation with real AI"""
        
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.STUDY_GUIDE.value,
            topic=sample_topics["college"],
            age_group="college",
            learning_objectives=educational_learning_objectives,
            additional_requirements="Include practice problems and self-assessment questions"
        )

        # Validate response structure
        assert result["content_type"] == "study_guide"
        
        # Validate study guide specific structure
        content = result["generated_content"]
        assert "title" in content
        
        # Study guides should have educational structure
        expected_elements = ["sections", "chapters", "modules", "topics", "content"]
        has_structure = any(element in content for element in expected_elements)
        assert has_structure, f"Study guide missing structural elements. Keys: {list(content.keys())}"

        # Quality validation
        quality = result["quality_metrics"]
        await self._validate_quality_thresholds(quality, quality_thresholds, "study_guide")
        
        # Educational standards validation  
        await self._validate_educational_standards(content, "college", "study_guide")
        
        print(f"✅ Study Guide: Quality={quality.get('overall_quality_score', 0):.2f}")

    @pytest.mark.asyncio
    @pytest.mark.real_ai
    async def test_flashcards_real_ai(
        self, content_service, sample_topics, quality_thresholds
    ):
        """Test flashcards generation with real AI"""
        
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.FLASHCARDS.value,
            topic=sample_topics["middle_school"],
            age_group="middle_school",
            additional_requirements="Create 10-15 flashcards focusing on key vocabulary and concepts"
        )

        # Validate response structure
        assert result["content_type"] == "flashcards"
        
        # Validate flashcard specific structure
        content = result["generated_content"]
        assert "title" in content

        # Should contain cards in some format
        card_indicators = ["cards", "flashcards", "terms", "questions"]
        has_cards = any(indicator in content for indicator in card_indicators)
        assert has_cards, f"Flashcards missing card structure. Keys: {list(content.keys())}"

        # If cards exist, validate card structure
        if "cards" in content and isinstance(content["cards"], list):
            assert len(content["cards"]) >= 5, "Should have at least 5 flashcards"
            
            # Validate card structure - flexible to handle different formats
            for i, card in enumerate(content["cards"][:3]):  # Check first 3 cards
                has_question = any(key in card for key in ["front", "question", "term", "prompt"])
                has_answer = any(key in card for key in ["back", "answer", "definition", "response"])
                assert has_question, f"Card {i} missing question/front: {card}"
                assert has_answer, f"Card {i} missing answer/back: {card}"

        # Quality validation
        quality = result["quality_metrics"]
        await self._validate_quality_thresholds(quality, quality_thresholds, "flashcards")
        
        print(f"✅ Flashcards: Quality={quality.get('overall_quality_score', 0):.2f}")

    @pytest.mark.asyncio
    @pytest.mark.real_ai
    async def test_podcast_script_real_ai(
        self, content_service, sample_topics, quality_thresholds
    ):
        """Test podcast script generation with real AI"""
        
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.PODCAST_SCRIPT.value,
            topic=sample_topics["general"],
            age_group="general",
            additional_requirements="Include speaker notes and timing guidance for 15-20 minute episode"
        )

        # Validate response structure  
        assert result["content_type"] == "podcast_script"
        
        # Validate podcast script structure
        content = result["generated_content"]
        assert "title" in content
        
        # Podcast scripts should have conversational elements
        script_indicators = ["script", "dialogue", "segments", "sections", "introduction", "conclusion"]
        has_script_structure = any(indicator in content for indicator in script_indicators)
        assert has_script_structure, f"Podcast script missing structure. Keys: {list(content.keys())}"

        # Quality validation
        quality = result["quality_metrics"] 
        await self._validate_quality_thresholds(quality, quality_thresholds, "podcast_script")
        
        print(f"✅ Podcast Script: Quality={quality.get('overall_quality_score', 0):.2f}")

    @pytest.mark.asyncio
    @pytest.mark.real_ai
    @pytest.mark.parametrize("content_type", [
        "one_pager_summary",
        "detailed_reading_material", 
        "faq_collection",
        "reading_guide_questions"
    ])
    async def test_remaining_content_types_real_ai(
        self, content_service, sample_topics, quality_thresholds, content_type
    ):
        """Test remaining 4 content types with real AI"""
        
        # Select appropriate topic and age group for content type
        topic_mapping = {
            "one_pager_summary": ("elementary", sample_topics["elementary"]),
            "detailed_reading_material": ("college", sample_topics["college"]),
            "faq_collection": ("high_school", sample_topics["high_school"]),
            "reading_guide_questions": ("high_school", sample_topics["high_school"])
        }
        
        age_group, topic = topic_mapping[content_type]
        
        result = await content_service.generate_content(
            content_type=content_type,
            topic=topic,
            age_group=age_group,
            additional_requirements=f"Optimize for {age_group} educational level with clear learning focus"
        )

        # Validate basic response structure
        assert result["content_type"] == content_type
        assert "generated_content" in result
        assert "quality_metrics" in result

        # Validate generated content structure
        content = result["generated_content"]
        assert "title" in content
        assert isinstance(content, dict)
        assert len(content) > 1, f"Content should have multiple fields beyond title"

        # Content type specific validations
        if content_type == "faq_collection":
            faq_indicators = ["faqs", "questions", "qa_pairs", "faq_list"]
            has_faqs = any(indicator in content for indicator in faq_indicators)
            assert has_faqs, f"FAQ collection missing FAQ structure. Keys: {list(content.keys())}"
            
        elif content_type == "reading_guide_questions":
            question_indicators = ["questions", "discussion_questions", "guide_questions", "reading_questions"]
            has_questions = any(indicator in content for indicator in question_indicators)
            assert has_questions, f"Reading guide missing questions. Keys: {list(content.keys())}"

        # Quality validation
        quality = result["quality_metrics"]
        await self._validate_quality_thresholds(quality, quality_thresholds, content_type)
        
        print(f"✅ {content_type.replace('_', ' ').title()}: Quality={quality.get('overall_quality_score', 0):.2f}")

    # ========================================
    # COMPREHENSIVE QUALITY VALIDATION
    # ========================================

    @pytest.mark.asyncio
    @pytest.mark.real_ai
    async def test_batch_generation_quality_real_ai(
        self, content_service, sample_topics, quality_thresholds
    ):
        """Test batch generation with real AI - quality consistency across multiple types"""
        
        # Test batch generation with 4 content types
        content_types = ["study_guide", "flashcards", "one_pager_summary", "faq_collection"]
        
        result = await content_service.generate_multiple_content_types(
            topic=sample_topics["high_school"],
            content_types=content_types,
            age_group="high_school",
            additional_requirements="Focus on exam preparation and student comprehension"
        )

        # Validate batch response structure
        assert "results" in result
        assert len(result["results"]) == len(content_types)
        assert "summary" in result

        # Validate each generated content type
        for content_type in content_types:
            assert content_type in result["results"]
            content_result = result["results"][content_type]
            
            # Basic structure validation
            assert "generated_content" in content_result
            assert "quality_metrics" in content_result
            assert content_result["content_type"] == content_type

            # Quality threshold validation
            quality = content_result["quality_metrics"]
            await self._validate_quality_thresholds(quality, quality_thresholds, f"batch_{content_type}")

        # Validate batch summary metrics
        summary = result["summary"]
        assert summary["successful_generations"] == len(content_types)
        assert summary["failed_generations"] == 0
        assert summary["average_quality_score"] >= quality_thresholds["overall_minimum"]
        
        print(f"✅ Batch Generation: {len(content_types)} types, Avg Quality={summary['average_quality_score']:.2f}")

    # ========================================
    # EDUCATIONAL STANDARDS VALIDATION
    # ========================================

    @pytest.mark.asyncio
    @pytest.mark.real_ai  
    async def test_age_appropriate_language_validation(
        self, content_service, quality_thresholds
    ):
        """Test that content language complexity matches target age groups"""
        
        test_cases = [
            ("elementary", "Animals and Their Habitats"),
            ("middle_school", "Introduction to Fractions and Decimals"), 
            ("high_school", "Newton's Laws of Motion"),
            ("college", "Statistical Hypothesis Testing")
        ]

        results = {}
        
        for age_group, topic in test_cases:
            result = await content_service.generate_content(
                content_type=LaFactoriaContentType.STUDY_GUIDE.value,
                topic=topic,
                age_group=age_group,
                additional_requirements=f"Ensure language complexity is appropriate for {age_group} level"
            )
            
            results[age_group] = result
            
            # Validate age-appropriate quality metrics
            quality = result["quality_metrics"]
            
            # Age appropriateness should be high for target level
            age_appropriateness = quality.get("age_appropriateness", quality.get("readability_score", {}).get("age_appropriateness_score", 0))
            if isinstance(age_appropriateness, dict):
                age_appropriateness = age_appropriateness.get("age_appropriateness_score", 0)
                
            assert age_appropriateness >= 0.7, f"{age_group}: Age appropriateness too low ({age_appropriateness:.2f})"
            
            # Educational effectiveness should be maintained
            educational_effectiveness = quality.get("educational_effectiveness", quality.get("educational_value", 0))
            assert educational_effectiveness >= quality_thresholds["educational_minimum"], \
                f"{age_group}: Educational effectiveness too low ({educational_effectiveness:.2f})"

        # Validate complexity progression (optional - complexity should generally increase with age)
        complexity_scores = []
        for age_group in ["elementary", "middle_school", "high_school", "college"]:
            if age_group in results:
                # Use a proxy for complexity - could be readability score or content length
                content = results[age_group]["generated_content"]
                content_text = str(content)
                complexity_proxy = len(content_text.split()) / 100  # Words per hundred as complexity proxy
                complexity_scores.append((age_group, complexity_proxy))

        print("📊 Age Appropriateness Validation:")
        for age_group, topic in test_cases:
            if age_group in results:
                quality = results[age_group]["quality_metrics"]
                age_score = quality.get("age_appropriateness", "N/A")
                educational_score = quality.get("educational_effectiveness", quality.get("educational_value", "N/A"))
                print(f"  {age_group}: Age={age_score:.2f}, Educational={educational_score:.2f}")

    # ========================================
    # PERFORMANCE AND RELIABILITY VALIDATION  
    # ========================================

    @pytest.mark.asyncio
    @pytest.mark.real_ai
    async def test_generation_time_performance(
        self, content_service, sample_topics
    ):
        """Test that content generation completes within reasonable time limits"""
        
        # Test performance for different content types
        performance_tests = [
            ("flashcards", 30),           # Should be fast - 30 seconds
            ("one_pager_summary", 45),    # Medium - 45 seconds
            ("study_guide", 60),          # Longer - 60 seconds
            ("detailed_reading_material", 90)  # Longest - 90 seconds
        ]

        performance_results = {}
        
        for content_type, max_time_seconds in performance_tests:
            start_time = datetime.now()
            
            result = await content_service.generate_content(
                content_type=content_type,
                topic=sample_topics["high_school"],
                age_group="high_school",
                additional_requirements="Generate high-quality educational content efficiently"
            )
            
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            # Validate generation completed within time limit
            assert generation_time <= max_time_seconds, \
                f"{content_type} took {generation_time:.1f}s (limit: {max_time_seconds}s)"
            
            # Validate quality wasn't sacrificed for speed
            quality = result["quality_metrics"]
            overall_quality = quality.get("overall_quality_score", 0)
            assert overall_quality >= 0.65, \
                f"{content_type} quality too low for time constraint: {overall_quality:.2f}"
                
            performance_results[content_type] = {
                "generation_time": generation_time,
                "quality_score": overall_quality
            }

        print("⚡ Performance Validation Results:")
        for content_type, metrics in performance_results.items():
            print(f"  {content_type}: {metrics['generation_time']:.1f}s, Quality={metrics['quality_score']:.2f}")

    # ========================================
    # HELPER METHODS
    # ========================================

    async def _validate_quality_thresholds(
        self, quality_metrics: Dict[str, Any], thresholds: Dict[str, float], content_type: str
    ):
        """Validate that quality metrics meet La Factoria production thresholds"""
        
        # Overall quality score validation
        overall_score = quality_metrics.get("overall_quality_score", 0)
        assert overall_score >= thresholds["overall_minimum"], \
            f"{content_type}: Overall quality {overall_score:.2f} below threshold {thresholds['overall_minimum']}"

        # Educational effectiveness validation  
        educational_score = quality_metrics.get("educational_effectiveness", quality_metrics.get("educational_value", 0))
        assert educational_score >= thresholds["educational_minimum"], \
            f"{content_type}: Educational value {educational_score:.2f} below threshold {thresholds['educational_minimum']}"

        # Factual accuracy validation
        factual_score = quality_metrics.get("factual_accuracy", 0)
        assert factual_score >= thresholds["factual_minimum"], \
            f"{content_type}: Factual accuracy {factual_score:.2f} below threshold {thresholds['factual_minimum']}"

        # Engagement validation (if present)
        engagement_score = quality_metrics.get("engagement_score", quality_metrics.get("engagement_level", 0))
        if engagement_score > 0:  # Only validate if engagement score exists
            assert engagement_score >= thresholds["engagement_minimum"], \
                f"{content_type}: Engagement {engagement_score:.2f} below threshold {thresholds['engagement_minimum']}"

        # Structural quality validation (if present)
        structural_score = quality_metrics.get("structural_quality", 0)
        if structural_score > 0:  # Only validate if structural score exists
            assert structural_score >= thresholds["structural_minimum"], \
                f"{content_type}: Structural quality {structural_score:.2f} below threshold {thresholds['structural_minimum']}"

    async def _validate_educational_standards(
        self, content: Dict[str, Any], age_group: str, content_type: str
    ):
        """Validate content meets educational standards for target age group"""
        
        # Content should not be empty
        assert content, f"{content_type}: Generated content is empty"
        
        # Should have a title
        assert "title" in content, f"{content_type}: Missing title"
        assert content["title"].strip(), f"{content_type}: Title is empty"

        # Extract text content for analysis
        content_text = self._extract_text_for_analysis(content)
        assert len(content_text) >= 50, f"{content_type}: Content too short ({len(content_text)} chars)"

        # Basic educational content validation
        educational_indicators = [
            "learn", "understand", "knowledge", "concept", "skill", "practice",
            "example", "exercise", "question", "objective", "goal"
        ]
        
        has_educational_content = any(
            indicator in content_text.lower() 
            for indicator in educational_indicators
        )
        assert has_educational_content, f"{content_type}: Lacks educational indicators"

    def _extract_text_for_analysis(self, content: Dict[str, Any]) -> str:
        """Extract text content from structured content for analysis"""
        text_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str):
                        text_parts.append(value)
                    else:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
            elif isinstance(obj, str):
                text_parts.append(obj)
                
        extract_recursive(content)
        return " ".join(text_parts)

    # ========================================
    # COMPREHENSIVE TEST SUMMARY
    # ========================================

    @pytest.mark.asyncio
    @pytest.mark.real_ai
    async def test_comprehensive_validation_summary(
        self, content_service, sample_topics, quality_thresholds
    ):
        """Comprehensive validation summary - production readiness report"""
        
        print("\n" + "="*60)
        print("🎓 LA FACTORIA REAL AI VALIDATION SUMMARY")
        print("="*60)
        
        # Test all 8 content types quickly for summary
        all_content_types = [ct.value for ct in LaFactoriaContentType]
        summary_results = {}
        
        for content_type in all_content_types:
            try:
                result = await content_service.generate_content(
                    content_type=content_type,
                    topic=sample_topics["general"],
                    age_group="general",
                    additional_requirements="Production validation test"
                )
                
                quality = result["quality_metrics"]
                summary_results[content_type] = {
                    "success": True,
                    "quality_score": quality.get("overall_quality_score", 0),
                    "educational_value": quality.get("educational_effectiveness", quality.get("educational_value", 0)),
                    "factual_accuracy": quality.get("factual_accuracy", 0)
                }
                
            except Exception as e:
                summary_results[content_type] = {
                    "success": False,
                    "error": str(e)
                }

        # Generate summary report
        successful_types = [ct for ct, result in summary_results.items() if result.get("success")]
        failed_types = [ct for ct, result in summary_results.items() if not result.get("success")]
        
        print(f"✅ Successful Content Types: {len(successful_types)}/8")
        print(f"❌ Failed Content Types: {len(failed_types)}/8")
        
        if successful_types:
            avg_quality = sum(summary_results[ct]["quality_score"] for ct in successful_types) / len(successful_types)
            avg_educational = sum(summary_results[ct]["educational_value"] for ct in successful_types) / len(successful_types)
            avg_factual = sum(summary_results[ct]["factual_accuracy"] for ct in successful_types) / len(successful_types)
            
            print(f"📊 Average Quality Scores:")
            print(f"   Overall: {avg_quality:.3f} (threshold: {quality_thresholds['overall_minimum']:.2f})")
            print(f"   Educational: {avg_educational:.3f} (threshold: {quality_thresholds['educational_minimum']:.2f})")
            print(f"   Factual: {avg_factual:.3f} (threshold: {quality_thresholds['factual_minimum']:.2f})")

        print(f"\n🎯 Production Readiness Assessment:")
        readiness_score = (len(successful_types) / 8) * 100
        print(f"   Content Type Coverage: {readiness_score:.1f}%")
        
        if readiness_score >= 87.5:  # 7/8 types working
            print(f"   Status: ✅ PRODUCTION READY")
        elif readiness_score >= 75.0:  # 6/8 types working  
            print(f"   Status: ⚠️  MOSTLY READY - Minor issues")
        else:
            print(f"   Status: ❌ NOT READY - Major issues")

        print("="*60)
        
        # Assert overall success for test completion
        assert len(successful_types) >= 6, f"Only {len(successful_types)}/8 content types working - below production threshold"
        
        if successful_types:
            assert avg_quality >= quality_thresholds["overall_minimum"], \
                f"Average quality {avg_quality:.2f} below threshold {quality_thresholds['overall_minimum']}"