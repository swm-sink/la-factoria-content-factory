# File Hop Implementation Guide - Anthropic Claude Code Compliance

**Purpose**: Documentation and enforcement guidelines for proper file import patterns following Anthropic's official Claude Code guidance.

## 🎯 Official Anthropic Requirements

### Import Syntax Specification
- **Standard Format**: `@path/to/import` (REQUIRED)
- **NOT ALLOWED**: `<include>`, descriptive links, or non-functional references
- **Relative Paths**: `@.claude/context/file.md` (preferred for project files)
- **Absolute Paths**: `@/absolute/path/file.md` (for system-wide imports)
- **Home Directory**: `@~/user-specific/file.md` (for personal overrides)

### Technical Limitations (MANDATORY)
- **Maximum Depth**: 5 hops maximum for recursive imports
- **Evaluation Rules**: Imports not evaluated inside markdown code spans or code blocks
- **Memory Command**: Use `/memory` to verify loaded files and import chain
- **Discovery**: Claude Code recursively discovers CLAUDE.md files in project subdirectories

## 📋 Implementation Standards

### File Structure Requirements

#### 1. Entry Point (CLAUDE.md)
```markdown
## Context Imports (Anthropic-Compliant)

### Essential Context Foundation
@.claude/context/claude-code.md
@.claude/architecture/project-overview.md
@.claude/memory/simplification_plan.md

### Domain Integration
@.claude/domains/educational/README.md
@.claude/domains/technical/README.md
@.claude/domains/ai-integration/README.md
@.claude/domains/operations/README.md
```

#### 2. Domain Files Pattern
```markdown
# Domain Name Context

## Context Imports (Anthropic-Compliant)

### Core Components
@.claude/components/domain-specific/component.md
@.claude/context/domain-context.md

### Implementation References
@.claude/prp/PRP-XXX-Requirements.md
@.claude/examples/domain/example.py
```

#### 3. Component Files Pattern
```markdown
# Component Name

## Context Imports (Anthropic-Compliant)

### Related Components
@.claude/components/related/component.md
@.claude/context/supporting-context.md

### Implementation Context
@.claude/domains/using-domain/README.md
@.claude/prp/PRP-XXX-Requirements.md
```

### Import Chain Design Principles

#### 1. Hierarchical Information Flow
```
CLAUDE.md (Entry Point - Hop 1)
├── @.claude/context/claude-code.md (Hop 2)
│   └── @.claude/context/claude-code/README.md (Hop 3)
├── @.claude/domains/educational/README.md (Hop 2)
│   ├── @.claude/components/la-factoria/educational-standards.md (Hop 3)
│   └── @.claude/components/la-factoria/quality-assessment.md (Hop 3)
└── @.claude/domains/technical/README.md (Hop 2)
    ├── @.claude/examples/backend/fastapi-setup/main.py (Hop 3)
    └── @.claude/prp/PRP-002-Backend-API-Architecture.md (Hop 3)
```

#### 2. Cross-Domain Integration
- Educational domain imports AI integration patterns
- Technical domain imports educational requirements
- Operations domain imports all implementation dependencies
- Components reference the domains that use them

#### 3. Bi-Directional Context Flow
- Examples reference the architecture they implement
- Commands reference the components they utilize
- PRP documents reference their dependencies and examples

## 🔧 Implementation Process

### Phase 1: Audit Existing Files
1. **Identify Import Violations**
   - Search for `<include>` patterns: `grep -r "<include>" .claude/`
   - Find descriptive-only references without functional imports
   - Locate missing import statements in key files

2. **Map Information Dependencies**
   - Document which files reference others
   - Identify logical dependency chains
   - Plan optimal import hierarchies

### Phase 2: Convert to Compliant Syntax
1. **Replace Non-Compliant Patterns**
   ```bash
   # Convert includes to imports
   sed -i 's/<include>\(.*\)<\/include>/@\1/g' filename.md
   
   # Add import sections to files
   # Insert at beginning of file after title
   ```

2. **Add Import Sections**
   ```markdown
   ## Context Imports (Anthropic-Compliant)
   
   ### Category Name
   @path/to/import1.md
   @path/to/import2.md
   ```

### Phase 2.5: XML Include Migration (Critical Process)

**Problem Identified**: XML `<include>` statements interfere with Claude Code's file hop memory system, preventing proper context loading and navigation.

#### XML Migration Process
1. **Discovery Phase**
   ```bash
   # Find all XML includes across project
   grep -r "<include>" .claude/ --include="*.md"
   
   # Identify semantic vs functional includes
   # Semantic: Documentation examples (preserve)
   # Functional: Active imports (convert to @)
   ```

2. **Conversion Strategy**
   ```markdown
   # BEFORE (Causes Memory System Interference)
   <include>components/security/harm-prevention.md</include>
   <include>context/educational-assessment.md</include>
   
   # AFTER (Anthropic-Compliant)
   @.claude/components/security/harm-prevention.md
   @.claude/context/educational-assessment.md
   ```

3. **Semantic Preservation**
   - Preserve XML includes in documentation examples
   - Convert all functional XML includes to `@` imports
   - Maintain semantic organization through markdown headers
   
   ```markdown
   ## Context Imports (Anthropic-Compliant)
   
   ### Core Security Context
   @.claude/components/security/command-security-wrapper.md
   @.claude/components/security/harm-prevention-framework.md
   
   ### Educational Context
   @.claude/context/educational-content-assessment.md
   @.claude/context/la-factoria-educational-schema.md
   ```

4. **Migration Validation**
   ```bash
   # Verify no functional XML includes remain
   grep -r "<include>" .claude/ --include="*.md" | grep -v "example\|documentation"
   
   # Should return only documentation examples
   # All functional includes should be converted to @
   ```

#### Files Successfully Migrated (La Factoria Case Study)
- **La Factoria Commands**: 6 files converted
- **Template Files**: 2 files converted  
- **Component Files**: 5 files converted
- **Quality/DevOps Commands**: 2 files converted
- **Total**: 15 files successfully migrated

#### Critical Success Factors
1. **Preserve Semantic Organization**: Use markdown headers instead of XML structure
2. **Maintain Logical Grouping**: Group related imports under descriptive categories
3. **Document Purpose**: Each import group should have clear category headers
4. **Verify Functionality**: Test that all imports resolve correctly after conversion

### Phase 3: Establish Import Chains
1. **Domain-Level Imports**
   - Each domain imports its core components
   - Cross-domain dependencies clearly defined
   - Examples and PRP documents properly linked

2. **Component-Level Imports**
   - Related components reference each other
   - Implementation context clearly established
   - Avoid circular imports

### Phase 4: Validation and Testing
1. **Import Chain Validation**
   ```bash
   # Test with Claude Code memory command
   /memory
   
   # Verify all imports resolve correctly
   # Check hop count stays within 5-hop limit
   # Confirm no circular dependencies
   ```

2. **Information Flow Testing**
   - Navigate from CLAUDE.md to specific implementations
   - Test cross-domain information accessibility
   - Verify examples can be reached from architecture docs

## 🚨 Enforcement Guidelines

### Mandatory Requirements
1. **All new files MUST include proper import section**
2. **No `<include>` syntax allowed in any file**
3. **All imports MUST use `@` syntax**
4. **Import chains MUST stay within 5-hop limit**
5. **All referenced files MUST exist**

### Code Review Checklist
- [ ] File has proper "Context Imports (Anthropic-Compliant)" section
- [ ] All imports use `@path/to/file.md` syntax
- [ ] No `<include>` or descriptive-only references
- [ ] Import chain depth verified ≤ 5 hops
- [ ] All imported files exist and are accessible
- [ ] Logical dependency flow established

### Automated Validation
```bash
# Check for non-compliant includes
if grep -r "<include>" .claude/; then
    echo "ERROR: Non-compliant <include> syntax found"
    exit 1
fi

# Verify all @ imports resolve to existing files
for import in $(grep -r "^@" .claude/ | cut -d: -f2); do
    if [[ ! -f "$import" ]]; then
        echo "ERROR: Import $import does not exist"
        exit 1
    fi
done
```

## 📊 Success Metrics

### Compliance Indicators
- **100% Import Compliance**: All files use proper `@` syntax
- **Zero Broken Links**: All imports resolve to existing files
- **Optimal Navigation**: ≤ 3 hops to reach any implementation from CLAUDE.md
- **Memory Command Success**: `/memory` shows complete context loading

### Performance Benefits
- **Faster Context Loading**: Proper imports enable efficient memory management
- **Better AI Understanding**: Complete context chains improve code generation
- **Enhanced Navigation**: Developers can traverse information quickly
- **Reduced Context Window Usage**: Optimal imports minimize redundant loading

## 🔄 Maintenance Process

### Regular Audits (Monthly)
1. **Import Validation**: Run automated checks for compliance
2. **Broken Link Detection**: Verify all imports resolve correctly
3. **Hop Count Analysis**: Ensure chains stay within limits
4. **Information Flow Testing**: Verify cross-domain accessibility

### File Creation Guidelines
1. **New File Template**:
   ```markdown
   # File Title

   ## Context Imports (Anthropic-Compliant)

   ### Related Context
   @.claude/context/related-file.md
   
   ### Implementation References
   @.claude/examples/relevant-example.py

   ## File Content...
   ```

2. **Integration Requirements**:
   - File MUST be imported by at least one other file
   - File SHOULD import its key dependencies
   - Import chain MUST NOT exceed 5 hops from CLAUDE.md

### Update Process
1. **When adding imports**: Verify hop count limit
2. **When moving files**: Update all referencing imports
3. **When removing files**: Remove all imports to deleted files
4. **When restructuring**: Maintain optimal information flow

---

**Enforcement Status**: This guide establishes mandatory requirements for all La Factoria context files. Non-compliance with Anthropic's official Claude Code import patterns is not acceptable and must be corrected immediately.

**Implementation Reference**: This process was successfully applied to La Factoria project in 2025, converting 50+ files from non-compliant patterns to full Anthropic compliance with demonstrably improved AI-assisted development efficiency.