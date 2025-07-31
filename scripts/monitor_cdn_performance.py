#!/usr/bin/env python3
"""
CDN Performance Monitoring Script
Monitors CDN performance metrics and cache hit rates
"""

import os
import sys
import json
import time
import requests
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

# CDN configuration
CDN_BASE_URL = os.getenv("VITE_CDN_URL", "https://cdn.lafactoria.app")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", "")

# Monitoring configuration
MONITORING_WINDOW_HOURS = 24
SAMPLE_INTERVAL_MINUTES = 5
ALERT_THRESHOLDS = {
    "cache_hit_rate_min": 85,  # Alert if cache hit rate drops below 85%
    "response_time_p95_max": 300,  # Alert if P95 response time exceeds 300ms
    "error_rate_max": 1,  # Alert if error rate exceeds 1%
    "bandwidth_saving_min": 70,  # Alert if bandwidth saving drops below 70%
}


class CDNMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.alerts = []
        
    def collect_cloudflare_analytics(self) -> Dict:
        """Collect analytics from Cloudflare API"""
        if not CLOUDFLARE_API_TOKEN or not CLOUDFLARE_ZONE_ID:
            print("Warning: Cloudflare credentials not configured")
            return {}
        
        # Calculate time window
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=MONITORING_WINDOW_HOURS)
        
        # Format timestamps for API
        start_ts = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_ts = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Cloudflare Analytics API endpoint
        url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/analytics/dashboard"
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        params = {
            "since": start_ts,
            "until": end_ts,
            "continuous": "true"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                return self._process_cloudflare_data(data.get("result", {}))
            else:
                print(f"Cloudflare API error: {data.get('errors', [])}")
                return {}
                
        except Exception as e:
            print(f"Error fetching Cloudflare analytics: {e}")
            return {}
    
    def _process_cloudflare_data(self, data: Dict) -> Dict:
        """Process Cloudflare analytics data"""
        totals = data.get("totals", {})
        
        # Calculate key metrics
        requests_total = totals.get("requests", {}).get("all", 0)
        requests_cached = totals.get("requests", {}).get("cached", 0)
        bytes_total = totals.get("bytes", {}).get("all", 0)
        bytes_cached = totals.get("bytes", {}).get("cached", 0)
        
        cache_hit_rate = (requests_cached / requests_total * 100) if requests_total > 0 else 0
        bandwidth_saving = (bytes_cached / bytes_total * 100) if bytes_total > 0 else 0
        
        # Response time percentiles (if available)
        percentiles = totals.get("percentiles", {})
        
        return {
            "cache_hit_rate": round(cache_hit_rate, 2),
            "bandwidth_saving": round(bandwidth_saving, 2),
            "total_requests": requests_total,
            "cached_requests": requests_cached,
            "total_bytes": bytes_total,
            "cached_bytes": bytes_cached,
            "response_time_p50": percentiles.get("originResponseTimeMs", {}).get("p50", 0),
            "response_time_p95": percentiles.get("originResponseTimeMs", {}).get("p95", 0),
            "response_time_p99": percentiles.get("originResponseTimeMs", {}).get("p99", 0),
        }
    
    def test_endpoint_performance(self, endpoint: str) -> Dict:
        """Test performance of a specific endpoint"""
        url = f"{CDN_BASE_URL}{endpoint}"
        response_times = []
        errors = 0
        
        # Multiple samples for accuracy
        for _ in range(5):
            try:
                start = time.time()
                response = requests.get(url, timeout=10)
                elapsed = (time.time() - start) * 1000  # Convert to ms
                
                response_times.append(elapsed)
                
                if response.status_code >= 400:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                print(f"Error testing {endpoint}: {e}")
            
            time.sleep(0.5)  # Small delay between requests
        
        if response_times:
            return {
                "endpoint": endpoint,
                "avg_response_time": statistics.mean(response_times),
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "error_rate": (errors / 5) * 100,
                "samples": len(response_times),
            }
        else:
            return {
                "endpoint": endpoint,
                "error_rate": 100,
                "error": "All requests failed"
            }
    
    def check_cache_headers(self, endpoint: str) -> Dict:
        """Check cache headers for an endpoint"""
        url = f"{CDN_BASE_URL}{endpoint}"
        
        try:
            response = requests.head(url, timeout=5)
            
            return {
                "endpoint": endpoint,
                "cache_control": response.headers.get("Cache-Control", ""),
                "cf_cache_status": response.headers.get("CF-Cache-Status", ""),
                "age": response.headers.get("Age", ""),
                "expires": response.headers.get("Expires", ""),
                "etag": bool(response.headers.get("ETag")),
                "last_modified": bool(response.headers.get("Last-Modified")),
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "error": str(e)
            }
    
    def generate_alerts(self, metrics: Dict) -> List[Dict]:
        """Generate alerts based on thresholds"""
        alerts = []
        timestamp = datetime.utcnow().isoformat()
        
        # Check cache hit rate
        cache_hit_rate = metrics.get("cloudflare", {}).get("cache_hit_rate", 100)
        if cache_hit_rate < ALERT_THRESHOLDS["cache_hit_rate_min"]:
            alerts.append({
                "level": "WARNING",
                "metric": "cache_hit_rate",
                "value": cache_hit_rate,
                "threshold": ALERT_THRESHOLDS["cache_hit_rate_min"],
                "message": f"Cache hit rate ({cache_hit_rate}%) is below threshold",
                "timestamp": timestamp
            })
        
        # Check response times
        for endpoint_data in metrics.get("endpoints", []):
            p95_time = endpoint_data.get("p95_response_time", 0)
            if p95_time > ALERT_THRESHOLDS["response_time_p95_max"]:
                alerts.append({
                    "level": "WARNING",
                    "metric": "response_time_p95",
                    "endpoint": endpoint_data["endpoint"],
                    "value": p95_time,
                    "threshold": ALERT_THRESHOLDS["response_time_p95_max"],
                    "message": f"P95 response time ({p95_time}ms) exceeds threshold for {endpoint_data['endpoint']}",
                    "timestamp": timestamp
                })
        
        # Check error rates
        for endpoint_data in metrics.get("endpoints", []):
            error_rate = endpoint_data.get("error_rate", 0)
            if error_rate > ALERT_THRESHOLDS["error_rate_max"]:
                alerts.append({
                    "level": "ERROR",
                    "metric": "error_rate",
                    "endpoint": endpoint_data["endpoint"],
                    "value": error_rate,
                    "threshold": ALERT_THRESHOLDS["error_rate_max"],
                    "message": f"Error rate ({error_rate}%) exceeds threshold for {endpoint_data['endpoint']}",
                    "timestamp": timestamp
                })
        
        # Check bandwidth savings
        bandwidth_saving = metrics.get("cloudflare", {}).get("bandwidth_saving", 100)
        if bandwidth_saving < ALERT_THRESHOLDS["bandwidth_saving_min"]:
            alerts.append({
                "level": "INFO",
                "metric": "bandwidth_saving",
                "value": bandwidth_saving,
                "threshold": ALERT_THRESHOLDS["bandwidth_saving_min"],
                "message": f"Bandwidth saving ({bandwidth_saving}%) is below optimal",
                "timestamp": timestamp
            })
        
        return alerts
    
    def run_monitoring_cycle(self) -> Dict:
        """Run a complete monitoring cycle"""
        print(f"\n=== CDN Monitoring Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cloudflare": {},
            "endpoints": [],
            "cache_headers": [],
            "alerts": []
        }
        
        # 1. Collect Cloudflare analytics
        print("\nCollecting Cloudflare analytics...")
        cf_data = self.collect_cloudflare_analytics()
        if cf_data:
            metrics["cloudflare"] = cf_data
            print(f"  Cache hit rate: {cf_data.get('cache_hit_rate', 0)}%")
            print(f"  Bandwidth saving: {cf_data.get('bandwidth_saving', 0)}%")
        
        # 2. Test critical endpoints
        print("\nTesting endpoint performance...")
        critical_endpoints = [
            "/assets/js/vendor.js",
            "/assets/js/index.js",
            "/assets/css/index.css",
            "/index.html",
        ]
        
        for endpoint in critical_endpoints:
            perf_data = self.test_endpoint_performance(endpoint)
            metrics["endpoints"].append(perf_data)
            print(f"  {endpoint}: {perf_data.get('avg_response_time', 0):.1f}ms avg, "
                  f"{perf_data.get('error_rate', 0)}% errors")
        
        # 3. Check cache headers
        print("\nChecking cache headers...")
        for endpoint in critical_endpoints[:2]:  # Check first 2 endpoints
            header_data = self.check_cache_headers(endpoint)
            metrics["cache_headers"].append(header_data)
            if not header_data.get("error"):
                print(f"  {endpoint}: {header_data.get('cf_cache_status', 'UNKNOWN')}")
        
        # 4. Generate alerts
        alerts = self.generate_alerts(metrics)
        metrics["alerts"] = alerts
        
        if alerts:
            print(f"\n⚠️  {len(alerts)} alerts generated:")
            for alert in alerts:
                print(f"  [{alert['level']}] {alert['message']}")
        else:
            print("\n✓ No alerts - all metrics within thresholds")
        
        # 5. Save metrics
        self.save_metrics(metrics)
        
        return metrics
    
    def save_metrics(self, metrics: Dict):
        """Save metrics to file"""
        filename = f"cdn_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"\nMetrics saved to {filename}")
    
    def generate_report(self) -> str:
        """Generate a performance report"""
        report = []
        report.append("=== CDN Performance Report ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Monitoring window: {MONITORING_WINDOW_HOURS} hours")
        report.append("")
        
        # Run monitoring cycle
        metrics = self.run_monitoring_cycle()
        
        # Summary section
        report.append("SUMMARY")
        report.append("-" * 50)
        
        cf_data = metrics.get("cloudflare", {})
        if cf_data:
            report.append(f"Cache Hit Rate: {cf_data.get('cache_hit_rate', 0)}%")
            report.append(f"Bandwidth Saving: {cf_data.get('bandwidth_saving', 0)}%")
            report.append(f"Total Requests: {cf_data.get('total_requests', 0):,}")
            report.append(f"Cached Requests: {cf_data.get('cached_requests', 0):,}")
        
        # Performance section
        report.append("")
        report.append("ENDPOINT PERFORMANCE")
        report.append("-" * 50)
        
        for endpoint in metrics.get("endpoints", []):
            if not endpoint.get("error"):
                report.append(f"\n{endpoint['endpoint']}:")
                report.append(f"  Average Response: {endpoint.get('avg_response_time', 0):.1f}ms")
                report.append(f"  P95 Response: {endpoint.get('p95_response_time', 0):.1f}ms")
                report.append(f"  Error Rate: {endpoint.get('error_rate', 0)}%")
        
        # Alerts section
        alerts = metrics.get("alerts", [])
        if alerts:
            report.append("")
            report.append("ALERTS")
            report.append("-" * 50)
            for alert in alerts:
                report.append(f"[{alert['level']}] {alert['message']}")
        
        # Recommendations
        report.append("")
        report.append("RECOMMENDATIONS")
        report.append("-" * 50)
        
        if cf_data.get("cache_hit_rate", 100) < 90:
            report.append("• Review cache headers and TTL settings")
            report.append("• Check for cache-busting query parameters")
        
        if any(e.get("error_rate", 0) > 0 for e in metrics.get("endpoints", [])):
            report.append("• Investigate endpoint errors")
            report.append("• Check origin server health")
        
        bandwidth_saving = cf_data.get("bandwidth_saving", 100)
        if bandwidth_saving < 80:
            report.append("• Consider increasing cache TTLs")
            report.append("• Enable more aggressive caching")
        
        return "\n".join(report)


def main():
    """Main monitoring function"""
    monitor = CDNMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Continuous monitoring mode
        print("Starting continuous CDN monitoring...")
        print(f"Sampling every {SAMPLE_INTERVAL_MINUTES} minutes")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                monitor.run_monitoring_cycle()
                time.sleep(SAMPLE_INTERVAL_MINUTES * 60)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
    else:
        # Single report mode
        report = monitor.generate_report()
        print("\n" + report)
        
        # Save report
        with open("cdn_performance_report.txt", "w") as f:
            f.write(report)
        print("\nReport saved to cdn_performance_report.txt")


if __name__ == "__main__":
    main()