You are an expert subject matter author. Based on the provided Content Outline (in JSON format), generate Detailed Reading Material.
The material should be comprehensive, well-structured, and suitable for in-depth study.

Content Outline:
---
{{ outline_json }}
---

Your output MUST be a single JSON object that strictly adheres to the following structure and constraints,
matching the 'DetailedReadingMaterial' Pydantic model. The 'sections' in your output should directly correspond to the sections in the input Content Outline.

JSON Structure Example:
```json
{
  "title": "Reading Material Title (matches outline, 10-200 chars)",
  "introduction": "Introduction to the material (200-1000 chars).",
  "sections": [
    {
      "title": "Section 1 Title (min 10 chars, matches outline section title)",
      "content": "Detailed content for section 1 (min 200 chars, elaborates on outline section description and key points)."
    },
    {
      "title": "Section 2 Title (min 10 chars, matches outline section title)",
      "content": "Detailed content for section 2 (min 200 chars, elaborates on outline section description and key points)."
    }
  ],
  "conclusion": "Conclusion for the material (200-1000 chars).",
  "references": ["Optional reference 1", "Optional reference 2"]
}
```

Detailed Constraints (based on Pydantic model 'DetailedReadingMaterial'):
- `title`: string, 10-200 characters. This should ideally match the title from the input Content Outline.
- `introduction`: string, 200-1000 characters. Provide a thorough introduction to the subject matter.
- `sections`: list of section objects, 3 to 10 sections. Each section object must contain:
    - `title`: string, minimum 10 characters. This title should correspond to a section title from the input Content Outline.
    - `content`: string, minimum 200 characters. This content should expand significantly on the corresponding section's description and key points from the input Content Outline, providing detailed explanations, examples, and depth.
- `conclusion`: string, 200-1000 characters. A comprehensive conclusion summarizing the material.
- `references`: list of strings, optional. Cite any sources or further reading.

Ensure the material is detailed, accurate, and academically appropriate.

IMPORTANT: Do not include any Personally Identifiable Information (PII) such as real names (unless they are widely known public figures relevant to the content), addresses, phone numbers, email addresses, or any other private data in the generated content.

---
CRITICAL OUTPUT REQUIREMENTS:
1. Your response MUST be valid JSON matching the structure and constraints detailed above.
   Ensure all field names, types, and nesting are exactly as specified.
   Do not include any text before or after the JSON object.
   Do not wrap the JSON in markdown code blocks (e.g., ```json ... ```).

2. VALIDATION RULES (derived from Pydantic model and common sense):
   - `title`: Must be a non-empty string, 10-200 characters. Should align with the outline's title.
   - `introduction`: Must be a non-empty string, 200-1000 characters.
   - `sections`: Must be a list of 3 to 10 section objects.
     - Each `section.title`: Must be a non-empty string, at least 10 characters, and correspond to a title from the input Content Outline.
     - Each `section.content`: Must be a non-empty string, at least 200 characters, providing substantial detail.
   - `conclusion`: Must be a non-empty string, 200-1000 characters.
   - All textual content should be meaningful, well-written, detailed, accurate, and directly relevant to the Content Outline.

3. QUALITY CHECKS (Before responding, internally verify these):
   ✓ All required fields (title, introduction, sections with their sub-fields, conclusion) are populated with valid data meeting length/count constraints.
   ✓ The reading material's content directly and comprehensively expands upon the provided Content Outline.
   ✓ Each section in the output corresponds to a section in the input outline and elaborates on its description and key points.
   ✓ The content is academically appropriate, detailed, and accurate.
   ✓ `references` (if provided) are relevant.
---

Generate the JSON object now.
