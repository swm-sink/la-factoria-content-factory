You are an expert educational writer. Based on the provided Content Outline (in JSON format), generate a comprehensive Study Guide.
The guide should be well-structured, informative, and help learners understand the material.

Content Outline:
---
{{ outline_json }}
---

Your output MUST be a single JSON object that strictly adheres to the following structure and constraints,
matching the 'StudyGuide' Pydantic model.

JSON Structure Example:
```json
{
  "title": "Study Guide Title (matches outline, 10-200 chars)",
  "overview": "Overview of the study guide (100-1000 chars).",
  "key_concepts": ["Concept 1", "Concept 2", "Concept 3", "Concept 4", "Concept 5"],
  "detailed_content": "Comprehensive content for the study guide (500-8000 chars). Structure this based on the outline sections.",
  "summary": "Concise summary of the guide (100-1000 chars).",
  "recommended_reading": ["Optional reading 1", "Optional reading 2"]
}
```

Detailed Constraints (based on Pydantic model 'StudyGuide'):
- `title`: string, 10-200 characters. This should ideally match the title from the input Content Outline.
- `overview`: string, 100-1000 characters. Provide a brief introduction to what the study guide covers.
- `key_concepts`: list of strings, 5 to 20 key concepts. These should be important terms or ideas from the content.
- `detailed_content`: string, 500-8000 characters. This section should elaborate on the topics/sections from the input Content Outline, providing explanations, examples, and details suitable for a study guide.
- `summary`: string, 100-1000 characters. A concise recap of the main points of the study guide.
- `recommended_reading`: list of strings, optional. Suggest further readings or resources.

Ensure the content is educational, clear, and well-organized.

IMPORTANT: Do not include any Personally Identifiable Information (PII) such as real names (unless they are widely known public figures relevant to the content), addresses, phone numbers, email addresses, or any other private data in the generated content.

Generate the JSON object now.
