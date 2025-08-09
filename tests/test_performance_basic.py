#!/usr/bin/env python3
"""
Basic Performance Testing for La Factoria
Minimum viable performance validation for Phase 3D
"""

import time
import requests
import concurrent.futures
from typing import List, Dict
import statistics
import json


class PerformanceTester:
    """Simple performance tester using Python requests"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    def test_endpoint(self, endpoint: str, method: str = "GET", data: dict = None) -> float:
        """Test a single endpoint and return response time"""
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            elapsed = time.time() - start
            
            return {
                "endpoint": endpoint,
                "status": response.status_code,
                "time": elapsed * 1000,  # Convert to ms
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status": 0,
                "time": (time.time() - start) * 1000,
                "success": False,
                "error": str(e)
            }
    
    def load_test(self, endpoint: str, concurrent_users: int = 10, 
                  requests_per_user: int = 10, method: str = "GET", data: dict = None) -> Dict:
        """Run a simple load test"""
        print(f"\n🚀 Load Testing: {endpoint}")
        print(f"   Concurrent users: {concurrent_users}")
        print(f"   Requests per user: {requests_per_user}")
        print(f"   Total requests: {concurrent_users * requests_per_user}")
        
        all_results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            for user in range(concurrent_users):
                for req in range(requests_per_user):
                    future = executor.submit(self.test_endpoint, endpoint, method, data)
                    futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                all_results.append(result)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        successful = [r for r in all_results if r["success"]]
        failed = [r for r in all_results if not r["success"]]
        response_times = [r["time"] for r in successful]
        
        stats = {
            "endpoint": endpoint,
            "total_requests": len(all_results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(all_results) * 100 if all_results else 0,
            "total_time": total_time,
            "requests_per_second": len(all_results) / total_time if total_time > 0 else 0,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0,
                "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 1 else 0,
            }
        }
        
        return stats
    
    def run_performance_suite(self) -> Dict:
        """Run complete performance test suite"""
        print("\n" + "="*60)
        print("LA FACTORIA PERFORMANCE TEST SUITE")
        print("Phase 3D - Minimum Viable Performance Validation")
        print("="*60)
        
        test_results = []
        
        # Test 1: Health endpoint (baseline)
        health_stats = self.load_test(
            "/api/v1/health",
            concurrent_users=20,
            requests_per_user=10
        )
        test_results.append(health_stats)
        self.print_results(health_stats)
        
        # Test 2: Content generation endpoint (light load)
        content_data = {
            "topic": "Python Programming",
            "content_type": "study_guide",
            "educational_level": "intermediate"
        }
        
        content_stats = self.load_test(
            "/api/v1/content/generate",
            concurrent_users=5,
            requests_per_user=2,
            method="POST",
            data=content_data
        )
        test_results.append(content_stats)
        self.print_results(content_stats)
        
        # Test 3: Multiple endpoints (mixed load)
        print("\n🔄 Mixed Load Test (simulating real usage)...")
        mixed_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            # Mix of different endpoints
            for _ in range(20):
                futures.append(executor.submit(self.test_endpoint, "/api/v1/health"))
            for _ in range(10):
                futures.append(executor.submit(self.test_endpoint, "/api/v1/content/types"))
            for _ in range(5):
                futures.append(executor.submit(
                    self.test_endpoint, 
                    "/api/v1/content/generate", 
                    "POST", 
                    content_data
                ))
            
            for future in concurrent.futures.as_completed(futures):
                mixed_results.append(future.result())
        
        # Summary
        self.print_summary(test_results, mixed_results)
        
        return {
            "load_tests": test_results,
            "mixed_test": mixed_results,
            "passed": self.evaluate_performance(test_results)
        }
    
    def print_results(self, stats: Dict):
        """Print formatted test results"""
        print(f"\n📊 Results for {stats['endpoint']}:")
        print(f"   ✅ Success Rate: {stats['success_rate']:.1f}%")
        print(f"   📈 Throughput: {stats['requests_per_second']:.1f} req/s")
        print(f"   ⏱️ Response Times (ms):")
        print(f"      Min: {stats['response_times']['min']:.1f}")
        print(f"      Median: {stats['response_times']['median']:.1f}")
        print(f"      Mean: {stats['response_times']['mean']:.1f}")
        print(f"      P95: {stats['response_times']['p95']:.1f}")
        print(f"      P99: {stats['response_times']['p99']:.1f}")
        print(f"      Max: {stats['response_times']['max']:.1f}")
    
    def print_summary(self, load_tests: List[Dict], mixed_results: List[Dict]):
        """Print test summary"""
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        # Overall statistics
        total_requests = sum(test["total_requests"] for test in load_tests)
        total_success = sum(test["successful"] for test in load_tests)
        
        print(f"\n📌 Total Requests: {total_requests}")
        print(f"📌 Total Successful: {total_success}")
        print(f"📌 Overall Success Rate: {total_success/total_requests*100:.1f}%")
        
        # Performance against targets
        print("\n🎯 Performance vs Targets (Phase 3D):")
        
        health_test = next((t for t in load_tests if "health" in t["endpoint"]), None)
        if health_test:
            health_p95 = health_test["response_times"]["p95"]
            print(f"   Health Endpoint P95: {health_p95:.1f}ms", end="")
            print(" ✅ PASS" if health_p95 < 200 else " ❌ FAIL (target: <200ms)")
        
        content_test = next((t for t in load_tests if "generate" in t["endpoint"]), None)
        if content_test:
            content_p95 = content_test["response_times"]["p95"]
            print(f"   Content Generation P95: {content_p95:.1f}ms", end="")
            print(" ✅ PASS" if content_p95 < 5000 else " ❌ FAIL (target: <5000ms)")
    
    def evaluate_performance(self, test_results: List[Dict]) -> bool:
        """Evaluate if performance meets Phase 3D criteria"""
        # Criteria from Phase 3D:
        # - <200ms response time for basic endpoints
        # - <5000ms for content generation
        # - >95% success rate
        
        for test in test_results:
            if test["success_rate"] < 95:
                return False
            
            if "health" in test["endpoint"] and test["response_times"]["p95"] > 200:
                return False
            
            if "generate" in test["endpoint"] and test["response_times"]["p95"] > 5000:
                return False
        
        return True


def main():
    """Run performance tests"""
    tester = PerformanceTester()
    
    # Check if server is running
    try:
        response = requests.get(f"{tester.base_url}/api/v1/health")
        if response.status_code != 200:
            print("⚠️ Server health check failed. Please start the server:")
            print("   uvicorn src.main:app --reload")
            return False
    except:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("   Please start the server with:")
        print("   uvicorn src.main:app --reload")
        return False
    
    # Run performance tests
    results = tester.run_performance_suite()
    
    # Save results
    with open("performance_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n💾 Results saved to performance_results.json")
    
    if results["passed"]:
        print("\n✅ PERFORMANCE TESTS PASSED - Phase 3D criteria met!")
        return True
    else:
        print("\n❌ PERFORMANCE TESTS FAILED - Does not meet Phase 3D criteria")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)