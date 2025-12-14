"""
Custom exception hierarchy for AI Interviewer.

This module provides a structured exception hierarchy following MAANG best practices:
- Specific exception types for different error categories
- Error codes for programmatic error handling
- Context preservation for debugging
"""

from typing import Optional, Dict, Any


class AIInterviewerError(Exception):
    """
    Base exception for all AI Interviewer errors.
    
    All custom exceptions inherit from this base class, allowing
    catch-all error handling while maintaining specificity.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., "VALIDATION_ERROR")
            details: Additional context for debugging
        """
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return formatted error message."""
        if self.details:
            return f"{self.error_code}: {self.message} (Details: {self.details})"
        return f"{self.error_code}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ValidationError(AIInterviewerError):
    """
    Raised when input validation fails.
    
    Use for:
    - Invalid user input
    - Missing required fields
    - Format violations
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Name of the field that failed validation
            value: The invalid value (for debugging)
        """
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["invalid_value"] = str(value)[:100]  # Truncate long values
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"}
        )
        self.field = field
        self.value = value


class SessionError(AIInterviewerError):
    """
    Raised when session management operations fail.
    
    Use for:
    - Invalid or expired sessions
    - Session not found
    - Session creation failures
    """
    
    def __init__(
        self,
        message: str,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize session error.
        
        Args:
            message: Error message
            session_id: ID of the session (if applicable)
        """
        details = kwargs.get("details", {})
        if session_id:
            details["session_id"] = session_id
        
        super().__init__(
            message=message,
            error_code="SESSION_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"}
        )
        self.session_id = session_id


class LLMError(AIInterviewerError):
    """
    Raised when LLM API calls fail.
    
    Use for:
    - API connection errors
    - Rate limiting
    - Invalid responses
    - Model unavailable
    """
    
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        api_error: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize LLM error.
        
        Args:
            message: Error message
            model: Model name that failed
            api_error: Original API error message
        """
        details = kwargs.get("details", {})
        if model:
            details["model"] = model
        if api_error:
            details["api_error"] = api_error
        
        super().__init__(
            message=message,
            error_code="LLM_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"}
        )
        self.model = model
        self.api_error = api_error


class ConfigurationError(AIInterviewerError):
    """
    Raised when configuration is invalid or missing.
    
    Use for:
    - Missing required environment variables
    - Invalid configuration values
    - Configuration file errors
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
        """
        details = kwargs.get("details", {})
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"}
        )
        self.config_key = config_key


class SecurityError(AIInterviewerError):
    """
    Raised when security validation fails.
    
    Use for:
    - SSRF protection violations
    - XSS pattern detection
    - File security scanning failures
    - Input sanitization failures
    """
    
    def __init__(
        self,
        message: str,
        violation_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize security error.
        
        Args:
            message: Error message (sanitized for production)
            violation_type: Type of security violation (e.g., "SSRF", "XSS")
        """
        details = kwargs.get("details", {})
        if violation_type:
            details["violation_type"] = violation_type
        
        super().__init__(
            message=message,
            error_code="SECURITY_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"}
        )
        self.violation_type = violation_type


class ProcessingError(AIInterviewerError):
    """
    Raised when data processing operations fail.
    
    Use for:
    - Resume parsing errors
    - URL scraping failures
    - Text extraction errors
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize processing error.
        
        Args:
            message: Error message
            operation: Name of the operation that failed
        """
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="PROCESSING_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"}
        )
        self.operation = operation


class ResourceError(AIInterviewerError):
    """
    Raised when resource limits are exceeded.
    
    Use for:
    - Memory exhaustion
    - Rate limiting
    - Concurrent session limits
    - Timeout errors
    """
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        limit: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize resource error.
        
        Args:
            message: Error message
            resource_type: Type of resource (e.g., "memory", "sessions")
            limit: The limit that was exceeded
        """
        details = kwargs.get("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if limit is not None:
            details["limit"] = str(limit)
        
        super().__init__(
            message=message,
            error_code="RESOURCE_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"}
        )
        self.resource_type = resource_type
        self.limit = limit

