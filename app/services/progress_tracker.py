"""
Progress tracking service for monitoring long-form content generation.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from prometheus_client import Gauge, Counter

# Prometheus metrics
ACTIVE_GENERATIONS = Gauge('active_content_generations', 'Number of active content generations')
COMPLETED_GENERATIONS = Counter('completed_content_generations_total', 'Total completed generations')
FAILED_GENERATIONS = Counter('failed_content_generations_total', 'Total failed generations')

class GenerationStage(Enum):
    """Stages of content generation."""
    INITIALIZING = "initializing"
    DECOMPOSING_TOPICS = "decomposing_topics"
    GENERATING_OUTLINES = "generating_outlines"
    GENERATING_SECTIONS = "generating_sections"
    ASSEMBLING_CONTENT = "assembling_content"
    GENERATING_AUDIO = "generating_audio"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class StageProgress:
    """Progress information for a specific stage."""
    stage: GenerationStage
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    current_item: Optional[str] = None
    total_items: Optional[int] = None
    completed_items: int = 0
    error_message: Optional[str] = None

@dataclass
class GenerationProgress:
    """Tracks progress of a content generation job."""
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
    
    def update_stage_progress(
        self,
        stage: GenerationStage,
        progress_percentage: float,
        current_item: Optional[str] = None,
        completed_items: Optional[int] = None
    ) -> None:
        """Update progress for a specific stage."""
        if stage not in self.stages:
            self.stages[stage] = StageProgress(
                stage=stage,
                started_at=datetime.utcnow()
            )
        
        stage_progress = self.stages[stage]
        stage_progress.progress_percentage = progress_percentage
        stage_progress.current_item = current_item
        
        if completed_items is not None:
            stage_progress.completed_items = completed_items
        
        if progress_percentage >= 100.0:
            stage_progress.completed_at = datetime.utcnow()
        
        self._update_overall_progress()
    
    def complete_stage(self, stage: GenerationStage) -> None:
        """Mark a stage as completed."""
        if stage in self.stages:
            self.stages[stage].completed_at = datetime.utcnow()
            self.stages[stage].progress_percentage = 100.0
        
        self._update_overall_progress()
    
    def fail_stage(self, stage: GenerationStage, error_message: str) -> None:
        """Mark a stage as failed."""
        if stage not in self.stages:
            self.stages[stage] = StageProgress(
                stage=stage,
                started_at=datetime.utcnow()
            )
        
        self.stages[stage].error_message = error_message
        self.current_stage = GenerationStage.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
    
    def _update_overall_progress(self) -> None:
        """Update overall progress based on stage progress."""
        stage_weights = {
            GenerationStage.INITIALIZING: 5,
            GenerationStage.DECOMPOSING_TOPICS: 10,
            GenerationStage.GENERATING_OUTLINES: 15,
            GenerationStage.GENERATING_SECTIONS: 50,
            GenerationStage.ASSEMBLING_CONTENT: 15,
            GenerationStage.GENERATING_AUDIO: 5
        }
        
        total_weight = sum(stage_weights.values())
        weighted_progress = 0.0
        
        for stage, weight in stage_weights.items():
            if stage in self.stages:
                stage_progress = self.stages[stage].progress_percentage
                weighted_progress += (stage_progress / 100.0) * weight
        
        self.overall_progress = (weighted_progress / total_weight) * 100.0

class ProgressTracker:
    """Service for tracking content generation progress."""
    
    def __init__(self):
        """Initialize the progress tracker."""
        self._jobs: Dict[str, GenerationProgress] = {}
        self._lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def start_job(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None
    ) -> str:
        """
        Start tracking a new content generation job.
        
        Returns:
            Job ID for tracking progress
        """
        job_id = str(uuid.uuid4())
        
        with self._lock:
            progress = GenerationProgress(
                job_id=job_id,
                syllabus_text=syllabus_text,
                target_format=target_format,
                target_duration=target_duration,
                target_pages=target_pages,
                started_at=datetime.utcnow(),
                current_stage=GenerationStage.INITIALIZING
            )
            
            self._jobs[job_id] = progress
            ACTIVE_GENERATIONS.inc()
        
        self.logger.info(f"Started tracking job: {job_id}")
        return job_id
    
    def update_stage(
        self,
        job_id: str,
        stage: GenerationStage,
        progress_percentage: float = 0.0,
        current_item: Optional[str] = None,
        total_items: Optional[int] = None,
        completed_items: Optional[int] = None
    ) -> None:
        """Update the current stage and progress."""
        with self._lock:
            if job_id not in self._jobs:
                self.logger.warning(f"Job not found: {job_id}")
                return
            
            progress = self._jobs[job_id]
            progress.current_stage = stage
            
            if stage not in progress.stages:
                progress.stages[stage] = StageProgress(
                    stage=stage,
                    started_at=datetime.utcnow(),
                    total_items=total_items
                )
            
            progress.update_stage_progress(
                stage, progress_percentage, current_item, completed_items
            )
        
        self.logger.info(f"Job {job_id}: {stage.value} - {progress_percentage}%")
    
    def complete_job(self, job_id: str, result: Dict[str, Any]) -> None:
        """Mark a job as completed."""
        with self._lock:
            if job_id not in self._jobs:
                self.logger.warning(f"Job not found: {job_id}")
                return
            
            progress = self._jobs[job_id]
            progress.current_stage = GenerationStage.COMPLETED
            progress.completed_at = datetime.utcnow()
            progress.result = result
            progress.overall_progress = 100.0
            
            ACTIVE_GENERATIONS.dec()
            COMPLETED_GENERATIONS.inc()
        
        self.logger.info(f"Job completed: {job_id}")
    
    def fail_job(self, job_id: str, error_message: str) -> None:
        """Mark a job as failed."""
        with self._lock:
            if job_id not in self._jobs:
                self.logger.warning(f"Job not found: {job_id}")
                return
            
            progress = self._jobs[job_id]
            progress.current_stage = GenerationStage.FAILED
            progress.completed_at = datetime.utcnow()
            progress.error_message = error_message
            
            ACTIVE_GENERATIONS.dec()
            FAILED_GENERATIONS.inc()
        
        self.logger.error(f"Job failed: {job_id} - {error_message}")
    
    def get_progress(self, job_id: str) -> Optional[GenerationProgress]:
        """Get progress information for a job."""
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_all_jobs(self) -> List[GenerationProgress]:
        """Get all tracked jobs."""
        with self._lock:
            return list(self._jobs.values())
    
    def get_active_jobs(self) -> List[GenerationProgress]:
        """Get all active (not completed/failed) jobs."""
        with self._lock:
            return [
                job for job in self._jobs.values()
                if job.current_stage not in [GenerationStage.COMPLETED, GenerationStage.FAILED]
            ]
    
    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """
        Remove old completed/failed jobs.
        
        Returns:
            Number of jobs removed
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        with self._lock:
            jobs_to_remove = [
                job_id for job_id, job in self._jobs.items()
                if job.completed_at and job.completed_at < cutoff_time
            ]
            
            for job_id in jobs_to_remove:
                self._jobs.pop(job_id, None)
                removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old jobs")
        
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        with self._lock:
            total_jobs = len(self._jobs)
            active_jobs = len(self.get_active_jobs())
            completed_jobs = len([
                j for j in self._jobs.values()
                if j.current_stage == GenerationStage.COMPLETED
            ])
            failed_jobs = len([
                j for j in self._jobs.values()
                if j.current_stage == GenerationStage.FAILED
            ])
        
        return {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'success_rate': completed_jobs / total_jobs if total_jobs > 0 else 0
        } 