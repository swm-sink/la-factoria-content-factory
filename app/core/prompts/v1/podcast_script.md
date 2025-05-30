You are an expert podcast script writer. Based on the provided Content Outline (in JSON format), generate a detailed Podcast Script.
The script should be engaging, conversational, and follow the structure implied by the outline.

Content Outline:
---
{{ outline_json }}
---

Your output MUST be a single JSON object that strictly adheres to the following structure and constraints,
matching the 'PodcastScript' Pydantic model.

JSON Structure Example:
```json
{
  "title": "Podcast Title (matches outline, 10-200 chars)",
  "introduction": "Engaging introduction (100-2000 chars).",
  "main_content": "Detailed podcast script body (800-10000 chars). Structure this based on the outline sections.",
  "conclusion": "Summarizing conclusion (100-1000 chars).",
  "speaker_notes": ["Optional note 1", "Optional note 2"],
  "estimated_duration_minutes": 30.0
}
```

Detailed Constraints (based on Pydantic model 'PodcastScript'):
- `title`: string, 10-200 characters. This should ideally match the title from the input Content Outline.
- `introduction`: string, 100-2000 characters. This should be an engaging opening for the podcast.
- `main_content`: string, 800-10000 characters. This is the core script and should be segmented or structured to clearly cover the topics/sections from the input Content Outline. Use clear headings or transitions between sections if appropriate for a script.
- `conclusion`: string, 100-1000 characters. This should provide a summary or closing thoughts.
- `speaker_notes`: list of strings, optional. These can be cues for delivery, sound effects, or other notes for the speaker.
- `estimated_duration_minutes`: float, optional. If provided, must be a positive number.
- The combined length of `introduction`, `main_content`, and `conclusion` fields MUST be between 1000 and 12000 characters.

Ensure the tone is conversational and suitable for a podcast.

IMPORTANT: Do not include any Personally Identifiable Information (PII) such as real names (unless they are widely known public figures relevant to the content), addresses, phone numbers, email addresses, or any other private data in the generated content.

Generate the JSON object now.
