# La Factoria Simple v2

A dramatically simplified content generation system. From 50,000+ lines to <1,000 lines.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
cd src && uvicorn main:app --reload

# Run tests
pytest
```

## Project Status

### ✅ Completed
- Project structure (5 directories)
- Health check endpoint with TDD
- Prompt templates extracted (10 templates)
- Migration guide created
- Archive strategy documented

### 🚧 In Progress
- Content generation endpoint
- Simple authentication
- Railway deployment

### 📋 Planned
- User migration tools
- Railway Postgres integration
- Production deployment

## Architecture

```
la-factoria-simple-v2/
├── src/                    # Backend API (<200 lines target)
│   └── main.py            # FastAPI application
├── static/                 # Frontend (vanilla JS)
├── tests/                  # TDD test suite
├── prompts/               # AI prompt templates
├── scripts/               # Migration scripts
└── docs/                  # Documentation
```

## Simplification Metrics

| Metric | Old System | New System | Reduction |
|--------|------------|------------|-----------|
| Files | 1,000+ | <20 | 98% |
| Dependencies | 69 | <15 | 78% |
| Lines of Code | 50,000+ | <1,000 | 98% |
| Setup Time | 2 days | 10 minutes | 99% |
| Monthly Cost | $500+ | $20 | 96% |

## Development Process

Following rigorous methodology:
1. **Explore** - Deep analysis before decisions
2. **Plan** - Detailed roadmap
3. **Critique** - Stress test the plan  
4. **Correct** - Refine based on critique
5. **Atomize** - Break into 2-4 hour tasks
6. **Implement** - TDD for each task
7. **Gate** - Quality checks
8. **Commit** - Atomic commits
9. **Review** - Holistic assessment

## Key Decisions

- **Railway over GCP**: Managed infrastructure
- **Vanilla JS over React**: No build complexity
- **Postgres over Firestore**: Simple SQL
- **Sync over Async**: Direct processing
- **Langfuse (Phase 2)**: External prompt management

## Migration from Old System

See [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) for detailed steps.

Old system preserved at tag: `v2.0-enterprise-final`

## Contributing

1. Follow TDD approach
2. Keep it simple
3. Document decisions
4. One task = one commit

## License

MIT - Keep it simple!