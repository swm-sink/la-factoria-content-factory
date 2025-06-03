# Strict JSON Output Instructions

**Critical Requirements for All Content Generation Prompts**

## JSON Output Format Requirements

1. **ONLY JSON**: Return valid JSON only. No markdown, no explanations, no code blocks.
2. **No Markdown Blocks**: Do not wrap JSON in ```json``` or ``` blocks.
3. **No Additional Text**: No introductory text, comments, or explanations.
4. **Valid JSON**: Must parse with standard JSON parsers.
5. **Complete Response**: Entire response must be valid JSON.

## Example of CORRECT Response:
```
{"title": "Introduction to AI", "overview": "Comprehensive course...", "main_topics": ["Machine Learning", "Neural Networks"]}
```

## Examples of INCORRECT Responses:
```
Here's the JSON:
{"title": "Introduction to AI"}

```json
{"title": "Introduction to AI"}
```

The content outline is:
{"title": "Introduction to AI"}
```

## Validation Requirements

- JSON must validate against the specified Pydantic model
- All required fields must be present
- Field types must match exactly
- String lengths must meet minimum/maximum requirements
- Lists must contain the specified number of items

## Error Prevention

- Double-check JSON syntax before responding
- Ensure all quotes are properly escaped
- Verify all brackets and braces are balanced
- Test field constraints (min/max lengths, required fields)
- Avoid special characters that might break JSON parsing

## Content Quality Standards

While maintaining strict JSON format:
- Provide meaningful, educational content
- Ensure content length meets minimum requirements
- Create engaging, well-structured material
- Maintain consistency with the provided syllabus/outline
- Use clear, professional language
