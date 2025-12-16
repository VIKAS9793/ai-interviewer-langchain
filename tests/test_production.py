"""
Comprehensive Production-Grade Test Suite for Autonomous AI Interviewer

This test suite covers:
- Unit tests for all autonomous components
- Integration tests for complete interview flow
- Edge case testing
- Error recovery testing
- Guardrails and responsible AI testing
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_interviewer.core import (
    AutonomousReasoningEngine,
    AutonomousInterviewer,
    AutonomousFlowController,
    InterviewContext,
    CandidateState,
    ThoughtChain,
    ReasoningMode,
    InterviewSession,
    InterviewPhase,
    ResponsibleAI,
    AIGuardrails,
    SafetyLevel,
    BiasCategory
)


class TestAutonomousReasoningEngine(unittest.TestCase):
    """Tests for Chain-of-Thought Reasoning Engine"""
    
    def setUp(self):
        self.engine = AutonomousReasoningEngine(model_name="meta-llama/Meta-Llama-3-8B-Instruct")
        self.context = InterviewContext(
            session_id="test123",
            candidate_name="Test User",
            topic="Python/Backend Development",
            question_number=1,
            max_questions=5
        )
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.model_name, "meta-llama/Meta-Llama-3-8B-Instruct")
        self.assertEqual(len(self.engine.thought_history), 0)
    
    def test_think_before_acting_returns_thought_chain(self):
        """Test that reasoning produces a thought chain"""
        thought = self.engine.think_before_acting(self.context, "generate_question")
        
        self.assertIsInstance(thought, ThoughtChain)
        self.assertIsNotNone(thought.reasoning_id)
        self.assertIsNotNone(thought.conclusion)
        self.assertGreaterEqual(thought.confidence, 0)
        self.assertLessEqual(thought.confidence, 1)
    
    def test_reasoning_mode_selection(self):
        """Test correct reasoning mode based on context"""
        # Struggling candidate should use empathetic mode
        self.context.candidate_state = CandidateState.STRUGGLING
        mode = self.engine._determine_reasoning_mode(self.context, "generate_question")
        self.assertEqual(mode, ReasoningMode.EMPATHETIC)
        
        # Excelling candidate should use strategic mode
        self.context.candidate_state = CandidateState.EXCELLING
        mode = self.engine._determine_reasoning_mode(self.context, "generate_question")
        self.assertEqual(mode, ReasoningMode.STRATEGIC)
    
    def test_generate_options(self):
        """Test option generation"""
        situation = {"performance_trend": "improving", "knowledge_profile": {"gaps": []}}
        options = self.engine._generate_options(self.context, "generate_question", situation)
        
        self.assertIsInstance(options, list)
        self.assertGreater(len(options), 0)
        for option in options:
            self.assertIn("approach", option)
            self.assertIn("suitability", option)
    
    def test_self_reflection(self):
        """Test self-reflection mechanism"""
        actions = [
            {"question": "Q1", "score": 7},
            {"question": "Q2", "score": 8},
            {"question": "Q3", "score": 6}
        ]
        reflection = self.engine.self_reflect(actions)
        
        self.assertIn("insights", reflection)
        self.assertIn("improvements", reflection)
        self.assertIn("confidence_in_approach", reflection)
    
    def test_error_recovery(self):
        """Test self-healing on error"""
        error = Exception("Test error")
        context = {"action": "test"}
        recovery = self.engine.recover_from_error(error, context)
        
        self.assertEqual(recovery["status"], "recovered")
        self.assertIn("recovery_action", recovery)
    
    def test_performance_tracking(self):
        """Test performance metrics tracking"""
        initial_success = self.engine.performance_metrics["successful_reasonings"]
        
        # Trigger reasoning
        self.engine.think_before_acting(self.context, "generate_question")
        
        self.assertGreaterEqual(
            self.engine.performance_metrics["successful_reasonings"],
            initial_success
        )


class TestAutonomousInterviewer(unittest.TestCase):
    """Tests for Main Interview Agent"""
    
    def setUp(self):
        self.interviewer = AutonomousInterviewer(model_name="meta-llama/Meta-Llama-3-8B-Instruct")
    
    def test_interviewer_initialization(self):
        """Test interviewer initializes correctly"""
        self.assertIsNotNone(self.interviewer)
        self.assertIsNotNone(self.interviewer.reasoning_engine)
        self.assertEqual(len(self.interviewer.session_manager.active_sessions), 0)
    
    def test_start_interview(self):
        """Test starting an interview"""
        result = self.interviewer.start_interview(
            topic="Python/Backend Development",
            candidate_name="John Doe"
        )
        
        self.assertEqual(result["status"], "started")
        self.assertIn("session_id", result)
        self.assertIn("greeting", result)
        self.assertIn("first_question", result)
    
    def test_process_answer(self):
        """Test processing an answer"""
        # Start interview first
        start_result = self.interviewer.start_interview(
            topic="Python/Backend Development",
            candidate_name="Jane Doe"
        )
        session_id = start_result["session_id"]
        
        # Process an answer
        result = self.interviewer.process_answer(
            session_id,
            "Python uses reference counting and garbage collection for memory management."
        )
        
        self.assertIn("status", result)
        self.assertIn(result["status"], ["continue", "completed"])
    
    def test_invalid_session(self):
        """Test handling invalid session"""
        result = self.interviewer.process_answer(
            "invalid_session_id",
            "Some answer"
        )
        
        self.assertEqual(result["status"], "error")
    
    def test_session_status(self):
        """Test getting session status"""
        # Start interview
        start_result = self.interviewer.start_interview(
            topic="JavaScript/Frontend Development",
            candidate_name="Test User"
        )
        session_id = start_result["session_id"]
        
        status = self.interviewer.get_session_status(session_id)
        
        self.assertIn("status", status)
        self.assertIn("phase", status)
    
    def test_human_like_greeting(self):
        """Test greeting generation"""
        result = self.interviewer.start_interview(
            topic="Machine Learning/AI",
            candidate_name="Alice"
        )
        
        self.assertIn("greeting", result)
        self.assertIn("Alice", result["greeting"])


class TestAutonomousFlowController(unittest.TestCase):
    """Tests for Flow Controller"""
    
    def setUp(self):
        self.controller = AutonomousFlowController(
            max_concurrent_sessions=5,
            model_name="meta-llama/Meta-Llama-3-8B-Instruct"
        )
    
    def test_controller_initialization(self):
        """Test controller initializes correctly"""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.max_concurrent_sessions, 5)
    
    def test_start_interview_via_controller(self):
        """Test starting interview through controller"""
        result = self.controller.start_interview(
            topic="System Design",
            candidate_name="Bob"
        )
        
        self.assertEqual(result["status"], "started")
        # Response now includes session_id, greeting, first_question
        self.assertIn("session_id", result)
    
    def test_system_status(self):
        """Test getting system status"""
        status = self.controller.get_system_status()
        
        self.assertIn("status", status)
        self.assertIn("autonomous_features", status)
        self.assertIn("capacity", status)
    
    def test_concurrent_sessions_limit(self):
        """Test concurrency limit enforcement"""
        # Start max sessions
        for i in range(5):
            self.controller.start_interview(
                topic="Python/Backend Development",
                candidate_name=f"User{i}"
            )
        
        # Try to start one more
        result = self.controller.start_interview(
            topic="Python/Backend Development",
            candidate_name="ExtraUser"
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("CONCURRENCY_LIMIT", result.get("error_code", ""))


class TestAIGuardrails(unittest.TestCase):
    """Tests for Responsible AI Guardrails"""
    
    def setUp(self):
        self.guardrails = AIGuardrails()
    
    def test_safe_content_passes(self):
        """Test that safe content passes checks"""
        result = self.guardrails.check_content_safety(
            "Please explain how Python handles memory management."
        )
        
        self.assertTrue(result.passed)
        self.assertEqual(result.safety_level, SafetyLevel.SAFE)
    
    def test_harmful_content_flagged(self):
        """Test that harmful content is flagged"""
        result = self.guardrails.check_content_safety(
            "This is a terrible, awful, horrible, incompetent, useless response."
        )
        
        self.assertEqual(result.safety_level, SafetyLevel.CAUTION)
    
    def test_evaluation_fairness_pass(self):
        """Test fair evaluation passes"""
        evaluation = {
            "score": 7,
            "feedback": "Good understanding of core concepts demonstrated."
        }
        result = self.guardrails.check_evaluation_fairness(evaluation)
        
        self.assertTrue(result.passed)
    
    def test_extreme_score_requires_justification(self):
        """Test that extreme scores require justification"""
        # High score without detailed feedback
        evaluation = {"score": 9, "feedback": "Good"}
        result = self.guardrails.check_evaluation_fairness(evaluation)
        
        self.assertFalse(result.passed)
        self.assertTrue(any("justification" in issue.lower() for issue in result.issues))
    
    def test_question_fairness(self):
        """Test question fairness check"""
        # Technical question should pass
        result = self.guardrails.check_question_fairness(
            "Can you explain the difference between SQL and NoSQL databases?",
            "Python/Backend Development"
        )
        self.assertTrue(result.passed)
    
    def test_discriminatory_question_blocked(self):
        """Test discriminatory questions are blocked"""
        result = self.guardrails.check_question_fairness(
            "Are you married? Do you have children?",
            "Python/Backend Development"
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.safety_level, SafetyLevel.BLOCKED)
    
    def test_bias_detection(self):
        """Test bias detection in text"""
        bias_result = self.guardrails._detect_bias(
            "Men are typically better at this kind of work."
        )
        
        self.assertTrue(bias_result["detected"])
        self.assertIn(BiasCategory.GENDER.value, bias_result["categories"])


class TestResponsibleAI(unittest.TestCase):
    """Tests for Complete Responsible AI System"""
    
    def setUp(self):
        self.responsible_ai = ResponsibleAI()
    
    def test_validate_and_explain_question(self):
        """Test question validation with explanation"""
        result = self.responsible_ai.validate_and_explain_question(
            question="Explain Python decorators.",
            topic="Python/Backend Development",
            thought_chain={"conclusion": "progressive_challenge", "confidence": 0.8, "thoughts": []},
            context={"question_number": 2, "max_questions": 5}
        )
        
        self.assertIn("approved", result)
        self.assertIn("explanation", result)
        self.assertIn("decision_id", result)
    
    def test_validate_and_explain_evaluation(self):
        """Test evaluation validation with explanation"""
        result = self.responsible_ai.validate_and_explain_evaluation(
            evaluation={"score": 7, "feedback": "Good understanding shown."},
            answer="Python uses decorators to modify function behavior.",
            question="What are decorators?"
        )
        
        self.assertIn("fair", result)
        self.assertIn("explanation", result)
    
    def test_compliance_status(self):
        """Test compliance status reporting"""
        status = self.responsible_ai.get_compliance_status()
        
        self.assertIn("audit_summary", status)
        self.assertIn("compliance_report", status)


class TestEdgeCases(unittest.TestCase):
    """Edge case and error handling tests"""
    
    def setUp(self):
        self.controller = AutonomousFlowController()
    
    def test_empty_answer(self):
        """Test handling empty answer"""
        start = self.controller.start_interview("Python/Backend Development", "Test")
        result = self.controller.process_answer(start["session_id"], "")
        
        # Should not crash, should handle gracefully
        self.assertIn("status", result)
    
    def test_very_long_answer(self):
        """Test handling very long answer"""
        start = self.controller.start_interview("Python/Backend Development", "Test")
        long_answer = "Python " * 1000  # Very long answer
        result = self.controller.process_answer(start["session_id"], long_answer)
        
        self.assertIn("status", result)
    
    def test_special_characters_in_name(self):
        """Test handling special characters in candidate name"""
        result = self.controller.start_interview(
            "Python/Backend Development",
            "John O'Brien-Smith <script>alert('xss')</script>"
        )
        
        self.assertEqual(result["status"], "started")
    
    def test_unicode_in_answer(self):
        """Test handling unicode characters"""
        start = self.controller.start_interview("Python/Backend Development", "Test")
        result = self.controller.process_answer(
            start["session_id"],
            "Python использует сборку мусора 🐍 для управления памятью"
        )
        
        self.assertIn("status", result)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete interview flow (Mocked)"""
    
    @patch('src.ai_interviewer.core.autonomous_flow_controller.AutonomousInterviewer')
    def test_complete_interview_flow(self, MockInterviewer):
        """Test complete interview from start to finish with mocks"""
        # Setup mocks
        mock_interviewer_instance = MockInterviewer.return_value
        
        # Mock session manager attached to interviewer
        mock_session = MagicMock()
        mock_session.session_id = "test_sess_integration"
        mock_interviewer_instance.session_manager.active_sessions = {"test_sess_integration": mock_session}
        
        # Mock start_interview response
        mock_interviewer_instance.start_interview.return_value = {
            "status": "started",
            "session_id": "test_sess_integration",
            "greeting": "Hello",
            "first_question": "First Q",
            "message": "Welcome"
        }
        
        # Mock process_answer responses for sequence
        # We'll simulate 2 questions then completion
        mock_interviewer_instance.process_answer.side_effect = [
            {"status": "continue", "next_question": "Next Q"},
            {"status": "completed", "final_report": "Report"}
        ]
        
        controller = AutonomousFlowController()
        print(f"DEBUG: controller.interviewer type: {type(controller.interviewer)}")
        print(f"DEBUG: MockInterviewer type: {type(MockInterviewer)}")
        
        # Start interview
        start = controller.start_interview("Python/Backend Development", "Integration Test")
        print(f"DEBUG: Start result: {start}")
        self.assertEqual(start["status"], "started")
        session_id = start["session_id"]
        
        # Answer questions until complete (simulated)
        answers = [
            "Answer 1",
            "Answer 2"
        ]
        
        for i, answer in enumerate(answers):
            result = controller.process_answer(session_id, answer)
            print(f"DEBUG: Process answer {i} result: {result}")
            
            if result["status"] == "completed":
                self.assertIn("final_report", result)
            elif result["status"] == "continue":
                self.assertIn("next_question", result)
            else:
                self.fail(f"Unexpected status: {result['status']}")


def run_production_tests():
    """Run all production tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousReasoningEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousInterviewer))
    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousFlowController))
    suite.addTests(loader.loadTestsFromTestCase(TestAIGuardrails))
    suite.addTests(loader.loadTestsFromTestCase(TestResponsibleAI))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("PRODUCTION TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Success Rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    run_production_tests()
