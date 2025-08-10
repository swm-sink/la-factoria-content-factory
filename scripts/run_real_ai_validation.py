#!/usr/bin/env python3
"""
Real AI Content Validation Runner for La Factoria
===============================================

This script runs comprehensive validation of all 8 educational content types
with real AI providers to validate production readiness.

IMPORTANT: This will consume API credits from configured AI providers.
Only run when you have proper API keys and want to validate production quality.

Usage:
    python scripts/run_real_ai_validation.py [options]

Options:
    --content-type TYPE    Test only specific content type
    --age-group GROUP      Test only specific age group  
    --quick                Run quick validation (reduced test coverage)
    --report               Generate detailed HTML report
    --no-ai-check         Skip AI API key validation
"""

import os
import sys
import asyncio
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# AI Provider validation
def check_ai_providers() -> Dict[str, bool]:
    """Check which AI providers are configured with API keys"""
    providers = {
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "Anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "Google Cloud": bool(os.getenv("GOOGLE_CLOUD_PROJECT") and 
                           (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or 
                            os.getenv("GOOGLE_CLOUD_KEY_JSON")))
    }
    return providers

def print_provider_status(providers: Dict[str, bool]) -> bool:
    """Print AI provider status and return if any are configured"""
    print("🤖 AI Provider Status:")
    
    any_configured = False
    for provider, configured in providers.items():
        status = "✅ Configured" if configured else "❌ Not Configured"
        print(f"   {provider}: {status}")
        if configured:
            any_configured = True
    
    if not any_configured:
        print("\n⚠️  WARNING: No AI providers configured!")
        print("   Set one of these environment variables:")
        print("   - OPENAI_API_KEY (for OpenAI/GPT-4)")  
        print("   - ANTHROPIC_API_KEY (for Claude)")
        print("   - GOOGLE_CLOUD_PROJECT + GOOGLE_APPLICATION_CREDENTIALS (for Vertex AI)")
        print("\n   Tests will be skipped without API keys.")
        return False
    
    print(f"\n✅ {sum(providers.values())} AI provider(s) ready for testing")
    return True

def run_pytest_command(args: List[str]) -> subprocess.CompletedProcess:
    """Run pytest with specified arguments"""
    cmd = ["python3", "-m", "pytest"] + args
    print(f"🔬 Running: {' '.join(cmd)}")
    print("-" * 60)
    
    return subprocess.run(cmd, cwd=project_root)

def generate_validation_report(results: Dict[str, Any], output_path: Path) -> None:
    """Generate HTML validation report"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>La Factoria Real AI Validation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #2E8B57; color: white; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #2E8B57; }}
            .success {{ color: #28a745; font-weight: bold; }}
            .warning {{ color: #ffc107; font-weight: bold; }}
            .error {{ color: #dc3545; font-weight: bold; }}
            .metric {{ margin: 10px 0; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎓 La Factoria Real AI Validation Report</h1>
            <p>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        
        <div class="section">
            <h2>📊 Validation Summary</h2>
            <div class="metric">Tests Run: <strong>{results.get('tests_run', 'N/A')}</strong></div>
            <div class="metric">Tests Passed: <strong class="success">{results.get('tests_passed', 'N/A')}</strong></div>
            <div class="metric">Tests Failed: <strong class="error">{results.get('tests_failed', 'N/A')}</strong></div>
            <div class="metric">Success Rate: <strong>{results.get('success_rate', 'N/A')}%</strong></div>
        </div>
        
        <div class="section">
            <h2>🤖 AI Provider Status</h2>
            <table>
                <tr><th>Provider</th><th>Status</th></tr>
                {chr(10).join(f'<tr><td>{provider}</td><td class="{"success" if configured else "error"}">{"✅ Ready" if configured else "❌ Not Configured"}</td></tr>' 
                             for provider, configured in results.get('providers', {}).items())}
            </table>
        </div>
        
        <div class="section">
            <h2>🎯 Content Type Results</h2>
            <p>Validation results for all 8 La Factoria educational content types:</p>
            {results.get('content_type_details', '<p>Details not available</p>')}
        </div>
        
        <div class="section">
            <h2>📈 Quality Metrics</h2>
            <p>Educational quality thresholds validation:</p>
            {results.get('quality_details', '<p>Quality metrics not available</p>')}
        </div>
        
        <div class="section">
            <h2>🏁 Recommendations</h2>
            {results.get('recommendations', '<p>No specific recommendations</p>')}
        </div>
    </body>
    </html>
    """
    
    output_path.write_text(html_content)
    print(f"\n📋 Detailed report generated: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Run La Factoria Real AI Validation Tests")
    
    parser.add_argument("--content-type", 
                       help="Test only specific content type (e.g., study_guide)")
    parser.add_argument("--age-group", 
                       help="Test only specific age group (e.g., high_school)")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick validation with reduced coverage")
    parser.add_argument("--report", action="store_true", 
                       help="Generate detailed HTML report")
    parser.add_argument("--no-ai-check", action="store_true",
                       help="Skip AI provider validation check")
    parser.add_argument("--force", action="store_true",
                       help="Force run even without AI providers configured")
    
    args = parser.parse_args()

    print("🎓 La Factoria Real AI Content Validation")
    print("=" * 50)

    # Check AI provider configuration
    providers = check_ai_providers()
    
    if not args.no_ai_check and not any(providers.values()) and not args.force:
        print("\n❌ No AI providers configured. Use --force to run anyway (tests will be skipped).")
        return 1

    # Build pytest command
    pytest_args = [
        "tests/test_real_ai_content_validation.py",
        "-v",
        "--tb=short",
        "-m", "real_ai"
    ]

    # Add content type filter if specified
    if args.content_type:
        pytest_args.extend(["-k", f"test_{args.content_type}_real_ai"])

    # Quick mode - run subset of tests
    if args.quick:
        pytest_args.extend(["-k", "test_master_content_outline_real_ai or test_study_guide_real_ai or test_flashcards_real_ai"])
        print("🚀 Running QUICK validation (3 content types)")
    else:
        print("🔬 Running COMPREHENSIVE validation (all 8 content types)")

    # Run validation tests
    print(f"\n⏱️  Starting validation at {datetime.now().strftime('%H:%M:%S')}")
    result = run_pytest_command(pytest_args)
    
    # Parse results for reporting
    validation_results = {
        "providers": providers,
        "success_rate": "Unknown",
        "tests_run": "Unknown", 
        "tests_passed": "Unknown",
        "tests_failed": "Unknown",
        "exit_code": result.returncode
    }

    # Generate report if requested
    if args.report:
        report_path = project_root / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        generate_validation_report(validation_results, report_path)

    # Print final status
    print("\n" + "=" * 50)
    if result.returncode == 0:
        print("✅ VALIDATION SUCCESSFUL - All tests passed!")
        print("🎯 La Factoria is ready for production deployment")
    else:
        print("❌ VALIDATION FAILED - Some tests failed")
        print("🔧 Review failures before production deployment")
        
    print(f"⏱️  Completed at {datetime.now().strftime('%H:%M:%S')}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())