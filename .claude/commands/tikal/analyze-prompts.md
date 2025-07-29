---
name: /tikal-analyze-prompts
description: "Analyze Tikal's existing prompts for optimization opportunities"
usage: /tikal-analyze-prompts [prompt-file-or-directory]
category: tikal-commands
tools: Read, Glob, Grep
---

# Tikal Prompt Analysis and Optimization

I'll analyze Tikal's existing prompt templates to identify optimization opportunities and provide specific recommendations.

## Your Task
Analyze prompts in: $ARGUMENTS

## Analysis Framework

### 1. **Token Efficiency Analysis**
I'll examine each prompt for:
- **Redundant Instructions**: Repeated requirements that can be consolidated
- **Verbose Phrasing**: Unnecessarily long instructions that can be simplified
- **Duplicate Constraints**: Same requirements stated multiple times
- **Implicit Requirements**: Things that don't need explicit stating

### 2. **Educational Effectiveness**
I'll assess prompts for:
- **Learning Objective Clarity**: Are educational goals clearly defined?
- **Audience Appropriateness**: Is the language level specified correctly?
- **Pedagogical Structure**: Does it follow educational best practices?
- **Assessment Integration**: Are evaluation criteria included?

### 3. **Quality Requirements Analysis**
I'll evaluate:
- **Specificity**: Are quality requirements concrete and measurable?
- **Consistency**: Do all prompts have similar quality standards?
- **Completeness**: Are all necessary quality aspects covered?
- **Validation**: Can outputs be easily validated against requirements?

### 4. **Structure and Organization**
I'll check for:
- **Logical Flow**: Information presented in optimal order
- **Section Clarity**: Clear delineation between different requirements
- **Context Placement**: Background info positioned effectively
- **Output Specification**: Clear format requirements

### 5. **Best Practices Compliance**
I'll verify adherence to:
- **Prompt Engineering Principles**: Clear instructions, examples, constraints
- **Educational Standards**: Age-appropriate, inclusive, accessible
- **JSON Output Standards**: Proper schema specification
- **Safety Requirements**: PII prevention, content appropriateness

## Analysis Process

### Step 1: Prompt Inventory
- Locate all prompt files in specified directory
- Categorize by content type
- Note file sizes and token estimates

### Step 2: Detailed Analysis
For each prompt, I'll analyze:
- Current token count and structure
- Redundancies and inefficiencies
- Missing educational elements
- Quality requirement gaps
- Optimization opportunities

### Step 3: Comparative Analysis
- Compare similar prompts for consistency
- Identify common patterns across prompts
- Find shared elements that could be extracted
- Note divergent quality standards

### Step 4: Optimization Recommendations
Generate specific suggestions for:
- Token reduction strategies
- Educational enhancement opportunities
- Quality requirement improvements
- Structural reorganization
- Reusable component extraction

## Output Report

### Summary Statistics
```
Total Prompts Analyzed: X
Average Token Count: Y
Token Reduction Potential: Z%
Quality Improvement Opportunities: N
```

### Per-Prompt Analysis
```
Prompt: study_guide.md
Current Tokens: ~850
Optimized Tokens: ~600 (29% reduction)
Issues Found:
- Redundant JSON structure explanation (3 times)
- Missing audience level specification
- Vague quality requirements
- No educational framework reference

Recommendations:
1. Consolidate JSON requirements into single section
2. Add explicit audience parameters
3. Include specific quality metrics
4. Reference educational standards component
```

### Global Optimization Opportunities
1. **Create Shared Components**:
   - JSON output specifications
   - Quality requirements
   - Educational standards
   - Safety/PII guidelines

2. **Standardize Structure**:
   - Consistent section ordering
   - Unified constraint format
   - Common validation rules

3. **Enhance Educational Focus**:
   - Add learning objective templates
   - Include assessment criteria
   - Specify engagement requirements

### Implementation Priority
1. **High Impact** (>30% improvement):
   - Remove redundant JSON explanations
   - Consolidate validation rules
   - Extract common components

2. **Medium Impact** (15-30% improvement):
   - Standardize quality requirements
   - Add educational parameters
   - Improve structure consistency

3. **Low Impact** (<15% improvement):
   - Minor wording optimizations
   - Format standardization
   - Additional examples

## Next Steps
Based on the analysis, I recommend:
1. Creating optimized versions of each prompt
2. Implementing shared component system
3. Establishing prompt maintenance guidelines
4. Setting up A/B testing framework
5. Creating prompt performance metrics

This analysis provides the foundation for systematic prompt improvement in Tikal's content generation system.