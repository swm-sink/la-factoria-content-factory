"""
Export monitoring service for tracking export metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from prometheus_client import Counter, Gauge, Histogram, Summary

from app.models.export import ExportFormat, ExportStatus
from app.services.job.firestore_client import query_documents

logger = logging.getLogger(__name__)

# Prometheus metrics for export monitoring
export_requests_total = Counter("export_requests_total", "Total number of export requests", ["format", "status"])

export_duration_seconds = Histogram(
    "export_duration_seconds",
    "Time taken to complete export in seconds",
    ["format"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

export_file_size_bytes = Summary("export_file_size_bytes", "Size of exported files in bytes", ["format"])

active_export_jobs = Gauge("active_export_jobs", "Number of currently active export jobs", ["status"])

export_errors_total = Counter("export_errors_total", "Total number of export errors", ["format", "error_type"])

export_content_items_total = Counter("export_content_items_total", "Total number of content items exported", ["format"])


class ExportMonitor:
    """Monitor for export operations and metrics."""

    def __init__(self):
        """Initialize the export monitor."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def record_export_request(self, format: ExportFormat, content_count: int):
        """
        Record a new export request.

        Args:
            format: Export format
            content_count: Number of content items to export
        """
        export_requests_total.labels(format=format.value, status="requested").inc()

        export_content_items_total.labels(format=format.value).inc(content_count)

        self.logger.info(f"Export request recorded: format={format.value}, items={content_count}")

    async def record_export_completion(
        self, format: ExportFormat, duration_seconds: float, file_size_bytes: int, status: ExportStatus
    ):
        """
        Record export completion.

        Args:
            format: Export format
            duration_seconds: Time taken to complete export
            file_size_bytes: Size of exported file
            status: Final export status
        """
        # Record completion status
        export_requests_total.labels(format=format.value, status=status.value).inc()

        # Record duration
        export_duration_seconds.labels(format=format.value).observe(duration_seconds)

        # Record file size
        export_file_size_bytes.labels(format=format.value).observe(file_size_bytes)

        self.logger.info(
            f"Export completion recorded: format={format.value}, "
            f"status={status.value}, duration={duration_seconds:.2f}s, "
            f"size={file_size_bytes} bytes"
        )

    async def record_export_error(self, format: ExportFormat, error_type: str, error_message: str):
        """
        Record an export error.

        Args:
            format: Export format
            error_type: Type of error
            error_message: Error message
        """
        export_errors_total.labels(format=format.value, error_type=error_type).inc()

        self.logger.error(
            f"Export error recorded: format={format.value}, " f"type={error_type}, message={error_message}"
        )

    async def update_active_jobs_gauge(self):
        """Update the gauge for active export jobs."""
        # Query active jobs by status
        statuses = [ExportStatus.PENDING, ExportStatus.PROCESSING]

        for status in statuses:
            jobs = await query_documents(collection="export_jobs", filters={"status": status.value})
            active_export_jobs.labels(status=status.value).set(len(jobs))

    async def get_export_statistics(self, time_range_hours: int = 24) -> Dict[str, any]:
        """
        Get export statistics for the specified time range.

        Args:
            time_range_hours: Number of hours to look back

        Returns:
            Dictionary with export statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)

        # Query export jobs
        jobs = await query_documents(collection="export_jobs", filters={"created_at__gte": cutoff_time})

        # Calculate statistics
        stats = {
            "total_exports": len(jobs),
            "by_format": {},
            "by_status": {},
            "average_duration": 0,
            "total_size_bytes": 0,
            "error_rate": 0,
        }

        total_duration = 0
        completed_count = 0
        error_count = 0

        for job in jobs:
            # Count by format
            format = job.get("format", "unknown")
            stats["by_format"][format] = stats["by_format"].get(format, 0) + 1

            # Count by status
            status = job.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Calculate durations for completed jobs
            if status == ExportStatus.COMPLETED.value:
                if job.get("created_at") and job.get("completed_at"):
                    duration = (job["completed_at"] - job["created_at"]).total_seconds()
                    total_duration += duration
                    completed_count += 1

                # Add file size
                if job.get("file_size"):
                    stats["total_size_bytes"] += job["file_size"]

            elif status == ExportStatus.FAILED.value:
                error_count += 1

        # Calculate averages
        if completed_count > 0:
            stats["average_duration"] = total_duration / completed_count

        if len(jobs) > 0:
            stats["error_rate"] = error_count / len(jobs)

        return stats

    async def get_user_export_summary(self, user_id: str, days: int = 30) -> Dict[str, any]:
        """
        Get export summary for a specific user.

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            Dictionary with user export summary
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        # Query user's export jobs
        jobs = await query_documents(
            collection="export_jobs", filters={"user_id": user_id, "created_at__gte": cutoff_time}
        )

        # Calculate summary
        summary = {
            "total_exports": len(jobs),
            "formats_used": set(),
            "total_content_exported": 0,
            "total_size_bytes": 0,
            "last_export": None,
        }

        for job in jobs:
            # Track formats
            if job.get("format"):
                summary["formats_used"].add(job["format"])

            # Sum content items
            if job.get("content_count"):
                summary["total_content_exported"] += job["content_count"]

            # Sum file sizes
            if job.get("file_size"):
                summary["total_size_bytes"] += job["file_size"]

            # Track last export
            if job.get("created_at"):
                if not summary["last_export"] or job["created_at"] > summary["last_export"]:
                    summary["last_export"] = job["created_at"]

        # Convert set to list for JSON serialization
        summary["formats_used"] = list(summary["formats_used"])

        return summary


# Global monitor instance
export_monitor = ExportMonitor()
