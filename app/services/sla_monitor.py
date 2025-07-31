"""
SLA Monitoring Service

Tracks SLIs, calculates SLO compliance, and manages error budgets.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import yaml
import json
from pathlib import Path

from app.core.cache import get_cache_backend
from app.core.metrics import metrics

# Get cache instance
cache = get_cache_backend()

logger = logging.getLogger(__name__)


@dataclass
class SLI:
    """Service Level Indicator"""
    name: str
    value: float
    target: float
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_compliant(self) -> bool:
        """Check if SLI meets target"""
        return self.value >= self.target


@dataclass
class SLO:
    """Service Level Objective"""
    name: str
    description: str
    target: float
    window: str
    indicators: List[SLI] = field(default_factory=list)
    
    @property
    def compliance_rate(self) -> float:
        """Calculate compliance rate"""
        if not self.indicators:
            return 100.0
        compliant = sum(1 for sli in self.indicators if sli.is_compliant)
        return (compliant / len(self.indicators)) * 100
    
    @property
    def is_met(self) -> bool:
        """Check if SLO is being met"""
        return self.compliance_rate >= self.target


@dataclass
class ErrorBudget:
    """Error budget tracking"""
    slo_name: str
    total_minutes: float
    consumed_minutes: float
    window: str
    
    @property
    def remaining_minutes(self) -> float:
        """Calculate remaining error budget"""
        return max(0, self.total_minutes - self.consumed_minutes)
    
    @property
    def consumption_rate(self) -> float:
        """Calculate consumption rate as percentage"""
        if self.total_minutes == 0:
            return 0
        return (self.consumed_minutes / self.total_minutes) * 100
    
    @property
    def burn_rate(self) -> float:
        """Calculate burn rate (1x = normal)"""
        # Simplified burn rate calculation
        expected_consumption = 1.0  # Expected consumption per time unit
        actual_consumption = self.consumption_rate / 100
        return actual_consumption / expected_consumption if expected_consumption > 0 else 0


class SLAMonitor:
    """Service for monitoring SLAs and SLOs"""
    
    def __init__(self):
        self.slos: Dict[str, SLO] = {}
        self.error_budgets: Dict[str, ErrorBudget] = {}
        self._load_slo_config()
        self._monitoring_task: Optional[asyncio.Task] = None
    
    def _load_slo_config(self):
        """Load SLO configuration from YAML"""
        config_path = Path("monitoring/slos.yaml")
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    for name, slo_config in config.get("slos", {}).items():
                        self.slos[name] = SLO(
                            name=name,
                            description=slo_config.get("description", ""),
                            target=slo_config.get("target", 99.9),
                            window=slo_config.get("window", "30d")
                        )
                        # Initialize error budget
                        if "error_budget" in slo_config:
                            self.error_budgets[name] = ErrorBudget(
                                slo_name=name,
                                total_minutes=slo_config["error_budget"].get("monthly_minutes", 43.2),
                                consumed_minutes=0,
                                window="30d"
                            )
            except Exception as e:
                logger.error(f"Failed to load SLO config: {e}")
    
    async def start_monitoring(self):
        """Start continuous SLA monitoring"""
        if not self._monitoring_task:
            self._monitoring_task = asyncio.create_task(self._monitor_loop())
            logger.info("SLA monitoring started")
    
    async def stop_monitoring(self):
        """Stop SLA monitoring"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
            logger.info("SLA monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self._collect_metrics()
                await asyncio.sleep(60)  # Collect metrics every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_metrics(self):
        """Collect all SLI metrics"""
        # API Availability
        await self._collect_availability_metrics()
        
        # Response Time
        await self._collect_latency_metrics()
        
        # Error Rate
        await self._collect_error_metrics()
        
        # Content Generation
        await self._collect_content_metrics()
        
        # Update error budgets
        await self._update_error_budgets()
    
    async def _collect_availability_metrics(self):
        """Collect availability SLIs"""
        try:
            # Get health check success rate from cache/metrics
            success_rate = await cache.get("health_check_success_rate") or 99.9
            
            sli = SLI(
                name="health_check_success",
                value=float(success_rate),
                target=99.9,
                unit="%"
            )
            
            if "api_availability" in self.slos:
                self.slos["api_availability"].indicators.append(sli)
                # Keep only recent indicators (last 1000)
                if len(self.slos["api_availability"].indicators) > 1000:
                    self.slos["api_availability"].indicators = self.slos["api_availability"].indicators[-1000:]
            
            # Record metric
            metrics.gauge("sla.availability.current", success_rate)
            
        except Exception as e:
            logger.error(f"Error collecting availability metrics: {e}")
    
    async def _collect_latency_metrics(self):
        """Collect latency SLIs"""
        try:
            # Get latency metrics from cache/metrics
            p95_latency = await cache.get("api_latency_p95") or 250
            p99_latency = await cache.get("api_latency_p99") or 500
            
            if "api_latency" in self.slos:
                self.slos["api_latency"].indicators.extend([
                    SLI(name="p95_latency", value=float(p95_latency), target=500, unit="ms"),
                    SLI(name="p99_latency", value=float(p99_latency), target=1000, unit="ms")
                ])
            
            # Record metrics
            metrics.gauge("sla.latency.p95", p95_latency)
            metrics.gauge("sla.latency.p99", p99_latency)
            
        except Exception as e:
            logger.error(f"Error collecting latency metrics: {e}")
    
    async def _collect_error_metrics(self):
        """Collect error rate SLIs"""
        try:
            # Get error rate from cache/metrics
            error_rate = await cache.get("api_error_rate") or 0.5
            
            sli = SLI(
                name="5xx_errors",
                value=100 - float(error_rate),  # Convert to success rate
                target=99.0,
                unit="%"
            )
            
            if "error_rate" in self.slos:
                self.slos["error_rate"].indicators.append(sli)
            
            # Record metric
            metrics.gauge("sla.error_rate.current", error_rate)
            
        except Exception as e:
            logger.error(f"Error collecting error metrics: {e}")
    
    async def _collect_content_metrics(self):
        """Collect content generation SLIs"""
        try:
            # Get content generation metrics
            success_rate = await cache.get("content_generation_success_rate") or 98.5
            generation_time = await cache.get("content_generation_p95") or 3000
            
            if "content_generation" in self.slos:
                self.slos["content_generation"].indicators.extend([
                    SLI(name="generation_success_rate", value=float(success_rate), target=98.0, unit="%"),
                    SLI(name="generation_latency_p95", value=float(generation_time), target=5000, unit="ms")
                ])
            
            # Record metrics
            metrics.gauge("sla.content.success_rate", success_rate)
            metrics.gauge("sla.content.latency_p95", generation_time)
            
        except Exception as e:
            logger.error(f"Error collecting content metrics: {e}")
    
    async def _update_error_budgets(self):
        """Update error budget consumption"""
        for slo_name, slo in self.slos.items():
            if slo_name in self.error_budgets:
                budget = self.error_budgets[slo_name]
                
                # Calculate downtime based on compliance
                if not slo.is_met:
                    # Each minute not meeting SLO consumes budget
                    budget.consumed_minutes += 1
                
                # Record metrics
                metrics.gauge(f"sla.error_budget.{slo_name}.remaining", budget.remaining_minutes)
                metrics.gauge(f"sla.error_budget.{slo_name}.consumption_rate", budget.consumption_rate)
                metrics.gauge(f"sla.error_budget.{slo_name}.burn_rate", budget.burn_rate)
                
                # Check for alerts
                await self._check_burn_rate_alerts(slo_name, budget)
    
    async def _check_burn_rate_alerts(self, slo_name: str, budget: ErrorBudget):
        """Check error budget burn rate and trigger alerts"""
        if budget.burn_rate >= 10:
            logger.critical(f"Critical burn rate for {slo_name}: {budget.burn_rate}x")
            await self._trigger_alert(slo_name, "critical", f"Burn rate: {budget.burn_rate}x")
        elif budget.burn_rate >= 5:
            logger.error(f"High burn rate for {slo_name}: {budget.burn_rate}x")
            await self._trigger_alert(slo_name, "error", f"Burn rate: {budget.burn_rate}x")
        elif budget.burn_rate >= 2:
            logger.warning(f"Elevated burn rate for {slo_name}: {budget.burn_rate}x")
            await self._trigger_alert(slo_name, "warning", f"Burn rate: {budget.burn_rate}x")
    
    async def _trigger_alert(self, slo_name: str, severity: str, message: str):
        """Trigger alert for SLA violation"""
        alert_data = {
            "slo": slo_name,
            "severity": severity,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "error_budget": self.error_budgets.get(slo_name)
        }
        
        # Store alert in cache
        await cache.set(f"sla_alert:{slo_name}:{severity}", json.dumps(alert_data, default=str), expire=3600)
        
        # Log alert
        logger.info(f"SLA Alert triggered: {slo_name} - {severity} - {message}")
    
    async def get_sla_status(self) -> Dict[str, Any]:
        """Get current SLA status"""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "slos": {},
            "error_budgets": {},
            "alerts": []
        }
        
        # SLO compliance
        for name, slo in self.slos.items():
            status["slos"][name] = {
                "name": slo.name,
                "description": slo.description,
                "target": slo.target,
                "compliance_rate": slo.compliance_rate,
                "is_met": slo.is_met,
                "indicator_count": len(slo.indicators)
            }
        
        # Error budgets
        for name, budget in self.error_budgets.items():
            status["error_budgets"][name] = {
                "total_minutes": budget.total_minutes,
                "consumed_minutes": budget.consumed_minutes,
                "remaining_minutes": budget.remaining_minutes,
                "consumption_rate": budget.consumption_rate,
                "burn_rate": budget.burn_rate
            }
        
        # Active alerts
        alert_keys = await cache.keys("sla_alert:*")
        for key in alert_keys:
            alert_data = await cache.get(key)
            if alert_data:
                status["alerts"].append(json.loads(alert_data))
        
        return status
    
    async def get_sli_history(self, slo_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get SLI history for a specific SLO"""
        if slo_name not in self.slos:
            return []
        
        slo = self.slos[slo_name]
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        history = []
        for sli in slo.indicators:
            if sli.timestamp >= cutoff:
                history.append({
                    "name": sli.name,
                    "value": sli.value,
                    "target": sli.target,
                    "unit": sli.unit,
                    "timestamp": sli.timestamp.isoformat(),
                    "is_compliant": sli.is_compliant
                })
        
        return history
    
    async def generate_sla_report(self, period: str = "weekly") -> Dict[str, Any]:
        """Generate SLA compliance report"""
        report = {
            "period": period,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "overall_compliance": 0,
                "slos_met": 0,
                "slos_total": len(self.slos),
                "critical_violations": 0
            },
            "details": {},
            "recommendations": []
        }
        
        # Calculate compliance for each SLO
        total_compliance = 0
        for name, slo in self.slos.items():
            compliance = slo.compliance_rate
            total_compliance += compliance
            
            if slo.is_met:
                report["summary"]["slos_met"] += 1
            elif compliance < 95:
                report["summary"]["critical_violations"] += 1
            
            report["details"][name] = {
                "compliance_rate": compliance,
                "is_met": slo.is_met,
                "target": slo.target,
                "indicator_performance": {}
            }
            
            # Analyze indicators
            if slo.indicators:
                for indicator_name in set(sli.name for sli in slo.indicators):
                    indicators = [sli for sli in slo.indicators if sli.name == indicator_name]
                    if indicators:
                        avg_value = sum(sli.value for sli in indicators) / len(indicators)
                        report["details"][name]["indicator_performance"][indicator_name] = {
                            "average": avg_value,
                            "min": min(sli.value for sli in indicators),
                            "max": max(sli.value for sli in indicators),
                            "compliance": sum(1 for sli in indicators if sli.is_compliant) / len(indicators) * 100
                        }
        
        # Overall compliance
        if self.slos:
            report["summary"]["overall_compliance"] = total_compliance / len(self.slos)
        
        # Generate recommendations
        for name, slo in self.slos.items():
            if not slo.is_met:
                if slo.compliance_rate < 90:
                    report["recommendations"].append(
                        f"Critical: {name} is significantly below target. Immediate action required."
                    )
                else:
                    report["recommendations"].append(
                        f"Warning: {name} is below target. Review and optimize."
                    )
        
        return report


# Global instance
sla_monitor = SLAMonitor()