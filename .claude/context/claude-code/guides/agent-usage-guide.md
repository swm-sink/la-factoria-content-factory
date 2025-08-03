# How to Use La Factoria Claude Code Agents

## 🚀 Quick Start Guide

Now that the agents are set up, here's how to actually use them in Claude Code:

### 1. **View Available Agents**
```bash
# In Claude Code terminal, type:
@
# This will show you all available agents including our new La Factoria agents
```

### 2. **Invoke Specific Agents**

#### **For Complete Content Generation (Start Here)**
```bash
@orchestrator Generate a complete educational content set for "Introduction to Python Programming" targeting high school students (ages 15-17). Include all 8 content types with focus on practical coding skills and real-world applications.
```

#### **For Research Foundation**
```bash
@content-researcher Research comprehensive information about machine learning fundamentals for undergraduate computer science students. Focus on supervised learning, neural networks, and practical applications. Ensure sources are academic and current (within 3 years).
```

#### **For Educational Structure**
```bash
@master-outline Create a master educational outline for "Climate Change Science" targeting middle school students (ages 11-14). Include clear learning objectives using Bloom's taxonomy and ensure age-appropriate complexity progression.
```

#### **For Detailed Study Materials**
```bash
@study-guide Using the master outline provided, create a comprehensive study guide for "Photosynthesis" for 9th grade biology students. Include practice exercises, self-assessment tools, and real-world applications.
```

#### **For Audio Content**
```bash
@podcast-script Transform the study guide content into an engaging 15-minute podcast script about "The Water Cycle" for 6th grade students. Include conversational elements, questions for listeners, and clear audio production notes.
```

#### **For Quality Validation**
```bash
@educational-validator Review this chemistry study guide for age-appropriateness, educational standards compliance, and accessibility. Target audience is 10th grade students. Provide detailed assessment with improvement recommendations.
```

```bash
@quality-assessor Conduct comprehensive quality assessment of this complete content set for "Algebra Basics". Provide numerical scores across all dimensions and specific improvement recommendations with priority rankings.
```

### 3. **Multi-Agent Workflows**

#### **Complete Educational Content Pipeline**
```bash
# Step 1: Research
@content-researcher Research "Renewable Energy Technologies" for high school environmental science. Focus on solar, wind, and hydroelectric power with current statistics and real-world examples.

# Step 2: Structure  
@master-outline Using the research provided, create educational outline for "Renewable Energy Technologies" targeting grades 9-12. Include hands-on project opportunities and assessment strategies.

# Step 3: Content Creation
@study-guide Create comprehensive study guide based on the outline and research for renewable energy unit.

@podcast-script Create engaging podcast script covering key renewable energy concepts from the study guide.

# Step 4: Quality Assurance
@educational-validator Validate all content for educational standards and age-appropriateness.

@quality-assessor Provide final quality assessment with scores and recommendations.
```

#### **Iterative Improvement Workflow**
```bash
# Initial generation
@orchestrator Create educational content for "Basic Statistics" targeting college freshmen.

# Quality review
@quality-assessor Assess the statistics content and identify improvement opportunities.

# Targeted improvements
@study-guide Revise the statistics study guide based on quality assessor feedback, focusing on clarity and engagement improvements.

# Final validation
@educational-validator Confirm revised content meets all educational standards.
```

### 4. **Agent Coordination Examples**

#### **Research-Heavy Content**
```bash
@content-researcher + @master-outline + @study-guide
Research ancient civilizations → Create educational structure → Develop comprehensive materials
```

#### **Quality-Focused Pipeline**
```bash
@orchestrator + @educational-validator + @quality-assessor
Generate content → Validate standards → Assess quality → Iterate improvements
```

#### **Multi-Format Content**
```bash
@master-outline + @study-guide + @podcast-script
Create structure → Develop study materials → Transform to audio format
```

## 🎯 Best Practices

### **Starting a New Project**
1. Always begin with `@content-researcher` for factual foundation
2. Use `@master-outline` to establish educational structure
3. Generate specific content with specialized agents
4. Validate with `@educational-validator` and `@quality-assessor`

### **Quality Assurance**
- Run validation agents on ALL content before delivery
- Address improvement recommendations iteratively
- Maintain educational effectiveness ≥0.75 and factual accuracy ≥0.85

### **Coordination Tips**
- Use `@orchestrator` for complex multi-content projects
- Reference previous agent outputs in subsequent requests
- Specify target audience clearly in all requests
- Request specific improvements based on validator feedback

## 📊 Expected Outcomes

### **Quality Standards**
- Educational Effectiveness: ≥0.75
- Factual Accuracy: ≥0.85  
- Age Appropriateness: ≥0.80
- Accessibility Compliance: ≥0.80
- Overall Quality Score: ≥0.80

### **Performance Targets**
- Complete content set: ~8 minutes generation time
- Individual content pieces: ~2-3 minutes
- Quality validation: ~1-2 minutes
- Revision cycles: ~3-5 minutes

## 🔧 Troubleshooting

### **If Agents Don't Appear**
- Verify `.claude/agents/` directory exists
- Check agent files are properly formatted Markdown
- Restart Claude Code terminal session

### **If Quality Standards Aren't Met**
- Use iterative improvement with validator feedback
- Specify more detailed requirements in prompts
- Leverage research agent for better source foundation

### **For Complex Projects**
- Start with `@orchestrator` for workflow coordination
- Break large topics into smaller, manageable chunks
- Use multiple validation cycles for iterative improvement

The agents are now ready to create high-quality educational content! Start with `@orchestrator` for complete projects or use specialized agents for targeted tasks.