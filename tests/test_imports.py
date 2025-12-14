"""
Import and path verification tests.

Tests that all new modules can be imported correctly and that
the exception hierarchy and error handling work as expected.
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestImports(unittest.TestCase):
    """Test that all modules can be imported correctly."""
    
    def test_exceptions_import(self):
        """Test that exceptions module can be imported."""
        try:
            from src.ai_interviewer.exceptions import (
                AIInterviewerError,
                ValidationError,
                SessionError,
                LLMError,
                ConfigurationError,
                SecurityError,
                ProcessingError,
                ResourceError
            )
            self.assertTrue(True, "All exceptions imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import exceptions: {e}")
    
    def test_error_handler_import(self):
        """Test that error_handler module can be imported."""
        try:
            from src.ai_interviewer.utils.error_handler import ErrorHandler
            self.assertTrue(True, "ErrorHandler imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import ErrorHandler: {e}")
    
    def test_types_import(self):
        """Test that types module can be imported."""
        try:
            from src.ai_interviewer.utils.types import (
                InterviewResponse,
                PracticeModeResponse,
                ErrorResponse,
                InterviewStartResponse,
                AnswerProcessResponse,
                SessionStatusResponse,
                SystemStatusResponse,
                ResumeAnalysisResponse
            )
            self.assertTrue(True, "All types imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import types: {e}")
    
    def test_controller_imports(self):
        """Test that controller can import all dependencies."""
        try:
            from src.ai_interviewer.controller import InterviewApplication
            self.assertTrue(True, "Controller imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import controller: {e}")
    
    def test_flow_controller_imports(self):
        """Test that flow controller can import all dependencies."""
        try:
            from src.ai_interviewer.core.autonomous_flow_controller import (
                AutonomousFlowController
            )
            self.assertTrue(True, "Flow controller imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import flow controller: {e}")


class TestExceptionHierarchy(unittest.TestCase):
    """Test that exception hierarchy works correctly."""
    
    def test_base_exception(self):
        """Test base exception can be raised and caught."""
        from src.ai_interviewer.exceptions import AIInterviewerError
        
        with self.assertRaises(AIInterviewerError):
            raise AIInterviewerError("Test error", error_code="TEST_ERROR")
    
    def test_validation_error(self):
        """Test ValidationError can be raised and caught."""
        from src.ai_interviewer.exceptions import ValidationError, AIInterviewerError
        
        with self.assertRaises(ValidationError):
            raise ValidationError("Invalid input", field="test_field")
        
        # Should also be catchable as base exception
        try:
            raise ValidationError("Invalid input", field="test_field")
        except AIInterviewerError as e:
            self.assertEqual(e.error_code, "VALIDATION_ERROR")
            self.assertEqual(e.field, "test_field")
    
    def test_session_error(self):
        """Test SessionError can be raised and caught."""
        from src.ai_interviewer.exceptions import SessionError
        
        with self.assertRaises(SessionError):
            raise SessionError("Session expired", session_id="test_session")
    
    def test_llm_error(self):
        """Test LLMError can be raised and caught."""
        from src.ai_interviewer.exceptions import LLMError
        
        with self.assertRaises(LLMError):
            raise LLMError("API error", model="test_model")
    
    def test_security_error(self):
        """Test SecurityError can be raised and caught."""
        from src.ai_interviewer.exceptions import SecurityError
        
        with self.assertRaises(SecurityError):
            raise SecurityError("SSRF detected", violation_type="SSRF")
    
    def test_exception_to_dict(self):
        """Test exception can be converted to dictionary."""
        from src.ai_interviewer.exceptions import ValidationError
        
        error = ValidationError("Invalid input", field="test_field", value="bad_value")
        error_dict = error.to_dict()
        
        self.assertEqual(error_dict["error_code"], "VALIDATION_ERROR")
        self.assertEqual(error_dict["message"], "Invalid input")
        self.assertIn("field", error_dict["details"])
        self.assertEqual(error_dict["details"]["field"], "test_field")


class TestErrorHandler(unittest.TestCase):
    """Test that ErrorHandler works correctly."""
    
    def test_error_handler_imports_exceptions(self):
        """Test that ErrorHandler can access all exception types."""
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        from src.ai_interviewer.exceptions import (
            ValidationError,
            SecurityError,
            SessionError,
            LLMError
        )
        
        # Test that isinstance checks work
        validation_error = ValidationError("Test", field="test")
        security_error = SecurityError("Test", violation_type="XSS")
        
        # These should not raise errors
        self.assertTrue(isinstance(validation_error, ValidationError))
        self.assertTrue(isinstance(security_error, SecurityError))
    
    def test_error_handler_from_custom_exception(self):
        """Test ErrorHandler.from_exception with custom exception."""
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        from src.ai_interviewer.exceptions import ValidationError
        
        error = ValidationError("Invalid input", field="test_field")
        response = ErrorHandler.from_exception(error)
        
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "VALIDATION_ERROR")
        self.assertIn("message", response)
        self.assertIn("timestamp", response)
    
    def test_error_handler_from_standard_exception(self):
        """Test ErrorHandler.from_exception with standard exception."""
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        error = ValueError("Test value error")
        response = ErrorHandler.from_exception(error)
        
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "VALIDATION_ERROR")
        self.assertIn("message", response)
    
    def test_error_handler_production_mode(self):
        """Test ErrorHandler sanitizes messages in production."""
        import os
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        from src.ai_interviewer.exceptions import ValidationError
        
        # Set production mode
        original_env = os.environ.get("ENVIRONMENT")
        os.environ["ENVIRONMENT"] = "production"
        
        try:
            error = ValidationError("Detailed error message with sensitive info", field="test")
            response = ErrorHandler.from_exception(error)
            
            # In production, should get generic message
            self.assertNotIn("sensitive", response["message"].lower())
            self.assertEqual(response["details"], {})  # Details hidden in production
        finally:
            # Restore original environment
            if original_env:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
    
    def test_error_handler_log_error(self):
        """Test ErrorHandler.log_error doesn't raise exceptions."""
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        from src.ai_interviewer.exceptions import ValidationError
        
        error = ValidationError("Test error", field="test")
        
        # Should not raise exception
        try:
            ErrorHandler.log_error(error, {"operation": "test"})
            self.assertTrue(True, "log_error completed without exception")
        except Exception as e:
            self.fail(f"log_error raised exception: {e}")


class TestControllerImports(unittest.TestCase):
    """Test that controller can import and use all dependencies."""
    
    def test_controller_imports_exceptions(self):
        """Test controller can import exceptions."""
        from src.ai_interviewer.controller import InterviewApplication
        from src.ai_interviewer.exceptions import ValidationError, SessionError, LLMError
        
        # Verify imports work
        self.assertTrue(True, "Controller and exceptions imported successfully")
    
    def test_controller_imports_error_handler(self):
        """Test controller can import ErrorHandler."""
        from src.ai_interviewer.controller import InterviewApplication
        from src.ai_interviewer.utils.error_handler import ErrorHandler
        
        # Verify imports work
        self.assertTrue(True, "Controller and ErrorHandler imported successfully")
    
    def test_controller_imports_types(self):
        """Test controller can import types."""
        from src.ai_interviewer.controller import InterviewApplication
        from src.ai_interviewer.utils.types import (
            InterviewResponse,
            PracticeModeResponse
        )
        
        # Verify imports work
        self.assertTrue(True, "Controller and types imported successfully")


class TestFlowControllerImports(unittest.TestCase):
    """Test that flow controller can import all dependencies."""
    
    def test_flow_controller_imports_types(self):
        """Test flow controller can import types."""
        from src.ai_interviewer.core.autonomous_flow_controller import (
            AutonomousFlowController
        )
        from src.ai_interviewer.utils.types import (
            InterviewStartResponse,
            AnswerProcessResponse,
            ResumeAnalysisResponse
        )
        
        # Verify imports work
        self.assertTrue(True, "Flow controller and types imported successfully")


class TestModulePaths(unittest.TestCase):
    """Test that module paths are correct."""
    
    def test_exceptions_module_path(self):
        """Test exceptions module is in correct location."""
        import src.ai_interviewer.exceptions as exc_module
        expected_path = "src.ai_interviewer.exceptions"
        self.assertEqual(exc_module.__name__, expected_path)
    
    def test_error_handler_module_path(self):
        """Test error_handler module is in correct location."""
        import src.ai_interviewer.utils.error_handler as error_module
        expected_path = "src.ai_interviewer.utils.error_handler"
        self.assertEqual(error_module.__name__, expected_path)
    
    def test_types_module_path(self):
        """Test types module is in correct location."""
        import src.ai_interviewer.utils.types as types_module
        expected_path = "src.ai_interviewer.utils.types"
        self.assertEqual(types_module.__name__, expected_path)


def run_import_tests():
    """Run all import tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestImports))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionHierarchy))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestControllerImports))
    suite.addTests(loader.loadTestsFromTestCase(TestFlowControllerImports))
    suite.addTests(loader.loadTestsFromTestCase(TestModulePaths))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("Import and Path Verification Tests")
    print("=" * 70)
    print()
    
    result = run_import_tests()
    
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
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    sys.exit(0 if result.wasSuccessful() else 1)

