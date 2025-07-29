# Prompt Validation Component

## Validation Framework for Tikal Prompts

### Schema Validation Rules

#### Required Fields by Content Type

**Study Guide**
- title: string (10-200 chars)
- overview: string (100-1000 chars)
- key_concepts: array[string] (5-20 items)
- detailed_content: string (500-8000 chars)
- summary: string (100-1000 chars)
- recommended_reading: array[string] (optional)

**Flashcards**
- title: string (10-200 chars)
- description: string (50-500 chars)
- flashcards: array[object] (5-50 items)
  - id: string
  - question: string (10-200 chars)
  - answer: string (10-300 chars)
  - difficulty: enum[easy, medium, hard]
  - category: string
- study_tips: array[string] (optional)

**Master Outline**
- title: string (10-200 chars)
- description: string (50-500 chars)
- sections: array[object] (3-10 items)
  - title: string
  - duration: integer
  - learning_objectives: array[string]
  - key_points: array[string] (2-5 items)
- total_duration: integer
- overall_objectives: array[string] (3-10 items)

**Podcast Script**
- title: string (10-200 chars)
- episode_summary: string (100-500 chars)
- introduction: object
  - hook: string
  - preview: string
  - duration_seconds: integer
- segments: array[object] (3-6 items)
- conclusion: object
- total_duration_seconds: integer

### Quality Validation Criteria

#### Content Quality Metrics
1. **Readability Score**
   - Elementary: 3rd-5th grade level
   - Middle School: 6th-8th grade level
   - High School: 9th-12th grade level
   - University: 13th+ grade level

2. **Educational Alignment**
   - Learning objectives clearly stated
   - Content supports objectives
   - Assessment opportunities included
   - Progressive complexity

3. **Engagement Factors**
   - Variety in presentation
   - Interactive elements
   - Real-world applications
   - Clear relevance

#### Technical Validation
1. **JSON Validity**
   - Proper structure
   - Valid data types
   - No missing required fields
   - Proper character encoding

2. **Constraint Compliance**
   - Length limits respected
   - Array size constraints met
   - Enum values valid
   - Format specifications followed

### Validation Process

#### Pre-Generation Validation
1. Template parameter verification
2. Context data completeness
3. Audience level appropriateness
4. Educational goal clarity

#### Post-Generation Validation
1. Schema compliance check
2. Content quality assessment
3. Educational standards verification
4. Performance metrics collection

### Error Classifications

#### Critical Errors (Fail)
- Missing required fields
- Invalid JSON structure
- Schema type mismatches
- Content below minimum length

#### Major Issues (Review)
- Quality score below 0.70
- Readability mismatch
- Learning objectives unclear
- Inadequate examples

#### Minor Issues (Warning)
- Slightly over length limits
- Formatting inconsistencies
- Optional field suggestions
- Enhancement opportunities

### Validation Test Cases

#### Happy Path Tests
- Standard input → Valid output
- All parameters → Complete content
- Clear requirements → Quality result

#### Edge Case Tests
- Minimal input → Acceptable output
- Complex topics → Structured content
- Special characters → Proper handling
- Long content → Appropriate truncation

#### Negative Tests
- Missing parameters → Error handling
- Invalid values → Validation errors
- Conflicting requirements → Resolution

### Quality Benchmarks

#### Minimum Acceptable Scores
- Overall Quality: 0.70
- Educational Value: 0.75
- Readability Match: 0.80
- Structure Score: 0.70
- Engagement Level: 0.65

#### Target Scores
- Overall Quality: 0.85+
- Educational Value: 0.90+
- Readability Match: 0.95+
- Structure Score: 0.85+
- Engagement Level: 0.80+

### Continuous Validation

#### Metrics to Track
- Success rate per template
- Average quality scores
- Common failure patterns
- Performance trends

#### Improvement Triggers
- Success rate <90%
- Quality score decline
- Repeated failures
- User complaints

This validation component ensures all Tikal prompts meet high standards for educational content generation.