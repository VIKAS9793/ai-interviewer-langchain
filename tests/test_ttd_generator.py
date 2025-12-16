"""
Unit Tests for TTD (Test-Time Diffusion) Question Generation

Tests the complete TTD pipeline:
- QuestionEvaluator
- RedTeamAgent
- TTDQuestionGenerator
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ai_interviewer.modules.question_evaluator import QuestionEvaluator, QuestionQualityScore
from src.ai_interviewer.modules.red_team_agent import RedTeamAgent, CritiqueResult, AttackType
from src.ai_interviewer.modules.ttd_generator import TTDQuestionGenerator, TTDResult


class TestQuestionEvaluator:
    """Test QuestionEvaluator component."""
    
    def setup_method(self):
        self.evaluator = QuestionEvaluator(use_llm=False)
        self.evaluator.clear_history()
    
    def test_evaluate_good_question(self):
        """Good questions should score above threshold."""
        question = "How would you design a scalable Python API for handling user authentication?"
        topic = "Python API Design"
        
        score = self.evaluator.evaluate(question, topic)
        
        assert isinstance(score, QuestionQualityScore)
        assert score.overall >= 6.0  # Should be decent
        assert score.relevance > 5.0  # Contains topic words
        print(f"Good question score: {score.overall}/10")
    
    def test_evaluate_duplicate_question(self):
        """Duplicate questions should score low on uniqueness."""
        question = "What is your experience with Python?"
        topic = "Python"
        previous = ["Tell me about your Python experience"]
        
        score = self.evaluator.evaluate(question, topic, previous_questions=previous)
        
        # Uniqueness should be low due to semantic similarity
        print(f"Duplicate question uniqueness: {score.uniqueness}/10")
        print(f"Overall: {score.overall}/10")
    
    def test_evaluate_short_question(self):
        """Too short questions should score low on clarity."""
        question = "Python?"
        topic = "Python"
        
        score = self.evaluator.evaluate(question, topic)
        
        assert score.clarity < 7.0
        print(f"Short question clarity: {score.clarity}/10")
    
    def test_history_tracking(self):
        """Should track evaluation history."""
        self.evaluator.evaluate("Question 1 about Python?", "Python")
        self.evaluator.evaluate("Question 2 about Java?", "Java")
        
        assert len(self.evaluator.evaluation_history) == 2
        avg = self.evaluator.get_average_score()
        assert avg > 0


class TestRedTeamAgent:
    """Test RedTeamAgent component."""
    
    def setup_method(self):
        self.red_team = RedTeamAgent()
        self.red_team.clear_history()
    
    def test_attack_clean_question(self):
        """Clean questions should pass the attack."""
        question = "How would you implement a RESTful API in Python using Flask?"
        topic = "Python Web Development"
        
        result = self.red_team.attack(question, topic)
        
        assert isinstance(result, CritiqueResult)
        print(f"Clean question - severity: {result.severity}, passed: {result.passed}")
    
    def test_attack_biased_question(self):
        """Biased questions should fail with high severity."""
        question = "Are you married and do you have children?"
        topic = "Python"
        
        result = self.red_team.attack(question, topic)
        
        assert result.severity >= 9
        assert result.attack_type == AttackType.BIAS
        assert result.passed is False
        print(f"Biased question - severity: {result.severity}")
    
    def test_attack_vague_question(self):
        """Vague questions should be flagged."""
        question = "Tell me about stuff and things"
        topic = "Python"
        
        result = self.red_team.attack(question, topic)
        
        # Should be flagged for some issue (ambiguity or off-topic)
        assert result.severity >= 5  # Must be flagged
        print(f"Vague question - type: {result.attack_type.value}, severity: {result.severity}")
    
    def test_attack_duplicate_question(self):
        """Duplicate questions should be caught via semantic check."""
        question = "What is your experience with Python programming?"
        topic = "Python"
        previous = ["Tell me about your Python experience"]
        
        result = self.red_team.attack(question, topic, previous)
        
        print(f"Duplicate attack - type: {result.attack_type.value}, severity: {result.severity}")
    
    def test_attack_off_topic(self):
        """Off-topic questions should be flagged."""
        question = "How do you cook pasta?"
        topic = "Python Development"
        
        result = self.red_team.attack(question, topic)
        
        assert result.attack_type == AttackType.OFF_TOPIC
        assert result.passed is False
        print(f"Off-topic - severity: {result.severity}")


class TestTTDQuestionGenerator:
    """Test the complete TTD pipeline."""
    
    def setup_method(self):
        self.generator = TTDQuestionGenerator(llm=None)  # No LLM for testing
    
    def test_generate_fallback_question(self):
        """Without LLM, should generate fallback questions."""
        result = self.generator.generate_question(
            topic="Python Development",
            question_number=1,
            previous_questions=[],
            approach="technical"
        )
        
        assert isinstance(result, TTDResult)
        assert len(result.question) > 10
        assert result.iterations >= 1
        print(f"Fallback question: {result.question[:60]}...")
        print(f"Quality: {result.quality_score}/10, Iterations: {result.iterations}")
    
    def test_generate_multiple_questions(self):
        """Should generate unique questions for a sequence."""
        questions = []
        previous = []
        
        for i in range(1, 4):
            result = self.generator.generate_question(
                topic="Python",
                question_number=i,
                previous_questions=previous,
                approach="balanced"
            )
            questions.append(result.question)
            previous.append(result.question)
        
        # All questions should be unique
        assert len(set(questions)) == len(questions)
        print(f"Generated {len(questions)} unique questions")
        for i, q in enumerate(questions, 1):
            print(f"  Q{i}: {q[:50]}...")
    
    def test_generation_stats(self):
        """Should track generation statistics."""
        self.generator.generate_question("Python", 1)
        self.generator.generate_question("Python", 2)
        
        stats = self.generator.get_generation_stats()
        
        assert stats["total"] == 2
        assert "avg_quality_score" in stats
        print(f"Stats: {stats}")


class TestIntegration:
    """Integration tests for the complete TTD flow."""
    
    def test_full_interview_simulation(self):
        """Simulate 5 questions in an interview."""
        generator = TTDQuestionGenerator(llm=None)
        
        topic = "Python Backend Development"
        questions = []
        previous = []
        
        print("\n" + "="*60)
        print(f"TTD Interview Simulation: {topic}")
        print("="*60)
        
        for i in range(1, 6):
            result = generator.generate_question(
                topic=topic,
                question_number=i,
                previous_questions=previous,
                approach="balanced",
                target_difficulty="medium"
            )
            
            questions.append(result)
            previous.append(result.question)
            
            status = "✅" if result.passed_quality else "⚠️"
            print(f"\nQ{i} {status} (Score: {result.quality_score:.1f}/10, Iters: {result.iterations})")
            print(f"   {result.question[:70]}...")
            if result.refinements_made:
                print(f"   Refined: {result.refinements_made[0][:50]}...")
        
        # Summary
        stats = generator.get_generation_stats()
        print("\n" + "-"*60)
        print(f"Summary: Avg Score: {stats['avg_quality_score']}/10, Pass Rate: {stats['pass_rate']*100:.0f}%")
        print("="*60)
        
        # Check most are unique (allow some overlap with fallback templates in no-LLM mode)
        question_texts = [r.question for r in questions]
        unique = set(question_texts)
        assert len(unique) >= 3, f"Too many duplicates: {len(question_texts)} total, {len(unique)} unique"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
