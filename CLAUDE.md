# Claude Code Configuration

This file contains project-specific instructions and standards for Claude Code to follow when working with this repository.

## Project Overview

**La Factoria** is an AI-powered educational content generation platform that transforms textual input into comprehensive educational materials. The system generates 8 different content types from a master outline, creating cohesive educational experiences including podcasts, study guides, flashcards, and more.

### Core Mission
Transform topics/syllabi into structured educational content with high pedagogical value, leveraging advanced AI models and educational science principles.

### Content Types Generated
1. **Master Content Outline** - Foundation structure with learning objectives
2. **Podcast Script** - Conversational audio content with speaker notes
3. **Study Guide** - Comprehensive educational material with key concepts
4. **One-Pager Summary** - Concise overview with essential takeaways
5. **Detailed Reading Material** - In-depth content with examples and exercises
6. **FAQ Collection** - Question-answer pairs covering common topics
7. **Flashcards** - Term-definition pairs for memorization and review
8. **Reading Guide Questions** - Discussion questions for comprehension

## Technology Stack

### Backend (IMPLEMENTED)
- **Framework**: FastAPI with Python 3.11+ (✅ Complete)
- **AI Integration**: Multi-provider (OpenAI, Anthropic, Vertex AI) (🔧 In Progress)
- **Database**: PostgreSQL with SQLAlchemy (✅ Complete)
- **Audio Generation**: ElevenLabs integration (🔧 Partial)
- **Infrastructure**: Railway deployment configured (✅ Complete)

### Frontend (IMPLEMENTED - Different from Original Plan)
- **Framework**: Vanilla HTML/CSS/JavaScript (✅ Complete)
- **Styling**: Custom CSS (not Tailwind as originally planned) (✅ Complete)
- **State Management**: Local storage and vanilla JS (✅ Complete)

### Current State & Implementation Approach

This is a **substantial implementation** - extensive codebase already exists. The current assets are:
- **~17,950 lines** of production-ready implementation code
- Complete FastAPI backend with educational content generation services
- Vanilla HTML/CSS/JS frontend (not React/TypeScript as originally planned)
- Comprehensive test suite and database migrations
- Comprehensive prompt engineering system in `.claude/`
- Educational content templates and validation frameworks  
- Context engineering for educational standards and quality assessment

**🎯 Implementation Philosophy**: 
- **Production-Ready Implementation**: Substantial codebase (~17,950 lines), Railway deployment ready, comprehensive features
- **Comprehensive Context**: Full `.claude/` system with all domain knowledge for optimal AI assistance
- **Research-Backed**: Follows 2024-2025 context engineering best practices where AI performs 2x better with well-organized context

## MEP-CE Development Protocol

**Multi-step Exhaustive Planning - Critical Execution** methodology for systematic development planning and implementation.

### MEP-CE Framework Steps

1. **Exploration & Scoping** - Define precise boundaries for implementation within project ecosystem
2. **External Research** - Search for best practices and current industry standards (2024-2025)
3. **Initial Plan Formulation** - Create detailed implementation plan with all components
4. **Plan Critique** - Adversarial review of approach to identify potential issues
5. **Finalized Plan** - Battle-hardened final version incorporating critique feedback
6. **Micro-Task Breakdown** - Exhaustive checklist of atomic implementation steps
7. **Todo Critique** - Review todo list for completeness and missing elements
8. **Finalized Todos** - Locked-down implementation checklist with priorities
9. **Implementation** - Execute todos precisely with detailed progress logging
10. **Initial Validation** - Verify against success criteria with comprehensive testing
11. **Corrective Action** - Document and perform any fixes based on validation
12. **Final Review** - Holistic assessment of completed implementation
13. **Final Edits** - Minor adjustments from review to ensure 100% compliance
14. **Atomic Commit** - Git commit with detailed message documenting all changes

### MEP-CE Implementation Standards

- **Zero-Tolerance Quality**: All validation steps must pass before progression
- **Evidence-Based Planning**: Every decision backed by 2024-2025 research
- **Comprehensive Documentation**: Each step fully documented with rationale
- **Iterative Refinement**: Plans improved through systematic critique cycles
- **Atomic Implementation**: Changes made in discrete, testable increments

## Ultra-Deep Validation System

**Comprehensive validation framework ensuring 100% quality compliance across the entire .claude/ ecosystem.**

### Validation Components

#### 1. **Directory Structure** (.claude/validation/)
```
.claude/validation/
├── README.md                           # User-friendly documentation
├── conftest.py                         # Pytest shared fixtures (portable)
├── pytest.ini                         # Pytest configuration (flexible paths)
├── context-system-integration-testing.md  # Context system testing documentation
├── context-system-quality-validation.md   # Quality validation documentation
├── fixtures/                           # Test fixtures directory
│   └── conftest.py                     # Additional pytest fixtures
└── test_data/                          # Sample test files
    ├── valid_agent.md
    ├── valid_command.md
    └── valid_context.md
```

**📖 Comprehensive Usage Guide**: See `.claude/context/validation-system-usage.md` for detailed usage instructions, troubleshooting, and integration examples.

#### 2. **Claude Code Settings** (.claude/settings.json)
Project-level settings file that configures Claude Code permissions and validation integration:
- **Script Permissions**: Allows all validation scripts and testing commands
- **Directory Access**: Grants access to validation, context, and educational content directories  
- **Environment Variables**: Sets PYTHONPATH and validation flags
- **Hooks Integration**: Automatic validation on file edits and writes
- **Security**: Denies dangerous operations while allowing development workflows

**📚 Comprehensive Settings Guide**: See `.claude/context/claude-code-settings-guide.md` for detailed configuration options, maximum autonomy settings, MCP server setup, and advanced hooks configuration based on 20+ online sources.

**🔧 Troubleshooting**: If you see `hooks: Expected object, but received array` error, the settings use the new hooks format (PostToolUse/PreToolUse events). Run `claude doctor` to validate configuration.

**⚡ New Validation Workflow**: Pre-commit now uses minimal checks only (<5s). For quality validation, use manual commands:
- `source .claude/validation-commands.sh` - Load validation aliases
- `validate` - Full system validation (when needed)
- `health-check` - Quick Claude Code functionality check

**Note**: `.claude/settings.local.json` is git-ignored for personal overrides.

#### 3. **Claude Code Hooks Integration** (.claude/hooks/)
```
.claude/hooks/
├── hooks.json                  # Hooks configuration
├── pre_tool_use.py            # Pre-operation validation
├── post_tool_use.py           # Post-operation quality checks
└── user_prompt_submit.py      # Prompt security validation
```

#### 3. **Artifact Management** (.claude/artifacts/)
```
.claude/artifacts/
├── reports/validation/YYYY-MM-DD/    # Date-organized reports
│   ├── system_validation_executive_summary.md
│   ├── system_validation_detailed_results.json
│   ├── agents_validation_report.md
│   ├── context_validation_report.md
│   └── commands_validation_report.md
└── logs/validation/YYYY-MM-DD/       # Validation audit logs
    ├── pre_tool_validation_YYYY-MM-DD.log
    ├── post_tool_validation_YYYY-MM-DD.log
    └── prompt_validation_YYYY-MM-DD.log
```

### Validation Standards (2024-2025)

- **Zero-Tolerance Policy**: All modules must achieve 100% pass rate
- **Research-Based Criteria**: Every validation step backed by current industry research
- **Evidence Collection**: Comprehensive documentation of all validation results
- **Performance Benchmarks**: System validation completes in <120 seconds
- **Security Integration**: Automatic security scanning and prompt validation
- **CI/CD Integration**: Pytest-compatible for automated testing pipelines

### Usage Examples

#### Manual Validation
```bash
# Load validation aliases
source .claude/validation-commands.sh

# Run full system validation (when needed)
validate

# Quick Claude Code functionality check
health-check

# Run pytest-compatible tests
pytest .claude/validation/ -v
```

#### Automatic Validation (Hooks)
Validation automatically runs on:
- **Pre-Tool-Use**: Security and safety checks before file operations
- **Post-Tool-Use**: Quality validation after file modifications
- **User-Prompt-Submit**: Security scanning of all user prompts

### Quality Thresholds
- **Agent System**: 100% YAML compliance, tool optimization, naming consistency
- **Context System**: ≥80% cross-reference coverage, ≤3 navigation hops, ≥90% content quality
- **Commands System**: 100% section completeness, ≥90% formatting compliance
- **Overall System**: 100% module success rate, ≥95% step completion rate

## Prompt Engineering System

### Available La Factoria Commands

Located in `.claude/commands/la-factoria/`:
- `/la-factoria-content` - Educational content generation using hyper-specific La Factoria patterns
- `/la-factoria-prompt-optimizer` - Advanced meta-prompting for educational content optimization
- `/la-factoria-monitoring` - Monitor content generation performance and quality metrics
- `/la-factoria-frontend` - Frontend development with educational UX patterns
- `/la-factoria-postgres` - Database operations optimized for educational content storage
- `/la-factoria-langfuse` - Prompt management and observability integration
- `/la-factoria-gdpr` - Privacy compliance and data protection for educational platforms
- `/la-factoria-init` - Project initialization with La Factoria-specific setup

### Optimized Prompt Templates

Located in `.claude/templates/la-factoria/`:
- `study-guide-optimized.md` - Enhanced study guide generation with educational frameworks
- `flashcards-optimized.md` - Cognitive science-based flashcard creation
- `master-outline-optimized.md` - Comprehensive content outline with Bloom's taxonomy
- `podcast-script-optimized.md` - Audio content script optimization

### Core Prompt Library

Located in `prompts/`:
- `master_content_outline.md` - Foundation outline generation
- `podcast_script.md` - Audio script creation
- `study_guide.md` - Educational guide generation
- `study_guide_enhanced.md` - Advanced study guide with additional features
- `flashcards.md` - Learning card generation
- `one_pager_summary.md` - Concise summary creation
- `detailed_reading_material.md` - In-depth content generation
- `faq_collection.md` - FAQ generation
- `reading_guide_questions.md` - Discussion question creation
- `strict_json_instructions.md` - JSON formatting guidelines

### Educational Components

Located in `.claude/components/la-factoria/`:
- `educational-standards.md` - Age-appropriate guidelines and learning frameworks
- `quality-assessment.md` - Quality metrics and scoring algorithms
- `prompt-validation.md` - Schema validation and testing frameworks
- `security-validation.md` - Input sanitization and safety measures

### Project Context

Key context files in `.claude/context/`:
- `la-factoria-project.md` - Comprehensive project architecture and capabilities
- `educational-content-assessment.md` - Learning science and quality assessment frameworks
- `fastapi.md` - FastAPI development best practices
- `elevenlabs.md` - Audio generation integration patterns
- `claude-4-best-practices.md` - AI interaction optimization

## Development Guidelines

### Git Configuration (Repository-Specific)
- **Author**: This repository uses swm-sink (stefan.menssink@gmail.com) for commits
- **Authentication**: GitHub PAT (Personal Access Token) for push operations
- **Configuration**: Run `.git-local-config.sh` to set repository-specific git settings
- **Anti-Patterns**: See `.claude/memory/git_commit_patterns.md` for Phase 3C learnings

### Code Standards
- **Python**: FastAPI patterns, PEP 8, type hints, Pydantic models
- **Testing**: pytest with comprehensive coverage
- **Quality**: Use pre-commit hooks (already configured)
- **Documentation**: Clear docstrings with educational context
- **Security**: Input validation, PII prevention, API key management

### Educational Content Standards
- **Quality Threshold**: Minimum 0.70 overall score for generated content
- **Educational Value**: Must be ≥ 0.75 for learning effectiveness
- **Factual Accuracy**: Must be ≥ 0.85 for information reliability
- **Age Appropriateness**: Language and complexity matching target audience
- **Pedagogical Structure**: Following educational best practices

### Prompt Optimization Principles
1. **Token Efficiency**: 20-40% reduction through consolidation and clarity
2. **Educational Focus**: Explicit learning objectives and audience targeting
3. **Quality Requirements**: Specific, measurable quality criteria
4. **Consistency**: Standardized structure across all content types
5. **Validation**: Built-in quality checks and educational standards

## Memory System & Analysis Standards

### Context-First Analysis
- **NEVER** make architectural recommendations without understanding business/legal requirements
- **ALWAYS** discover compliance obligations before suggesting changes
- **VERIFY** all claims with specific file references and line numbers
- **DOCUMENT** findings in `.claude/memory/` before proceeding

### Memory System Structure

Located in `.claude/memory/`:
- `analysis_learnings.md` - Major findings and corrections
- `decision_rationale.md` - Context and justification for decisions
- `git_commit_patterns.md` - Atomic commit standards and anti-pattern learnings from Phase 3C
- `la-factoria-project.md` - Current project context and corrections

### No Hallucination Policy (Enhanced 2024-2025 Standards)

**CRITICAL**: This policy was established following comprehensive online research of context engineering best practices and is MANDATORY for all AI interactions.

#### Zero Tolerance Framework
- **ZERO TOLERANCE** for unverified claims about project capabilities, file locations, or technical implementations
- **ALL** assertions must reference specific files with line numbers (format: `file_path:line_number`)
- **IMMEDIATE** correction required when evidence contradicts assumptions
- **MANDATORY** verification of regulatory/compliance context before architectural recommendations

#### Verification Requirements (Research-Backed)
1. **File References**: Every claim about existing code/config must include exact file path and line number
2. **Online Verification**: For external claims (libraries, best practices), provide specific URLs from 2024-2025 sources
3. **Context Validation**: Before suggesting changes, verify current project context in `.claude/memory/` and `.claude/context/`
4. **Implementation Alignment**: Ensure all recommendations align with "simple implementation, comprehensive context" principle

#### Anti-Hallucination Checklist
- [ ] Verified file exists at specified path
- [ ] Confirmed line numbers match actual content  
- [ ] Checked for contradictory information in memory files
- [ ] Validated external claims with recent online sources
- [ ] Ensured recommendations preserve ALL project-specific context

## 🗺️ Master Navigation Guide (2024-2025 Context Engineering)

**This section provides comprehensive navigation for the La Factoria context system, organized for optimal Claude Code effectiveness.**

### 📁 Examples Directory (CRITICAL for Claude Code Success)

**Research Finding**: "AI coding assistants perform much better when they can see patterns to follow"

Located in `.claude/examples/`:
- **`backend/fastapi-setup/`** - Complete FastAPI application patterns with authentication, validation, and educational content endpoints
- **`frontend/content-forms/`** - Vanilla HTML/CSS/JS components for content generation with form validation and API integration
- **`ai-integration/content-generation/`** - AI service integration patterns for OpenAI, Anthropic, and Vertex AI
- **`educational/content-types/`** - Examples of all 8 content types with quality assessment metrics
- **`infrastructure/`** - Railway deployment, testing patterns, and monitoring examples

### 🏗️ Project Structure (Complete System)

```
bangui/
├── prompts/              # Core educational content generation prompts
│   ├── master_content_outline.md
│   ├── podcast_script.md
│   ├── study_guide.md
│   └── ... (8 content types)
├── src/                  # Complete FastAPI implementation
│   ├── api/routes/       # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   └── core/             # Core components
├── static/               # Complete frontend implementation
│   ├── index.html        # Main application page
│   ├── css/style.css     # Application styling
│   └── js/app.js         # Application logic
└── tests/                # Comprehensive test suite
    ├── test_api_endpoints.py
    ├── test_services.py
    └── ... (multiple test files)

.claude/
├── examples/             # CRITICAL: Working patterns for Claude to follow
│   ├── backend/          # FastAPI patterns and complete examples
│   ├── frontend/         # Vanilla HTML/CSS/JS components and UI patterns
│   ├── ai-integration/   # AI service integration examples
│   ├── educational/      # Content type examples with quality metrics
│   └── infrastructure/   # Deployment and testing patterns
├── commands/             # Automation commands for content optimization
├── templates/            # Optimized prompt templates and workflows
├── components/           # Educational frameworks and validation systems
├── context/              # Project and domain context knowledge
└── memory/               # Analysis findings and decision rationale
```

### 🎯 Context Discovery System

**Quick Reference by Development Task**:

#### Building Backend API
1. **Start with**: `.claude/examples/backend/fastapi-setup/main.py`
2. **Reference**: Educational content standards in project overview above
3. **Validate against**: `.claude/components/quality/` frameworks
4. **Deploy using**: Railway patterns in `.claude/examples/infrastructure/`

#### Building Frontend Interface
1. **Start with**: `.claude/examples/frontend/content-forms/ContentGenerationForm.tsx`
2. **Reference**: UI patterns for educational tools
3. **Integrate with**: Backend API examples
4. **Style using**: Simple CSS patterns (no complex frameworks)

#### Integrating AI Services
1. **Start with**: `.claude/examples/ai-integration/content-generation/ai_content_service.py`
2. **Reference**: Prompt templates in `prompts/`
3. **Validate using**: Educational quality assessment components
4. **Monitor with**: Performance tracking patterns

#### Educational Content Development
1. **Start with**: `.claude/examples/educational/content-types/`
2. **Reference**: Quality rubrics and assessment criteria
3. **Follow**: Pedagogical patterns and best practices
4. **Validate against**: Educational standards frameworks

### 🔄 Context Engineering Workflow (2024-2025 Best Practices)

**Research Finding**: "Context engineering is 10x better than prompt engineering and 100x better than vibe coding"

#### Before Starting Any Development Task:
1. **Check Examples First** - Review `.claude/examples/` for relevant patterns
2. **Verify Context** - Ensure no contradictory information in `.claude/memory/`
3. **Reference Architecture** - Use project structure as single source of truth
4. **Follow Anti-Hallucination Policy** - Verify all claims with specific file references

#### During Development:
1. **Preserve ALL Project Context** - Never remove FastAPI, React, educational, or AI integration context
2. **Follow Established Patterns** - Use examples as templates, not starting points
3. **Maintain Quality Standards** - All code must meet educational content quality thresholds
4. **Document Decisions** - Update `.claude/memory/` with rationale for changes

#### Context Organization Principles:
- **Domain Separation**: Related context grouped together (backend, frontend, educational, AI)
- **Living Documentation**: Context references actual working examples
- **Cross-References**: Clear links between related context across domains
- **Version Alignment**: All context reflects current project direction and technology choices

## 🧭 Context Navigation Hub (Anthropic-Compliant File Imports)

**Purpose**: Efficient navigation through La Factoria's comprehensive context system using official Anthropic Claude Code file import patterns with 5-hop maximum depth.

### 📍 Core Context Imports (Following Anthropic Guidance)

#### Essential Context Foundation
@.claude/context/claude-code.md
@.claude/architecture/project-overview.md
@.claude/memory/simplification_plan.md

#### Educational Domain Context
@.claude/domains/educational/README.md
@.claude/components/la-factoria/educational-standards.md
@.claude/components/la-factoria/quality-assessment.md

#### Technical Implementation Context  
@.claude/domains/technical/README.md
@.claude/prp/PRP-002-Backend-API-Architecture.md  
@.claude/prp/PRP-003-Frontend-User-Interface.md

#### AI Integration and Quality
@.claude/domains/ai-integration/README.md
@.claude/prp/PRP-004-Quality-Assessment-System.md
@.claude/prp/PRP-005-Deployment-Operations.md

### 🚀 Development Task Navigation (Max 5-Hop Depth)

#### Backend Development Workflow
- **Primary**: @.claude/examples/backend/fastapi-setup/main.py
- **Architecture**: @.claude/prp/PRP-002-Backend-API-Architecture.md
- **Domain Context**: @.claude/domains/technical/README.md

#### Frontend Development Workflow  
- **Primary**: @static/index.html (main application interface)
- **JavaScript**: @static/js/app.js (application logic)
- **Architecture**: @.claude/prp/PRP-003-Frontend-User-Interface.md
- **Domain Context**: @.claude/domains/technical/README.md

#### AI Integration Workflow
- **Primary**: @.claude/examples/ai-integration/content-generation/ai_content_service.py
- **Architecture**: @.claude/domains/ai-integration/README.md
- **Requirements**: @.claude/prp/PRP-001-Educational-Content-Generation.md
- **MCP Integration**: Model Context Protocol support for 2025 AI standards
- **Evaluation Framework**: 20-query testing standard for quality assessment

#### Educational Content Workflow
- **Primary**: @.claude/examples/educational/content-types/study_guide_example.md
- **Quality Framework**: @.claude/components/la-factoria/quality-assessment.md
- **Standards**: @.claude/components/la-factoria/educational-standards.md

### 🎯 Quick Access Import Patterns

**Claude Code Integration**: @.claude/context/claude-code.md → Advanced agent system and development workflows  
**Master Index**: @.claude/indexes/master-context-index.md → Complete cross-reference system  
**Commands**: @.claude/commands/la-factoria/la-factoria-content.md → Educational content generation commands

### 🏗️ Architecture & Requirements
- **Complete Architecture**: `.claude/architecture/project-overview.md` - Single source of truth for system design
- **Implementation Approach**: `.claude/memory/simplification_plan.md` - Simple implementation, comprehensive context
- **Requirements Framework**: `.claude/prp/README.md` - Product Requirements Prompt system

### 💡 Context Discovery Strategy
1. **New to Project**: CLAUDE.md → Master Index → Architecture Overview → Examples
2. **Specific Development Task**: CLAUDE.md → Quick File Hop → Domain Context → Examples
3. **Quality Focus**: CLAUDE.md → Educational Domain → Quality Assessment → Requirements
4. **Deployment/Operations**: CLAUDE.md → Operations Domain → Infrastructure Examples

## Usage Examples

### Content Generation Workflow
```bash
# 1. Initialize La Factoria project setup
/la-factoria-init

# 2. Generate educational content using existing prompt templates
/la-factoria-content generate study-guide "Python Programming" high-school

# 3. Optimize prompts for better educational outcomes
/la-factoria-prompt-optimizer study-guide medium

# 4. Monitor content generation performance
/la-factoria-monitoring dashboard
```

### Educational Platform Management
```bash
# Frontend development with educational UX patterns
/la-factoria-frontend create-content-form

# Database operations for educational content
/la-factoria-postgres setup-educational-schema

# Prompt management with Langfuse integration
/la-factoria-langfuse sync-templates
```

## Next Steps for Development

### Phase 1: Backend Foundation
1. Set up FastAPI application structure
2. Implement core content generation service
3. Integrate prompt templates from `prompts/`
4. Add AI model integration (Vertex AI/OpenAI)

### Phase 2: Quality & Validation
1. Implement quality assessment pipeline using `.claude/components/la-factoria/`
2. Add educational standards validation
3. Create automated testing for content generation
4. Implement feedback loops for prompt optimization

### Phase 3: Audio & Advanced Features
1. Integrate ElevenLabs for podcast script to audio conversion
2. Add batch processing capabilities
3. Implement content versioning and iteration
4. Add analytics and performance monitoring

### Phase 4: Frontend & User Experience
1. Create React frontend for content generation requests
2. Build dashboard for content management
3. Add user authentication and authorization
4. Implement content sharing and export features

## Important Notes

- This is a **substantial existing implementation** with comprehensive codebase to build upon
- Extensive prompt engineering and context system already in place
- Focus on educational quality and pedagogical effectiveness
- Leverage existing `.claude/` framework for optimization and validation
- Pre-commit hooks configured for code quality and security

## 📚 Claude Code File Import System (Official Anthropic Guidance)

### File Import Specifications
This project follows Anthropic's official Claude Code file import patterns for optimal AI-assisted development:

#### Import Syntax (Official)
- **Standard Format**: `@path/to/import` (not `<include>` or other formats)
- **Relative Paths**: `@.claude/context/file.md` (recommended for project files)
- **Absolute Paths**: `@/absolute/path/file.md` (for system-wide imports)
- **Home Directory**: `@~/user-specific/file.md` (for personal overrides)

#### Technical Limitations
- **Maximum Depth**: 5 hops maximum for recursive imports
- **Evaluation Rules**: Imports not evaluated inside markdown code spans or code blocks  
- **Memory Command**: Use `/memory` to see loaded files and import chain
- **Discovery**: Claude Code recursively discovers CLAUDE.md files in project subdirectories

#### Import Chain Example (Max 5 Hops)
```
CLAUDE.md (Hop 1)
└── @.claude/context/claude-code.md (Hop 2)
    └── @.claude/context/claude-code/README.md (Hop 3)
        └── @.claude/domains/technical/README.md (Hop 4)
            └── @.claude/examples/backend/main.py (Hop 5)
```

#### Best Practices (2024-2025)
1. **Keep Core Imports in CLAUDE.md**: Essential context should be directly imported
2. **Use Relative Paths**: Prefer `@.claude/` over absolute paths for portability  
3. **Organize by Domain**: Group related imports together (educational, technical, AI)
4. **Test Import Chains**: Use `/memory` command to verify all imports load correctly
5. **Avoid Deep Nesting**: Stay well under 5-hop limit for reliable loading

### Implementation Note
This file implements the official Anthropic Claude Code memory system with proper `@` import syntax, replacing previous descriptive file hop patterns with actual functional imports that Claude Code can process automatically.

## 📋 File Import Implementation Enforcement

**MANDATORY COMPLIANCE**: All files in this project MUST follow Anthropic's official Claude Code import patterns.

### Implementation Guide
@.claude/context/file-hop-implementation-guide.md

### Enforcement Standards
1. **All new files MUST include proper import section** using `@path/to/file.md` syntax
2. **NO `<include>` syntax allowed** - only Anthropic-compliant `@` imports
3. **Import chains MUST stay within 5-hop limit** as per official guidelines
4. **All referenced files MUST exist** - no broken import links allowed

### Validation Command
Use `/memory` command to verify all imports load correctly and validate import chain compliance.

### Non-Compliance Correction
Any file found using non-compliant import patterns must be corrected immediately according to the implementation guide. This is required for optimal AI-assisted development performance.