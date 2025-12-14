import unittest
import logging
from unittest.mock import MagicMock, patch

from src.ai_interviewer.core.interview_graph import InterviewGraph
from src.ai_interviewer.core.autonomous_reasoning_engine import AutonomousReasoningEngine, InterviewContext, ReasoningMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CompanyTest")

class TestCompanyIntelligence(unittest.TestCase):
    
    def setUp(self):
        self.engine = AutonomousReasoningEngine()
        # Mock LLM to avoid calls
        self.engine._llm = MagicMock()
        
    def test_amazon_strategy_generation(self):
        """Test that Amazon context triggers Leadership Principles option"""
        context = InterviewContext(
            session_id="test_sess",
            candidate_name="Tester",
            topic="Coding",
            question_number=1,
            max_questions=5,
            company_name="Amazon"
        )
        
        # Act
        options = self.engine._generate_options(
            context, 
            "generate_question", 
            {"performance_trend": "stable", "knowledge_profile": {"gaps": []}}
        )
        
        # Assert
        strategies = [opt["approach"] for opt in options]
        logger.info(f"Generated strategies for Amazon: {strategies}")
        
        self.assertIn("leadership_principles", strategies)
        
        # Verify specific description
        amazon_opt = next(opt for opt in options if opt["approach"] == "leadership_principles")
        self.assertIn("Customer Obsession", amazon_opt["description"])

    def test_google_strategy_generation(self):
        """Test that Google context triggers GCA option"""
        context = InterviewContext(
            session_id="test_sess",
            candidate_name="Tester",
            topic="Coding",
            question_number=1,
            max_questions=5,
            company_name="Google"
        )
        
        # Act
        options = self.engine._generate_options(
            context, 
            "generate_question", 
            {"performance_trend": "stable", "knowledge_profile": {"gaps": []}}
        )
        
        # Assert
        strategies = [opt["approach"] for opt in options]
        logger.info(f"Generated strategies for Google: {strategies}")
        
        self.assertIn("gca_check", strategies)

if __name__ == '__main__':
    unittest.main()
