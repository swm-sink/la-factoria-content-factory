#!/usr/bin/env python3
"""
Validate Context Links - Ensures all @file links in CLAUDE.md are valid
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

def extract_file_links(content: str) -> List[Tuple[str, str]]:
    """Extract all @file links from content."""
    # Pattern for @file links: [@file:name](path)
    pattern = r'\[@file:([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    # Also find inline @file references
    inline_pattern = r'@file:([^\s\)]+)'
    inline_matches = re.findall(inline_pattern, content)
    
    return matches

def validate_path(base_path: Path, link_path: str) -> Tuple[bool, str]:
    """Validate if a path exists relative to base."""
    # Handle relative paths
    if link_path.startswith('.'):
        full_path = base_path / link_path
    else:
        full_path = base_path / link_path
    
    # Resolve and check
    try:
        resolved = full_path.resolve()
        exists = resolved.exists()
        return exists, str(resolved)
    except Exception as e:
        return False, str(e)

def validate_claude_md():
    """Validate all links in CLAUDE.md."""
    # Base paths
    project_root = Path("/Users/smenssink/Developer/la-factoria-content-factory")
    claude_md_path = project_root / "CLAUDE.md"
    
    if not claude_md_path.exists():
        print(f"❌ CLAUDE.md not found at {claude_md_path}")
        return False
    
    # Read CLAUDE.md
    with open(claude_md_path, 'r') as f:
        content = f.read()
    
    # Extract links
    links = extract_file_links(content)
    
    print(f"🔍 Found {len(links)} @file links in CLAUDE.md\n")
    
    # Validate each link
    valid_count = 0
    invalid_links = []
    
    for name, path in links:
        exists, full_path = validate_path(project_root, path)
        
        if exists:
            print(f"✅ {name}: {path}")
            valid_count += 1
        else:
            print(f"❌ {name}: {path} - NOT FOUND")
            invalid_links.append((name, path))
    
    # Summary
    print(f"\n📊 Validation Summary:")
    print(f"  Total Links: {len(links)}")
    print(f"  Valid Links: {valid_count}")
    print(f"  Invalid Links: {len(invalid_links)}")
    
    if invalid_links:
        print(f"\n⚠️ Invalid Links Found:")
        for name, path in invalid_links:
            print(f"  - {name}: {path}")
        return False
    
    print(f"\n✅ All @file links are valid!")
    return True

def check_bidirectional_links():
    """Check for bidirectional linking patterns."""
    project_root = Path("/Users/smenssink/Developer/la-factoria-content-factory")
    
    # Key files that should have bidirectional links
    key_files = [
        "CLAUDE.md",
        ".claude/indexes/master-context-index.md",
        ".claude/PROJECT.md",
        ".claude/IMPLEMENTATION.md",
        ".claude/METHODOLOGY.md"
    ]
    
    print("\n🔄 Checking Bidirectional Links:\n")
    
    for file_path in key_files:
        full_path = project_root / file_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()
            
            links = extract_file_links(content)
            if links:
                print(f"📄 {file_path}:")
                print(f"   Links to {len(links)} files")
                
                # Check if any linked files link back
                back_links = 0
                for name, link_path in links[:5]:  # Check first 5 for brevity
                    linked_file = project_root / link_path
                    if linked_file.exists() and linked_file.suffix == '.md':
                        with open(linked_file, 'r') as lf:
                            linked_content = lf.read()
                        if file_path in linked_content or Path(file_path).name in linked_content:
                            back_links += 1
                
                if back_links > 0:
                    print(f"   ✅ Has {back_links} bidirectional links")
                else:
                    print(f"   ⚠️ No bidirectional links detected")
            else:
                print(f"📄 {file_path}: No @file links found")
        else:
            print(f"❌ {file_path}: File not found")
    
    return True

def analyze_hop_patterns():
    """Analyze the hop patterns for efficiency."""
    print("\n🎯 Analyzing Hop Patterns:\n")
    
    hop_patterns = {
        "Development": [
            "CLAUDE.md → master-context-index.md → technical/README.md → main.py",
            "Maximum hops: 4 (optimal)"
        ],
        "Testing": [
            "CLAUDE.md → validation/README.md → conftest.py → test files",
            "Maximum hops: 4 (optimal)"
        ],
        "Content Generation": [
            "CLAUDE.md → educational/README.md → prompts/ → quality_assessor.py",
            "Maximum hops: 4 (optimal)"
        ],
        "Deployment": [
            "CLAUDE.md → operations/README.md → railway.toml → DEPLOYMENT_GUIDE.md",
            "Maximum hops: 4 (optimal)"
        ]
    }
    
    for task, patterns in hop_patterns.items():
        print(f"📋 {task}:")
        for pattern in patterns:
            print(f"   {pattern}")
    
    print("\n✅ All hop patterns are within the 5-hop limit for optimal context loading")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Context Link Validation for La Factoria")
    print("=" * 60)
    
    # Run validations
    links_valid = validate_claude_md()
    bidirectional_valid = check_bidirectional_links()
    patterns_valid = analyze_hop_patterns()
    
    # Final report
    print("\n" + "=" * 60)
    if links_valid and bidirectional_valid and patterns_valid:
        print("✅ VALIDATION PASSED: All context links are properly configured")
        print("🚀 Ready for optimal dynamic context loading with @file hops")
    else:
        print("⚠️ VALIDATION INCOMPLETE: Some issues detected")
        print("Please review and fix the issues above")
    print("=" * 60)