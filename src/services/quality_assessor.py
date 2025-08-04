"""
Educational Quality Assessor for La Factoria
Assess educational content quality using learning science principles
Following patterns from educational-content-assessment.md
"""

import logging
from typing import Dict, Any, Optional, List
import asyncio
import re

from ..models.educational import LearningObjective
from ..core.config import settings

logger = logging.getLogger(__name__)

class EducationalQualityAssessor:
    """Assess educational content quality using learning science metrics"""

    def __init__(self):
        self.min_quality_threshold = settings.QUALITY_THRESHOLD_OVERALL
        self.min_educational_threshold = settings.QUALITY_THRESHOLD_EDUCATIONAL
        self.min_factual_threshold = settings.QUALITY_THRESHOLD_FACTUAL

    async def assess_content_quality(
        self,
        content: Dict[str, Any],
        content_type: str,
        age_group: str,
        learning_objectives: Optional[List[LearningObjective]] = None
    ) -> Dict[str, Any]:
        """Comprehensive educational quality assessment"""

        try:
            # Extract text content for analysis
            content_text = self._extract_text_content(content)

            if not content_text:
                logger.warning("No text content found for quality assessment")
                return self._default_quality_metrics()

            # Parallel assessment of different quality dimensions
            assessments = await asyncio.gather(
                self._assess_cognitive_load(content_text, age_group),
                self._assess_readability(content_text, age_group),
                self._assess_educational_effectiveness(content, content_type),
                self._assess_learning_objective_alignment(content, learning_objectives),
                self._assess_engagement_elements(content_text),
                self._assess_structural_quality(content_text, content_type),
                return_exceptions=True
            )

            # Handle any exceptions in assessments
            cognitive_load = assessments[0] if not isinstance(assessments[0], Exception) else {}
            readability = assessments[1] if not isinstance(assessments[1], Exception) else {}
            effectiveness = assessments[2] if not isinstance(assessments[2], Exception) else 0.5
            alignment = assessments[3] if not isinstance(assessments[3], Exception) else 0.5
            engagement = assessments[4] if not isinstance(assessments[4], Exception) else 0.5
            structural = assessments[5] if not isinstance(assessments[5], Exception) else 0.5

            # Calculate overall quality score
            quality_score = self._calculate_overall_quality(
                cognitive_load, readability, effectiveness, alignment, engagement, structural
            )

            return {
                "overall_quality_score": quality_score,
                "cognitive_load_metrics": cognitive_load,
                "readability_score": readability,
                "educational_effectiveness": effectiveness,
                "learning_objective_alignment": alignment,
                "engagement_score": engagement,
                "structural_quality": structural,
                "meets_quality_threshold": quality_score >= self.min_quality_threshold,
                "meets_educational_threshold": effectiveness >= self.min_educational_threshold,
                "meets_factual_threshold": True,  # Placeholder for factual accuracy
                "assessment_metadata": {
                    "content_type": content_type,
                    "age_group": age_group,
                    "text_length": len(content_text),
                    "has_learning_objectives": learning_objectives is not None,
                    "assessment_version": "1.0"
                }
            }

        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return self._default_quality_metrics()

    def _extract_text_content(self, content: Dict[str, Any]) -> str:
        """Extract all text content from structured content for analysis"""
        text_parts = []

        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in ['content', 'text', 'description', 'answer', 'question', 'title']:
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
        return ' '.join(text_parts)

    async def _assess_cognitive_load(self, text: str, age_group: str) -> Dict[str, float]:
        """Assess cognitive load using educational psychology principles"""

        # Intrinsic load: content complexity
        intrinsic_load = self._calculate_intrinsic_load(text, age_group)

        # Extraneous load: presentation complexity
        extraneous_load = self._calculate_extraneous_load(text)

        # Germane load: learning effort required
        germane_load = self._calculate_germane_load(text, age_group)

        # Total cognitive load (weighted average)
        total_load = (intrinsic_load * 0.4) + (extraneous_load * 0.3) + (germane_load * 0.3)

        return {
            "intrinsic_load": round(intrinsic_load, 2),
            "extraneous_load": round(extraneous_load, 2),
            "germane_load": round(germane_load, 2),
            "total_cognitive_load": round(total_load, 2),
            "appropriate_for_age": total_load <= self._get_cognitive_load_threshold(age_group)
        }

    def _calculate_intrinsic_load(self, text: str, age_group: str) -> float:
        """Calculate intrinsic cognitive load based on content complexity"""

        # Word complexity analysis
        words = text.split()
        if not words:
            return 0.0

        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Complex words (>6 characters)
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_word_ratio = complex_words / len(words)

        # Technical terms (basic heuristic)
        technical_indicators = ['algorithm', 'function', 'variable', 'equation', 'theorem', 'hypothesis']
        technical_count = sum(1 for indicator in technical_indicators if indicator.lower() in text.lower())
        technical_density = technical_count / len(words) * 1000  # per 1000 words

        # Calculate intrinsic load (0-1 scale)
        load = (
            (avg_word_length - 4) / 6 * 0.3 +  # Word length factor
            complex_word_ratio * 0.4 +         # Complex word factor
            min(technical_density / 10, 1) * 0.3  # Technical density factor
        )

        return max(0.0, min(1.0, load))

    def _calculate_extraneous_load(self, text: str) -> float:
        """Calculate extraneous cognitive load from presentation"""

        # Sentence length analysis
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return 0.0

        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # Very long sentences increase extraneous load
        long_sentence_penalty = max(0, (avg_sentence_length - 20) / 30)

        # Lack of structure (few paragraph breaks)
        paragraph_breaks = text.count('\n\n')
        text_length = len(text.split())
        structure_score = min(1.0, paragraph_breaks / (text_length / 100)) if text_length > 0 else 0

        # Calculate extraneous load
        load = (
            long_sentence_penalty * 0.6 +      # Long sentence penalty
            (1 - structure_score) * 0.4        # Poor structure penalty
        )

        return max(0.0, min(1.0, load))

    def _calculate_germane_load(self, text: str, age_group: str) -> float:
        """Calculate germane cognitive load (learning effort)"""

        # Learning indicators
        learning_indicators = [
            'understand', 'learn', 'remember', 'apply', 'analyze', 'evaluate', 'create',
            'example', 'practice', 'exercise', 'question', 'problem'
        ]

        learning_density = sum(
            1 for indicator in learning_indicators
            if indicator.lower() in text.lower()
        ) / max(1, len(text.split())) * 1000  # per 1000 words

        # Interactive elements
        interactive_indicators = ['try', 'practice', 'exercise', 'activity', 'question']
        interactive_density = sum(
            1 for indicator in interactive_indicators
            if indicator.lower() in text.lower()
        ) / max(1, len(text.split())) * 1000

        # Calculate germane load (appropriate learning effort)
        load = (
            min(learning_density / 20, 1) * 0.6 +     # Learning content density
            min(interactive_density / 10, 1) * 0.4    # Interactive elements
        )

        return max(0.0, min(1.0, load))

    def _get_cognitive_load_threshold(self, age_group: str) -> float:
        """Get appropriate cognitive load threshold for age group"""
        thresholds = {
            "elementary": 1.5,
            "middle_school": 2.0,
            "high_school": 2.5,
            "college": 3.0,
            "adult_learning": 2.8,
            "general": 2.3
        }
        return thresholds.get(age_group.lower(), 2.3)

    async def _assess_readability(self, text: str, age_group: str) -> Dict[str, float]:
        """Assess readability using multiple metrics"""

        if not text:
            return {"age_appropriateness_score": 0.0}

        # Basic readability metrics (simplified implementation)
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]

        if not words or not sentences:
            return {"age_appropriateness_score": 0.5}

        # Simple metrics
        avg_words_per_sentence = len(words) / len(sentences)
        avg_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words)

        # Flesch Reading Ease approximation
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp to 0-100

        # Age appropriateness thresholds
        age_thresholds = {
            "elementary": 80,     # Very easy
            "middle_school": 70,  # Fairly easy
            "high_school": 60,    # Standard
            "college": 50,        # Fairly difficult
            "adult_learning": 55,
            "general": 60
        }

        threshold = age_thresholds.get(age_group.lower(), 60)
        appropriateness_score = min(1.0, flesch_score / threshold)

        return {
            "flesch_reading_ease": round(flesch_score, 1),
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "avg_syllables_per_word": round(avg_syllables_per_word, 1),
            "age_appropriateness_score": round(appropriateness_score, 2)
        }

    def _count_syllables(self, word: str) -> int:
        """Simple syllable counting heuristic"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel

        # Handle silent e
        if word.endswith('e'):
            count -= 1

        return max(1, count)  # Every word has at least 1 syllable

    async def _assess_educational_effectiveness(self, content: Dict[str, Any], content_type: str) -> float:
        """Assess educational effectiveness based on pedagogical principles"""

        effectiveness_score = 0.0

        # Content structure assessment
        if isinstance(content, dict):
            # Check for educational elements
            if 'learning_objectives' in content or 'objectives' in content:
                effectiveness_score += 0.2

            if 'examples' in content or any('example' in str(v).lower() for v in content.values()):
                effectiveness_score += 0.2

            if 'exercises' in content or 'practice' in content or 'activities' in content:
                effectiveness_score += 0.2

            # Content type specific checks
            if content_type == 'flashcards':
                if 'cards' in content or 'flashcards' in content:
                    effectiveness_score += 0.2
            elif content_type == 'study_guide':
                if 'sections' in content or 'chapters' in content:
                    effectiveness_score += 0.2
            elif content_type == 'faq_collection':
                if 'faqs' in content or 'questions' in content:
                    effectiveness_score += 0.2

        # Text content analysis
        text_content = self._extract_text_content(content)
        if text_content:
            educational_indicators = [
                'learn', 'understand', 'remember', 'apply', 'practice',
                'example', 'exercise', 'question', 'concept', 'skill'
            ]

            indicator_count = sum(
                1 for indicator in educational_indicators
                if indicator.lower() in text_content.lower()
            )

            # Normalize based on text length
            words = text_content.split()
            if words:
                indicator_density = indicator_count / len(words) * 100
                effectiveness_score += min(0.4, indicator_density / 5)  # Up to 0.4 points

        return max(0.0, min(1.0, effectiveness_score))

    async def _assess_learning_objective_alignment(
        self,
        content: Dict[str, Any],
        learning_objectives: Optional[List[LearningObjective]]
    ) -> float:
        """Assess alignment with specified learning objectives"""

        if not learning_objectives:
            return 0.7  # Default score when no objectives specified

        text_content = self._extract_text_content(content)
        if not text_content:
            return 0.0

        alignment_scores = []

        for objective in learning_objectives:
            # Check for objective-related terms in content
            objective_terms = [
                objective.subject_area.lower(),
                objective.specific_skill.lower(),
                objective.cognitive_level.value.lower() if hasattr(objective.cognitive_level, 'value') else str(objective.cognitive_level).lower()
            ]

            alignment_score = 0.0
            for term in objective_terms:
                if term in text_content.lower():
                    alignment_score += 0.33

            alignment_scores.append(min(1.0, alignment_score))

        return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0

    async def _assess_engagement_elements(self, text: str) -> float:
        """Assess presence of engaging elements"""

        if not text:
            return 0.0

        engagement_indicators = {
            'questions': r'\?',
            'examples': r'\bexample\b|\bfor instance\b',
            'activities': r'\bactivity\b|\bexercise\b|\bpractice\b',
            'real_world': r'\bin real life\b|\bin practice\b|\bin the world\b',
            'interactive': r'\btry\b|\byou can\b|\blet\'s\b'
        }

        engagement_score = 0.0

        for indicator_type, pattern in engagement_indicators.items():
            if re.search(pattern, text, re.IGNORECASE):
                engagement_score += 0.2

        return min(1.0, engagement_score)

    async def _assess_structural_quality(self, text: str, content_type: str) -> float:
        """Assess structural quality and organization"""

        if not text:
            return 0.0

        structure_score = 0.0

        # Check for headings/sections
        if re.search(r'^#{1,3}\s', text, re.MULTILINE):
            structure_score += 0.3

        # Check for lists or bullet points
        if re.search(r'^\s*[-*•]\s', text, re.MULTILINE) or re.search(r'^\s*\d+\.\s', text, re.MULTILINE):
            structure_score += 0.2

        # Check for paragraph breaks
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            structure_score += 0.2

        # Content type specific structure
        if content_type == 'flashcards':
            if 'question' in text.lower() and 'answer' in text.lower():
                structure_score += 0.3
        elif content_type == 'study_guide':
            if len(paragraphs) >= 3:  # Multiple sections expected
                structure_score += 0.3

        return min(1.0, structure_score)

    def _calculate_overall_quality(
        self,
        cognitive_load: Dict[str, Any],
        readability: Dict[str, Any],
        effectiveness: float,
        alignment: float,
        engagement: float,
        structural: float
    ) -> float:
        """Calculate weighted overall quality score"""

        # Extract key metrics
        cognitive_appropriate = cognitive_load.get('appropriate_for_age', True)
        readability_score = readability.get('age_appropriateness_score', 0.5)

        # Weight the different components
        weights = {
            'cognitive_load': 0.15,
            'readability': 0.20,
            'educational_effectiveness': 0.30,
            'learning_alignment': 0.15,
            'engagement': 0.10,
            'structural_quality': 0.10
        }

        # Calculate weighted score
        overall_score = (
            (1.0 if cognitive_appropriate else 0.5) * weights['cognitive_load'] +
            readability_score * weights['readability'] +
            effectiveness * weights['educational_effectiveness'] +
            alignment * weights['learning_alignment'] +
            engagement * weights['engagement'] +
            structural * weights['structural_quality']
        )

        return round(overall_score, 3)

    def _default_quality_metrics(self) -> Dict[str, Any]:
        """Return default quality metrics when assessment fails"""
        return {
            "overall_quality_score": 0.5,
            "cognitive_load_metrics": {},
            "readability_score": {},
            "educational_effectiveness": 0.5,
            "learning_objective_alignment": 0.5,
            "engagement_score": 0.5,
            "structural_quality": 0.5,
            "meets_quality_threshold": False,
            "meets_educational_threshold": False,
            "meets_factual_threshold": False,
            "assessment_metadata": {
                "error": "Assessment failed - using default values"
            }
        }
