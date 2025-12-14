
import sys
import os
import unittest
import importlib

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestUIIntegrity(unittest.TestCase):
    """
    Verifies that all UI modules can be imported successfully.
    This catches circular dependency errors and syntax errors.
    """
    
    def test_import_components(self):
        """Test importing UI components"""
        try:
            import src.ui.components.feedback
            import src.ui.components.inputs
            # Add chat if it exists (not created yet in this refactor, but feedback is there)
        except ImportError as e:
            self.fail(f"Failed to import components: {e}")

    def test_import_tabs(self):
        """Test importing UI tabs"""
        try:
            import src.ui.tabs.interview_tab
            import src.ui.tabs.practice_tab
        except ImportError as e:
            self.fail(f"Failed to import tabs: {e}")

    def test_import_handlers(self):
        """Test importing handlers"""
        try:
            import src.ui.handlers
        except ImportError as e:
            self.fail(f"Failed to import handlers: {e}")

    def test_import_app(self):
        """Test importing main app"""
        try:
            import src.ui.app
        except ImportError as e:
            self.fail(f"Failed to import src.ui.app: {e}")

    def test_import_main_app_entry(self):
        """Test importing the root logical controller (that depends on UI now decoupled? no, UI depends on Controller)"""
        try:
            import src.ai_interviewer.controller
        except ImportError as e:
            self.fail(f"Failed to import controller: {e}")

if __name__ == '__main__':
    unittest.main()
