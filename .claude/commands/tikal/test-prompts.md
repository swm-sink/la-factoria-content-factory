---
name: /tikal-test-prompts
description: "Test and validate Tikal's prompt templates for quality and effectiveness"
usage: /tikal-test-prompts [template-name] [test-scenario]
category: tikal-commands
tools: Read, Write, Grep
---

# Tikal Prompt Testing Framework

I'll test and validate Tikal's prompt templates to ensure they produce high-quality educational content consistently.

## Your Task
Test prompt template: $ARGUMENTS

## Testing Framework

### 1. **Template Functionality Tests**
Verify core template mechanics:
- **Parameter Substitution**: All variables properly replaced
- **Format Compliance**: Output matches specified JSON schema
- **Constraint Adherence**: Length limits and requirements met
- **Error Handling**: Graceful handling of edge cases

### 2. **Educational Quality Tests**
Validate educational effectiveness:
- **Learning Objective Alignment**: Content supports stated goals
- **Audience Appropriateness**: Language and complexity match level
- **Pedagogical Structure**: Follows educational best practices
- **Engagement Factors**: Interactive and compelling content

### 3. **Consistency Tests**
Check cross-template consistency:
- **Quality Standards**: Similar requirements across templates
- **Output Formats**: Consistent structure patterns
- **Terminology**: Unified vocabulary usage
- **Style Guidelines**: Coherent voice and tone

### 4. **Performance Tests**
Measure efficiency metrics:
- **Token Usage**: Actual vs estimated token counts
- **Generation Time**: Response latency measurements
- **Success Rate**: Percentage of valid outputs
- **Quality Scores**: Average content quality ratings

## Test Scenarios

### Scenario 1: Basic Functionality
```
Input: Standard educational topic with all parameters
Expected: Valid JSON output meeting all constraints
Validation: Schema compliance, field completeness
```

### Scenario 2: Edge Cases
```
Input: Minimal parameters, complex topics, special characters
Expected: Graceful handling, appropriate defaults
Validation: Error-free output, reasonable content
```

### Scenario 3: Educational Standards
```
Input: Various audience levels (elementary to university)
Expected: Appropriate complexity and language
Validation: Readability scores, vocabulary analysis
```

### Scenario 4: Quality Benchmarks
```
Input: Diverse subject matters
Expected: Consistent high-quality output
Validation: Quality scores >0.80, engagement metrics
```

## Test Execution Process

### Step 1: Template Analysis
- Load template and identify parameters
- Review requirements and constraints
- Note quality criteria and standards

### Step 2: Test Case Generation
- Create representative test inputs
- Include edge cases and variations
- Cover all audience levels
- Test different subject domains

### Step 3: Output Validation
- Verify JSON structure validity
- Check constraint compliance
- Assess educational quality
- Measure performance metrics

### Step 4: Results Compilation
- Success/failure rates
- Quality score distribution
- Common issues identified
- Improvement recommendations

## Test Report Format

### Summary Metrics
```json
{
  "template": "study-guide-optimized",
  "tests_run": 20,
  "success_rate": 0.95,
  "average_quality": 0.87,
  "average_tokens": 650,
  "issues_found": 2
}
```

### Detailed Results
```json
{
  "test_cases": [
    {
      "scenario": "high_school_biology",
      "status": "passed",
      "quality_score": 0.89,
      "tokens_used": 680,
      "validation": {
        "schema_valid": true,
        "constraints_met": true,
        "educational_value": 0.91
      }
    }
  ],
  "issues": [
    {
      "severity": "minor",
      "description": "Summary sometimes exceeds 1000 chars",
      "frequency": "10%",
      "recommendation": "Adjust summary generation instructions"
    }
  ]
}
```

### Quality Analysis
- **Strengths**: Consistent structure, clear language
- **Weaknesses**: Occasional length violations
- **Opportunities**: Enhanced example generation
- **Recommendations**: Minor instruction refinements

## Automated Test Suite

### Unit Tests
- Parameter substitution accuracy
- Format specification compliance
- Constraint validation logic
- Default value handling

### Integration Tests
- Multi-template workflows
- Context sharing between templates
- Quality score calculations
- Performance under load

### Regression Tests
- Quality maintenance over time
- Consistency across updates
- Backward compatibility
- Performance stability

## Continuous Improvement

### Feedback Loop
1. Collect test results
2. Identify patterns in failures
3. Update templates based on findings
4. Re-test to verify improvements
5. Document changes and impacts

### Quality Metrics Tracking
- Average quality scores over time
- Success rate trends
- Token efficiency improvements
- User satisfaction correlation

This testing framework ensures Tikal's prompts maintain high standards and continuously improve based on empirical data.