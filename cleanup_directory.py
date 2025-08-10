#!/usr/bin/env python3
"""
Directory Cleanup and Organization Script
==========================================

Cleans up duplicate files, organizes reports, and improves directory structure.
Following DRY/SSOT principles.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json


class DirectoryCleanup:
    """Handles directory cleanup and organization"""
    
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stats = {
            "files_moved": 0,
            "files_deleted": 0,
            "directories_removed": 0,
            "space_freed_mb": 0
        }
    
    def organize_reports(self):
        """Move all report files to reports/ directory"""
        report_patterns = [
            "*_REPORT.md",
            "*_COMPLETE.md", 
            "*_ANALYSIS_*.md",
            "PHASE_*.md",
            "P1_*.md"
        ]
        
        reports_dir = self.base_path / "reports" / "cleanup_moved"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        for pattern in report_patterns:
            for file in self.base_path.glob(pattern):
                if file.is_file():
                    dest = reports_dir / file.name
                    print(f"Moving {file.name} to reports/cleanup_moved/")
                    shutil.move(str(file), str(dest))
                    self.stats["files_moved"] += 1
    
    def clean_logs(self):
        """Move or delete old log files"""
        log_patterns = [
            "*.log",
            "server_test*.log",
            "frontend_test.log",
            "railway_setup_log_*.txt"
        ]
        
        logs_dir = self.base_path / "logs_archive"
        logs_dir.mkdir(exist_ok=True)
        
        for pattern in log_patterns:
            for file in self.base_path.glob(f"**/{pattern}"):
                if file.is_file():
                    # Archive logs instead of deleting
                    dest = logs_dir / file.name
                    print(f"Archiving {file.name} to logs_archive/")
                    shutil.move(str(file), str(dest))
                    self.stats["files_moved"] += 1
    
    def remove_duplicate_backups(self):
        """Remove duplicate backup directories"""
        duplicate_dirs = [
            "archive/claude_duplicate_20250809",
            "backup_claude_20250809_115235"
        ]
        
        for dir_path in duplicate_dirs:
            full_path = self.base_path / dir_path
            if full_path.exists() and full_path.is_dir():
                # Calculate size before deletion
                size_mb = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file()) / (1024 * 1024)
                self.stats["space_freed_mb"] += size_mb
                
                print(f"Removing duplicate backup: {dir_path} ({size_mb:.2f} MB)")
                shutil.rmtree(full_path)
                self.stats["directories_removed"] += 1
    
    def organize_scripts(self):
        """Ensure all scripts are in scripts/ directory"""
        script_files = [
            "consolidate_claude_dirs.sh",
            "fix_test_imports.py",
            "generate_master_plan_report.py",
            "update_master_plan.sh",
            "setup-github-auth.sh"
        ]
        
        scripts_dir = self.base_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        for script in script_files:
            source = self.base_path / script
            if source.exists() and source.is_file():
                dest = scripts_dir / script
                print(f"Moving {script} to scripts/")
                shutil.move(str(source), str(dest))
                self.stats["files_moved"] += 1
    
    def create_gitignore(self):
        """Create/update .gitignore with proper patterns"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover
.hypothesis/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Project specific
*.db
*.log
logs_archive/
node_modules/
.env
.env.local
*.bak
*.backup

# Reports and temporary files
reports/cleanup_moved/
archive/
backup_*/

# Performance test results
performance_results.json
security_results.json
validation_report_*.html
"""
        
        gitignore_path = self.base_path / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("Updated .gitignore file")
    
    def generate_cleanup_report(self):
        """Generate a report of cleanup actions"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.stats,
            "actions_taken": [
                "Organized report files into reports/cleanup_moved/",
                "Archived log files to logs_archive/",
                "Removed duplicate backup directories",
                "Moved scripts to scripts/ directory",
                "Updated .gitignore file"
            ]
        }
        
        report_path = self.base_path / "reports" / "cleanup_report.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nCleanup Complete!")
        print(f"Files moved: {self.stats['files_moved']}")
        print(f"Files deleted: {self.stats['files_deleted']}")
        print(f"Directories removed: {self.stats['directories_removed']}")
        print(f"Space freed: {self.stats['space_freed_mb']:.2f} MB")
        print(f"Report saved to: {report_path}")
    
    def run(self, dry_run=False):
        """Execute cleanup operations"""
        if dry_run:
            print("DRY RUN MODE - No changes will be made")
            return
        
        print("Starting directory cleanup...")
        self.organize_reports()
        self.clean_logs()
        self.remove_duplicate_backups()
        self.organize_scripts()
        self.create_gitignore()
        self.generate_cleanup_report()


if __name__ == "__main__":
    import sys
    
    dry_run = "--dry-run" in sys.argv
    cleanup = DirectoryCleanup()
    cleanup.run(dry_run=dry_run)