#!/usr/bin/env python3
"""
Generate Focused Context Files

Creates focused context files for specific debugging scenarios.
This complements the comprehensive dump with targeted information.
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


def generate_project_overview(project_root: Path, output_dir: Path) -> None:
    """Generate project overview and status."""
    logger.info("Generating project overview...")
    
    content = []
    
    # Header
    content.append("# Project Overview - AI Content Factory")
    content.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("\n---\n")
    
    # Current status
    content.append("## 🎯 Current Project Status\n")
    
    # Check key files
    key_files = [
        "app/main.py",
        "requirements.txt", 
        "Dockerfile",
        "docker-compose.yml",
        ".env.example"
    ]
    
    content.append("### Key Files Status\n")
    for file in key_files:
        file_path = project_root / file
        status = "✅" if file_path.exists() else "❌"
        content.append(f"- {status} `{file}`")
    
    content.append("\n")
    
    # Environment check
    content.append("### Environment Configuration\n")
    env_vars = [
        "GCP_PROJECT_ID",
        "OPENAI_API_KEY", 
        "GEMINI_API_KEY",
        "ELEVENLABS_API_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "NOT_SET")
        if value == "NOT_SET":
            status = "❌"
        elif value == "FAKE_PROJECT_ID":
            status = "⚠️"
        else:
            status = "✅"
            value = "SET" if len(value) > 10 else value
        content.append(f"- {status} `{var}`: {value}")
    
    content.append("\n")
    
    # Recent activity
    content.append("### Recent Activity\n")
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            content.append("```")
            content.append(result.stdout.strip())
            content.append("```\n")
        else:
            content.append("*No git history available*\n")
    except Exception:
        content.append("*Unable to check git history*\n")
    
    # Write file
    output_file = output_dir / "project_overview.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    
    logger.info(f"Project overview saved: {output_file}")


def generate_quick_reference(project_root: Path, output_dir: Path) -> None:
    """Generate quick reference for API endpoints and common commands."""
    logger.info("Generating quick reference...")
    
    content = []
    
    # Header
    content.append("# Quick Reference - AI Content Factory")
    content.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("\n---\n")
    
    # API Endpoints
    content.append("## 🚀 API Endpoints\n")
    
    # Common endpoints
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/healthz", "Health check"),
        ("POST", "/api/v1/jobs", "Create content generation job"),
        ("GET", "/api/v1/jobs/{job_id}", "Get job status"),
        ("GET", "/api/v1/jobs/{job_id}/result", "Get job result"),
    ]
    
    content.append("### Main Endpoints\n")
    for method, path, description in endpoints:
        content.append(f"- **{method}** `{path}` - {description}")
    
    content.append("\n")
    
    # Common commands
    content.append("## ⚡ Common Commands\n")
    
    commands = [
        ("Start local server", "uvicorn app.main:app --reload --host 0.0.0.0 --port 8080"),
        ("Test health endpoint", "curl http://localhost:8080/healthz"),
        ("Run tests", "pytest"),
        ("Format code", "black . && isort ."),
        ("Build Docker image", "docker build -t ai-content-factory ."),
        ("Start with Docker Compose", "docker-compose up -d"),
        ("Update AI context", "python scripts/smart_ai_context.py"),
    ]
    
    for desc, cmd in commands:
        content.append(f"### {desc}\n```bash\n{cmd}\n```\n")
    
    # Debug commands
    content.append("## 🔍 Debug Commands\n")
    
    debug_commands = [
        ("Check environment", "printenv | grep -E '(GCP|API|KEY)'"),
        ("Test Firestore connection", "gcloud firestore databases list"),
        ("Check Docker status", "docker ps"),
        ("View logs", "docker-compose logs -f api"),
        ("Test job creation", "curl -X POST http://localhost:8080/api/v1/jobs -H 'Content-Type: application/json' -d '{\"syllabus_text\":\"Test topic\", \"options\":{}}'"),
    ]
    
    for desc, cmd in debug_commands:
        content.append(f"### {desc}\n```bash\n{cmd}\n```\n")
    
    # Write file
    output_file = output_dir / "quick_reference.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    
    logger.info(f"Quick reference saved: {output_file}")


def generate_focused_context() -> None:
    """Generate all focused context files."""
    project_root = Path.cwd()
    output_dir = project_root / "ai_context"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Generate focused files
    generate_project_overview(project_root, output_dir)
    generate_quick_reference(project_root, output_dir)
    
    logger.info("Focused context generation complete")


if __name__ == "__main__":
    generate_focused_context() 