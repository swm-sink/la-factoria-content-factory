You are an AI assistant skilled in formulating thought-provoking questions. Based on the provided Content Outline (in JSON format), generate a list of Reading Guide Questions.
These questions should encourage critical thinking and deeper understanding of the material.

Content Outline:
---
{{ outline_json }}
---

Your output MUST be a single JSON object that strictly adheres to the following structure and constraints,
matching the 'ReadingGuideQuestions' Pydantic model.

JSON Structure Example:
```json
{
  "title": "Reading Guide Questions",
  "questions": [
    "Question 1 about the content (min 15 chars, ends with ?)?",
    "Question 2 exploring a key theme (min 15 chars, ends with ?)?",
    "Question 3 prompting critical analysis (min 15 chars, ends with ?)?"
  ]
}
```

Detailed Constraints (based on Pydantic model 'ReadingGuideQuestions'):
- `title`: string. If not specified otherwise, defaults to "Reading Guide Questions". Max length 200 characters.
- `questions`: list of strings, 5 to 15 questions. Each question must be:
    - At least 15 characters long.
    - End with a question mark (?).

Focus on questions that probe understanding of the outline's sections, key points, and overall learning objectives.

IMPORTANT: Do not include any Personally Identifiable Information (PII) such as real names (unless they are widely known public figures relevant to the content), addresses, phone numbers, email addresses, or any other private data in the generated content.

---
CRITICAL OUTPUT REQUIREMENTS:
1. Your response MUST be valid JSON matching the structure and constraints detailed above.
   Ensure all field names, types, and nesting are exactly as specified.
   Do not include any text before or after the JSON object.
   Do not wrap the JSON in markdown code blocks (e.g., ```json ... ```).

2. VALIDATION RULES (derived from Pydantic model and common sense):
   - `title`: Must be a non-empty string, max 200 characters. Defaults to "Reading Guide Questions" if not contextually different.
   - `questions`: Must be a list of 5 to 15 non-empty strings.
     - Each question: Must be at least 15 characters long and MUST end with a question mark (?).
   - All questions should be meaningful, well-formulated, and directly relevant to the Content Outline.
   - Questions should encourage critical thinking and deeper understanding.

3. QUALITY CHECKS (Before responding, internally verify these):
   ✓ All required fields (title, questions) are populated with valid data meeting length/count constraints.
   ✓ Each question is a non-empty string, at least 15 characters long, and ends with a question mark.
   ✓ The questions are relevant to the provided Content Outline, probing understanding of its sections and key points.
   ✓ The number of questions is within the specified range (5-15).
---

Generate the JSON object now.
