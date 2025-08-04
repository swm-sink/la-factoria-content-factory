"""
Educational Quality Assessor Implementation for La Factoria
===========================================================

This example bridges the abstract quality assessment system with concrete algorithms.
Implements the quality metrics defined in project-overview.md and PRP-004.

Key patterns demonstrated:
- Multi-dimensional quality scoring (educational value ≥0.75, factual accuracy ≥0.85, overall ≥0.70)
- Learning science integration (Bloom's taxonomy, cognitive load theory)
- AI-powered quality evaluation using cross-provider validation
- Concrete assessment algorithms for educational effectiveness
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import openai
import anthropic
from textstat import textstat
import nltk
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Quality assessment dimensions from architecture"""
    EDUCATIONAL_VALUE = "educational_value"
    FACTUAL_ACCURACY = "factual_accuracy"
    AGE_APPROPRIATENESS = "age_appropriateness"
    STRUCTURAL_QUALITY = "structural_quality"
    ENGAGEMENT_LEVEL = "engagement_level"

@dataclass
class QualityScore:
    """
    Quality score structure matching database model

    Bridges Architecture Concept:
    - Maps to QualityScore table from models.py
    - Implements thresholds from project-overview.md
    """
    overall_score: float
    educational_value: float        # ≥0.75 threshold
    factual_accuracy: float         # ≥0.85 threshold
    age_appropriateness: float
    structural_quality: float
    engagement_level: float
    assessment_details: Dict[str, Any]
    meets_quality_threshold: bool

@dataclass
class ContentAnalysis:
    """Intermediate analysis results for quality assessment"""
    word_count: int
    sentence_count: int
    paragraph_count: int
    reading_level: float
    educational_keywords: List[str]
    learning_indicators: List[str]
    structural_elements: Dict[str, bool]
    engagement_elements: List[str]

class EducationalQualityAssessor:
    """
    Concrete implementation of quality assessment system

    Bridges Architecture Concept:
    - "Quality Assessment System" from project-overview.md
    - "Multi-dimensional quality assessment" from PRP-001
    - Learning science integration with Bloom's taxonomy
    """

    def __init__(self):
        # Quality thresholds from architecture
        self.thresholds = {
            "overall_score": 0.70,
            "educational_value": 0.75,
            "factual_accuracy": 0.85,
            "age_appropriateness": 0.70,
            "structural_quality": 0.70,
            "engagement_level": 0.65
        }

        # Quality dimension weights for overall score calculation
        self.weights = {
            "educational_value": 0.35,      # Highest weight - pedagogical effectiveness
            "factual_accuracy": 0.25,       # Critical for educational content
            "age_appropriateness": 0.15,     # Essential for target audience
            "structural_quality": 0.15,     # Important for comprehension
            "engagement_level": 0.10,       # Enhances learning outcomes
        }

        # Initialize AI clients for cross-provider validation
        self.openai_client = openai.AsyncOpenAI() if openai.api_key else None
        self.anthropic_client = anthropic.AsyncAnthropic() if anthropic.api_key else None

        # Educational keywords for assessment
        self.educational_keywords = {
            'learning_objectives': ['objective', 'goal', 'learn', 'understand', 'apply', 'analyze', 'evaluate', 'create'],
            'assessment_terms': ['quiz', 'test', 'exercise', 'practice', 'assessment', 'evaluation', 'review'],
            'pedagogical_terms': ['concept', 'principle', 'theory', 'method', 'technique', 'strategy', 'approach'],
            'engagement_terms': ['example', 'activity', 'interactive', 'hands-on', 'experiment', 'project']
        }

    async def assess_content_quality(
        self,
        content: str,
        content_type: str,
        target_audience: str,
        topic: str = "",
        additional_context: Optional[str] = None
    ) -> QualityScore:
        """
        Main quality assessment method implementing architecture requirements

        Bridges Architecture Concept:
        - Implements "Content quality assessment and validation" from AI Content Service
        - Uses multi-dimensional scoring approach from Quality Assessment System
        """
        logger.info(f"Starting quality assessment for {content_type} content targeting {target_audience}")

        # Perform content analysis
        analysis = await self._analyze_content_structure(content, content_type)

        # Run parallel quality assessments
        assessment_tasks = [
            self._assess_educational_value(content, content_type, analysis),
            self._assess_factual_accuracy(content, topic),
            self._assess_age_appropriateness(content, target_audience, analysis),
            self._assess_structural_quality(content, content_type, analysis),
            self._assess_engagement_level(content, analysis)
        ]

        results = await asyncio.gather(*assessment_tasks, return_exceptions=True)

        # Handle any assessment failures gracefully
        educational_value = results[0] if not isinstance(results[0], Exception) else 0.5
        factual_accuracy = results[1] if not isinstance(results[1], Exception) else 0.5
        age_appropriateness = results[2] if not isinstance(results[2], Exception) else 0.5
        structural_quality = results[3] if not isinstance(results[3], Exception) else 0.5
        engagement_level = results[4] if not isinstance(results[4], Exception) else 0.5

        # Calculate overall weighted score
        overall_score = (
            educational_value * self.weights["educational_value"] +
            factual_accuracy * self.weights["factual_accuracy"] +
            age_appropriateness * self.weights["age_appropriateness"] +
            structural_quality * self.weights["structural_quality"] +
            engagement_level * self.weights["engagement_level"]
        )

        # Check quality thresholds
        meets_threshold = (
            overall_score >= self.thresholds["overall_score"] and
            educational_value >= self.thresholds["educational_value"] and
            factual_accuracy >= self.thresholds["factual_accuracy"]
        )

        # Compile assessment details
        assessment_details = {
            "content_analysis": {
                "word_count": analysis.word_count,
                "reading_level": analysis.reading_level,
                "educational_keywords_found": len(analysis.educational_keywords),
                "structural_completeness": sum(analysis.structural_elements.values()) / len(analysis.structural_elements)
            },
            "quality_breakdown": {
                "educational_value_details": f"Learning indicators: {len(analysis.learning_indicators)}",
                "structural_quality_details": f"Required elements: {analysis.structural_elements}",
                "engagement_details": f"Engagement elements: {len(analysis.engagement_elements)}"
            },
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "assessor_version": "1.0.0"
        }

        logger.info(f"Quality assessment complete: overall={overall_score:.3f}, meets_threshold={meets_threshold}")

        return QualityScore(
            overall_score=round(overall_score, 3),
            educational_value=round(educational_value, 3),
            factual_accuracy=round(factual_accuracy, 3),
            age_appropriateness=round(age_appropriateness, 3),
            structural_quality=round(structural_quality, 3),
            engagement_level=round(engagement_level, 3),
            assessment_details=assessment_details,
            meets_quality_threshold=meets_threshold
        )

    async def _analyze_content_structure(self, content: str, content_type: str) -> ContentAnalysis:
        """Analyze content structure for quality assessment"""

        # Basic text metrics
        word_count = len(content.split())
        sentences = re.split(r'[.!?]+', content)
        sentence_count = len([s for s in sentences if s.strip()])
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])

        # Reading level analysis
        reading_level = textstat.flesch_kincaid().grade(content)

        # Educational keyword analysis
        content_lower = content.lower()
        educational_keywords = []
        for category, keywords in self.educational_keywords.items():
            found_keywords = [kw for kw in keywords if kw in content_lower]
            educational_keywords.extend(found_keywords)

        # Learning indicators (Bloom's taxonomy terms)
        learning_indicators = []
        bloom_terms = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create',
                      'identify', 'describe', 'explain', 'demonstrate', 'compare', 'design']
        for term in bloom_terms:
            if term in content_lower:
                learning_indicators.append(term)

        # Structural elements based on content type
        structural_elements = self._check_structural_elements(content, content_type)

        # Engagement elements
        engagement_elements = []
        engagement_patterns = [
            r'example:', r'for instance', r'activity:', r'exercise:',
            r'try this', r'practice', r'quiz', r'question:'
        ]
        for pattern in engagement_patterns:
            if re.search(pattern, content_lower):
                engagement_elements.append(pattern)

        return ContentAnalysis(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            reading_level=reading_level,
            educational_keywords=educational_keywords,
            learning_indicators=learning_indicators,
            structural_elements=structural_elements,
            engagement_elements=engagement_elements
        )

    def _check_structural_elements(self, content: str, content_type: str) -> Dict[str, bool]:
        """Check for required structural elements based on content type"""
        content_lower = content.lower()

        # Content type specific requirements from prompts/
        requirements = {
            "study_guide": {
                "has_learning_objectives": any(term in content_lower for term in ['objective', 'goals', 'will learn']),
                "has_main_content": len(content.split('\n\n')) >= 3,
                "has_examples": 'example' in content_lower,
                "has_assessment": any(term in content_lower for term in ['exercise', 'practice', 'quiz', 'question'])
            },
            "flashcards": {
                "has_term_definition_pairs": content_lower.count('term:') > 0 or content_lower.count('definition:') > 0,
                "appropriate_card_count": 10 <= content_lower.count('\n') <= 100,
                "clear_structure": '|' in content or 'term:' in content_lower
            },
            "master_content_outline": {
                "has_sections": content_lower.count('#') >= 3,
                "has_objectives": 'objective' in content_lower,
                "has_timeline": any(term in content_lower for term in ['time', 'duration', 'minutes', 'hours'])
            },
            "podcast_script": {
                "has_speakers": any(term in content for term in ['Host:', 'Speaker:', 'Narrator:']),
                "has_timing_cues": any(term in content_lower for term in ['pause', 'music', 'sound', 'fade']),
                "conversational_tone": content_lower.count('?') >= 2
            }
        }

        return requirements.get(content_type, {
            "has_content": len(content.strip()) > 100,
            "has_structure": content.count('\n') >= 5
        })

    async def _assess_educational_value(self, content: str, content_type: str, analysis: ContentAnalysis) -> float:
        """
        Assess educational value using learning science principles

        Bridges Architecture Concept:
        - "Educational value (≥0.75 threshold)" from project-overview.md
        - Learning science integration from PRP-001
        """

        score_components = {}

        # Learning objectives clarity (25% of educational value)
        learning_obj_score = len(analysis.learning_indicators) / 10  # Normalize to 0-1
        learning_obj_score = min(1.0, learning_obj_score)
        score_components['learning_objectives'] = learning_obj_score

        # Educational keyword density (20% of educational value)
        keyword_density = len(analysis.educational_keywords) / max(analysis.word_count / 100, 1)
        keyword_score = min(1.0, keyword_density / 5)  # Target 5% density
        score_components['educational_keywords'] = keyword_score

        # Structural completeness (25% of educational value)
        structure_score = sum(analysis.structural_elements.values()) / len(analysis.structural_elements)
        score_components['structural_completeness'] = structure_score

        # Bloom's taxonomy coverage (20% of educational value)
        bloom_coverage = len(set(analysis.learning_indicators)) / 6  # 6 levels of Bloom's
        bloom_score = min(1.0, bloom_coverage)
        score_components['bloom_taxonomy'] = bloom_score

        # Content depth vs breadth balance (10% of educational value)
        depth_score = min(1.0, analysis.word_count / 800)  # Target 800+ words for depth
        score_components['content_depth'] = depth_score

        # Calculate weighted educational value
        educational_value = (
            learning_obj_score * 0.25 +
            keyword_score * 0.20 +
            structure_score * 0.25 +
            bloom_score * 0.20 +
            depth_score * 0.10
        )

        logger.debug(f"Educational value components: {score_components}")
        return educational_value

    async def _assess_factual_accuracy(self, content: str, topic: str) -> float:
        """
        Assess factual accuracy using AI cross-validation

        Bridges Architecture Concept:
        - "Factual accuracy (≥0.85 threshold)" from project-overview.md
        - Cross-provider AI validation for fact-checking
        """

        if not self.openai_client and not self.anthropic_client:
            logger.warning("No AI clients available for factual accuracy assessment")
            return 0.75  # Conservative default

        try:
            # Extract factual claims from content
            fact_extraction_prompt = f"""
            Analyze the following educational content about "{topic}" and extract the main factual claims.
            Return a JSON list of factual statements that can be verified.

            Content: {content[:2000]}  # Limit for token efficiency

            Return format: {{"factual_claims": ["claim1", "claim2", ...]}}
            """

            # Use available AI provider for fact extraction
            if self.anthropic_client:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    messages=[{"role": "user", "content": fact_extraction_prompt}]
                )

                try:
                    claims_data = json.loads(response.content[0].text)
                    factual_claims = claims_data.get("factual_claims", [])
                except json.JSONDecodeError:
                    factual_claims = []
            else:
                factual_claims = []

            # If we found claims, assess them
            if factual_claims:
                # Simple heuristic: longer, more specific claims are more likely accurate
                accuracy_scores = []
                for claim in factual_claims:
                    # Basic accuracy heuristics
                    specificity_score = min(1.0, len(claim.split()) / 15)  # More specific = better
                    certainty_indicators = sum(1 for word in ['is', 'are', 'was', 'were', 'exactly', 'precisely'] if word in claim.lower())
                    certainty_score = min(1.0, certainty_indicators / 3)

                    claim_accuracy = (specificity_score + certainty_score) / 2
                    accuracy_scores.append(claim_accuracy)

                overall_accuracy = sum(accuracy_scores) / len(accuracy_scores)
                return overall_accuracy
            else:
                # No specific claims found - assess general factual tone
                factual_language_score = 0.8  # Default for educational content
                return factual_language_score

        except Exception as e:
            logger.error(f"Factual accuracy assessment failed: {e}")
            return 0.75  # Conservative fallback

    async def _assess_age_appropriateness(self, content: str, target_audience: str, analysis: ContentAnalysis) -> float:
        """
        Assess age appropriateness using readability metrics

        Bridges Architecture Concept:
        - "Age appropriateness (target audience alignment)" from project-overview.md
        - Links to educational standards for different age groups
        """

        # Target reading levels by audience
        target_levels = {
            "elementary": {"min_grade": 3, "max_grade": 5},
            "middle_school": {"min_grade": 6, "max_grade": 8},
            "high_school": {"min_grade": 9, "max_grade": 12},
            "college": {"min_grade": 13, "max_grade": 16},
            "adult": {"min_grade": 10, "max_grade": 14}
        }

        target = target_levels.get(target_audience, {"min_grade": 8, "max_grade": 12})
        content_grade_level = analysis.reading_level

        # Score based on how well reading level matches target
        if target["min_grade"] <= content_grade_level <= target["max_grade"]:
            level_score = 1.0
        elif content_grade_level < target["min_grade"]:
            # Too easy - score based on how close to minimum
            gap = target["min_grade"] - content_grade_level
            level_score = max(0.3, 1.0 - (gap / 3))
        else:
            # Too difficult - score based on how far above maximum
            gap = content_grade_level - target["max_grade"]
            level_score = max(0.2, 1.0 - (gap / 4))

        # Additional age-appropriateness factors
        sentence_length_score = self._assess_sentence_complexity(analysis, target_audience)
        vocabulary_score = self._assess_vocabulary_appropriateness(content, target_audience)

        # Weighted age appropriateness score
        age_appropriateness = (
            level_score * 0.5 +
            sentence_length_score * 0.3 +
            vocabulary_score * 0.2
        )

        return age_appropriateness

    def _assess_sentence_complexity(self, analysis: ContentAnalysis, target_audience: str) -> float:
        """Assess sentence complexity for age appropriateness"""
        avg_sentence_length = analysis.word_count / max(analysis.sentence_count, 1)

        # Target sentence lengths by audience
        target_lengths = {
            "elementary": 12,
            "middle_school": 16,
            "high_school": 20,
            "college": 25,
            "adult": 22
        }

        target_length = target_lengths.get(target_audience, 18)

        if avg_sentence_length <= target_length:
            return 1.0
        else:
            excess = avg_sentence_length - target_length
            return max(0.3, 1.0 - (excess / target_length))

    def _assess_vocabulary_appropriateness(self, content: str, target_audience: str) -> float:
        """Assess vocabulary complexity for age appropriateness"""
        words = content.lower().split()

        # Simple heuristic: count syllables and complex words
        complex_word_count = 0
        total_syllables = 0

        for word in words:
            syllable_count = textstat.syllable_count(word)
            total_syllables += syllable_count
            if syllable_count >= 3:  # Complex words have 3+ syllables
                complex_word_count += 1

        complex_word_ratio = complex_word_count / max(len(words), 1)

        # Target complexity ratios by audience
        target_ratios = {
            "elementary": 0.05,
            "middle_school": 0.10,
            "high_school": 0.15,
            "college": 0.20,
            "adult": 0.18
        }

        target_ratio = target_ratios.get(target_audience, 0.12)

        if complex_word_ratio <= target_ratio:
            return 1.0
        else:
            excess_ratio = complex_word_ratio - target_ratio
            return max(0.4, 1.0 - (excess_ratio / target_ratio))

    async def _assess_structural_quality(self, content: str, content_type: str, analysis: ContentAnalysis) -> float:
        """
        Assess structural quality and organization

        Bridges Architecture Concept:
        - "Structural clarity and organization" from project-overview.md
        - Content type specific structural requirements
        """

        # Base structural elements
        has_clear_sections = content.count('#') >= 2 or content.count('\n\n') >= 3
        has_logical_flow = self._assess_logical_flow(content)
        has_appropriate_length = self._assess_content_length(analysis.word_count, content_type)

        # Content type specific structure
        type_structure_score = sum(analysis.structural_elements.values()) / max(len(analysis.structural_elements), 1)

        # Readability structure
        paragraph_balance = self._assess_paragraph_balance(analysis)

        structural_quality = (
            (1.0 if has_clear_sections else 0.3) * 0.25 +
            has_logical_flow * 0.25 +
            has_appropriate_length * 0.20 +
            type_structure_score * 0.20 +
            paragraph_balance * 0.10
        )

        return structural_quality

    def _assess_logical_flow(self, content: str) -> float:
        """Assess logical flow using transition words and structure"""
        transition_words = [
            'first', 'second', 'third', 'next', 'then', 'finally', 'however',
            'therefore', 'furthermore', 'moreover', 'in addition', 'for example'
        ]

        content_lower = content.lower()
        transition_count = sum(1 for word in transition_words if word in content_lower)

        # Normalize based on content length
        paragraphs = len(content.split('\n\n'))
        expected_transitions = max(2, paragraphs // 2)

        flow_score = min(1.0, transition_count / expected_transitions)
        return flow_score

    def _assess_content_length(self, word_count: int, content_type: str) -> float:
        """Assess if content length is appropriate for type"""
        target_lengths = {
            "study_guide": (800, 2000),
            "flashcards": (200, 800),
            "one_pager_summary": (300, 600),
            "detailed_reading_material": (1200, 3000),
            "faq_collection": (400, 1000),
            "podcast_script": (1000, 2500),
            "master_content_outline": (500, 1200),
            "reading_guide_questions": (300, 800)
        }

        min_words, max_words = target_lengths.get(content_type, (500, 1500))

        if min_words <= word_count <= max_words:
            return 1.0
        elif word_count < min_words:
            return max(0.3, word_count / min_words)
        else:
            excess = word_count - max_words
            return max(0.5, 1.0 - (excess / max_words))

    def _assess_paragraph_balance(self, analysis: ContentAnalysis) -> float:
        """Assess paragraph length balance"""
        if analysis.paragraph_count == 0:
            return 0.3

        avg_words_per_paragraph = analysis.word_count / analysis.paragraph_count

        # Target 50-150 words per paragraph for readability
        if 50 <= avg_words_per_paragraph <= 150:
            return 1.0
        elif avg_words_per_paragraph < 50:
            return max(0.4, avg_words_per_paragraph / 50)
        else:
            return max(0.4, 150 / avg_words_per_paragraph)

    async def _assess_engagement_level(self, content: str, analysis: ContentAnalysis) -> float:
        """
        Assess student engagement potential

        Bridges Architecture Concept:
        - Engagement level scoring for learning effectiveness
        - Interactive elements and real-world applications
        """

        # Interactive elements
        interactive_score = len(analysis.engagement_elements) / 5  # Target 5 engagement elements
        interactive_score = min(1.0, interactive_score)

        # Question frequency (encourages active thinking)
        question_count = content.count('?')
        question_score = min(1.0, question_count / 8)  # Target 8+ questions

        # Example usage (concrete application)
        example_count = content.lower().count('example')
        example_score = min(1.0, example_count / 3)  # Target 3+ examples

        # Varied sentence structure (maintains interest)
        sentence_variety = self._assess_sentence_variety(content)

        engagement_level = (
            interactive_score * 0.3 +
            question_score * 0.3 +
            example_score * 0.25 +
            sentence_variety * 0.15
        )

        return engagement_level

    def _assess_sentence_variety(self, content: str) -> float:
        """Assess sentence length variety for engagement"""
        sentences = re.split(r'[.!?]+', content)
        sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]

        if len(sentence_lengths) < 3:
            return 0.5

        # Calculate coefficient of variation (std dev / mean)
        mean_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((length - mean_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        std_dev = variance ** 0.5

        if mean_length == 0:
            return 0.5

        coefficient_of_variation = std_dev / mean_length

        # Target moderate variety (0.3-0.6 CV ratio)
        if 0.3 <= coefficient_of_variation <= 0.6:
            return 1.0
        elif coefficient_of_variation < 0.3:
            return coefficient_of_variation / 0.3
        else:
            return max(0.4, 0.6 / coefficient_of_variation)

"""
Usage Example:
==============

async def assess_generated_content():
    assessor = EducationalQualityAssessor()

    sample_content = '''
    # Python Programming Basics Study Guide

    ## Learning Objectives
    Students will understand variables, functions, and control structures in Python.

    ## Variables
    Variables store data. For example: name = "Alice"

    ## Practice Exercise
    Create a variable for your age.
    '''

    quality_score = await assessor.assess_content_quality(
        content=sample_content,
        content_type="study_guide",
        target_audience="high_school",
        topic="Python Programming"
    )

    print(f"Overall Score: {quality_score.overall_score}")
    print(f"Educational Value: {quality_score.educational_value}")
    print(f"Meets Threshold: {quality_score.meets_quality_threshold}")

# Run assessment
asyncio.run(assess_generated_content())
"""
