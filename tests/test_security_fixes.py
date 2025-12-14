"""
Security Fixes Test Suite
Tests for input validation, SSRF protection, error sanitization, and session expiration.
"""

import pytest
import time
from unittest.mock import Mock, patch

from src.ai_interviewer.utils.input_validator import InputValidator, ValidationError
from src.ai_interviewer.utils.url_scraper import URLScraper
from src.ai_interviewer.core.session_manager import SessionManager, InterviewSession, InterviewPhase
from src.ai_interviewer.utils.config import Config


class TestInputValidator:
    """Test input validation utilities"""
    
    def test_validate_name_success(self):
        """Test valid name validation"""
        is_valid, error = InputValidator.validate_name("John Doe")
        assert is_valid is True
        assert error is None
    
    def test_validate_name_empty(self):
        """Test empty name rejection"""
        is_valid, error = InputValidator.validate_name("")
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_name_too_long(self):
        """Test name length limit"""
        long_name = "A" * (Config.MAX_NAME_LENGTH + 1)
        is_valid, error = InputValidator.validate_name(long_name)
        assert is_valid is False
        assert "too long" in error.lower()
    
    def test_validate_name_xss_pattern(self):
        """Test XSS pattern detection"""
        malicious_name = "<script>alert('xss')</script>"
        is_valid, error = InputValidator.validate_name(malicious_name)
        assert is_valid is False
        assert "unsafe" in error.lower() or "invalid" in error.lower()
    
    def test_validate_answer_text_success(self):
        """Test valid answer text"""
        answer = "This is a valid answer with reasonable length."
        is_valid, error = InputValidator.validate_answer_text(answer)
        assert is_valid is True
        assert error is None
    
    def test_validate_answer_text_too_long(self):
        """Test answer length limit"""
        long_answer = "A" * (Config.MAX_ANSWER_LENGTH + 1)
        is_valid, error = InputValidator.validate_answer_text(long_answer)
        assert is_valid is False
        assert "too long" in error.lower()
    
    def test_validate_url_success(self):
        """Test valid URL"""
        url = "https://example.com/job-description"
        is_valid, error = InputValidator.validate_url(url)
        assert is_valid is True
        assert error is None
    
    def test_validate_url_ssrf_localhost(self):
        """Test SSRF protection - localhost"""
        url = "http://localhost:8080/internal"
        is_valid, error = InputValidator.validate_url(url)
        assert is_valid is False
        assert "localhost" in error.lower() or "not allowed" in error.lower()
    
    def test_validate_url_ssrf_private_ip(self):
        """Test SSRF protection - private IP"""
        url = "http://192.168.1.1/internal"
        is_valid, error = InputValidator.validate_url(url)
        assert is_valid is False
        assert "private" in error.lower() or "not allowed" in error.lower()
    
    def test_validate_url_dangerous_scheme(self):
        """Test dangerous scheme rejection"""
        url = "file:///etc/passwd"
        is_valid, error = InputValidator.validate_url(url)
        assert is_valid is False
        assert "scheme" in error.lower() or "not allowed" in error.lower()
    
    def test_validate_voice_transcript_success(self):
        """Test valid voice transcript"""
        transcript = "This is a valid transcript."
        is_valid, error = InputValidator.validate_voice_transcript(transcript)
        assert is_valid is True
        assert error is None
    
    def test_validate_voice_transcript_too_long(self):
        """Test voice transcript length limit"""
        long_transcript = "A" * (Config.VOICE_MAX_TRANSCRIPT_LENGTH + 1)
        is_valid, error = InputValidator.validate_voice_transcript(long_transcript)
        assert is_valid is False
        assert "too long" in error.lower()
    
    def test_sanitize_error_message_production(self):
        """Test error message sanitization in production"""
        error = ValueError("Internal database error: connection failed")
        message = InputValidator.sanitize_error_message(error, is_production=True)
        assert "Internal database error" not in message
        assert "connection failed" not in message
        assert len(message) > 0
    
    def test_sanitize_error_message_development(self):
        """Test error message details in development"""
        error = ValueError("Test error message")
        message = InputValidator.sanitize_error_message(error, is_production=False)
        assert "ValueError" in message or "Test error message" in message


class TestURLScraperSSRF:
    """Test SSRF protection in URL scraper"""
    
    @patch('src.ai_interviewer.utils.url_scraper.requests.get')
    def test_scrape_valid_url(self, mock_get):
        """Test scraping valid external URL"""
        mock_response = Mock()
        mock_response.headers = {'Content-Length': '1000'}
        mock_response.iter_content.return_value = [b'<html><body>Job Description</body></html>']
        mock_get.return_value = mock_response
        
        result = URLScraper.extract_text("https://example.com/job")
        assert result is not None
        assert "Job Description" in result
    
    def test_scrape_localhost_blocked(self):
        """Test that localhost URLs are blocked"""
        result = URLScraper.extract_text("http://localhost:8080/internal")
        assert result is None
    
    def test_scrape_private_ip_blocked(self):
        """Test that private IPs are blocked"""
        result = URLScraper.extract_text("http://192.168.1.1/internal")
        assert result is None
    
    @patch('src.ai_interviewer.utils.url_scraper.requests.get')
    def test_scrape_large_response_blocked(self, mock_get):
        """Test that large responses are blocked"""
        mock_response = Mock()
        mock_response.headers = {'Content-Length': str(URLScraper.MAX_RESPONSE_SIZE + 1)}
        mock_get.return_value = mock_response
        
        result = URLScraper.extract_text("https://example.com/large")
        assert result is None


class TestSessionExpiration:
    """Test session expiration and cleanup"""
    
    def test_session_not_expired(self):
        """Test active session is not expired"""
        session = InterviewSession(
            session_id="test-1",
            candidate_name="Test User",
            topic="Python"
        )
        assert session.is_expired() is False
    
    def test_session_expired(self):
        """Test expired session detection"""
        session = InterviewSession(
            session_id="test-2",
            candidate_name="Test User",
            topic="Python"
        )
        # Manually set last_activity to past
        session.last_activity = time.time() - Config.SESSION_EXPIRATION_SECONDS - 1
        assert session.is_expired() is True
    
    def test_completed_session_not_expired(self):
        """Test completed sessions don't expire"""
        session = InterviewSession(
            session_id="test-3",
            candidate_name="Test User",
            topic="Python"
        )
        session.interview_complete = True
        session.last_activity = time.time() - Config.SESSION_EXPIRATION_SECONDS - 1
        assert session.is_expired() is False
    
    def test_session_activity_update(self):
        """Test activity timestamp update"""
        session = InterviewSession(
            session_id="test-4",
            candidate_name="Test User",
            topic="Python"
        )
        old_activity = session.last_activity
        time.sleep(0.1)
        session.update_activity()
        assert session.last_activity > old_activity
    
    def test_session_manager_cleanup(self):
        """Test session manager cleanup of expired sessions"""
        manager = SessionManager()
        
        # Create expired session
        session = InterviewSession(
            session_id="expired-1",
            candidate_name="Test",
            topic="Python"
        )
        session.last_activity = time.time() - Config.SESSION_EXPIRATION_SECONDS - 1
        manager.active_sessions["expired-1"] = session
        
        # Create active session
        active_session = InterviewSession(
            session_id="active-1",
            candidate_name="Test",
            topic="Python"
        )
        manager.active_sessions["active-1"] = active_session
        
        # Cleanup
        cleaned = manager.cleanup_expired_sessions()
        assert cleaned == 1
        assert "expired-1" not in manager.active_sessions
        assert "active-1" in manager.active_sessions
    
    def test_get_session_updates_activity(self):
        """Test that getting session updates activity"""
        manager = SessionManager()
        session = manager.create_session("test-5", "Test", "Python")
        old_activity = session.last_activity
        
        time.sleep(0.1)
        retrieved = manager.get_session("test-5")
        assert retrieved is not None
        assert retrieved.last_activity > old_activity
    
    def test_get_expired_session_returns_none(self):
        """Test that expired sessions are removed on access"""
        manager = SessionManager()
        session = manager.create_session("expired-2", "Test", "Python")
        session.last_activity = time.time() - Config.SESSION_EXPIRATION_SECONDS - 1
        
        retrieved = manager.get_session("expired-2")
        assert retrieved is None
        assert "expired-2" not in manager.active_sessions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

