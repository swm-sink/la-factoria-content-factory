#!/usr/bin/env python3
"""
Tikal Study Guide Quality Validation Script

This script validates the quality of a study guide for high school level
using Tikal's comprehensive validation system.

Usage:
    python validate_study_guide.py [--input-file FILEPATH] [--interactive]
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Setup path for imports
sys.path.append(str(Path(__file__).parent))

from app.services.comprehensive_content_validator import ComprehensiveContentValidator
from app.services.content_validation import get_content_validation_service
from app.services.quality_metrics import QualityMetricsService
from app.models.pydantic.content import StudyGuide, ContentOutline, GeneratedContent
from app.utils.content_validation import validate_and_parse_content_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StudyGuideValidator:
    """High School Study Guide Quality Validator using Tikal's validation system."""

    def __init__(self):
        """Initialize the validator with Tikal's validation services."""
        self.comprehensive_validator = ComprehensiveContentValidator()
        self.content_validator = get_content_validation_service()
        self.quality_metrics = QualityMetricsService()
        
    def create_sample_study_guide(self) -> Dict[str, Any]:
        """Create a sample high school study guide for validation."""
        return {
            "content_outline": {
                "title": "Introduction to World History: Ancient Civilizations",
                "overview": "This comprehensive study guide covers the major ancient civilizations including Mesopotamia, Egypt, Greece, and Rome. Students will explore the political, social, economic, and cultural aspects of these civilizations and their lasting impact on modern society.",
                "learning_objectives": [
                    "Understand the development of early human civilizations",
                    "Analyze the political systems of ancient civilizations", 
                    "Compare and contrast different ancient cultures",
                    "Evaluate the lasting impact of ancient civilizations",
                    "Develop critical thinking skills about historical sources"
                ],
                "sections": [
                    {
                        "section_number": 1,
                        "title": "Mesopotamian Civilization",
                        "description": "Explore the world's first civilization in the fertile crescent, including Sumerian city-states and the development of writing.",
                        "key_points": [
                            "Development of cuneiform writing system",
                            "Sumerian city-states and government",
                            "Code of Hammurabi and early laws",
                            "Religious beliefs and ziggurats",
                            "Agricultural innovations and irrigation"
                        ]
                    },
                    {
                        "section_number": 2,
                        "title": "Ancient Egyptian Civilization", 
                        "description": "Study the civilization along the Nile River, focusing on pharaohs, pyramids, and Egyptian society.",
                        "key_points": [
                            "Pharaonic system and divine kingship",
                            "Pyramid construction and burial practices",
                            "Hieroglyphic writing system",
                            "Social hierarchy and daily life",
                            "Religious beliefs and afterlife concepts"
                        ]
                    },
                    {
                        "section_number": 3,
                        "title": "Ancient Greek Civilization",
                        "description": "Examine the birthplace of democracy, philosophy, and Western culture.",
                        "key_points": [
                            "Development of democracy in Athens",
                            "Greek philosophy and major thinkers",
                            "Olympic Games and Greek culture",
                            "Greek mythology and religion",
                            "Military tactics and the phalanx"
                        ]
                    }
                ]
            },
            "study_guide": {
                "title": "Introduction to World History: Ancient Civilizations Study Guide",
                "overview": "This study guide provides comprehensive coverage of ancient civilizations for high school students. It includes key concepts, detailed explanations, and connections to modern society to help students understand the foundations of human civilization.",
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
                    "Cause and effect in history"
                ],
                "detailed_content": """
# Ancient Civilizations Study Guide

## Introduction
Ancient civilizations laid the foundation for modern society. By studying these early cultures, we can understand how human societies developed government, law, religion, and culture.

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

### Comparison: Athens vs. Sparta
- **Athens**: Democracy, education, arts, and philosophy
- **Sparta**: Military state, warrior culture, strict discipline

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
                """,
                "summary": "Ancient civilizations including Mesopotamia, Egypt, and Greece established fundamental aspects of human society including government, law, writing, and culture. Understanding these early societies helps us comprehend the development of modern civilization and appreciate our shared human heritage.",
                "recommended_reading": [
                    "The Complete World History by DK Publishing",
                    "Ancient Civilizations by National Geographic Kids",
                    "Primary sources: Code of Hammurabi excerpts",
                    "Greek Philosophy: Plato's Republic (simplified version)"
                ]
            }
        }

    def validate_study_guide_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a study guide using Tikal's comprehensive validation system.
        
        Args:
            content_data: Dictionary containing study guide and outline data
            
        Returns:
            Dictionary with validation results and recommendations
        """
        logger.info("Starting comprehensive study guide validation for high school level")
        
        try:
            # Parse the content into Pydantic models
            outline = ContentOutline(**content_data["content_outline"])
            study_guide = StudyGuide(**content_data["study_guide"])
            
            # Create GeneratedContent object for comprehensive validation
            generated_content = GeneratedContent(
                content_outline=outline,
                study_guide=study_guide
            )
            
            # Run comprehensive validation
            validation_report = self.comprehensive_validator.validate_content_pipeline(
                generated_content=generated_content,
                target_format="study_guide"
            )
            
            # Calculate quality metrics specific to the study guide text
            study_guide_text = study_guide.detailed_content
            outline_text = f"{outline.title} {outline.overview}"
            
            quality_metrics = self.quality_metrics.evaluate_content(
                content=study_guide_text,
                syllabus_text=outline_text,
                target_format="study_guide",
                metadata={"education_level": "high_school"}
            )
            
            # Validate against high school standards
            high_school_validation = self._validate_high_school_standards(study_guide)
            
            # Compile comprehensive results
            results = {
                "overall_quality": {
                    "passed": validation_report.overall_passed,
                    "score": validation_report.overall_score,
                    "grade": self._calculate_grade(validation_report.overall_score)
                },
                "validation_stages": [
                    {
                        "stage": stage.stage_name,
                        "passed": stage.passed,
                        "score": stage.score,
                        "issues": stage.issues_found,
                        "suggestion": stage.improvement_suggestion
                    }
                    for stage in validation_report.stage_results
                ],
                "quality_metrics": {
                    "readability_score": quality_metrics.readability_score,
                    "complexity_score": quality_metrics.complexity_score,
                    "engagement_score": quality_metrics.engagement_score,
                    "overall_score": quality_metrics.overall_score
                },
                "high_school_standards": high_school_validation,
                "actionable_feedback": validation_report.actionable_feedback,
                "refinement_suggestions": validation_report.refinement_prompts,
                "summary": self._generate_validation_summary(validation_report, quality_metrics, high_school_validation)
            }
            
            logger.info(f"Validation completed. Overall score: {validation_report.overall_score:.2f}")
            return results
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {
                "error": str(e),
                "overall_quality": {"passed": False, "score": 0.0, "grade": "F"}
            }
    
    def _validate_high_school_standards(self, study_guide: StudyGuide) -> Dict[str, Any]:
        """Validate study guide against high school educational standards."""
        validation_results = {
            "passed": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check reading level appropriateness (should be grades 9-12)
        content_length = len(study_guide.detailed_content)
        if content_length < 1000:
            validation_results["issues"].append("Content too brief for high school level")
            validation_results["passed"] = False
        elif content_length > 5000:
            validation_results["recommendations"].append("Consider breaking into smaller sections for better readability")
        
        # Check for critical thinking elements
        critical_thinking_indicators = [
            "compare", "contrast", "analyze", "evaluate", "why", "how", 
            "explain", "examine", "consider", "argument", "evidence"
        ]
        
        content_lower = study_guide.detailed_content.lower()
        found_indicators = [word for word in critical_thinking_indicators if word in content_lower]
        
        if len(found_indicators) < 3:
            validation_results["issues"].append("Insufficient critical thinking elements for high school level")
            validation_results["passed"] = False
        
        # Check for vocabulary appropriateness
        if len(study_guide.key_concepts) < 8:
            validation_results["issues"].append("Too few key concepts for comprehensive high school study guide")
            validation_results["passed"] = False
        
        # Check for connections to modern world
        modern_connections = ["today", "modern", "current", "contemporary", "influence", "legacy"]
        found_connections = [word for word in modern_connections if word in content_lower]
        
        if len(found_connections) < 2:
            validation_results["recommendations"].append("Add more connections to modern world for relevance")
        
        return validation_results
    
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
    
    def _generate_validation_summary(self, validation_report, quality_metrics, high_school_validation) -> str:
        """Generate a human-readable summary of the validation results."""
        grade = self._calculate_grade(validation_report.overall_score)
        
        summary = f"""
TIKAL STUDY GUIDE QUALITY VALIDATION REPORT
==========================================

Overall Assessment: {grade} ({validation_report.overall_score:.2f}/1.0)
High School Standards: {'PASSED' if high_school_validation['passed'] else 'NEEDS IMPROVEMENT'}

Key Metrics:
- Readability Score: {quality_metrics.readability_score:.2f}
- Content Structure: {quality_metrics.complexity_score:.2f}  
- Student Engagement: {quality_metrics.engagement_score:.2f}

Validation Status: {'PASSED' if validation_report.overall_passed else 'FAILED'}

Major Strengths:
{self._list_strengths(validation_report)}

Areas for Improvement:
{self._list_improvements(validation_report.actionable_feedback)}

High School Standards Review:
{self._format_high_school_feedback(high_school_validation)}
        """
        
        return summary.strip()
    
    def _list_strengths(self, validation_report) -> str:
        """Identify and list the strengths of the study guide."""
        strengths = []
        
        for stage in validation_report.stage_results:
            if stage.passed and stage.score > 0.8:
                strengths.append(f"- Excellent {stage.stage_name.lower()}")
        
        if not strengths:
            strengths = ["- Basic structural requirements met"]
            
        return "\n".join(strengths)
    
    def _list_improvements(self, feedback_list) -> str:
        """Format improvement suggestions."""
        if not feedback_list:
            return "- No major improvements needed"
        
        return "\n".join([f"- {feedback}" for feedback in feedback_list[:5]])
    
    def _format_high_school_feedback(self, high_school_validation) -> str:
        """Format high school specific feedback."""
        feedback = []
        
        if high_school_validation["issues"]:
            feedback.extend([f"⚠️  {issue}" for issue in high_school_validation["issues"]])
        
        if high_school_validation["recommendations"]:
            feedback.extend([f"💡 {rec}" for rec in high_school_validation["recommendations"]])
        
        if not feedback:
            feedback = ["✅ Meets high school educational standards"]
            
        return "\n".join(feedback)


def main():
    """Main function to run the study guide validation."""
    parser = argparse.ArgumentParser(
        description="Validate study guide quality using Tikal's validation system"
    )
    parser.add_argument(
        "--input-file", 
        type=str, 
        help="JSON file containing study guide data"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true", 
        help="Run in interactive mode with sample data"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="validation_report.json",
        help="Output file for validation report"
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = StudyGuideValidator()
    
    # Get input data
    if args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                content_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load input file: {e}")
            sys.exit(1)
    else:
        logger.info("Using sample high school study guide for validation")
        content_data = validator.create_sample_study_guide()
    
    # Run validation
    print("\n🔍 TIKAL STUDY GUIDE QUALITY VALIDATION")
    print("=" * 50)
    print("Validating study guide for high school educational standards...")
    
    results = validator.validate_study_guide_quality(content_data)
    
    if "error" in results:
        print(f"❌ Validation failed: {results['error']}")
        sys.exit(1)
    
    # Display results
    print(results["summary"])
    
    # Save detailed results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed validation report saved to: {args.output}")
    
    # Exit with appropriate code
    if results["overall_quality"]["passed"]:
        print("\n✅ Study guide validation PASSED")
        sys.exit(0)
    else:
        print("\n❌ Study guide validation FAILED")
        print("Review the feedback above and make improvements before resubmitting.")
        sys.exit(1)


if __name__ == "__main__":
    main()