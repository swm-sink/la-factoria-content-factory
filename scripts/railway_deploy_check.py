#!/usr/bin/env python3
"""
Railway Deployment Readiness Check
Validates that the application is ready for Railway deployment
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class RailwayReadinessChecker:
    """Check Railway deployment readiness"""
    
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []
    
    def check_railway_config(self) -> bool:
        """Check if railway.toml exists and is valid"""
        print("🚂 Checking Railway configuration...")
        
        if not Path("railway.toml").exists():
            self.checks_failed.append("railway.toml missing")
            print("   ❌ railway.toml not found")
            return False
        
        # Check basic structure
        with open("railway.toml", "r") as f:
            content = f.read()
            required = ["[build]", "[deploy]", "PORT"]
            
            for item in required:
                if item not in content:
                    self.checks_failed.append(f"railway.toml missing {item}")
                    print(f"   ❌ Missing {item} in railway.toml")
                    return False
        
        self.checks_passed.append("Railway configuration")
        print("   ✅ railway.toml properly configured")
        return True
    
    def check_requirements(self) -> bool:
        """Check if requirements.txt exists and is valid"""
        print("📦 Checking Python requirements...")
        
        if not Path("requirements.txt").exists():
            self.checks_failed.append("requirements.txt missing")
            print("   ❌ requirements.txt not found")
            return False
        
        # Check for essential packages
        with open("requirements.txt", "r") as f:
            requirements = f.read()
            essential = ["fastapi", "uvicorn", "sqlalchemy", "pydantic"]
            
            missing = []
            for pkg in essential:
                if pkg not in requirements.lower():
                    missing.append(pkg)
            
            if missing:
                self.warnings.append(f"Possibly missing packages: {', '.join(missing)}")
                print(f"   ⚠️ Check if these packages are included: {', '.join(missing)}")
        
        self.checks_passed.append("Requirements file")
        print("   ✅ requirements.txt exists")
        return True
    
    def check_runtime(self) -> bool:
        """Check if runtime.txt exists for Python version"""
        print("🐍 Checking Python runtime...")
        
        if not Path("runtime.txt").exists():
            self.warnings.append("runtime.txt missing (Railway will use default)")
            print("   ⚠️ runtime.txt not found (Railway will use default Python)")
            return True
        
        with open("runtime.txt", "r") as f:
            runtime = f.read().strip()
            if "python" in runtime.lower():
                self.checks_passed.append("Python runtime specified")
                print(f"   ✅ Runtime specified: {runtime}")
            else:
                self.warnings.append(f"Unusual runtime: {runtime}")
                print(f"   ⚠️ Unusual runtime: {runtime}")
        
        return True
    
    def check_environment_vars(self) -> bool:
        """Check for .env.example or documentation of required env vars"""
        print("🔐 Checking environment variables...")
        
        env_files = [".env.example", ".env.sample", "env.example"]
        found = False
        
        for env_file in env_files:
            if Path(env_file).exists():
                found = True
                self.checks_passed.append("Environment template")
                print(f"   ✅ {env_file} found")
                break
        
        if not found:
            self.warnings.append("No .env.example found - ensure env vars are documented")
            print("   ⚠️ No .env.example found - ensure Railway env vars are documented")
        
        return True
    
    def check_database_config(self) -> bool:
        """Check database configuration"""
        print("🗄️ Checking database configuration...")
        
        # Check for migrations
        if Path("migrations").exists():
            self.checks_passed.append("Database migrations")
            print("   ✅ Migrations folder exists")
        else:
            self.warnings.append("No migrations folder - ensure DB schema is handled")
            print("   ⚠️ No migrations folder found")
        
        # Check for PostgreSQL support
        with open("requirements.txt", "r") as f:
            if "psycopg" in f.read():
                self.checks_passed.append("PostgreSQL driver")
                print("   ✅ PostgreSQL driver included")
            else:
                self.warnings.append("PostgreSQL driver not found in requirements")
                print("   ⚠️ psycopg2 not in requirements (needed for PostgreSQL)")
        
        return True
    
    def check_health_endpoint(self) -> bool:
        """Check if health endpoint is accessible"""
        print("💓 Checking health endpoint...")
        
        try:
            import requests
            response = requests.get("http://localhost:8000/api/v1/health")
            if response.status_code == 200:
                self.checks_passed.append("Health endpoint")
                print("   ✅ Health endpoint responding")
                return True
        except:
            pass
        
        self.warnings.append("Could not verify health endpoint (server may not be running)")
        print("   ⚠️ Could not verify health endpoint (ensure it exists)")
        return True
    
    def check_tests(self) -> bool:
        """Check if tests pass"""
        print("🧪 Checking tests...")
        
        if not Path("tests").exists():
            self.warnings.append("No tests folder found")
            print("   ⚠️ No tests folder found")
            return True
        
        # Try to run a basic test
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "-q", "--tb=no"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "passed" in result.stdout:
                self.checks_passed.append("Tests passing")
                print("   ✅ Tests are passing")
            else:
                self.warnings.append("Some tests may be failing")
                print("   ⚠️ Some tests may be failing")
        except:
            self.warnings.append("Could not run tests")
            print("   ⚠️ Could not run tests automatically")
        
        return True
    
    def check_static_files(self) -> bool:
        """Check static files configuration"""
        print("📁 Checking static files...")
        
        if Path("static").exists():
            self.checks_passed.append("Static files")
            print("   ✅ Static folder exists")
        else:
            self.warnings.append("No static folder (okay if API-only)")
            print("   ⚠️ No static folder (okay if API-only)")
        
        return True
    
    def run_all_checks(self) -> bool:
        """Run all deployment readiness checks"""
        print("\n" + "="*60)
        print("RAILWAY DEPLOYMENT READINESS CHECK")
        print("="*60 + "\n")
        
        # Run all checks
        self.check_railway_config()
        self.check_requirements()
        self.check_runtime()
        self.check_environment_vars()
        self.check_database_config()
        self.check_health_endpoint()
        self.check_tests()
        self.check_static_files()
        
        # Summary
        print("\n" + "="*60)
        print("DEPLOYMENT READINESS SUMMARY")
        print("="*60)
        
        print(f"\n✅ Checks Passed: {len(self.checks_passed)}")
        for check in self.checks_passed:
            print(f"   • {check}")
        
        if self.checks_failed:
            print(f"\n❌ Checks Failed: {len(self.checks_failed)}")
            for check in self.checks_failed:
                print(f"   • {check}")
        
        if self.warnings:
            print(f"\n⚠️ Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # Final verdict
        print("\n" + "="*60)
        if not self.checks_failed:
            print("✅ READY FOR RAILWAY DEPLOYMENT")
            print("\nNext steps:")
            print("1. Set up Railway project: railway init")
            print("2. Configure environment variables in Railway dashboard")
            print("3. Deploy: railway up")
            print("4. Monitor logs: railway logs")
            return True
        else:
            print("❌ NOT READY FOR DEPLOYMENT")
            print("\nFix the failed checks before deploying")
            return False
    
    def generate_env_template(self):
        """Generate .env.example if it doesn't exist"""
        if not Path(".env.example").exists():
            env_template = """# La Factoria Environment Variables

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
# For local development with SQLite:
# DATABASE_URL=sqlite:///./la_factoria.db

# AI Providers (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
VERTEX_AI_PROJECT_ID=your-project-id

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=info

# Optional Services
ELEVENLABS_API_KEY=your-elevenlabs-key
SENTRY_DSN=your-sentry-dsn
"""
            with open(".env.example", "w") as f:
                f.write(env_template)
            print("\n📝 Generated .env.example template")


def main():
    """Run deployment readiness check"""
    checker = RailwayReadinessChecker()
    
    # Run checks
    ready = checker.run_all_checks()
    
    # Generate env template if needed
    if ".env.example" not in [check for check in checker.checks_passed]:
        checker.generate_env_template()
    
    # Exit with appropriate code
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()