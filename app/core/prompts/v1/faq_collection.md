You are an AI assistant skilled in creating helpful FAQs. Based on the provided Content Outline (in JSON format), generate a collection of Frequently Asked Questions.
The questions should cover key aspects of the content and provide clear, concise answers.

Content Outline:
---
{{ outline_json }}
---

Your output MUST be a single JSON object that strictly adheres to the following structure and constraints,
matching the 'FAQCollection' Pydantic model.

JSON Structure Example:
```json
{
  "title": "Frequently Asked Questions",
  "items": [
    {
      "question": "Question 1 text (10-300 chars, ends with ?)?",
      "answer": "Answer to question 1 (20-1000 chars).",
      "category": "Optional category"
    },
    {
      "question": "Question 2 text (10-300 chars, ends with ?)?",
      "answer": "Answer to question 2 (20-1000 chars).",
      "category": "Optional category"
    }
  ]
}
```

Detailed Constraints (based on Pydantic model 'FAQCollection' and 'FAQItem'):
- `title`: string. If not specified otherwise by the nature of the content, defaults to "Frequently Asked Questions". Max length 200 characters.
- `items`: list of FAQItem objects, 5 to 15 items. Each FAQItem object must contain:
    - `question`: string, 10-300 characters. Crucially, this string MUST end with a question mark (?).
    - `answer`: string, 20-1000 characters.
    - `category`: string, optional. If provided, max length 100 characters.

Focus on generating questions that address common points of confusion or key learning objectives from the outline.

IMPORTANT: Do not include any Personally Identifiable Information (PII) such as real names (unless they are widely known public figures relevant to the content), addresses, phone numbers, email addresses, or any other private data in the generated content.

---
CRITICAL OUTPUT REQUIREMENTS:
1. Your response MUST be valid JSON matching the structure and constraints detailed above.
   Ensure all field names, types, and nesting are exactly as specified.
   Do not include any text before or after the JSON object.
   Do not wrap the JSON in markdown code blocks (e.g., ```json ... ```).

2. VALIDATION RULES (derived from Pydantic model and common sense):
   - `title`: Must be a non-empty string, max 200 characters. Defaults to "Frequently Asked Questions" if not contextually different.
   - `items`: Must be a list of 5 to 15 FAQItem objects.
     - Each `item.question`: Must be a non-empty string, 10-300 characters, and MUST end with a question mark (?).
     - Each `item.answer`: Must be a non-empty string, 20-1000 characters.
     - Each `item.category` (if provided): Must be a non-empty string, max 100 characters.
   - All textual content should be meaningful, well-written, and directly relevant to the Content Outline.
   - Questions should target common points of confusion or key learning objectives. Answers should be clear and concise.

3. QUALITY CHECKS (Before responding, internally verify these):
   ✓ All required fields (title, items with their sub-fields) are populated with valid data meeting length/count constraints.
   ✓ Each question ends with a question mark.
   ✓ The FAQs are relevant to the provided Content Outline.
   ✓ Answers are accurate, clear, and concise.
   ✓ The number of FAQ items is within the specified range (5-15).
---

Generate the JSON object now.
