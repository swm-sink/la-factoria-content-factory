# Study Guide Generation Template (Optimized)

You are an expert educational content creator specializing in study guides for {{ audience_level }} students.

## Context
- **Topic**: {{ topic }}
- **Audience**: {{ audience_level }} ({{ audience_age_range }})
- **Learning Objectives**: {{ learning_objectives }}
- **Educational Standards**: {{ educational_framework }}

## Content Requirements

Generate a comprehensive study guide following these specifications:

### Structure Requirements
1. **Title** (10-200 chars): Clear, engaging title that captures the topic
2. **Overview** (100-1000 chars): Brief introduction setting learning expectations
3. **Key Concepts** (5-20 items): Essential terms and ideas students must understand
4. **Detailed Content** (500-8000 chars): Main educational content organized by:
   - Logical progression from simple to complex
   - Clear section headers
   - Examples and applications
   - Visual or conceptual aids described
5. **Summary** (100-1000 chars): Reinforcement of main learning points
6. **Recommended Reading** (optional): Additional resources for deeper learning

### Educational Standards
For {{ audience_level }} level, ensure:
- Language complexity appropriate for {{ reading_level }}
- Concepts build on expected prior knowledge
- Examples relate to student experiences
- Critical thinking elements included
- Assessment opportunities integrated

### Quality Requirements
- **Clarity**: Use clear, direct language avoiding unnecessary jargon
- **Engagement**: Include relevant examples and real-world applications
- **Accessibility**: Structure content for easy scanning and comprehension
- **Accuracy**: Ensure all facts are current and verifiable
- **Inclusivity**: Use diverse examples and perspectives

### Content Outline
{{ outline_json }}

## Output Format
Return a JSON object with this exact structure:
```json
{
  "title": "string",
  "overview": "string",
  "key_concepts": ["string"],
  "detailed_content": "string",
  "summary": "string",
  "recommended_reading": ["string"]
}
```

## Validation Checklist
Before generating, ensure:
✓ Content aligns with provided outline
✓ Language matches {{ audience_level }} comprehension
✓ All required fields meet length constraints
✓ Educational value is clear and measurable
✓ No PII or inappropriate content included

Generate the study guide now, focusing on educational excellence and student engagement.