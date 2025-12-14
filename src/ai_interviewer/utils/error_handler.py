"""
Error handling utilities for AI Interviewer.

Provides standardized error response formatting and error conversion utilities.
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from ..exceptions import (
    AIInterviewerError,
    ValidationError,
    SecurityError,
    SessionError,
    LLMError,
    ProcessingError,
    ResourceError,
    ConfigurationError
)
from .types import ErrorResponse

logger = logging.getLogger(__name__)


@dataclass
class ErrorHandler:
    """
    Standardized error response handler.
    
    Converts exceptions to user-friendly error responses with
    environment-aware message sanitization.
    """
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production mode."""
        return os.getenv("ENVIRONMENT", "").lower() == "production"
    
    @staticmethod
    def from_exception(
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorResponse:
        """
        Convert exception to standardized error response.
        
        Args:
            error: The exception that occurred
            context: Additional context (e.g., session_id, operation)
            
        Returns:
            Standardized error response dictionary
        """
        is_prod = ErrorHandler.is_production()
        
        # Handle custom exceptions
        if isinstance(error, AIInterviewerError):
            return ErrorHandler._from_custom_exception(error, is_prod, context)
        
        # Handle standard Python exceptions
        return ErrorHandler._from_standard_exception(error, is_prod, context)
    
    @staticmethod
    def _from_custom_exception(
        error: AIInterviewerError,
        is_production: bool,
        context: Optional[Dict[str, Any]]
    ) -> ErrorResponse:
        """Convert custom exception to error response."""
        # Merge context with error details
        details = error.details.copy()
        if context:
            details.update(context)
        
        # Sanitize message for production
        if is_production:
            # Use generic messages in production
            message = ErrorHandler._get_generic_message(error.error_code)
        else:
            # Use detailed messages in development
            message = error.message
        
        return {
            "success": False,
            "error_code": error.error_code,
            "message": message,
            "details": details if not is_production else {},  # Hide details in production
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _from_standard_exception(
        error: Exception,
        is_production: bool,
        context: Optional[Dict[str, Any]]
    ) -> ErrorResponse:
        """Convert standard exception to error response."""
        error_type = type(error).__name__
        
        # Map common exceptions to error codes
        error_code_map = {
            "ValueError": "VALIDATION_ERROR",
            "KeyError": "VALIDATION_ERROR",
            "TypeError": "VALIDATION_ERROR",
            "AttributeError": "VALIDATION_ERROR",
            "ConnectionError": "LLM_ERROR",
            "TimeoutError": "RESOURCE_ERROR",
            "MemoryError": "RESOURCE_ERROR",
            "FileNotFoundError": "PROCESSING_ERROR",
            "PermissionError": "SECURITY_ERROR",
        }
        
        error_code = error_code_map.get(error_type, "INTERNAL_ERROR")
        
        # Sanitize message for production
        if is_production:
            message = ErrorHandler._get_generic_message(error_code)
        else:
            message = f"{error_type}: {str(error)}"
        
        details = {}
        if context:
            details.update(context)
        if not is_production:
            details["exception_type"] = error_type
            details["exception_message"] = str(error)
        
        return {
            "success": False,
            "error_code": error_code,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _get_generic_message(error_code: str) -> str:
        """
        Get generic error message for production.
        
        Returns user-friendly messages that don't expose internal details.
        """
        generic_messages = {
            "VALIDATION_ERROR": "Invalid input provided. Please check your input and try again.",
            "SESSION_ERROR": "Session error. Please start a new interview.",
            "LLM_ERROR": "Service temporarily unavailable. Please try again later.",
            "CONFIG_ERROR": "Configuration error. Please contact support.",
            "SECURITY_ERROR": "Security validation failed. Please check your input.",
            "PROCESSING_ERROR": "Processing error. Please try again.",
            "RESOURCE_ERROR": "Resource limit exceeded. Please try again later.",
            "INTERNAL_ERROR": "An unexpected error occurred. Please try again later.",
            "UNKNOWN_ERROR": "An error occurred. Please try again later."
        }
        
        return generic_messages.get(error_code, generic_messages["UNKNOWN_ERROR"])
    
    @staticmethod
    def log_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "error"
    ) -> None:
        """
        Log error with context.
        
        Args:
            error: The exception
            context: Additional context
            level: Log level ("error", "warning", "critical")
        """
        log_func = getattr(logger, level.lower(), logger.error)
        
        if isinstance(error, AIInterviewerError):
            log_func(
                f"{error.error_code}: {error.message}",
                extra={
                    "error_code": error.error_code,
                    "details": error.details,
                    **(context or {})
                },
                exc_info=not isinstance(error, (ValidationError, SecurityError))
            )
        else:
            log_func(
                f"{type(error).__name__}: {str(error)}",
                extra=context,
                exc_info=True
            )

