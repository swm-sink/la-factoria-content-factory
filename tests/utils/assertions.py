"""
Custom assertions for La Factoria test suite
"""

from typing import Any, Dict, List, Optional, Union
import json
import re
from datetime import datetime


def assert_valid_uuid(value: str, message: str = "Invalid UUID format"):
    """Assert that a string is a valid UUID"""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    assert uuid_pattern.match(value), f"{message}: {value}"


def assert_valid_email(email: str, message: str = "Invalid email format"):
    """Assert that a string is a valid email"""
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    assert email_pattern.match(email), f"{message}: {email}"


def assert_valid_api_key(api_key: str, message: str = "Invalid API key format"):
    """Assert that a string is a valid API key"""
    assert len(api_key) >= 20, f"API key too short: {len(api_key)} < 20"
    assert len(api_key) <= 256, f"API key too long: {len(api_key)} > 256"
    assert re.match(r'^[A-Za-z0-9_\-\.]+$', api_key), f"{message}: {api_key}"


def assert_valid_json(data: Union[str, Dict], message: str = "Invalid JSON"):
    """Assert that data is valid JSON"""
    if isinstance(data, str):
        try:
            json.loads(data)
        except json.JSONDecodeError as e:
            raise AssertionError(f"{message}: {e}")
    elif isinstance(data, dict):
        try:
            json.dumps(data)
        except (TypeError, ValueError) as e:
            raise AssertionError(f"{message}: {e}")
    else:
        raise AssertionError(f"{message}: Expected str or dict, got {type(data)}")


def assert_quality_score_valid(score: float, message: str = "Invalid quality score"):
    """Assert that a quality score is valid (0.0 to 1.0)"""
    assert isinstance(score, (int, float)), f"{message}: Expected number, got {type(score)}"
    assert 0.0 <= score <= 1.0, f"{message}: {score} not in range [0.0, 1.0]"


def assert_content_structure(
    content: Dict[str, Any],
    required_fields: List[str],
    message: str = "Invalid content structure"
):
    """Assert that content has required structure"""
    assert isinstance(content, dict), f"{message}: Expected dict, got {type(content)}"
    
    missing_fields = [field for field in required_fields if field not in content]
    assert not missing_fields, f"{message}: Missing fields: {missing_fields}"


def assert_response_time(
    response_time: float,
    max_time: float = 0.2,
    message: str = "Response time exceeded"
):
    """Assert that response time is within acceptable limits"""
    assert isinstance(response_time, (int, float)), f"Invalid response time type: {type(response_time)}"
    assert response_time >= 0, f"Negative response time: {response_time}"
    assert response_time <= max_time, f"{message}: {response_time}s > {max_time}s"


def assert_http_status(
    status_code: int,
    expected: Union[int, List[int]],
    message: str = "Unexpected HTTP status"
):
    """Assert that HTTP status code matches expected"""
    if isinstance(expected, int):
        expected = [expected]
    
    assert status_code in expected, f"{message}: {status_code} not in {expected}"


def assert_error_response(
    response: Dict[str, Any],
    expected_status: int = None,
    expected_message: str = None
):
    """Assert that response is a valid error response"""
    assert "error" in response or "detail" in response, "No error field in response"
    
    if expected_status is not None:
        assert response.get("status_code") == expected_status, \
            f"Expected status {expected_status}, got {response.get('status_code')}"
    
    if expected_message is not None:
        error_msg = response.get("error") or response.get("detail", "")
        assert expected_message in str(error_msg), \
            f"Expected message '{expected_message}' not in '{error_msg}'"


def assert_success_response(
    response: Dict[str, Any],
    required_fields: List[str] = None
):
    """Assert that response is a valid success response"""
    assert "error" not in response, f"Unexpected error in response: {response.get('error')}"
    assert "detail" not in response or response.get("status_code", 200) < 400, \
        f"Unexpected error detail: {response.get('detail')}"
    
    if required_fields:
        assert_content_structure(response, required_fields, "Missing required response fields")


def assert_datetime_format(
    value: str,
    format: str = "%Y-%m-%dT%H:%M:%S",
    message: str = "Invalid datetime format"
):
    """Assert that string is valid datetime in expected format"""
    try:
        datetime.strptime(value, format)
    except ValueError as e:
        raise AssertionError(f"{message}: {value} - {e}")


def assert_list_length(
    lst: List,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    exact_length: Optional[int] = None,
    message: str = "Invalid list length"
):
    """Assert that list length meets requirements"""
    assert isinstance(lst, list), f"Expected list, got {type(lst)}"
    
    if exact_length is not None:
        assert len(lst) == exact_length, \
            f"{message}: Expected {exact_length}, got {len(lst)}"
    else:
        if min_length is not None:
            assert len(lst) >= min_length, \
                f"{message}: {len(lst)} < minimum {min_length}"
        if max_length is not None:
            assert len(lst) <= max_length, \
                f"{message}: {len(lst)} > maximum {max_length}"


def assert_contains_keywords(
    text: str,
    keywords: List[str],
    case_sensitive: bool = False,
    message: str = "Missing required keywords"
):
    """Assert that text contains all required keywords"""
    if not case_sensitive:
        text = text.lower()
        keywords = [k.lower() for k in keywords]
    
    missing = [k for k in keywords if k not in text]
    assert not missing, f"{message}: {missing}"


def assert_no_dangerous_patterns(
    text: str,
    message: str = "Dangerous pattern detected"
):
    """Assert that text contains no dangerous patterns"""
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'DROP\s+TABLE',
        r'DELETE\s+FROM',
        r'INSERT\s+INTO',
        r'\.\./\.\.',
        r'/etc/passwd',
        r'\x00'
    ]
    
    for pattern in dangerous_patterns:
        assert not re.search(pattern, text, re.IGNORECASE), \
            f"{message}: Pattern '{pattern}' found in text"


def assert_rate_limit_headers(
    headers: Dict[str, str],
    message: str = "Missing rate limit headers"
):
    """Assert that rate limit headers are present and valid"""
    required_headers = [
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset"
    ]
    
    for header in required_headers:
        assert header in headers, f"{message}: Missing {header}"
    
    # Validate header values
    limit = int(headers["X-RateLimit-Limit"])
    remaining = int(headers["X-RateLimit-Remaining"])
    reset = int(headers["X-RateLimit-Reset"])
    
    assert limit > 0, f"Invalid rate limit: {limit}"
    assert 0 <= remaining <= limit, f"Invalid remaining: {remaining}/{limit}"
    assert reset > 0, f"Invalid reset time: {reset}"