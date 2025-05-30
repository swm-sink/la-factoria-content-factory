You are an expert instructional designer. Analyze the following syllabus text and generate a comprehensive Content Outline.
The Content Outline will serve as the foundation for generating various educational materials.

Syllabus Text:
---
{{ syllabus_text }}
---

Your output MUST be a single JSON object that strictly adheres to the following structure and constraints.
Pay close attention to field descriptions, types, and length/count constraints mentioned in the example and the detailed constraints list.

JSON Structure Example:
```json
{
  "title": "Example Title (10-200 chars)",
  "overview": "Example overview of the content (50-1000 chars).",
  "learning_objectives": [
    "Objective 1 (min 15 chars)",
    "Objective 2 (min 15 chars)",
    "Objective 3 (min 15 chars)"
  ],
  "sections": [
    {
      "section_number": 1,
      "title": "Section 1 Title (5-200 chars)",
      "description": "Detailed description of section 1 (20-1000 chars).",
      "estimated_duration_minutes": 10.5,
      "key_points": [
        "Key point 1.1 (min 10 chars)",
        "Key point 1.2 (min 10 chars)"
      ]
    },
    {
      "section_number": 2,
      "title": "Section 2 Title (5-200 chars)",
      "description": "Detailed description of section 2 (20-1000 chars).",
      "estimated_duration_minutes": 15.0,
      "key_points": [
        "Key point 2.1 (min 10 chars)"
      ]
    }
  ],
  "estimated_total_duration": 25.5,
  "target_audience": "e.g., University Students",
  "difficulty_level": "intermediate"
}
```

Detailed Constraints (based on Pydantic model 'ContentOutline'):
- `title`: string, 10-200 characters.
- `overview`: string, 50-1000 characters.
- `learning_objectives`: list of strings, 3 to 10 objectives, each objective minimum 15 characters.
- `sections`: list of section objects, 3 to 15 sections in total. Each section object must contain:
    - `section_number`: integer, starting from 1 and incrementing sequentially.
    - `title`: string, 5-200 characters.
    - `description`: string, 20-1000 characters.
    - `estimated_duration_minutes`: float, optional. If provided, must be a positive number.
    - `key_points`: list of strings, 0 to 10 key points, each key point minimum 10 characters if provided.
- `estimated_total_duration`: float, optional. If provided, must be a positive number. This should ideally be the sum of section durations if they are provided.
- `target_audience`: string, optional, 5-100 characters if provided.
- `difficulty_level`: string, optional. If provided, must be one of 'beginner', 'intermediate', 'advanced'.

IMPORTANT: Do not include any Personally Identifiable Information (PII) such as real names (unless they are widely known public figures relevant to the content), addresses, phone numbers, email addresses, or any other private data in the generated content.

Generate the JSON object now.
