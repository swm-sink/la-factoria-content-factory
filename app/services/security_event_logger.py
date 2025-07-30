"""Security event logging service for comprehensive security monitoring."""

import json
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

from app.core.config.settings import get_settings


class SecurityEventType(Enum):
    """Types of security events that can be logged."""
    
    # Authentication events
    AUTH_FAILURE = "auth_failure"
    AUTH_SUCCESS = "auth_success"
    API_KEY_INVALID = "api_key_invalid"
    API_KEY_EXPIRED = "api_key_expired"
    API_KEY_ABUSE = "api_key_abuse"
    
    # Request validation events
    MALICIOUS_REQUEST = "malicious_request"
    REQUEST_TOO_LARGE = "request_too_large"
    MALICIOUS_USER_AGENT = "malicious_user_agent"
    MALICIOUS_QUERY = "malicious_query"
    MALICIOUS_CONTENT = "malicious_content"
    
    # Rate limiting events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    RATE_LIMIT_WARNING = "rate_limit_warning"
    
    # Access control events
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FORBIDDEN_RESOURCE = "forbidden_resource"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    
    # System events
    SECURITY_SCAN_DETECTED = "security_scan_detected"
    INTRUSION_ATTEMPT = "intrusion_attempt"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # Configuration events
    CONFIG_CHANGE = "config_change"
    SECURITY_POLICY_VIOLATION = "security_policy_violation"


class SecurityEventSeverity(Enum):
    """Severity levels for security events."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Structure for security events."""
    
    event_type: SecurityEventType
    severity: SecurityEventSeverity
    message: str
    timestamp: float
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    @property
    def iso_timestamp(self) -> str:
        """Get timestamp in ISO format."""
        return datetime.fromtimestamp(self.timestamp).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['iso_timestamp'] = self.iso_timestamp
        return data


class SecurityEventLogger:
    """Centralized security event logging service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(f"{__name__}.security_events")
        
        # Configure security-specific logger
        self._setup_security_logger()
        
        # Event counters for rate limiting and monitoring
        self.event_counters: Dict[str, int] = {}
        self.last_reset_time = time.time()
        
        # High-priority events that require immediate attention
        self.critical_events = {
            SecurityEventType.INTRUSION_ATTEMPT,
            SecurityEventType.DATA_BREACH_ATTEMPT,
            SecurityEventType.PRIVILEGE_ESCALATION,
            SecurityEventType.API_KEY_ABUSE,
            SecurityEventType.SECURITY_SCAN_DETECTED,
        }
    
    def _setup_security_logger(self):
        """Set up security-specific logger configuration."""
        # Add custom formatter for security events
        security_formatter = logging.Formatter(
            '%(asctime)s [SECURITY] %(levelname)s %(name)s - %(message)s'
        )
        
        # Create handler for security events
        security_handler = logging.StreamHandler()
        security_handler.setFormatter(security_formatter)
        
        self.logger.addHandler(security_handler)
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate logging in parent loggers
        self.logger.propagate = False
    
    def log_event(self, event: SecurityEvent) -> None:
        """Log a security event with appropriate handling based on severity."""
        try:
            # Increment event counter
            event_key = f"{event.event_type.value}_{event.severity.value}"
            self.event_counters[event_key] = self.event_counters.get(event_key, 0) + 1
            
            # Convert to structured data
            event_data = event.to_dict()
            
            # Add metadata
            event_data.update({
                'logger_name': self.logger.name,
                'event_counter': self.event_counters[event_key],
                'environment': getattr(self.settings, 'env', 'unknown'),
            })
            
            # Log based on severity
            if event.severity == SecurityEventSeverity.CRITICAL:
                self.logger.critical(json.dumps(event_data))
                self._handle_critical_event(event)
            elif event.severity == SecurityEventSeverity.HIGH:
                self.logger.error(json.dumps(event_data))
                self._handle_high_severity_event(event)
            elif event.severity == SecurityEventSeverity.MEDIUM:
                self.logger.warning(json.dumps(event_data))
            else:
                self.logger.info(json.dumps(event_data))
            
            # Store for analytics if needed (avoid logging sensitive data)
            self._store_for_analytics(event_data)
            
        except Exception as e:
            # Fallback logging to prevent security event loss
            self.logger.error(f"Failed to log security event: {e}")
            self.logger.error(f"Original event: {event}")
    
    def _handle_critical_event(self, event: SecurityEvent) -> None:
        """Handle critical security events that require immediate action."""
        # In production, this could:
        # - Send alerts to security team
        # - Trigger automated responses
        # - Escalate to incident management system
        
        self.logger.critical(f"CRITICAL SECURITY EVENT: {event.message}")
        
        # For demonstration, we'll just log additional context
        if event.event_type in self.critical_events:
            self.logger.critical(
                f"Event type {event.event_type.value} requires immediate attention. "
                f"Source: {event.source_ip}, Endpoint: {event.endpoint}"
            )
    
    def _handle_high_severity_event(self, event: SecurityEvent) -> None:
        """Handle high severity events."""
        # Could trigger automated defensive measures
        if event.event_type == SecurityEventType.RATE_LIMIT_EXCEEDED:
            self.logger.error(f"Rate limit exceeded from {event.source_ip}")
        elif event.event_type == SecurityEventType.MALICIOUS_REQUEST:
            self.logger.error(f"Malicious request blocked from {event.source_ip}")
    
    def _store_for_analytics(self, event_data: Dict[str, Any]) -> None:
        """Store event data for security analytics and reporting."""
        # In production, this could store events in:
        # - Time-series database for metrics
        # - SIEM system for correlation
        # - Data warehouse for reporting
        
        # For now, we'll just ensure the data is properly formatted
        pass
    
    def _safe_decode_payload(self, payload: bytes) -> str:
        """Safely decode payload avoiding sensitive data exposure."""
        try:
            # Decode with error handling  
            # avoid logging sensitive data
            return payload.decode('utf-8', errors='ignore')[:200]
        except Exception:
            return "Unable to decode payload"
    
    def log_auth_failure(
        self,
        source_ip: str,
        endpoint: str,
        user_id: Optional[str] = None,
        reason: str = "Invalid credentials",
        **kwargs
    ) -> None:
        """Log authentication failure event."""
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_FAILURE,
            severity=SecurityEventSeverity.MEDIUM,
            message=f"Authentication failed: {reason}",
            timestamp=time.time(),
            source_ip=source_ip,
            endpoint=endpoint,
            user_id=user_id,
            additional_data=kwargs
        )
        self.log_event(event)
    
    def log_malicious_request(
        self,
        source_ip: str,
        endpoint: str,
        method: str,
        attack_type: str = "unknown",
        payload_sample: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log malicious request event."""
        additional_data = kwargs.copy()
        if payload_sample:
            # Truncate payload for logging (avoid logging sensitive data)
            additional_data['payload_sample'] = payload_sample[:200] + "..." if len(payload_sample) > 200 else payload_sample
        
        event = SecurityEvent(
            event_type=SecurityEventType.MALICIOUS_REQUEST,
            severity=SecurityEventSeverity.HIGH,
            message=f"Malicious request blocked: {attack_type}",
            timestamp=time.time(),
            source_ip=source_ip,
            endpoint=endpoint,
            method=method,
            additional_data=additional_data
        )
        self.log_event(event)
    
    def log_rate_limit_exceeded(
        self,
        source_ip: str,
        endpoint: str,
        limit_type: str = "requests",
        current_count: Optional[int] = None,
        limit_value: Optional[int] = None,
        **kwargs
    ) -> None:
        """Log rate limit exceeded event."""
        additional_data = kwargs.copy()
        additional_data.update({
            'limit_type': limit_type,
            'current_count': current_count,
            'limit_value': limit_value,
            # Truncate any user agent in additional data to avoid logging sensitive data
            'user_agent_sample': kwargs.get('user_agent', '')[:100] if 'user_agent' in kwargs else None,
        })
        
        event = SecurityEvent(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            severity=SecurityEventSeverity.HIGH,  
            message=f"Rate limit exceeded for {limit_type}",
            timestamp=time.time(),
            source_ip=source_ip,
            endpoint=endpoint,
            additional_data=additional_data
        )
        self.log_event(event)
    
    def log_api_key_abuse(
        self,
        api_key_id: str,
        source_ip: str,
        abuse_type: str,
        **kwargs
    ) -> None:
        """Log API key abuse event."""
        event = SecurityEvent(
            event_type=SecurityEventType.API_KEY_ABUSE,
            severity=SecurityEventSeverity.CRITICAL,
            message=f"API key abuse detected: {abuse_type}",
            timestamp=time.time(),
            source_ip=source_ip,
            api_key_id=api_key_id,
            additional_data=kwargs
        )
        self.log_event(event)
    
    def log_suspicious_activity(
        self,
        source_ip: str,
        activity_type: str,
        confidence_score: float = 0.0,
        **kwargs
    ) -> None:
        """Log suspicious activity event."""
        # Determine severity based on confidence score
        if confidence_score >= 0.8:
            severity = SecurityEventSeverity.HIGH
        elif confidence_score >= 0.5:
            severity = SecurityEventSeverity.MEDIUM
        else:
            severity = SecurityEventSeverity.LOW
        
        additional_data = kwargs.copy()
        additional_data['confidence_score'] = confidence_score
        
        event = SecurityEvent(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            severity=severity,
            message=f"Suspicious activity detected: {activity_type}",
            timestamp=time.time(),
            source_ip=source_ip,
            additional_data=additional_data
        )
        self.log_event(event)
    
    def get_event_summary(self, time_window_minutes: int = 60) -> Dict[str, int]:
        """Get summary of events in the specified time window."""
        # Reset counters if needed (simple implementation)
        current_time = time.time()
        if current_time - self.last_reset_time > time_window_minutes * 60:
            self.event_counters = {}
            self.last_reset_time = current_time
        
        return self.event_counters.copy()
    
    def is_under_attack(self, threshold: int = 10, time_window_minutes: int = 5) -> bool:
        """Determine if the system is potentially under attack."""
        high_severity_events = sum(
            count for key, count in self.event_counters.items()
            if ('high' in key.lower() or 'critical' in key.lower())
        )
        
        return high_severity_events >= threshold


# Global security event logger instance
security_logger = SecurityEventLogger()


# Convenience functions for common security events
def log_auth_failure(source_ip: str, endpoint: str, **kwargs) -> None:
    """Convenience function to log authentication failures."""
    security_logger.log_auth_failure(source_ip, endpoint, **kwargs)


def log_malicious_request(source_ip: str, endpoint: str, method: str, **kwargs) -> None:
    """Convenience function to log malicious requests."""
    security_logger.log_malicious_request(source_ip, endpoint, method, **kwargs)


def log_rate_limit_exceeded(source_ip: str, endpoint: str, **kwargs) -> None:
    """Convenience function to log rate limit exceeded events."""
    security_logger.log_rate_limit_exceeded(source_ip, endpoint, **kwargs)


def log_api_key_abuse(api_key_id: str, source_ip: str, abuse_type: str, **kwargs) -> None:
    """Convenience function to log API key abuse."""
    security_logger.log_api_key_abuse(api_key_id, source_ip, abuse_type, **kwargs)


def log_suspicious_activity(source_ip: str, activity_type: str, **kwargs) -> None:
    """Convenience function to log suspicious activity."""
    security_logger.log_suspicious_activity(source_ip, activity_type, **kwargs)


def get_security_event_summary(time_window_minutes: int = 60) -> Dict[str, int]:
    """Get summary of security events."""
    return security_logger.get_event_summary(time_window_minutes)


def is_system_under_attack(threshold: int = 10) -> bool:
    """Check if system is potentially under attack."""
    return security_logger.is_under_attack(threshold)