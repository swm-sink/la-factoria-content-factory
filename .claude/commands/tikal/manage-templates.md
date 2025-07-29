---
name: /tikal-templates
description: "Manage and optimize Tikal's prompt templates"
usage: /tikal-templates [list|compare|optimize|test] [template-name]
category: tikal-commands
tools: Read, Write, Glob, Grep
---

# Tikal Template Management System

I'll help you manage, compare, and optimize Tikal's prompt templates for maximum effectiveness.

## Your Task
Template operation: $ARGUMENTS

## Available Operations

### 1. **List Templates** (`list`)
Display all available templates with their characteristics:
- Template name and location
- Token count estimate
- Supported parameters
- Quality features
- Last optimization date

### 2. **Compare Templates** (`compare [original] [optimized]`)
Side-by-side comparison showing:
- Token reduction achieved
- New features added
- Quality improvements
- Parameter differences
- Educational enhancements

### 3. **Optimize Template** (`optimize [template-name]`)
Apply optimization techniques:
- Remove redundancies
- Consolidate instructions
- Enhance clarity
- Add educational best practices
- Improve output specifications

### 4. **Test Template** (`test [template-name] [sample-context]`)
Validate template functionality:
- Parameter substitution
- Output format compliance
- Quality requirement coverage
- Educational standard alignment

## Template Inventory

### Core Templates (Optimized)
Located in `.claude/templates/tikal/`:

1. **master-outline-optimized.md**
   - Token reduction: 35% from original
   - Features: Bloom's taxonomy, scaffolding, assessment points
   - Parameters: syllabus_text, audience_level, duration, learning_goal

2. **study-guide-optimized.md**
   - Token reduction: 30% from original
   - Features: Educational standards, quality checklist
   - Parameters: outline_json, topic, audience_level, learning_objectives

3. **flashcards-optimized.md**
   - Token reduction: 40% from original
   - Features: Cognitive science principles, spaced repetition
   - Parameters: outline_json, topic, audience_level, card_count

4. **podcast-script-optimized.md**
   - Token reduction: 25% from original
   - Features: Conversational techniques, audio optimization
   - Parameters: outline_json, audience_level, duration, style

### Templates Pending Optimization
From `app/core/prompts/v1/`:
- one_pager_summary.md
- detailed_reading_material.md
- faq_collection.md
- reading_guide_questions.md

## Optimization Framework

### Token Efficiency Techniques
1. **Consolidation**: Merge similar instructions
2. **Implicit Requirements**: Remove obvious constraints
3. **Structured Format**: Use consistent organization
4. **Reference Components**: Link to shared standards

### Quality Enhancement Methods
1. **Specificity**: Concrete, measurable requirements
2. **Educational Focus**: Learning objectives, assessment
3. **Validation**: Built-in quality checks
4. **Examples**: Clear output format demonstrations

### Template Best Practices
1. **Parameter Design**: Flexible, reusable variables
2. **Context Integration**: Leverage project knowledge
3. **Output Clarity**: Unambiguous format specs
4. **Error Prevention**: Validation checklists

## Usage Examples

### List All Templates
```
/tikal-templates list
```
Output: Complete inventory with metrics

### Compare Original vs Optimized
```
/tikal-templates compare study_guide study-guide-optimized
```
Output: Detailed comparison report

### Optimize Existing Template
```
/tikal-templates optimize one_pager_summary
```
Output: Optimized version with improvements noted

### Test Template
```
/tikal-templates test flashcards-optimized "Python basics,high-school"
```
Output: Validation results and sample output

## Quality Assurance

### Template Validation Criteria
- All required parameters documented
- Output format clearly specified
- Educational standards integrated
- Quality requirements measurable
- Token usage optimized

### Performance Metrics
- Token count reduction
- Output quality score
- Generation success rate
- User satisfaction rating
- Educational effectiveness

This management system ensures Tikal's templates remain optimized, consistent, and effective for educational content generation.