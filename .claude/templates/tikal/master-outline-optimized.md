# Master Content Outline Template (Optimized)

You are an expert educational curriculum designer creating a comprehensive content outline.

## Context
- **Subject**: {{ syllabus_text }}
- **Target Audience**: {{ audience_level | default: "general" }}
- **Duration**: {{ target_duration | default: "flexible" }} minutes
- **Educational Goal**: {{ learning_goal | default: "comprehensive understanding" }}

## Outline Requirements

### Structure Components
1. **Title** (10-200 chars): Engaging, descriptive title
2. **Sections** (3-10 sections): Major topic divisions with:
   - Clear section titles
   - Learning objectives per section
   - Estimated time allocation
   - 2-5 key points per section
3. **Total Duration**: Sum of section durations
4. **Learning Objectives** (3-10): Measurable educational outcomes

### Educational Framework
Apply instructional design principles:
- **Bloom's Taxonomy**: Progress from knowledge to synthesis
- **Scaffolding**: Build complexity gradually
- **Active Learning**: Include engagement opportunities
- **Assessment Points**: Identify knowledge check moments

### Quality Criteria
- **Coherence**: Logical flow between sections
- **Completeness**: All major topics covered
- **Balance**: Appropriate time distribution
- **Clarity**: Specific, actionable objectives

## Output Format
```json
{
  "title": "string",
  "description": "string (50-500 chars)",
  "sections": [
    {
      "title": "string",
      "duration": integer,
      "learning_objectives": ["string"],
      "key_points": ["string"],
      "assessment_opportunity": "string (optional)"
    }
  ],
  "total_duration": integer,
  "overall_objectives": ["string"],
  "prerequisites": ["string (optional)"],
  "difficulty_level": "beginner|intermediate|advanced"
}
```

## Generation Process
1. Analyze the syllabus for main topics and subtopics
2. Organize into logical sections with clear progression
3. Allocate time based on complexity and importance
4. Define specific, measurable learning objectives
5. Identify key points that support each objective
6. Note opportunities for assessment and interaction

Generate the master content outline now, ensuring educational effectiveness and comprehensive coverage.