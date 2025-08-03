# Master Context Index - La Factoria

**Purpose**: Comprehensive cross-reference system for optimal Claude Code navigation and context discovery.

## Context Imports (Anthropic-Compliant - Entry Point)

### Core Architecture & Navigation
@.claude/context/claude-code.md
@.claude/architecture/project-overview.md
@.claude/memory/simplification_plan.md

### Domain Integration
@.claude/domains/educational/README.md
@.claude/domains/technical/README.md
@.claude/domains/ai-integration/README.md
@.claude/domains/operations/README.md

### Implementation Requirements
@.claude/prp/PRP-001-Educational-Content-Generation.md
@.claude/prp/PRP-002-Backend-API-Architecture.md
@.claude/prp/PRP-003-Frontend-User-Interface.md

### Working Examples
@.claude/examples/backend/fastapi-setup/main.py
@.claude/examples/frontend/content-forms/ContentGenerationForm.tsx
@.claude/examples/ai-integration/content-generation/ai_content_service.py

**🔗 File Hop Integration**: This index provides bidirectional navigation following 2024-2025 Claude Code best practices with functional imports.

## 🗺️ Quick Navigation by Task

### 🚀 Starting Development
**First-time setup and onboarding**

1. **Read First**: `CLAUDE.md` - Master navigation guide and project overview (includes Context Navigation Hub with file hop patterns)
2. **Understand Architecture**: `.claude/architecture/project-overview.md` - Complete system architecture
3. **Check Examples**: `.claude/examples/README.md` - Working patterns and code examples
4. **Review Requirements**: `.claude/prp/PRP-001-Educational-Content-Generation.md` - Core functionality requirements

### 💻 Backend Development (FastAPI)
**Building the API layer**

**Start Here**: `.claude/examples/backend/fastapi-setup/main.py`
**Domain Context**: `.claude/domains/technical/README.md`
**Requirements**: `.claude/prp/README.md` (PRP-002 planned)
**Cross-References**:
- Educational content models: `.claude/domains/educational/README.md`
- AI service integration: `.claude/domains/ai-integration/README.md`
- Deployment patterns: `.claude/domains/operations/README.md`

### 🎨 Frontend Development (React)
**Building the user interface**

**Start Here**: `.claude/examples/frontend/content-forms/ContentGenerationForm.tsx`
**Domain Context**: `.claude/domains/technical/README.md`
**Requirements**: `.claude/prp/README.md` (PRP-003 planned)
**Cross-References**:
- Backend API integration: `.claude/examples/backend/`
- Educational UX patterns: `.claude/domains/educational/README.md`
- Operations monitoring: `.claude/domains/operations/README.md`

### 🤖 AI Integration Development
**Integrating AI services for content generation**

**Start Here**: `.claude/examples/ai-integration/content-generation/ai_content_service.py`
**Domain Context**: `.claude/domains/ai-integration/README.md`
**Requirements**: `.claude/prp/PRP-001-Educational-Content-Generation.md`
**Cross-References**:
- Prompt templates: `la-factoria/prompts/`
- Quality assessment: `.claude/domains/educational/README.md`
- Backend integration: `.claude/domains/technical/README.md`

### 🎓 Educational Content Development
**Working with educational frameworks and quality assessment**

**Start Here**: `.claude/examples/educational/content-types/study_guide_example.md`
**Domain Context**: `.claude/domains/educational/README.md`
**Requirements**: `.claude/prp/README.md` (PRP-004 planned)
**Cross-References**:
- AI prompt optimization: `.claude/domains/ai-integration/README.md`
- Content validation: `.claude/domains/technical/README.md`
- User experience: `.claude/domains/operations/README.md`

### 🚀 Deployment & Operations
**Deploying and operating the platform**

**Start Here**: `.claude/domains/operations/README.md` (infrastructure examples planned)
**Domain Context**: `.claude/domains/operations/README.md`
**Requirements**: `.claude/prp/README.md` (PRP-005 planned)
**Cross-References**:
- Technical architecture: `.claude/domains/technical/README.md`
- Monitoring requirements: `.claude/domains/operations/README.md`
- Quality tracking: `.claude/domains/educational/README.md`

## 📁 Directory Cross-Reference Map

### Core Navigation Files
```
├── CLAUDE.md                              # Master navigation and project guide
├── .claude/indexes/master-context-index.md # This file - comprehensive navigation
├── .claude/architecture/project-overview.md # Single source of truth for architecture
└── .claude/memory/simplification_plan.md   # Implementation approach clarification
```

### Domain Organization
```
.claude/domains/
├── educational/README.md      # Educational frameworks and quality assessment
├── technical/README.md        # FastAPI, React, database, and infrastructure
├── ai-integration/README.md   # AI services, prompts, and content generation
└── operations/README.md       # Deployment, monitoring, and operational excellence
```

### Working Examples
```
.claude/examples/
├── backend/fastapi-setup/     # Complete FastAPI application example
├── frontend/content-forms/    # React content generation form
├── ai-integration/            # AI service integration patterns
├── educational/content-types/ # Educational content examples with quality metrics
└── infrastructure/           # Deployment and operational examples
```

### Requirements Framework
```
.claude/prp/
├── README.md                  # PRP framework overview and templates
├── PRP-001-Educational-Content-Generation.md # Core content generation requirements (exists)
├── PRP-002-Backend-API-Architecture.md       # API implementation requirements (planned)
├── PRP-003-Frontend-User-Interface.md        # Frontend implementation requirements (planned)
├── PRP-004-Quality-Assessment-System.md      # Quality framework requirements (planned)
└── PRP-005-Deployment-Operations.md          # Operational requirements (planned)
```

### Project Memory System
```
.claude/memory/
├── simplification_plan.md     # Implementation approach (simple code, comprehensive context)
└── implementation_roadmap.md  # Development phases and quality gates
```

## 🔗 Cross-Domain Relationship Map

### Educational ↔ AI Integration
- **Educational Standards** → **AI Prompt Templates**: Quality requirements inform AI generation
- **Quality Assessment** → **AI Optimization**: Assessment results guide prompt improvement
- **Content Types** → **AI Service Selection**: Educational needs drive AI provider choice

### Educational ↔ Technical
- **Learning Objectives** → **API Design**: Educational workflows drive technical requirements
- **Quality Metrics** → **Database Schema**: Assessment data structures and storage
- **User Experience** → **Frontend Components**: Educational patterns inform UI design

### AI Integration ↔ Technical
- **AI Services** → **Backend API**: AI integration patterns and service orchestration
- **Content Generation** → **Database Storage**: Generated content persistence and management
- **Performance Monitoring** → **Operations**: AI service health and cost tracking

### Technical ↔ Operations
- **Application Architecture** → **Deployment Strategy**: Technical stack drives operational approach
- **Performance Requirements** → **Monitoring Setup**: Technical SLAs inform operational metrics
- **Security Implementation** → **Compliance Framework**: Technical security supports operational compliance

## 📊 Context Quality Reference

### Research-Backed Principles
All context organization follows 2024-2025 best practices:

- **Examples-First Approach**: "AI coding assistants perform much better when they can see patterns to follow"
- **Comprehensive Context**: "Context engineering is 10x better than prompt engineering"
- **Domain Organization**: Clear separation while maintaining cross-references
- **Living Documentation**: Context linked to actual working examples

### Quality Validation Checklist
- [ ] All project-specific context preserved (FastAPI, React, educational, AI integration)
- [ ] Clear navigation paths for common development tasks
- [ ] Cross-references maintain context relationships
- [ ] Examples provide concrete implementation patterns
- [ ] Requirements drive implementation decisions
- [ ] No hallucination policy enforced with verification requirements

## 🎯 Context Discovery Strategies

### By Development Phase
1. **Project Setup**: CLAUDE.md → Architecture Overview → Examples
2. **Requirements Analysis**: PRP framework → Domain context → Cross-references
3. **Implementation**: Examples → Domain context → Requirements validation
4. **Quality Assurance**: Educational domain → Quality assessment → Compliance verification
5. **Deployment**: Operations domain → Infrastructure examples → Monitoring setup

### By Feature Type
1. **Core Features**: PRP-001 → Educational domain → AI integration examples
2. **Technical Infrastructure**: Technical domain → Backend examples → Operations requirements
3. **User Experience**: Frontend examples → Educational UX → Technical integration
4. **Quality Systems**: Educational domain → Quality assessment → AI optimization

### By Expertise Level
1. **New to Project**: CLAUDE.md → Architecture overview → Simple examples
2. **Experienced Developer**: Domain-specific context → Advanced examples → Requirements
3. **Educational Specialist**: Educational domain → Quality framework → Content examples
4. **Operations Engineer**: Operations domain → Infrastructure examples → Monitoring setup

## 🔄 Context Maintenance Guidelines

### Adding New Context
1. **Identify Domain**: Determine primary domain (educational, technical, AI, operations)
2. **Create Examples**: Provide working code examples for new patterns
3. **Update Cross-References**: Add references in related domains and indexes
4. **Validate Quality**: Ensure context meets project standards and research principles

### Updating Existing Context
1. **Verify Accuracy**: Ensure all file references and line numbers are current
2. **Maintain Relationships**: Update cross-references when context changes
3. **Preserve Examples**: Keep working examples aligned with context updates
4. **Document Changes**: Update memory system with rationale for changes

### Quality Assurance
1. **Anti-Hallucination Verification**: All claims verified with specific file references
2. **Cross-Reference Validation**: Ensure all links and references are accurate
3. **Example Alignment**: Verify examples match documented patterns and requirements
4. **Domain Consistency**: Maintain consistent organization within and across domains

---

*This master context index provides comprehensive navigation for La Factoria's context engineering system, enabling optimal Claude Code effectiveness while preserving all valuable project-specific knowledge.*