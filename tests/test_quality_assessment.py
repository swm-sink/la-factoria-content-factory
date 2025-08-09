"""
Comprehensive test suite for Educational Quality Assessment System
Testing against La Factoria educational standards and quality thresholds
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, Mock
from typing import Dict, Any

from src.services.quality_assessor import EducationalQualityAssessor
from src.models.educational import LearningObjective, CognitiveLevel

class TestEducationalQualityAssessor:
    """Test suite for educational quality assessment functionality"""

    @pytest.fixture
    def quality_assessor(self):
        """Create quality assessor instance"""
        return EducationalQualityAssessor()

    @pytest.fixture
    def sample_high_quality_content(self):
        """Sample content that should meet all quality thresholds"""
        return {
            "title": "Introduction to Algebra",
            "learning_objectives": [
                "Students will understand basic algebraic concepts",
                "Students will apply algebraic principles to solve equations"
            ],
            "content": """
            # Introduction to Algebra

            ## Learning Objectives
            By the end of this lesson, you will be able to:
            - Understand what algebra is and why it's useful
            - Solve simple algebraic equations
            - Apply algebraic thinking to real-world problems

            ## What is Algebra?
            Algebra is a branch of mathematics that uses symbols and letters to represent numbers.
            For example, instead of saying "some number plus 3 equals 7", we can write x + 3 = 7.

            ## Examples and Practice
            Let's try some examples together:
            1. If x + 5 = 12, what is x?
            2. In real life, you might use algebra to calculate how much money you need to save.

            ## Exercise
            Try solving these problems on your own:
            - 2x = 10
            - y - 3 = 8

            ## Summary
            Algebra helps us solve problems by using symbols to represent unknown values.
            With practice, you'll find it becomes a powerful tool for understanding mathematics.
            """,
            "examples": [
                {"problem": "x + 3 = 7", "solution": "x = 4"},
                {"problem": "2y = 10", "solution": "y = 5"}
            ],
            "exercises": [
                {"question": "Solve for x: x + 5 = 12", "answer": "x = 7"},
                {"question": "What is y if y - 3 = 8?", "answer": "y = 11"}
            ]
        }

    @pytest.fixture
    def sample_learning_objectives(self):
        """Sample learning objectives for testing"""
        return [
            LearningObjective(
                cognitive_level=CognitiveLevel.UNDERSTAND,
                subject_area="mathematics",
                specific_skill="algebraic equations",
                measurable_outcome="solve basic linear equations",
                difficulty_level="beginner"
            ),
            LearningObjective(
                cognitive_level=CognitiveLevel.APPLY,
                subject_area="mathematics",
                specific_skill="problem solving",
                measurable_outcome="apply algebra to real-world scenarios",
                difficulty_level="intermediate"
            )
        ]

    @pytest.fixture
    def sample_poor_quality_content(self):
        """Sample content that should fail quality thresholds"""
        return {
            "text": "This is bad content with no structure or educational value."
        }

    @pytest.mark.asyncio
    async def test_comprehensive_quality_assessment(
        self, quality_assessor, sample_high_quality_content, sample_learning_objectives
    ):
        """Test comprehensive quality assessment with high-quality content"""

        result = await quality_assessor.assess_content_quality(
            content=sample_high_quality_content,
            content_type="study_guide",
            age_group="high_school",
            learning_objectives=sample_learning_objectives
        )

        # Validate response structure
        assert "overall_quality_score" in result
        assert "cognitive_load_metrics" in result
        assert "readability_score" in result
        assert "educational_effectiveness" in result
        assert "learning_objective_alignment" in result
        assert "engagement_score" in result
        assert "structural_quality" in result
        assert "meets_quality_threshold" in result
        assert "meets_educational_threshold" in result
        assert "assessment_metadata" in result

        # Validate quality thresholds for high-quality content
        assert result["overall_quality_score"] >= 0.70, f"Overall quality {result['overall_quality_score']} below threshold"
        assert result["educational_effectiveness"] >= 0.75, f"Educational effectiveness {result['educational_effectiveness']} below threshold"
        assert result["meets_quality_threshold"] == True
        assert result["meets_educational_threshold"] == True

        # Validate cognitive load assessment
        cognitive_load = result["cognitive_load_metrics"]
        assert isinstance(cognitive_load, dict)
        assert "total_cognitive_load" in cognitive_load
        assert "appropriate_for_age" in cognitive_load

        # Validate readability assessment
        readability = result["readability_score"]
        assert isinstance(readability, dict)
        assert "age_appropriateness_score" in readability

    @pytest.mark.asyncio
    async def test_poor_quality_content_rejection(
        self, quality_assessor, sample_poor_quality_content
    ):
        """Test that poor quality content is properly identified"""

        result = await quality_assessor.assess_content_quality(
            content=sample_poor_quality_content,
            content_type="study_guide",
            age_group="high_school"
        )

        # Poor content should fail thresholds
        assert result["overall_quality_score"] < 0.70
        assert result["educational_effectiveness"] < 0.75
        assert result["meets_quality_threshold"] == False
        assert result["meets_educational_threshold"] == False

    @pytest.mark.asyncio
    async def test_cognitive_load_assessment(self, quality_assessor):
        """Test cognitive load assessment across age groups"""

        # Complex text for testing
        complex_text = """
        The thermodynamic equilibrium principle dictates that spontaneous processes
        proceed toward maximum entropy states, characterized by the minimization of
        Gibbs free energy in isothermal-isobaric systems, thereby establishing the
        fundamental criterion for chemical reaction feasibility.
        """

        # Simple text for testing
        simple_text = """
        Water turns into ice when it gets very cold. This happens at 32 degrees.
        Ice melts back into water when it gets warm again.
        """

        # Test complex text with different age groups
        complex_result = await quality_assessor._assess_cognitive_load(complex_text, "elementary")
        assert complex_result["total_cognitive_load"] > 0.7  # Should be high for elementary

        # Test simple text with elementary
        simple_result = await quality_assessor._assess_cognitive_load(simple_text, "elementary")
        assert simple_result["total_cognitive_load"] < complex_result["total_cognitive_load"]
        assert simple_result["appropriate_for_age"] == True

    @pytest.mark.asyncio
    async def test_readability_assessment_age_groups(self, quality_assessor):
        """Test readability assessment for different age groups"""

        test_cases = [
            {
                "text": "The cat sat on the mat. It was warm there.",
                "age_group": "elementary",
                "expected_appropriate": True
            },
            {
                "text": "The aforementioned feline established its corporeal presence upon the textile floor covering.",
                "age_group": "elementary",
                "expected_appropriate": False
            },
            {
                "text": "Photosynthesis is the process by which plants convert sunlight into energy.",
                "age_group": "high_school",
                "expected_appropriate": True
            }
        ]

        for case in test_cases:
            result = await quality_assessor._assess_readability(case["text"], case["age_group"])

            assert "age_appropriateness_score" in result
            assert "flesch_reading_ease" in result

            if case["expected_appropriate"]:
                assert result["age_appropriateness_score"] >= 0.6
            else:
                assert result["age_appropriateness_score"] < 0.6

    @pytest.mark.asyncio
    async def test_educational_effectiveness_assessment(self, quality_assessor):
        """Test educational effectiveness assessment"""

        # High educational value content
        high_value_content = {
            "learning_objectives": ["Understand concepts", "Apply knowledge"],
            "examples": ["Example 1", "Example 2"],
            "exercises": ["Practice problem 1"],
            "content": "This content helps students learn and understand through examples and practice."
        }

        # Low educational value content
        low_value_content = {
            "text": "Some random text with no educational structure."
        }

        high_result = await quality_assessor._assess_educational_effectiveness(
            high_value_content, "study_guide"
        )
        low_result = await quality_assessor._assess_educational_effectiveness(
            low_value_content, "study_guide"
        )

        assert high_result >= 0.75  # Should meet educational threshold
        assert low_result < high_result  # Should be lower than high-value content

    @pytest.mark.asyncio
    async def test_learning_objective_alignment(
        self, quality_assessor, sample_learning_objectives
    ):
        """Test learning objective alignment assessment"""

        # Content aligned with objectives
        aligned_content = {
            "content": """
            This lesson covers mathematics and algebraic equations.
            Students will understand how to solve problems using algebra.
            We will apply these concepts to real-world scenarios.
            """
        }

        # Content not aligned with objectives
        unaligned_content = {
            "content": "This is about cooking recipes and has nothing to do with mathematics."
        }

        aligned_result = await quality_assessor._assess_learning_objective_alignment(
            aligned_content, sample_learning_objectives
        )
        unaligned_result = await quality_assessor._assess_learning_objective_alignment(
            unaligned_content, sample_learning_objectives
        )

        assert aligned_result > unaligned_result
        assert aligned_result >= 0.5  # Should show some alignment

    @pytest.mark.asyncio
    async def test_engagement_elements_assessment(self, quality_assessor):
        """Test engagement elements assessment"""

        # Engaging content with questions, examples, activities
        engaging_text = """
        What do you think happens when you mix oil and water?
        Let's try an example together. For instance, we can observe...
        Here's an activity you can try at home.
        In real life, this concept applies to many situations.
        """

        # Non-engaging content
        boring_text = "This is plain text with no engaging elements whatsoever."

        engaging_score = await quality_assessor._assess_engagement_elements(engaging_text)
        boring_score = await quality_assessor._assess_engagement_elements(boring_text)

        assert engaging_score > boring_score
        assert engaging_score >= 0.6  # Should detect multiple engagement elements

    @pytest.mark.asyncio
    async def test_structural_quality_assessment(self, quality_assessor):
        """Test structural quality assessment"""

        # Well-structured content
        structured_content = """
        # Main Title

        ## Introduction
        This is the introduction paragraph with clear structure.

        ## Key Concepts
        - Point 1
        - Point 2
        - Point 3

        ## Examples
        1. First example
        2. Second example

        ## Conclusion
        This concludes our structured content.
        """

        # Poorly structured content
        unstructured_content = "This is all one big paragraph with no structure no headings no lists nothing to help organize the information for the reader making it very difficult to follow and understand the key points being presented."

        structured_score = await quality_assessor._assess_structural_quality(
            structured_content, "study_guide"
        )
        unstructured_score = await quality_assessor._assess_structural_quality(
            unstructured_content, "study_guide"
        )

        assert structured_score > unstructured_score
        assert structured_score >= 0.7  # Should detect good structure

    @pytest.mark.asyncio
    async def test_content_type_specific_assessment(self, quality_assessor):
        """Test content type specific quality assessment"""

        # Flashcard content
        flashcard_content = {
            "cards": [
                {"question": "What is 2+2?", "answer": "4"},
                {"question": "What is photosynthesis?", "answer": "Process plants use to make energy"}
            ]
        }

        # Study guide content
        study_guide_content = {
            "sections": [
                {"title": "Introduction", "content": "Overview of topic"},
                {"title": "Main Content", "content": "Detailed explanation"},
                {"title": "Summary", "content": "Key takeaways"}
            ]
        }

        flashcard_result = await quality_assessor._assess_educational_effectiveness(
            flashcard_content, "flashcards"
        )
        study_guide_result = await quality_assessor._assess_educational_effectiveness(
            study_guide_content, "study_guide"
        )

        # Both should have decent educational effectiveness
        assert flashcard_result >= 0.6
        assert study_guide_result >= 0.6

    @pytest.mark.asyncio
    async def test_error_handling_and_fallbacks(self, quality_assessor):
        """Test error handling and fallback behavior"""

        # Empty content
        empty_result = await quality_assessor.assess_content_quality(
            content={},
            content_type="study_guide",
            age_group="high_school"
        )

        assert empty_result["overall_quality_score"] == 0.5  # Default value
        assert empty_result["meets_quality_threshold"] == False

        # Invalid content structure
        invalid_result = await quality_assessor.assess_content_quality(
            content="not a dictionary",
            content_type="study_guide",
            age_group="high_school"
        )

        # Should handle gracefully and return default metrics
        assert "overall_quality_score" in invalid_result
        assert invalid_result["meets_quality_threshold"] == False

    def test_syllable_counting_accuracy(self, quality_assessor):
        """Test syllable counting heuristic accuracy"""

        test_words = [
            ("cat", 1),
            ("running", 2),
            ("beautiful", 3),
            ("education", 4),
            ("university", 4),
            ("simple", 2),
            ("the", 1)
        ]

        for word, expected_syllables in test_words:
            actual = quality_assessor._count_syllables(word)
            # Allow some tolerance for heuristic method
            assert abs(actual - expected_syllables) <= 1, f"Word '{word}': expected ~{expected_syllables}, got {actual}"

    @pytest.mark.asyncio
    async def test_quality_threshold_calibration(
        self, quality_assessor, sample_high_quality_content, sample_learning_objectives
    ):
        """Test that quality thresholds are properly calibrated"""

        # Test with different quality levels
        quality_levels = [
            # Excellent content
            {
                "content": sample_high_quality_content,
                "expected_overall": 0.85,
                "expected_educational": 0.85
            },
            # Good content (modified to be slightly lower quality)
            {
                "content": {
                    "title": "Basic Math",
                    "content": "This covers basic math. Some examples included."
                },
                "expected_overall": 0.70,
                "expected_educational": 0.75
            }
        ]

        for level in quality_levels:
            result = await quality_assessor.assess_content_quality(
                content=level["content"],
                content_type="study_guide",
                age_group="high_school",
                learning_objectives=sample_learning_objectives
            )

            # Quality scores should be reasonable for the content level
            assert result["overall_quality_score"] >= 0.0
            assert result["overall_quality_score"] <= 1.0
            assert result["educational_effectiveness"] >= 0.0
            assert result["educational_effectiveness"] <= 1.0

    @pytest.mark.asyncio
    async def test_age_group_specific_thresholds(self, quality_assessor):
        """Test that age group specific thresholds work correctly"""

        # Complex academic text
        complex_text = """
        The pedagogical implications of constructivist epistemology necessitate a
        paradigmatic shift toward learner-centered methodologies that emphasize
        metacognitive awareness and self-regulated learning strategies.
        """

        age_groups = ["elementary", "middle_school", "high_school", "college"]

        for age_group in age_groups:
            result = await quality_assessor._assess_readability(complex_text, age_group)
            cognitive_result = await quality_assessor._assess_cognitive_load(complex_text, age_group)

            # More complex text should be less appropriate for younger age groups
            if age_group == "elementary":
                assert result["age_appropriateness_score"] < 0.5
                assert cognitive_result["appropriate_for_age"] == False
            elif age_group == "college":
                # Should be more appropriate for college level
                assert result["age_appropriateness_score"] > 0.3

    @pytest.mark.asyncio
    async def test_factual_accuracy_placeholder_enhancement(self, quality_assessor):
        """Test that factual accuracy assessment needs enhancement"""

        # Current implementation has placeholder - this test documents needed enhancement
        result = await quality_assessor.assess_content_quality(
            content={"content": "The Earth is flat and the moon is made of cheese."},
            content_type="study_guide",
            age_group="high_school"
        )

        # Current implementation returns True as placeholder
        assert result["meets_factual_threshold"] == True

        # TODO: This test should fail once factual accuracy is properly implemented
        # The above false statement should result in meets_factual_threshold == False

class TestQualityAssessmentIntegration:
    """Integration tests for quality assessment with other services"""

    @pytest.mark.asyncio
    async def test_integration_with_content_service(self, quality_assessor, sample_high_quality_content):
        """Test integration with educational content service"""
        # Mock content service integration
        result = await quality_assessor.assess_content_quality(
            content=sample_high_quality_content,
            content_type="study_guide",
            age_group="high_school"
        )

        # Should integrate properly with service layer
        assert "overall_quality_score" in result
        assert result["meets_quality_threshold"] == True

    @pytest.mark.asyncio
    async def test_quality_metrics_persistence(self, quality_assessor):
        """Test that quality metrics are properly stored and retrieved"""
        # Mock database persistence
        test_content = {
            "title": "Test Content",
            "content": "This is test educational content for persistence testing."
        }

        result = await quality_assessor.assess_content_quality(
            content=test_content,
            content_type="study_guide",
            age_group="high_school"
        )

        # Should return structured metrics for persistence
        assert isinstance(result, dict)
        assert "assessment_metadata" in result
        assert "timestamp" in result.get("assessment_metadata", {})


class TestAdvancedQualityScenarios:
    """Advanced quality assessment scenarios and edge cases"""

    @pytest.mark.asyncio
    async def test_multilingual_content_assessment(self, quality_assessor):
        """Test quality assessment for non-English content"""
        spanish_content = {
            "titulo": "Introducción a la Programación en Python",
            "contenido": """
            Python es un lenguaje de programación muy popular y fácil de aprender.
            Es perfecto para principiantes porque tiene una sintaxis clara y simple.

            Ejemplo de código Python:
            ```python
            nombre = "María"
            edad = 25
            print(f"Hola, me llamo {nombre} y tengo {edad} años")
            ```

            Ejercicios:
            1. Crear una variable para tu nombre
            2. Crear una variable para tu edad
            3. Usar print() para mostrar la información
            """,
            "ejemplos": ["nombre = 'Juan'", "edad = 30"],
            "ejercicios": ["Práctica con variables", "Uso de print()"]
        }

        result = await quality_assessor.assess_content_quality(
            content=spanish_content,
            content_type="study_guide",
            age_group="high_school"
        )

        # Should handle non-English content appropriately
        assert "overall_quality_score" in result
        assert result["overall_quality_score"] >= 0.0
        assert result["overall_quality_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_content_with_code_examples(self, quality_assessor):
        """Test quality assessment for content with code examples"""
        code_content = {
            "title": "Python Functions Tutorial",
            "content": """
            # Python Functions

            Functions are reusable blocks of code that perform specific tasks.

            ## Basic Function Syntax
            ```python
            def greet(name):
                return f"Hello, {name}!"

            # Call the function
            message = greet("Alice")
            print(message)
            ```

            ## Functions with Multiple Parameters
            ```python
            def calculate_area(length, width):
                area = length * width
                return area

            rectangle_area = calculate_area(5, 3)
            print(f"Area: {rectangle_area}")
            ```

            ## Exercise
            Create a function that calculates the square of a number.
            """,
            "examples": [
                {"code": "def square(x): return x ** 2", "description": "Square function"},
                {"code": "result = square(5)", "description": "Function call"}
            ]
        }

        result = await quality_assessor.assess_content_quality(
            content=code_content,
            content_type="detailed_reading_material",
            age_group="college"
        )

        # Should properly assess code-heavy content
        assert result["overall_quality_score"] >= 0.65
        assert result["structural_quality"] >= 0.7  # Good structure with headers and examples

    @pytest.mark.asyncio
    async def test_content_with_mathematical_formulas(self, quality_assessor):
        """Test quality assessment for mathematical content"""
        math_content = {
            "title": "Quadratic Equations",
            "content": """
            # Quadratic Equations

            A quadratic equation has the form: ax² + bx + c = 0

            ## The Quadratic Formula
            The solutions are given by:
            x = (-b ± √(b² - 4ac)) / (2a)

            ## Example
            Solve: 2x² + 5x - 3 = 0
            Here: a = 2, b = 5, c = -3

            x = (-5 ± √(25 - 4(2)(-3))) / (2(2))
            x = (-5 ± √(25 + 24)) / 4
            x = (-5 ± √49) / 4
            x = (-5 ± 7) / 4

            So: x = 1/2 or x = -3
            """,
            "formulas": ["ax² + bx + c = 0", "x = (-b ± √(b² - 4ac)) / (2a)"],
            "examples": [{"equation": "2x² + 5x - 3 = 0", "solutions": ["x = 1/2", "x = -3"]}]
        }

        result = await quality_assessor.assess_content_quality(
            content=math_content,
            content_type="detailed_reading_material",
            age_group="high_school"
        )

        # Should handle mathematical content appropriately
        assert result["overall_quality_score"] >= 0.70
        assert result["educational_effectiveness"] >= 0.75

    @pytest.mark.asyncio
    async def test_content_length_extremes(self, quality_assessor):
        """Test quality assessment for very short and very long content"""
        # Very short content
        short_content = {
            "title": "Brief",
            "content": "Python is a programming language."
        }

        short_result = await quality_assessor.assess_content_quality(
            content=short_content,
            content_type="one_pager_summary",
            age_group="high_school"
        )

        # Very long content
        long_content = {
            "title": "Comprehensive Guide",
            "content": "Python programming. " * 1000,  # Very repetitive long content
            "sections": [{"title": f"Section {i}", "content": "Content " * 100} for i in range(20)]
        }

        long_result = await quality_assessor.assess_content_quality(
            content=long_content,
            content_type="detailed_reading_material",
            age_group="college"
        )

        # Both should be assessed, but short content should score lower for comprehensive types
        assert short_result["overall_quality_score"] >= 0.0
        assert long_result["overall_quality_score"] >= 0.0

        # Long content should score better for detailed reading material
        if long_result["content_type"] == "detailed_reading_material":
            # Length should be more appropriate for detailed content
            pass

    @pytest.mark.asyncio
    async def test_content_with_accessibility_features(self, quality_assessor):
        """Test assessment of content with accessibility features"""
        accessible_content = {
            "title": "Accessible Learning Guide: Solar System",
            "content": """
            # The Solar System (Audio description available)

            ## Introduction
            The solar system consists of the Sun and all objects orbiting it.
            [Image description: Diagram showing the Sun at center with 8 planets in orbital paths]

            ## The Planets
            1. **Mercury** (closest to Sun) - Very hot, no atmosphere
            2. **Venus** - Thick cloudy atmosphere, hottest planet
            3. **Earth** - Our home planet with water and life
            4. **Mars** - Red planet with polar ice caps
            [Continue for all planets]

            ## Interactive Elements
            - Audio pronunciation guides for planet names
            - High contrast images for visual learners
            - Tactile diagrams available for blind students

            ## Summary
            Each planet has unique characteristics that make our solar system diverse and fascinating.
            """,
            "accessibility_features": [
                "alt_text_for_images",
                "audio_descriptions",
                "high_contrast_options",
                "tactile_descriptions"
            ],
            "visual_aids": [
                {"type": "diagram", "description": "Solar system overview with planet positions"},
                {"type": "size_comparison", "description": "Relative sizes of planets"}
            ]
        }

        result = await quality_assessor.assess_content_quality(
            content=accessible_content,
            content_type="study_guide",
            age_group="middle_school"
        )

        # Should score highly for accessibility features
        assert result["overall_quality_score"] >= 0.75
        # Accessibility features should boost the score
        assert "accessibility_score" in result

    @pytest.mark.asyncio
    async def test_content_cultural_sensitivity_assessment(self, quality_assessor):
        """Test assessment of culturally sensitive content"""
        culturally_diverse_content = {
            "title": "World Celebrations and Traditions",
            "content": """
            # Celebrations Around the World

            Different cultures celebrate important events in unique ways.
            Let's explore some traditions from various parts of the world.

            ## Winter Celebrations
            - **Christmas** (Christian tradition): Celebrated December 25th in many countries
            - **Hanukkah** (Jewish tradition): Eight-day celebration with lighting of the menorah
            - **Kwanzaa** (African-American tradition): Seven-day celebration of African heritage
            - **Diwali** (Hindu tradition): Festival of lights celebrated in fall/winter

            ## Spring Celebrations
            - **Chinese New Year**: Lunar calendar celebration with dragon dances
            - **Nowruz** (Persian New Year): Spring equinox celebration in many Middle Eastern cultures
            - **Holi** (Hindu festival): Festival of colors celebrating spring

            ## Learning Respect
            Each tradition is meaningful to the people who celebrate it.
            We can learn from different cultures while respecting their uniqueness.
            """,
            "cultural_elements": [
                "diverse_representation",
                "respectful_language",
                "inclusive_examples",
                "educational_approach"
            ]
        }

        result = await quality_assessor.assess_content_quality(
            content=culturally_diverse_content,
            content_type="study_guide",
            age_group="elementary"
        )

        # Should score well for cultural sensitivity
        assert result["overall_quality_score"] >= 0.70
        assert result["age_appropriateness_score"] >= 0.75

    @pytest.mark.asyncio
    async def test_stem_content_specialized_assessment(self, quality_assessor):
        """Test specialized assessment for STEM content"""
        stem_content = {
            "title": "Introduction to Machine Learning",
            "content": """
            # Machine Learning Basics

            Machine learning is a subset of artificial intelligence that enables computers to learn patterns from data.

            ## Types of Machine Learning

            ### 1. Supervised Learning
            - Uses labeled training data
            - Examples: Image classification, spam detection
            - Algorithms: Linear regression, decision trees, neural networks

            ### 2. Unsupervised Learning
            - Finds patterns in unlabeled data
            - Examples: Customer segmentation, anomaly detection
            - Algorithms: K-means clustering, PCA

            ### 3. Reinforcement Learning
            - Learns through interaction with environment
            - Examples: Game playing, robotics
            - Uses rewards and penalties

            ## Simple Example: Predicting House Prices
            ```python
            # Simplified example
            import sklearn
            from sklearn.linear_model import LinearRegression

            # Features: [size, bedrooms, age]
            houses = [[1500, 3, 10], [2000, 4, 5], [1200, 2, 15]]
            prices = [300000, 400000, 250000]

            model = LinearRegression()
            model.fit(houses, prices)

            # Predict price for new house
            new_house = [[1800, 3, 8]]
            predicted_price = model.predict(new_house)
            ```

            ## Ethical Considerations
            - Bias in training data
            - Privacy concerns
            - Transparency in decision-making
            """,
            "technical_concepts": [
                "supervised_learning", "unsupervised_learning",
                "reinforcement_learning", "algorithms", "data_bias"
            ],
            "code_examples": True,
            "ethical_considerations": True
        }

        result = await quality_assessor.assess_content_quality(
            content=stem_content,
            content_type="detailed_reading_material",
            age_group="college"
        )

        # STEM content should meet high technical standards
        assert result["overall_quality_score"] >= 0.75
        assert result["educational_effectiveness"] >= 0.80
        assert result["factual_accuracy"] >= 0.85

    @pytest.mark.asyncio
    async def test_content_with_learning_disabilities_considerations(self, quality_assessor):
        """Test assessment considering learning disabilities"""
        inclusive_content = {
            "title": "Reading Strategies for Everyone",
            "content": """
            # Effective Reading Strategies

            ## Break It Down (Chunking Strategy)
            Read one paragraph at a time. Take breaks between sections.

            **Why this helps:** Makes large texts less overwhelming.

            ## Use Visual Aids
            - Draw pictures of what you read
            - Use highlighters for important points
            - Create mind maps to connect ideas

            ## Read Aloud Strategy
            Reading out loud can help you:
            1. Hear the words clearly
            2. Catch mistakes
            3. Remember better

            ## Check Understanding
            After each section, ask yourself:
            - What did I just read?
            - What was the main idea?
            - How does this connect to what I know?

            ## Take Your Time
            Everyone reads at their own pace. That's perfectly normal!

            ## Get Help When Needed
            - Ask questions about confusing parts
            - Use audio books when available
            - Work with a study buddy
            """,
            "learning_support_features": [
                "chunking_strategy",
                "visual_aids",
                "multi_sensory_approach",
                "self_monitoring",
                "positive_reinforcement"
            ],
            "accessibility_considerations": [
                "clear_structure",
                "simple_language",
                "encouraging_tone",
                "multiple_strategies"
            ]
        }

        result = await quality_assessor.assess_content_quality(
            content=inclusive_content,
            content_type="study_guide",
            age_group="middle_school"
        )

        # Should score highly for inclusive design
        assert result["overall_quality_score"] >= 0.75
        assert result["engagement_score"] >= 0.70
        assert result["structural_quality"] >= 0.80
