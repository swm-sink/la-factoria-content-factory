# 🧠 Langchain Production System

## Overview

The `langchain/` directory contains all **production-focused** AI agents, prompts, and configurations for the La Factoria educational content generation platform. This is separate from the `.claude/` development system.

## 📁 Directory Structure

```
langchain/
├── agents/          # Production AI agents for content generation
│   ├── content-generation/    # Content creation agents
│   ├── quality-assessment/    # Quality validation agents
│   └── orchestration/         # Workflow orchestration agents
├── commands/        # Production commands and workflows
│   └── la-factoria/          # La Factoria specific commands
├── context/         # Production context and knowledge base
├── prompts/         # Content generation prompts
└── README.md        # This file
```

## 🎯 Purpose & Scope

### Production System (langchain/)
- **Content Generation**: Creating educational materials for end users
- **Quality Assessment**: Validating and improving generated content
- **User Workflows**: End-user facing functionality
- **Production Prompts**: Prompts used by the live application

### Development System (.claude/)
- **Code Development**: Building and maintaining the platform
- **Development Tools**: Code quality, testing, deployment
- **Development Workflows**: Internal development processes
- **Meta Prompts**: Prompts for improving the development process

## 🚀 Content Types Supported

The following educational content types are available in `prompts/`:

1. **Study Guide** (`study_guide.md`, `study_guide_enhanced.md`)
2. **Flashcards** (`flashcards.md`)
3. **Detailed Reading Material** (`detailed_reading_material.md`)
4. **One Pager Summary** (`one_pager_summary.md`)
5. **FAQ Collection** (`faq_collection.md`)
6. **Podcast Script** (`podcast_script.md`)
7. **Reading Guide Questions** (`reading_guide_questions.md`)
8. **Master Content Outline** (`master_content_outline.md`)

## 🔧 Integration with Application

### Using Prompts in Code

```python
from src.services.prompt_loader import PromptLoader

# Load a specific content type prompt
prompt_loader = PromptLoader()
study_guide_prompt = prompt_loader.load_prompt("study_guide")
```

### Agent Integration

The agents in this directory are designed to work with:
- **LangChain**: Primary orchestration framework
- **FastAPI**: Web service integration  
- **Multiple AI Providers**: OpenAI, Anthropic, etc.

## 📊 Quality Standards

All prompts and agents follow:
- **Strict JSON Output**: Structured response formats
- **Quality Assessment**: Built-in validation criteria
- **Educational Standards**: Pedagogically sound content generation
- **Multi-language Support**: Content in multiple languages

## 🔄 Workflow Integration

### Content Generation Flow

1. **Input Processing**: User provides source material
2. **Agent Selection**: Choose appropriate content generation agent
3. **Prompt Application**: Apply selected prompt template
4. **Quality Validation**: Run through quality assessment agent
5. **Output Delivery**: Return validated educational content

### Command Usage

```bash
# Example: Generate study guide
python -m langchain.commands.la_factoria.content --type study_guide --input "source_material.pdf"
```

## 🛠️ Development vs Production

| Aspect | Development (.claude/) | Production (langchain/) |
|--------|----------------------|-------------------------|
| **Purpose** | Build the platform | Use the platform |
| **Audience** | Developers | End users |
| **Focus** | Code quality | Content quality |
| **Agents** | Code cleanup, testing | Content generation |
| **Prompts** | Meta-development | Educational content |

## 📈 Monitoring & Quality

- **Content Quality Metrics**: Tracked via quality assessment agents
- **Performance Monitoring**: Integration with application monitoring
- **User Feedback Loop**: Continuous improvement based on usage

## 🔐 Security Considerations

- **Prompt Injection**: All prompts validated for security
- **Content Safety**: Educational content filtered for appropriateness  
- **Data Privacy**: User content handled per GDPR requirements

## 📝 Usage Examples

### Basic Content Generation

```python
from langchain.agents.content_generation import StudyGuideAgent

agent = StudyGuideAgent()
result = agent.generate(
    source_text="Your educational material here",
    difficulty_level="intermediate",
    language="en"
)
```

### Quality Assessment

```python
from langchain.agents.quality_assessment import ContentQualityAgent

quality_agent = ContentQualityAgent()
assessment = quality_agent.assess(generated_content)
```

## 📚 Additional Resources

- **Application Code**: `src/services/educational_content_service.py`
- **API Endpoints**: `src/api/routes/content_generation.py`
- **Quality System**: `src/services/quality_assessor.py`
- **Development Docs**: `.claude/documentation/`

---

**Last Updated**: August 4, 2025  
**Version**: 1.0.0  
**Contact**: La Factoria Development Team