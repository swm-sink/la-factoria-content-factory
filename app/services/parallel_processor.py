"""
Parallel processing service for concurrent content generation.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from prometheus_client import Histogram, Counter

# Prometheus metrics
PARALLEL_EXECUTION_TIME = Histogram(
    'parallel_execution_duration_seconds',
    'Time spent on parallel execution'
)
PARALLEL_TASKS_COMPLETED = Counter(
    'parallel_tasks_completed_total',
    'Total parallel tasks completed'
)
PARALLEL_TASKS_FAILED = Counter(
    'parallel_tasks_failed_total',
    'Total parallel tasks failed'
)

@dataclass
class TaskResult:
    """Result of a parallel task execution."""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0

class ParallelProcessor:
    """Service for executing content generation tasks in parallel."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the parallel processor.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
    
    def execute_parallel_tasks(
        self,
        tasks: List[Callable],
        task_ids: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> List[TaskResult]:
        """
        Execute multiple tasks in parallel using ThreadPoolExecutor.
        
        Args:
            tasks: List of callable tasks to execute
            task_ids: List of task identifiers
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of TaskResult objects
        """
        if len(tasks) != len(task_ids):
            raise ValueError("Number of tasks must match number of task IDs")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_task_with_timing, task, task_id): task_id
                for task, task_id in zip(tasks, task_ids)
            }
            
            completed_count = 0
            total_tasks = len(tasks)
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        PARALLEL_TASKS_COMPLETED.inc()
                    else:
                        PARALLEL_TASKS_FAILED.inc()
                    
                    completed_count += 1
                    
                    # Update progress
                    if progress_callback:
                        progress = (completed_count / total_tasks) * 100
                        progress_callback(task_id, progress)
                    
                    self.logger.info(f"Task {task_id} completed: {result.success}")
                    
                except Exception as e:
                    error_result = TaskResult(
                        task_id=task_id,
                        success=False,
                        error=str(e)
                    )
                    results.append(error_result)
                    PARALLEL_TASKS_FAILED.inc()
                    
                    self.logger.error(f"Task {task_id} failed: {str(e)}")
        
        return results
    
    def _execute_task_with_timing(self, task: Callable, task_id: str) -> TaskResult:
        """Execute a single task with timing measurement."""
        import time
        
        start_time = time.time()
        
        try:
            with PARALLEL_EXECUTION_TIME.time():
                result = task()
            
            execution_time = time.time() - start_time
            
            return TaskResult(
                task_id=task_id,
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return TaskResult(
                task_id=task_id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def execute_async_tasks(
        self,
        async_tasks: List[Awaitable],
        task_ids: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> List[TaskResult]:
        """
        Execute multiple async tasks concurrently.
        
        Args:
            async_tasks: List of awaitable tasks
            task_ids: List of task identifiers
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of TaskResult objects
        """
        if len(async_tasks) != len(task_ids):
            raise ValueError("Number of tasks must match number of task IDs")
        
        results = []
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def execute_with_semaphore(task: Awaitable, task_id: str) -> TaskResult:
            """Execute task with semaphore to limit concurrency."""
            async with semaphore:
                return await self._execute_async_task_with_timing(task, task_id)
        
        # Create tasks with semaphore
        limited_tasks = [
            execute_with_semaphore(task, task_id)
            for task, task_id in zip(async_tasks, task_ids)
        ]
        
        completed_count = 0
        total_tasks = len(async_tasks)
        
        # Execute all tasks concurrently
        for coro in asyncio.as_completed(limited_tasks):
            result = await coro
            results.append(result)
            
            if result.success:
                PARALLEL_TASKS_COMPLETED.inc()
            else:
                PARALLEL_TASKS_FAILED.inc()
            
            completed_count += 1
            
            # Update progress
            if progress_callback:
                progress = (completed_count / total_tasks) * 100
                progress_callback(result.task_id, progress)
            
            self.logger.info(f"Async task {result.task_id} completed: {result.success}")
        
        return results
    
    async def _execute_async_task_with_timing(
        self,
        task: Awaitable,
        task_id: str
    ) -> TaskResult:
        """Execute a single async task with timing measurement."""
        import time
        
        start_time = time.time()
        
        try:
            result = await task
            execution_time = time.time() - start_time
            
            return TaskResult(
                task_id=task_id,
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return TaskResult(
                task_id=task_id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def batch_process(
        self,
        items: List[Any],
        processor_func: Callable[[Any], Any],
        batch_size: int = None
    ) -> List[TaskResult]:
        """
        Process items in batches with parallel execution.
        
        Args:
            items: List of items to process
            processor_func: Function to process each item
            batch_size: Size of each batch (defaults to max_workers)
            
        Returns:
            List of TaskResult objects
        """
        if batch_size is None:
            batch_size = self.max_workers
        
        all_results = []
        
        # Process items in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Create tasks for this batch
            tasks = [lambda item=item: processor_func(item) for item in batch]
            task_ids = [f"batch_{i//batch_size}_item_{j}" for j in range(len(batch))]
            
            # Execute batch in parallel
            batch_results = self.execute_parallel_tasks(tasks, task_ids)
            all_results.extend(batch_results)
            
            self.logger.info(f"Completed batch {i//batch_size + 1}")
        
        return all_results
    
    def get_optimal_worker_count(self, task_count: int) -> int:
        """
        Get optimal number of workers for a given task count.
        
        Args:
            task_count: Number of tasks to execute
            
        Returns:
            Optimal worker count
        """
        # Don't use more workers than tasks
        if task_count < self.max_workers:
            return task_count
        
        # For small task counts, use fewer workers to reduce overhead
        if task_count < 10:
            return min(task_count, 2)
        
        return self.max_workers 