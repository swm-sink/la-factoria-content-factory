"""
Prompt optimization service for improving LLM prompt efficiency and effectiveness.

This service analyzes and optimizes prompts for token efficiency while maintaining
content quality and effectiveness for the AI Content Factory.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from prometheus_client import Counter, Histogram

# Prometheus metrics
PROMPT_OPTIMIZATIONS = Counter(
    "prompt_optimizations_total", "Total prompt optimizations", ["optimization_type"]
)
PROMPT_TOKEN_SAVINGS = Histogram(
    "prompt_token_savings", "Token savings from prompt optimization"
)
PROMPT_OPTIMIZATION_DURATION = Histogram(
    "prompt_optimization_duration_seconds", "Time spent optimizing prompts"
)


@dataclass
class OptimizationResult:
    """Result of prompt optimization."""

    original_prompt: str
    optimized_prompt: str
    original_tokens: int
    optimized_tokens: int
    token_savings: int
    optimization_techniques: List[str]
    quality_score: float
    metadata: Dict[str, Any]

    @property
    def savings_percentage(self) -> float:
        """Calculate percentage of tokens saved."""
        if self.original_tokens == 0:
            return 0.0
        return (self.token_savings / self.original_tokens) * 100


@dataclass
class PromptMetrics:
    """Metrics for prompt analysis."""

    token_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    complexity_score: float
    redundancy_score: float
    clarity_score: float


class PromptContext:
    """Context for prompt optimization and generation."""

    def __init__(
        self,
        topic: str = "Educational Content",
        audience_level: str = "beginner",
        content_type: str = "educational",
        key_topics: Optional[List[str]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        target_tokens: Optional[int] = None,
        quality_threshold: float = 0.8,
    ):
        self.topic = topic
        self.audience_level = audience_level
        self.content_type = content_type
        self.key_topics = key_topics or []
        self.constraints = constraints or {}
        self.target_tokens = target_tokens
        self.quality_threshold = quality_threshold


class PromptOptimizer:
    """Service for optimizing LLM prompts for efficiency and effectiveness."""

    def __init__(self):
        """Initialize the prompt optimizer."""
        self.logger = logging.getLogger(__name__)

        # Common redundant phrases to remove or simplify
        self.redundant_phrases = {
            "please make sure to": "",
            "it is important to": "",
            "you should": "",
            "make sure that": "ensure",
            "in order to": "to",
            "at this point in time": "now",
            "due to the fact that": "because",
            "for the purpose of": "for",
            "in the event that": "if",
            "with regard to": "about",
            "with respect to": "about",
            "as a matter of fact": "",
            "the fact that": "that",
            "it should be noted that": "",
            "it is worth noting that": "",
        }

        # Verbose instruction patterns to simplify
        self.verbose_patterns = [
            (r"Please provide a comprehensive and detailed", "Provide a detailed"),
            (r"I would like you to", ""),
            (r"Could you please", ""),
            (r"I need you to", ""),
            (r"Make sure to include", "Include"),
            (r"Be sure to", ""),
            (r"Don't forget to", ""),
            (r"Remember to", ""),
            (r"It is essential that you", ""),
            (r"You must", ""),
            (r"very important", "important"),
            (r"extremely important", "critical"),
            (r"absolutely necessary", "required"),
        ]

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: 1 token ≈ 0.75 words for English
        words = len(text.split())
        return int(words / 0.75)

    def analyze_prompt(self, prompt: str) -> PromptMetrics:
        """Analyze prompt structure and complexity."""
        words = prompt.split()
        sentences = re.split(r"[.!?]+", prompt)
        paragraphs = prompt.split("\n\n")

        # Calculate basic metrics
        token_count = self.estimate_tokens(prompt)
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        paragraph_count = len([p for p in paragraphs if p.strip()])

        # Calculate complexity score (0-1, higher = more complex)
        avg_sentence_length = word_count / max(sentence_count, 1)
        complexity_score = min(avg_sentence_length / 20, 1.0)  # Normalize to 0-1

        # Calculate redundancy score (0-1, higher = more redundant)
        unique_words = len(set(word.lower() for word in words))
        redundancy_score = 1 - (unique_words / max(word_count, 1))

        # Calculate clarity score (0-1, higher = clearer)
        # Based on sentence length, word complexity, etc.
        clarity_score = max(0, 1 - (complexity_score * 0.5) - (redundancy_score * 0.3))

        return PromptMetrics(
            token_count=token_count,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            complexity_score=complexity_score,
            redundancy_score=redundancy_score,
            clarity_score=clarity_score,
        )

    def remove_redundancies(self, prompt: str) -> Tuple[str, List[str]]:
        """Remove redundant phrases and verbose language."""
        optimized = prompt
        techniques = []

        # Remove redundant phrases
        for redundant, replacement in self.redundant_phrases.items():
            if redundant in optimized.lower():
                pattern = re.compile(re.escape(redundant), re.IGNORECASE)
                optimized = pattern.sub(replacement, optimized)
                techniques.append(f"removed_redundancy: {redundant}")

        # Apply verbose pattern simplifications
        for pattern, replacement in self.verbose_patterns:
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                techniques.append(f"simplified_pattern: {pattern}")

        # Remove extra whitespace
        optimized = re.sub(r"\s+", " ", optimized).strip()

        return optimized, techniques

    def optimize_structure(self, prompt: str) -> Tuple[str, List[str]]:
        """Optimize prompt structure for clarity and efficiency."""
        techniques = []
        lines = prompt.split("\n")
        optimized_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Convert bullet points to more concise format
            if line.startswith("- ") or line.startswith("* "):
                line = line[2:].strip()
                if not line.endswith(".") and not line.endswith(":"):
                    line += "."
                techniques.append("optimized_bullet_point")

            # Combine short consecutive lines (likely fragmented instructions)
            if (
                optimized_lines
                and len(line) < 50
                and len(optimized_lines[-1]) < 50
                and not optimized_lines[-1].endswith(".")
                and not line.startswith("Output:")
            ):
                optimized_lines[-1] += f" {line}"
                techniques.append("combined_short_lines")
            else:
                optimized_lines.append(line)

        return "\n".join(optimized_lines), techniques

    def optimize_instructions(self, prompt: str) -> Tuple[str, List[str]]:
        """Optimize instruction clarity and conciseness."""
        optimized = prompt
        techniques = []

        # Consolidate JSON format instructions
        json_patterns = [
            r"return the result in json format",
            r"provide your response as json",
            r"format your response as json",
            r"respond with json",
            r"use json format",
        ]

        for pattern in json_patterns:
            if re.search(pattern, optimized, re.IGNORECASE):
                # Replace all variations with a single clear instruction
                optimized = re.sub(pattern, "", optimized, flags=re.IGNORECASE)
                techniques.append("consolidated_json_instruction")

        # Add single JSON instruction if any were found
        if "consolidated_json_instruction" in techniques:
            if "Output format: JSON" not in optimized:
                optimized += "\n\nOutput format: JSON"

        # Optimize example formatting
        if "Example:" in optimized and "Output:" in optimized:
            # Ensure examples are concise
            example_section = re.search(
                r"Example:.*?(?=Output:|$)", optimized, re.DOTALL
            )
            if example_section and len(example_section.group()) > 200:
                techniques.append("condensed_example")

        return optimized, techniques

    def optimize_prompt(
        self, prompt: str, context: Optional[PromptContext] = None
    ) -> OptimizationResult:
        """
        Optimize a prompt for efficiency while maintaining quality.

        Args:
            prompt: The original prompt to optimize
            context: Optional context for optimization decisions

        Returns:
            OptimizationResult with optimization details
        """
        with PROMPT_OPTIMIZATION_DURATION.time():
            self.logger.info(
                f"Starting prompt optimization for {len(prompt)} character prompt"
            )

            original_metrics = self.analyze_prompt(prompt)
            all_techniques = []

            # Apply optimization techniques
            optimized = prompt

            # Step 1: Remove redundancies
            optimized, techniques = self.remove_redundancies(optimized)
            all_techniques.extend(techniques)

            # Step 2: Optimize structure
            optimized, techniques = self.optimize_structure(optimized)
            all_techniques.extend(techniques)

            # Step 3: Optimize instructions
            optimized, techniques = self.optimize_instructions(optimized)
            all_techniques.extend(techniques)

            # Calculate final metrics
            optimized_metrics = self.analyze_prompt(optimized)
            token_savings = original_metrics.token_count - optimized_metrics.token_count

            # Calculate quality score (based on clarity improvement and content preservation)
            quality_score = min(
                1.0,
                optimized_metrics.clarity_score
                + (0.1 if token_savings > 0 else 0)
                + (  # Bonus for efficiency
                    0.1 if len(all_techniques) > 0 else 0
                ),  # Bonus for successful optimization
            )

            # Check if optimization meets quality threshold
            if context and quality_score < context.quality_threshold:
                self.logger.warning(
                    f"Optimization quality score {quality_score} below threshold {context.quality_threshold}"
                )

            # Record metrics
            if token_savings > 0:
                PROMPT_TOKEN_SAVINGS.observe(token_savings)
                PROMPT_OPTIMIZATIONS.labels(optimization_type="successful").inc()
            else:
                PROMPT_OPTIMIZATIONS.labels(optimization_type="no_improvement").inc()

            result = OptimizationResult(
                original_prompt=prompt,
                optimized_prompt=optimized,
                original_tokens=original_metrics.token_count,
                optimized_tokens=optimized_metrics.token_count,
                token_savings=token_savings,
                optimization_techniques=all_techniques,
                quality_score=quality_score,
                metadata={
                    "original_metrics": original_metrics,
                    "optimized_metrics": optimized_metrics,
                    "context": context.__dict__ if context else None,
                },
            )

            self.logger.info(
                f"Prompt optimization complete: {token_savings} tokens saved "
                f"({result.savings_percentage:.1f}%), quality score: {quality_score:.2f}"
            )

            return result

    def batch_optimize_prompts(
        self, prompts: Dict[str, str], context: Optional[PromptContext] = None
    ) -> Dict[str, OptimizationResult]:
        """
        Optimize multiple prompts in batch.

        Args:
            prompts: Dictionary of prompt_name -> prompt_text
            context: Optional context for optimization

        Returns:
            Dictionary of prompt_name -> OptimizationResult
        """
        results = {}
        total_original_tokens = 0
        total_optimized_tokens = 0

        for name, prompt in prompts.items():
            try:
                result = self.optimize_prompt(prompt, context)
                results[name] = result
                total_original_tokens += result.original_tokens
                total_optimized_tokens += result.optimized_tokens
            except Exception as e:
                self.logger.error(f"Failed to optimize prompt '{name}': {e}")
                # Create a fallback result with original prompt
                results[name] = OptimizationResult(
                    original_prompt=prompt,
                    optimized_prompt=prompt,
                    original_tokens=self.estimate_tokens(prompt),
                    optimized_tokens=self.estimate_tokens(prompt),
                    token_savings=0,
                    optimization_techniques=[],
                    quality_score=0.5,
                    metadata={"error": str(e)},
                )

        total_savings = total_original_tokens - total_optimized_tokens
        self.logger.info(
            f"Batch optimization complete: {len(prompts)} prompts, "
            f"{total_savings} total tokens saved "
            f"({(total_savings/max(total_original_tokens, 1)*100):.1f}%)"
        )

        return results

    def suggest_improvements(self, prompt: str) -> List[str]:
        """Suggest specific improvements for a prompt."""
        suggestions = []
        metrics = self.analyze_prompt(prompt)

        # Token count suggestions
        if metrics.token_count > 1000:
            suggestions.append("Consider breaking this into smaller, focused prompts")

        # Clarity suggestions
        if metrics.clarity_score < 0.6:
            suggestions.append("Simplify sentence structure for better clarity")

        # Redundancy suggestions
        if metrics.redundancy_score > 0.3:
            suggestions.append("Remove redundant phrases and repetitive instructions")

        # Structure suggestions
        if metrics.sentence_count > 20 and "\n" not in prompt:
            suggestions.append("Add paragraph breaks to improve readability")

        # Specific pattern suggestions
        if "please" in prompt.lower():
            suggestions.append("Remove unnecessary politeness words like 'please'")

        if prompt.count("important") > 2:
            suggestions.append(
                "Reduce emphasis words - not everything can be 'important'"
            )

        return suggestions
