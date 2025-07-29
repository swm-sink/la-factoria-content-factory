---
name: /tikal-generate
description: "Generate educational content using Tikal's optimized prompts and context"
usage: /tikal-generate [content-type] [topic] [audience-level]
category: tikal-commands
tools: Read, Write, Grep, Glob
---

# Tikal Educational Content Generation

I'll generate high-quality educational content using Tikal's content generation pipeline with optimized prompts and educational standards.

## Your Task
Generate content for: $ARGUMENTS

## Context Integration
I'm loading Tikal's project context and educational standards to ensure content meets quality requirements...

## Content Generation Framework

### Supported Content Types
1. **master-outline** - Foundation structure with learning objectives
2. **study-guide** - Comprehensive educational content with key concepts  
3. **podcast-script** - Conversational format with speaker notes
4. **one-pager** - Concise summary with key takeaways
5. **detailed-reading** - In-depth educational material with examples
6. **faq-collection** - Question-answer pairs for common topics
7. **flashcards** - Term-definition pairs for memorization
8. **reading-questions** - Discussion questions for comprehension

### Generation Process

#### Step 1: Requirements Analysis
I'll analyze the generation request:
- **Content Type**: Determine format and structure requirements
- **Topic**: Understand subject matter and scope
- **Audience Level**: Set appropriate complexity and language
- **Learning Objectives**: Define educational goals
- **Context Requirements**: Gather necessary background information

#### Step 2: Educational Framework Application
Using Tikal's educational standards component:
- Apply age-appropriate content guidelines
- Structure using learning objectives framework
- Integrate pedagogical best practices
- Ensure inclusivity and accessibility
- Apply bias prevention measures

#### Step 3: Content Structure Planning
Based on content type specifications:
- Define section hierarchy and organization
- Plan content flow and transitions
- Identify key concepts and terminology
- Plan examples and interactive elements
- Design assessment opportunities

#### Step 4: Content Generation
Generate content following Tikal's quality standards:
- Use educational vocabulary appropriate for audience
- Include concrete examples and applications
- Integrate interactive elements where appropriate
- Maintain consistent tone and style
- Follow content type specific requirements

#### Step 5: Quality Validation
Apply Tikal's quality assessment framework:
- Validate educational value and learning alignment
- Check readability for target audience
- Assess structure and organization
- Verify factual accuracy
- Evaluate engagement level

## Example Generation Workflows

### Study Guide Generation
```
Input: /tikal-generate study-guide "Python Programming Basics" high-school

Process:
1. Analyze Python programming concepts for high school level
2. Structure content using educational best practices
3. Include key terms, examples, and practice exercises
4. Apply quality validation for educational value
5. Generate comprehensive study guide meeting Tikal standards
```

### Flashcards Generation
```
Input: /tikal-generate flashcards "World War II Timeline" middle-school

Process:
1. Identify key events and dates for middle school level
2. Create concise question-answer pairs
3. Ensure age-appropriate language and concepts
4. Validate for factual accuracy and clarity
5. Generate flashcard set with educational value assessment
```

## Quality Assurance Integration

### Automatic Quality Checks
- **Educational Standards Compliance**: Content meets age and level requirements
- **Learning Objectives Alignment**: Content supports stated educational goals
- **Readability Validation**: Language complexity matches target audience
- **Structure Assessment**: Content follows logical organization
- **Factual Accuracy Check**: Information is current and verifiable

### Quality Score Calculation
Using Tikal's weighted scoring algorithm:
```
Quality Score = (
  Educational Value × 0.30 +
  Readability Score × 0.25 +
  Structure Score × 0.20 +
  Factual Accuracy × 0.15 +
  Engagement Level × 0.10
)
```

### Quality Gates
Content must meet minimum thresholds:
- Overall Quality Score: ≥ 0.70
- Educational Value: ≥ 0.75
- Factual Accuracy: ≥ 0.85
- Schema Compliance: 100%

## Output Format

### Generated Content
The primary educational content in the requested format, structured according to Tikal's content type specifications.

### Quality Report
```json
{
  "content_type": "study_guide",
  "topic": "Python Programming Basics", 
  "audience_level": "high_school",
  "quality_score": 0.87,
  "educational_value": 0.89,
  "readability_score": 0.84,
  "meets_standards": true,
  "generation_metadata": {
    "word_count": 1250,
    "reading_time": "8 minutes",
    "complexity_level": "appropriate",
    "learning_objectives_covered": 5
  }
}
```

### Recommendations
- Suggestions for content enhancement
- Educational best practice improvements  
- Engagement optimization opportunities
- Assessment integration recommendations

This command provides comprehensive educational content generation using Tikal's quality standards and educational best practices.