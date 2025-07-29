#!/usr/bin/env python3
"""
Tikal Study Guide Quality Validation Demo

This script demonstrates the validation functionality that would be used
for the '/tikal-validate-quality study-guide high-school' command.

Usage:
    python3 tikal_validate_demo.py
"""

import json
import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationStage(Enum):
    """Validation stages for content quality assessment."""
    STRUCTURAL = "Structural Validation"
    COMPLETENESS = "Completeness Validation"
    READABILITY = "Readability Validation"
    HIGH_SCHOOL_STANDARDS = "High School Standards"
    ENGAGEMENT = "Engagement Assessment"


@dataclass
class ValidationResult:
    """Result of a validation stage."""
    stage: ValidationStage
    passed: bool
    score: float
    issues: List[str]
    suggestions: List[str]


class TikalStudyGuideValidator:
    """
    Simplified Tikal Study Guide Validator for high school content.
    
    This demonstrates the quality validation system that would be used
    in the full Tikal platform.
    """

    def __init__(self):
        """Initialize the validator with high school standards."""
        self.high_school_standards = {
            "min_content_length": 1000,
            "max_content_length": 6000,
            "min_key_concepts": 8,
            "max_key_concepts": 15,
            "min_critical_thinking_words": 5,
            "target_reading_level": {"min": 9, "max": 12}
        }
        
        self.critical_thinking_words = [
            "analyze", "compare", "contrast", "evaluate", "explain",
            "examine", "consider", "argue", "evidence", "conclude",
            "interpret", "assess", "justify", "synthesize", "critique"
        ]
        
        self.engagement_indicators = [
            "example", "imagine", "consider", "think about", "question",
            "discover", "explore", "understand", "learn", "practice"
        ]

    def validate_study_guide(self, study_guide_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of a study guide for high school level.
        
        Args:
            study_guide_data: Dictionary containing study guide content
            
        Returns:
            Comprehensive validation report
        """
        print("🔍 TIKAL STUDY GUIDE QUALITY VALIDATION")
        print("=" * 50)
        print("Validating study guide for high school educational standards...\n")
        
        validation_results = []
        
        # Stage 1: Structural Validation
        structural_result = self._validate_structure(study_guide_data)
        validation_results.append(structural_result)
        print(f"✓ {structural_result.stage.value}: {'PASSED' if structural_result.passed else 'FAILED'} ({structural_result.score:.2f})")
        
        # Stage 2: Completeness Validation
        completeness_result = self._validate_completeness(study_guide_data)
        validation_results.append(completeness_result)
        print(f"✓ {completeness_result.stage.value}: {'PASSED' if completeness_result.passed else 'FAILED'} ({completeness_result.score:.2f})")
        
        # Stage 3: Readability Validation
        readability_result = self._validate_readability(study_guide_data)
        validation_results.append(readability_result)
        print(f"✓ {readability_result.stage.value}: {'PASSED' if readability_result.passed else 'FAILED'} ({readability_result.score:.2f})")
        
        # Stage 4: High School Standards
        standards_result = self._validate_high_school_standards(study_guide_data)
        validation_results.append(standards_result)
        print(f"✓ {standards_result.stage.value}: {'PASSED' if standards_result.passed else 'FAILED'} ({standards_result.score:.2f})")
        
        # Stage 5: Engagement Assessment
        engagement_result = self._validate_engagement(study_guide_data)
        validation_results.append(engagement_result)
        print(f"✓ {engagement_result.stage.value}: {'PASSED' if engagement_result.passed else 'FAILED'} ({engagement_result.score:.2f})")
        
        # Calculate overall results
        overall_score = sum(r.score for r in validation_results) / len(validation_results)
        overall_passed = all(r.passed for r in validation_results)
        grade = self._calculate_grade(overall_score)
        
        print(f"\n📊 OVERALL ASSESSMENT")
        print(f"Score: {overall_score:.2f}/1.0 (Grade: {grade})")
        print(f"Status: {'PASSED' if overall_passed else 'NEEDS IMPROVEMENT'}")
        
        # Generate detailed report
        report = self._generate_detailed_report(validation_results, overall_score, overall_passed, grade)
        
        return report

    def _validate_structure(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate the structural integrity of the study guide."""
        issues = []
        score = 1.0
        
        # Check required fields
        required_fields = ["title", "overview", "key_concepts", "detailed_content", "summary"]
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
                score -= 0.2
        
        # Check data types
        if "title" in data and not isinstance(data["title"], str):
            issues.append("Title must be a string")
            score -= 0.1
            
        if "key_concepts" in data and not isinstance(data["key_concepts"], list):
            issues.append("Key concepts must be a list")
            score -= 0.1
        
        passed = len(issues) == 0
        suggestions = ["Ensure all required fields are present and properly formatted"] if issues else []
        
        return ValidationResult(
            stage=ValidationStage.STRUCTURAL,
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            suggestions=suggestions
        )

    def _validate_completeness(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate content completeness according to Tikal standards."""
        issues = []
        score = 1.0
        
        # Title length (10-200 characters)
        if "title" in data:
            title_len = len(data["title"])
            if title_len < 10:
                issues.append("Title too short (minimum 10 characters)")
                score -= 0.1
            elif title_len > 200:
                issues.append("Title too long (maximum 200 characters)")
                score -= 0.1
        
        # Overview length (100-1000 characters)
        if "overview" in data:
            overview_len = len(data["overview"])
            if overview_len < 100:
                issues.append("Overview too short (minimum 100 characters)")
                score -= 0.2
            elif overview_len > 1000:
                issues.append("Overview too long (maximum 1000 characters)")
                score -= 0.1
        
        # Key concepts count (5-20)
        if "key_concepts" in data:
            concepts_count = len(data["key_concepts"])
            if concepts_count < 5:
                issues.append("Too few key concepts (minimum 5)")
                score -= 0.2
            elif concepts_count > 20:
                issues.append("Too many key concepts (maximum 20)")
                score -= 0.1
        
        # Detailed content length (500-8000 characters)
        if "detailed_content" in data:
            content_len = len(data["detailed_content"])
            if content_len < 500:
                issues.append("Detailed content too short (minimum 500 characters)")
                score -= 0.3
            elif content_len > 8000:
                issues.append("Detailed content too long (maximum 8000 characters)")
                score -= 0.1
        
        # Summary length (100-1000 characters)
        if "summary" in data:
            summary_len = len(data["summary"])
            if summary_len < 100:
                issues.append("Summary too short (minimum 100 characters)")
                score -= 0.1
            elif summary_len > 1000:
                issues.append("Summary too long (maximum 1000 characters)")
                score -= 0.1
        
        passed = len(issues) == 0
        suggestions = ["Adjust content length to meet Tikal standards"] if issues else []
        
        return ValidationResult(
            stage=ValidationStage.COMPLETENESS,
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            suggestions=suggestions
        )

    def _validate_readability(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate readability for high school level."""
        issues = []
        score = 1.0
        
        if "detailed_content" not in data:
            return ValidationResult(
                stage=ValidationStage.READABILITY,
                passed=False,
                score=0.0,
                issues=["No content to analyze"],
                suggestions=["Add detailed content for readability analysis"]
            )
        
        content = data["detailed_content"]
        
        # Simple readability metrics
        sentences = len([s for s in content.split('.') if s.strip()])
        words = len(content.split())
        
        if sentences == 0:
            avg_sentence_length = 0
        else:
            avg_sentence_length = words / sentences
        
        # Check average sentence length (should be reasonable for high school)
        if avg_sentence_length > 25:
            issues.append("Sentences too long for high school level")
            score -= 0.2
        elif avg_sentence_length < 8:
            issues.append("Sentences too short - may lack depth")
            score -= 0.1
        
        # Check for complex vocabulary indicators
        complex_words = 0
        for word in content.split():
            if len(word) > 12:  # Simple complexity metric
                complex_words += 1
        
        complexity_ratio = complex_words / max(1, words)
        if complexity_ratio > 0.15:
            issues.append("Content may be too complex for high school level")
            score -= 0.2
        elif complexity_ratio < 0.05:
            issues.append("Content may lack academic vocabulary")
            score -= 0.1
        
        # Check for paragraph structure
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < 3:
            issues.append("Content needs better paragraph structure")
            score -= 0.1
        
        passed = len(issues) == 0
        suggestions = ["Adjust sentence length and vocabulary for high school level"] if issues else []
        
        return ValidationResult(
            stage=ValidationStage.READABILITY,
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            suggestions=suggestions
        )

    def _validate_high_school_standards(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate against specific high school educational standards."""
        issues = []
        score = 1.0
        
        if "detailed_content" not in data:
            return ValidationResult(
                stage=ValidationStage.HIGH_SCHOOL_STANDARDS,
                passed=False,
                score=0.0,
                issues=["No content to validate against standards"],
                suggestions=["Add detailed content for standards validation"]
            )
        
        content = data["detailed_content"].lower()
        
        # Check for critical thinking elements
        critical_thinking_count = sum(1 for word in self.critical_thinking_words if word in content)
        if critical_thinking_count < self.high_school_standards["min_critical_thinking_words"]:
            issues.append("Insufficient critical thinking elements for high school level")
            score -= 0.3
        
        # Check content length for high school appropriateness
        content_length = len(data["detailed_content"])
        if content_length < self.high_school_standards["min_content_length"]:
            issues.append("Content too brief for comprehensive high school study guide")
            score -= 0.2
        elif content_length > self.high_school_standards["max_content_length"]:
            issues.append("Content may be too lengthy for typical high school study guide")
            score -= 0.1
        
        # Check key concepts count
        if "key_concepts" in data:
            concepts_count = len(data["key_concepts"])
            if concepts_count < self.high_school_standards["min_key_concepts"]:
                issues.append("Too few key concepts for high school level depth")
                score -= 0.2
        
        # Check for historical connections (subject-specific)
        connections = ["modern", "today", "current", "contemporary", "influence", "impact"]
        connection_count = sum(1 for word in connections if word in content)
        if connection_count < 2:
            issues.append("Needs more connections to modern world/relevance")
            score -= 0.1
        
        # Check for examples and applications
        examples = ["example", "for instance", "such as", "including", "like"]
        example_count = sum(1 for phrase in examples if phrase in content)
        if example_count < 3:
            issues.append("Needs more examples and concrete applications")
            score -= 0.1
        
        passed = len(issues) == 0
        suggestions = [
            "Add more critical thinking elements",
            "Include more real-world connections",
            "Provide concrete examples and applications"
        ] if issues else []
        
        return ValidationResult(
            stage=ValidationStage.HIGH_SCHOOL_STANDARDS,
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            suggestions=suggestions
        )

    def _validate_engagement(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate student engagement elements."""
        issues = []
        score = 1.0
        
        if "detailed_content" not in data:
            return ValidationResult(
                stage=ValidationStage.ENGAGEMENT,
                passed=False,
                score=0.0,
                issues=["No content to analyze for engagement"],
                suggestions=["Add engaging content elements"]
            )
        
        content = data["detailed_content"].lower()
        
        # Check for engagement indicators
        engagement_count = sum(1 for word in self.engagement_indicators if word in content)
        if engagement_count < 3:
            issues.append("Limited student engagement elements")
            score -= 0.2
        
        # Check for questions (engagement through inquiry)
        question_count = content.count('?')
        if question_count < 2:
            issues.append("Needs more questions to engage students")
            score -= 0.1
        
        # Check for active voice and direct address
        active_indicators = ["you", "your", "we", "let's", "consider"]
        active_count = sum(1 for word in active_indicators if word in content)
        if active_count < 5:
            issues.append("Could use more direct student engagement")
            score -= 0.1
        
        # Check for varied content structure
        headers = len(re.findall(r'^#+\s', data["detailed_content"], re.MULTILINE))
        if headers < 3:
            issues.append("Needs better content organization with headers")
            score -= 0.1
        
        # Check for lists or bullet points (visual engagement)
        list_items = content.count('*') + content.count('-') + content.count('1.')
        if list_items < 5:
            issues.append("Could benefit from more lists and structured information")
            score -= 0.1
        
        passed = len(issues) == 0
        suggestions = [
            "Add more interactive elements",
            "Include discussion questions",
            "Use varied content formatting"
        ] if issues else []
        
        return ValidationResult(
            stage=ValidationStage.ENGAGEMENT,
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            suggestions=suggestions
        )

    def _calculate_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 0.90:
            return "A"
        elif score >= 0.80:
            return "B"
        elif score >= 0.70:
            return "C"
        elif score >= 0.60:
            return "D"
        else:
            return "F"

    def _generate_detailed_report(self, results: List[ValidationResult], 
                                overall_score: float, overall_passed: bool, 
                                grade: str) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        
        # Separate issues and suggestions
        all_issues = []
        all_suggestions = []
        
        for result in results:
            all_issues.extend(result.issues)
            all_suggestions.extend(result.suggestions)
        
        # Generate summary
        summary = f"""
TIKAL STUDY GUIDE VALIDATION REPORT
===================================

Overall Assessment: {grade} ({overall_score:.2f}/1.0)
Status: {'PASSED' if overall_passed else 'NEEDS IMPROVEMENT'}

Validation Stages:
{self._format_stage_results(results)}

Summary:
This study guide {'meets' if overall_passed else 'does not meet'} the quality standards 
for high school educational content. {'No major issues found.' if overall_passed else 'Please address the issues listed below.'}

Major Issues Found:
{self._format_issues(all_issues) if all_issues else '- None'}

Improvement Suggestions:
{self._format_suggestions(all_suggestions) if all_suggestions else '- Content meets current standards'}

Next Steps:
{'✅ Study guide approved for high school use' if overall_passed else '⚠️  Revise content and resubmit for validation'}
        """
        
        return {
            "overall_score": overall_score,
            "grade": grade,
            "passed": overall_passed,
            "validation_stages": [
                {
                    "stage": result.stage.value,
                    "passed": result.passed,
                    "score": result.score,
                    "issues": result.issues,
                    "suggestions": result.suggestions
                }
                for result in results
            ],
            "summary": summary.strip(),
            "total_issues": len(all_issues),
            "total_suggestions": len(all_suggestions)
        }

    def _format_stage_results(self, results: List[ValidationResult]) -> str:
        """Format validation stage results for display."""
        lines = []
        for result in results:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            lines.append(f"- {result.stage.value}: {status} ({result.score:.2f})")
        return "\n".join(lines)

    def _format_issues(self, issues: List[str]) -> str:
        """Format issues list for display."""
        return "\n".join([f"- {issue}" for issue in issues[:10]])  # Limit to top 10

    def _format_suggestions(self, suggestions: List[str]) -> str:
        """Format suggestions list for display."""
        unique_suggestions = list(set(suggestions))  # Remove duplicates
        return "\n".join([f"- {suggestion}" for suggestion in unique_suggestions[:10]])


def create_sample_study_guide() -> Dict[str, Any]:
    """Create a sample high school study guide for demonstration."""
    return {
        "title": "Introduction to World History: Ancient Civilizations",
        "overview": "This comprehensive study guide covers the major ancient civilizations including Mesopotamia, Egypt, Greece, and Rome. Students will explore the political, social, economic, and cultural aspects of these civilizations and their lasting impact on modern society.",
        "key_concepts": [
            "Civilization",
            "City-state", 
            "Cuneiform writing",
            "Divine kingship",
            "Democracy",
            "Philosophy",
            "Social hierarchy",
            "Cultural diffusion",
            "Historical evidence",
            "Cause and effect"
        ],
        "detailed_content": """# Ancient Civilizations Study Guide

## Introduction
Ancient civilizations laid the foundation for modern society. By studying these early cultures, we can understand how human societies developed government, law, religion, and culture. Consider how these ancient innovations continue to influence our world today.

## Mesopotamian Civilization (3500-539 BCE)

### Key Features:
- **Location**: Between the Tigris and Euphrates rivers (modern-day Iraq)
- **First Civilization**: Developed the world's first cities and writing system
- **Government**: City-states ruled by priest-kings

### Major Achievements:
1. **Cuneiform Writing**: First writing system using wedge-shaped marks on clay tablets
2. **Code of Hammurabi**: One of the first written legal codes with the principle "eye for an eye"
3. **Ziggurats**: Massive temple complexes that served as religious and political centers
4. **Irrigation Systems**: Advanced farming techniques that supported large populations

How do you think these innovations compare to modern technological advances? What similarities can you identify?

### Social Structure:
- Nobles and priests at the top
- Merchants and artisans in the middle
- Farmers and slaves at the bottom

## Ancient Egyptian Civilization (3100-30 BCE)

### Key Features:
- **Location**: Along the Nile River in northeastern Africa
- **Pharaonic Rule**: Divine kings who were considered gods on earth
- **Stable Society**: Lasted over 3000 years with remarkable consistency

### Major Achievements:
1. **Pyramids**: Massive burial monuments demonstrating advanced engineering
2. **Mummification**: Sophisticated preservation techniques for the afterlife
3. **Hieroglyphics**: Complex writing system using pictures and symbols
4. **Calendar**: 365-day solar calendar similar to ours today

Analyze the significance of these achievements: What do they tell us about Egyptian values and priorities?

### Social Structure:
- Pharaoh at the top as divine ruler
- Nobles, priests, and government officials
- Skilled craftsmen and merchants
- Farmers (majority of population)
- Slaves at the bottom

## Ancient Greek Civilization (800-146 BCE)

### Key Features:
- **Location**: Greek peninsula and islands in the Mediterranean
- **City-States**: Independent political units like Athens and Sparta
- **Cultural Innovation**: Birthplace of democracy, philosophy, and theater

### Major Achievements:
1. **Democracy**: Athens developed the first democratic government
2. **Philosophy**: Great thinkers like Socrates, Plato, and Aristotle
3. **Olympic Games**: Athletic competitions honoring the gods
4. **Literature**: Epic poems like the Iliad and Odyssey

Think about this: How do Greek democratic principles influence modern governments?

### Comparison: Athens vs. Sparta
- **Athens**: Democracy, education, arts, and philosophy
- **Sparta**: Military state, warrior culture, strict discipline

Compare and contrast these two approaches to governance. Which elements do you see in modern societies?

## Connections to Today
These ancient civilizations continue to influence us:
- **Government**: Democratic principles from Greece
- **Law**: Legal concepts from Mesopotamia and Rome
- **Architecture**: Greek columns and Roman arches
- **Language**: Many English words come from Greek and Latin roots
- **Philosophy**: Ancient Greek ideas about ethics and logic

## Study Tips:
1. Create timeline comparisons between civilizations
2. Make connections between ancient and modern practices
3. Use maps to understand geographic influences
4. Practice analyzing primary sources like ancient texts
5. Develop arguments about historical cause and effect

What questions do you have about these civilizations? How might understanding them help you better understand current world events?
        """,
        "summary": "Ancient civilizations including Mesopotamia, Egypt, and Greece established fundamental aspects of human society including government, law, writing, and culture. Understanding these early societies helps us comprehend the development of modern civilization and appreciate our shared human heritage. Students should focus on making connections between ancient innovations and contemporary society.",
        "recommended_reading": [
            "The Complete World History by DK Publishing",
            "Ancient Civilizations by National Geographic Kids",
            "Primary sources: Code of Hammurabi excerpts",
            "Greek Philosophy: Plato's Republic (simplified version)"
        ]
    }


def main():
    """Main function to demonstrate Tikal study guide validation."""
    print("TIKAL STUDY GUIDE QUALITY VALIDATION SYSTEM")
    print("=" * 60)
    print("This demonstrates the '/tikal-validate-quality study-guide high-school' functionality\n")
    
    # Create validator
    validator = TikalStudyGuideValidator()
    
    # Create sample study guide
    study_guide = create_sample_study_guide()
    
    print("Sample Study Guide Created:")
    print(f"- Title: {study_guide['title']}")
    print(f"- Content Length: {len(study_guide['detailed_content'])} characters")
    print(f"- Key Concepts: {len(study_guide['key_concepts'])} items")
    print()
    
    # Run validation
    report = validator.validate_study_guide(study_guide)
    
    # Display summary
    print("\n" + "=" * 60)
    print(report["summary"])
    
    # Save report to file
    with open("tikal_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: tikal_validation_report.json")
    
    return report["passed"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)