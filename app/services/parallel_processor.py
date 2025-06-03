"""
Advanced parallel processor for handling concurrent tasks with optimizations.

This service provides efficient parallel processing with circuit breakers,
adaptive scaling, resource monitoring, and comprehensive metrics.
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

import psutil
from prometheus_client import Counter, Gauge, Histogram

# Prometheus metrics
PARALLEL_EXECUTION_TIME = Histogram(
    "parallel_execution_duration_seconds",
    "Time spent on parallel execution",
    ["task_type"],
)
PARALLEL_TASKS_COMPLETED = Counter(
    "parallel_tasks_completed_total", "Total parallel tasks completed", ["task_type"]
)
PARALLEL_TASKS_FAILED = Counter(
    "parallel_tasks_failed_total",
    "Total parallel tasks failed",
    ["task_type", "error_type"],
)
PARALLEL_ACTIVE_WORKERS = Gauge("parallel_active_workers", "Number of active workers")
PARALLEL_QUEUE_SIZE = Gauge("parallel_queue_size", "Number of tasks in queue")
PARALLEL_THROUGHPUT = Histogram(
    "parallel_throughput_tasks_per_second", "Tasks processed per second"
)
PARALLEL_MEMORY_USAGE = Gauge(
    "parallel_memory_usage_mb", "Memory usage during parallel processing"
)
PARALLEL_CPU_USAGE = Gauge(
    "parallel_cpu_usage_percent", "CPU usage during parallel processing"
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Enhanced result of a processing task."""

    success: bool
    data: Any
    error: Optional[str] = None
    task_id: str = ""
    execution_time: float = 0.0
    memory_peak: float = 0.0
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for fault tolerance."""

    failure_count: int = 0
    last_failure_time: float = 0.0
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_threshold: int = 5
    recovery_timeout: float = 60.0  # seconds

    def should_allow_request(self) -> bool:
        """Check if request should be allowed."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


@dataclass
class ResourceMonitor:
    """Monitor system resources during parallel processing."""

    initial_memory: float = 0.0
    peak_memory: float = 0.0
    initial_cpu: float = 0.0
    peak_cpu: float = 0.0

    def start_monitoring(self):
        """Start resource monitoring."""
        process = psutil.Process()
        self.initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        self.initial_cpu = process.cpu_percent()
        self.peak_memory = self.initial_memory
        self.peak_cpu = self.initial_cpu

    def update_peak_usage(self):
        """Update peak resource usage."""
        try:
            process = psutil.Process()
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            current_cpu = process.cpu_percent()

            if current_memory > self.peak_memory:
                self.peak_memory = current_memory
            if current_cpu > self.peak_cpu:
                self.peak_cpu = current_cpu

            # Update Prometheus metrics
            PARALLEL_MEMORY_USAGE.set(current_memory)
            PARALLEL_CPU_USAGE.set(current_cpu)
        except Exception as e:
            logger.warning(f"Failed to update resource usage: {e}")


class AdvancedParallelProcessor:
    """Advanced parallel processor with optimizations and monitoring."""

    def __init__(self, max_workers: int = 4, enable_circuit_breaker: bool = True):
        """Initialize the advanced parallel processor."""
        self.max_workers = max_workers
        self.enable_circuit_breaker = enable_circuit_breaker
        self.executor = None  # Will be created when needed
        self.circuit_breaker = CircuitBreakerState() if enable_circuit_breaker else None
        self.resource_monitor = ResourceMonitor()
        self.active_workers = 0
        self.queue_size = 0

    def _get_executor(self) -> ThreadPoolExecutor:
        """Get or create thread pool executor."""
        if self.executor is None:
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self.executor

    def execute_parallel_tasks(
        self,
        tasks: List[Callable],
        task_ids: List[str],
        task_type: str = "default",
        progress_callback: Optional[Callable[[str, float], None]] = None,
        enable_retries: bool = True,
        max_retries: int = 2,
    ) -> List[ProcessingResult]:
        """
        Execute multiple tasks in parallel with advanced features.

        Args:
            tasks: List of callable tasks to execute
            task_ids: List of task identifiers
            task_type: Type of tasks for metrics
            progress_callback: Optional callback for progress updates
            enable_retries: Whether to enable automatic retries
            max_retries: Maximum number of retries per task

        Returns:
            List of ProcessingResult objects
        """
        if len(tasks) != len(task_ids):
            raise ValueError("Number of tasks must match number of task IDs")

        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.should_allow_request():
            logger.warning("Circuit breaker is OPEN, rejecting parallel task execution")
            return [
                ProcessingResult(
                    success=False,
                    data=None,
                    error="Circuit breaker is OPEN",
                    task_id=task_id,
                    metadata={"circuit_breaker_state": self.circuit_breaker.state},
                )
                for task_id in task_ids
            ]

        results = []
        start_time = time.time()

        # Start resource monitoring
        self.resource_monitor.start_monitoring()

        # Update queue size metric
        self.queue_size = len(tasks)
        PARALLEL_QUEUE_SIZE.set(self.queue_size)

        executor = self._get_executor()

        # Submit all tasks
        future_to_task = {}
        for task, task_id in zip(tasks, task_ids):
            future = executor.submit(
                self._execute_task_with_monitoring,
                task,
                task_id,
                task_type,
                enable_retries,
                max_retries,
            )
            future_to_task[future] = task_id
            self.active_workers += 1
            PARALLEL_ACTIVE_WORKERS.set(self.active_workers)

        completed_count = 0
        total_tasks = len(tasks)
        failed_tasks = 0

        # Process completed tasks
        for future in as_completed(future_to_task):
            task_id = future_to_task[future]

            try:
                result = future.result()
                results.append(result)

                if result.success:
                    PARALLEL_TASKS_COMPLETED.labels(task_type=task_type).inc()
                    if self.circuit_breaker:
                        self.circuit_breaker.record_success()
                else:
                    failed_tasks += 1
                    error_type = self._classify_error(result.error)
                    PARALLEL_TASKS_FAILED.labels(
                        task_type=task_type, error_type=error_type
                    ).inc()
                    if self.circuit_breaker:
                        self.circuit_breaker.record_failure()

                completed_count += 1
                self.active_workers -= 1
                PARALLEL_ACTIVE_WORKERS.set(self.active_workers)

                # Update progress
                if progress_callback:
                    progress = (completed_count / total_tasks) * 100
                    progress_callback(task_id, progress)

                # Update resource monitoring
                self.resource_monitor.update_peak_usage()

                logger.info(f"Task {task_id} completed: {result.success}")

            except Exception as e:
                error_result = ProcessingResult(
                    success=False,
                    data=None,
                    error=str(e),
                    task_id=task_id,
                    metadata={"execution_error": True},
                )
                results.append(error_result)
                failed_tasks += 1

                error_type = self._classify_error(str(e))
                PARALLEL_TASKS_FAILED.labels(
                    task_type=task_type, error_type=error_type
                ).inc()

                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()

                self.active_workers -= 1
                PARALLEL_ACTIVE_WORKERS.set(self.active_workers)

                logger.error(f"Task {task_id} failed: {str(e)}")

        # Calculate and record throughput
        execution_time = time.time() - start_time
        throughput = total_tasks / execution_time if execution_time > 0 else 0
        PARALLEL_THROUGHPUT.observe(throughput)

        # Reset queue size
        self.queue_size = 0
        PARALLEL_QUEUE_SIZE.set(self.queue_size)

        logger.info(
            f"Parallel execution completed: {total_tasks} tasks, "
            f"{failed_tasks} failed, throughput: {throughput:.2f} tasks/sec"
        )

        return results

    def _execute_task_with_monitoring(
        self,
        task: Callable,
        task_id: str,
        task_type: str,
        enable_retries: bool = True,
        max_retries: int = 2,
    ) -> ProcessingResult:
        """Execute a single task with comprehensive monitoring."""
        start_time = time.time()
        retry_count = 0
        last_error = None

        while retry_count <= max_retries:
            try:
                with PARALLEL_EXECUTION_TIME.labels(task_type=task_type).time():
                    result = task()

                execution_time = time.time() - start_time

                return ProcessingResult(
                    success=True,
                    data=result,
                    task_id=task_id,
                    execution_time=execution_time,
                    memory_peak=self.resource_monitor.peak_memory,
                    retry_count=retry_count,
                    metadata={"task_type": task_type, "final_attempt": True},
                )

            except Exception as e:
                last_error = str(e)
                retry_count += 1

                if not enable_retries or retry_count > max_retries:
                    break

                # Exponential backoff for retries
                retry_delay = min(2**retry_count, 10)  # Max 10 seconds
                time.sleep(retry_delay)

                logger.warning(
                    f"Task {task_id} failed, retry {retry_count}/{max_retries}: {e}"
                )

        execution_time = time.time() - start_time

        return ProcessingResult(
            success=False,
            data=None,
            error=last_error,
            task_id=task_id,
            execution_time=execution_time,
            memory_peak=self.resource_monitor.peak_memory,
            retry_count=retry_count,
            metadata={
                "task_type": task_type,
                "retries_exhausted": retry_count > max_retries,
            },
        )

    def _classify_error(self, error_message: str) -> str:
        """Classify error type for metrics."""
        if not error_message:
            return "unknown"

        error_lower = error_message.lower()

        if "timeout" in error_lower:
            return "timeout"
        elif "memory" in error_lower or "out of memory" in error_lower:
            return "memory"
        elif "connection" in error_lower or "network" in error_lower:
            return "network"
        elif "permission" in error_lower or "unauthorized" in error_lower:
            return "permission"
        elif "validation" in error_lower or "invalid" in error_lower:
            return "validation"
        else:
            return "application"

    async def execute_async_tasks(
        self,
        async_tasks: List[Awaitable],
        task_ids: List[str],
        task_type: str = "async_default",
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> List[ProcessingResult]:
        """Execute multiple async tasks concurrently with monitoring."""
        if len(async_tasks) != len(task_ids):
            raise ValueError("Number of tasks must match number of task IDs")

        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.should_allow_request():
            logger.warning("Circuit breaker is OPEN, rejecting async task execution")
            return [
                ProcessingResult(
                    success=False,
                    data=None,
                    error="Circuit breaker is OPEN",
                    task_id=task_id,
                    metadata={"circuit_breaker_state": self.circuit_breaker.state},
                )
                for task_id in task_ids
            ]

        results = []
        start_time = time.time()
        semaphore = asyncio.Semaphore(self.max_workers)

        # Start resource monitoring
        self.resource_monitor.start_monitoring()

        async def execute_with_semaphore(
            task: Awaitable, task_id: str
        ) -> ProcessingResult:
            """Execute task with semaphore to limit concurrency."""
            async with semaphore:
                return await self._execute_async_task_with_monitoring(
                    task, task_id, task_type
                )

        # Create tasks with semaphore
        limited_tasks = [
            execute_with_semaphore(task, task_id)
            for task, task_id in zip(async_tasks, task_ids)
        ]

        completed_count = 0
        total_tasks = len(async_tasks)
        failed_tasks = 0

        # Execute all tasks concurrently
        for coro in asyncio.as_completed(limited_tasks):
            result = await coro
            results.append(result)

            if result.success:
                PARALLEL_TASKS_COMPLETED.labels(task_type=task_type).inc()
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()
            else:
                failed_tasks += 1
                error_type = self._classify_error(result.error)
                PARALLEL_TASKS_FAILED.labels(
                    task_type=task_type, error_type=error_type
                ).inc()
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()

            completed_count += 1

            # Update progress
            if progress_callback:
                progress = (completed_count / total_tasks) * 100
                progress_callback(result.task_id, progress)

            # Update resource monitoring
            self.resource_monitor.update_peak_usage()

            logger.info(f"Async task {result.task_id} completed: {result.success}")

        # Calculate and record throughput
        execution_time = time.time() - start_time
        throughput = total_tasks / execution_time if execution_time > 0 else 0
        PARALLEL_THROUGHPUT.observe(throughput)

        logger.info(
            f"Async parallel execution completed: {total_tasks} tasks, "
            f"{failed_tasks} failed, throughput: {throughput:.2f} tasks/sec"
        )

        return results

    async def _execute_async_task_with_monitoring(
        self, task: Awaitable, task_id: str, task_type: str
    ) -> ProcessingResult:
        """Execute a single async task with timing measurement."""
        start_time = time.time()

        try:
            result = await task
            execution_time = time.time() - start_time

            return ProcessingResult(
                success=True,
                data=result,
                task_id=task_id,
                execution_time=execution_time,
                memory_peak=self.resource_monitor.peak_memory,
                metadata={"task_type": task_type},
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return ProcessingResult(
                success=False,
                data=None,
                error=str(e),
                task_id=task_id,
                execution_time=execution_time,
                memory_peak=self.resource_monitor.peak_memory,
                metadata={"task_type": task_type},
            )

    def get_optimal_worker_count(
        self, task_count: int, task_complexity: str = "medium"
    ) -> int:
        """
        Get optimal number of workers based on task count and complexity.

        Args:
            task_count: Number of tasks to execute
            task_complexity: Complexity level (low, medium, high)

        Returns:
            Optimal worker count
        """
        # Base calculation
        base_workers = min(task_count, self.max_workers)

        # Adjust based on complexity
        if task_complexity == "low":
            # I/O-bound tasks can handle more parallelism
            optimal = min(task_count, self.max_workers * 2)
        elif task_complexity == "high":
            # CPU-intensive tasks need fewer workers
            optimal = min(task_count, max(1, self.max_workers // 2))
        else:  # medium
            optimal = base_workers

        # Don't create more workers than tasks
        return min(optimal, task_count)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        return {
            "active_workers": self.active_workers,
            "queue_size": self.queue_size,
            "max_workers": self.max_workers,
            "circuit_breaker_state": self.circuit_breaker.state
            if self.circuit_breaker
            else None,
            "resource_usage": {
                "memory_peak_mb": self.resource_monitor.peak_memory,
                "cpu_peak_percent": self.resource_monitor.peak_cpu,
            },
        }

    def __del__(self):
        """Cleanup resources."""
        if self.executor:
            self.executor.shutdown(wait=False)


# Legacy alias for backward compatibility
ParallelProcessor = AdvancedParallelProcessor
