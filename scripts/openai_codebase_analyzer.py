#!/usr/bin/env python3
"""
OpenAI Codebase Analyzer

Uses OpenAI GPT-4 to analyze the complete codebase and provide insights.
Only runs if OPENAI_API_KEY is available.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_openai_availability() -> bool:
    """Check if OpenAI API is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.info("No OpenAI API key found - analysis skipped")
        return False
    
    try:
        import openai
        return True
    except ImportError:
        logger.error("OpenAI package not installed - run: pip install openai")
        return False


def analyze_codebase_with_openai(codebase_file: Path, output_file: Path) -> bool:
    """Analyze codebase using OpenAI GPT-4."""
    if not check_openai_availability():
        return False
    
    try:
        import openai
        
        # Read the codebase dump
        with open(codebase_file, "r", encoding="utf-8") as f:
            codebase_content = f.read()
        
        # Truncate if too large (GPT-4 token limits)
        max_tokens = 100000  # Conservative limit
        if len(codebase_content) > max_tokens:
            logger.info(f"Codebase too large ({len(codebase_content)} chars), truncating...")
            codebase_content = codebase_content[:max_tokens] + "\n\n[TRUNCATED]"
        
        # Analysis prompt
        analysis_prompt = f"""
You are a senior software engineer analyzing the AI Content Factory project.

Based on the codebase below, provide a comprehensive analysis covering:

1. **Architecture Assessment**: Overall structure, design patterns, strengths/weaknesses
2. **Critical Issues**: Bugs, security concerns, performance bottlenecks  
3. **Code Quality**: Best practices, maintainability, documentation
4. **Priority Tasks**: Top 5 most important items to work on next
5. **Risk Assessment**: What could break or cause problems
6. **Recommendations**: Specific actionable improvements

Format your response in markdown with clear sections and bullet points.
Focus on actionable insights that would help a developer working on this project.

Codebase:
{codebase_content}
"""
        
        logger.info("Sending request to OpenAI GPT-4...")
        
        # Make API call
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a senior software engineer providing code analysis."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        analysis_result = response.choices[0].message.content
        
        # Create analysis report
        report_content = f"""# AI Codebase Analysis
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analyzer**: OpenAI GPT-4
**Source**: {codebase_file.name}

---

{analysis_result}

---

**Generation Info**:
- Model: gpt-4
- Tokens used: ~{response.usage.total_tokens if response.usage else 'unknown'}
- Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*This analysis is AI-generated and should be reviewed by a human developer.*
"""
        
        # Write analysis
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        logger.info(f"AI analysis saved: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"OpenAI analysis failed: {e}")
        return False


def main():
    """Main entry point."""
    project_root = Path.cwd()
    ai_context_dir = project_root / "ai_context"
    
    # Input and output files
    codebase_file = ai_context_dir / "complete_codebase.md"
    output_file = ai_context_dir / "ai_analysis.md"
    
    if not codebase_file.exists():
        logger.error(f"Codebase file not found: {codebase_file}")
        sys.exit(1)
    
    # Run analysis
    success = analyze_codebase_with_openai(codebase_file, output_file)
    
    if success:
        print(f"✅ AI analysis complete: {output_file}")
    else:
        print("⚠️ AI analysis skipped (no OpenAI API key or package)")
        sys.exit(1)


if __name__ == "__main__":
    main() 