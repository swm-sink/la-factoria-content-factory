"""
Structured logging service for enhanced monitoring and debugging.
Provides consistent log formatting, correlation IDs, and integration with monitoring systems.
"""

import json
import logging
import sys
import time
import traceback
from contextvars import ContextVar
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union

from pythonjsonlogger import jsonlogger


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventType(Enum):
    """Event type enumeration for categorizing logs."""
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    CONTENT_GENERATION = "content_generation"
    VALIDATION = "validation"
    ERROR = "error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS_METRIC = "business_metric"


# Context variables for request tracking
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
session_id: ContextVar[Optional[str]] = ContextVar('session_id', default=None)


class StructuredLogger:
    """
    Structured logger with enhanced context and monitoring integration.
    """
    
    def __init__(self, name: str = __name__, level: LogLevel = LogLevel.INFO):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            level: Log level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Clear existing handlers to avoid duplication
        self.logger.handlers.clear()
        
        # Create structured formatter
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
        )
        
        # Console handler with structured format
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False
    
    def _build_log_context(self, extra_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build log context with correlation IDs and metadata.
        
        Args:
            extra_context: Additional context to include
            
        Returns:
            Complete log context dictionary
        """
        context = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'correlation_id': correlation_id.get(),
            'user_id': user_id.get(),
            'session_id': session_id.get(),
            'service': 'tikal-content-generator',
            'version': '1.0.0',  # Could be loaded from config
        }
        
        if extra_context:
            context.update(extra_context)
        
        # Remove None values
        return {k: v for k, v in context.items() if v is not None}
    
    def log_event(
        self,
        level: LogLevel,
        event_type: EventType,
        message: str,
        **kwargs
    ):
        """
        Log a structured event.
        
        Args:
            level: Log level
            event_type: Type of event
            message: Log message
            **kwargs: Additional context data
        """
        context = self._build_log_context({
            'event_type': event_type.value,
            **kwargs
        })
        
        log_method = getattr(self.logger, level.value.lower())
        log_method(message, extra=context)
    
    def log_request_start(
        self,
        method: str,
        path: str,
        user_agent: str = None,
        client_ip: str = None,
        **kwargs
    ):
        """
        Log request start event.
        
        Args:
            method: HTTP method
            path: Request path
            user_agent: User agent string
            client_ip: Client IP address
            **kwargs: Additional context
        """
        self.log_event(
            LogLevel.INFO,
            EventType.REQUEST_START,
            f"Request started: {method} {path}",
            http_method=method,
            path=path,
            user_agent=user_agent,
            client_ip=client_ip,
            **kwargs
        )
    
    def log_request_end(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ):
        """
        Log request end event.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
            **kwargs: Additional context
        """
        self.log_event(
            LogLevel.INFO,
            EventType.REQUEST_END,
            f"Request completed: {method} {path} - {status_code} ({duration_ms:.2f}ms)",
            http_method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            success=200 <= status_code < 300,
            **kwargs
        )
    
    def log_content_generation(
        self,
        job_id: str,
        target_format: str,
        status: str,
        duration_ms: float = None,
        tokens_used: int = None,
        ai_model: str = None,
        **kwargs
    ):
        """
        Log content generation event.
        
        Args:
            job_id: Job identifier
            target_format: Target content format
            status: Generation status (started, completed, failed)
            duration_ms: Generation duration in milliseconds
            tokens_used: Number of AI tokens consumed
            ai_model: AI model used
            **kwargs: Additional context
        """
        self.log_event(
            LogLevel.INFO,
            EventType.CONTENT_GENERATION,
            f"Content generation {status}: {job_id}",
            job_id=job_id,
            target_format=target_format,
            status=status,
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            ai_model=ai_model,
            **kwargs
        )
    
    def log_validation_result(
        self,
        job_id: str,
        is_valid: bool,
        validation_score: float,
        error_count: int = 0,
        warning_count: int = 0,
        duration_ms: float = None,
        **kwargs
    ):
        """
        Log validation result event.
        
        Args:
            job_id: Job identifier
            is_valid: Whether content passed validation
            validation_score: Overall validation score
            error_count: Number of validation errors
            warning_count: Number of validation warnings
            duration_ms: Validation duration in milliseconds
            **kwargs: Additional context
        """
        self.log_event(
            LogLevel.INFO if is_valid else LogLevel.WARNING,
            EventType.VALIDATION,
            f"Content validation {'passed' if is_valid else 'failed'}: {job_id}",
            job_id=job_id,
            is_valid=is_valid,
            validation_score=validation_score,
            error_count=error_count,
            warning_count=warning_count,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_error(
        self,
        error: Exception,
        context: str = None,
        **kwargs
    ):
        """
        Log error with full context and stack trace.
        
        Args:
            error: Exception that occurred
            context: Additional context about when/where error occurred
            **kwargs: Additional context data
        """
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            'context': context,
            **kwargs
        }
        
        self.log_event(
            LogLevel.ERROR,
            EventType.ERROR,
            f"Error occurred: {type(error).__name__}: {str(error)}",
            **error_context
        )
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        unit: str = None,
        tags: Dict[str, str] = None,
        **kwargs
    ):
        """
        Log performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Metric tags for grouping/filtering
            **kwargs: Additional context
        """
        self.log_event(
            LogLevel.INFO,
            EventType.PERFORMANCE,
            f"Performance metric: {metric_name} = {value} {unit or ''}",
            metric_name=metric_name,
            metric_value=value,
            metric_unit=unit,
            metric_tags=tags or {},
            **kwargs
        )
    
    def log_business_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        user_id: str = None,
        **kwargs
    ):
        """
        Log business metric for analytics.
        
        Args:
            metric_name: Name of the business metric
            value: Metric value
            user_id: User associated with the metric
            **kwargs: Additional context
        """
        self.log_event(
            LogLevel.INFO,
            EventType.BUSINESS_METRIC,
            f"Business metric: {metric_name} = {value}",
            metric_name=metric_name,
            metric_value=value,
            business_user_id=user_id,
            **kwargs
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        source_ip: str = None,
        user_id: str = None,
        **kwargs
    ):
        """
        Log security-related event.
        
        Args:
            event_type: Type of security event
            severity: Event severity (low, medium, high, critical)
            description: Event description
            source_ip: Source IP address
            user_id: User ID involved
            **kwargs: Additional context
        """
        level = LogLevel.WARNING if severity in ['low', 'medium'] else LogLevel.ERROR
        
        self.log_event(
            level,
            EventType.SECURITY,
            f"Security event: {event_type} - {description}",
            security_event_type=event_type,
            severity=severity,
            description=description,
            source_ip=source_ip,
            affected_user_id=user_id,
            **kwargs
        )


class LoggingContextManager:
    """Context manager for setting logging context variables."""
    
    def __init__(
        self,
        correlation_id_value: str = None,
        user_id_value: str = None,
        session_id_value: str = None
    ):
        """
        Initialize context manager.
        
        Args:
            correlation_id_value: Correlation ID to set
            user_id_value: User ID to set
            session_id_value: Session ID to set
        """
        self.correlation_id_value = correlation_id_value
        self.user_id_value = user_id_value
        self.session_id_value = session_id_value
        self.tokens = []
    
    def __enter__(self):
        """Enter context and set variables."""
        if self.correlation_id_value:
            self.tokens.append(correlation_id.set(self.correlation_id_value))
        if self.user_id_value:
            self.tokens.append(user_id.set(self.user_id_value))
        if self.session_id_value:
            self.tokens.append(session_id.set(self.session_id_value))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and reset variables."""
        for token in reversed(self.tokens):
            token.var.set(token.old_value)


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, logger: StructuredLogger, operation_name: str, **context):
        """
        Initialize performance timer.
        
        Args:
            logger: Structured logger instance
            operation_name: Name of the operation being timed
            **context: Additional context to log
        """
        self.logger = logger
        self.operation_name = operation_name
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        self.logger.log_event(
            LogLevel.DEBUG,
            EventType.PERFORMANCE,
            f"Started operation: {self.operation_name}",
            operation=self.operation_name,
            **self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log duration."""
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            
            level = LogLevel.INFO
            if exc_type:
                level = LogLevel.ERROR
            
            self.logger.log_event(
                level,
                EventType.PERFORMANCE,
                f"Completed operation: {self.operation_name} ({duration_ms:.2f}ms)",
                operation=self.operation_name,
                duration_ms=duration_ms,
                success=exc_type is None,
                **self.context
            )


# Global logger instance
_global_logger: Optional[StructuredLogger] = None


def get_logger(name: str = __name__) -> StructuredLogger:
    """
    Get or create a structured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        StructuredLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(name)
    return _global_logger


def set_correlation_context(
    correlation_id_value: str = None,
    user_id_value: str = None,
    session_id_value: str = None
) -> LoggingContextManager:
    """
    Create a context manager for setting logging context.
    
    Args:
        correlation_id_value: Correlation ID
        user_id_value: User ID
        session_id_value: Session ID
        
    Returns:
        LoggingContextManager instance
    """
    return LoggingContextManager(
        correlation_id_value=correlation_id_value,
        user_id_value=user_id_value,
        session_id_value=session_id_value
    )


def time_operation(
    operation_name: str,
    logger: StructuredLogger = None,
    **context
) -> PerformanceTimer:
    """
    Create a performance timer context manager.
    
    Args:
        operation_name: Name of the operation
        logger: Logger to use (defaults to global logger)
        **context: Additional context
        
    Returns:
        PerformanceTimer instance
    """
    if logger is None:
        logger = get_logger()
    
    return PerformanceTimer(logger, operation_name, **context)