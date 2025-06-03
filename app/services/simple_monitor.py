"""
Simple Monitor - Lightweight monitoring and metrics tracking
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from prometheus_client import Counter, Gauge, Histogram

# Simple Prometheus metrics
OPERATION_COUNTER = Counter(
    "content_generation_operations_total",
    "Total content generation operations",
    ["operation", "status"],
)

OPERATION_DURATION = Histogram(
    "content_generation_duration_seconds",
    "Time spent on content generation",
    ["operation"],
)

CACHE_HIT_COUNTER = Counter("content_generation_cache_hits_total", "Total cache hits")

QUALITY_GAUGE = Gauge(
    "content_generation_quality_score", "Latest quality score", ["job_id"]
)

TOKEN_COUNTER = Counter(
    "content_generation_tokens_total",
    "Total tokens used",
    ["token_type"],  # input or output
)


@dataclass
class OperationTracker:
    """Track a single operation"""

    operation_name: str
    job_id: str
    monitor: "SimpleMonitor" = field(repr=False)
    start_time: float = field(default_factory=time.time)

    def record_success(self, duration: float, token_usage: Dict[str, int]) -> None:
        """Record successful operation"""
        OPERATION_COUNTER.labels(operation=self.operation_name, status="success").inc()

        OPERATION_DURATION.labels(operation=self.operation_name).observe(duration)

        # Record token usage
        if token_usage:
            TOKEN_COUNTER.labels(token_type="input").inc(
                token_usage.get("input_tokens", 0)
            )
            TOKEN_COUNTER.labels(token_type="output").inc(
                token_usage.get("output_tokens", 0)
            )

        self.monitor.logger.info(
            f"Operation {self.operation_name} completed",
            extra={
                "job_id": self.job_id,
                "duration_seconds": duration,
                "tokens_used": sum(token_usage.values()) if token_usage else 0,
                "status": "success",
            },
        )

    def record_failure(self, error: str) -> None:
        """Record failed operation"""
        OPERATION_COUNTER.labels(operation=self.operation_name, status="failure").inc()

        duration = time.time() - self.start_time
        OPERATION_DURATION.labels(operation=self.operation_name).observe(duration)

        self.monitor.logger.error(
            f"Operation {self.operation_name} failed",
            extra={
                "job_id": self.job_id,
                "duration_seconds": duration,
                "error": error,
                "status": "failure",
            },
        )

    def record_cache_hit(self) -> None:
        """Record cache hit"""
        CACHE_HIT_COUNTER.inc()

        self.monitor.logger.info(
            f"Cache hit for {self.operation_name}",
            extra={"job_id": self.job_id, "status": "cache_hit"},
        )


class SimpleMonitor:
    """
    Simple monitoring service for tracking operations and metrics.
    Focused on essential metrics without complexity.
    """

    def __init__(self):
        """Initialize monitor"""
        self.logger = logging.getLogger(__name__)
        self._operation_history: Dict[str, Dict[str, Any]] = {}

    @contextmanager
    def track_operation(self, operation_name: str, job_id: str):
        """
        Context manager for tracking an operation.

        Usage:
            with monitor.track_operation("content_generation", job_id) as tracker:
                # Do work
                tracker.record_success(duration, tokens)
        """
        tracker = OperationTracker(
            operation_name=operation_name, job_id=job_id, monitor=self
        )

        # Record start
        self.logger.info(
            f"Starting operation {operation_name}",
            extra={"job_id": job_id, "operation": operation_name, "status": "started"},
        )

        try:
            yield tracker
        except Exception as e:
            # Auto-record failure if exception occurs
            tracker.record_failure(str(e))
            raise

    def record_quality(self, job_id: str, quality_score: float) -> None:
        """Record quality score"""
        QUALITY_GAUGE.labels(job_id=job_id).set(quality_score)

        self.logger.info(
            "Quality score recorded",
            extra={"job_id": job_id, "quality_score": quality_score},
        )

    def get_operation_stats(self) -> Dict[str, Any]:
        """Get simple operation statistics"""
        # This would aggregate from Prometheus in production
        return {
            "total_operations": len(self._operation_history),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def log_debug_info(self, job_id: str, info: Dict[str, Any]) -> None:
        """Log debug information"""
        self.logger.debug("Debug info", extra={"job_id": job_id, "debug_info": info})
