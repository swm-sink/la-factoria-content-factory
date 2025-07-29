---
name: /tikal-validate-quality
description: "Comprehensive quality validation for Tikal's AI-generated educational content"
usage: /tikal-validate-quality [content-type] [quality-threshold]
category: tikal-commands
tools: Read, Write, Grep, Glob
---

# Tikal Content Quality Validation

I'll perform comprehensive quality validation on Tikal's AI-generated educational content using educational standards and best practices.

## Your Task
Validate content quality for: $ARGUMENTS

## Context Integration
Loading Tikal project context for educational content standards and quality requirements...

## Validation Framework

### 1. **Educational Content Standards**
I'll validate content against educational criteria:
- **Age Appropriateness**: Language complexity matches target audience
- **Learning Objectives**: Content aligns with stated educational goals
- **Pedagogical Structure**: Follows educational best practices
- **Factual Accuracy**: Information is current and verifiable
- **Inclusivity**: Content respects diverse perspectives and cultures

### 2. **Content Quality Metrics**
I'll assess using Tikal's quality framework:
- **Readability Score**: Flesch-Kincaid and ARI analysis
- **Engagement Level**: Interactive elements and compelling content
- **Structure Score**: Logical organization and flow
- **Completeness**: Covers required learning objectives
- **Consistency**: Maintains style and tone throughout

### 3. **Technical Validation**
I'll check technical requirements:
- **JSON Schema Compliance**: For structured content types
- **Field Requirements**: All required fields populated
- **Length Constraints**: Content meets specified limits
- **Format Adherence**: Follows content type specifications

### 4. **Quality Scoring Algorithm**
```
Overall Score = (
  Educational Value × 0.30 +
  Readability Score × 0.25 +
  Structure Score × 0.20 +
  Factual Accuracy × 0.15 +
  Engagement Level × 0.10
)
```

## Validation Process

### Step 1: Content Analysis
- Parse content structure and extract key elements
- Identify learning objectives and target audience
- Analyze content complexity and reading level

### Step 2: Educational Standards Check
- Verify age-appropriate language and concepts
- Validate learning objective alignment
- Check for pedagogical best practices
- Assess inclusivity and bias prevention

### Step 3: Quality Metrics Calculation
- Calculate readability scores using multiple algorithms
- Assess content structure and organization
- Evaluate engagement factors and interactivity
- Check factual accuracy against knowledge base

### Step 4: Technical Compliance
- Validate JSON schema compliance for structured content
- Check all required fields are properly populated
- Verify content length meets specifications
- Ensure format adherence for content type

### Step 5: Comprehensive Scoring
- Calculate individual metric scores
- Apply weighted scoring algorithm
- Generate overall quality score
- Identify improvement recommendations

## Output Format

### Quality Report
```json
{
  "overall_score": 0.85,
  "content_type": "study_guide",
  "target_audience": "high_school",
  "metrics": {
    "educational_value": 0.88,
    "readability_score": 0.82,
    "structure_score": 0.90,
    "factual_accuracy": 0.85,
    "engagement_level": 0.78
  },
  "compliance": {
    "schema_valid": true,
    "required_fields": "complete",
    "length_requirements": "within_limits"
  },
  "recommendations": [
    "Increase interactive elements for better engagement",
    "Add more concrete examples for complex concepts"
  ],
  "quality_gates": {
    "meets_threshold": true,
    "threshold_used": 0.80,
    "ready_for_publication": true
  }
}
```

## Improvement Recommendations
Based on validation results, I'll provide:
- Specific suggestions for content enhancement
- Educational best practice improvements
- Engagement optimization recommendations
- Structure and organization improvements
- Factual accuracy enhancement suggestions

## Quality Gates
I'll apply Tikal's quality thresholds:
- **Minimum Quality Score**: 0.70 (configurable)
- **Educational Value**: Must be ≥ 0.75
- **Factual Accuracy**: Must be ≥ 0.85
- **Schema Compliance**: Must be 100%
- **Required Fields**: Must be complete

Content must pass all quality gates before publication approval.