# Educational Content Assessment and Learning Science Context

## Learning Science Principles (2024-2025)

### 1. Cognitive Science Foundations
```python
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class LearningLevel(Enum):
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    COLLEGE = "college"

class ContentType(Enum):
    STUDY_GUIDE = "study_guide"
    FLASHCARDS = "flashcards"
    QUIZ = "quiz"
    PODCAST = "podcast"
    INTERACTIVE = "interactive"

@dataclass
class LearningObjective:
    """Structured learning objective based on Bloom's Taxonomy."""
    cognitive_level: str  # remember, understand, apply, analyze, evaluate, create
    subject_area: str
    specific_skill: str
    measurable_outcome: str
    difficulty_level: int  # 1-10 scale

@dataclass
class CognitiveLoadMetrics:
    """Cognitive load assessment metrics."""
    intrinsic_load: float  # Content complexity (0-1)
    extraneous_load: float  # Presentation complexity (0-1)
    germane_load: float  # Learning effort required (0-1)
    total_cognitive_load: float
    
    @classmethod
    def calculate(cls, content_complexity: float, presentation_clarity: float, prior_knowledge: float) -> 'CognitiveLoadMetrics':
        intrinsic = content_complexity
        extraneous = 1.0 - presentation_clarity
        germane = max(0, 1.0 - prior_knowledge) * content_complexity
        total = intrinsic + extraneous + germane
        
        return cls(
            intrinsic_load=intrinsic,
            extraneous_load=extraneous,
            germane_load=germane,
            total_cognitive_load=min(total, 3.0)  # Cap at maximum
        )

class EducationalStandardsFramework:
    """Educational standards and assessment framework."""
    
    def __init__(self):
        self.bloom_taxonomy = {
            "remember": {
                "keywords": ["define", "list", "recall", "identify", "name", "state"],
                "cognitive_level": 1,
                "assessment_types": ["multiple_choice", "matching", "true_false"]
            },
            "understand": {
                "keywords": ["explain", "describe", "summarize", "interpret", "compare"],
                "cognitive_level": 2,
                "assessment_types": ["short_answer", "explanation", "examples"]
            },
            "apply": {
                "keywords": ["solve", "use", "demonstrate", "calculate", "implement"],
                "cognitive_level": 3,
                "assessment_types": ["problem_solving", "case_studies", "simulations"]
            },
            "analyze": {
                "keywords": ["analyze", "break down", "examine", "categorize", "differentiate"],
                "cognitive_level": 4,
                "assessment_types": ["critical_thinking", "case_analysis", "comparison"]
            },
            "evaluate": {
                "keywords": ["judge", "critique", "assess", "justify", "argue"],
                "cognitive_level": 5,
                "assessment_types": ["evaluation", "critique", "recommendation"]
            },
            "create": {
                "keywords": ["design", "create", "develop", "compose", "plan"],
                "cognitive_level": 6,
                "assessment_types": ["project", "design", "original_work"]
            }
        }
        
        self.learning_styles = {
            "visual": {
                "characteristics": ["prefers diagrams", "learns from charts", "needs visual organization"],
                "content_adaptations": ["include_diagrams", "use_color_coding", "structured_layouts"]
            },
            "auditory": {
                "characteristics": ["learns from listening", "benefits from discussions", "remembers spoken information"],
                "content_adaptations": ["audio_content", "rhythmic_patterns", "verbal_explanations"]
            },
            "kinesthetic": {
                "characteristics": ["learns by doing", "needs movement", "prefers hands-on activities"],
                "content_adaptations": ["interactive_elements", "practical_examples", "step_by_step_practice"]
            },
            "reading_writing": {
                "characteristics": ["prefers text", "learns from writing", "enjoys reading"],
                "content_adaptations": ["detailed_text", "note_taking_guides", "written_exercises"]
            }
        }
```

## AI-Powered Content Quality Assessment

### 1. Automated Quality Evaluation Framework
```python
import asyncio
from typing import Dict, List, Any, Optional
import re
import statistics
from dataclasses import dataclass

@dataclass
class QualityMetrics:
    """Comprehensive quality assessment metrics."""
    
    # Content Quality (0-1 scale)
    accuracy_score: float
    clarity_score: float
    completeness_score: float
    engagement_score: float
    
    # Educational Effectiveness (0-1 scale)
    learning_objective_alignment: float
    cognitive_level_appropriateness: float
    difficulty_appropriateness: float
    
    # Technical Quality (0-1 scale)
    readability_score: float
    structure_score: float
    language_appropriateness: float
    
    # Overall Assessment
    overall_score: float
    confidence_level: float
    improvement_areas: List[str]
    
    @classmethod
    def calculate_overall(cls, metrics: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        weights = {
            "accuracy_score": 0.25,
            "clarity_score": 0.20,
            "completeness_score": 0.15,
            "engagement_score": 0.15,
            "learning_objective_alignment": 0.15,
            "cognitive_level_appropriateness": 0.05,
            "difficulty_appropriateness": 0.05
        }
        
        return sum(metrics.get(key, 0) * weight for key, weight in weights.items())

class EducationalContentEvaluator:
    """AI-powered educational content quality evaluator."""
    
    def __init__(self, claude_client, evaluation_prompts: Dict[str, str]):
        self.claude_client = claude_client
        self.evaluation_prompts = evaluation_prompts
        self.readability_analyzer = ReadabilityAnalyzer()
        self.structure_analyzer = ContentStructureAnalyzer()
    
    async def evaluate_content_comprehensive(
        self,
        content: str,
        content_type: ContentType,
        audience_level: LearningLevel,
        subject_area: str,
        learning_objectives: List[LearningObjective]
    ) -> QualityMetrics:
        """Comprehensive content evaluation using multiple AI judges."""
        
        # Parallel evaluation tasks
        evaluation_tasks = await asyncio.gather(
            self._evaluate_accuracy(content, subject_area),
            self._evaluate_clarity(content, audience_level),
            self._evaluate_completeness(content, learning_objectives),
            self._evaluate_engagement(content, content_type, audience_level),
            self._evaluate_learning_alignment(content, learning_objectives),
            self._evaluate_cognitive_level(content, audience_level),
            self._evaluate_difficulty(content, audience_level),
            return_exceptions=True
        )
        
        # Process results
        scores = {}
        for i, task_result in enumerate(evaluation_tasks):
            if not isinstance(task_result, Exception):
                scores.update(task_result)
        
        # Technical assessments
        readability = self.readability_analyzer.analyze(content, audience_level)
        structure = self.structure_analyzer.analyze(content, content_type)
        language = await self._evaluate_language_appropriateness(content, audience_level)
        
        scores.update({
            "readability_score": readability.score,
            "structure_score": structure.score,
            "language_appropriateness": language["score"]
        })
        
        # Calculate overall score and confidence
        overall_score = QualityMetrics.calculate_overall(scores)
        confidence_level = self._calculate_confidence(scores)
        improvement_areas = self._identify_improvement_areas(scores)
        
        return QualityMetrics(
            accuracy_score=scores.get("accuracy_score", 0.5),
            clarity_score=scores.get("clarity_score", 0.5),
            completeness_score=scores.get("completeness_score", 0.5),
            engagement_score=scores.get("engagement_score", 0.5),
            learning_objective_alignment=scores.get("learning_objective_alignment", 0.5),
            cognitive_level_appropriateness=scores.get("cognitive_level_appropriateness", 0.5),
            difficulty_appropriateness=scores.get("difficulty_appropriateness", 0.5),
            readability_score=scores.get("readability_score", 0.5),
            structure_score=scores.get("structure_score", 0.5),
            language_appropriateness=scores.get("language_appropriateness", 0.5),
            overall_score=overall_score,
            confidence_level=confidence_level,
            improvement_areas=improvement_areas
        )
    
    async def _evaluate_accuracy(self, content: str, subject_area: str) -> Dict[str, float]:
        """Evaluate content accuracy using AI judge."""
        
        prompt = f"""
        Evaluate the factual accuracy of the following educational content about {subject_area}.
        
        Content:
        {content}
        
        Assessment Criteria:
        1. Are all facts correct and up-to-date?
        2. Are there any misleading or false statements?
        3. Are sources/references credible (if mentioned)?
        4. Is the information consistent throughout?
        
        Provide a score from 0.0 to 1.0 where:
        - 1.0 = Completely accurate, no factual errors
        - 0.8 = Mostly accurate, minor errors that don't affect learning
        - 0.6 = Some errors that could mislead learners
        - 0.4 = Significant errors affecting core concepts
        - 0.2 = Major inaccuracies throughout
        - 0.0 = Mostly or completely inaccurate
        
        Respond with JSON format:
        {{
            "accuracy_score": float,
            "error_count": int,
            "error_examples": [list of specific errors if any],
            "reasoning": "explanation of the score"
        }}
        """
        
        response = await self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            import json
            result = json.loads(response.content[0].text)
            return {"accuracy_score": result["accuracy_score"]}
        except:
            return {"accuracy_score": 0.5}  # Default if parsing fails
    
    async def _evaluate_clarity(self, content: str, audience_level: LearningLevel) -> Dict[str, float]:
        """Evaluate content clarity for target audience."""
        
        prompt = f"""
        Evaluate how clearly this educational content explains concepts for {audience_level.value} students.
        
        Content:
        {content}
        
        Assessment Criteria:
        1. Are explanations clear and easy to understand?
        2. Is vocabulary appropriate for the audience level?
        3. Are concepts introduced in logical order?
        4. Are examples helpful and relevant?
        5. Are complex ideas broken down effectively?
        
        Score from 0.0 to 1.0:
        - 1.0 = Crystal clear, perfectly appropriate explanations
        - 0.8 = Clear with minor areas for improvement
        - 0.6 = Generally clear but some confusing sections
        - 0.4 = Unclear in several important areas
        - 0.2 = Difficult to understand for target audience
        - 0.0 = Very confusing or inappropriate
        
        JSON format:
        {{
            "clarity_score": float,
            "vocabulary_appropriateness": float,
            "explanation_quality": float,
            "reasoning": "explanation"
        }}
        """
        
        response = await self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            import json
            result = json.loads(response.content[0].text)
            return {"clarity_score": result["clarity_score"]}
        except:
            return {"clarity_score": 0.5}
    
    async def _evaluate_engagement(
        self, 
        content: str, 
        content_type: ContentType, 
        audience_level: LearningLevel
    ) -> Dict[str, float]:
        """Evaluate content engagement potential."""
        
        prompt = f"""
        Evaluate how engaging this {content_type.value} content is for {audience_level.value} students.
        
        Content:
        {content}
        
        Assessment Criteria:
        1. Does it capture and maintain interest?
        2. Are there interactive or thought-provoking elements?
        3. Is the tone appropriate and engaging?
        4. Are examples relatable and interesting?
        5. Does it encourage active learning?
        
        Score engagement level from 0.0 to 1.0:
        - 1.0 = Highly engaging, students will be motivated to learn
        - 0.8 = Good engagement with interesting elements
        - 0.6 = Moderately engaging, adequate interest level
        - 0.4 = Somewhat dry but acceptable
        - 0.2 = Low engagement, likely to bore students
        - 0.0 = Very boring or off-putting
        
        JSON format:
        {{
            "engagement_score": float,
            "interactive_elements": int,
            "tone_appropriateness": float,
            "motivation_potential": float,
            "reasoning": "explanation"
        }}
        """
        
        response = await self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            import json
            result = json.loads(response.content[0].text)
            return {"engagement_score": result["engagement_score"]}
        except:
            return {"engagement_score": 0.5}
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate confidence level based on score consistency."""
        score_values = [v for v in scores.values() if isinstance(v, (int, float))]
        if len(score_values) < 2:
            return 0.5
        
        # Higher confidence when scores are consistent
        std_dev = statistics.stdev(score_values)
        confidence = max(0.0, 1.0 - (std_dev * 2))  # Scale standard deviation
        return min(confidence, 1.0)
    
    def _identify_improvement_areas(self, scores: Dict[str, float]) -> List[str]:
        """Identify areas needing improvement based on low scores."""
        improvement_areas = []
        threshold = 0.7  # Scores below this need improvement
        
        area_mapping = {
            "accuracy_score": "Factual accuracy needs verification",
            "clarity_score": "Explanations could be clearer",
            "completeness_score": "Content coverage could be more comprehensive",
            "engagement_score": "Content could be more engaging",
            "learning_objective_alignment": "Better alignment with learning objectives needed",
            "readability_score": "Readability could be improved for target audience",
            "structure_score": "Content structure and organization needs improvement"
        }
        
        for metric, message in area_mapping.items():
            if scores.get(metric, 1.0) < threshold:
                improvement_areas.append(message)
        
        return improvement_areas
```

### 2. Readability and Structure Analysis
```python
import re
import statistics
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ReadabilityMetrics:
    """Readability assessment metrics."""
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    automated_readability_index: float
    coleman_liau_index: float
    score: float  # Normalized 0-1 score for target audience
    grade_level: float
    recommendations: List[str]

class ReadabilityAnalyzer:
    """Analyze content readability for educational appropriateness."""
    
    def __init__(self):
        self.grade_level_targets = {
            LearningLevel.ELEMENTARY: (3, 6),
            LearningLevel.MIDDLE_SCHOOL: (6, 8),
            LearningLevel.HIGH_SCHOOL: (9, 12),
            LearningLevel.COLLEGE: (13, 16)
        }
    
    def analyze(self, content: str, target_level: LearningLevel) -> ReadabilityMetrics:
        """Comprehensive readability analysis."""
        
        # Text statistics
        sentences = self._count_sentences(content)
        words = self._count_words(content)
        syllables = self._count_syllables(content)
        characters = len(re.sub(r'\s', '', content))
        
        if sentences == 0 or words == 0:
            return ReadabilityMetrics(0, 0, 0, 0, 0, 0, ["Content too short to analyze"])
        
        # Calculate readability metrics
        flesch_ease = self._flesch_reading_ease(sentences, words, syllables)
        flesch_grade = self._flesch_kincaid_grade(sentences, words, syllables)
        ari = self._automated_readability_index(sentences, words, characters)
        coleman_liau = self._coleman_liau_index(sentences, words, characters)
        
        # Average grade level
        avg_grade = statistics.mean([flesch_grade, ari, coleman_liau])
        
        # Score appropriateness for target level
        target_range = self.grade_level_targets[target_level]
        score = self._calculate_appropriateness_score(avg_grade, target_range)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            avg_grade, target_range, words/sentences if sentences > 0 else 0
        )
        
        return ReadabilityMetrics(
            flesch_reading_ease=flesch_ease,
            flesch_kincaid_grade=flesch_grade,
            automated_readability_index=ari,
            coleman_liau_index=coleman_liau,
            score=score,
            grade_level=avg_grade,
            recommendations=recommendations
        )
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _count_syllables(self, text: str) -> int:
        """Estimate syllable count."""
        words = re.findall(r'\b\w+\b', text.lower())
        total_syllables = 0
        
        for word in words:
            # Simple syllable counting heuristic
            vowels = re.findall(r'[aeiouy]', word)
            syllables = len(vowels)
            
            # Adjust for common patterns
            if word.endswith('e'):
                syllables -= 1
            if word.endswith('le') and len(word) > 2:
                syllables += 1
            if syllables == 0:
                syllables = 1
            
            total_syllables += syllables
        
        return total_syllables
    
    def _flesch_reading_ease(self, sentences: int, words: int, syllables: int) -> float:
        """Calculate Flesch Reading Ease score."""
        if sentences == 0 or words == 0:
            return 0
        return 206.835 - (1.015 * words/sentences) - (84.6 * syllables/words)
    
    def _flesch_kincaid_grade(self, sentences: int, words: int, syllables: int) -> float:
        """Calculate Flesch-Kincaid Grade Level."""
        if sentences == 0 or words == 0:
            return 0
        return (0.39 * words/sentences) + (11.8 * syllables/words) - 15.59
    
    def _automated_readability_index(self, sentences: int, words: int, characters: int) -> float:
        """Calculate Automated Readability Index."""
        if sentences == 0 or words == 0:
            return 0
        return (4.71 * characters/words) + (0.5 * words/sentences) - 21.43
    
    def _coleman_liau_index(self, sentences: int, words: int, characters: int) -> float:
        """Calculate Coleman-Liau Index."""
        if words == 0:
            return 0
        L = (characters / words) * 100
        S = (sentences / words) * 100
        return (0.0588 * L) - (0.296 * S) - 15.8
    
    def _calculate_appropriateness_score(self, grade_level: float, target_range: Tuple[int, int]) -> float:
        """Calculate how appropriate the grade level is for target audience."""
        min_grade, max_grade = target_range
        
        if min_grade <= grade_level <= max_grade:
            return 1.0  # Perfect fit
        elif grade_level < min_grade:
            # Too easy
            diff = min_grade - grade_level
            return max(0.5, 1.0 - (diff * 0.1))
        else:
            # Too difficult
            diff = grade_level - max_grade
            return max(0.0, 1.0 - (diff * 0.15))
    
    def _generate_recommendations(self, grade_level: float, target_range: Tuple[int, int], avg_sentence_length: float) -> List[str]:
        """Generate readability improvement recommendations."""
        recommendations = []
        min_grade, max_grade = target_range
        
        if grade_level > max_grade:
            recommendations.append(f"Content is too difficult (grade {grade_level:.1f} vs target {max_grade})")
            if avg_sentence_length > 20:
                recommendations.append("Use shorter sentences (current average: {:.1f} words)".format(avg_sentence_length))
            recommendations.append("Replace complex words with simpler alternatives")
            recommendations.append("Break long paragraphs into shorter ones")
        
        elif grade_level < min_grade:
            recommendations.append(f"Content may be too simple (grade {grade_level:.1f} vs target {min_grade})")
            recommendations.append("Consider using more sophisticated vocabulary")
            recommendations.append("Add more detailed explanations")
        
        if avg_sentence_length > 25:
            recommendations.append("Sentences are too long for clear comprehension")
        elif avg_sentence_length < 8:
            recommendations.append("Sentences could be more detailed")
        
        return recommendations

@dataclass
class StructureMetrics:
    """Content structure assessment metrics."""
    has_introduction: bool
    has_conclusion: bool
    has_clear_sections: bool
    logical_flow_score: float
    heading_hierarchy_score: float
    transition_quality: float
    score: float  # Overall structure score 0-1
    suggestions: List[str]

class ContentStructureAnalyzer:
    """Analyze educational content structure and organization."""
    
    def analyze(self, content: str, content_type: ContentType) -> StructureMetrics:
        """Analyze content structure for educational effectiveness."""
        
        # Detect structural elements
        has_intro = self._has_introduction(content)
        has_conclusion = self._has_conclusion(content)
        has_sections = self._has_clear_sections(content)
        
        # Analyze structure quality
        logical_flow = self._analyze_logical_flow(content, content_type)
        heading_hierarchy = self._analyze_heading_hierarchy(content)
        transition_quality = self._analyze_transitions(content)
        
        # Calculate overall score
        structure_elements = [has_intro, has_conclusion, has_sections]
        element_score = sum(structure_elements) / len(structure_elements)
        quality_score = statistics.mean([logical_flow, heading_hierarchy, transition_quality])
        overall_score = (element_score + quality_score) / 2
        
        # Generate suggestions
        suggestions = self._generate_structure_suggestions(
            has_intro, has_conclusion, has_sections, logical_flow, heading_hierarchy
        )
        
        return StructureMetrics(
            has_introduction=has_intro,
            has_conclusion=has_conclusion,
            has_clear_sections=has_sections,
            logical_flow_score=logical_flow,
            heading_hierarchy_score=heading_hierarchy,
            transition_quality=transition_quality,
            score=overall_score,
            suggestions=suggestions
        )
    
    def _has_introduction(self, content: str) -> bool:
        """Check if content has a clear introduction."""
        intro_patterns = [
            r'^.{0,200}(introduction|overview|in this|we will|this guide)',
            r'^.{0,200}(welcome|let\'s explore|today we)',
            r'^.{0,200}(what is|understanding|learning about)'
        ]
        
        first_paragraph = content[:500].lower()
        return any(re.search(pattern, first_paragraph, re.IGNORECASE | re.MULTILINE) for pattern in intro_patterns)
    
    def _has_conclusion(self, content: str) -> bool:
        """Check if content has a clear conclusion."""
        conclusion_patterns = [
            r'(conclusion|summary|in summary|to summarize)',
            r'(key takeaways|remember|important points)',
            r'(final thoughts|wrapping up|to conclude)'
        ]
        
        last_paragraph = content[-500:].lower()
        return any(re.search(pattern, last_paragraph, re.IGNORECASE) for pattern in conclusion_patterns)
    
    def _has_clear_sections(self, content: str) -> bool:
        """Check if content has clear section divisions."""
        # Look for headings, numbered sections, or clear breaks
        heading_patterns = [
            r'^#{1,6}\s+',  # Markdown headings
            r'^\d+\.\s+[A-Z]',  # Numbered sections
            r'^[A-Z][^.]{10,50}:?\s*$',  # Title-case headings
            r'\n\n[A-Z][^.]{5,30}\n'  # Standalone section titles
        ]
        
        return any(re.search(pattern, content, re.MULTILINE) for pattern in heading_patterns)
    
    def _analyze_logical_flow(self, content: str, content_type: ContentType) -> float:
        """Analyze logical flow of content."""
        # This is a simplified analysis - in production would use more sophisticated NLP
        paragraphs = content.split('\n\n')
        
        if len(paragraphs) < 2:
            return 0.5
        
        # Check for logical flow indicators
        flow_indicators = [
            r'\b(first|second|third|next|then|finally|therefore|however|moreover)\b',
            r'\b(as a result|consequently|in addition|furthermore|meanwhile)\b',
            r'\b(for example|for instance|such as|specifically|namely)\b'
        ]
        
        indicator_count = 0
        for paragraph in paragraphs:
            for pattern in flow_indicators:
                if re.search(pattern, paragraph, re.IGNORECASE):
                    indicator_count += 1
                    break
        
        # Score based on proportion of paragraphs with flow indicators
        flow_score = min(indicator_count / len(paragraphs), 1.0)
        
        # Bonus for content type-specific structure
        if content_type == ContentType.STUDY_GUIDE:
            if re.search(r'(definition|explanation|example|practice)', content, re.IGNORECASE):
                flow_score += 0.2
        elif content_type == ContentType.QUIZ:
            if re.search(r'(question|answer|explanation)', content, re.IGNORECASE):
                flow_score += 0.2
        
        return min(flow_score, 1.0)
    
    def _analyze_heading_hierarchy(self, content: str) -> float:
        """Analyze heading hierarchy and organization."""
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        
        if not headings:
            return 0.3  # No headings is poor structure
        
        # Check for proper hierarchy (more complex analysis would be needed)
        if len(headings) >= 3:
            return 0.9  # Good structure
        elif len(headings) >= 1:
            return 0.7  # Decent structure
        else:
            return 0.5
    
    def _analyze_transitions(self, content: str) -> float:
        """Analyze quality of transitions between sections."""
        transition_words = [
            'however', 'therefore', 'moreover', 'furthermore', 'consequently',
            'in addition', 'as a result', 'for example', 'in contrast',
            'similarly', 'meanwhile', 'nevertheless', 'thus', 'hence'
        ]
        
        paragraphs = content.split('\n\n')
        if len(paragraphs) < 2:
            return 0.5
        
        transition_count = 0
        for paragraph in paragraphs[1:]:  # Skip first paragraph
            first_sentence = paragraph.split('.')[0].lower()
            if any(word in first_sentence for word in transition_words):
                transition_count += 1
        
        return min(transition_count / (len(paragraphs) - 1), 1.0)
    
    def _generate_structure_suggestions(
        self, 
        has_intro: bool, 
        has_conclusion: bool, 
        has_sections: bool,
        logical_flow: float,
        heading_hierarchy: float
    ) -> List[str]:
        """Generate suggestions for improving content structure."""
        suggestions = []
        
        if not has_intro:
            suggestions.append("Add a clear introduction that previews the content")
        
        if not has_conclusion:
            suggestions.append("Include a conclusion that summarizes key points")
        
        if not has_sections:
            suggestions.append("Organize content into clearly defined sections with headings")
        
        if logical_flow < 0.6:
            suggestions.append("Improve logical flow with better transitions between ideas")
        
        if heading_hierarchy < 0.7:
            suggestions.append("Create a clear heading hierarchy to organize content")
        
        return suggestions
```

## Sources
71. Learning Science and Cognitive Load Theory Principles
72. Bloom's Taxonomy Educational Standards Framework
73. AI-Powered Educational Content Quality Assessment (2024-2025)
74. Automated Readability Analysis for Educational Content
75. Content Structure Assessment for Learning Effectiveness
76. Educational Assessment Using Multiple AI Judges
77. Learning Objectives Alignment and Cognitive Level Assessment
78. Multi-Modal Educational Content Evaluation Framework
79. Real-Time Content Quality Monitoring Systems
80. Educational Content Improvement Recommendation Systems