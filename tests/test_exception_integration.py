"""
Integration tests for exception handling system.

Tests that exceptions are raised, caught, and handled correctly
throughout the application flow.
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestExceptionFlow(unittest.TestCase):
    """Test exception flow through the system."""
    
    def test_validation_error_flow(self):
        """Test ValidationError flows through ErrorHandler correctly."""
        from src.ai_interviewer.exceptions import ValidationError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        # Create validation error
        error = ValidationError("Name is required", field="candidate_name")
        
        # Convert to response
        response = ErrorHandler.from_exception(error)
        
        # Verify response structure
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "VALIDATION_ERROR")
        self.assertIn("message", response)
        self.assertIn("timestamp", response)
        self.assertIn("field", response["details"])
    
    def test_session_error_flow(self):
        """Test SessionError flows through ErrorHandler correctly."""
        from src.ai_interviewer.exceptions import SessionError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        # Create session error
        error = SessionError("Session expired", session_id="test_123")
        
        # Convert to response
        response = ErrorHandler.from_exception(error)
        
        # Verify response structure
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "SESSION_ERROR")
        self.assertIn("session_id", response["details"])
        self.assertEqual(response["details"]["session_id"], "test_123")
    
    def test_llm_error_flow(self):
        """Test LLMError flows through ErrorHandler correctly."""
        from src.ai_interviewer.exceptions import LLMError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        # Create LLM error
        error = LLMError("API rate limit exceeded", model="test-model", api_error="429")
        
        # Convert to response
        response = ErrorHandler.from_exception(error)
        
        # Verify response structure
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "LLM_ERROR")
        self.assertIn("model", response["details"])
        self.assertIn("api_error", response["details"])
    
    def test_security_error_flow(self):
        """Test SecurityError flows through ErrorHandler correctly."""
        from src.ai_interviewer.exceptions import SecurityError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        # Create security error
        error = SecurityError("SSRF attempt detected", violation_type="SSRF")
        
        # Convert to response
        response = ErrorHandler.from_exception(error)
        
        # Verify response structure
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "SECURITY_ERROR")
        self.assertIn("violation_type", response["details"])
        self.assertEqual(response["details"]["violation_type"], "SSRF")
    
    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from base correctly."""
        from src.ai_interviewer.exceptions import (
            AIInterviewerError,
            ValidationError,
            SessionError,
            LLMError
        )
        
        # All should be instances of base exception
        validation = ValidationError("Test")
        session = SessionError("Test")
        llm = LLMError("Test")
        
        self.assertIsInstance(validation, AIInterviewerError)
        self.assertIsInstance(session, AIInterviewerError)
        self.assertIsInstance(llm, AIInterviewerError)
    
    def test_error_handler_context(self):
        """Test ErrorHandler preserves context correctly."""
        from src.ai_interviewer.exceptions import ValidationError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        error = ValidationError("Test error", field="test_field")
        context = {"operation": "test_operation", "user_id": "123"}
        
        response = ErrorHandler.from_exception(error, context=context)
        
        # Context should be merged into details
        self.assertIn("operation", response["details"])
        self.assertIn("user_id", response["details"])
        self.assertEqual(response["details"]["operation"], "test_operation")


class TestControllerExceptionHandling(unittest.TestCase):
    """Test that controller handles exceptions correctly."""
    
    def test_controller_handles_validation_error(self):
        """Test controller handles ValidationError for invalid input."""
        from src.ai_interviewer.controller import InterviewApplication
        from src.ai_interviewer.exceptions import ValidationError
        
        app = InterviewApplication()
        
        # Should catch ValidationError and return error response
        result = app.start_topic_interview("Python", "")
        
        # Verify error response structure
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)
        self.assertIn("error_code", result)
        self.assertEqual(result["error_code"], "VALIDATION_ERROR")
        self.assertIn("timestamp", result)
    
    def test_controller_raises_session_error(self):
        """Test controller raises SessionError when no session exists."""
        from src.ai_interviewer.controller import InterviewApplication
        from src.ai_interviewer.exceptions import SessionError
        
        app = InterviewApplication()
        app.current_session = None  # No active session
        
        # Should raise SessionError
        with self.assertRaises(SessionError):
            app.process_answer("test answer")


class TestErrorHandlerProductionMode(unittest.TestCase):
    """Test ErrorHandler behavior in production mode."""
    
    def setUp(self):
        """Save original environment."""
        self.original_env = os.environ.get("ENVIRONMENT")
    
    def tearDown(self):
        """Restore original environment."""
        if self.original_env:
            os.environ["ENVIRONMENT"] = self.original_env
        elif "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
    
    def test_production_sanitizes_messages(self):
        """Test that production mode sanitizes error messages."""
        from src.ai_interviewer.exceptions import ValidationError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        os.environ["ENVIRONMENT"] = "production"
        
        error = ValidationError("Detailed error: field 'email' contains invalid format", field="email")
        response = ErrorHandler.from_exception(error)
        
        # Should get generic message, not detailed
        self.assertNotIn("email", response["message"].lower())
        self.assertNotIn("invalid format", response["message"].lower())
        self.assertEqual(response["details"], {})  # Details hidden
    
    def test_development_shows_details(self):
        """Test that development mode shows detailed messages."""
        from src.ai_interviewer.exceptions import ValidationError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        
        error = ValidationError("Detailed error: field 'email' contains invalid format", field="email")
        response = ErrorHandler.from_exception(error)
        
        # Should show detailed message
        self.assertIn("message", response)
        self.assertIn("details", response)
        self.assertIn("field", response["details"])


class TestExceptionLogging(unittest.TestCase):
    """Test that exception logging works correctly."""
    
    def test_error_handler_logs_validation_error(self):
        """Test ErrorHandler logs ValidationError correctly."""
        from src.ai_interviewer.exceptions import ValidationError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        error = ValidationError("Test validation error", field="test")
        
        # Should not raise exception
        try:
            ErrorHandler.log_error(error, {"operation": "test"})
            self.assertTrue(True, "Logging completed successfully")
        except Exception as e:
            self.fail(f"Logging raised exception: {e}")
    
    def test_error_handler_logs_with_context(self):
        """Test ErrorHandler logs with context."""
        from src.ai_interviewer.exceptions import LLMError
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        error = LLMError("API error", model="test-model")
        context = {"session_id": "123", "operation": "generate_question"}
        
        # Should not raise exception
        try:
            ErrorHandler.log_error(error, context=context, level="error")
            self.assertTrue(True, "Logging with context completed successfully")
        except Exception as e:
            self.fail(f"Logging raised exception: {e}")


def run_integration_tests():
    """Run all integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestControllerExceptionHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandlerProductionMode))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionLogging))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("Exception Integration Tests")
    print("=" * 70)
    print()
    
    result = run_integration_tests()
    
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("=" * 70)
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(traceback)
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(traceback)
    
    sys.exit(0 if result.wasSuccessful() else 1)

