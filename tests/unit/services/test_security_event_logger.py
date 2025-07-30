"""Tests for security event logger service."""

import json
import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from app.services.security_event_logger import (
    SecurityEventLogger,
    SecurityEvent,
    SecurityEventType,
    SecurityEventSeverity,
    security_logger,
    log_auth_failure,
    log_malicious_request,
    log_rate_limit_exceeded,
    log_api_key_abuse,
    log_suspicious_activity,
    get_security_event_summary,
    is_system_under_attack,
)


class TestSecurityEvent:
    """Test SecurityEvent dataclass functionality."""
    
    def test_security_event_creation(self):
        """Test creating a security event."""
        timestamp = time.time()
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_FAILURE,
            severity=SecurityEventSeverity.MEDIUM,
            message="Test authentication failure",
            timestamp=timestamp,
            source_ip="127.0.0.1",
            endpoint="/api/auth/login",
            user_id="test_user"
        )
        
        assert event.event_type == SecurityEventType.AUTH_FAILURE
        assert event.severity == SecurityEventSeverity.MEDIUM
        assert event.message == "Test authentication failure"
        assert event.timestamp == timestamp
        assert event.source_ip == "127.0.0.1"
        assert event.endpoint == "/api/auth/login"
        assert event.user_id == "test_user"
    
    def test_security_event_to_dict(self):
        """Test converting security event to dictionary."""
        timestamp = time.time()
        event = SecurityEvent(
            event_type=SecurityEventType.MALICIOUS_REQUEST,
            severity=SecurityEventSeverity.HIGH,
            message="Test malicious request",
            timestamp=timestamp,
            source_ip="192.168.1.100",
            additional_data={"attack_type": "sql_injection"}
        )
        
        event_dict = event.to_dict()
        
        assert event_dict['event_type'] == 'malicious_request'
        assert event_dict['severity'] == 'high'
        assert event_dict['message'] == 'Test malicious request'
        assert event_dict['timestamp'] == timestamp
        assert event_dict['source_ip'] == '192.168.1.100'
        assert event_dict['additional_data'] == {"attack_type": "sql_injection"}
        assert 'iso_timestamp' in event_dict
    
    def test_iso_timestamp_property(self):
        """Test ISO timestamp property."""
        timestamp = 1643723400.0  # Fixed timestamp for testing
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_SUCCESS,
            severity=SecurityEventSeverity.LOW,
            message="Test message",
            timestamp=timestamp
        )
        
        iso_timestamp = event.iso_timestamp
        assert isinstance(iso_timestamp, str)
        assert "T" in iso_timestamp  # ISO format contains T separator


class TestSecurityEventLogger:
    """Test SecurityEventLogger functionality."""
    
    @pytest.fixture
    def logger_instance(self):
        """Create a fresh logger instance for testing."""
        return SecurityEventLogger()
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch('app.services.security_event_logger.get_settings') as mock:
            mock_settings = Mock()
            mock_settings.env = 'test'
            mock.return_value = mock_settings
            yield mock_settings
    
    def test_logger_initialization(self, mock_settings):
        """Test logger initialization."""
        logger = SecurityEventLogger()
        
        assert logger.settings is not None
        assert logger.logger is not None
        assert isinstance(logger.event_counters, dict)
        assert isinstance(logger.last_reset_time, float)
        assert len(logger.critical_events) > 0
    
    def test_log_event_info_level(self, logger_instance, caplog):
        """Test logging info level security event."""
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_SUCCESS,
            severity=SecurityEventSeverity.LOW,
            message="Successful authentication",
            timestamp=time.time(),
            source_ip="127.0.0.1"
        )
        
        logger_instance.log_event(event)
        
        # Check that event was logged
        assert len(caplog.records) > 0
        
        # Check event counter was incremented
        event_key = f"{event.event_type.value}_{event.severity.value}"
        assert logger_instance.event_counters[event_key] == 1
    
    def test_log_event_critical_level(self, logger_instance, caplog):
        """Test logging critical level security event."""
        event = SecurityEvent(
            event_type=SecurityEventType.INTRUSION_ATTEMPT,
            severity=SecurityEventSeverity.CRITICAL,
            message="Intrusion attempt detected",
            timestamp=time.time(),
            source_ip="192.168.1.100"
        )
        
        logger_instance.log_event(event)
        
        # Check that critical event was handled
        assert len(caplog.records) > 0
        
        # Check for critical-specific logging
        critical_logs = [record for record in caplog.records if record.levelname == 'CRITICAL']
        assert len(critical_logs) > 0
    
    def test_log_auth_failure(self, logger_instance, caplog):
        """Test logging authentication failure."""
        logger_instance.log_auth_failure(
            source_ip="127.0.0.1",
            endpoint="/api/auth/login",
            user_id="test_user",
            reason="Invalid password"
        )
        
        assert len(caplog.records) > 0
        
        # Check event counter
        event_key = f"{SecurityEventType.AUTH_FAILURE.value}_{SecurityEventSeverity.MEDIUM.value}"
        assert logger_instance.event_counters[event_key] == 1
    
    def test_log_malicious_request(self, logger_instance, caplog):
        """Test logging malicious request."""
        logger_instance.log_malicious_request(
            source_ip="192.168.1.100",
            endpoint="/api/users",
            method="POST",
            attack_type="sql_injection",
            payload_sample="'; DROP TABLE users; --"
        )
        
        assert len(caplog.records) > 0
        
        # Check event counter
        event_key = f"{SecurityEventType.MALICIOUS_REQUEST.value}_{SecurityEventSeverity.HIGH.value}"
        assert logger_instance.event_counters[event_key] == 1
    
    def test_log_rate_limit_exceeded(self, logger_instance, caplog):
        """Test logging rate limit exceeded."""
        logger_instance.log_rate_limit_exceeded(
            source_ip="127.0.0.1",
            endpoint="/api/content/generate",
            limit_type="requests",
            current_count=101,
            limit_value=100
        )
        
        assert len(caplog.records) > 0
        
        # Check event counter
        event_key = f"{SecurityEventType.RATE_LIMIT_EXCEEDED.value}_{SecurityEventSeverity.HIGH.value}"
        assert logger_instance.event_counters[event_key] == 1
    
    def test_log_api_key_abuse(self, logger_instance, caplog):
        """Test logging API key abuse."""
        logger_instance.log_api_key_abuse(
            api_key_id="key_123",
            source_ip="10.0.0.1",
            abuse_type="excessive_requests",
            requests_per_hour=1000
        )
        
        assert len(caplog.records) > 0
        
        # Check event counter and critical handling
        event_key = f"{SecurityEventType.API_KEY_ABUSE.value}_{SecurityEventSeverity.CRITICAL.value}"
        assert logger_instance.event_counters[event_key] == 1
        
        # Should trigger critical event handling
        critical_logs = [record for record in caplog.records if record.levelname == 'CRITICAL']
        assert len(critical_logs) > 0
    
    def test_log_suspicious_activity(self, logger_instance, caplog):
        """Test logging suspicious activity with different confidence scores."""
        # High confidence (high severity)
        logger_instance.log_suspicious_activity(
            source_ip="172.16.0.1",
            activity_type="unusual_access_pattern",
            confidence_score=0.9
        )
        
        # Medium confidence (medium severity)
        logger_instance.log_suspicious_activity(
            source_ip="172.16.0.2",
            activity_type="rapid_endpoint_scanning",
            confidence_score=0.6
        )
        
        # Low confidence (low severity)
        logger_instance.log_suspicious_activity(
            source_ip="172.16.0.3",
            activity_type="minor_anomaly",
            confidence_score=0.3
        )
        
        assert len(caplog.records) >= 3
        
        # Check different severity levels were used
        high_key = f"{SecurityEventType.SUSPICIOUS_ACTIVITY.value}_{SecurityEventSeverity.HIGH.value}"
        medium_key = f"{SecurityEventType.SUSPICIOUS_ACTIVITY.value}_{SecurityEventSeverity.MEDIUM.value}"
        low_key = f"{SecurityEventType.SUSPICIOUS_ACTIVITY.value}_{SecurityEventSeverity.LOW.value}"
        
        assert logger_instance.event_counters[high_key] == 1
        assert logger_instance.event_counters[medium_key] == 1
        assert logger_instance.event_counters[low_key] == 1
    
    def test_get_event_summary(self, logger_instance):
        """Test getting event summary."""
        # Log some events
        logger_instance.log_auth_failure("127.0.0.1", "/api/auth/login")
        logger_instance.log_malicious_request("127.0.0.1", "/api/users", "POST", attack_type="xss")
        logger_instance.log_auth_failure("127.0.0.1", "/api/auth/login")  # Second failure
        
        summary = logger_instance.get_event_summary()
        
        assert isinstance(summary, dict)
        assert len(summary) >= 2
        
        # Check specific counts
        auth_failure_key = f"{SecurityEventType.AUTH_FAILURE.value}_{SecurityEventSeverity.MEDIUM.value}"
        malicious_request_key = f"{SecurityEventType.MALICIOUS_REQUEST.value}_{SecurityEventSeverity.HIGH.value}"
        
        assert summary[auth_failure_key] == 2
        assert summary[malicious_request_key] == 1
    
    def test_is_under_attack(self, logger_instance):
        """Test attack detection."""
        # Initially not under attack
        assert not logger_instance.is_under_attack(threshold=5)
        
        # Log high severity events
        for i in range(6):
            logger_instance.log_malicious_request(
                f"192.168.1.{i}",
                "/api/test",
                "POST",
                attack_type="injection"
            )
        
        # Should now be considered under attack
        assert logger_instance.is_under_attack(threshold=5)
    
    def test_event_counter_reset(self, logger_instance):
        """Test event counter reset after time window."""
        # Log an event
        logger_instance.log_auth_failure("127.0.0.1", "/api/auth/login")
        assert len(logger_instance.event_counters) > 0
        
        # Simulate time passing
        logger_instance.last_reset_time = time.time() - 3700  # Over 1 hour ago
        
        # Get summary should reset counters
        summary = logger_instance.get_event_summary(time_window_minutes=60)
        
        # Counters should be reset
        assert len(summary) == 0
    
    def test_payload_truncation(self, logger_instance, caplog):
        """Test that long payloads are truncated in logs."""
        long_payload = "A" * 300  # Longer than 200 character limit
        
        logger_instance.log_malicious_request(
            source_ip="127.0.0.1",
            endpoint="/api/test",
            method="POST",
            payload_sample=long_payload
        )
        
        # Check that payload was truncated
        log_records = [record.message for record in caplog.records]
        log_data = json.loads(log_records[0])
        
        payload_in_log = log_data['additional_data']['payload_sample']
        assert len(payload_in_log) <= 203  # 200 chars + "..."
        assert payload_in_log.endswith("...")
    
    def test_exception_handling_in_log_event(self, logger_instance, caplog):
        """Test that exceptions in log_event are handled gracefully."""
        # Create an event that might cause issues
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_FAILURE,
            severity=SecurityEventSeverity.MEDIUM,
            message="Test message",
            timestamp=time.time()
        )
        
        # Mock the logger to raise an exception
        with patch.object(logger_instance.logger, 'info', side_effect=Exception("Test exception")):
            logger_instance.log_event(event)
        
        # Should have fallback error logs
        error_logs = [record for record in caplog.records if record.levelname == 'ERROR']
        assert len(error_logs) > 0


class TestConvenienceFunctions:
    """Test convenience functions for security logging."""
    
    def test_log_auth_failure_function(self, caplog):
        """Test global auth failure logging function."""
        log_auth_failure("127.0.0.1", "/api/auth/login", user_id="test_user")
        
        assert len(caplog.records) > 0
    
    def test_log_malicious_request_function(self, caplog):
        """Test global malicious request logging function."""
        log_malicious_request("127.0.0.1", "/api/test", "POST", attack_type="xss")
        
        assert len(caplog.records) > 0
    
    def test_log_rate_limit_exceeded_function(self, caplog):
        """Test global rate limit logging function."""
        log_rate_limit_exceeded("127.0.0.1", "/api/test", limit_type="requests")
        
        assert len(caplog.records) > 0
    
    def test_log_api_key_abuse_function(self, caplog):
        """Test global API key abuse logging function."""
        log_api_key_abuse("key_123", "127.0.0.1", "excessive_use")
        
        assert len(caplog.records) > 0
    
    def test_log_suspicious_activity_function(self, caplog):
        """Test global suspicious activity logging function."""
        log_suspicious_activity("127.0.0.1", "unusual_pattern", confidence_score=0.8)
        
        assert len(caplog.records) > 0
    
    def test_get_security_event_summary_function(self):
        """Test global event summary function."""
        # Log an event first
        log_auth_failure("127.0.0.1", "/api/auth/login")
        
        summary = get_security_event_summary()
        assert isinstance(summary, dict)
    
    def test_is_system_under_attack_function(self):
        """Test global attack detection function."""
        result = is_system_under_attack(threshold=10)
        assert isinstance(result, bool)


class TestSecurityEventEnums:
    """Test security event enums."""
    
    def test_security_event_type_enum(self):
        """Test SecurityEventType enum values."""
        assert SecurityEventType.AUTH_FAILURE.value == "auth_failure"
        assert SecurityEventType.MALICIOUS_REQUEST.value == "malicious_request"
        assert SecurityEventType.RATE_LIMIT_EXCEEDED.value == "rate_limit_exceeded"
        assert SecurityEventType.API_KEY_ABUSE.value == "api_key_abuse"
        assert SecurityEventType.INTRUSION_ATTEMPT.value == "intrusion_attempt"
    
    def test_security_event_severity_enum(self):
        """Test SecurityEventSeverity enum values."""
        assert SecurityEventSeverity.LOW.value == "low"
        assert SecurityEventSeverity.MEDIUM.value == "medium"
        assert SecurityEventSeverity.HIGH.value == "high"
        assert SecurityEventSeverity.CRITICAL.value == "critical"


class TestSecurityEventIntegration:
    """Integration tests for security event logging."""
    
    def test_multiple_event_types_logging(self, caplog):
        """Test logging multiple different event types."""
        # Clear any existing events
        security_logger.event_counters = {}
        
        # Log various types of events
        log_auth_failure("127.0.0.1", "/api/auth/login")
        log_malicious_request("192.168.1.1", "/api/users", "GET", attack_type="injection")
        log_rate_limit_exceeded("10.0.0.1", "/api/content", limit_type="requests")
        log_api_key_abuse("key_456", "172.16.0.1", "quota_exceeded")
        log_suspicious_activity("203.0.113.1", "port_scanning", confidence_score=0.7)
        
        # Check that all events were logged
        assert len(caplog.records) >= 5
        
        # Check event counters
        summary = get_security_event_summary()
        assert len(summary) >= 5
    
    def test_concurrent_event_logging(self, caplog):
        """Test that concurrent event logging works correctly."""
        import threading
        import time
        
        def log_events():
            for i in range(5):
                log_auth_failure(f"127.0.0.{i}", "/api/auth/login")
                time.sleep(0.01)  # Small delay to simulate real usage
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=log_events)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all events were logged
        summary = get_security_event_summary()
        auth_failure_key = f"{SecurityEventType.AUTH_FAILURE.value}_{SecurityEventSeverity.MEDIUM.value}"
        assert summary.get(auth_failure_key, 0) == 15  # 3 threads * 5 events each