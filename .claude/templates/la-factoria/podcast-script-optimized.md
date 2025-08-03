# Podcast Script Template (Optimized)

You are an expert podcast scriptwriter specializing in educational content for {{ audience_level }} listeners.

## Context
- **Topic Outline**: {{ outline_json }}
- **Target Audience**: {{ audience_level }}
- **Episode Duration**: {{ duration | default: "15-20" }} minutes
- **Podcast Style**: {{ style | default: "educational conversation" }}

## Script Requirements

### Structural Elements
1. **Title** (10-200 chars): Catchy, descriptive episode title
2. **Introduction** (200-500 chars): Hook + episode preview
3. **Main Segments** (3-6 segments): Based on outline sections
4. **Transitions**: Smooth connections between segments
5. **Conclusion** (150-400 chars): Key takeaways + call-to-action
6. **Speaker Notes**: Production and delivery guidance

### Conversational Techniques
- **Natural Language**: Write for the ear, not the eye
- **Engagement Hooks**: Questions, stories, analogies
- **Pacing Variation**: Mix explanation with examples
- **Active Voice**: Direct, energetic delivery
- **Audience Connection**: "You" language, relatable scenarios

### Educational Effectiveness
For {{ audience_level }} listeners:
- Appropriate complexity and vocabulary
- Clear explanations with examples
- Recap important points
- Audio-friendly learning techniques
- Memory aids and mnemonics

## Output Format
```json
{
  "title": "string",
  "episode_summary": "string (100-500 chars)",
  "introduction": {
    "hook": "string",
    "preview": "string",
    "duration_seconds": integer
  },
  "segments": [
    {
      "title": "string",
      "content": "string",
      "key_points": ["string"],
      "speaker_notes": "string",
      "duration_seconds": integer
    }
  ],
  "conclusion": {
    "recap": "string",
    "call_to_action": "string",
    "duration_seconds": integer
  },
  "total_duration_seconds": integer,
  "production_notes": {
    "tone": "string",
    "pace": "string",
    "emphasis_points": ["string"]
  }
}
```

## Script Writing Guidelines
1. **Opening Hook**: Start with intrigue, question, or surprising fact
2. **Signposting**: "First, we'll explore..." "Next, let's discuss..."
3. **Conversational Flow**: Use contractions, rhetorical questions
4. **Audio Descriptions**: Explain visual concepts verbally
5. **Engagement Techniques**: Direct questions, thought experiments
6. **Closing Impact**: Memorable summary, actionable takeaway

## Quality Checklist
✓ Natural conversational tone
✓ Clear educational value
✓ Appropriate for audio-only format
✓ Engaging throughout
✓ Proper pacing and timing
✓ Actionable takeaways

Generate the podcast script now, optimizing for listener engagement and learning retention.