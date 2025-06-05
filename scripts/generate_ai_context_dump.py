#!/usr/bin/env python3
"""
AI Context Dump Generator

Generates a comprehensive codebase dump for AI analysis and context sharing.
This script creates a single markdown file containing all relevant project information.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def should_include_file(file_path: Path, project_root: Path) -> bool:
    """Determine if a file should be included in the context dump."""

    # Convert to relative path for easier checking
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        return False

    # Exclude patterns
    exclude_patterns = [
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "venv",
        "node_modules",
        ".coverage",
        "coverage.xml",
        ".env",
        ".env.local",
        ".env.production",
        "ai_context",  # Don't include existing AI context to avoid recursion
        ".terraform",
        "*.pyc",
        "*.pyo",
        "*.log",
    ]

    # Check if any part of the path matches exclude patterns
    path_parts = str(rel_path).split(os.sep)
    for part in path_parts:
        for pattern in exclude_patterns:
            if pattern.startswith("*"):
                if part.endswith(pattern[1:]):
                    return False
            elif pattern in part:
                return False

    # Include only text files and common config files
    include_extensions = {
        ".py",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".cfg",
        ".conf",
        ".ini",
        ".env.example",
        ".gitignore",
        ".dockerignore",
        ".tf",
        ".sh",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".css",
        ".html",
        ".sql",
    }

    # Special files to include
    special_files = {
        "Dockerfile",
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "package.json",
        "README",
        "LICENSE",
        "CHANGELOG",
        "docker-compose.yml",
    }

    if file_path.suffix.lower() in include_extensions:
        return True

    if file_path.name in special_files:
        return True

    return False


def generate_codebase_dump(project_root: Path, output_file: Path) -> None:
    """Generate a comprehensive codebase dump."""

    logger.info(f"Starting codebase dump generation...")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Output file: {output_file}")

    content = []

    # Header
    content.append("# AI Content Factory - Complete Codebase Context")
    content.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append(f"**Project Root**: {project_root}")
    content.append("\n---\n")

    # Project structure
    content.append("## 📁 Project Structure\n")
    content.append("```")

    def add_tree_structure(
        path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0
    ):
        if current_depth >= max_depth:
            return

        items = []
        try:
            items = sorted([p for p in path.iterdir() if not p.name.startswith(".")])
        except PermissionError:
            return

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            content.append(f"{prefix}{current_prefix}{item.name}")

            if item.is_dir() and not any(
                exclude in item.name
                for exclude in ["__pycache__", ".git", "venv", "node_modules"]
            ):
                next_prefix = prefix + ("    " if is_last else "│   ")
                add_tree_structure(item, next_prefix, max_depth, current_depth + 1)

    add_tree_structure(project_root)
    content.append("```\n")

    # File contents
    content.append("## 📄 File Contents\n")

    file_count = 0
    total_lines = 0

    # Walk through all files
    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [
            d
            for d in dirs
            if not any(
                exclude in d
                for exclude in [
                    "__pycache__",
                    ".git",
                    "venv",
                    "node_modules",
                    "ai_context",
                    ".terraform",
                ]
            )
        ]

        root_path = Path(root)

        for file in files:
            file_path = root_path / file

            if should_include_file(file_path, project_root):
                try:
                    rel_path = file_path.relative_to(project_root)

                    content.append(f"### `{rel_path}`\n")

                    # Read file content
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_content = f.read()

                        lines = file_content.split("\n")
                        total_lines += len(lines)
                        file_count += 1

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
                        elif file_extension in [".sh", ".bash"]:
                            content.append("```bash")
                        elif file_extension in [".js", ".jsx"]:
                            content.append("```javascript")
                        elif file_extension in [".ts", ".tsx"]:
                            content.append("```typescript")
                        else:
                            content.append("```")

                        content.append(file_content)
                        content.append("```\n")

                    except (UnicodeDecodeError, PermissionError) as e:
                        content.append(f"*[File could not be read: {e}]*\n")

                except ValueError:
                    # Skip files outside project root
                    continue

    # Summary
    content.append(f"## 📊 Summary\n")
    content.append(f"- **Files processed**: {file_count}")
    content.append(f"- **Total lines**: {total_lines:,}")
    content.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Write to output file
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    logger.info(f"Codebase dump generated successfully: {output_file}")
    logger.info(f"Processed {file_count} files with {total_lines:,} total lines")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python generate_ai_context_dump.py <output_file>")
        sys.exit(1)

    project_root = Path.cwd()
    output_file = Path(sys.argv[1])

    try:
        generate_codebase_dump(project_root, output_file)
        print(f"✅ Successfully generated codebase dump: {output_file}")
    except Exception as e:
        logger.error(f"Failed to generate codebase dump: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
