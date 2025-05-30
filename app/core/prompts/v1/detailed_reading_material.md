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

Generate the JSON object now.
