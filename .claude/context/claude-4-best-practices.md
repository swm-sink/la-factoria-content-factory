# Claude 4 Model Usage and Best Practices

## Model Overview

### Claude 4 Models
- **Claude Opus 4**: Highest level of intelligence and capability
- **Claude Sonnet 4**: High intelligence and balanced performance  
- Both support text and image input with 200K context window
- Multilingual and vision-capable
- Enhanced reasoning, coding, and long-context handling

### Model Selection
```python
# Production model names
CLAUDE_OPUS_4 = "claude-opus-4-20250514"
CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"

# Choose model based on use case
def select_model(task_complexity: str, budget_tier: str) -> str:
    if task_complexity == "high" and budget_tier == "premium":
        return CLAUDE_OPUS_4
    elif task_complexity in ["medium", "high"] and budget_tier == "standard":
        return CLAUDE_SONNET_4
    else:
        return CLAUDE_SONNET_4  # Default for most use cases
```

### Pricing (as of 2025)
- **Opus 4**: $15/MTok input, $75/MTok output
- **Sonnet 4**: $3/MTok input, $15/MTok output

## Prompt Engineering Best Practices

### 1. Clear and Direct Instructions
```python
# Bad prompt
prompt = "Make study content about Python"

# Good prompt
prompt = """
Create a comprehensive study guide about Python programming for high school students.

Requirements:
- 8-10 key concepts with clear explanations
- 2-3 practical examples for each concept
- 5 practice questions with answers
- Beginner-friendly language
- Approximately 1500-2000 words

Focus on:
1. Variables and data types
2. Control structures (if/else, loops)
3. Functions
4. Lists and dictionaries
5. Basic file operations
"""
```

### 2. XML Tags for Structure
```python
def create_structured_prompt(topic: str, audience: str, format: str) -> str:
    return f"""
<task>
Generate educational content about {topic} for {audience} in {format} format.
</task>

<audience>
- Education level: {audience}
- Prior knowledge: Assume basic understanding
- Learning style: Visual and practical examples preferred
</audience>

<format_requirements>
- Structure: Clear headings and subheadings
- Length: 1000-1500 words
- Examples: Include at least 3 practical examples
- Assessment: End with 3-5 review questions
</format_requirements>

<tone>
Engaging, clear, and educational. Use analogies where helpful.
</tone>

<output_format>
# [Title]

## Introduction
[Brief overview and learning objectives]

## Key Concepts
[Main content with examples]

## Summary
[Key takeaways]

## Review Questions
[Assessment questions]
</output_format>
"""
```

### 3. System Prompts for Role Definition
```python
EDUCATIONAL_CONTENT_SYSTEM_PROMPT = """
You are an expert educational content creator with 15+ years of experience in curriculum design and instructional writing. Your expertise includes:

- Adapting content for different learning levels
- Creating engaging and memorable educational materials
- Using evidence-based learning principles
- Incorporating active learning techniques
- Following educational standards and best practices

Your goal is to create high-quality educational content that:
- Meets specific learning objectives
- Engages students with clear explanations and examples
- Provides appropriate challenge level
- Includes assessment opportunities
- Uses accessible and inclusive language

Always consider the learner's perspective and optimize for comprehension and retention.
"""

def create_content_with_system_prompt(user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": EDUCATIONAL_CONTENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    return messages
```

### 4. Chain of Thought Reasoning
```python
def create_reasoning_prompt(topic: str, complexity: str) -> str:
    return f"""
Create educational content about {topic} for {complexity} level students.

Before creating the content, think through this step by step:

<thinking>
1. What are the core concepts students need to understand?
2. What prior knowledge can I assume?
3. What are the most common misconceptions about this topic?
4. What real-world examples would make this relatable?
5. How can I structure this for optimal learning?
6. What questions should I include to check understanding?
</thinking>

Now create the educational content based on your analysis above.
"""
```

### 5. Few-Shot Examples for Educational Content
```python
EDUCATIONAL_EXAMPLES = """
Example 1:
Topic: Functions in Python
Audience: High school students
Output:
# Understanding Functions in Python

## What is a Function?
Think of a function like a recipe. Just as a recipe takes ingredients (inputs) and produces a dish (output), a Python function takes data and produces a result.

```python
def greet(name):
    return f"Hello, {name}!"

# Using the function
message = greet("Alice")
print(message)  # Output: Hello, Alice!
```

## Why Use Functions?
- **Reusability**: Write once, use many times
- **Organization**: Keep code tidy and logical
- **Testing**: Easier to test small pieces

Example 2:
Topic: Photosynthesis
Audience: Middle school students  
Output:
# Photosynthesis: How Plants Make Food

## The Amazing Food Factory
Imagine if you could make your own food just by standing in sunlight! That's exactly what plants do through photosynthesis.

## The Recipe for Plant Food
Plants need three main ingredients:
1. **Sunlight** (energy source)
2. **Water** (from roots)
3. **Carbon dioxide** (from air)

## The Chemical Equation
6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂

Translation: Carbon dioxide + Water + Sunlight = Sugar + Oxygen

Now create similar educational content for the given topic.
"""
```

### 6. Long Context Optimization
```python
def optimize_for_long_context(content_sections: list, context_limit: int = 200000) -> str:
    """Optimize prompts for Claude's 200K context window."""
    
    # Estimate token count (rough approximation: 1 token ≈ 4 characters)
    estimated_tokens = sum(len(section) // 4 for section in content_sections)
    
    if estimated_tokens > context_limit * 0.8:  # Use 80% of limit for safety
        # Prioritize most important sections
        priority_sections = content_sections[:5]  # Keep first 5 sections
        summary_sections = [f"Summary: {section[:200]}..." for section in content_sections[5:]]
        optimized_sections = priority_sections + summary_sections
    else:
        optimized_sections = content_sections
    
    return "\n\n".join(optimized_sections)
```

## Production Implementation Patterns

### 1. Content Generation Service
```python
import anthropic
from typing import Dict, List, Optional
import logging

class ClaudeContentGenerator:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    async def generate_educational_content(
        self,
        topic: str,
        content_type: str,
        audience_level: str,
        additional_requirements: Optional[str] = None
    ) -> Dict:
        """Generate educational content with Claude 4."""
        
        prompt = self._build_educational_prompt(
            topic, content_type, audience_level, additional_requirements
        )
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": EDUCATIONAL_CONTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            
            # Log usage for monitoring
            self.logger.info(f"Generated {content_type} content - Topic: {topic}, Audience: {audience_level}")
            
            return {
                "content": content,
                "metadata": {
                    "topic": topic,
                    "content_type": content_type,
                    "audience_level": audience_level,
                    "model": self.model,
                    "token_usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {str(e)}")
            raise
    
    def _build_educational_prompt(
        self, topic: str, content_type: str, audience_level: str, additional_requirements: Optional[str]
    ) -> str:
        base_prompt = f"""
<task>
Create a {content_type} about {topic} for {audience_level} students.
</task>

<content_type_specifications>
{self._get_content_type_specs(content_type)}
</content_type_specifications>

<audience_considerations>
- Education level: {audience_level}
- Adjust vocabulary and complexity accordingly
- Include relatable examples and analogies
- Consider attention span and engagement needs
</audience_considerations>"""

        if additional_requirements:
            base_prompt += f"""

<additional_requirements>
{additional_requirements}
</additional_requirements>"""

        base_prompt += """

<quality_standards>
- Accuracy: Ensure all information is correct and up-to-date
- Clarity: Use clear, concise language appropriate for the audience
- Engagement: Include interactive elements, questions, or interesting facts
- Structure: Organize content logically with clear headings
- Completeness: Cover the topic comprehensively within scope
</quality_standards>

Please create the educational content following these guidelines."""

        return base_prompt
    
    def _get_content_type_specs(self, content_type: str) -> str:
        specifications = {
            "study_guide": """
- Length: 1500-2500 words
- Structure: Introduction, key concepts (5-8 main points), examples, summary, practice questions
- Include: Definitions, explanations, real-world applications, review questions
- Format: Use headings, bullet points, and numbered lists for clarity
            """,
            "flashcards": """
- Create 15-25 flashcard pairs
- Front: Clear, concise question or prompt
- Back: Comprehensive answer with brief explanation
- Include: Key terms, concepts, formulas, or facts
- Difficulty: Mix of basic recall and application questions
            """,
            "quiz": """
- 10-15 questions of varying difficulty
- Question types: Multiple choice, true/false, short answer
- Include: Answer key with explanations
- Topics: Cover all major concepts from the subject
- Progressive difficulty: Start easier, increase complexity
            """,
            "lesson_plan": """
- Duration: 45-60 minute lesson
- Structure: Objectives, materials, activities, assessment
- Include: Opening hook, main instruction, guided practice, independent practice
- Activities: Interactive and engaging for the age group
- Assessment: Formative and summative evaluation methods
            """
        }
        return specifications.get(content_type, "Create comprehensive educational content appropriate for the specified audience.")
```

### 2. Prompt Template Management
```python
class PromptTemplateManager:
    def __init__(self):
        self.templates = {
            "study_guide": self._load_study_guide_template(),
            "flashcards": self._load_flashcards_template(),
            "quiz": self._load_quiz_template(),
            "lesson_plan": self._load_lesson_plan_template()
        }
    
    def get_template(self, content_type: str, **kwargs) -> str:
        template = self.templates.get(content_type)
        if not template:
            raise ValueError(f"Unknown content type: {content_type}")
        
        return template.format(**kwargs)
    
    def _load_study_guide_template(self) -> str:
        return """
Create a comprehensive study guide about {topic} for {audience_level} students.

<learning_objectives>
By the end of this study guide, students will be able to:
- Understand the fundamental concepts of {topic}
- Apply key principles in practical scenarios
- Analyze and evaluate related information
- Synthesize knowledge for problem-solving
</learning_objectives>

<structure_requirements>
1. **Introduction** (100-150 words)
   - Hook to capture interest
   - Overview of what will be covered
   - Why this topic matters
   
2. **Core Concepts** (1000-1200 words)
   - 5-7 main concepts with clear explanations
   - Real-world examples for each concept
   - Common misconceptions and clarifications
   
3. **Applications and Examples** (300-400 words)
   - Practical applications
   - Step-by-step worked examples
   - Case studies or scenarios
   
4. **Summary and Key Takeaways** (100-150 words)
   - Main points recap
   - Connections between concepts
   - Why these concepts matter
   
5. **Practice and Review** (200-300 words)
   - 5-7 review questions with answers
   - Self-assessment checklist
   - Further learning suggestions
</structure_requirements>

<audience_specific_guidelines>
{self._get_audience_guidelines('{audience_level}')}
</audience_specific_guidelines>

Create the study guide following these specifications.
"""
    
    def _get_audience_guidelines(self, audience_level: str) -> str:
        guidelines = {
            "elementary": """
- Use simple vocabulary and short sentences
- Include lots of visual descriptions and analogies
- Add fun facts and interesting connections
- Keep explanations concrete rather than abstract
- Use familiar examples from daily life
            """,
            "middle_school": """
- Balance simple and more advanced vocabulary
- Include relatable examples from student experiences
- Add some abstract thinking opportunities
- Use analogies and metaphors effectively
- Encourage critical thinking with guided questions
            """,
            "high_school": """
- Use grade-appropriate academic vocabulary
- Include complex examples and scenarios
- Encourage analytical and critical thinking
- Connect to current events and real-world issues
- Prepare for standardized test format questions
            """,
            "college": """
- Use advanced academic vocabulary and concepts
- Include research-based examples and evidence
- Encourage critical analysis and evaluation
- Connect to professional and academic applications
- Include references for further study
            """
        }
        return guidelines.get(audience_level, guidelines["high_school"])
```

### 3. Quality Assurance and Validation
```python
class ContentQualityValidator:
    def __init__(self, claude_client):
        self.claude_client = claude_client
    
    async def validate_educational_content(self, content: str, topic: str, audience: str) -> Dict:
        """Validate content quality using Claude as a judge."""
        
        validation_prompt = f"""
Please evaluate the following educational content about {topic} for {audience} students.

<content_to_evaluate>
{content}
</content_to_evaluate>

<evaluation_criteria>
Rate each criterion on a scale of 1-5 (5 being excellent):

1. **Accuracy**: Is the information correct and up-to-date?
2. **Clarity**: Is the content easy to understand for the target audience?
3. **Completeness**: Does it cover the topic comprehensively?
4. **Engagement**: Is it interesting and engaging for students?
5. **Structure**: Is it well-organized with logical flow?
6. **Appropriateness**: Is it suitable for the {audience} level?
7. **Educational Value**: Does it effectively teach the concepts?
</evaluation_criteria>

<response_format>
{{
  "overall_score": [1-5],
  "criteria_scores": {{
    "accuracy": [1-5],
    "clarity": [1-5], 
    "completeness": [1-5],
    "engagement": [1-5],
    "structure": [1-5],
    "appropriateness": [1-5],
    "educational_value": [1-5]
  }},
  "strengths": ["list of 2-3 main strengths"],
  "improvements": ["list of 2-3 specific improvement suggestions"],
  "recommendations": "overall recommendation and next steps"
}}
</response_format>

Provide your evaluation in the exact JSON format above.
"""

        try:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.1,  # Low temperature for consistent evaluation
                messages=[
                    {"role": "user", "content": validation_prompt}
                ]
            )
            
            import json
            evaluation = json.loads(response.content[0].text)
            return evaluation
            
        except Exception as e:
            return {
                "error": f"Validation failed: {str(e)}",
                "overall_score": 0,
                "criteria_scores": {},
                "strengths": [],
                "improvements": ["Unable to validate content"],
                "recommendations": "Manual review required"
            }
```

### 4. Cost Optimization Strategies
```python
class CostOptimizedGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.token_costs = {
            "claude-opus-4-20250514": {"input": 15/1000000, "output": 75/1000000},
            "claude-sonnet-4-20250514": {"input": 3/1000000, "output": 15/1000000}
        }
    
    def estimate_cost(self, prompt: str, expected_output_tokens: int, model: str) -> float:
        """Estimate cost before making API call."""
        input_tokens = len(prompt) // 4  # Rough estimation
        
        input_cost = input_tokens * self.token_costs[model]["input"]
        output_cost = expected_output_tokens * self.token_costs[model]["output"]
        
        return input_cost + output_cost
    
    def choose_cost_effective_model(self, complexity: str, budget_limit: float) -> str:
        """Choose the most cost-effective model for the task."""
        
        # Estimate token requirements based on complexity
        token_estimates = {
            "simple": 1500,
            "medium": 3000,
            "complex": 4500
        }
        
        expected_tokens = token_estimates.get(complexity, 3000)
        
        # Calculate costs for each model
        costs = {}
        for model in self.token_costs:
            # Assume prompt is ~500 tokens
            cost = self.estimate_cost("x" * 2000, expected_tokens, model)  
            costs[model] = cost
        
        # Choose most cost-effective option within budget
        for model, cost in sorted(costs.items(), key=lambda x: x[1]):
            if cost <= budget_limit:
                return model
        
        # If no model fits budget, return cheapest option
        return min(costs.keys(), key=lambda x: costs[x])
    
    async def generate_with_budget_control(
        self, 
        prompt: str, 
        max_budget: float,
        content_type: str = "medium"
    ) -> Dict:
        """Generate content while staying within budget."""
        
        model = self.choose_cost_effective_model(content_type, max_budget)
        estimated_cost = self.estimate_cost(prompt, 3000, model)
        
        if estimated_cost > max_budget:
            return {
                "error": f"Estimated cost (${estimated_cost:.4f}) exceeds budget (${max_budget:.4f})",
                "suggested_model": model,
                "estimated_cost": estimated_cost
            }
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=min(4000, int(max_budget / self.token_costs[model]["output"])),
                messages=[{"role": "user", "content": prompt}]
            )
            
            actual_cost = (
                response.usage.input_tokens * self.token_costs[model]["input"] +
                response.usage.output_tokens * self.token_costs[model]["output"]
            )
            
            return {
                "content": response.content[0].text,
                "model_used": model,
                "actual_cost": actual_cost,
                "budget_remaining": max_budget - actual_cost,
                "token_usage": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            return {"error": f"Generation failed: {str(e)}"}
```

## Sources
26. Anthropic Claude 4 Model Documentation
27. Anthropic Prompt Engineering Best Practices
28. Claude 4 Pricing and Performance Guidelines
29. Production Claude Integration Patterns
30. Educational Content Generation with Claude 4