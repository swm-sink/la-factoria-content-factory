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

Generate the JSON object now.
