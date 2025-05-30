You are an expert technical writer. Based on the provided Content Outline (in JSON format), generate a concise One-Pager Summary.
The summary must capture the essence of the content in a brief format.

Content Outline:
---
{{ outline_json }}
---

Your output MUST be a single JSON object that strictly adheres to the following structure and constraints,
matching the 'OnePagerSummary' Pydantic model.

JSON Structure Example:
```json
{
  "title": "One-Pager Title (matches outline, 10-200 chars)",
  "executive_summary": "Brief executive summary (100-500 chars).",
  "key_takeaways": [
    "Takeaway 1 (min 20 chars)",
    "Takeaway 2 (min 20 chars)",
    "Takeaway 3 (min 20 chars)"
  ],
  "main_content": "Concise main content of the summary (200-1500 chars). Summarize sections from the outline."
}
```

Detailed Constraints (based on Pydantic model 'OnePagerSummary'):
- `title`: string, 10-200 characters. This should ideally match the title from the input Content Outline.
- `executive_summary`: string, 100-500 characters. A very brief overview of the entire content.
- `key_takeaways`: list of strings, 3 to 7 items. Each takeaway must be at least 20 characters long.
- `main_content`: string, 200-1500 characters. This section should briefly summarize the key information from the input Content Outline, touching upon its main sections.

IMPORTANT: Do not include any Personally Identifiable Information (PII) such as real names (unless they are widely known public figures relevant to the content), addresses, phone numbers, email addresses, or any other private data in the generated content.

Ensure the summary is highly condensed and impactful.
Generate the JSON object now.
