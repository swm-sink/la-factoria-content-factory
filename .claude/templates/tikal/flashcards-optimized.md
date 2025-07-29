# Flashcards Generation Template (Optimized)

You are an expert in creating effective educational flashcards for {{ audience_level }} students.

## Context
- **Topic**: {{ topic }}
- **Audience**: {{ audience_level }}
- **Learning Focus**: {{ learning_objectives }}
- **Card Count Target**: {{ card_count | default: 10-20 }}

## Flashcard Design Principles

### Cognitive Science Foundation
- **Spaced Repetition**: Design for repeated review over time
- **Active Recall**: Questions that require genuine retrieval
- **Elaborative Encoding**: Connect to existing knowledge
- **Dual Coding**: Combine verbal and conceptual elements

### Educational Requirements
For {{ audience_level }}, ensure:
- Vocabulary matches student comprehension level
- Concepts build progressively in difficulty
- Clear, unambiguous questions and answers
- One key concept per card (atomic principle)

## Content Outline
{{ outline_json }}

## Generation Guidelines

### Question Side (Front)
- Pose clear, specific questions
- Avoid yes/no questions when possible
- Use active voice and direct language
- Include context clues when necessary
- Test understanding, not just memorization

### Answer Side (Back)
- Provide complete but concise answers
- Include memory aids or mnemonics
- Add brief explanations for "why"
- Use examples when helpful
- Keep answers under 100 characters when possible

### Card Types to Include
1. **Definition Cards**: Term → Definition
2. **Application Cards**: Scenario → Solution
3. **Comparison Cards**: Concept A vs B → Key Differences
4. **Example Cards**: Principle → Real-world Example
5. **Process Cards**: Step N → What comes next?

## Output Format
```json
{
  "title": "Flashcard Set Title (10-200 chars)",
  "description": "Brief description of the flashcard set (50-500 chars)",
  "flashcards": [
    {
      "id": "unique_id",
      "question": "Clear, specific question (10-200 chars)",
      "answer": "Concise, complete answer (10-300 chars)",
      "difficulty": "easy|medium|hard",
      "category": "concept category"
    }
  ],
  "study_tips": ["Tip 1", "Tip 2", "Tip 3"]
}
```

## Quality Checklist
✓ Each card tests one clear concept
✓ Questions are unambiguous
✓ Answers are factually accurate
✓ Difficulty progression is logical
✓ Content aligns with learning objectives
✓ No duplicate or redundant cards

Generate the flashcard set now, optimizing for effective learning and retention.