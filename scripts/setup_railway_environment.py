#!/usr/bin/env python3
"""
Railway Environment Setup Script for La Factoria
===============================================

This script automates the Railway production environment setup for La Factoria,
including project initialization, addon configuration, and environment variables.

Usage:
    python3 scripts/setup_railway_environment.py [options]

Options:
    --dry-run         Show what would be done without executing
    --skip-auth       Skip Railway authentication (assume already logged in)
    --skip-addons     Skip addon setup (PostgreSQL and Redis)
    --project-name    Specify Railway project name (default: la-factoria)
    --verbose         Enable verbose output

Requirements:
    - Railway CLI installed (npm install -g @railway/cli)
    - Railway account and authentication
    - Environment variables for API keys (optional for initial setup)
"""

import os
import sys
import subprocess
import json
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class RailwayEnvironmentSetup:
    """Railway production environment setup automation"""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.project_root = project_root
        self.setup_log = []
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log setup progress with timestamps"""
        timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.setup_log.append(log_entry)
        
        if self.verbose and level == "DEBUG":
            print(f"  DEBUG: {message}")
    
    def run_command(self, cmd: List[str], description: str = None, capture_output: bool = True) -> Tuple[bool, str]:
        """Run command with error handling and logging"""
        cmd_str = " ".join(cmd)
        
        if description:
            self.log(f"{description}: {cmd_str}")
        else:
            self.log(f"Running: {cmd_str}")
        
        if self.dry_run:
            self.log("DRY RUN: Command not executed", "DEBUG")
            return True, "DRY RUN - command not executed"
        
        try:
            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
                if result.returncode == 0:
                    self.log("Command completed successfully", "DEBUG")
                    return True, result.stdout.strip()
                else:
                    self.log(f"Command failed with exit code {result.returncode}: {result.stderr}", "ERROR")
                    return False, result.stderr.strip()
            else:
                result = subprocess.run(cmd, cwd=self.project_root)
                success = result.returncode == 0
                status = "success" if success else f"failed with exit code {result.returncode}"
                self.log(f"Command completed: {status}", "DEBUG")
                return success, status
        except Exception as e:
            self.log(f"Command execution error: {str(e)}", "ERROR")
            return False, str(e)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.log("🔍 Checking Prerequisites")
        
        # Check if Railway CLI is installed
        success, output = self.run_command(["railway", "--version"], "Checking Railway CLI")
        if not success:
            self.log("❌ Railway CLI not found. Install with: npm install -g @railway/cli", "ERROR")
            return False
        
        self.log(f"✅ Railway CLI installed: {output}")
        
        # Check if railway.toml exists
        railway_toml = self.project_root / "railway.toml"
        if not railway_toml.exists():
            self.log("❌ railway.toml not found", "ERROR")
            return False
        
        self.log("✅ railway.toml configuration found")
        
        # Check if requirements.txt exists
        requirements_txt = self.project_root / "requirements.txt"
        if not requirements_txt.exists():
            self.log("❌ requirements.txt not found", "ERROR")
            return False
            
        self.log("✅ requirements.txt found")
        
        return True
    
    def authenticate_railway(self, skip_auth: bool = False) -> bool:
        """Authenticate with Railway"""
        if skip_auth:
            self.log("⏩ Skipping Railway authentication (assumed already logged in)")
            return True
            
        self.log("🔐 Authenticating with Railway")
        
        # Check if already authenticated
        success, output = self.run_command(["railway", "whoami"], "Checking current auth status")
        if success:
            self.log(f"✅ Already authenticated: {output}")
            return True
        
        self.log("🌐 Opening Railway login in browser...")
        success, output = self.run_command(["railway", "login"], "Railway authentication", capture_output=False)
        
        if success:
            self.log("✅ Railway authentication successful")
            return True
        else:
            self.log("❌ Railway authentication failed", "ERROR")
            return False
    
    def initialize_project(self, project_name: str = "la-factoria") -> bool:
        """Initialize or link Railway project"""
        self.log(f"🚀 Initializing Railway Project: {project_name}")
        
        # Check if already linked to a project
        success, output = self.run_command(["railway", "status"], "Checking project status")
        if success and "Project:" in output:
            self.log(f"✅ Already linked to Railway project")
            return True
        
        # Try to link to existing project first
        self.log("🔗 Attempting to link to existing project...")
        success, output = self.run_command(["railway", "link"], "Linking to existing project", capture_output=False)
        
        if success:
            self.log("✅ Successfully linked to existing project")
            return True
        
        # If linking fails, initialize new project
        self.log(f"📦 Creating new Railway project: {project_name}")
        success, output = self.run_command(["railway", "init", project_name], "Creating new project", capture_output=False)
        
        if success:
            self.log(f"✅ Railway project '{project_name}' initialized successfully")
            return True
        else:
            self.log("❌ Project initialization failed", "ERROR")
            return False
    
    def setup_postgresql_addon(self) -> bool:
        """Setup PostgreSQL addon"""
        self.log("🐘 Setting up PostgreSQL Database")
        
        # Check if PostgreSQL is already configured
        success, output = self.run_command(["railway", "variables"], "Checking existing variables")
        if success and "DATABASE_URL" in output:
            self.log("✅ PostgreSQL already configured (DATABASE_URL found)")
            return True
        
        # Add PostgreSQL addon
        self.log("📦 Adding PostgreSQL addon...")
        success, output = self.run_command(["railway", "add", "--database", "postgresql"], "Adding PostgreSQL")
        
        if success:
            self.log("✅ PostgreSQL addon added successfully")
            
            # Wait for DATABASE_URL to be available
            self.log("⏳ Waiting for DATABASE_URL to be configured...")
            for attempt in range(30):  # Wait up to 30 seconds
                if self.dry_run:
                    break
                    
                time.sleep(1)
                success, output = self.run_command(["railway", "variables"], "Checking for DATABASE_URL")
                if success and "DATABASE_URL" in output:
                    self.log("✅ DATABASE_URL configured")
                    return True
            
            if not self.dry_run:
                self.log("⚠️  DATABASE_URL not found after waiting, but addon was added", "WARNING")
            return True
        else:
            self.log("❌ Failed to add PostgreSQL addon", "ERROR") 
            return False
    
    def setup_redis_addon(self) -> bool:
        """Setup Redis addon (optional)"""
        self.log("🔴 Setting up Redis Cache (Optional)")
        
        # Check if Redis is already configured
        success, output = self.run_command(["railway", "variables"], "Checking existing variables")
        if success and "REDIS_URL" in output:
            self.log("✅ Redis already configured (REDIS_URL found)")
            return True
        
        # Add Redis addon
        self.log("📦 Adding Redis addon...")
        success, output = self.run_command(["railway", "add", "--database", "redis"], "Adding Redis")
        
        if success:
            self.log("✅ Redis addon added successfully")
            
            # Wait for REDIS_URL to be available
            self.log("⏳ Waiting for REDIS_URL to be configured...")
            for attempt in range(30):  # Wait up to 30 seconds
                if self.dry_run:
                    break
                    
                time.sleep(1)
                success, output = self.run_command(["railway", "variables"], "Checking for REDIS_URL")
                if success and "REDIS_URL" in output:
                    self.log("✅ REDIS_URL configured")
                    return True
            
            if not self.dry_run:
                self.log("⚠️  REDIS_URL not found after waiting, but addon was added", "WARNING")
            return True
        else:
            self.log("⚠️  Failed to add Redis addon (continuing without caching)", "WARNING")
            return True  # Redis is optional, so continue
    
    def configure_environment_variables(self) -> bool:
        """Configure essential environment variables"""
        self.log("⚙️  Configuring Environment Variables")
        
        # Define required environment variables
        required_vars = {
            "ENVIRONMENT": "production",
            "DEBUG": "false", 
            "APP_NAME": "La Factoria",
            "APP_VERSION": "1.0.0",
            "QUALITY_THRESHOLD_OVERALL": "0.70",
            "QUALITY_THRESHOLD_EDUCATIONAL": "0.75", 
            "QUALITY_THRESHOLD_FACTUAL": "0.85",
            "RATE_LIMIT_REQUESTS_PER_MINUTE": "100",
            "MAX_CONCURRENT_GENERATIONS": "10",
            "LOG_LEVEL": "INFO",
            "METRICS_ENABLED": "true"
        }
        
        # Optional variables that should be set if available in environment
        optional_vars = {
            "SECRET_KEY": os.getenv("SECRET_KEY"),
            "LA_FACTORIA_API_KEY": os.getenv("LA_FACTORIA_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT"),
            "LANGFUSE_PUBLIC_KEY": os.getenv("LANGFUSE_PUBLIC_KEY"),
            "LANGFUSE_SECRET_KEY": os.getenv("LANGFUSE_SECRET_KEY"),
            "LANGFUSE_HOST": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY")
        }
        
        # Set required variables
        for var_name, var_value in required_vars.items():
            success, output = self.run_command(
                ["railway", "variables", "set", f"{var_name}={var_value}"],
                f"Setting {var_name}"
            )
            if success:
                self.log(f"✅ {var_name} configured")
            else:
                self.log(f"❌ Failed to set {var_name}", "ERROR")
                return False
        
        # Set optional variables if available
        vars_set = 0
        vars_available = 0
        
        for var_name, var_value in optional_vars.items():
            if var_value:
                vars_available += 1
                success, output = self.run_command(
                    ["railway", "variables", "set", f"{var_name}={var_value}"],
                    f"Setting {var_name}"
                )
                if success:
                    self.log(f"✅ {var_name} configured")
                    vars_set += 1
                else:
                    self.log(f"⚠️  Failed to set {var_name}", "WARNING")
        
        self.log(f"📊 Environment Variables: {len(required_vars)} required + {vars_set}/{vars_available} optional configured")
        
        # Warn about missing critical variables
        critical_vars = ["SECRET_KEY", "LA_FACTORIA_API_KEY", "OPENAI_API_KEY"]
        missing_critical = [var for var in critical_vars if not optional_vars.get(var)]
        
        if missing_critical:
            self.log("⚠️  CRITICAL: The following variables need to be set manually:", "WARNING")
            for var in missing_critical:
                self.log(f"   railway variables set {var}=your-{var.lower().replace('_', '-')}-here", "WARNING")
        
        return True
    
    def validate_setup(self) -> Dict[str, bool]:
        """Validate the Railway environment setup"""
        self.log("✅ Validating Railway Environment Setup")
        
        validation_results = {}
        
        # Check project status
        success, output = self.run_command(["railway", "status"], "Checking project status")
        validation_results["project_initialized"] = success and "Project:" in output
        
        if validation_results["project_initialized"]:
            self.log("✅ Railway project initialized and linked")
        else:
            self.log("❌ Railway project not properly initialized", "ERROR")
        
        # Check environment variables
        success, output = self.run_command(["railway", "variables"], "Checking environment variables")
        if success:
            required_vars = ["ENVIRONMENT", "QUALITY_THRESHOLD_OVERALL", "APP_NAME"]
            vars_present = all(var in output for var in required_vars)
            validation_results["environment_variables_configured"] = vars_present
            
            if vars_present:
                self.log("✅ Environment variables configured")
            else:
                self.log("❌ Required environment variables missing", "ERROR")
        else:
            validation_results["environment_variables_configured"] = False
            self.log("❌ Could not check environment variables", "ERROR")
        
        # Check PostgreSQL addon
        if not self.dry_run:
            success, output = self.run_command(["railway", "variables"], "Checking PostgreSQL")
            validation_results["postgresql_addon_connected"] = success and "DATABASE_URL" in output
        else:
            validation_results["postgresql_addon_connected"] = True  # Assume success in dry run
        
        if validation_results["postgresql_addon_connected"]:
            self.log("✅ PostgreSQL addon connected")
        else:
            self.log("❌ PostgreSQL addon not connected", "ERROR")
        
        # Check Redis addon (optional)
        if not self.dry_run:
            success, output = self.run_command(["railway", "variables"], "Checking Redis")
            validation_results["redis_addon_configured"] = success and "REDIS_URL" in output
        else:
            validation_results["redis_addon_configured"] = True  # Assume success in dry run
        
        if validation_results["redis_addon_configured"]:
            self.log("✅ Redis addon configured")
        else:
            self.log("⚠️  Redis addon not configured (optional)", "WARNING")
        
        return validation_results
    
    def generate_setup_report(self, validation_results: Dict[str, bool]) -> None:
        """Generate comprehensive setup report"""
        self.log("\n" + "="*60)
        self.log("🎯 RAILWAY ENVIRONMENT SETUP REPORT")
        self.log("="*60)
        
        # Summary
        total_checks = len(validation_results)
        passed_checks = sum(validation_results.values())
        success_rate = (passed_checks / total_checks) * 100
        
        self.log(f"📊 Setup Status: {passed_checks}/{total_checks} checks passed ({success_rate:.1f}%)")
        
        # Individual results
        self.log("\n📋 Detailed Results:")
        for check, result in validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            check_name = check.replace('_', ' ').title()
            self.log(f"   {check_name}: {status}")
        
        # Next steps
        self.log("\n🚀 Next Steps:")
        if all(validation_results.values()):
            self.log("✅ Railway environment setup completed successfully!")
            self.log("   Ready for Phase 3C: Deploy to Railway Staging")
            self.log("   Run: railway up")
        else:
            self.log("⚠️  Setup incomplete. Address the following:")
            for check, result in validation_results.items():
                if not result:
                    self.log(f"   - Fix: {check.replace('_', ' ')}")
        
        # Environment variable reminders
        self.log("\n🔑 Important Environment Variables to Set:")
        self.log("   railway variables set SECRET_KEY=your-secure-secret-key")
        self.log("   railway variables set LA_FACTORIA_API_KEY=your-api-key")
        self.log("   railway variables set OPENAI_API_KEY=sk-your-openai-key")
        
        # Deployment commands
        self.log("\n⚡ Quick Deployment Commands:")
        self.log("   railway up                    # Deploy to production")
        self.log("   railway logs                  # View application logs")
        self.log("   railway open                  # Open in browser")
        self.log("   railway status                # Check deployment status")
        
        self.log("="*60)
    
    def save_setup_log(self) -> None:
        """Save setup log to file"""
        log_file = self.project_root / f"railway_setup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(log_file, 'w') as f:
            f.write("La Factoria Railway Environment Setup Log\n")
            f.write("="*50 + "\n\n")
            for log_entry in self.setup_log:
                f.write(log_entry + "\n")
        
        self.log(f"📝 Setup log saved: {log_file}")
    
    def run_setup(self, skip_auth: bool = False, skip_addons: bool = False, project_name: str = "la-factoria") -> bool:
        """Run complete Railway environment setup"""
        self.log("🚀 Starting Railway Environment Setup for La Factoria")
        self.log(f"📁 Project Directory: {self.project_root}")
        
        if self.dry_run:
            self.log("🔍 DRY RUN MODE - No changes will be made", "WARNING")
        
        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: Authenticate
            if not self.authenticate_railway(skip_auth):
                return False
            
            # Step 3: Initialize project
            if not self.initialize_project(project_name):
                return False
            
            # Step 4: Setup addons (if not skipped)
            if not skip_addons:
                if not self.setup_postgresql_addon():
                    return False
                
                if not self.setup_redis_addon():
                    return False
            
            # Step 5: Configure environment variables
            if not self.configure_environment_variables():
                return False
            
            # Step 6: Validate setup
            validation_results = self.validate_setup()
            
            # Step 7: Generate report
            self.generate_setup_report(validation_results)
            
            # Step 8: Save log
            self.save_setup_log()
            
            # Return success if all critical validations pass
            critical_validations = ["project_initialized", "environment_variables_configured", "postgresql_addon_connected"]
            return all(validation_results.get(check, False) for check in critical_validations)
            
        except KeyboardInterrupt:
            self.log("⚠️  Setup interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"❌ Setup failed with error: {str(e)}", "ERROR")
            return False

def main():
    """Main entry point for Railway environment setup"""
    parser = argparse.ArgumentParser(description="Setup Railway production environment for La Factoria")
    
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without executing")
    parser.add_argument("--skip-auth", action="store_true", 
                       help="Skip Railway authentication (assume already logged in)")
    parser.add_argument("--skip-addons", action="store_true",
                       help="Skip addon setup (PostgreSQL and Redis)")
    parser.add_argument("--project-name", default="la-factoria",
                       help="Railway project name (default: la-factoria)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Create setup instance
    setup = RailwayEnvironmentSetup(dry_run=args.dry_run, verbose=args.verbose)
    
    # Run setup
    success = setup.run_setup(
        skip_auth=args.skip_auth,
        skip_addons=args.skip_addons,
        project_name=args.project_name
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()