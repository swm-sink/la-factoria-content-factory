# Project Corrections & Clarifications

## Project Name Correction (2025-08-02)

### Error
- **Incorrect**: Used "Tikal" and "Tikal Simple" throughout analysis
- **Source**: Outdated reference in CLAUDE.md line 6
- **Impact**: All documentation and folder names used wrong project name

### Correction  
- **Correct Name**: **La Factoria**
- **Evidence**: 
  - Directory structure: `/la-factoria-v2/`
  - Monitoring config: `monitoring/alertmanager.yml:32` references "La Factoria Prometheus"
  - User confirmation: "it is called 'La Factoria'"

### Action Items
- All future references must use "La Factoria"
- Simplified version should be "la-factoria-simple" not "tikal-simple"
- Update any generated documentation to reflect correct name

### Learning
Always verify project name from multiple sources before using throughout documentation. When in doubt, ask for clarification.