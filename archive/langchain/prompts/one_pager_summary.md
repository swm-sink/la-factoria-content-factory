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

---
CRITICAL OUTPUT REQUIREMENTS:
1. Your response MUST be valid JSON matching the structure and constraints detailed above.
   Ensure all field names, types, and nesting are exactly as specified.
   Do not include any text before or after the JSON object.
   Do not wrap the JSON in markdown code blocks (e.g., ```json ... ```).

2. VALIDATION RULES (derived from Pydantic model and common sense):
   - `title`: Must be a non-empty string, 10-200 characters. Should align with the outline's title.
   - `executive_summary`: Must be a non-empty string, 100-500 characters.
   - `key_takeaways`: Must be a list of 3 to 7 non-empty strings, each at least 20 characters long.
   - `main_content`: Must be a non-empty string, 200-1500 characters. It should concisely summarize the Content Outline.
   - All textual content should be meaningful, well-written, concise, and directly relevant to the Content Outline.

3. QUALITY CHECKS (Before responding, internally verify these):
   ✓ All required fields (title, executive_summary, key_takeaways, main_content) are populated with valid data meeting length/count constraints.
   ✓ The summary's content directly and concisely reflects the provided Content Outline.
   ✓ Key takeaways are impactful and accurately represent core messages.
   ✓ The main content is a succinct yet comprehensive summary of the outline's sections.
---

Generate the JSON object now.
