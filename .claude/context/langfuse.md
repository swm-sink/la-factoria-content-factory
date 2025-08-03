# Langfuse Integration Context

## Platform Overview

### Core Purpose
Langfuse is an open-source LLM engineering platform designed to help teams develop, debug, and improve AI applications through comprehensive observability and evaluation tools.

### Key Capabilities
1. **Tracing**: Detailed logs of LLM interactions with latency, cost, and performance metrics
2. **Prompt Management**: Version control, interactive playground, and deployment
3. **Evaluations**: LLM-as-a-judge, user feedback, manual annotations, custom scoring
4. **Analytics**: Performance monitoring and usage analytics

## Integration Setup

### Python SDK Installation
```bash
pip install langfuse
```

### Basic Configuration
```python
from langfuse import Langfuse

# Initialize Langfuse client
langfuse = Langfuse(
    secret_key="sk-lf-...",
    public_key="pk-lf-...",
    host="https://cloud.langfuse.com"  # or self-hosted URL
)
```

### Environment Variables
```bash
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"
```

## Tracing Implementation

### Manual Tracing
```python
from langfuse.decorators import observe

@observe()
def generate_content(topic: str, content_type: str) -> str:
    """Generate educational content with Langfuse tracing."""
    
    # Create a trace
    trace = langfuse.trace(
        name="content_generation",
        metadata={"content_type": content_type},
        tags=["education", "ai-generated"]
    )
    
    # Add span for prompt preparation
    with trace.span(name="prompt_preparation") as span:
        prompt = f"Create a {content_type} about {topic}"
        span.update(
            input={"topic": topic, "content_type": content_type},
            output={"prompt": prompt}
        )
    
    # Add span for LLM generation
    with trace.span(name="llm_generation") as span:
        # Mock LLM call
        response = call_llm(prompt)
        span.update(
            input={"prompt": prompt},
            output={"response": response},
            metadata={
                "model": "gpt-4",
                "tokens": 1500,
                "cost": 0.045
            }
        )
    
    return response

def call_llm(prompt: str) -> str:
    # Your LLM integration here
    return "Generated content..."
```

### LangChain Integration
```python
from langfuse.callback import CallbackHandler

# Initialize Langfuse callback
langfuse_handler = CallbackHandler(
    secret_key="sk-lf-...",
    public_key="pk-lf-...",
    host="https://cloud.langfuse.com"
)

# Use with LangChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(
    model="gpt-4",
    callbacks=[langfuse_handler]
)

prompt = ChatPromptTemplate.from_template(
    "Create educational content about {topic} in {format} format"
)

chain = prompt | llm

# This will automatically trace to Langfuse
result = chain.invoke({
    "topic": "machine learning",
    "format": "study guide"
})
```

### OpenAI Integration
```python
from langfuse.openai import openai

# Initialize OpenAI client with Langfuse
client = openai.OpenAI()

# Automatically traced
completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Create a study guide about Python"}
    ],
    langfuse_observation_id="custom-id",
    langfuse_prompt_name="study-guide-v1"
)
```

## Evaluation & Scoring

### LLM-as-a-Judge Implementation
```python
from langfuse.client import Langfuse

class ContentQualityEvaluator:
    def __init__(self, langfuse_client: Langfuse):
        self.langfuse = langfuse_client
        self.judge_model = "gpt-4"
    
    def evaluate_content_quality(self, trace_id: str, content: str, content_type: str) -> dict:
        """Evaluate content quality using LLM-as-a-judge."""
        
        evaluation_prompt = f"""
        Please evaluate the following {content_type} content on a scale of 0-1 based on:
        1. Educational value (clarity, accuracy, completeness)
        2. Structure and organization
        3. Engagement and readability
        4. Appropriate difficulty level
        
        Content to evaluate:
        {content}
        
        Provide your evaluation as JSON with:
        - overall_score (0-1)
        - educational_value (0-1)
        - structure (0-1)  
        - engagement (0-1)
        - difficulty (0-1)
        - reasoning (explanation of your scores)
        """
        
        # Call judge model
        judge_response = self._call_judge_model(evaluation_prompt)
        evaluation_result = self._parse_evaluation(judge_response)
        
        # Log score to Langfuse
        self.langfuse.score(
            trace_id=trace_id,
            name="content_quality",
            value=evaluation_result["overall_score"],
            comment=evaluation_result["reasoning"],
            metadata={
                "content_type": content_type,
                "detailed_scores": {
                    "educational_value": evaluation_result["educational_value"],
                    "structure": evaluation_result["structure"],
                    "engagement": evaluation_result["engagement"],
                    "difficulty": evaluation_result["difficulty"]
                }
            }
        )
        
        return evaluation_result
    
    def _call_judge_model(self, prompt: str) -> str:
        # Implementation depends on your LLM provider
        import openai
        response = openai.chat.completions.create(
            model=self.judge_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1  # Low temperature for consistent evaluation
        )
        return response.choices[0].message.content
    
    def _parse_evaluation(self, response: str) -> dict:
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing logic
            return {
                "overall_score": 0.5,
                "educational_value": 0.5,
                "structure": 0.5,
                "engagement": 0.5,
                "difficulty": 0.5,
                "reasoning": "Failed to parse evaluation response"
            }
```

### Custom Scoring System
```python
class EducationalContentScorer:
    def __init__(self, langfuse_client: Langfuse):
        self.langfuse = langfuse_client
    
    def score_content(self, trace_id: str, content: str, metadata: dict):
        """Apply multiple scoring dimensions to educational content."""
        
        scores = {
            "readability": self._calculate_readability(content),
            "completeness": self._assess_completeness(content, metadata),
            "accuracy": self._verify_accuracy(content),
            "engagement": self._measure_engagement(content)
        }
        
        # Overall weighted score
        weights = {"readability": 0.25, "completeness": 0.30, "accuracy": 0.30, "engagement": 0.15}
        overall_score = sum(scores[dim] * weights[dim] for dim in scores)
        
        # Log individual scores
        for dimension, score in scores.items():
            self.langfuse.score(
                trace_id=trace_id,
                name=f"content_{dimension}",
                value=score,
                metadata={"dimension": dimension}
            )
        
        # Log overall score
        self.langfuse.score(
            trace_id=trace_id,
            name="content_overall",
            value=overall_score,
            metadata={"scoring_weights": weights, "individual_scores": scores}
        )
        
        return overall_score, scores
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (0-1)."""
        # Implement readability scoring (Flesch-Kincaid, etc.)
        word_count = len(content.split())
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        
        if sentence_count == 0:
            return 0.5
        
        avg_words_per_sentence = word_count / sentence_count
        
        # Simple readability heuristic (lower is better, so invert)
        if avg_words_per_sentence <= 15:
            return 1.0
        elif avg_words_per_sentence <= 20:
            return 0.8
        elif avg_words_per_sentence <= 25:
            return 0.6
        else:
            return 0.4
    
    def _assess_completeness(self, content: str, metadata: dict) -> float:
        """Assess content completeness based on expected elements."""
        content_type = metadata.get("content_type", "")
        required_elements = {
            "study_guide": ["introduction", "main concepts", "examples", "summary"],
            "flashcards": ["question", "answer", "explanation"],
            "quiz": ["questions", "options", "correct answers"]
        }
        
        elements = required_elements.get(content_type, [])
        if not elements:
            return 0.8  # Default score for unknown types
        
        found_elements = sum(1 for element in elements if element.lower() in content.lower())
        return found_elements / len(elements)
    
    def _verify_accuracy(self, content: str) -> float:
        """Verify content accuracy (placeholder - would use fact-checking APIs)."""
        # This would integrate with fact-checking services
        # For now, return a baseline score
        return 0.85
    
    def _measure_engagement(self, content: str) -> float:
        """Measure content engagement potential."""
        engagement_indicators = [
            "?",  # Questions
            "example",  # Examples
            "imagine",  # Imagination prompts
            "try",  # Action prompts
            "!"   # Excitement
        ]
        
        indicator_count = sum(content.lower().count(indicator) for indicator in engagement_indicators)
        content_length = len(content.split())
        
        if content_length == 0:
            return 0.0
        
        engagement_ratio = indicator_count / (content_length / 100)  # Per 100 words
        return min(engagement_ratio, 1.0)  # Cap at 1.0
```

## Prompt Management

### Prompt Templates
```python
# Create prompt template
prompt_template = langfuse.create_prompt(
    name="study-guide-generator",
    prompt="Create a comprehensive study guide about {{topic}} for {{audience_level}} students. Include:\n1. Key concepts\n2. Examples\n3. Practice questions\n4. Summary",
    config={
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000
    },
    labels=["education", "study-guide"]
)

# Use prompt template
def generate_study_guide(topic: str, audience_level: str):
    prompt = langfuse.get_prompt("study-guide-generator")
    
    compiled_prompt = prompt.compile(
        topic=topic,
        audience_level=audience_level
    )
    
    # Generate with tracing
    with langfuse.observe(name="study_guide_generation") as span:
        span.update(
            input={"topic": topic, "audience_level": audience_level},
            metadata={"prompt_version": prompt.version}
        )
        
        response = call_llm(compiled_prompt)
        
        span.update(output={"content": response})
        
        return response
```

### A/B Testing Prompts
```python
class PromptExperiment:
    def __init__(self, langfuse_client: Langfuse):
        self.langfuse = langfuse_client
    
    def run_prompt_experiment(self, topic: str, audience: str):
        """Run A/B test between two prompt versions."""
        
        import random
        
        # Randomly select prompt version
        version = "A" if random.random() < 0.5 else "B"
        
        if version == "A":
            prompt_name = "study-guide-v1"
            experiment_tag = "prompt_experiment_v1"
        else:
            prompt_name = "study-guide-v2"  
            experiment_tag = "prompt_experiment_v2"
        
        with self.langfuse.observe(
            name="prompt_experiment",
            metadata={"experiment_version": version, "prompt_name": prompt_name}
        ) as span:
            
            prompt = self.langfuse.get_prompt(prompt_name)
            compiled_prompt = prompt.compile(topic=topic, audience=audience)
            
            response = call_llm(compiled_prompt)
            
            span.update(
                input={"topic": topic, "audience": audience},
                output={"content": response},
                tags=[experiment_tag]
            )
            
            return response, version
```

## Analytics and Monitoring

### Usage Analytics
```python
class LangfuseAnalytics:
    def __init__(self, langfuse_client: Langfuse):
        self.langfuse = langfuse_client
    
    def get_usage_metrics(self, time_range: str = "7d"):
        """Get usage metrics from Langfuse."""
        
        # This would use Langfuse API to get analytics
        # For now, showing the structure
        
        metrics = {
            "total_traces": 0,
            "total_cost": 0.0,
            "avg_latency": 0.0,
            "success_rate": 0.0,
            "content_types": {},
            "model_usage": {},
            "quality_scores": {
                "avg_overall": 0.0,
                "avg_educational_value": 0.0,
                "avg_engagement": 0.0
            }
        }
        
        return metrics
    
    def create_quality_dashboard(self):
        """Create dashboard for content quality monitoring."""
        
        dashboard_config = {
            "charts": [
                {
                    "type": "line",
                    "title": "Content Quality Over Time",
                    "metric": "content_overall",
                    "time_range": "30d"
                },
                {
                    "type": "bar",
                    "title": "Quality by Content Type",
                    "metric": "content_overall",
                    "group_by": "content_type"
                },
                {
                    "type": "histogram",
                    "title": "Score Distribution",
                    "metric": "content_overall"
                }
            ]
        }
        
        return dashboard_config
```

## Production Best Practices

### Error Handling
```python
from langfuse.decorators import observe
import logging

logger = logging.getLogger(__name__)

@observe()
def robust_content_generation(topic: str, content_type: str):
    """Content generation with robust error handling."""
    
    try:
        # Main generation logic
        content = generate_content(topic, content_type)
        
        # Log success
        langfuse.score(
            name="generation_success",
            value=1.0,
            metadata={"topic": topic, "content_type": content_type}
        )
        
        return content
        
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        
        # Log failure
        langfuse.score(
            name="generation_success", 
            value=0.0,
            comment=str(e),
            metadata={"topic": topic, "content_type": content_type, "error_type": type(e).__name__}
        )
        
        # Return fallback content
        return f"Sorry, I couldn't generate {content_type} content about {topic} at this time."
```

### Performance Optimization
```python
from langfuse import Langfuse
import asyncio

class OptimizedLangfuseClient:
    def __init__(self):
        self.langfuse = Langfuse()
        self._batch_scores = []
        self._batch_size = 10
    
    async def batch_score(self, trace_id: str, name: str, value: float, **kwargs):
        """Batch scoring for better performance."""
        
        score_data = {
            "trace_id": trace_id,
            "name": name,
            "value": value,
            **kwargs
        }
        
        self._batch_scores.append(score_data)
        
        if len(self._batch_scores) >= self._batch_size:
            await self._flush_scores()
    
    async def _flush_scores(self):
        """Flush batched scores to Langfuse."""
        if not self._batch_scores:
            return
        
        # Send batch
        for score_data in self._batch_scores:
            self.langfuse.score(**score_data)
        
        self._batch_scores.clear()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._flush_scores()
```

### Security Considerations
```python
import os
from typing import Optional

class SecureLangfuseConfig:
    def __init__(self):
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY") 
        self.host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if not self.secret_key or not self.public_key:
            raise ValueError("Langfuse keys must be set in environment variables")
    
    def create_client(self, user_id: Optional[str] = None) -> Langfuse:
        """Create Langfuse client with user context."""
        
        client = Langfuse(
            secret_key=self.secret_key,
            public_key=self.public_key,
            host=self.host
        )
        
        if user_id:
            client.identify(
                user_id=user_id,
                metadata={"session_start": time.time()}
            )
        
        return client
```

## Sources
11. Langfuse Documentation - Platform Overview
12. Langfuse Model-Based Evaluations and LLM-as-a-Judge
13. Langfuse Integrations with LangChain, OpenAI, and other providers
14. Langfuse Tracing and Observability Features
15. Langfuse Prompt Management and A/B Testing