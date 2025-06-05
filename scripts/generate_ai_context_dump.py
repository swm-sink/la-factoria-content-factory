#!/usr/bin/env python3
"""
AI Context Dump Generator - Optimized & Selective

Generates a focused, practical codebase dump for AI analysis.
Prioritizes essential files and provides intelligent summaries.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def should_include_file(file_path: Path, project_root: Path) -> dict:
    """Determine if a file should be included and at what detail level."""
    
    # Essential files - full content
    essential_files = {
        "main.py", "app.py", "__init__.py", "settings.py", "config.py",
        "Dockerfile", "requirements.txt", "pyproject.toml", "docker-compose.yml",
        "README.md", "PROJECT_STATUS.md"
    }
    
    # Important files - summary only
    important_extensions = {".py", ".yaml", ".yml", ".json", ".toml"}
    
    # Documentation files - brief summary
    doc_extensions = {".md"}
    
    # Skip these entirely
    skip_patterns = {
        "__pycache__", ".git", "venv", "node_modules", ".terraform",
        "ai_context", "archive", ".pytest_cache", ".mypy_cache"
    }
    
    # Check if file should be skipped
    if any(pattern in str(file_path) for pattern in skip_patterns):
        return {"include": False}
    
    # Check for essential files
    if file_path.name in essential_files:
        return {"include": True, "level": "full"}
    
    # Check for important files
    if file_path.suffix.lower() in important_extensions:
        # Skip test files and very large files
        if "test" in file_path.name.lower() or file_path.stat().st_size > 50000:  # 50KB limit
            return {"include": True, "level": "summary"}
        return {"include": True, "level": "full"}
    
    # Documentation files
    if file_path.suffix.lower() in doc_extensions and file_path.stat().st_size < 10000:  # 10KB limit
        return {"include": True, "level": "summary"}
    
    return {"include": False}


def get_file_summary(file_path: Path) -> str:
    """Generate a smart summary of a file instead of full content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        lines = content.split("\n")
        total_lines = len(lines)
        
        # For Python files, extract key information
        if file_path.suffix == ".py":
            imports = [line.strip() for line in lines if line.strip().startswith(("import ", "from "))]
            classes = [line.strip() for line in lines if line.strip().startswith("class ")]
            functions = [line.strip() for line in lines if line.strip().startswith("def ")]
            
            summary = f"**Python Module** ({total_lines} lines)\n"
            if imports:
                summary += f"- **Imports**: {len(imports)} (e.g., {', '.join(imports[:3])})\n"
            if classes:
                summary += f"- **Classes**: {len(classes)} (e.g., {', '.join([c.split('(')[0].replace('class ', '') for c in classes[:3]])})\n"
            if functions:
                summary += f"- **Functions**: {len(functions)} (e.g., {', '.join([f.split('(')[0].replace('def ', '') for f in functions[:3]])})\n"
            
            return summary
        
        # For other files, provide basic info
        else:
            return f"**{file_path.suffix.upper().replace('.', '')} File** ({total_lines} lines, {len(content)} chars)"
    
    except Exception as e:
        return f"*[Could not analyze: {e}]*"


def generate_codebase_dump(project_root: Path, output_file: Path) -> None:
    """Generate a focused, practical codebase dump."""

    logger.info(f"Starting optimized codebase dump generation...")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Output file: {output_file}")

    content = []

    # Header
    content.append("# AI Content Factory - Focused Codebase Context")
    content.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append(f"**Analysis Type**: Selective & Optimized")
    content.append("\n---\n")

    # Key project info
    content.append("## 🎯 Project Overview\n")
    content.append("**Type**: AI Content Generation API")
    content.append("**Tech Stack**: Python, FastAPI, Google Cloud Platform")
    content.append("**Purpose**: Generate educational content from text input\n")

    # Essential files section
    content.append("## 📋 Essential Files (Full Content)\n")
    
    essential_count = 0
    summary_count = 0
    
    # Walk through files with intelligent selection
    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(
            exclude in d for exclude in [
                "__pycache__", ".git", "venv", "node_modules", 
                "ai_context", "archive", ".terraform", ".pytest_cache"
            ]
        )]

        root_path = Path(root)

        for file in files:
            file_path = root_path / file
            
            try:
                file_info = should_include_file(file_path, project_root)
                
                if not file_info.get("include"):
                    continue
                
                rel_path = file_path.relative_to(project_root)
                
                if file_info.get("level") == "full":
                    essential_count += 1
                    content.append(f"### `{rel_path}`\n")
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_content = f.read()

                        # Limit content size for very large files
                        if len(file_content) > 10000:  # 10KB limit
                            lines = file_content.split("\n")
                            file_content = "\n".join(lines[:200]) + f"\n\n... [File truncated: {len(lines)-200} more lines] ..."

                        # Add file content with proper markdown formatting
                        file_extension = file_path.suffix.lower()

                        if file_extension == ".py":
                            content.append("```python")
                        elif file_extension in [".yaml", ".yml"]:
                            content.append("```yaml")
                        elif file_extension == ".json":
                            content.append("```json")
                        elif file_extension == ".md":
                            content.append("```markdown")
                        else:
                            content.append("```")

                        content.append(file_content)
                        content.append("```\n")

                    except Exception as e:
                        content.append(f"*[File could not be read: {e}]*\n")
                
            except Exception as e:
                logger.warning(f"Error processing {file_path}: {e}")
                continue

    # File summaries section
    content.append("## 📄 File Summaries\n")
    
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if not any(
            exclude in d for exclude in [
                "__pycache__", ".git", "venv", "node_modules", 
                "ai_context", "archive", ".terraform"
            ]
        )]

        root_path = Path(root)

        for file in files:
            file_path = root_path / file
            
            try:
                file_info = should_include_file(file_path, project_root)
                
                if file_info.get("include") and file_info.get("level") == "summary":
                    summary_count += 1
                    rel_path = file_path.relative_to(project_root)
                    
                    content.append(f"### `{rel_path}`")
                    content.append(get_file_summary(file_path))
                    content.append("")
                    
            except Exception as e:
                continue

    # Summary
    content.append(f"## 📊 Summary\n")
    content.append(f"- **Essential files (full content)**: {essential_count}")
    content.append(f"- **Additional files (summarized)**: {summary_count}")
    content.append(f"- **Total files analyzed**: {essential_count + summary_count}")
    content.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("\n*This focused dump prioritizes essential files and provides intelligent summaries to maintain practical AI context size.*")

    # Write to output file
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    logger.info(f"Optimized codebase dump generated: {output_file}")
    logger.info(f"Essential files: {essential_count}, Summaries: {summary_count}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python generate_ai_context_dump.py <output_file>")
        sys.exit(1)

    project_root = Path.cwd()
    output_file = Path(sys.argv[1])

    try:
        generate_codebase_dump(project_root, output_file)
        print(f"✅ Successfully generated optimized codebase dump: {output_file}")
    except Exception as e:
        logger.error(f"Failed to generate codebase dump: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
