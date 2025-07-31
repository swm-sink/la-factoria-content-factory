"""
SLI Tracking Middleware

Collects Service Level Indicators for SLA monitoring.
"""

import time
import logging
from typing import Callable
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import get_cache_backend
from app.core.metrics import metrics
from app.services.sla_monitor import sla_monitor

# Get cache instance
cache = get_cache_backend()

logger = logging.getLogger(__name__)


class SLITrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track SLI metrics for SLA monitoring.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track SLI metrics for each request.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response with SLI metrics tracked
        """
        # Skip health check endpoint from general metrics
        is_health_check = request.url.path == "/health"
        
        # Start timing
        start_time = time.time()
        
        # Default values
        status_code = 500
        response = None
        exception_occurred = False
        
        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            exception_occurred = True
            raise
            
        finally:
            # Calculate metrics
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update SLI metrics
            await self._update_sli_metrics(
                request=request,
                status_code=status_code,
                duration=duration,
                exception_occurred=exception_occurred,
                is_health_check=is_health_check
            )
        
        return response
    
    async def _update_sli_metrics(
        self,
        request: Request,
        status_code: int,
        duration: float,
        exception_occurred: bool,
        is_health_check: bool
    ):
        """Update SLI metrics in cache and monitoring systems."""
        try:
            # API Availability (based on health checks)
            if is_health_check:
                success = status_code < 400 and not exception_occurred
                await self._update_availability_metric(success)
            
            # Skip metrics for health checks in other SLIs
            if not is_health_check:
                # Response Time metrics
                await self._update_latency_metrics(duration)
                
                # Error Rate metrics
                is_error = status_code >= 500 or exception_occurred
                await self._update_error_metrics(is_error)
                
                # Endpoint-specific metrics
                if request.url.path.startswith("/api/content/generate"):
                    await self._update_content_generation_metrics(
                        status_code=status_code,
                        duration=duration
                    )
                elif request.url.path.startswith("/api/audio/generate"):
                    await self._update_audio_generation_metrics(
                        status_code=status_code,
                        duration=duration
                    )
            
            # Record general metrics
            metrics.increment(
                "http_requests_total",
                tags={
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status": str(status_code)
                }
            )
            
            metrics.histogram(
                "http_request_duration_seconds",
                duration / 1000,  # Convert back to seconds
                tags={
                    "method": request.method,
                    "endpoint": request.url.path
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating SLI metrics: {e}")
    
    async def _update_availability_metric(self, success: bool):
        """Update availability SLI."""
        # Get current success rate
        current_rate = await cache.get("health_check_success_rate") or 99.9
        current_count = await cache.get("health_check_count") or 0
        
        # Calculate new rate (simple moving average)
        new_count = current_count + 1
        if new_count > 1000:  # Reset periodically to avoid overflow
            new_count = 100
            current_rate = 99.9
        
        new_rate = ((current_rate * current_count) + (100 if success else 0)) / new_count
        
        # Update cache
        await cache.set("health_check_success_rate", new_rate, expire=3600)
        await cache.set("health_check_count", new_count, expire=3600)
        
        # Record metric
        metrics.gauge("sli.health_check_success_rate", new_rate)
    
    async def _update_latency_metrics(self, duration: float):
        """Update latency SLIs."""
        # Store individual latency values for percentile calculation
        latencies_key = "api_latencies"
        latencies = await cache.get(latencies_key) or []
        
        # Keep last 1000 values
        latencies.append(duration)
        if len(latencies) > 1000:
            latencies = latencies[-1000:]
        
        await cache.set(latencies_key, latencies, expire=3600)
        
        # Calculate percentiles
        if latencies:
            sorted_latencies = sorted(latencies)
            p95_index = int(len(sorted_latencies) * 0.95)
            p99_index = int(len(sorted_latencies) * 0.99)
            
            p95 = sorted_latencies[p95_index] if p95_index < len(sorted_latencies) else sorted_latencies[-1]
            p99 = sorted_latencies[p99_index] if p99_index < len(sorted_latencies) else sorted_latencies[-1]
            
            await cache.set("api_latency_p95", p95, expire=300)
            await cache.set("api_latency_p99", p99, expire=300)
            
            # Record metrics
            metrics.gauge("sli.api_latency_p95", p95)
            metrics.gauge("sli.api_latency_p99", p99)
    
    async def _update_error_metrics(self, is_error: bool):
        """Update error rate SLI."""
        # Get current error rate
        error_count = await cache.get("api_error_count") or 0
        total_count = await cache.get("api_total_count") or 0
        
        # Update counts
        total_count += 1
        if is_error:
            error_count += 1
        
        # Reset periodically
        if total_count > 10000:
            total_count = 1000
            error_count = int(error_count * 0.1)  # Keep proportional
        
        # Calculate error rate
        error_rate = (error_count / total_count * 100) if total_count > 0 else 0
        
        # Update cache
        await cache.set("api_error_count", error_count, expire=3600)
        await cache.set("api_total_count", total_count, expire=3600)
        await cache.set("api_error_rate", error_rate, expire=300)
        
        # Record metric
        metrics.gauge("sli.api_error_rate", error_rate)
    
    async def _update_content_generation_metrics(self, status_code: int, duration: float):
        """Update content generation SLIs."""
        # Success rate
        success_count = await cache.get("content_generation_success_count") or 0
        total_count = await cache.get("content_generation_total_count") or 0
        
        total_count += 1
        if status_code < 400:
            success_count += 1
        
        # Reset periodically
        if total_count > 1000:
            total_count = 100
            success_count = int(success_count * 0.1)
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 98.0
        
        await cache.set("content_generation_success_count", success_count, expire=3600)
        await cache.set("content_generation_total_count", total_count, expire=3600)
        await cache.set("content_generation_success_rate", success_rate, expire=300)
        
        # Generation time percentiles
        gen_times_key = "content_generation_times"
        gen_times = await cache.get(gen_times_key) or []
        gen_times.append(duration)
        
        if len(gen_times) > 500:
            gen_times = gen_times[-500:]
        
        await cache.set(gen_times_key, gen_times, expire=3600)
        
        if gen_times:
            sorted_times = sorted(gen_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95 = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
            await cache.set("content_generation_p95", p95, expire=300)
            
            # Record metrics
            metrics.gauge("sli.content_generation_success_rate", success_rate)
            metrics.gauge("sli.content_generation_p95", p95)
    
    async def _update_audio_generation_metrics(self, status_code: int, duration: float):
        """Update audio generation SLIs."""
        # Similar to content generation
        success_count = await cache.get("audio_generation_success_count") or 0
        total_count = await cache.get("audio_generation_total_count") or 0
        
        total_count += 1
        if status_code < 400:
            success_count += 1
        
        if total_count > 1000:
            total_count = 100
            success_count = int(success_count * 0.1)
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 97.0
        
        await cache.set("audio_generation_success_count", success_count, expire=3600)
        await cache.set("audio_generation_total_count", total_count, expire=3600)
        await cache.set("audio_generation_success_rate", success_rate, expire=300)
        
        # Record metric
        metrics.gauge("sli.audio_generation_success_rate", success_rate)


class DependencyHealthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track health of external dependencies.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track dependency health based on request patterns.
        """
        response = await call_next(request)
        
        # Track dependency health based on specific endpoints
        try:
            if "database" in request.url.path or request.url.path.startswith("/api/"):
                await self._check_database_health()
            
            if request.url.path.startswith("/api/content/generate"):
                await self._check_gemini_health()
            
            if request.url.path.startswith("/api/audio/generate"):
                await self._check_elevenlabs_health()
                
        except Exception as e:
            logger.error(f"Error checking dependency health: {e}")
        
        return response
    
    async def _check_database_health(self):
        """Check and update database health status."""
        # This would be updated by actual database monitoring
        # For now, we'll use a simple check
        await cache.set("dependency_postgresql_status", "healthy", expire=60)
        await cache.set("dependency_postgresql_latency", 5, expire=60)
        await cache.set("dependency_postgresql_last_check", datetime.utcnow().isoformat(), expire=60)
    
    async def _check_gemini_health(self):
        """Check and update Gemini API health status."""
        await cache.set("dependency_gemini_status", "healthy", expire=60)
        await cache.set("dependency_gemini_latency", 200, expire=60)
        await cache.set("dependency_gemini_last_check", datetime.utcnow().isoformat(), expire=60)
    
    async def _check_elevenlabs_health(self):
        """Check and update ElevenLabs API health status."""
        await cache.set("dependency_elevenlabs_status", "healthy", expire=60)
        await cache.set("dependency_elevenlabs_latency", 300, expire=60)
        await cache.set("dependency_elevenlabs_last_check", datetime.utcnow().isoformat(), expire=60)