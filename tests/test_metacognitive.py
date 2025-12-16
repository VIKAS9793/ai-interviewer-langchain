
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock heavily to avoid loading models
mock_chroma = MagicMock()
sys.modules["chromadb"] = mock_chroma
sys.modules["chromadb.config"] = MagicMock()
sys.modules["chromadb.api"] = MagicMock()

sys.modules["whisper"] = MagicMock()
sys.modules["langchain_huggingface"] = MagicMock()

from src.ai_interviewer.core.autonomous_interviewer import AutonomousInterviewer, InterviewSession
from src.ai_interviewer.core.session_manager import CandidateState, InterviewPhase
from src.ai_interviewer.modules.critic_service import ReflectAgent, ReflectionOutcome, ReflectionResult

class TestMetacognitiveWiring(unittest.TestCase):
    
    def setUp(self):
        # Patch dependencies that load in init
        with patch('src.ai_interviewer.core.autonomous_interviewer.AutonomousReasoningEngine') as MockEngine:
            with patch('src.ai_interviewer.core.autonomous_interviewer.SessionManager') as MockSess:
                 with patch('src.ai_interviewer.modules.critic_service.ReflectAgent') as MockReflect: # Real agent or mock?
                    self.interviewer = AutonomousInterviewer()
                    # We want to test the wiring, so let's mock the ReflectAgent instance specifically
                    self.interviewer.reflect_agent = MagicMock()
                    self.interviewer.reasoning_engine = MagicMock()
                    self.interviewer.session_manager = MagicMock()

    def test_fairness_check_calls(self):
        """Verify fairness check is called during question generation"""
        
        # Setup session with ALL required attributes
        session = MagicMock()
        session.session_id = "test_sess_123"
        session.candidate_name = "Test User"
        session.topic = "Python"
        session.question_number = 1
        session.max_questions = 5
        session.performance_history = []
        session.knowledge_gaps = []
        session.strengths = []
        session.emotional_cues = []
        session.candidate_state = CandidateState.NEUTRAL
        session.thought_chains = []
        session.qa_pairs = []
        session.metadata = {}  # Required attribute
        session.current_question = None
        session.current_answer = None
        session.difficulty_level = "medium"
        session.interview_phase = InterviewPhase.CORE_ASSESSMENT
        
        # Mock engine generation
        self.interviewer.reasoning_engine.generate_human_like_question.return_value = {
            "question": "What is your age?",  # Biased question
            "metadata": {"confidence": 0.9}
        }
        
        # Mock Fairness Check to FAIL on first call, PASS on subsequent
        self.interviewer.reflect_agent.evaluate_question_fairness.return_value = ReflectionResult(
            outcome=ReflectionOutcome.FAILED,
            dimension="fairness",
            message="Age is protected"
        )
        
        # Execute
        result = self.interviewer._generate_next_question_autonomous(session)
        
        # Verify fairness check was called
        self.assertTrue(self.interviewer.reflect_agent.evaluate_question_fairness.called)
        print("✅ Fairness Check wiring passed (Called correctly)")

    def test_consistency_check_calls(self):
        """Verify consistency check is called during answer evaluations"""
        
        session = MagicMock(spec=InterviewSession)
        session.performance_history = [5, 5]
        session.current_answer = "My Answer"
        session.topic = "Java"
        
        # Mock Engine LLM (Prometheus Check)
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = '{"score": 5, "feedback": "Good"}'
        self.interviewer.reasoning_engine._get_llm = MagicMock(return_value=mock_llm)
        self.interviewer.reasoning_engine._current_model = "test_model"
        
        # Execute
        self.interviewer._evaluate_answer_autonomous(session, MagicMock())
        
        # Verify Call
        self.interviewer.reflect_agent.evaluate_scoring_consistency.assert_called()
        print("✅ Consistency Check wiring passed")

if __name__ == '__main__':
    unittest.main()
