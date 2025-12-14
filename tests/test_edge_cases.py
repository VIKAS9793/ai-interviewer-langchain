
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# --- AGGRESSIVE MOCKING START ---
# We mock these BEFORE importing any app code to prevent "Cold Start" model loading
mock_chroma = MagicMock()
sys.modules["chromadb"] = mock_chroma
sys.modules["chromadb.config"] = MagicMock()

mock_whisper = MagicMock()
sys.modules["whisper"] = mock_whisper

mock_hf = MagicMock()
sys.modules["langchain_huggingface"] = mock_hf
# --- AGGRESSIVE MOCKING END ---

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai_interviewer.core.interview_graph import InterviewGraph
from src.ai_interviewer.utils.config import Config

class TestInterviewGraphEdgeCases(unittest.TestCase):
    
    def setUp(self):
        # Mock the heavy components
        self.mock_interviewer = MagicMock()
        self.mock_session_manager = MagicMock()
        
        # Patch the imports inside interview_graph.py (or init)
        # Since we instantiate InterviewGraph, we need to intercept the init
        
        with patch('src.ai_interviewer.core.interview_graph.AutonomousInterviewer') as MockAuth:
            MockAuth.return_value = self.mock_interviewer
            with patch('src.ai_interviewer.core.interview_graph.SessionManager') as MockSess:
                MockSess.return_value = self.mock_session_manager
                self.graph_engine = InterviewGraph()
                
                
        # Setup mock behavior with SIDE EFFECTS to simulate progress
        self.mock_interviewer.start_interview.return_value = {
            "session_id": "mock_session_123", 
            "greeting": "Mock Greeting"
        }
        
        # When generating question, return mock
        self.mock_interviewer._generate_next_question_autonomous.return_value = {
            "question": "Mock Question?"
        }
        
        # IMPORTANT: process_answer must return data that helps Evaluate Node update state
        # In the real app, Evaluate Node updates performance_history. 
        # But crucially, 'question_number' update happens in the Question Node logic if not mocked, 
        # or we need to ensure the graph flow increments it.
        # Let's look at interview_graph.py: _question_node increments question_number = state['question_number'] + 1
        # So the graph logic itself handles the increment!
        
        # Wait, Recursion Limit means the graph ran > 25 loops in ONE invoke() call.
        # This shouldn't happen if we have human-in-the-loop 'await_answer' node.
        # Ah! check edges in interview_graph.py
        # extract -> greeting -> generate -> validate -> await_answer
        # It SHOULD stop at 'await_answer'.
        
        # If it didn't stop, it means it skipped 'await_answer'?? 
        # Or mock setup makes it fail to extract context?
        
        self.mock_interviewer.process_answer.return_value = {
            "evaluation": {"score": 5, "feedback": "Good"},
            "score": 5
        }
        self.mock_interviewer._complete_interview.return_value = {
            "summary": {"grade": "A"}
        }

    def test_invalid_session_id(self):
        """Test processing an answer for a non-existent session"""
        print("\n🧪 Testing Invalid Session ID...")
        result = self.graph_engine.process_answer("fake_id_999", "My answer")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])
        print("✅ Correctly handled invalid session")

    def test_concurrent_sessions(self):
        """Test two candidates interviewing at the same time"""
        print("\n🧪 Testing Concurrent Sessions...")
        
        # User A
        self.mock_interviewer.start_interview.return_value = {"session_id": "session_A"}
        res_A = self.graph_engine.start_interview("Topic A", "Alice")
        id_A = res_A["session_id"]
        
        # User B
        self.mock_interviewer.start_interview.return_value = {"session_id": "session_B"}
        res_B = self.graph_engine.start_interview("Topic B", "Bob")
        id_B = res_B["session_id"]
        
        self.assertNotEqual(id_A, id_B)
        
        # Verify Contexts stored correctly
        state_A = self.graph_engine._active_states[id_A]
        state_B = self.graph_engine._active_states[id_B]
        
        self.assertEqual(state_A["candidate_name"], "Alice")
        self.assertEqual(state_B["candidate_name"], "Bob")
        print("✅ Concurrent sessions validated successfully")

    def test_context_propagation(self):
        """Test if resume skills are correctly passed to internal state"""
        print("\n🧪 Testing Context Propagation...")
        
        custom_context = {
            "target_role": "Ninja",
            "resume_skills": ["Stealth", "Shuriken"]
        }
        
        # Start
        self.mock_interviewer.start_interview.return_value = {"session_id": "session_ctx"}
        result = self.graph_engine.start_interview(
            "Ninja 101", 
            "Ryu", 
            custom_context=custom_context
        )
        
        sid = result["session_id"]
        state = self.graph_engine._active_states[sid]
        
        # Check if extracted context node did its job (or initial state)
        self.assertEqual(state["target_role"], "Ninja")
        self.assertIn("Stealth", state["resume_skills"])
        print("✅ Context propagated to state successfully")

if __name__ == '__main__':
    unittest.main()
