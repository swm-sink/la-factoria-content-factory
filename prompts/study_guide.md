You are an expert educational writer specializing in pedagogically sound study guides. Based on the provided Content Outline (in JSON format), generate a comprehensive Study Guide that includes clear learning objectives, age-appropriate content, and integrated assessment opportunities.

The guide should be well-structured, informative, and help learners achieve specific learning outcomes.

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
  "learning_objectives": ["Students will understand key concept 1", "Students will be able to apply technique 2", "Students will analyze relationship 3"],
  "target_audience": "Target grade level or age group (e.g., 'high school', 'college', 'adult learners')",
  "overview": "Overview of the study guide (100-1000 chars).",
  "key_concepts": ["Concept 1", "Concept 2", "Concept 3", "Concept 4", "Concept 5"],
  "detailed_content": "Comprehensive content for the study guide (500-8000 chars). Structure this based on the outline sections.",
  "practice_exercises": ["Exercise 1: Apply concept X to solve problem Y", "Exercise 2: Compare and contrast A and B", "Exercise 3: Analyze case study Z"],
  "assessment_questions": ["What is the relationship between X and Y?", "How would you apply concept Z in situation W?", "Explain the significance of principle A"],
  "summary": "Concise summary of the guide (100-1000 chars).",
  "recommended_reading": ["Optional reading 1", "Optional reading 2"]
}
```

Detailed Constraints (based on Pydantic model 'StudyGuide'):
- `title`: string, 10-200 characters. This should ideally match the title from the input Content Outline.
- `learning_objectives`: list of strings, 3-8 learning objectives. Use action verbs (understand, apply, analyze, evaluate) and specify what students will achieve.
- `target_audience`: string, 10-100 characters. Specify the appropriate age group, grade level, or educational stage.
- `overview`: string, 100-1000 characters. Provide a brief introduction to what the study guide covers.
- `key_concepts`: list of strings, 5 to 20 key concepts. These should be important terms or ideas from the content.
- `detailed_content`: string, 500-8000 characters. This section should elaborate on the topics/sections from the input Content Outline, providing explanations, examples, and details suitable for a study guide.
- `practice_exercises`: list of strings, 3-10 practice exercises. Design hands-on activities that reinforce learning objectives.
- `assessment_questions`: list of strings, 5-15 assessment questions. Create questions that test understanding and application of key concepts.
- `summary`: string, 100-1000 characters. A concise recap of the main points of the study guide.
- `recommended_reading`: list of strings, optional. Suggest further readings or resources.

Ensure the content is educational, clear, and well-organized.

IMPORTANT: Do not include any Personally Identifiable Information (PII) such as real names (unless they are widely known public figures relevant to the content), addresses, phone numbers, email addresses, or any other private data in the generated content.

---
CRITICAL OUTPUT REQUIREMENTS:
1. Your response MUST be valid JSON matching the structure and constraints detailed above.
   Ensure all field names, types, and nesting are exactly as specified.
   Do not include any text before or after the JSON object.
   Do not wrap the JSON in markdown code blocks (e.g., ```json ... ```).

2. VALIDATION RULES (derived from Pydantic model and common sense):
   - `title`: Must be a non-empty string, 10-200 characters. Should align with the outline's title.
   - `learning_objectives`: Must be a list of 3-8 non-empty strings. Each should start with action verbs and specify measurable outcomes.
   - `target_audience`: Must be a non-empty string, 10-100 characters. Should specify appropriate educational level.
   - `overview`: Must be a non-empty string, 100-1000 characters.
   - `key_concepts`: Must be a list of 5 to 20 non-empty strings.
   - `detailed_content`: Must be a non-empty string, 500-8000 characters. It should expand on the Content Outline.
   - `practice_exercises`: Must be a list of 3-10 non-empty strings. Each should be an actionable learning activity.
   - `assessment_questions`: Must be a list of 5-15 non-empty strings. Questions should test comprehension and application.
   - `summary`: Must be a non-empty string, 100-1000 characters.
   - All textual content should be meaningful, well-written, educational, and directly relevant to the Content Outline.

3. QUALITY CHECKS (Before responding, internally verify these):
   ✓ All required fields (title, learning_objectives, target_audience, overview, key_concepts, detailed_content, practice_exercises, assessment_questions, summary) are populated with valid data meeting length/count constraints.
   ✓ Learning objectives use measurable action verbs and align with educational best practices.
   ✓ Target audience is clearly specified and age-appropriate language is used throughout.
   ✓ The study guide's content directly expands upon the provided Content Outline.
   ✓ Key concepts are relevant and accurately reflect the core ideas.
   ✓ Practice exercises provide hands-on learning opportunities that reinforce objectives.
   ✓ Assessment questions test both comprehension and application of concepts.
   ✓ The detailed content is informative, well-structured, and suitable for learners.
   ✓ `recommended_reading` (if provided) lists relevant resources.
---

Generate the JSON object now.
