
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai_interviewer.core.autonomous_interviewer import AutonomousInterviewer
from src.ai_interviewer.core.session_manager import InterviewSession, InterviewPhase

class TestRefactor(unittest.TestCase):
    def setUp(self):
        self.interviewer = AutonomousInterviewer()
        # Mock engine to avoid costly calls
        self.interviewer.reasoning_engine = MagicMock()
        
    def test_session_manager_integration(self):
        """Verify AutonomousInterviewer uses SessionManager correctly"""
        # 1. Start Interview
        result = self.interviewer.start_interview(
            topic="Test Topic",
            candidate_name="Tester",
        )
        session_id = result["session_id"]
        
        # 2. Check SessionManager state
        session = self.interviewer.session_manager.get_session(session_id)
        self.assertIsNotNone(session, "Session should exist in manager")
        self.assertEqual(session.candidate_name, "Tester", "Details should match")
        self.assertEqual(session.phase, InterviewPhase.WARM_UP, "Phase should be set")
        
        # 3. Process Answer (should verify retrieval)
        self.interviewer.process_answer(session_id, "My answer")
        updated_session = self.interviewer.session_manager.get_session(session_id)
        self.assertEqual(updated_session.current_answer, "My answer", "Manager should persist updates")
        
        print(f"\n✅ Refactor Verification Passed: SessionManager handling state for {session_id}")

if __name__ == "__main__":
    unittest.main()
