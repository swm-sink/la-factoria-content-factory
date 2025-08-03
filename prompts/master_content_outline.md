You are an expert instructional designer. Analyze the following syllabus text and generate a comprehensive Content Outline.
The Content Outline will serve as the foundation for generating various educational materials.

Syllabus Text:
---
{syllabus_text}
---

Your output MUST be a single JSON object that strictly adheres to the following structure and constraints.
Pay close attention to field descriptions, types, and length/count constraints mentioned in the example and the detailed constraints list.

JSON Structure Example:
```json
{{
  "title": "Example Title (10-200 chars)",
  "overview": "Example overview of the content (50-1000 chars).",
  "learning_objectives": [
    "Objective 1 (min 15 chars)",
    "Objective 2 (min 15 chars)",
    "Objective 3 (min 15 chars)"
  ],
  "sections": [
    {{
      "section_number": 1,
      "title": "Section 1 Title (5-200 chars)",
      "description": "Detailed description of section 1 (20-1000 chars).",
      "estimated_duration_minutes": 10.5,
      "key_points": [
        "Key point 1.1 (min 10 chars)",
        "Key point 1.2 (min 10 chars)"
      ]
    }},
    {{
      "section_number": 2,
      "title": "Section 2 Title (5-200 chars)",
      "description": "Detailed description of section 2 (20-1000 chars).",
      "estimated_duration_minutes": 15.0,
      "key_points": [
        "Key point 2.1 (min 10 chars)"
      ]
    }}
  ],
  "estimated_total_duration": 25.5,
  "target_audience": "e.g., University Students",
  "difficulty_level": "intermediate"
}}
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

---
CRITICAL OUTPUT REQUIREMENTS:
1. Your response MUST be valid JSON matching the structure and constraints detailed above.
   Ensure all field names, types, and nesting are exactly as specified.
   Do not include any text before or after the JSON object.
   Do not wrap the JSON in markdown code blocks (e.g., ```json ... ```).

2. VALIDATION RULES (derived from Pydantic model and common sense):
   - `title`: Must be a non-empty string, 10-200 characters.
   - `overview`: Must be a non-empty string, 50-1000 characters.
   - `learning_objectives`: Must be a list of 3 to 10 non-empty strings, each at least 15 characters.
   - `sections`: Must be a list of 3 to 15 section objects.
     - Each `section.title`: Must be a non-empty string, 5-200 characters.
     - Each `section.description`: Must be a non-empty string, 20-1000 characters.
     - Each `section.key_points` (if provided): Must be a list of non-empty strings, each at least 10 characters.
   - All textual content should be meaningful, well-written, and directly relevant to the syllabus.
   - Content must be factually accurate and educationally sound based on the provided syllabus.

3. QUALITY CHECKS (Before responding, internally verify these):
   ✓ All required fields (title, overview, learning_objectives, sections with their required sub-fields) are populated with valid data.
   ✓ Content is specific to the syllabus (no generic placeholders or irrelevant information).
   ✓ Language is clear, concise, and professional.
   ✓ The number of learning objectives and sections falls within the specified ranges.
   ✓ `section_number` is sequential and starts from 1.
   ✓ `estimated_total_duration` (if provided) aligns with the sum of `estimated_duration_minutes` in sections.
---

Generate the JSON object now.
