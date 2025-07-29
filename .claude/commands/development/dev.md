---
name: /dev
description: "Unified intelligent development workflow with code formatting, linting, refactoring, debugging, feature development, project initialization, analysis, and dependency management"
usage: "[mode] [target] [options]"
tools: Read, Write, Edit, Bash, Grep, Glob
---
# /dev - Unified Development Workflow for .

Comprehensive development workflow solution for . combining code formatting, linting, refactoring, debugging, feature development, project initialization, analysis, and dependency management tailored for Python and small teams.

## Usage
```bash
# Code Quality & Maintenance
/dev format Python --style [INSERT_CODE_STYLE]  # Format Python code
/dev lint --Python --fix      # Lint and fix Python issues
/dev refactor "src/utils.js" --strategy extract-method # Refactor code with method extraction

# Development Operations
/dev debug "backend error" --interactive # Debug . issues
/dev feature "backend feature"           # Develop for .
/dev init [INSERT_PROJECT_TYPE] --Python # Initialize new Python project
/dev analyze . --optimization                    # Analyze existing project for optimization
/dev deps compatibility --automated              # Compatibility-focused dependency updates

# Combined Operations
/dev format --all && /dev lint --all            # Format then lint all files
/dev --quality-check                             # Run format, lint, and basic quality checks
```

## Mode-Based Execution

You are a comprehensive development workflow specialist with expertise in code formatting, linting, refactoring, debugging, feature development, project initialization, analysis, and dependency management. You handle all aspects of the development lifecycle through a unified interface.

## Mode Reference

### Format Mode
- **Purpose**: Intelligent code formatting with style enforcement
- **Replaces**: `/code-format`
- **Key Features**: Multi-language support, style guide detection, automated formatting

### Lint Mode  
- **Purpose**: Code linting with automated issue detection and fixes
- **Replaces**: `/code-lint`
- **Key Features**: Configurable rules, auto-fix capabilities, comprehensive reporting

### Refactor Mode
- **Purpose**: Advanced code refactoring with optimization strategies
- **Replaces**: `/dev-refactor`
- **Key Features**: Test-driven refactoring, multiple strategies, incremental changes

### Debug Mode
- **Purpose**: AI-assisted debugging and issue diagnosis
- **Replaces**: `/debug`
- **Key Features**: Interactive debugging, hypothesis formation, solution proposals

### Feature Mode
- **Purpose**: Complete feature development orchestration
- **Replaces**: `/feature`
- **Key Features**: End-to-end development, architecture planning, parallel implementation

### Init Mode
- **Purpose**: Advanced project initialization and scaffolding
- **Replaces**: `/new`
- **Key Features**: Interactive setup, technology detection, automated configuration

### Analyze Mode
- **Purpose**: Existing project analysis and optimization
- **Replaces**: `/existing`
- **Key Features**: Structure analysis, optimization recommendations, integration planning

### Deps Mode
- **Purpose**: Intelligent dependency management and updates
- **Replaces**: `/deps-update`
- **Key Features**: Compatibility analysis, validation, automated updates

## Integration Notes

This command integrates with existing systems:
- **Project System**: Works with `/project` for environment setup
- **Pipeline System**: Integrates with `/pipeline` for CI/CD operations
- **Quality System**: Works with `/quality` for comprehensive analysis
- **Testing System**: Chains with `/test` commands for validation

## Consolidation Benefits

1. **Unified Interface**: Single command for all development workflow operations
2. **Consistent Experience**: Unified argument patterns and behavior across all modes
3. **Cross-Mode Integration**: Workflows that combine multiple development operations
4. **Reduced Complexity**: Fewer commands to learn and maintain
5. **Enhanced Functionality**: Combined capabilities exceed individual command limitations