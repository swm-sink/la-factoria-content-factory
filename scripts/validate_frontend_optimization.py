#!/usr/bin/env python3
"""
Validate frontend bundle optimization implementation.
Checks that bundle sizes are optimized and code splitting is working correctly.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def check_vite_config() -> Tuple[bool, List[str]]:
    """Check if Vite is properly configured for optimization."""
    errors = []
    config_path = Path("frontend/vite.config.ts")
    
    if not config_path.exists():
        errors.append("Vite config not found at frontend/vite.config.ts")
        return False, errors
    
    config_content = config_path.read_text()
    
    # Check for optimization features
    required_features = [
        ("minify", "Minification not enabled"),
        ("terserOptions", "Terser options not configured"),
        ("manualChunks", "Manual chunking not configured"),
        ("rollup-plugin-visualizer", "Bundle analyzer not configured"),
        ("chunkSizeWarningLimit", "Chunk size limit not set"),
    ]
    
    for feature, error_msg in required_features:
        if feature not in config_content:
            errors.append(f"Vite config: {error_msg}")
    
    return len(errors) == 0, errors

def check_lazy_loading() -> Tuple[bool, List[str]]:
    """Check if lazy loading is implemented correctly."""
    errors = []
    
    # Check for lazy loading utility
    lazy_util = Path("frontend/src/utils/lazy.ts")
    if not lazy_util.exists():
        errors.append("Lazy loading utility not found at frontend/src/utils/lazy.ts")
    
    # Check App.tsx for lazy imports
    app_path = Path("frontend/src/App.tsx")
    if app_path.exists():
        app_content = app_path.read_text()
        
        required_patterns = [
            ("lazy(() => import", "React.lazy not used for dynamic imports"),
            ("Suspense", "Suspense not used for lazy components"),
            ("lazyLoad", "Custom lazy load utility not used"),
        ]
        
        for pattern, error_msg in required_patterns:
            if pattern not in app_content:
                errors.append(f"App.tsx: {error_msg}")
    else:
        errors.append("App.tsx not found")
    
    return len(errors) == 0, errors

def build_and_analyze() -> Tuple[bool, Dict[str, any]]:
    """Build the frontend and analyze bundle sizes."""
    os.chdir("frontend")
    
    try:
        # Install dependencies if needed
        if not Path("node_modules").exists():
            print("Installing dependencies...")
            subprocess.run(["npm", "install"], check=True, capture_output=True)
        
        # Build the project
        print("Building frontend...")
        result = subprocess.run(
            ["npm", "run", "build"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Build failed: {result.stderr}")
            return False, {"error": result.stderr}
        
        # Parse build output for bundle sizes
        output = result.stdout
        stats = {
            "total_size": 0,
            "chunks": [],
            "initial_bundle": 0
        }
        
        # Look for dist directory
        dist_path = Path("dist")
        if dist_path.exists():
            # Calculate total size
            total_size = 0
            js_files = list(dist_path.glob("**/*.js"))
            
            for js_file in js_files:
                size = js_file.stat().st_size
                total_size += size
                stats["chunks"].append({
                    "name": js_file.name,
                    "size": size,
                    "size_kb": round(size / 1024, 2)
                })
            
            # Find index.html and calculate initial bundle
            index_path = dist_path / "index.html"
            if index_path.exists():
                index_content = index_path.read_text()
                initial_size = 0
                
                # Find script tags that are not async/defer
                import re
                script_pattern = r'<script[^>]*src="([^"]+)"[^>]*>'
                scripts = re.findall(script_pattern, index_content)
                
                for script in scripts:
                    if "defer" not in script and "async" not in script:
                        script_path = dist_path / script.lstrip("/")
                        if script_path.exists():
                            initial_size += script_path.stat().st_size
                
                stats["initial_bundle"] = initial_size
                stats["initial_bundle_kb"] = round(initial_size / 1024, 2)
            
            stats["total_size"] = total_size
            stats["total_size_kb"] = round(total_size / 1024, 2)
        
        os.chdir("..")
        return True, stats
        
    except Exception as e:
        os.chdir("..")
        return False, {"error": str(e)}

def check_bundle_monitoring() -> Tuple[bool, List[str]]:
    """Check if bundle monitoring is set up in CI."""
    errors = []
    
    # Check GitHub Actions workflow
    ci_path = Path(".github/workflows/ci.yml")
    if ci_path.exists():
        ci_content = ci_path.read_text()
        if "bundle" not in ci_content.lower() and "size" not in ci_content.lower():
            errors.append("Bundle size monitoring not found in CI workflow")
    else:
        errors.append("CI workflow not found at .github/workflows/ci.yml")
    
    # Check for stats.html generation
    stats_configured = False
    vite_config = Path("frontend/vite.config.ts")
    if vite_config.exists():
        if "visualizer" in vite_config.read_text():
            stats_configured = True
    
    if not stats_configured:
        errors.append("Bundle analyzer (stats.html) not configured")
    
    return len(errors) == 0, errors

def main():
    """Run all validation checks."""
    print("Frontend Bundle Optimization Validation")
    print("=" * 50)
    
    all_passed = True
    
    # Check Vite configuration
    print("\n1. Checking Vite configuration...")
    passed, errors = check_vite_config()
    if passed:
        print("✅ Vite optimization configured correctly")
    else:
        print("❌ Vite configuration issues:")
        for error in errors:
            print(f"   - {error}")
        all_passed = False
    
    # Check lazy loading implementation
    print("\n2. Checking lazy loading implementation...")
    passed, errors = check_lazy_loading()
    if passed:
        print("✅ Lazy loading implemented correctly")
    else:
        print("❌ Lazy loading issues:")
        for error in errors:
            print(f"   - {error}")
        all_passed = False
    
    # Build and analyze bundle
    print("\n3. Building and analyzing bundle...")
    passed, stats = build_and_analyze()
    if passed and "error" not in stats:
        print("✅ Build successful")
        print(f"\nBundle Statistics:")
        print(f"   Total size: {stats.get('total_size_kb', 0)} KB")
        print(f"   Initial bundle: {stats.get('initial_bundle_kb', 0)} KB")
        print(f"   Number of chunks: {len(stats.get('chunks', []))}")
        
        # Check if initial bundle is under 200KB
        initial_kb = stats.get('initial_bundle_kb', 0)
        if initial_kb < 200:
            print(f"   ✅ Initial bundle size ({initial_kb} KB) is under 200KB target")
        else:
            print(f"   ❌ Initial bundle size ({initial_kb} KB) exceeds 200KB target")
            all_passed = False
        
        # Show chunk details
        if stats.get('chunks'):
            print("\n   Chunk details:")
            for chunk in sorted(stats['chunks'], key=lambda x: x['size'], reverse=True)[:5]:
                print(f"   - {chunk['name']}: {chunk['size_kb']} KB")
    else:
        print("❌ Build failed")
        if "error" in stats:
            print(f"   Error: {stats['error']}")
        all_passed = False
    
    # Check bundle monitoring
    print("\n4. Checking bundle monitoring setup...")
    passed, errors = check_bundle_monitoring()
    if passed:
        print("✅ Bundle monitoring configured")
    else:
        print("❌ Bundle monitoring issues:")
        for error in errors:
            print(f"   - {error}")
        # This is a warning, not a failure
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All frontend optimization checks passed!")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())