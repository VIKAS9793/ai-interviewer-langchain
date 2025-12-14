"""
Input Validation Utilities
Secure-by-default input validation for all user inputs.
"""

import re
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse
import ipaddress

from .config import Config
from ..exceptions import ValidationError

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Centralized input validation following OWASP guidelines.
    All validation methods return (is_valid: bool, error_message: Optional[str])
    """
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate candidate name.
        
        Rules:
        - Non-empty after stripping
        - Length <= MAX_NAME_LENGTH
        - No control characters
        - No script injection patterns
        """
        if not name or not name.strip():
            return False, "Name cannot be empty"
        
        name = name.strip()
        
        if len(name) > Config.MAX_NAME_LENGTH:
            return False, f"Name too long (max {Config.MAX_NAME_LENGTH} characters)"
        
        # Check for control characters (except space, tab, newline)
        if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', name):
            return False, "Name contains invalid characters"
        
        # Basic XSS pattern detection
        if re.search(r'<[^>]*>|javascript:|on\w+\s*=', name, re.IGNORECASE):
            return False, "Name contains potentially unsafe content"
        
        return True, None
    
    @staticmethod
    def validate_answer_text(text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate answer text.
        
        Rules:
        - Non-empty after stripping
        - Length <= MAX_ANSWER_LENGTH
        - No excessive control characters
        """
        if not text or not text.strip():
            return False, "Answer cannot be empty"
        
        text = text.strip()
        
        if len(text) > Config.MAX_ANSWER_LENGTH:
            return False, f"Answer too long (max {Config.MAX_ANSWER_LENGTH} characters)"
        
        # Allow reasonable whitespace but prevent excessive control chars
        # Allow newlines and tabs for formatted answers
        if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', text):
            return False, "Answer contains invalid control characters"
        
        return True, None
    
    @staticmethod
    def validate_jd_text(text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate job description text.
        
        Rules:
        - Length <= MAX_JD_TEXT_LENGTH
        - No excessive control characters
        """
        if not text:
            return True, None  # JD text is optional
        
        text = text.strip()
        
        if len(text) > Config.MAX_JD_TEXT_LENGTH:
            return False, f"Job description too long (max {Config.MAX_JD_TEXT_LENGTH} characters)"
        
        # Allow reasonable formatting but prevent control chars
        if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', text):
            return False, "Job description contains invalid control characters"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL for SSRF protection.
        
        Rules:
        - Valid URL format
        - Only HTTP/HTTPS schemes
        - No localhost/internal IPs
        - Length <= MAX_JD_URL_LENGTH
        - No dangerous protocols (file://, ftp://, etc.)
        
        Reference: OWASP SSRF Prevention Cheat Sheet
        """
        if not url or not url.strip():
            return False, "URL cannot be empty"
        
        url = url.strip()
        
        if len(url) > Config.MAX_JD_URL_LENGTH:
            return False, f"URL too long (max {Config.MAX_JD_URL_LENGTH} characters)"
        
        try:
            parsed = urlparse(url)
        except (ValueError, AttributeError) as e:
            logger.warning(f"URL parse error: {e}")
            return False, "Invalid URL format"
        except Exception as e:
            # Catch-all for unexpected parsing errors
            logger.warning(f"Unexpected URL parse error: {e}")
            return False, "Invalid URL format"
        
        # Scheme validation
        if not parsed.scheme:
            return False, "URL must include scheme (http:// or https://)"
        
        if parsed.scheme.lower() not in Config.ALLOWED_URL_SCHEMES:
            return False, f"Only {', '.join(Config.ALLOWED_URL_SCHEMES)} schemes are allowed"
        
        # Hostname validation
        if not parsed.hostname:
            return False, "URL must include a valid hostname"
        
        hostname_lower = parsed.hostname.lower()
        
        # Block localhost variants
        if hostname_lower in Config.BLOCKED_HOSTNAMES:
            return False, "Localhost URLs are not allowed for security reasons"
        
        # Block private IP ranges (SSRF protection)
        try:
            # Try to parse as IP address
            ip = ipaddress.ip_address(hostname_lower)
            
            # Block private/internal IP ranges
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False, "Private/internal IP addresses are not allowed"
            
            # Block multicast and other special ranges
            if ip.is_multicast:
                return False, "Multicast IP addresses are not allowed"
                
        except ValueError:
            # Not an IP address, check hostname patterns
            # Block localhost-like hostnames
            if any(blocked in hostname_lower for blocked in ['localhost', '127.', '192.168.', '10.', '172.16', '172.17', '172.18', '172.19', '172.20', '172.21', '172.22', '172.23', '172.24', '172.25', '172.26', '172.27', '172.28', '172.29', '172.30', '172.31']):
                return False, "Internal hostnames are not allowed"
        
        # Block file:// and other dangerous protocols (already handled by scheme check, but double-check)
        if url.startswith(('file://', 'ftp://', 'gopher://', 'data:', 'javascript:')):
            return False, "Dangerous URL schemes are not allowed"
        
        return True, None
    
    @staticmethod
    def validate_voice_transcript(text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate voice transcription text.
        
        Rules:
        - Length <= VOICE_MAX_TRANSCRIPT_LENGTH
        - No control characters
        """
        if not text:
            return True, None  # Empty is valid (no speech detected)
        
        text = text.strip()
        
        if len(text) > Config.VOICE_MAX_TRANSCRIPT_LENGTH:
            return False, f"Transcription too long (max {Config.VOICE_MAX_TRANSCRIPT_LENGTH} characters)"
        
        # Allow reasonable formatting
        if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', text):
            return False, "Transcription contains invalid control characters"
        
        return True, None
    
    @staticmethod
    def sanitize_error_message(error: Exception, is_production: bool = False) -> str:
        """
        Sanitize error messages for user display.
        
        In production, return generic messages to prevent information disclosure.
        In development, return detailed messages for debugging.
        
        Args:
            error: The exception that occurred
            is_production: Whether running in production mode
            
        Returns:
            Safe error message for user display
        """
        if is_production:
            # Generic messages in production
            error_type = type(error).__name__
            
            if "Connection" in error_type or "Timeout" in error_type:
                return "Connection error. Please check your network and try again."
            elif "Validation" in error_type or "Value" in error_type:
                return "Invalid input provided. Please check your input and try again."
            elif "Permission" in error_type or "Forbidden" in error_type:
                return "Access denied. Please check your permissions."
            elif "NotFound" in error_type:
                return "Resource not found. Please verify your request."
            else:
                return "An error occurred. Please try again later."
        else:
            # Detailed messages in development
            return f"Error: {type(error).__name__}: {str(error)}"

