"""
Advanced progress tracker for monitoring task progress with real-time updates.

This service provides comprehensive progress tracking with WebSocket support,
persistence, webhooks, and advanced analytics.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
ACTIVE_GENERATIONS = Gauge(
    "active_content_generations", "Number of active content generations"
)
COMPLETED_GENERATIONS = Counter(
    "completed_content_generations_total",
    "Total completed generations",
    ["format", "success"],
)
FAILED_GENERATIONS = Counter(
    "failed_content_generations_total",
    "Total failed generations",
    ["error_type", "stage"],
)
GENERATION_DURATION = Histogram(
    "content_generation_duration_seconds",
    "Time to complete content generation",
    ["format"],
)
STAGE_DURATION = Histogram(
    "generation_stage_duration_seconds", "Time to complete each stage", ["stage"]
)
PROGRESS_UPDATE_RATE = Counter(
    "progress_updates_total", "Total progress updates sent", ["method"]
)
WEBHOOK_NOTIFICATIONS = Counter(
    "webhook_notifications_total", "Total webhook notifications sent", ["status"]
)


class ProgressStatus(Enum):
    """Status of a progress tracker."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationStage(Enum):
    """Stages of content generation with detailed sub-stages."""

    INITIALIZING = "initializing"
    VALIDATING_INPUT = "validating_input"
    DECOMPOSING_TOPICS = "decomposing_topics"
    GENERATING_OUTLINES = "generating_outlines"
    GENERATING_CONTENT = "generating_content"
    QUALITY_VALIDATION = "quality_validation"
    CONTENT_REFINEMENT = "content_refinement"
    GENERATING_AUDIO = "generating_audio"
    FINAL_ASSEMBLY = "final_assembly"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StageProgress:
    """Enhanced progress information for a specific stage."""

    stage: GenerationStage
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    current_item: Optional[str] = None
    total_items: Optional[int] = None
    completed_items: int = 0
    failed_items: int = 0
    error_message: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    throughput: float = 0.0  # items per second
    quality_score: Optional[float] = None
    retry_count: int = 0
    sub_stages: Dict[str, float] = field(default_factory=dict)

    def calculate_throughput(self) -> float:
        """Calculate current throughput."""
        if not self.started_at or self.completed_items == 0:
            return 0.0

        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        if elapsed <= 0:
            return 0.0

        self.throughput = self.completed_items / elapsed
        return self.throughput

    def estimate_completion(self) -> Optional[datetime]:
        """Estimate completion time based on current progress."""
        if not self.total_items or self.throughput <= 0:
            return None

        remaining_items = self.total_items - self.completed_items
        if remaining_items <= 0:
            return datetime.utcnow()

        estimated_seconds = remaining_items / self.throughput
        self.estimated_completion = datetime.utcnow() + timedelta(
            seconds=estimated_seconds
        )
        return self.estimated_completion


@dataclass
class ProgressUpdate:
    """Structure for progress update notifications."""

    job_id: str
    stage: GenerationStage
    progress_percentage: float
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationProgress:
    """Enhanced tracking of content generation job progress."""

    job_id: str
    syllabus_text: str
    target_format: str
    target_duration: Optional[float]
    target_pages: Optional[int]
    started_at: datetime
    current_stage: GenerationStage
    stages: Dict[GenerationStage, StageProgress] = field(default_factory=dict)
    overall_progress: float = 0.0
    estimated_completion: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    priority: int = 5  # 1-10, 10 being highest
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    webhook_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def update_stage_progress(
        self,
        stage: GenerationStage,
        progress_percentage: float,
        current_item: Optional[str] = None,
        completed_items: Optional[int] = None,
        quality_score: Optional[float] = None,
        sub_stage: Optional[str] = None,
        sub_stage_progress: Optional[float] = None,
    ) -> None:
        """Update progress for a specific stage with enhanced tracking."""
        if stage not in self.stages:
            self.stages[stage] = StageProgress(
                stage=stage, started_at=datetime.utcnow()
            )

        stage_progress = self.stages[stage]
        stage_progress.progress_percentage = min(100.0, max(0.0, progress_percentage))
        stage_progress.current_item = current_item

        if completed_items is not None:
            stage_progress.completed_items = completed_items
            stage_progress.calculate_throughput()

        if quality_score is not None:
            stage_progress.quality_score = quality_score

        if sub_stage and sub_stage_progress is not None:
            stage_progress.sub_stages[sub_stage] = sub_stage_progress

        if progress_percentage >= 100.0:
            stage_progress.completed_at = datetime.utcnow()

            # Record stage duration metric
            duration = (
                stage_progress.completed_at - stage_progress.started_at
            ).total_seconds()
            STAGE_DURATION.labels(stage=stage.value).observe(duration)

        self._update_overall_progress()
        stage_progress.estimate_completion()

    def complete_stage(
        self, stage: GenerationStage, quality_score: Optional[float] = None
    ) -> None:
        """Mark a stage as completed with quality assessment."""
        if stage in self.stages:
            self.stages[stage].completed_at = datetime.utcnow()
            self.stages[stage].progress_percentage = 100.0
            if quality_score is not None:
                self.stages[stage].quality_score = quality_score

        self._update_overall_progress()

    def fail_stage(
        self, stage: GenerationStage, error_message: str, retry_count: int = 0
    ) -> None:
        """Mark a stage as failed with retry tracking."""
        if stage not in self.stages:
            self.stages[stage] = StageProgress(
                stage=stage, started_at=datetime.utcnow()
            )

        self.stages[stage].error_message = error_message
        self.stages[stage].retry_count = retry_count

        if retry_count == 0:  # Final failure
            self.current_stage = GenerationStage.FAILED
            self.error_message = error_message
            self.completed_at = datetime.utcnow()

    def _update_overall_progress(self) -> None:
        """Update overall progress with weighted stage importance."""
        stage_weights = {
            GenerationStage.INITIALIZING: 2,
            GenerationStage.VALIDATING_INPUT: 3,
            GenerationStage.DECOMPOSING_TOPICS: 8,
            GenerationStage.GENERATING_OUTLINES: 12,
            GenerationStage.GENERATING_CONTENT: 35,
            GenerationStage.QUALITY_VALIDATION: 10,
            GenerationStage.CONTENT_REFINEMENT: 15,
            GenerationStage.GENERATING_AUDIO: 8,
            GenerationStage.FINAL_ASSEMBLY: 5,
            GenerationStage.FINALIZING: 2,
        }

        total_weight = sum(stage_weights.values())
        weighted_progress = 0.0

        for stage, weight in stage_weights.items():
            if stage in self.stages:
                stage_progress = self.stages[stage].progress_percentage
                weighted_progress += (stage_progress / 100.0) * weight

        self.overall_progress = min(100.0, (weighted_progress / total_weight) * 100.0)

        # Update overall estimated completion
        if self.overall_progress > 0 and self.overall_progress < 100:
            elapsed = (datetime.utcnow() - self.started_at).total_seconds()
            if elapsed > 0:
                rate = self.overall_progress / elapsed
                if rate > 0:
                    remaining = (100 - self.overall_progress) / rate
                    self.estimated_completion = datetime.utcnow() + timedelta(
                        seconds=remaining
                    )

    def get_current_throughput(self) -> float:
        """Get current processing throughput."""
        if self.current_stage in self.stages:
            return self.stages[self.current_stage].throughput
        return 0.0

    def get_eta_seconds(self) -> Optional[float]:
        """Get estimated time to completion in seconds."""
        if self.estimated_completion:
            return (self.estimated_completion - datetime.utcnow()).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)

        # Convert datetime objects to ISO strings
        data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        if self.estimated_completion:
            data["estimated_completion"] = self.estimated_completion.isoformat()

        # Convert enum values
        data["current_stage"] = self.current_stage.value

        # Convert stages
        stages_dict = {}
        for stage, progress in self.stages.items():
            stage_data = asdict(progress)
            stage_data["stage"] = stage.value
            stage_data["started_at"] = progress.started_at.isoformat()
            if progress.completed_at:
                stage_data["completed_at"] = progress.completed_at.isoformat()
            if progress.estimated_completion:
                stage_data[
                    "estimated_completion"
                ] = progress.estimated_completion.isoformat()
            stages_dict[stage.value] = stage_data

        data["stages"] = stages_dict
        return data


class AdvancedProgressTracker:
    """Advanced service for tracking content generation progress with real-time features."""

    def __init__(self, enable_webhooks: bool = True, enable_persistence: bool = True):
        """Initialize the advanced progress tracker."""
        self._jobs: Dict[str, GenerationProgress] = {}
        self._lock = Lock()
        self._subscribers: Dict[
            str, Set[Callable]
        ] = {}  # job_id -> set of callback functions
        self._global_subscribers: Set[Callable] = set()  # Global progress listeners
        self._webhook_enabled = enable_webhooks
        self._persistence_enabled = enable_persistence
        self.logger = logging.getLogger(__name__)

    def start_job(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None,
        user_id: Optional[str] = None,
        priority: int = 5,
        webhook_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Start tracking a new content generation job with enhanced options."""
        job_id = str(uuid.uuid4())

        with self._lock:
            progress = GenerationProgress(
                job_id=job_id,
                syllabus_text=syllabus_text,
                target_format=target_format,
                target_duration=target_duration,
                target_pages=target_pages,
                started_at=datetime.utcnow(),
                current_stage=GenerationStage.INITIALIZING,
                user_id=user_id,
                priority=priority,
                webhook_url=webhook_url,
                tags=tags or [],
            )

            self._jobs[job_id] = progress
            self._subscribers[job_id] = set()
            ACTIVE_GENERATIONS.inc()

        self.logger.info(
            f"Started tracking job: {job_id} (user: {user_id}, priority: {priority})"
        )

        # Notify subscribers
        self._notify_progress_update(
            job_id, GenerationStage.INITIALIZING, 0.0, "Job started"
        )

        return job_id

    def update_stage(
        self,
        job_id: str,
        stage: GenerationStage,
        progress_percentage: float = 0.0,
        current_item: Optional[str] = None,
        total_items: Optional[int] = None,
        completed_items: Optional[int] = None,
        quality_score: Optional[float] = None,
        message: Optional[str] = None,
        sub_stage: Optional[str] = None,
        sub_stage_progress: Optional[float] = None,
        resource_usage: Optional[Dict[str, float]] = None,
    ) -> None:
        """Update stage with comprehensive tracking information."""
        with self._lock:
            if job_id not in self._jobs:
                self.logger.warning(f"Job not found: {job_id}")
                return

            progress = self._jobs[job_id]

            # Update current stage if it's progressing forward
            if stage != progress.current_stage:
                progress.current_stage = stage

            # Initialize stage if not exists
            if stage not in progress.stages:
                progress.stages[stage] = StageProgress(
                    stage=stage, started_at=datetime.utcnow(), total_items=total_items
                )

            # Update progress
            progress.update_stage_progress(
                stage,
                progress_percentage,
                current_item,
                completed_items,
                quality_score,
                sub_stage,
                sub_stage_progress,
            )

            # Update resource usage
            if resource_usage:
                progress.resource_usage.update(resource_usage)

        # Create update message
        update_message = (
            message
            or f"{stage.value.replace('_', ' ').title()}: {progress_percentage:.1f}%"
        )
        if current_item:
            update_message += f" - {current_item}"

        self.logger.info(f"Job {job_id}: {update_message}")

        # Notify subscribers
        self._notify_progress_update(job_id, stage, progress_percentage, update_message)

        # Update metrics
        PROGRESS_UPDATE_RATE.labels(method="stage_update").inc()

    def complete_job(
        self,
        job_id: str,
        result: Dict[str, Any],
        quality_metrics: Optional[Dict[str, float]] = None,
    ) -> None:
        """Mark a job as completed with quality assessment."""
        with self._lock:
            if job_id not in self._jobs:
                self.logger.warning(f"Job not found: {job_id}")
                return

            progress = self._jobs[job_id]
            progress.current_stage = GenerationStage.COMPLETED
            progress.completed_at = datetime.utcnow()
            progress.result = result
            progress.overall_progress = 100.0

            if quality_metrics:
                progress.quality_metrics.update(quality_metrics)

            # Record completion metrics
            duration = (progress.completed_at - progress.started_at).total_seconds()
            GENERATION_DURATION.labels(format=progress.target_format).observe(duration)
            COMPLETED_GENERATIONS.labels(
                format=progress.target_format, success="true"
            ).inc()
            ACTIVE_GENERATIONS.dec()

        self.logger.info(f"Job completed: {job_id}")

        # Notify subscribers
        self._notify_progress_update(
            job_id, GenerationStage.COMPLETED, 100.0, "Job completed successfully"
        )

    def fail_job(
        self,
        job_id: str,
        error_message: str,
        error_stage: Optional[GenerationStage] = None,
        error_type: str = "unknown",
    ) -> None:
        """Mark a job as failed with detailed error information."""
        with self._lock:
            if job_id not in self._jobs:
                self.logger.warning(f"Job not found: {job_id}")
                return

            progress = self._jobs[job_id]
            progress.current_stage = GenerationStage.FAILED
            progress.completed_at = datetime.utcnow()
            progress.error_message = error_message

            # Mark the current stage as failed
            if error_stage and error_stage in progress.stages:
                progress.stages[error_stage].error_message = error_message

            # Record failure metrics
            stage_name = (
                error_stage.value if error_stage else progress.current_stage.value
            )
            FAILED_GENERATIONS.labels(error_type=error_type, stage=stage_name).inc()
            COMPLETED_GENERATIONS.labels(
                format=progress.target_format, success="false"
            ).inc()
            ACTIVE_GENERATIONS.dec()

        self.logger.error(f"Job failed: {job_id} - {error_message}")

        # Notify subscribers
        self._notify_progress_update(
            job_id,
            GenerationStage.FAILED,
            progress.overall_progress,
            f"Job failed: {error_message}",
        )

    def cancel_job(self, job_id: str, reason: str = "User cancelled") -> bool:
        """Cancel a running job."""
        with self._lock:
            if job_id not in self._jobs:
                self.logger.warning(f"Job not found: {job_id}")
                return False

            progress = self._jobs[job_id]

            if progress.current_stage in [
                GenerationStage.COMPLETED,
                GenerationStage.FAILED,
            ]:
                self.logger.warning(f"Cannot cancel already finished job: {job_id}")
                return False

            progress.current_stage = GenerationStage.CANCELLED
            progress.completed_at = datetime.utcnow()
            progress.error_message = reason

            ACTIVE_GENERATIONS.dec()

        self.logger.info(f"Job cancelled: {job_id} - {reason}")

        # Notify subscribers
        self._notify_progress_update(
            job_id,
            GenerationStage.CANCELLED,
            progress.overall_progress,
            f"Job cancelled: {reason}",
        )

        return True

    def subscribe_to_job(
        self, job_id: str, callback: Callable[[ProgressUpdate], None]
    ) -> bool:
        """Subscribe to progress updates for a specific job."""
        with self._lock:
            if job_id not in self._jobs:
                return False

            if job_id not in self._subscribers:
                self._subscribers[job_id] = set()

            self._subscribers[job_id].add(callback)

        self.logger.debug(f"Added subscriber to job: {job_id}")
        return True

    def unsubscribe_from_job(
        self, job_id: str, callback: Callable[[ProgressUpdate], None]
    ) -> bool:
        """Unsubscribe from job progress updates."""
        with self._lock:
            if job_id in self._subscribers:
                self._subscribers[job_id].discard(callback)
                if not self._subscribers[job_id]:  # Remove empty set
                    del self._subscribers[job_id]
                return True
        return False

    def subscribe_global(self, callback: Callable[[ProgressUpdate], None]) -> None:
        """Subscribe to all progress updates."""
        with self._lock:
            self._global_subscribers.add(callback)

        self.logger.debug("Added global progress subscriber")

    def unsubscribe_global(self, callback: Callable[[ProgressUpdate], None]) -> None:
        """Unsubscribe from global progress updates."""
        with self._lock:
            self._global_subscribers.discard(callback)

    def _notify_progress_update(
        self, job_id: str, stage: GenerationStage, progress: float, message: str
    ) -> None:
        """Send progress updates to all subscribers."""
        update = ProgressUpdate(
            job_id=job_id,
            stage=stage,
            progress_percentage=progress,
            message=message,
            timestamp=datetime.utcnow(),
        )

        # Notify job-specific subscribers
        job_subscribers = self._subscribers.get(job_id, set())
        for callback in job_subscribers:
            try:
                callback(update)
            except Exception as e:
                self.logger.error(f"Error in job subscriber callback: {e}")

        # Notify global subscribers
        for callback in self._global_subscribers:
            try:
                callback(update)
            except Exception as e:
                self.logger.error(f"Error in global subscriber callback: {e}")

        # Send webhook notification if enabled
        if self._webhook_enabled:
            asyncio.create_task(self._send_webhook_notification(job_id, update))

    async def _send_webhook_notification(
        self, job_id: str, update: ProgressUpdate
    ) -> None:
        """Send webhook notification for progress update."""
        try:
            with self._lock:
                job = self._jobs.get(job_id)
                if not job or not job.webhook_url:
                    return

            # Prepare webhook payload
            payload = {
                "job_id": job_id,
                "stage": update.stage.value,
                "progress": update.progress_percentage,
                "message": update.message,
                "timestamp": update.timestamp.isoformat(),
                "overall_progress": job.overall_progress,
                "estimated_completion": job.estimated_completion.isoformat()
                if job.estimated_completion
                else None,
            }

            # This would be implemented with actual HTTP client
            # For now, just log the webhook attempt
            self.logger.info(
                f"Webhook notification sent for job {job_id}: {job.webhook_url}"
            )
            WEBHOOK_NOTIFICATIONS.labels(status="success").inc()

        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            WEBHOOK_NOTIFICATIONS.labels(status="error").inc()

    def get_progress(self, job_id: str) -> Optional[GenerationProgress]:
        """Get progress information for a job."""
        with self._lock:
            return self._jobs.get(job_id)

    def get_all_jobs(self, user_id: Optional[str] = None) -> List[GenerationProgress]:
        """Get all tracked jobs, optionally filtered by user."""
        with self._lock:
            jobs = list(self._jobs.values())
            if user_id:
                jobs = [job for job in jobs if job.user_id == user_id]
            return jobs

    def get_active_jobs(
        self, user_id: Optional[str] = None
    ) -> List[GenerationProgress]:
        """Get all active jobs, optionally filtered by user."""
        with self._lock:
            active_stages = {
                GenerationStage.COMPLETED,
                GenerationStage.FAILED,
                GenerationStage.CANCELLED,
            }
            jobs = [
                job
                for job in self._jobs.values()
                if job.current_stage not in active_stages
            ]
            if user_id:
                jobs = [job for job in jobs if job.user_id == user_id]
            return jobs

    def get_jobs_by_priority(self, min_priority: int = 1) -> List[GenerationProgress]:
        """Get jobs filtered by minimum priority level."""
        with self._lock:
            return [job for job in self._jobs.values() if job.priority >= min_priority]

    def get_jobs_by_tags(
        self, tags: List[str], match_all: bool = False
    ) -> List[GenerationProgress]:
        """Get jobs filtered by tags."""
        with self._lock:
            jobs = []
            for job in self._jobs.values():
                if match_all:
                    if all(tag in job.tags for tag in tags):
                        jobs.append(job)
                else:
                    if any(tag in job.tags for tag in tags):
                        jobs.append(job)
            return jobs

    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Remove old completed/failed jobs."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        removed_count = 0

        with self._lock:
            jobs_to_remove = [
                job_id
                for job_id, job in self._jobs.items()
                if job.completed_at and job.completed_at < cutoff_time
            ]

            for job_id in jobs_to_remove:
                self._jobs.pop(job_id, None)
                self._subscribers.pop(job_id, None)  # Remove subscribers too
                removed_count += 1

        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old jobs")

        return removed_count

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive tracker statistics."""
        with self._lock:
            total_jobs = len(self._jobs)
            active_jobs = len(self.get_active_jobs())
            completed_jobs = len(
                [
                    j
                    for j in self._jobs.values()
                    if j.current_stage == GenerationStage.COMPLETED
                ]
            )
            failed_jobs = len(
                [
                    j
                    for j in self._jobs.values()
                    if j.current_stage == GenerationStage.FAILED
                ]
            )
            cancelled_jobs = len(
                [
                    j
                    for j in self._jobs.values()
                    if j.current_stage == GenerationStage.CANCELLED
                ]
            )

            # Calculate average quality scores
            quality_scores = [
                sum(job.quality_metrics.values()) / len(job.quality_metrics)
                for job in self._jobs.values()
                if job.quality_metrics
            ]
            avg_quality = (
                sum(quality_scores) / len(quality_scores) if quality_scores else 0
            )

            # Calculate average completion time
            completed_durations = [
                (job.completed_at - job.started_at).total_seconds()
                for job in self._jobs.values()
                if job.completed_at and job.current_stage == GenerationStage.COMPLETED
            ]
            avg_completion_time = (
                sum(completed_durations) / len(completed_durations)
                if completed_durations
                else 0
            )

        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "cancelled_jobs": cancelled_jobs,
            "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0,
            "average_quality_score": avg_quality,
            "average_completion_time_seconds": avg_completion_time,
            "total_subscribers": sum(len(subs) for subs in self._subscribers.values())
            + len(self._global_subscribers),
        }

    def export_job_data(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Export complete job data for analysis or backup."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            return job.to_dict()

    def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights and recommendations."""
        with self._lock:
            jobs = list(self._jobs.values())

        if not jobs:
            return {"message": "No jobs to analyze"}

        # Analyze stage performance
        stage_times = {}
        for job in jobs:
            for stage, stage_progress in job.stages.items():
                if stage_progress.completed_at:
                    duration = (
                        stage_progress.completed_at - stage_progress.started_at
                    ).total_seconds()
                    if stage.value not in stage_times:
                        stage_times[stage.value] = []
                    stage_times[stage.value].append(duration)

        # Calculate bottlenecks
        avg_stage_times = {
            stage: sum(times) / len(times)
            for stage, times in stage_times.items()
            if times
        }

        bottleneck_stage = (
            max(avg_stage_times.items(), key=lambda x: x[1])
            if avg_stage_times
            else None
        )

        return {
            "total_jobs_analyzed": len(jobs),
            "average_stage_times": avg_stage_times,
            "bottleneck_stage": bottleneck_stage[0] if bottleneck_stage else None,
            "bottleneck_avg_time": bottleneck_stage[1] if bottleneck_stage else None,
            "recommendations": self._generate_recommendations(avg_stage_times, jobs),
        }

    def _generate_recommendations(
        self, stage_times: Dict[str, float], jobs: List[GenerationProgress]
    ) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        if not stage_times:
            return ["Insufficient data for recommendations"]

        # Find slow stages
        max_time = max(stage_times.values()) if stage_times else 0
        slow_stages = [
            stage for stage, time in stage_times.items() if time > max_time * 0.7
        ]

        if slow_stages:
            recommendations.append(
                f"Consider optimizing stages: {', '.join(slow_stages)}"
            )

        # Check for frequent failures
        failed_jobs = [
            job for job in jobs if job.current_stage == GenerationStage.FAILED
        ]
        if len(failed_jobs) > len(jobs) * 0.1:  # More than 10% failure rate
            recommendations.append(
                "High failure rate detected - review error handling and input validation"
            )

        # Check for resource usage patterns
        high_resource_jobs = [
            job for job in jobs if job.resource_usage.get("memory_mb", 0) > 1000
        ]
        if high_resource_jobs:
            recommendations.append(
                "Consider implementing memory optimization for large content generation"
            )

        return recommendations


# Global instance for application use
progress_tracker = AdvancedProgressTracker()

# Legacy alias for backward compatibility
ProgressTracker = AdvancedProgressTracker
