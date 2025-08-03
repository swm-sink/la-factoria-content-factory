# Prompt Templates

These prompts were extracted from the enterprise system and will be migrated to Langfuse for easier management.

## Available Prompts

1. **master_content_outline.md** - Creates structured outline first
2. **study_guide.md** - Comprehensive study guide generation
3. **study_guide_enhanced.md** - Enhanced version with more detail
4. **podcast_script.md** - Audio content scripts
5. **flashcards.md** - Spaced repetition learning cards
6. **one_pager_summary.md** - Executive summaries
7. **detailed_reading_material.md** - In-depth content
8. **faq_collection.md** - Frequently asked questions
9. **reading_guide_questions.md** - Discussion questions
10. **strict_json_instructions.md** - JSON formatting helper

## Migration Plan

### Phase 1 (Current)
- Prompts stored as markdown files
- Loaded directly in code

### Phase 2 (Future)
- Upload to Langfuse UI
- Version control in Langfuse
- A/B testing capabilities
- Analytics on prompt performance

## Usage

```python
# Current (Phase 1)
with open('prompts/study_guide.md', 'r') as f:
    prompt_template = f.read()
    
prompt = prompt_template.replace('{{TOPIC}}', user_topic)

# Future (Phase 2)
from langfuse import Langfuse
langfuse = Langfuse()
prompt = langfuse.get_prompt("study_guide", version="1.0")
compiled = prompt.compile(topic=user_topic)
```