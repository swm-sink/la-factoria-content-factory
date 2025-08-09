#!/usr/bin/env python3
"""
Health Monitoring Validation Script for La Factoria
===================================================

Validates all health check and monitoring endpoints for production readiness.
Tests health checks, metrics collection, alerting thresholds, and Railway integration.

Requirements:
- Running application (locally or in Railway)
- Database connectivity
- AI provider configuration (optional)
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import requests
from urllib.parse import urljoin

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthMonitoringValidator:
    """Validate health monitoring implementation for La Factoria"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """Initialize validator with API endpoint"""
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("LA_FACTORIA_API_KEY", "test-api-key")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        self.test_results = {
            "basic_health": False,
            "detailed_health": False,
            "readiness_probe": False,
            "liveness_probe": False,
            "metrics_endpoint": False,
            "educational_metrics": False,
            "ai_provider_health": False,
            "content_service_health": False,
            "system_resources": False,
            "database_health": False,
            "response_times": {},
            "alerting_thresholds": False,
            "railway_compatibility": False
        }
        
    def test_basic_health(self) -> bool:
        """Test basic health check endpoint"""
        try:
            start = time.time()
            response = requests.get(
                urljoin(self.base_url, "/api/v1/health"),
                timeout=5
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate required fields
                required_fields = ["status", "timestamp", "version"]
                if all(field in data for field in required_fields):
                    logger.info(f"✅ Basic health check passed - Status: {data['status']}")
                    self.test_results["basic_health"] = True
                    self.test_results["response_times"]["basic_health"] = round(response_time, 2)
                    return True
                else:
                    logger.error(f"❌ Basic health missing fields: {data}")
            else:
                logger.error(f"❌ Basic health returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Basic health check failed: {e}")
            
        self.test_results["basic_health"] = False
        return False
    
    def test_detailed_health(self) -> bool:
        """Test detailed health check with system metrics"""
        try:
            start = time.time()
            response = requests.get(
                urljoin(self.base_url, "/api/v1/health/detailed"),
                timeout=10
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code in [200, 503]:  # 503 if degraded
                data = response.json()
                
                # Validate detailed health structure
                required_fields = ["status", "timestamp", "version", "system_metrics", "services"]
                has_fields = all(field in data for field in required_fields)
                
                if has_fields:
                    # Check system metrics
                    if "system_metrics" in data:
                        metrics = data["system_metrics"]
                        logger.info(f"  CPU Usage: {metrics.get('cpu_usage_percent', 'N/A')}%")
                        logger.info(f"  Memory Usage: {metrics.get('memory_usage_percent', 'N/A')}%")
                        logger.info(f"  Disk Usage: {metrics.get('disk_usage_percent', 'N/A')}%")
                        self.test_results["system_resources"] = True
                    
                    # Check service health
                    if "services" in data:
                        services = data["services"]
                        if "database" in services:
                            self.test_results["database_health"] = services["database"].get("status") == "healthy"
                        if "ai_providers" in services:
                            self.test_results["ai_provider_health"] = "healthy" in str(services["ai_providers"])
                    
                    logger.info(f"✅ Detailed health check passed - Status: {data['status']}")
                    self.test_results["detailed_health"] = True
                    self.test_results["response_times"]["detailed_health"] = round(response_time, 2)
                    return True
                else:
                    logger.error(f"❌ Detailed health missing fields")
            else:
                logger.error(f"❌ Detailed health returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Detailed health check failed: {e}")
            
        self.test_results["detailed_health"] = False
        return False
    
    def test_readiness_probe(self) -> bool:
        """Test Kubernetes/Railway readiness probe"""
        try:
            start = time.time()
            response = requests.get(
                urljoin(self.base_url, "/api/v1/ready"),
                timeout=5
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code in [200, 503]:
                data = response.json()
                is_ready = data.get("status") == "ready"
                
                if is_ready:
                    logger.info("✅ Readiness probe: Service is ready")
                else:
                    logger.warning(f"⚠️ Readiness probe: Service not ready - {data}")
                    
                self.test_results["readiness_probe"] = is_ready
                self.test_results["response_times"]["readiness"] = round(response_time, 2)
                return is_ready
            else:
                logger.error(f"❌ Readiness probe returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Readiness probe failed: {e}")
            
        self.test_results["readiness_probe"] = False
        return False
    
    def test_liveness_probe(self) -> bool:
        """Test Kubernetes/Railway liveness probe"""
        try:
            start = time.time()
            response = requests.get(
                urljoin(self.base_url, "/api/v1/live"),
                timeout=5
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "alive":
                    logger.info("✅ Liveness probe: Service is alive")
                    self.test_results["liveness_probe"] = True
                    self.test_results["response_times"]["liveness"] = round(response_time, 2)
                    return True
            else:
                logger.error(f"❌ Liveness probe returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Liveness probe failed: {e}")
            
        self.test_results["liveness_probe"] = False
        return False
    
    def test_metrics_endpoints(self) -> bool:
        """Test metrics collection endpoints"""
        try:
            # Test general metrics
            start = time.time()
            response = requests.get(
                urljoin(self.base_url, "/api/v1/metrics"),
                timeout=10
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                if "system" in data and "application" in data:
                    logger.info("✅ General metrics endpoint working")
                    self.test_results["metrics_endpoint"] = True
                    self.test_results["response_times"]["metrics"] = round(response_time, 2)
                    
                    # Display some metrics
                    if "application" in data:
                        app_metrics = data["application"]
                        logger.info(f"  Total Content: {app_metrics.get('total_content_generated', 0)}")
                        logger.info(f"  24h Content: {app_metrics.get('content_last_24h', 0)}")
                        logger.info(f"  Avg Quality: {app_metrics.get('average_quality_24h', 0)}")
            else:
                logger.error(f"❌ Metrics endpoint returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Metrics endpoint failed: {e}")
            self.test_results["metrics_endpoint"] = False
            
        # Test educational metrics
        try:
            response = requests.get(
                urljoin(self.base_url, "/api/v1/metrics/educational"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "quality_thresholds" in data:
                    thresholds = data["quality_thresholds"]
                    logger.info("✅ Educational metrics endpoint working")
                    logger.info(f"  Quality Thresholds - Overall: {thresholds.get('overall', 'N/A')}")
                    logger.info(f"  Educational: {thresholds.get('educational', 'N/A')}")
                    logger.info(f"  Factual: {thresholds.get('factual', 'N/A')}")
                    self.test_results["educational_metrics"] = True
            else:
                logger.warning(f"⚠️ Educational metrics returned {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Educational metrics failed: {e}")
            self.test_results["educational_metrics"] = False
            
        return self.test_results["metrics_endpoint"]
    
    def test_ai_provider_health(self) -> bool:
        """Test AI provider health check"""
        try:
            response = requests.get(
                urljoin(self.base_url, "/api/v1/health/ai-providers"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "providers" in data:
                    providers = data.get("providers", {})
                    overall = data.get("overall_status", "unknown")
                    
                    logger.info(f"✅ AI Provider health check - Status: {overall}")
                    for provider, status in providers.items():
                        logger.info(f"  {provider}: {status}")
                        
                    self.test_results["ai_provider_health"] = overall == "healthy"
                    return self.test_results["ai_provider_health"]
            else:
                logger.warning(f"⚠️ AI provider health returned {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ AI provider health check failed: {e}")
            
        self.test_results["ai_provider_health"] = False
        return False
    
    def test_content_service_health(self) -> bool:
        """Test content service health check"""
        try:
            response = requests.get(
                urljoin(self.base_url, "/api/v1/health/content-service"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("overall_status", "unknown")
                
                logger.info(f"✅ Content service health - Status: {status}")
                self.test_results["content_service_health"] = status == "healthy"
                return self.test_results["content_service_health"]
            else:
                logger.warning(f"⚠️ Content service health returned {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Content service health check failed: {e}")
            
        self.test_results["content_service_health"] = False
        return False
    
    def test_alerting_thresholds(self) -> bool:
        """Test that alerting thresholds are properly configured"""
        try:
            # Check if monitoring endpoints report threshold violations
            response = requests.get(
                urljoin(self.base_url, "/api/v1/health/detailed"),
                timeout=10
            )
            
            if response.status_code in [200, 503]:
                data = response.json()
                
                # Check if critical issues are detected
                if "critical_issues" in data or "failed_checks" in data:
                    logger.info("✅ Alerting thresholds are configured")
                    logger.info(f"  Critical Issues: {data.get('critical_issues', [])}")
                    logger.info(f"  Failed Checks: {data.get('failed_checks', [])}")
                    self.test_results["alerting_thresholds"] = True
                    return True
                elif data.get("status") == "healthy":
                    logger.info("✅ No threshold violations detected (healthy system)")
                    self.test_results["alerting_thresholds"] = True
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Alerting threshold test failed: {e}")
            
        self.test_results["alerting_thresholds"] = False
        return False
    
    def test_railway_compatibility(self) -> bool:
        """Test Railway platform compatibility"""
        railway_compatible = True
        
        # Check health endpoint format
        if self.test_results["basic_health"]:
            logger.info("✅ Railway health endpoint format compatible")
        else:
            logger.warning("⚠️ Railway health endpoint may not be compatible")
            railway_compatible = False
            
        # Check readiness/liveness probes
        if self.test_results["readiness_probe"] and self.test_results["liveness_probe"]:
            logger.info("✅ Railway probe endpoints compatible")
        else:
            logger.warning("⚠️ Railway probe endpoints may not be compatible")
            railway_compatible = False
            
        # Check response times (Railway expects <30s)
        slow_endpoints = [
            endpoint for endpoint, time_ms in self.test_results["response_times"].items()
            if time_ms > 30000
        ]
        
        if not slow_endpoints:
            logger.info("✅ All endpoints respond within Railway timeout limits")
        else:
            logger.warning(f"⚠️ Slow endpoints detected: {slow_endpoints}")
            railway_compatible = False
            
        self.test_results["railway_compatibility"] = railway_compatible
        return railway_compatible
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("=" * 60)
        report.append("Health Monitoring Validation Report")
        report.append("=" * 60)
        report.append(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        report.append(f"API Base URL: {self.base_url}")
        report.append("")
        
        # Test results
        report.append("Health Check Endpoints:")
        report.append("-" * 40)
        
        status_symbols = {True: "✅", False: "❌", None: "⏭️"}
        
        # Core health checks
        report.append(f"{status_symbols[self.test_results['basic_health']]} Basic Health Check")
        report.append(f"{status_symbols[self.test_results['detailed_health']]} Detailed Health Check")
        report.append(f"{status_symbols[self.test_results['readiness_probe']]} Readiness Probe")
        report.append(f"{status_symbols[self.test_results['liveness_probe']]} Liveness Probe")
        
        report.append("")
        report.append("Monitoring Features:")
        report.append("-" * 40)
        
        # Monitoring features
        report.append(f"{status_symbols[self.test_results['metrics_endpoint']]} Metrics Collection")
        report.append(f"{status_symbols[self.test_results['educational_metrics']]} Educational Metrics")
        report.append(f"{status_symbols[self.test_results['system_resources']]} System Resource Monitoring")
        report.append(f"{status_symbols[self.test_results['database_health']]} Database Health Monitoring")
        report.append(f"{status_symbols[self.test_results['ai_provider_health']]} AI Provider Health")
        report.append(f"{status_symbols[self.test_results['content_service_health']]} Content Service Health")
        report.append(f"{status_symbols[self.test_results['alerting_thresholds']]} Alerting Thresholds")
        
        report.append("")
        report.append("Performance Metrics:")
        report.append("-" * 40)
        
        # Response times
        for endpoint, time_ms in self.test_results["response_times"].items():
            status = "✅" if time_ms < 1000 else "⚠️" if time_ms < 5000 else "❌"
            report.append(f"{status} {endpoint}: {time_ms}ms")
        
        report.append("")
        report.append("Platform Compatibility:")
        report.append("-" * 40)
        
        report.append(f"{status_symbols[self.test_results['railway_compatibility']]} Railway Platform Compatible")
        
        # Summary
        report.append("")
        report.append("Summary:")
        report.append("-" * 40)
        
        total_tests = len([v for v in self.test_results.values() if isinstance(v, bool)])
        passed_tests = len([v for v in self.test_results.values() if v is True])
        
        report.append(f"Tests Passed: {passed_tests}/{total_tests}")
        report.append(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        # Railway deployment readiness
        report.append("")
        report.append("Railway Deployment Readiness:")
        report.append("-" * 40)
        
        critical_for_railway = [
            self.test_results["basic_health"],
            self.test_results["readiness_probe"],
            self.test_results["liveness_probe"]
        ]
        
        if all(critical_for_railway):
            report.append("✅ Ready for Railway deployment")
        else:
            report.append("❌ Not ready for Railway deployment")
            report.append("   Critical endpoints must be functional:")
            if not self.test_results["basic_health"]:
                report.append("   - Fix basic health check endpoint")
            if not self.test_results["readiness_probe"]:
                report.append("   - Fix readiness probe endpoint")
            if not self.test_results["liveness_probe"]:
                report.append("   - Fix liveness probe endpoint")
        
        # Recommendations
        report.append("")
        report.append("Recommendations:")
        report.append("-" * 40)
        
        if not self.test_results["database_health"]:
            report.append("- Ensure database is running and accessible")
        
        if not self.test_results["ai_provider_health"]:
            report.append("- Configure at least one AI provider")
        
        if self.test_results["response_times"]:
            slow = [e for e, t in self.test_results["response_times"].items() if t > 5000]
            if slow:
                report.append(f"- Optimize slow endpoints: {', '.join(slow)}")
        
        if not self.test_results["alerting_thresholds"]:
            report.append("- Configure alerting thresholds for monitoring")
        
        return "\n".join(report)
    
    async def run_all_tests(self):
        """Run all health monitoring validation tests"""
        logger.info("Starting Health Monitoring Validation...")
        logger.info(f"Testing API at: {self.base_url}")
        logger.info("")
        
        # Run tests in sequence
        tests = [
            ("Basic Health Check", self.test_basic_health),
            ("Detailed Health Check", self.test_detailed_health),
            ("Readiness Probe", self.test_readiness_probe),
            ("Liveness Probe", self.test_liveness_probe),
            ("Metrics Endpoints", self.test_metrics_endpoints),
            ("AI Provider Health", self.test_ai_provider_health),
            ("Content Service Health", self.test_content_service_health),
            ("Alerting Thresholds", self.test_alerting_thresholds),
            ("Railway Compatibility", self.test_railway_compatibility),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\nTesting: {test_name}")
            try:
                test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
        
        # Generate and save report
        report = self.generate_report()
        print("\n" + report)
        
        # Save report to file
        report_file = Path(__file__).parent.parent / "HEALTH_MONITORING_VALIDATION_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        logger.info(f"\nReport saved to: {report_file}")
        
        # Return overall success
        critical_tests = [
            self.test_results["basic_health"],
            self.test_results["readiness_probe"],
            self.test_results["liveness_probe"]
        ]
        
        return all(critical_tests)


def main():
    """Main entry point"""
    # Check if API is running
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    logger.info("Checking if API is accessible...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code != 200:
            logger.warning("API may not be fully functional, but continuing with tests...")
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to API at {base_url}")
        logger.info("Please ensure the API is running:")
        logger.info("  python -m uvicorn src.main:app --reload")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error checking API: {e}")
        sys.exit(1)
    
    # Create validator
    validator = HealthMonitoringValidator(base_url)
    
    # Run tests
    success = asyncio.run(validator.run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()