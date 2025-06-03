from enum import Enum
from typing import Any, Dict, Optional


class JobErrorCode(Enum):
    """Internal error codes for job-related and content generation issues."""

    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INPUT_VALIDATION_FAILED = "INPUT_VALIDATION_FAILED"
    OUTLINE_GENERATION_FAILED = "OUTLINE_GENERATION_FAILED"
    CONTENT_TYPE_GENERATION_FAILED = "CONTENT_TYPE_GENERATION_FAILED"
    AUDIO_GENERATION_FAILED = "AUDIO_GENERATION_FAILED"
    PIPELINE_ERROR = "PIPELINE_ERROR"
    JOB_CREATION_FAILED = "JOB_CREATION_FAILED"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    TASK_ENQUEUE_FAILED = "TASK_ENQUEUE_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"  # For Vertex AI, ElevenLabs, etc.


class AppExceptionBase(Exception):
    """Base class for custom application exceptions."""

    def __init__(
        self,
        status_code: int,
        user_message: str,
        error_code: JobErrorCode = JobErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        internal_log_message: Optional[str] = None,
    ):
        super().__init__(user_message)
        self.status_code = status_code
        self.user_message = user_message
        self.error_code = error_code
        self.details = details or {}
        self.internal_log_message = internal_log_message or user_message


class JobCreationError(AppExceptionBase):
    """Custom exception for errors during job creation."""

    def __init__(
        self,
        user_message: str = "Failed to create job.",
        error_code: JobErrorCode = JobErrorCode.JOB_CREATION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        internal_log_message: Optional[str] = None,
    ):
        super().__init__(
            status_code=500,
            user_message=user_message,
            error_code=error_code,
            details=details,
            internal_log_message=internal_log_message or user_message,
        )


class ContentGenerationError(AppExceptionBase):
    """Custom exception for errors during content generation pipeline."""

    def __init__(
        self,
        user_message: str = "Content generation process failed.",
        error_code: JobErrorCode = JobErrorCode.PIPELINE_ERROR,
        details: Optional[Dict[str, Any]] = None,
        internal_log_message: Optional[str] = None,
    ):
        super().__init__(
            status_code=500,
            user_message=user_message,
            error_code=error_code,
            details=details,
            internal_log_message=internal_log_message or user_message,
        )


class ExternalServiceError(AppExceptionBase):
    """Custom exception for errors from external services like Vertex AI or ElevenLabs."""

    def __init__(
        self,
        service_name: str,
        user_message: str = "An external service required for content generation is currently unavailable.",
        error_code: JobErrorCode = JobErrorCode.EXTERNAL_SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None,
        internal_log_message: Optional[str] = None,
    ):
        super().__init__(
            status_code=503,  # Service Unavailable
            user_message=user_message,
            error_code=error_code,
            details=details or {"service_name": service_name},
            internal_log_message=internal_log_message
            or f"Error with external service: {service_name}",
        )


class NotFoundError(AppExceptionBase):
    """Custom exception for resource not found errors."""

    def __init__(
        self,
        resource_name: str = "Resource",
        error_code: JobErrorCode = JobErrorCode.JOB_NOT_FOUND,  # Example, can be more generic
        details: Optional[Dict[str, Any]] = None,
        internal_log_message: Optional[str] = None,
    ):
        user_message = f"{resource_name} not found."
        super().__init__(
            status_code=404,
            user_message=user_message,
            error_code=error_code,
            details=details,
            internal_log_message=internal_log_message or user_message,
        )


class InvalidInputError(AppExceptionBase):
    """Custom exception for invalid input errors."""

    def __init__(
        self,
        user_message: str = "Invalid input provided.",
        error_code: JobErrorCode = JobErrorCode.INPUT_VALIDATION_FAILED,
        details: Optional[Dict[str, Any]] = None,  # Can contain Pydantic error details
        internal_log_message: Optional[str] = None,
    ):
        super().__init__(
            status_code=400,  # Bad Request
            user_message=user_message,
            error_code=error_code,
            details=details,
            internal_log_message=internal_log_message or user_message,
        )


# Ensure the directory exists for __init__.py
