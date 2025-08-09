#!/usr/bin/env python3
"""
Master Plan Report Generator
============================

Generates a human-readable markdown report from master_plan.yaml
for better project visibility and progress tracking.

Usage:
    python generate_master_plan_report.py [--output FILENAME]
"""

import yaml
import argparse
from datetime import datetime
from typing import Dict, Any, List
import os

def load_master_plan(yaml_file: str = "master_plan.yaml") -> Dict[str, Any]:
    """Load the master plan YAML file"""
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {yaml_file} not found")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        exit(1)

def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable format"""
    if minutes < 60:
        return f"{minutes}m"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes}m"

def format_confidence(confidence: str) -> str:
    """Format confidence level with emoji indicators"""
    confidence_map = {
        "very_high": "🟢 Very High",
        "high": "🟡 High", 
        "medium": "🟠 Medium",
        "low": "🔴 Low"
    }
    return confidence_map.get(confidence, confidence.title())

def format_priority(priority: str) -> str:
    """Format priority with emoji indicators"""
    priority_map = {
        "critical": "🚨 CRITICAL",
        "high": "⚡ HIGH",
        "medium": "📋 MEDIUM", 
        "low": "📝 LOW"
    }
    return priority_map.get(priority.lower(), priority.upper())

def format_status(status: str) -> str:
    """Format task status with emoji indicators"""
    status_map = {
        "pending": "⏳ Pending",
        "in_progress": "🔄 In Progress",
        "completed": "✅ Completed",
        "blocked": "🚫 Blocked",
        "failed": "❌ Failed"
    }
    return status_map.get(status, status.title())

def generate_project_overview(plan: Dict[str, Any]) -> str:
    """Generate project overview section"""
    project = plan.get("project", {})
    status = plan.get("status", {})
    current_status = plan.get("current_status", {})
    
    markdown = f"""# 📋 {project.get('name', 'La Factoria')} - Master Plan Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Version**: {project.get('version', '1.0.0')}  
**Current Phase**: {project.get('current_phase', 'Unknown')}  

## 🎯 Project Status Overview

| Metric | Value |
|--------|-------|
| **Completion** | {project.get('completion_percentage', 0)}% |
| **Total Estimated Hours** | {project.get('estimated_total_hours', 0)}h |
| **Critical Path Hours** | {project.get('critical_path_hours', 0)}h |
| **Remaining Hours** | {current_status.get('total_remaining_hours', 0)}h |
| **Critical Path Remaining** | {current_status.get('critical_path_remaining_hours', 0)}h |

### 🏗️ Foundation Status
- **Foundation Complete**: {'✅ Yes' if status.get('foundation_complete') else '❌ No'}
- **Critical Fixes Applied**: {'✅ Yes' if status.get('critical_fixes_applied') else '❌ No'}
- **Infrastructure Gaps**: {'⚠️ Yes' if status.get('infrastructure_gaps') else '✅ None'}
- **Ready for Execution**: {'🚀 Yes' if status.get('ready_for_execution') else '⏳ Not Yet'}

"""
    
    # Add key risks if present
    risks = current_status.get('key_risks', [])
    if risks:
        markdown += "### ⚠️ Key Risks\n"
        for risk in risks:
            markdown += f"- {risk}\n"
        markdown += "\n"
    
    # Add success indicators if present
    indicators = current_status.get('success_indicators', [])
    if indicators:
        markdown += "### 🎯 Success Indicators\n"
        for indicator in indicators:
            markdown += f"- ✅ {indicator}\n"
        markdown += "\n"
    
    return markdown

def generate_phases_overview(plan: Dict[str, Any]) -> str:
    """Generate phases overview section"""
    phases = plan.get("phases", {})
    current_status = plan.get("current_status", {})
    phase_progress = current_status.get("phase_progress", {})
    
    markdown = "## 🗓️ Execution Phases\n\n"
    
    for phase_key, phase_data in phases.items():
        progress = phase_progress.get(phase_key, 0)
        progress_bar = "🟩" * (progress // 10) + "⬜" * (10 - (progress // 10))
        
        # Format dependencies
        deps = phase_data.get('dependencies', [])
        deps_str = ", ".join(deps) if deps else "None"
        
        markdown += f"""### {phase_data.get('name', phase_key)}
**Objective**: {phase_data.get('objective', 'Not specified')}  
**Priority**: {format_priority(phase_data.get('priority', 'medium'))}  
**Estimated Time**: {phase_data.get('estimated_hours', 0)}h  
**Confidence**: {format_confidence(phase_data.get('confidence', 'medium'))}  
**Dependencies**: {deps_str}  
**Progress**: {progress}% {progress_bar}

**Success Criteria**:
"""
        
        for criteria in phase_data.get('success_criteria', []):
            markdown += f"- {criteria}\n"
        
        markdown += "\n---\n\n"
    
    return markdown

def generate_detailed_tasks(plan: Dict[str, Any]) -> str:
    """Generate detailed task breakdown section"""
    tasks = plan.get("tasks", {})
    phases = plan.get("phases", {})
    
    markdown = "## 📋 Detailed Task Breakdown\n\n"
    
    # Group tasks by phase
    tasks_by_phase = {}
    for task_id, task_data in tasks.items():
        phase = task_data.get('phase', 'unknown')
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append((task_id, task_data))
    
    # Generate tasks for each phase
    for phase_key in phases.keys():
        phase_tasks = tasks_by_phase.get(phase_key, [])
        if not phase_tasks:
            continue
            
        phase_name = phases[phase_key].get('name', phase_key)
        markdown += f"### 📁 {phase_name}\n\n"
        
        for task_id, task_data in phase_tasks:
            # Task header
            markdown += f"#### {task_data.get('name', task_id)}\n"
            markdown += f"**ID**: `{task_id}`  \n"
            markdown += f"**Status**: {format_status(task_data.get('status', 'pending'))}  \n"
            markdown += f"**Priority**: {format_priority(task_data.get('priority', 'medium'))}  \n"
            markdown += f"**Estimated Time**: {format_duration(task_data.get('estimated_minutes', 0))}  \n"
            markdown += f"**Confidence**: {format_confidence(task_data.get('confidence', 'medium'))}  \n"
            
            # Dependencies
            deps = task_data.get('dependencies', [])
            if deps:
                markdown += f"**Dependencies**: {', '.join(f'`{dep}`' for dep in deps)}  \n"
            else:
                markdown += "**Dependencies**: None  \n"
            
            # Description
            description = task_data.get('description', 'No description provided')
            markdown += f"\n**Description**: {description}\n\n"
            
            # Validation criteria
            validation = task_data.get('validation_criteria', [])
            if validation:
                markdown += "**Validation Criteria**:\n"
                for criteria in validation:
                    markdown += f"- [ ] {criteria}\n"
                markdown += "\n"
            
            # Files involved
            files = task_data.get('files_involved', [])
            if files:
                markdown += "**Files Involved**:\n"
                for file in files:
                    markdown += f"- `{file}`\n"
                markdown += "\n"
            
            # Commands to run
            commands = task_data.get('commands_to_run', [])
            if commands:
                markdown += "**Commands to Run**:\n"
                for cmd in commands:
                    markdown += f"```bash\n{cmd}\n```\n"
                markdown += "\n"
            
            # Notes and special considerations
            notes = task_data.get('notes', '')
            if notes:
                markdown += f"**Notes**: {notes}\n\n"
            
            # Technical debt flag
            if task_data.get('technical_debt', False):
                markdown += "🔧 **Technical Debt Resolution**\n\n"
            
            # Risk factors
            risks = task_data.get('risk_factors', [])
            if risks:
                markdown += "⚠️ **Risk Factors**:\n"
                for risk in risks:
                    markdown += f"- {risk}\n"
                markdown += "\n"
            
            markdown += "---\n\n"
    
    return markdown

def generate_execution_config(plan: Dict[str, Any]) -> str:
    """Generate execution configuration section"""
    config = plan.get("execution_config", {})
    
    if not config:
        return ""
    
    markdown = "## ⚙️ Execution Configuration\n\n"
    
    # Basic settings
    markdown += "### 🎛️ Basic Settings\n"
    markdown += f"- **Autonomous Mode**: {'✅ Enabled' if config.get('autonomous_mode') else '❌ Disabled'}\n"
    markdown += f"- **Validation Required**: {'✅ Yes' if config.get('validation_required') else '❌ No'}\n"
    markdown += f"- **Atomic Commits**: {'✅ Yes' if config.get('atomic_commits') else '❌ No'}\n"
    markdown += f"- **Test Driven Development**: {'✅ Yes' if config.get('test_driven_development') else '❌ No'}\n\n"
    
    # Progress reporting
    progress = config.get('progress_reporting', {})
    if progress:
        markdown += "### 📊 Progress Reporting\n"
        markdown += f"- **Update Frequency**: {progress.get('update_frequency', 'Not specified')}\n"
        markdown += f"- **Markdown Regeneration**: {'✅ Yes' if progress.get('markdown_regeneration') else '❌ No'}\n"
        markdown += f"- **Commit Messages Include Progress**: {'✅ Yes' if progress.get('commit_messages_include_progress') else '❌ No'}\n\n"
    
    # Risk management
    risk_mgmt = config.get('risk_management', {})
    if risk_mgmt:
        markdown += "### 🛡️ Risk Management\n"
        markdown += f"- **Max Consecutive Failures**: {risk_mgmt.get('max_consecutive_failures', 'Not specified')}\n"
        markdown += f"- **Fallback to Manual**: {'✅ Yes' if risk_mgmt.get('fallback_to_manual') else '❌ No'}\n"
        markdown += f"- **Critical Path Priority**: {'✅ Yes' if risk_mgmt.get('critical_path_priority') else '❌ No'}\n\n"
    
    # Success thresholds
    thresholds = config.get('success_thresholds', {})
    if thresholds:
        markdown += "### 🎯 Success Thresholds\n"
        for key, value in thresholds.items():
            if isinstance(value, float):
                markdown += f"- **{key.replace('_', ' ').title()}**: {value:.1%}\n"
            else:
                markdown += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        markdown += "\n"
    
    return markdown

def generate_progress_summary(plan: Dict[str, Any]) -> str:
    """Generate progress summary section"""
    current = plan.get("current_status", {})
    tasks = plan.get("tasks", {})
    
    markdown = "## 📈 Progress Summary\n\n"
    
    # Task status counts
    status_counts = {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0, "failed": 0}
    total_tasks = len(tasks)
    total_minutes = 0
    completed_minutes = 0
    
    for task_data in tasks.values():
        status = task_data.get('status', 'pending')
        minutes = task_data.get('estimated_minutes', 0)
        status_counts[status] = status_counts.get(status, 0) + 1
        total_minutes += minutes
        if status == 'completed':
            completed_minutes += minutes
    
    # Progress metrics
    completion_pct = (completed_minutes / total_minutes * 100) if total_minutes > 0 else 0
    
    markdown += f"### 📊 Task Completion Status\n"
    markdown += f"- **Total Tasks**: {total_tasks}\n"
    markdown += f"- **Completed**: {status_counts['completed']} ✅\n"
    markdown += f"- **In Progress**: {status_counts['in_progress']} 🔄\n"
    markdown += f"- **Pending**: {status_counts['pending']} ⏳\n"
    markdown += f"- **Blocked**: {status_counts['blocked']} 🚫\n"
    markdown += f"- **Failed**: {status_counts['failed']} ❌\n\n"
    
    markdown += f"### ⏱️ Time Tracking\n"
    markdown += f"- **Total Estimated**: {format_duration(total_minutes)}\n"
    markdown += f"- **Completed**: {format_duration(completed_minutes)}\n"
    markdown += f"- **Remaining**: {format_duration(total_minutes - completed_minutes)}\n"
    markdown += f"- **Completion**: {completion_pct:.1f}%\n\n"
    
    # Next scheduled task
    next_task = current.get('next_scheduled')
    if next_task and next_task in tasks:
        task_data = tasks[next_task]
        markdown += f"### 🎯 Next Scheduled Task\n"
        markdown += f"**{task_data.get('name', next_task)}** (`{next_task}`)\n"
        markdown += f"- Priority: {format_priority(task_data.get('priority', 'medium'))}\n"
        markdown += f"- Estimated Time: {format_duration(task_data.get('estimated_minutes', 0))}\n"
        markdown += f"- Phase: {task_data.get('phase', 'unknown').upper()}\n\n"
    
    # Current blockers
    blockers = current.get('blockers', [])
    if blockers:
        markdown += "### 🚫 Current Blockers\n"
        for blocker in blockers:
            markdown += f"- {blocker}\n"
        markdown += "\n"
    
    return markdown

def generate_master_plan_report(yaml_file: str, output_file: str):
    """Generate the complete master plan report"""
    print(f"Loading master plan from {yaml_file}...")
    plan = load_master_plan(yaml_file)
    
    print("Generating markdown report...")
    
    # Build the complete markdown report
    report_sections = [
        generate_project_overview(plan),
        generate_phases_overview(plan),
        generate_detailed_tasks(plan),
        generate_execution_config(plan),
        generate_progress_summary(plan)
    ]
    
    # Add footer
    footer = f"""
---

## 📋 Report Information

**Generated by**: `generate_master_plan_report.py`  
**Source**: `{yaml_file}`  
**Generated at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total sections**: {len([s for s in report_sections if s.strip()])}

> 💡 **Tip**: This report is automatically generated from the master plan YAML.  
> To update, modify the YAML file and regenerate this report.

---

*La Factoria Educational Content Platform - Master Plan Report*
"""
    
    report_sections.append(footer)
    full_report = "\n".join(report_sections)
    
    # Write to output file
    print(f"Writing report to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    print(f"✅ Master plan report generated successfully!")
    print(f"📁 Report saved to: {output_file}")
    print(f"📊 Report contains {len(full_report.split())} words and {len(full_report.splitlines())} lines")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate human-readable markdown report from master_plan.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_master_plan_report.py
    python generate_master_plan_report.py --output custom_report.md
    python generate_master_plan_report.py --yaml custom_plan.yaml --output report.md
        """
    )
    
    parser.add_argument(
        '--yaml', '-y',
        default='master_plan.yaml',
        help='Path to the master plan YAML file (default: master_plan.yaml)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='MASTER_PLAN_REPORT.md',
        help='Output markdown file path (default: MASTER_PLAN_REPORT.md)'
    )
    
    args = parser.parse_args()
    
    # Check if YAML file exists
    if not os.path.exists(args.yaml):
        print(f"❌ Error: {args.yaml} not found")
        print("Please ensure the master plan YAML file exists in the current directory.")
        exit(1)
    
    # Generate the report
    try:
        generate_master_plan_report(args.yaml, args.output)
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        exit(1)

if __name__ == "__main__":
    main()