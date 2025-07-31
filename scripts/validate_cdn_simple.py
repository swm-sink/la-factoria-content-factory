#!/usr/bin/env python3
"""
Simple CDN Validation Script
Validates CDN is configured and working properly
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Tuple
from urllib.parse import urljoin

# CDN endpoints
CDN_ENDPOINTS = {
    "main": os.getenv("VITE_CDN_URL", "https://cdn.lafactoria.app"),
    "static": os.getenv("VITE_STATIC_URL", "https://static.lafactoria.app"),
}

# Test assets
TEST_ASSETS = {
    "js": ["/assets/js/index.js"],
    "css": ["/assets/css/index.css"],
    "images": ["/assets/images/logo.png"],
}

# Performance thresholds
THRESHOLDS = {
    "cache_hit_rate": 90,
    "response_time_ms": 500,
}


def test_cdn_availability() -> Dict[str, bool]:
    """Test if CDN endpoints are reachable"""
    results = {}
    
    for name, endpoint in CDN_ENDPOINTS.items():
        try:
            response = requests.head(endpoint, timeout=5)
            results[name] = response.status_code < 500
        except Exception as e:
            print(f"Error testing {name}: {e}")
            results[name] = False
    
    return results


def test_asset_delivery() -> Dict[str, Dict]:
    """Test asset delivery from CDN"""
    results = {}
    
    for asset_type, assets in TEST_ASSETS.items():
        results[asset_type] = {}
        
        for asset in assets:
            url = urljoin(CDN_ENDPOINTS['main'], asset)
            
            try:
                start = time.time()
                response = requests.get(url, timeout=10)
                elapsed_ms = (time.time() - start) * 1000
                
                results[asset_type][asset] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "response_time_ms": round(elapsed_ms, 2),
                    "size_bytes": len(response.content),
                    "headers": {
                        "cache-control": response.headers.get("Cache-Control", ""),
                        "content-encoding": response.headers.get("Content-Encoding", ""),
                        "cf-cache-status": response.headers.get("CF-Cache-Status", ""),
                    }
                }
            except Exception as e:
                results[asset_type][asset] = {
                    "success": False,
                    "error": str(e)
                }
    
    return results


def test_cache_headers() -> Dict[str, bool]:
    """Test if proper cache headers are set"""
    results = {}
    
    # Test a JS file for proper caching
    test_url = urljoin(CDN_ENDPOINTS['main'], "/assets/js/vendor.js")
    
    try:
        response = requests.head(test_url, timeout=5)
        cache_control = response.headers.get("Cache-Control", "")
        
        results["has_cache_control"] = bool(cache_control)
        results["has_max_age"] = "max-age=" in cache_control
        results["is_immutable"] = "immutable" in cache_control
        results["has_public"] = "public" in cache_control
        
    except Exception as e:
        print(f"Error testing cache headers: {e}")
        results["error"] = str(e)
    
    return results


def test_compression() -> Dict[str, bool]:
    """Test if compression is enabled"""
    results = {}
    
    test_url = urljoin(CDN_ENDPOINTS['main'], "/assets/css/index.css")
    
    try:
        # Test with compression headers
        headers = {"Accept-Encoding": "gzip, br"}
        response = requests.get(test_url, headers=headers, timeout=5)
        
        content_encoding = response.headers.get("Content-Encoding", "")
        results["compression_enabled"] = bool(content_encoding)
        results["encoding_type"] = content_encoding
        results["compressed"] = content_encoding in ["gzip", "br"]
        
    except Exception as e:
        print(f"Error testing compression: {e}")
        results["error"] = str(e)
    
    return results


def print_results(
    availability: Dict,
    asset_delivery: Dict,
    cache_headers: Dict,
    compression: Dict
):
    """Print validation results"""
    
    print("\n=== CDN Validation Results ===\n")
    
    # Availability
    print("1. CDN Availability:")
    for endpoint, available in availability.items():
        status = "✓" if available else "✗"
        print(f"   {status} {endpoint}: {CDN_ENDPOINTS[endpoint]}")
    
    # Asset Delivery
    print("\n2. Asset Delivery:")
    all_success = True
    for asset_type, assets in asset_delivery.items():
        print(f"   {asset_type.upper()}:")
        for asset, result in assets.items():
            if result.get("success"):
                print(f"     ✓ {asset} - {result['response_time_ms']}ms, {result['size_bytes']} bytes")
                if result['headers'].get('cf-cache-status'):
                    print(f"       Cache: {result['headers']['cf-cache-status']}")
            else:
                print(f"     ✗ {asset} - {result.get('error', 'Failed')}")
                all_success = False
    
    # Cache Headers
    print("\n3. Cache Headers:")
    for header, present in cache_headers.items():
        if not header.startswith("has_") and not header.startswith("is_"):
            continue
        status = "✓" if present else "✗"
        print(f"   {status} {header.replace('_', ' ').title()}")
    
    # Compression
    print("\n4. Compression:")
    if compression.get("compressed"):
        print(f"   ✓ Compression enabled: {compression['encoding_type']}")
    else:
        print(f"   ✗ Compression not enabled")
    
    # Summary
    print("\n=== Summary ===")
    
    # Calculate overall score
    total_checks = 0
    passed_checks = 0
    
    # Count availability checks
    for available in availability.values():
        total_checks += 1
        if available:
            passed_checks += 1
    
    # Count asset delivery
    for assets in asset_delivery.values():
        for result in assets.values():
            total_checks += 1
            if result.get("success"):
                passed_checks += 1
    
    # Count cache headers
    important_headers = ["has_cache_control", "has_max_age", "is_immutable"]
    for header in important_headers:
        if header in cache_headers:
            total_checks += 1
            if cache_headers[header]:
                passed_checks += 1
    
    # Count compression
    total_checks += 1
    if compression.get("compressed"):
        passed_checks += 1
    
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n✓ All CDN validation tests passed!")
        return 0
    else:
        print("\n✗ Some CDN validation tests failed!")
        return 1


def main():
    """Run CDN validation tests"""
    
    print("CDN Validation Starting...")
    print(f"Testing CDN: {CDN_ENDPOINTS['main']}")
    print(f"Testing Static: {CDN_ENDPOINTS['static']}")
    
    # Run tests
    availability = test_cdn_availability()
    asset_delivery = test_asset_delivery()
    cache_headers = test_cache_headers()
    compression = test_compression()
    
    # Print results
    exit_code = print_results(
        availability,
        asset_delivery,
        cache_headers,
        compression
    )
    
    # Save results to file
    results = {
        "timestamp": time.time(),
        "endpoints": CDN_ENDPOINTS,
        "availability": availability,
        "asset_delivery": asset_delivery,
        "cache_headers": cache_headers,
        "compression": compression,
    }
    
    with open("cdn_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to cdn_validation_results.json")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()