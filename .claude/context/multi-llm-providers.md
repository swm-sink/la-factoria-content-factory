# Multi-LLM Provider Integration Context

## Anthropic Claude API

### Authentication & Setup
- API requires `x-api-key` header for authentication
- Client SDK available for Python and TypeScript
- Request size limits: 32MB (standard), 256MB (batch), 500MB (files)

### Model Selection
- Current recommended model: "claude-opus-4-20250514"
- Configurable parameters: max_tokens, temperature, top_p
- Flexible messaging interface with role-based conversations

### Integration Example
```python
import anthropic

client = anthropic.Anthropic(api_key="my_api_key")
message = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}]
)
```

### Response Structure
- JSON responses with request-id headers
- anthropic-organization-id for tracking
- Structured message format

### Best Practices
- Use client SDKs when possible
- Set appropriate token limits
- Handle rate limits gracefully
- Use version-specific endpoints

## OpenAI API

### Authentication & Setup
```python
import openai

client = openai.OpenAI(api_key="sk-your-key-here")
```

### Model Selection
- GPT-4: Most capable, higher cost
- GPT-3.5-turbo: Faster, cost-effective
- Function calling capabilities
- JSON mode support

### Integration Pattern
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=1000,
    temperature=0.7
)
```

## Multi-Provider Architecture

### Provider Abstraction Layer
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict], model: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate(self, messages: List[Dict], model: str = "claude-opus-4-20250514", **kwargs) -> str:
        response = self.client.messages.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 1024)
        )
        return response.content[0].text

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    async def generate(self, messages: List[Dict], model: str = "gpt-4", **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 1024)
        )
        return response.choices[0].message.content
```

### Provider Manager
```python
class LLMProviderManager:
    def __init__(self):
        self.providers = {}
        self.default_provider = None
    
    def register_provider(self, name: str, provider: LLMProvider, is_default: bool = False):
        self.providers[name] = provider
        if is_default or not self.default_provider:
            self.default_provider = name
    
    async def generate(self, messages: List[Dict], provider_name: str = None, **kwargs) -> str:
        provider_name = provider_name or self.default_provider
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not found")
        
        return await self.providers[provider_name].generate(messages, **kwargs)
    
    def get_provider_models(self, provider_name: str) -> List[str]:
        return self.providers[provider_name].get_available_models()
```

### Configuration Management
```python
# config.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ProviderConfig:
    name: str
    api_key: str
    default_model: str
    rate_limit: int
    timeout: int
    retry_attempts: int

class LLMConfig:
    def __init__(self):
        self.providers = {
            "anthropic": ProviderConfig(
                name="anthropic",
                api_key="your-anthropic-key",
                default_model="claude-opus-4-20250514",
                rate_limit=100,
                timeout=30,
                retry_attempts=3
            ),
            "openai": ProviderConfig(
                name="openai", 
                api_key="your-openai-key",
                default_model="gpt-4",
                rate_limit=60,
                timeout=30,
                retry_attempts=3
            )
        }
```

### Error Handling & Fallbacks
```python
import asyncio
from typing import Optional

class LLMProviderWithFallback:
    def __init__(self, manager: LLMProviderManager, fallback_order: List[str]):
        self.manager = manager
        self.fallback_order = fallback_order
    
    async def generate_with_fallback(self, messages: List[Dict], **kwargs) -> str:
        last_error = None
        
        for provider_name in self.fallback_order:
            try:
                return await self.manager.generate(messages, provider_name, **kwargs)
            except Exception as e:
                last_error = e
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
```

## Cost Optimization Strategies

### Token Counting
```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    # Pricing as of 2025 (example rates)
    pricing = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-opus-4-20250514": {"input": 0.015, "output": 0.075}
    }
    
    if model not in pricing:
        return 0.0
    
    input_cost = (input_tokens / 1000) * pricing[model]["input"]
    output_cost = (output_tokens / 1000) * pricing[model]["output"]
    return input_cost + output_cost
```

### Smart Model Selection
```python
class SmartModelSelector:
    def __init__(self):
        self.model_capabilities = {
            "simple_tasks": ["gpt-3.5-turbo", "claude-haiku"],
            "complex_reasoning": ["gpt-4", "claude-opus-4-20250514"],
            "code_generation": ["gpt-4", "claude-opus-4-20250514"],
            "creative_writing": ["claude-opus-4-20250514", "gpt-4"]
        }
    
    def select_model(self, task_type: str, budget_tier: str = "standard") -> str:
        models = self.model_capabilities.get(task_type, ["gpt-3.5-turbo"])
        
        if budget_tier == "economy":
            return models[-1]  # Cheapest option
        elif budget_tier == "premium":
            return models[0]   # Best option
        else:
            return models[len(models)//2] if len(models) > 1 else models[0]
```

## Rate Limiting & Monitoring

### Rate Limiter
```python
import time
from collections import defaultdict
from asyncio import Semaphore

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.semaphores = defaultdict(lambda: Semaphore(100))
    
    async def acquire(self, provider: str, limit: int = 100, window: int = 60):
        async with self.semaphores[provider]:
            now = time.time()
            # Clean old requests
            self.requests[provider] = [
                req_time for req_time in self.requests[provider] 
                if now - req_time < window
            ]
            
            if len(self.requests[provider]) >= limit:
                sleep_time = window - (now - self.requests[provider][0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            self.requests[provider].append(now)
```

### Usage Monitoring
```python
import logging
from dataclasses import dataclass
from typing import Dict
import json

@dataclass
class UsageMetrics:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency: float
    timestamp: float

class UsageTracker:
    def __init__(self):
        self.metrics = []
        self.logger = logging.getLogger(__name__)
    
    def track_usage(self, metrics: UsageMetrics):
        self.metrics.append(metrics)
        self.logger.info(f"LLM Usage: {metrics.provider}/{metrics.model} - "
                        f"Tokens: {metrics.input_tokens + metrics.output_tokens}, "
                        f"Cost: ${metrics.cost:.4f}, "
                        f"Latency: {metrics.latency:.2f}s")
    
    def get_usage_summary(self, hours: int = 24) -> Dict:
        cutoff = time.time() - (hours * 3600)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff]
        
        summary = {
            "total_requests": len(recent_metrics),
            "total_cost": sum(m.cost for m in recent_metrics),
            "total_tokens": sum(m.input_tokens + m.output_tokens for m in recent_metrics),
            "avg_latency": sum(m.latency for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
            "by_provider": defaultdict(lambda: {"requests": 0, "cost": 0, "tokens": 0})
        }
        
        for metric in recent_metrics:
            provider_stats = summary["by_provider"][metric.provider]
            provider_stats["requests"] += 1
            provider_stats["cost"] += metric.cost
            provider_stats["tokens"] += metric.input_tokens + metric.output_tokens
        
        return summary
```

## Sources
1. Anthropic Claude API Documentation
2. OpenAI API Documentation  
3. Multi-provider LLM integration patterns
4. Cost optimization strategies for LLM usage
5. Rate limiting and monitoring best practices